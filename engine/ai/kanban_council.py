"""Kanban-based Council orchestration for YI-CHRONOS.

Replaces the synchronous engine/ai/council.py 3-round Socratic flow with a
durable Hermes Kanban work queue:

- **P1 fan-out**: 1 sage = 1 task, all parallel (OS process per worker)
- **P3 quorum (fan-in)**: arbiter task linked from all sage tasks; only
  becomes ready when ALL sages complete
- **Durable**: every handoff is a row in SQLite; survives restarts
- **Observable**: anyone can read kanban.db to see partial progress
- **Human-interpose-able**: comment / block / unblock / reassign at any time

The dispatcher (`hermes kanban daemon`) is responsible for actually spawning
sage workers — see scripts/yi-council-daemon.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HERMES_HOME = PROJECT_ROOT / "data" / "hermes_yi"
HERMES_BIN = PROJECT_ROOT / "vendor" / "hermes-agent" / ".venv" / "bin" / "hermes"
KANBAN_DB = HERMES_HOME / "kanban" / "boards" / "yi-chronos" / "kanban.db"

# Map internal sage tag → kanban profile name
SAGES_BY_TAG: dict[str, str] = {
    "mai_hoa": "mai-hoa-sage",
    "luc_hao": "luc-hao-sage",
    "lien_hoa": "lien-hoa-sage",
    "tu_vi": "tu-vi-sage",
    "bat_tu": "bat-tu-sage",
    "ha_lac": "ha-lac-sage",
    "western": "chiem-tinh-sage",
    "than_so": "than-so-sage",
    "chieu_dom": "chieu-dom-kinh-sage",   # Tử Vi Bắc phái / 18 Phi Tinh (nội tâm)
    "thiet_ban": "thiet-ban-sage",        # Thiết Bản Thần Số — dịch điều văn + lời bình
}
ARBITER_PROFILE = "arbiter"


# ─── Routing heuristic (replaces orchestrator LLM call for cheap path) ───────


def select_sages(question: str) -> list[str]:
    """Heuristic sage selection based on Vietnamese keywords.

    Mirrors yi-orchestrator's SOUL.md routing table without spending an LLM
    call. For deeper routing, the orchestrator profile can be invoked
    explicitly via a kanban task assigned to `yi-orchestrator`.
    """
    q = question.lower()
    # Long-term destiny
    long_kw = ("đời", "sự nghiệp", "vận", "mệnh", "đại vận", "cách cục", "cung mệnh")
    # Short-term timing
    short_kw = ("tuần", "tháng này", "hôm nay", "ngày mai", "sắp", "đang", "ngắn hạn")
    # Psychology / inner
    psych_kw = ("tâm lý", "cảm xúc", "nội tâm", "quan hệ", "tình cảm", "yêu")

    long_hit = any(k in q for k in long_kw)
    short_hit = any(k in q for k in short_kw)
    psych_hit = any(k in q for k in psych_kw)

    sages: list[str] = []
    if short_hit:
        sages += ["mai_hoa", "luc_hao", "lien_hoa"]
    if long_hit:
        sages += ["tu_vi", "bat_tu", "ha_lac"]
    if psych_hit:
        sages += ["western", "bat_tu"]

    if not sages:
        # Cross-domain default: 4 most representative
        sages = ["mai_hoa", "bat_tu", "tu_vi", "western"]

    # Dedupe preserving order
    seen: set[str] = set()
    return [s for s in sages if not (s in seen or seen.add(s))]


# ─── Hermes CLI wrapper ──────────────────────────────────────────────────────


def _hermes_env() -> dict:
    env = os.environ.copy()
    env["HERMES_HOME"] = str(HERMES_HOME)
    return env


def _run_hermes(args: list[str], *, json_out: bool = True, timeout: int = 30) -> dict | str:
    cmd = [str(HERMES_BIN), *args]
    if json_out and "--json" not in args:
        cmd.append("--json")
    result = subprocess.run(
        cmd, env=_hermes_env(), capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"hermes {' '.join(args)} failed (rc={result.returncode}): {result.stderr.strip()}"
        )
    if json_out:
        return json.loads(result.stdout)
    return result.stdout.strip()


def _kanban_create(
    title: str,
    *,
    assignee: str,
    body: str = "",
    parent: str | None = None,
    priority: int = 0,
    idempotency_key: str | None = None,
) -> str:
    args = ["kanban", "create", title, "--assignee", assignee]
    if body:
        args += ["--body", body]
    if parent:
        args += ["--parent", parent]
    if priority:
        args += ["--priority", str(priority)]
    if idempotency_key:
        args += ["--idempotency-key", idempotency_key]
    out = _run_hermes(args)
    return out["id"]  # type: ignore[index]


def _kanban_link(parent_id: str, child_id: str) -> None:
    _run_hermes(["kanban", "link", parent_id, child_id], json_out=False)


# ─── Session model ───────────────────────────────────────────────────────────


@dataclass
class CouncilSession:
    """One council consultation = N sage tasks + 1 arbiter task."""

    question: str
    sage_task_ids: dict[str, str]      # sage_tag -> kanban task id
    arbiter_id: str                    # poll this for final synthesis
    soul_key: str = "_anon"

    @property
    def root_id(self) -> str:
        """Public ID clients poll on (= arbiter)."""
        return self.arbiter_id

    def to_dict(self) -> dict:
        return asdict(self) | {"root_id": self.root_id}


# ─── Public API ──────────────────────────────────────────────────────────────


def _build_sage_body(
    *,
    question: str,
    sage_tag: str,
    precast: dict | None,
    soul_key: str,
    chart_context: dict | None,
) -> str:
    """Build sage task body — embeds engine-computed JSON with explicit
    'DO NOT RECOMPUTE' instructions so sage focuses on read/gap/improve."""
    lines = [
        f"## Câu hỏi từ user (soul_key={soul_key})",
        "",
        question,
        "",
        "## ⚠️ INPUT từ engine YI-CHRONOS",
        "",
        f"Engine đã cast sẵn cho trường phái `{sage_tag}`. "
        "**KHÔNG được cast lại / gieo lại / tính lại Tứ Trụ**. "
        "Đọc JSON dưới đây và diễn giải.",
        "",
    ]
    if precast:
        lines += [
            f"### precast_data ({sage_tag})",
            "```json",
            json.dumps(precast, ensure_ascii=False, indent=2),
            "```",
        ]
    else:
        lines += [
            "**LƯU Ý**: không có precast_data cho task này — engine chưa "
            f"có cast function cho `{sage_tag}` hoặc client không cung cấp. "
            "Đánh dấu rõ trong `GAP.engine_gap`.",
        ]
    if chart_context:
        lines += [
            "",
            "### chart_context (shared)",
            "```json",
            json.dumps(chart_context, ensure_ascii=False, indent=2),
            "```",
        ]

    # ─── LEXICON CONTEXT (lexical pre-extraction → cost reduction) ──────────
    # Parse user question through YI-Lexicon to pre-resolve symbolic mappings.
    # Sage receives "tokens already resolved to ngũ hành / bát quái / mai hoa"
    # → KHÔNG cần re-derive symbolism → output token ↓ 30-50%.
    try:
        from engine.yi_lexicon.parser import interpret_observation
        lex_ctx = interpret_observation(question)
        if lex_ctx.tokens or lex_ctx.numbers_extracted or lex_ctx.time_context:
            lines += [
                "",
                "## 📚 LEXICON CONTEXT (đã pre-extract — KHÔNG cần re-derive)",
                "",
                "Hệ thống YI-Lexicon đã nhận diện sẵn các ánh xạ symbolic trong câu hỏi. "
                "Anh CHỈ tập trung **luận đoán tổng hợp + cá nhân hoá**, KHÔNG lặp lại "
                "phần \"X thuộc hành Y\" / \"Z là quẻ W\" — đã có sẵn dưới đây:",
                "",
                f"**Tóm tắt symbolic**: {lex_ctx.narrative_summary}",
                "",
            ]
            if lex_ctx.tokens:
                lines.append("**Token → concept → mapping**:")
                for t in lex_ctx.tokens[:10]:
                    if t.mappings:
                        m_strs = [f"{m.dim_type}={m.dim_value}" for m in t.mappings[:3]]
                        lines.append(f"  - `{t.token}` → **{t.canonical_vi}** ({t.concept_type}) → " + " | ".join(m_strs))
                    else:
                        lines.append(f"  - `{t.token}` → **{t.canonical_vi}** ({t.concept_type})")
                lines.append("")
            if lex_ctx.mai_hoa_candidate:
                mh = lex_ctx.mai_hoa_candidate
                lines += [
                    f"**Mai Hoa sơ bộ**: trên {mh['upper_quai']} / dưới {mh['lower_quai']}, hào động {mh['moving_line']}",
                    f"  (từ số {mh['source_numbers']}, hour rank {mh.get('hour_branch_rank')})",
                    "",
                ]
    except Exception:
        # Lexicon failure should not break sage spawn — silent skip
        pass

    lines += [
        "",
        "## OUTPUT bắt buộc",
        "Theo đúng format `READ → GAP → IMPROVE` quy định trong SOUL.md của anh.",
        "→ Tận dụng LEXICON CONTEXT ở trên: KHÔNG cần re-derive 'lá thuộc Mộc'. "
        "Đi thẳng vào TẦNG NGHĨA sâu + áp dụng cho user cụ thể.",
    ]
    return "\n".join(lines)


def consult(
    question: str,
    *,
    sages: list[str] | None = None,
    precast_data: dict[str, dict] | None = None,
    chart_context: dict | None = None,
    soul_key: str = "_anon",
) -> CouncilSession:
    """Create kanban tasks for a P3-quorum council consultation.

    Pattern (per Hermes Kanban v1 spec §5.3):
    - N sage tasks, no inter-deps, same shape, different assignees → P1 fan-out
    - 1 arbiter task linked as CHILD of all N sages → only ready when all done

    Each sage receives engine-precomputed JSON (`precast_data[tag]`) as INPUT
    and is instructed NOT to recompute — they focus on `READ / GAP / IMPROVE`.

    Args:
        question: User's question (Vietnamese).
        sages: Explicit sage tags. If None, derived from question keywords.
        precast_data: {sage_tag: engine_output_dict}. Optional but recommended.
        chart_context: Shared context (e.g. soul_key facts, recent topics).
        soul_key: User identifier for memory.

    The kanban dispatcher (`hermes kanban daemon`) picks tasks up and spawns
    one OS process per sage profile, each with its own HERMES_HOME.
    """
    sages_chosen = sages if sages is not None else select_sages(question)
    if not sages_chosen:
        raise ValueError("No sages selected and no defaults — pass sages= explicitly.")
    unknown = [s for s in sages_chosen if s not in SAGES_BY_TAG]
    if unknown:
        raise ValueError(f"Unknown sage tags: {unknown}")

    precast_data = precast_data or {}

    # 1. Fan-out: one task per sage with sage-specific precast JSON
    sage_task_ids: dict[str, str] = {}
    for tag in sages_chosen:
        profile = SAGES_BY_TAG[tag]
        title = f"[{tag}] {question[:80]}"
        body = _build_sage_body(
            question=question,
            sage_tag=tag,
            precast=precast_data.get(tag),
            soul_key=soul_key,
            chart_context=chart_context,
        )
        tid = _kanban_create(title=title, assignee=profile, body=body)
        sage_task_ids[tag] = tid

    # 2. Arbiter task — child of all sages (P3 quorum aggregator)
    arbiter_body = "\n".join([
        f"## Câu hỏi từ user (soul_key={soul_key})",
        "",
        question,
        "",
        f"## Nhiệm vụ — Tổng hợp {len(sages_chosen)} sage",
        "",
        "Parent task results (theo thứ tự link) chứa output của từng sage "
        "theo format `READ → GAP → IMPROVE`. Anh chỉ cần:",
        "",
        "1. **Tổng hợp READ** — diễn giải hợp nhất cho user (đồng thuận + "
        "mâu thuẫn phân định).",
        "2. **Bốc tách improve_user** từ mọi sage → action plan tổng.",
        "3. **KHÔNG xử lý improve_system** — phần đó đã được hệ thống auto-collect.",
        "",
        "Output theo format quy định trong SOUL.md của anh.",
    ])
    arbiter_id = _kanban_create(
        title=f"[arbiter] Tổng hợp: {question[:60]}",
        assignee=ARBITER_PROFILE,
        body=arbiter_body,
        priority=10,  # arbiter gets dispatched ahead once ready
    )
    for sage_tid in sage_task_ids.values():
        _kanban_link(parent_id=sage_tid, child_id=arbiter_id)

    return CouncilSession(
        question=question,
        sage_task_ids=sage_task_ids,
        arbiter_id=arbiter_id,
        soul_key=soul_key,
    )


# ─── Read path: direct SQLite (faster than CLI for polling) ──────────────────


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(KANBAN_DB))
    conn.row_factory = sqlite3.Row
    return conn


def task_status(task_id: str) -> dict | None:
    """Return a minimal status row for one task, or None if missing.

    Hermes Kanban stores worker output via `kanban_complete(summary=...)`
    in `task_runs.summary`, not `tasks.result`. We surface the latest
    completed-run summary as `result` so downstream code (snapshot, harvest)
    can read it uniformly.
    """
    with _db() as c:
        row = c.execute(
            "SELECT id, title, assignee, status, started_at, completed_at, result "
            "FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        # Fallback: latest completed run's summary
        if not data.get("result"):
            run = c.execute(
                "SELECT summary FROM task_runs "
                "WHERE task_id = ? AND status = 'done' AND summary IS NOT NULL "
                "ORDER BY ended_at DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if run and run["summary"]:
                data["result"] = run["summary"]
        return data


def session_snapshot(
    session: CouncilSession,
    *,
    harvest: bool = True,
    auto_distill: bool = True,
) -> dict:
    """Full status snapshot. Two side-effects (both safe + idempotent):

    1. If `harvest=True`, auto-extract `improve_system` items from completed
       sage tasks into the critique DB.
    2. If `auto_distill=True` AND arbiter just completed for the first time,
       fire a background thread to distill knowledge from sage outputs into
       the YI-Lexicon. Atomic claim prevents double-firing on repeated polls.
    """
    from engine.ai import critique_store as cs  # local import to avoid cycle

    sages_view = {}
    harvested_now: dict[str, int] = {}
    for tag, tid in session.sage_task_ids.items():
        status = task_status(tid) or {}
        sage_result = status.get("result")
        sages_view[tag] = {
            "task_id": tid,
            "profile": SAGES_BY_TAG[tag],
            "status": status.get("status"),
            "started_at": status.get("started_at"),
            "completed_at": status.get("completed_at"),
            "result": sage_result,
        }
        # Auto-harvest improve_system on first sight of done + result
        if harvest and status.get("status") == "done" and sage_result:
            ids = cs.harvest_from_sage_task(
                root_id=session.root_id,
                sage_tag=tag,
                task_id=tid,
                sage_output=sage_result,
            )
            if ids:
                harvested_now[tag] = len(ids)

    arb_status = task_status(session.arbiter_id) or {}
    arbiter_view = {
        "task_id": session.arbiter_id,
        "profile": ARBITER_PROFILE,
        "status": arb_status.get("status"),
        "started_at": arb_status.get("started_at"),
        "completed_at": arb_status.get("completed_at"),
        "result": arb_status.get("result"),
    }

    sages_done = sum(1 for s in sages_view.values() if s["status"] == "done")
    complete = arbiter_view["status"] == "done"

    # Auto-distill: fire once when arbiter first completes.
    distill_fired = False
    if auto_distill and complete:
        try:
            distill_fired = _maybe_fire_auto_distill(session.root_id)
        except Exception:
            import logging
            logging.exception(f"auto-distill claim failed for {session.root_id}")

    return {
        "session": session.to_dict(),
        "sages": sages_view,
        "arbiter": arbiter_view,
        "progress": {
            "sages_done": sages_done,
            "sages_total": len(sages_view),
            "arbiter_status": arbiter_view["status"],
            "complete": complete,
        },
        "harvested_critiques": harvested_now,
        "auto_distill": {
            "fired_this_call": distill_fired,
            "status_snapshot": get_distill_status(session.root_id),
        },
    }


def get_synthesis(session: CouncilSession) -> str | None:
    """Return arbiter's final report, or None if not done yet."""
    arb = task_status(session.arbiter_id)
    if arb and arb.get("status") == "done":
        return arb.get("result")
    return None


