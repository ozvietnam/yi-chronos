"""KnowledgeAwareDecomposer — Algorithm 1 PIKE-RAG port.

Anh chốt 2026-06-09 Decision 3: wrap engine v3/v4 hiện có (47 rules Trung Châu).
Engine cũ làm "atomic answerers" — Algorithm 1 orchestrator.

Loop logic (PIKE-RAG §5.3.2):
  while len(chosen) < max_iter (5):
    1. Propose atomic queries (LLM)
    2. Retrieve atom info (3-level fallback)
    3. Select most useful atom (LLM)
    4. If no select → break
  Final: answer original_query with all chosen chunks (LLM)

Output: structured response với atom citations + rationale + trajectory.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.base import LLMProvider, ProviderError  # noqa: E402
from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402
from engine.atomization.retriever import ChunkAtomRetriever, AtomRetrievalInfo  # noqa: E402


PROPOSER_PROMPT = """# Nhiệm vụ — Proposer
Em là Tử Vi sage. User hỏi:
{user_query}

Bối cảnh đã có (atomic chunks đã chọn từ các vòng trước):
{chosen_context}

Hãy đặt 3-5 ATOMIC SUB-QUESTIONS cụ thể có thể tìm trong knowledge base để
GẦN HƠN với câu trả lời cuối. Mỗi sub-Q phải nêu RÕ tên sao, cung, chi.

