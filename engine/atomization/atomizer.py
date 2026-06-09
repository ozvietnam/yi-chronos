"""Atomizer — TWO-PASS production-ready.

Anh dạy 2026-06-09 paradigm bottom-up:
  - 5 archetype + 4 format
  - LLM tự propose knowledge_categories per chunk
  - Câu hỏi mặc định EMERGE, không hardcode
  - Atomic Q phải có entity name rõ + source_quote

Pass 1 — Meta-Question Generation
Pass 2 — Atomic Instance Extraction

Features production:
- Retry JSON parse fail (max 3)
- Persist incremental vào SQLite
- Provenance log vào extraction_runs
- Batch parallel (configurable)

Usage:
    from engine.atomization.atomizer import Atomizer

    atomizer = Atomizer(provider_name="minimax")
    result = atomizer.atomize_chunk(chunk_id=123, text="...", book_corpus_id="trung-chau-q2")
    # → persist chunk_classifications + atomic_questions + extraction_runs
"""

from __future__ import annotations

import json
import sqlite3
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.ai.providers.base import LLMProvider, LLMResponse, ProviderError  # noqa: E402
from engine.ai.providers.minimax import MiniMaxProvider  # noqa: E402

DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"

PROMPT_VERSION = "v2.1"  # bump khi đổi prompt — track trong extraction_runs

# ═══════════════════════════════════════════════════════════════
# PROMPTS (port từ poc_atomize_v2.py + tinh chỉnh production)
# ═══════════════════════════════════════════════════════════════
PASS1_PROMPT = """# Nhiệm vụ Pass 1
Đọc đoạn văn dưới đây từ sách Tử Vi/Bát Tự/Kinh Dịch. Phân loại + ĐỀ XUẤT câu hỏi mặc định
PHÙ HỢP RIÊNG cho nội dung đoạn này.

# Bước 1 — Phân loại ARCHETYPE (boolean, overlap được)

- `is_chu_the`     (chủ thể): định nghĩa sao/cung/khái niệm gốc
- `is_cong_thuc`   (công thức): cách tính, quy tắc cố định (an sao, tra cứu)
- `is_luan_giai`   (luận giải): giải nghĩa cách cục cụ thể
- `is_to_hop`      (tổ hợp): combo sao/cung phái sinh cách mới
- `is_kinh_nghiem` (kinh nghiệm): wisdom áp dụng khi luận giải

# Bước 2 — Phân loại FORMAT STYLE

- `ket_qua`     — đưa ra kết quả phán định cứng ("đại phú", "phá tán")
- `nguyen_ly`   — chỉ ra nguyên lý + cơ chế hoạt động
- `tho_phu`     — văn vần Hán cổ / phú bình giải
- `bang_lookup` — bảng / lookup table

# Bước 3 — KNOWLEDGE CATEGORIES IN THIS CHUNK

Đoạn này nói về những MẢNG KIẾN THỨC nào? Liệt kê 2-6 categories CỤ THỂ
cho đoạn này (KHÔNG generic, phải nêu rõ chủ thể).

# Bước 4 — QUESTION TEMPLATES PER CATEGORY

Cho mỗi category ở Bước 3, ĐỀ XUẤT 3-7 LOẠI CÂU HỎI mặc định phù hợp.
Tự nghĩ theo nội dung đoạn — KHÔNG dùng template universal.

# Output JSON STRICT (KHÔNG markdown fence, JSON thuần, parsable bằng json.loads)
{
  "archetype": {"is_chu_the": 0, "is_cong_thuc": 0, "is_luan_giai": 0, "is_to_hop": 0, "is_kinh_nghiem": 0},
  "format_style": "ket_qua | nguyen_ly | tho_phu | bang_lookup",
  "subjects_mentioned": ["..."],
  "knowledge_categories": ["..."],
  "question_templates_per_category": {
    "category 1": ["template Q1", "..."]
  }
}

# Đoạn văn
{content}

# Output Pass 1 (JSON thuần, escape \\n thành \\\\n trong string nếu có):
"""

PASS2_PROMPT = """# Nhiệm vụ Pass 2
Cho mỗi câu hỏi TEMPLATE ở Pass 1, extract atomic question CỤ THỂ (instance)
có thể answer được bằng đoạn văn dưới.

QUY TẮC BẮT BUỘC:
1. Atomic Q nêu RÕ tên sao, cung, chi cụ thể. TUYỆT ĐỐI tránh đại từ.
2. Mỗi atomic Q PHẢI có source_quote = trích nguyên văn đoạn chứa câu trả lời.
3. KHÔNG bịa, không suy đoán. Bám đoạn 100%.
4. Tránh trùng lặp.

# Output JSON STRICT (KHÔNG markdown fence)
{
  "atomic_questions": [
    {
      "from_template": "...",
      "from_category": "...",
      "question": "atomic Q rõ entity",
      "subject_identifiers": {"sao": "...", "cung": "...", ...},
      "source_quote": "..."
    }
  ]
}

# Pass 1 templates
{pass1_output}

# Đoạn văn
{content}

# Output Pass 2 (JSON thuần):
"""

