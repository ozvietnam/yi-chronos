"""Hội Đồng Tư Vấn Trí Tuệ — multi-agent debate orchestrator.

3-round Socratic flow:

  Round 0 (Triage)    : Trọng tài chọn agents nào tham gia (dựa câu hỏi + chart).
  Round 1 (Independent): Mỗi agent đưa nhận định độc lập.
  Round 2 (Challenge) : Trọng tài chất vấn — tìm mâu thuẫn + đặt câu hỏi khó.
  Round 3 (Response)  : Agents phản hồi chất vấn.
  Round 4 (Synthesis) : Trọng tài tổng hợp + actionable insights.

Storage: each debate session is persisted in SQLite for review/audit.
"""

from __future__ import annotations

import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .agents import AgentResponse, run_agent
from .prompt_store import AGENT_IDS, AGENT_METADATA, get_prompt
from .providers import LLMProvider, ProviderError
from .registry import get_registry


# ─── Default agent provider mapping ──────────────────────────────────────────
# Anh có thể override per-agent runtime. Mặc định:
DEFAULT_AGENT_PROVIDER: dict[str, list[str]] = {
    # Đông agents — DeepSeek R1 best for Eastern reasoning, fallback ZAI
    "mai_hoa":  ["deepseek", "zai", "anthropic", "mock"],
    "luc_hao":  ["deepseek", "zai", "anthropic", "mock"],
    "lien_hoa": ["deepseek", "zai", "anthropic", "mock"],
    "tu_vi":    ["deepseek", "zai", "anthropic", "mock"],
    "bat_tu":   ["deepseek", "zai", "anthropic", "mock"],
    "ha_lac":   ["deepseek", "zai", "anthropic", "mock"],
    # Tây agent — Anthropic preferred for psychology, fallback ZAI
    "western":  ["anthropic", "zai", "deepseek", "mock"],
    "than_so":  ["deepseek", "zai", "anthropic", "mock"],
    "chieu_dom": ["deepseek", "zai", "anthropic", "mock"],   # Bắc phái nội tâm (council prefer_reasoning→M3)
}

# Orchestrator (Trọng tài tổng hợp) — MiniMax-M3 chủ lực 2026-06 (reasoning sâu cho
# bước synthesis là output quan trọng nhất user đọc). Anthropic/DeepSeek fallback.
ORCHESTRATOR_PROVIDER_ORDER: list[str] = ["minimax", "anthropic", "deepseek", "zai", "mock"]
ORCHESTRATOR_PREFERRED_MODEL: dict[str, str] = {
    "minimax":   "MiniMax-M3",      # chủ lực — reasoning model, token floor lo <think>
    "anthropic": "claude-opus-4-5-20250929",
    "deepseek":  "deepseek-reasoner",
    "zai":       "glm-4.5-flash",   # free tier — Council can run without z.ai balance
    "mock":      "mock-v1",
}