# ─── Optional: persist session metadata (so /api can poll later by id) ──────


_SESSIONS_DB = HERMES_HOME / "council_sessions.sqlite3"


def _ensure_sessions_db() -> None:
    _SESSIONS_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_SESSIONS_DB) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS sessions (
                root_id     TEXT PRIMARY KEY,
                question    TEXT NOT NULL,
                soul_key    TEXT,
                arbiter_id  TEXT NOT NULL,
                sage_tasks  TEXT NOT NULL,
                created_at  INTEGER NOT NULL
            )"""
        )
        # Migration: lexicon distillation tracking (anh, 2026-05-12)
        cols = [r[1] for r in c.execute("PRAGMA table_info(sessions)").fetchall()]
        if "lexicon_distilled" not in cols:
            c.execute("ALTER TABLE sessions ADD COLUMN lexicon_distilled TEXT")
            # NULL=untouched, 'pending'=claimed (in-flight), 'done'=completed, 'failed'=error
        if "lexicon_distilled_at" not in cols:
            c.execute("ALTER TABLE sessions ADD COLUMN lexicon_distilled_at INTEGER")
        if "lexicon_concepts_added" not in cols:
            c.execute("ALTER TABLE sessions ADD COLUMN lexicon_concepts_added INTEGER DEFAULT 0")
        if "lexicon_mappings_added" not in cols:
            c.execute("ALTER TABLE sessions ADD COLUMN lexicon_mappings_added INTEGER DEFAULT 0")


def _try_claim_distill(root_id: str) -> bool:
    """Atomic claim — returns True if we won the race to distill this session.

    NULL → 'pending'. If status was already 'pending'/'done'/'failed' → returns False.
    """
    _ensure_sessions_db()
    with sqlite3.connect(_SESSIONS_DB) as c:
        cur = c.execute(
            "UPDATE sessions SET lexicon_distilled='pending' "
            "WHERE root_id=? AND lexicon_distilled IS NULL",
            (root_id,),
        )
        return cur.rowcount > 0


def _mark_distill_result(root_id: str, *, status: str, concepts: int = 0, mappings: int = 0) -> None:
    """Update distill result after completion. status ∈ {'done', 'failed'}."""
    import time
    _ensure_sessions_db()
    with sqlite3.connect(_SESSIONS_DB) as c:
        c.execute(
            "UPDATE sessions SET lexicon_distilled=?, lexicon_distilled_at=?, "
            "lexicon_concepts_added=?, lexicon_mappings_added=? WHERE root_id=?",
            (status, int(time.time()), concepts, mappings, root_id),
        )


def get_distill_status(root_id: str) -> dict | None:
    """Query distill status for a council session."""
    _ensure_sessions_db()
    with sqlite3.connect(_SESSIONS_DB) as c:
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT lexicon_distilled, lexicon_distilled_at, "
            "lexicon_concepts_added, lexicon_mappings_added "
            "FROM sessions WHERE root_id = ?",
            (root_id,),
        ).fetchone()
    return dict(row) if row else None


def _run_distill_thread(root_id: str) -> None:
    """Background-thread target: actually run the distillation."""
    try:
        from engine.yi_lexicon.distill import distill_from_council
        result = distill_from_council(root_id)
        _mark_distill_result(
            root_id,
            status="done" if not result.errors else "failed",
            concepts=result.concepts_added,
            mappings=result.mappings_added,
        )
    except Exception:
        import logging
        logging.exception(f"auto-distill failed for {root_id}")
        _mark_distill_result(root_id, status="failed")


def _maybe_fire_auto_distill(root_id: str) -> bool:
    """If this is the first time we see arbiter done, claim + fire background distill.

    Returns True if we fired a new distill thread, False if already claimed/done.
    """
    import threading
    if not _try_claim_distill(root_id):
        return False
    threading.Thread(
        target=_run_distill_thread, args=(root_id,), daemon=True,
    ).start()
    return True


def save_session(session: CouncilSession) -> None:
    _ensure_sessions_db()
    import time

    with sqlite3.connect(_SESSIONS_DB) as c:
        c.execute(
            "INSERT OR REPLACE INTO sessions "
            "(root_id, question, soul_key, arbiter_id, sage_tasks, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                session.root_id,
                session.question,
                session.soul_key,
                session.arbiter_id,
                json.dumps(session.sage_task_ids),
                int(time.time()),
            ),
        )


def load_session(root_id: str) -> CouncilSession | None:
    _ensure_sessions_db()
    with sqlite3.connect(_SESSIONS_DB) as c:
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT * FROM sessions WHERE root_id = ?", (root_id,)
        ).fetchone()
    if not row:
        return None
    return CouncilSession(
        question=row["question"],
        sage_task_ids=json.loads(row["sage_tasks"]),
        arbiter_id=row["arbiter_id"],
        soul_key=row["soul_key"] or "_anon",
    )


def list_recent_sessions(limit: int = 20) -> list[dict]:
    _ensure_sessions_db()
    with sqlite3.connect(_SESSIONS_DB) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            "SELECT root_id, question, soul_key, created_at "
            "FROM sessions ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