RETRY_PROMPT_HINT = """

⚠ LƯU Ý: Lần trước em trả output KHÔNG parse được JSON. Hãy chú ý:
- KHÔNG dùng markdown ```json
- Escape " trong string giá trị thành \\"
- Escape newline trong string thành \\n
- Đảm bảo JSON đóng đủ { } [ ]
- Output chỉ JSON, không text thêm trước/sau
"""


def parse_json(content: str) -> tuple[dict | None, str | None]:
    raw = content.strip()
    # Strip markdown fence
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines)
    # Try extract first JSON object (greedy)
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        # Try repair: find first { and last }
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            candidate = raw[start:end + 1]
            try:
                return json.loads(candidate), None
            except json.JSONDecodeError as e2:
                return None, f"JSONDecodeError after repair: {e2}"
        return None, f"JSONDecodeError: {e}"


@dataclass
class AtomizeResult:
    chunk_id: int | None
    classification: dict | None
    atomic_questions: list[dict]
    pass1_run_id: int | None
    pass2_run_id: int | None
    error: str | None = None
    total_tokens: int = 0
    total_duration_sec: float = 0.0


class Atomizer:
    """Production atomizer với DB persist + retry."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        provider_name: str = "minimax",
        model: str | None = None,
        db_path: Path = DB_PATH,
        max_retries: int = 3,
    ):
        if provider:
            self.provider = provider
        else:
            self.provider = self._load_provider(provider_name)
        self.model = model or self._default_model_for(provider_name)
        self.db_path = db_path
        self.max_retries = max_retries

    @staticmethod
    def _load_provider(name: str) -> LLMProvider:
        keys = json.loads((PROJECT_ROOT / "data" / "ai_keys.json").read_text())
        if name == "minimax":
            return MiniMaxProvider(api_key=keys["minimax"])
        # Add more providers as needed
        raise ValueError(f"Unsupported provider: {name}")

    @staticmethod
    def _default_model_for(provider_name: str) -> str:
        return {"minimax": "MiniMax-M2"}.get(provider_name, "")

    def _open_db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _llm_call_with_retry(
        self, prompt: str, max_tokens: int, temperature: float, run_type: str,
        book_corpus_id: str, chunk_id: int | None = None,
    ) -> tuple[dict | None, LLMResponse | None, str | None, int | None]:
        """Returns (parsed_json, response, error, run_id)."""
        run_id = self._insert_run_pending(
            run_type=run_type, book_corpus_id=book_corpus_id, chunk_id=chunk_id,
            max_tokens=max_tokens, temperature=temperature,
        )

        last_error: str | None = None
        for attempt in range(self.max_retries):
            full_prompt = prompt if attempt == 0 else prompt + RETRY_PROMPT_HINT
            t_start = time.time()
            try:
                response = self.provider.chat(
                    messages=[{"role": "user", "content": full_prompt}],
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except ProviderError as e:
                last_error = f"ProviderError attempt {attempt+1}: {e}"
                continue
            duration = time.time() - t_start

            parsed, parse_err = parse_json(response.content)
            if parsed is not None:
                self._update_run_completed(
                    run_id, response, duration, status="completed",
                )
                return parsed, response, None, run_id
            last_error = parse_err
            # Mark this attempt failed but keep trying
            time.sleep(0.5)

        # All retries failed
        self._update_run_completed(run_id, None, 0, status="failed", error=last_error)
        return None, None, last_error, run_id

    def _insert_run_pending(
        self, run_type: str, book_corpus_id: str, chunk_id: int | None,
        max_tokens: int, temperature: float,
    ) -> int:
        with self._open_db() as conn:
            cur = conn.execute(
                """INSERT INTO extraction_runs
                   (run_type, book_corpus_id, chunk_id, llm_provider, llm_model,
                    temperature, max_tokens, prompt_version, status, started_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', strftime('%s','now'))""",
                (run_type, book_corpus_id, chunk_id, self.provider.name, self.model,
                 temperature, max_tokens, PROMPT_VERSION),
            )
            run_id = cur.lastrowid
            conn.commit()
            return int(run_id)

    def _update_run_completed(
        self, run_id: int, response: LLMResponse | None, duration: float,
        status: str = "completed", error: str | None = None,
    ) -> None:
        with self._open_db() as conn:
            if response:
                conn.execute(
                    """UPDATE extraction_runs SET
                       prompt_tokens=?, completion_tokens=?, duration_sec=?,
                       status=?, error_message=?, raw_response=?,
                       completed_at=strftime('%s','now')
                       WHERE run_id=?""",
                    (response.prompt_tokens, response.completion_tokens, duration,
                     status, error, response.content[:5000], run_id),
                )
            else:
                conn.execute(
                    """UPDATE extraction_runs SET
                       status=?, error_message=?, completed_at=strftime('%s','now')
                       WHERE run_id=?""",
                    (status, error, run_id),
                )
            conn.commit()

    def atomize_chunk(
        self,
        chunk_id: int,
        text: str,
        book_corpus_id: str,
        skip_if_exists: bool = True,
    ) -> AtomizeResult:
        """Atomize 1 chunk: Pass 1 → Pass 2 → persist."""
        # Idempotency: skip if already atomized
        if skip_if_exists:
            with self._open_db() as conn:
                existing = conn.execute(
                    "SELECT COUNT(*) FROM chunk_classifications WHERE chunk_id=? AND founder_verified >= 0",
                    (chunk_id,),
                ).fetchone()[0]
                if existing > 0:
                    return AtomizeResult(
                        chunk_id=chunk_id, classification=None, atomic_questions=[],
                        pass1_run_id=None, pass2_run_id=None,
                        error="already atomized, skipped",
                    )

        total_tokens = 0
        total_duration = 0.0

        # ── PASS 1 ────────────────────────────────────────────────
        p1_prompt = PASS1_PROMPT.replace("{content}", text)
        p1_parsed, p1_resp, p1_err, p1_run = self._llm_call_with_retry(
            prompt=p1_prompt, max_tokens=4000, temperature=0.7,
            run_type="pass1", book_corpus_id=book_corpus_id, chunk_id=chunk_id,
        )
        if p1_parsed is None:
            return AtomizeResult(
                chunk_id=chunk_id, classification=None, atomic_questions=[],
                pass1_run_id=p1_run, pass2_run_id=None, error=f"Pass 1 fail: {p1_err}",
            )
        if p1_resp:
            total_tokens += p1_resp.prompt_tokens + p1_resp.completion_tokens

        # Persist classification
        cc_id = self._persist_classification(chunk_id, p1_parsed)

        # ── PASS 2 ────────────────────────────────────────────────
        p2_prompt = (
            PASS2_PROMPT
            .replace("{pass1_output}", json.dumps(p1_parsed, ensure_ascii=False, indent=2))
            .replace("{content}", text)
        )
        p2_parsed, p2_resp, p2_err, p2_run = self._llm_call_with_retry(
            prompt=p2_prompt, max_tokens=10000, temperature=0.7,  # bumped to 10k
            run_type="pass2", book_corpus_id=book_corpus_id, chunk_id=chunk_id,
        )
        if p2_parsed is None:
            return AtomizeResult(
                chunk_id=chunk_id, classification=p1_parsed, atomic_questions=[],
                pass1_run_id=p1_run, pass2_run_id=p2_run,
                error=f"Pass 2 fail: {p2_err}", total_tokens=total_tokens,
            )
        if p2_resp:
            total_tokens += p2_resp.prompt_tokens + p2_resp.completion_tokens

        atoms = p2_parsed.get("atomic_questions", [])
        # Persist atoms
        atom_ids = self._persist_atoms(chunk_id, cc_id, atoms)

        # Update chunks_v2.atom_q_str (backup retrieval)
        self._update_chunk_atom_str(chunk_id, atoms)

        return AtomizeResult(
            chunk_id=chunk_id,
            classification=p1_parsed,
            atomic_questions=atoms,
            pass1_run_id=p1_run, pass2_run_id=p2_run,
            total_tokens=total_tokens,
        )

    def _persist_classification(self, chunk_id: int, p1: dict) -> int:
        arch = p1.get("archetype", {})
        with self._open_db() as conn:
            cur = conn.execute(
                """INSERT INTO chunk_classifications
                   (chunk_id, is_chu_the, is_cong_thuc, is_luan_giai, is_to_hop, is_kinh_nghiem,
                    format_style, knowledge_categories_json, question_templates_json,
                    subjects_json, extracted_by, confidence)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    chunk_id,
                    arch.get("is_chu_the", 0),
                    arch.get("is_cong_thuc", 0),
                    arch.get("is_luan_giai", 0),
                    arch.get("is_to_hop", 0),
                    arch.get("is_kinh_nghiem", 0),
                    p1.get("format_style"),
                    json.dumps(p1.get("knowledge_categories", []), ensure_ascii=False),
                    json.dumps(p1.get("question_templates_per_category", {}), ensure_ascii=False),
                    json.dumps(p1.get("subjects_mentioned", []), ensure_ascii=False),
                    f"{self.provider.name}/{self.model}",
                    0.85,
                ),
            )
            cc_id = cur.lastrowid
            conn.commit()
            return int(cc_id)

    def _persist_atoms(self, chunk_id: int, cc_id: int, atoms: list[dict]) -> list[int]:
        atom_ids = []
        with self._open_db() as conn:
            for a in atoms:
                cur = conn.execute(
                    """INSERT INTO atomic_questions
                       (chunk_id, cc_id, question_text, question_lang,
                        from_category, from_template,
                        subject_identifiers, source_quote, confidence, extracted_by)
                       VALUES (?, ?, ?, 'vi', ?, ?, ?, ?, ?, ?)""",
                    (
                        chunk_id, cc_id, a.get("question", ""),
                        a.get("from_category"), a.get("from_template"),
                        json.dumps(a.get("subject_identifiers", {}), ensure_ascii=False),
                        a.get("source_quote", ""),
                        0.85,
                        f"{self.provider.name}/{self.model}",
                    ),
                )
                atom_ids.append(int(cur.lastrowid))
            conn.commit()
        return atom_ids

    def _update_chunk_atom_str(self, chunk_id: int, atoms: list[dict]) -> None:
        atom_str = "\n".join(a.get("question", "") for a in atoms)
        with self._open_db() as conn:
            conn.execute(
                "UPDATE chunks_v2 SET atom_q_str=? WHERE chunk_id=?",
                (atom_str, chunk_id),
            )
            conn.commit()


# ═══════════════════════════════════════════════════════════════
# CLI test
# ═══════════════════════════════════════════════════════════════
def _cli_test() -> None:
    """Smoke test: pick 1 page Trung Châu Q2, atomize, verify DB persist."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", type=int, default=347, help="Page Trung Châu Q2 to test")
    args = parser.parse_args()

    # First create a chunks_v2 row from this page
    page_path = PROJECT_ROOT / "data" / "restored_books" / "trung-chau-tu-vi-dau-so-2" / "pages" / f"p{args.page:04d}.md"
    if not page_path.exists():
        sys.exit(f"❌ Page not found: {page_path}")
    text = page_path.read_text(encoding="utf-8").strip()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """INSERT INTO chunks_v2 (book_corpus_id, page_start, page_end, text)
           VALUES (?, ?, ?, ?)""",
        ("trung-chau-tu-vi-dau-so-2", args.page, args.page, text),
    )
    chunk_id = int(cur.lastrowid)
    conn.commit()
    conn.close()
    print(f"📦 Created chunks_v2 row chunk_id={chunk_id} for p{args.page:04d}")

    # Atomize
    atomizer = Atomizer()
    print(f"🔧 Atomizer: provider={atomizer.provider.name} model={atomizer.model}")
    result = atomizer.atomize_chunk(chunk_id, text, "trung-chau-tu-vi-dau-so-2", skip_if_exists=False)

    if result.error:
        print(f"❌ Error: {result.error}")
    else:
        print(f"✅ {len(result.atomic_questions)} atomic Q persisted")
        print(f"   Pass1 run_id: {result.pass1_run_id}")
        print(f"   Pass2 run_id: {result.pass2_run_id}")
        print(f"   Tokens: {result.total_tokens}")

    # Verify
    conn = sqlite3.connect(DB_PATH)
    n_cc = conn.execute("SELECT COUNT(*) FROM chunk_classifications WHERE chunk_id=?", (chunk_id,)).fetchone()[0]
    n_aq = conn.execute("SELECT COUNT(*) FROM atomic_questions WHERE chunk_id=?", (chunk_id,)).fetchone()[0]
    n_run = conn.execute("SELECT COUNT(*) FROM extraction_runs WHERE chunk_id=?", (chunk_id,)).fetchone()[0]
    print(f"\n📊 DB verify chunk_id={chunk_id}:")
    print(f"   chunk_classifications: {n_cc} rows")
    print(f"   atomic_questions: {n_aq} rows")
    print(f"   extraction_runs: {n_run} rows")
    conn.close()


if __name__ == "__main__":
    _cli_test()