_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ai_council.sqlite3"


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                question TEXT,
                chart_summary TEXT,
                agents_consulted TEXT,
                round_1_outputs TEXT,
                round_2_challenges TEXT,
                round_3_outputs TEXT,
                final_synthesis TEXT,
                total_tokens INTEGER DEFAULT 0,
                providers_used TEXT,
                duration_ms INTEGER
            )"""
        )


def _save_session(payload: dict) -> int:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO sessions
               (question, chart_summary, agents_consulted, round_1_outputs,
                round_2_challenges, round_3_outputs, final_synthesis,
                total_tokens, providers_used, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload["question"],
                json.dumps(payload.get("chart_summary", {}), ensure_ascii=False)[:2000],
                json.dumps(payload["agents_consulted"], ensure_ascii=False),
                json.dumps(payload["round_1_outputs"], ensure_ascii=False),
                payload.get("round_2_challenges", ""),
                json.dumps(payload.get("round_3_outputs", []), ensure_ascii=False),
                payload["final_synthesis"],
                payload["total_tokens"],
                json.dumps(payload["providers_used"], ensure_ascii=False),
                payload["duration_ms"],
            ),
        )
        return cur.lastrowid


# ─── Data classes ────────────────────────────────────────────────────────────


@dataclass
class CouncilSession:
    """Full record of one council consultation."""

    question: str
    agents_consulted: list[str] = field(default_factory=list)
    round_0_triage_reason: str = ""
    round_1_outputs: list[dict] = field(default_factory=list)   # AgentResponse dicts
    round_2_challenges: str = ""
    round_3_outputs: list[dict] = field(default_factory=list)
    final_synthesis: str = ""
    total_tokens: int = 0
    providers_used: dict[str, str] = field(default_factory=dict)
    duration_ms: int = 0
    session_id: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Orchestrator helpers ────────────────────────────────────────────────────


def _get_orchestrator_provider() -> tuple[LLMProvider, str]:
    """Pick first configured Trọng tài provider + preferred model."""
    reg = get_registry()
    for name in ORCHESTRATOR_PROVIDER_ORDER:
        try:
            p = reg.get(name)
            if p.is_configured:
                return p, ORCHESTRATOR_PREFERRED_MODEL.get(name, p.default_model)
        except KeyError:
            continue
    return reg.get("mock"), "mock-v1"


def _get_agent_provider(agent_id: str, prefer_reasoning: bool = False) -> tuple[LLMProvider, str]:
    """Pick provider for a specific agent based on preference order.

    prefer_reasoning=True (council premium luận sâu): đẩy MiniMax-M3 lên đầu chuỗi
    (chủ lực). Đường nhanh đồng bộ (run_quick) giữ False → DeepSeek nhanh, KHÔNG để
    M3 (~30-45s) phá UX "trả ngay" / timeout gunicorn.
    """
    reg = get_registry()
    order = DEFAULT_AGENT_PROVIDER.get(agent_id, ["zai", "deepseek", "anthropic", "mock"])
    if prefer_reasoning:
        order = ["minimax", *[p for p in order if p != "minimax"]]
    p = reg.first_configured(order)
    return p, p.default_model


def _orchestrator_triage(
    *,
    provider: LLMProvider,
    model: str,
    question: str,
    chart_summary: dict,
    explicit_agents: list[str] | None = None,
) -> tuple[list[str], str]:
    """Phase 0: Trọng tài chọn agents nào tham gia."""
    if explicit_agents:
        # User has manually picked agents.
        return [a for a in explicit_agents if a in AGENT_IDS], "User chỉ định cụ thể."

    persona = get_prompt("orchestrator")
    agent_metadata_str = "\n".join(
        f"- {aid}: {AGENT_METADATA[aid]['name_vi']} — {AGENT_METADATA[aid]['best_for']}"
        for aid in AGENT_IDS
    )
    user_msg = f"""## PHASE 0 — TRIAGE

Câu hỏi của user:
{question}

Tổng quan chart có sẵn:
```json
{json.dumps(chart_summary, ensure_ascii=False, indent=2)[:1500]}
```

Danh sách agents có thể gọi:
{agent_metadata_str}

Hãy chọn agents nào tham gia tranh luận cho câu hỏi này. Trả về JSON HỢP LỆ:
```json
{{
  "agents_to_consult": ["agent_id_1", "agent_id_2", ...],
  "reason": "Giải thích ngắn 1-2 câu tại sao chọn các agent này."
}}
```

Chọn 2-5 agent là vừa phải. Tránh gọi tất cả 7 trừ khi thực sự cross-domain.
"""

    try:
        resp = provider.chat(
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_msg},
            ],
            model=model,
            temperature=0.3,
            max_tokens=400,
        )
        content = resp.content
    except ProviderError:
        # Fallback: default to 3 mid agents.
        return ["bat_tu", "tu_vi", "lien_hoa"], "Fallback (provider lỗi)"

    # Try to parse JSON
    selected: list[str] = []
    reason = "(không parse được JSON từ Trọng tài)"
    try:
        # Find JSON block
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            obj = json.loads(content[start:end + 1])
            selected = [a for a in obj.get("agents_to_consult", []) if a in AGENT_IDS]
            reason = obj.get("reason", reason)
    except json.JSONDecodeError:
        pass

    # If parse failed, fall back to default trio.
    if not selected:
        selected = ["bat_tu", "tu_vi", "lien_hoa"]
        reason = f"Fallback (parse fail). Raw: {content[:200]}"

    return selected, reason


def _orchestrator_challenge(
    *,
    provider: LLMProvider,
    model: str,
    question: str,
    round_1_outputs: list[AgentResponse],
) -> str:
    """Phase 2: Trọng tài đọc Round 1 → đặt câu hỏi chất vấn."""
    persona = get_prompt("orchestrator")
    outputs_str = "\n\n---\n\n".join(
        f"### Agent {r.agent_name_vi} ({r.agent_id})\n{r.content}"
        for r in round_1_outputs if not r.error
    )
    user_msg = f"""## PHASE 2 — SOCRATIC CHALLENGE