QUY TẮC:
- KHÔNG đại từ ("nó", "mệnh này"). Phải nêu tên cụ thể.
- Nếu KHÔNG cần thêm thông tin → trả "decompose": false
- KHÔNG suy đoán, KHÔNG predict cứng (Iron Rule #6 — đọc đồng dạng)

# Output JSON (KHÔNG markdown fence):
{
  "decompose": true | false,
  "thinking": "<phân tích>",
  "sub_questions": ["Sub Q 1", "Sub Q 2", ...]
}

# Output Pass Proposer:
"""

SELECTOR_PROMPT = """# Nhiệm vụ — Selector
User hỏi: {user_query}
Bối cảnh đã chọn: {chosen_context}

Em xem danh sách atomic Q candidates dưới đây, chọn câu CÓ ÍCH NHẤT
để bổ sung context (TRÁNH chọn câu đã có thông tin tương đương trong bối cảnh).

# Candidates:
{candidates_str}

# Output JSON:
{
  "selected": true | false,
  "thinking": "<lý do chọn>",
  "candidate_idx": <integer 1 to N hoặc null nếu không chọn>
}

# Output:
"""

ANSWERER_PROMPT = """# Nhiệm vụ — Answerer
User hỏi:
{user_query}

Em đã thu thập các đoạn knowledge sau (từ sách, có citation):
{context}

Hãy trả lời User dựa TUYỆT ĐỐI trên context. KHÔNG bịa, KHÔNG predict cứng.
Paradigm Iron Rule #6: ĐỌC ĐỒNG DẠNG — phản chiếu xu hướng, KHÔNG phán cát/hung.
Nếu schools khác nhau → present cả góc nhìn, không ép merge.

# Output JSON:
{
  "answer": "<câu trả lời, có thể nhiều paragraph>",
  "rationale": "<lập luận, trích nguồn 'Trung Châu p347' / 'Phú Thái Vi p52'>",
  "citations": [
    {"book": "...", "page": ..., "atom_question": "..."}
  ]
}

# Output:
"""


def _parse_json(content: str) -> tuple[dict | None, str | None]:
    raw = content.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        # Repair: find first { and last }
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start:end + 1]), None
            except json.JSONDecodeError as e2:
                return None, str(e2)
        return None, str(e)


@dataclass
class DecomposeResult:
    user_query: str
    answer: str | None
    rationale: str | None
    citations: list[dict]
    chosen_atoms: list[AtomRetrievalInfo]
    trajectory: list[dict]
    total_tokens: int
    duration_sec: float
    error: str | None = None


class KnowledgeAwareDecomposer:
    """Algorithm 1 PIKE-RAG wrap engine v3/v4 hiện có.

    For MVP: engine v3/v4 sẽ wrap qua callback `legacy_engine_check(sub_q, la_so)`.
    Khi nào engine cũ match → ưu tiên dùng. Else fallback retriever.
    """

    def __init__(
        self,
        retriever: ChunkAtomRetriever | None = None,
        provider: LLMProvider | None = None,
        model: str = "MiniMax-M2",
        max_iter: int = 5,
        legacy_engine_check: Any = None,  # Callable[[str, dict], list[AtomRetrievalInfo]] | None
    ):
        self.retriever = retriever or ChunkAtomRetriever()
        self.provider = provider or self._default_provider()
        self.model = model
        self.max_iter = max_iter
        self.legacy_check = legacy_engine_check

    @staticmethod
    def _default_provider() -> LLMProvider:
        keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
        return MiniMaxProvider(api_key=keys["minimax"])

    def _llm_call(self, prompt: str, temperature: float = 0.3, max_tokens: int = 3000) -> dict | None:
        try:
            r = self.provider.chat(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except ProviderError as e:
            print(f"  ⚠ LLM error: {e}")
            return None
        parsed, err = _parse_json(r.content)
        if err:
            print(f"  ⚠ JSON parse: {err}")
        # Attach token usage for caller
        if parsed is not None:
            parsed["__usage"] = {
                "prompt": r.prompt_tokens, "completion": r.completion_tokens,
            }
        return parsed

    def _format_chosen_context(self, chosen: list[AtomRetrievalInfo]) -> str:
        if not chosen:
            return "(empty — vòng đầu)"
        parts = []
        for i, a in enumerate(chosen, 1):
            parts.append(
                f"[{i}] ({a.source_book} p{a.page_start}) atomic_Q: {a.atom_question}\n"
                f"   chunk: {a.chunk_text[:400]}..."
            )
        return "\n\n".join(parts)

    def _format_candidates(self, candidates: list[AtomRetrievalInfo]) -> str:
        parts = []
        for i, c in enumerate(candidates, 1):
            cat = c.from_category or "(no cat)"
            parts.append(
                f"{i}. [{c.source_book} p{c.page_start}] cat={cat}\n"
                f"   Q: {c.atom_question}\n"
                f"   quote: {(c.source_quote or '')[:200]}"
            )
        return "\n\n".join(parts)

    def decompose(
        self,
        user_query: str,
        la_so: dict | None = None,
        school: str | None = None,
    ) -> DecomposeResult:
        """Algorithm 1: propose → retrieve → select loop, then answer."""
        t_start = time.time()
        chosen: list[AtomRetrievalInfo] = []
        trajectory: list[dict] = []
        total_tokens = 0

        for t in range(self.max_iter):
            # ── Step 1: Propose atomic Q ──────────────────────────
            chosen_ctx = self._format_chosen_context(chosen)
            propose_prompt = (
                PROPOSER_PROMPT
                .replace("{user_query}", user_query)
                .replace("{chosen_context}", chosen_ctx)
            )
            p = self._llm_call(propose_prompt, temperature=0.5, max_tokens=2000)
            if not p:
                break
            total_tokens += p.pop("__usage", {}).get("prompt", 0) + p.get("__usage", {}).get("completion", 0)
            p.pop("__usage", None)
            decompose = p.get("decompose", False)
            sub_qs = p.get("sub_questions", [])
            trajectory.append({"iter": t + 1, "step": "propose", "decompose": decompose,
                              "sub_questions": sub_qs, "thinking": p.get("thinking", "")})
            if not decompose or not sub_qs:
                break

            # ── Step 2: Retrieve 3-level fallback ─────────────────
            chosen_chunk_ids = {a.chunk_id for a in chosen}
            candidates = self.retriever.retrieve_atoms(
                atomic_queries=sub_qs,
                original_query=user_query,
                chosen_chunk_ids=chosen_chunk_ids,
            )
            # Try legacy engine v3/v4 first (Decision 3)
            if self.legacy_check:
                try:
                    legacy_hits = self.legacy_check(sub_qs, la_so or {})
                    if legacy_hits:
                        candidates = legacy_hits + candidates
                except Exception as e:
                    print(f"  ⚠ Legacy engine error: {e}")

            if not candidates:
                trajectory.append({"iter": t + 1, "step": "retrieve", "result": "no candidates"})
                break
            trajectory.append({
                "iter": t + 1, "step": "retrieve",
                "n_candidates": len(candidates),
                "top_atoms": [c.atom_question for c in candidates[:3]],
            })

            # ── Step 3: Select best ───────────────────────────────
            candidates_str = self._format_candidates(candidates[:10])
            select_prompt = (
                SELECTOR_PROMPT
                .replace("{user_query}", user_query)
                .replace("{chosen_context}", chosen_ctx)
                .replace("{candidates_str}", candidates_str)
            )
            s = self._llm_call(select_prompt, temperature=0.3, max_tokens=1500)
            if not s:
                break
            total_tokens += s.pop("__usage", {}).get("prompt", 0) + s.get("__usage", {}).get("completion", 0)
            s.pop("__usage", None)
            if not s.get("selected") or s.get("candidate_idx") is None:
                trajectory.append({"iter": t + 1, "step": "select", "selected": False})
                break
            idx = int(s["candidate_idx"]) - 1
            if not (0 <= idx < len(candidates)):
                break
            chosen.append(candidates[idx])
            trajectory.append({
                "iter": t + 1, "step": "select",
                "selected_idx": idx + 1,
                "selected_atom": candidates[idx].atom_question,
                "thinking": s.get("thinking", ""),
            })

        # ── Final: Answer ─────────────────────────────────────────
        if not chosen:
            return DecomposeResult(
                user_query=user_query, answer=None, rationale=None,
                citations=[], chosen_atoms=[], trajectory=trajectory,
                total_tokens=total_tokens,
                duration_sec=time.time() - t_start,
                error="No atoms retrieved — KB chưa đủ data hoặc query không match",
            )
        context = "\n\n---\n\n".join(
            f"[Atom {i+1}] from {a.source_book} p{a.page_start}\n"
            f"Atomic Q: {a.atom_question}\n"
            f"Source quote: {a.source_quote or '(no quote)'}\n"
            f"Chunk: {a.chunk_text[:800]}"
            for i, a in enumerate(chosen)
        )
        answer_prompt = (
            ANSWERER_PROMPT
            .replace("{user_query}", user_query)
            .replace("{context}", context)
        )
        ans = self._llm_call(answer_prompt, temperature=0.4, max_tokens=4000)
        if not ans:
            return DecomposeResult(
                user_query=user_query, answer=None, rationale=None,
                citations=[], chosen_atoms=chosen, trajectory=trajectory,
                total_tokens=total_tokens,
                duration_sec=time.time() - t_start,
                error="Final answerer failed",
            )
        total_tokens += ans.pop("__usage", {}).get("prompt", 0) + ans.get("__usage", {}).get("completion", 0)
        ans.pop("__usage", None)

        return DecomposeResult(
            user_query=user_query,
            answer=ans.get("answer"),
            rationale=ans.get("rationale"),
            citations=ans.get("citations", []),
            chosen_atoms=chosen,
            trajectory=trajectory,
            total_tokens=total_tokens,
            duration_sec=time.time() - t_start,
        )


if __name__ == "__main__":
    # Smoke test
    d = KnowledgeAwareDecomposer()
    print("🤔 User query: 'Lá số mệnh Vũ Khúc Phá Quân tọa cung Tỵ có tính chất gì?'")
    print()
    r = d.decompose("Lá số mệnh Vũ Khúc Phá Quân tọa cung Tỵ có tính chất gì?")
    print(f"\n{'═'*60}")
    print(f"✅ Answer:\n{r.answer}\n")
    print(f"📖 Rationale: {r.rationale}\n")
    print(f"📚 Citations: {len(r.citations)}")
    for c in r.citations:
        print(f"   - {c}")
    print(f"\n🔍 {len(r.chosen_atoms)} atoms chosen")
    print(f"⏱  {r.duration_sec:.1f}s · {r.total_tokens} tokens")
    if r.error:
        print(f"⚠ Error: {r.error}")