Câu hỏi user: {question}

Round 1 outputs từ {len(round_1_outputs)} agents:

{outputs_str}

Hãy đọc các nhận định trên + tìm:
1. **Mâu thuẫn** giữa các agent (Đông nói X, Tây nói Y) — cần phán xét.
2. **Sáo ngữ** (agent nào nói chung chung "có thể xảy ra...") — ép cụ thể.
3. **Thiếu chi tiết** (ai chưa nói timing? ai chưa cho hành động cụ thể?) — chất vấn.

Đặt câu hỏi cụ thể cho từng agent. Một câu hỏi chuyển hoá Đông+Tây nếu có thể.

Format: Vietnamese prose, không cần JSON.
"""
    try:
        resp = provider.chat(
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_msg},
            ],
            model=model,
            temperature=0.5,
            max_tokens=800,
        )
        return resp.content
    except ProviderError as e:
        # Mark unhealthy + fall back to Mock so flow doesn't break.
        get_registry().mark_unhealthy(provider.name, str(e))
        try:
            mock = get_registry().get("mock")
            resp = mock.chat(
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": user_msg},
                ],
                model="mock-v1", temperature=0.5, max_tokens=800,
            )
            return f"[Trọng tài rơi vào Mock — {provider.name} lỗi: {e}]\n\n{resp.content}"
        except Exception:
            return f"(Trọng tài lỗi: {e})"


def _orchestrator_synthesize(
    *,
    provider: LLMProvider,
    model: str,
    question: str,
    round_1_outputs: list[AgentResponse],
    challenges: str,
    round_3_outputs: list[AgentResponse],
) -> str:
    """Phase 4: Trọng tài tổng hợp."""
    persona = get_prompt("orchestrator")
    r1 = "\n\n".join(
        f"### {r.agent_name_vi}\n{r.content}" for r in round_1_outputs if not r.error
    )
    r3 = "\n\n".join(
        f"### {r.agent_name_vi} (phản hồi)\n{r.content}"
        for r in round_3_outputs if not r.error
    )
    user_msg = f"""## PHASE 4 — SYNTHESIS

Câu hỏi user: {question}

## Round 1 (independent):
{r1}

## Round 2 (your challenges):
{challenges}

## Round 3 (agents respond):
{r3 or '(không có phản hồi — agents giữ nguyên Round 1)'}

Hãy viết báo cáo cuối theo format trong Persona orchestrator:
- **Đồng thuận** (mọi agent đồng ý)
- **Mâu thuẫn được phân định** (anh chọn bên nào + lý do)
- **Actionable Insights** (Nên làm / Cần tránh / Thời điểm / Cải vận Đông+Tây)

Vietnamese markdown.
"""
    try:
        resp = provider.chat(
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": user_msg},
            ],
            model=model,
            temperature=0.5,
            max_tokens=2000,
        )
        return resp.content
    except ProviderError as e:
        get_registry().mark_unhealthy(provider.name, str(e))
        try:
            mock = get_registry().get("mock")
            resp = mock.chat(
                messages=[
                    {"role": "system", "content": persona},
                    {"role": "user", "content": user_msg},
                ],
                model="mock-v1", temperature=0.5, max_tokens=1500,
            )
            return f"[Trọng tài fallback Mock — {provider.name} lỗi: {e}]\n\n{resp.content}"
        except Exception:
            return f"(Trọng tài lỗi giai đoạn tổng hợp: {e})"


# ─── Top-level orchestrator ──────────────────────────────────────────────────


def consult_council(
    *,
    question: str,
    chart_data: dict,
    chart_summary: dict | None = None,
    explicit_agents: list[str] | None = None,
    parallel: bool = True,
    skip_challenge: bool = False,
    persist: bool = True,
) -> dict:
    """Run full council consultation.

    Args:
        question: User's question (Vietnamese).
        chart_data: Full chart data dict — passed to each agent fully.
        chart_summary: Compact summary for Trọng tài triage (defaults to chart_data).
        explicit_agents: Override Trọng tài's triage; force specific agents.
        parallel: Run Round 1 + Round 3 agent calls in parallel (faster).
        skip_challenge: Skip Round 2/3 (cheaper, less Socratic depth).
        persist: Save session to SQLite for audit.

    Returns: CouncilSession.to_dict()
    """
    t0 = time.time()
    chart_summary = chart_summary if chart_summary is not None else chart_data

    # Phase 0: Triage
    orch_provider, orch_model = _get_orchestrator_provider()
    selected_agents, triage_reason = _orchestrator_triage(
        provider=orch_provider, model=orch_model,
        question=question, chart_summary=chart_summary,
        explicit_agents=explicit_agents,
    )

    session = CouncilSession(
        question=question,
        agents_consulted=selected_agents,
        round_0_triage_reason=triage_reason,
    )

    # Phase 1: Round 1 independent
    def _run_one(aid: str, round_label: str, challenges_text: str | None) -> AgentResponse:
        # Council = premium luận sâu → MiniMax-M3 chủ lực (prefer_reasoning).
        provider, model = _get_agent_provider(aid, prefer_reasoning=True)
        return run_agent(
            agent_id=aid, provider=provider, model=model,
            question=question, chart_data=chart_data,
            round_label=round_label, challenges=challenges_text,
        )

    if parallel and len(selected_agents) > 1:
        with ThreadPoolExecutor(max_workers=min(len(selected_agents), 4)) as pool:
            futures = {aid: pool.submit(_run_one, aid, "1", None) for aid in selected_agents}
            round_1 = [futures[aid].result() for aid in selected_agents]
    else:
        round_1 = [_run_one(aid, "1", None) for aid in selected_agents]

    session.round_1_outputs = [r.to_dict() for r in round_1]

    # Phase 2: Challenge + Phase 3: Response (optional)
    round_3: list[AgentResponse] = []
    if not skip_challenge and len(selected_agents) >= 2:
        challenges = _orchestrator_challenge(
            provider=orch_provider, model=orch_model,
            question=question, round_1_outputs=round_1,
        )
        session.round_2_challenges = challenges

        if parallel and len(selected_agents) > 1:
            with ThreadPoolExecutor(max_workers=min(len(selected_agents), 4)) as pool:
                futures = {aid: pool.submit(_run_one, aid, "3", challenges) for aid in selected_agents}
                round_3 = [futures[aid].result() for aid in selected_agents]
        else:
            round_3 = [_run_one(aid, "3", challenges) for aid in selected_agents]

        session.round_3_outputs = [r.to_dict() for r in round_3]

    # Phase 4: Synthesis
    final = _orchestrator_synthesize(
        provider=orch_provider, model=orch_model,
        question=question, round_1_outputs=round_1,
        challenges=session.round_2_challenges, round_3_outputs=round_3,
    )
    session.final_synthesis = final

    # Bookkeeping
    all_outputs = round_1 + round_3
    session.total_tokens = sum(r.total_tokens for r in all_outputs)
    session.providers_used = {
        r.agent_id: r.provider for r in all_outputs if r.provider
    }
    session.providers_used["orchestrator"] = orch_provider.name
    session.duration_ms = int((time.time() - t0) * 1000)

    # Persist
    if persist:
        try:
            payload = session.to_dict()
            payload["chart_summary"] = chart_summary
            session.session_id = _save_session(payload)
        except Exception:
            pass

    return session.to_dict()


def list_recent_sessions(limit: int = 20) -> list[dict]:
    """Return last N council sessions for audit/review."""
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        rows = conn.execute(
            """SELECT id, created_at, question, agents_consulted,
                      total_tokens, providers_used, duration_ms
               FROM sessions ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [
        {
            "id": r[0],
            "created_at": r[1],
            "question": r[2],
            "agents_consulted": json.loads(r[3]),
            "total_tokens": r[4],
            "providers_used": json.loads(r[5]) if r[5] else {},
            "duration_ms": r[6],
        }
        for r in rows
    ]


def get_session(session_id: int) -> dict | None:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        row = conn.execute(
            """SELECT created_at, question, chart_summary, agents_consulted,
                      round_1_outputs, round_2_challenges, round_3_outputs,
                      final_synthesis, total_tokens, providers_used, duration_ms
               FROM sessions WHERE id=?""",
            (session_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": session_id,
        "created_at": row[0],
        "question": row[1],
        "chart_summary": json.loads(row[2]) if row[2] else {},
        "agents_consulted": json.loads(row[3]),
        "round_1_outputs": json.loads(row[4]),
        "round_2_challenges": row[5],
        "round_3_outputs": json.loads(row[6]),
        "final_synthesis": row[7],
        "total_tokens": row[8],
        "providers_used": json.loads(row[9]) if row[9] else {},
        "duration_ms": row[10],
    }
