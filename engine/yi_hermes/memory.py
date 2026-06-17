"""YI-Hermes Memory — cross-session knowledge about user.

3 layers of memory:

1. **User Facts** — discrete facts extracted from chat
   ("Anh chuyển việc 2017", "Vợ anh tên Hoa, sinh 1987")
2. **Chat Summaries** — short summary of each session, full-text searchable
   (FTS5 trên SQLite · GIN to_tsvector trên Postgres).
3. **Glossary Views** — log which terms user viewed/asked about.

P0-2c (2026-06-17): chuyển từ sqlite3 trực tiếp → engine.db (dual-driver).
QUY TẮC HỢP NHẤT: nếu `DATABASE_URL` (Postgres) được set → memory dùng DB hợp nhất
đó; nếu không → giữ NGUYÊN file lịch sử `data/yi_hermes/memory.sqlite3` (non-breaking
trên dev/prod-sqlite, KHÔNG mất dữ liệu Hermes). Đây là module server-side theo
user_id tường minh → session_scope(service=True).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Lock

from sqlalchemy import text

from engine.db import get_engine, is_postgres

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "memory.sqlite3"
_lock = Lock()


def _mem_url() -> str:
    """Postgres hợp nhất nếu DATABASE_URL set; ngược lại file memory.sqlite3 lịch sử."""
    return os.environ.get("DATABASE_URL", "").strip() or f"sqlite:///{_DB_PATH}"


def _is_pg() -> bool:
    return is_postgres(_mem_url())


@contextmanager
def _scope():
    """Transaction + (Postgres) GUC service-mode (memory là op server-side theo uid)."""
    eng = get_engine(_mem_url())
    with eng.begin() as conn:
        if _is_pg():
            conn.execute(text("SELECT set_config('app.service_mode','on',true)"))
        yield conn


def _json_expr(col: str) -> str:
    return f"CAST(:{col} AS JSONB)" if _is_pg() else f":{col}"


def _as_list(v):
    if v is None or isinstance(v, list):
        return v or []
    try:
        return json.loads(v)
    except Exception:
        return []


# Fact categories
CATEGORY_EVENT = "event"
CATEGORY_PREFERENCE = "preference"
CATEGORY_RELATION = "relation"
CATEGORY_BELIEF = "belief"
CATEGORY_GOAL = "goal"
CATEGORY_HEALTH = "health"
CATEGORY_OTHER = "other"

CATEGORIES = (
    CATEGORY_EVENT, CATEGORY_PREFERENCE, CATEGORY_RELATION,
    CATEGORY_BELIEF, CATEGORY_GOAL, CATEGORY_HEALTH, CATEGORY_OTHER,
)


@dataclass(frozen=True)
class UserFact:
    id: int | None
    user_id: str
    fact: str
    category: str
    confidence: float
    source_session_id: int | None
    extracted_at: str
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ChatSummary:
    id: int | None
    user_id: str
    session_id: int | None
    summary: str
    key_topics: list[str]
    chart_data_hash: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def _ensure_db() -> None:
    """SQLite: tạo bảng + FTS5 trên file memory.sqlite3 lịch sử. Postgres: no-op
    (bảng user_facts/chat_summaries/glossary_views từ db/postgres/schema.sql)."""
    if _is_pg():
        return
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL, fact TEXT NOT NULL, category TEXT,
                confidence REAL DEFAULT 0.8, source_session_id INTEGER, notes TEXT,
                extracted_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_user ON user_facts(user_id)")
        conn.execute(
            """CREATE TABLE IF NOT EXISTS chat_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL, session_id INTEGER, summary TEXT NOT NULL,
                key_topics TEXT, chart_data_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_summaries_user ON chat_summaries(user_id)")
        try:
            conn.execute(
                """CREATE VIRTUAL TABLE IF NOT EXISTS summaries_fts USING fts5(
                    summary, key_topics, content='chat_summaries', content_rowid='id')"""
            )
            conn.execute(
                """CREATE TRIGGER IF NOT EXISTS summaries_ai AFTER INSERT ON chat_summaries
                   BEGIN INSERT INTO summaries_fts(rowid, summary, key_topics)
                     VALUES (new.id, new.summary, new.key_topics); END"""
            )
            conn.execute(
                """CREATE TRIGGER IF NOT EXISTS summaries_ad AFTER DELETE ON chat_summaries
                   BEGIN INSERT INTO summaries_fts(summaries_fts, rowid, summary, key_topics)
                     VALUES('delete', old.id, old.summary, old.key_topics); END"""
            )
            conn.execute(
                """CREATE TRIGGER IF NOT EXISTS summaries_au AFTER UPDATE ON chat_summaries
                   BEGIN
                     INSERT INTO summaries_fts(summaries_fts, rowid, summary, key_topics)
                       VALUES('delete', old.id, old.summary, old.key_topics);
                     INSERT INTO summaries_fts(rowid, summary, key_topics)
                       VALUES (new.id, new.summary, new.key_topics);
                   END"""
            )
        except sqlite3.OperationalError:
            pass
        conn.execute(
            """CREATE TABLE IF NOT EXISTS glossary_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL, term_vi TEXT NOT NULL,
                viewed_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
        )


# ─── User Facts ───────────────────────────────────────────────────────────────


def add_fact(
    *,
    user_id: str,
    fact: str,
    category: str = CATEGORY_OTHER,
    confidence: float = 0.8,
    source_session_id: int | None = None,
    notes: str = "",
) -> int:
    """Insert a new fact about the user. Returns fact ID."""
    if not user_id or not fact.strip():
        raise ValueError("user_id and fact required")
    if category not in CATEGORIES:
        category = CATEGORY_OTHER
    _ensure_db()
    with _lock, _scope() as conn:
        return conn.execute(
            text("""INSERT INTO user_facts
                    (user_id, fact, category, confidence, source_session_id, notes)
                    VALUES (:uid,:fact,:cat,:conf,:ssid,:notes) RETURNING id"""),
            {"uid": user_id, "fact": fact.strip(), "cat": category, "conf": confidence,
             "ssid": source_session_id, "notes": notes},
        ).scalar()


def list_facts(
    user_id: str,
    *,
    category: str | None = None,
    limit: int = 50,
    query_hint: str = "",
) -> list[UserFact]:
    """Recent facts first; when `query_hint` given, blend recency with relevance."""
    _ensure_db()
    fetch = max(limit * 4, 40) if query_hint.strip() else limit
    sql = ("SELECT id, user_id, fact, category, confidence, source_session_id, "
           "extracted_at, COALESCE(notes,'') FROM user_facts WHERE user_id=:uid")
    params: dict = {"uid": user_id}
    if category:
        sql += " AND category=:cat"
        params["cat"] = category
    sql += " ORDER BY extracted_at DESC, id DESC LIMIT :lim"
    params["lim"] = fetch
    with _scope() as conn:
        rows = conn.execute(text(sql), params).fetchall()
    facts = [
        UserFact(id=r[0], user_id=r[1], fact=r[2], category=r[3], confidence=r[4],
                 source_session_id=r[5], extracted_at=str(r[6]), notes=r[7])
        for r in rows
    ]
    if query_hint.strip() and facts:
        hint_tokens = {t for t in re.findall(r"\w+", query_hint.lower()) if len(t) > 1}
        if hint_tokens:
            def _relevance(f: UserFact) -> int:
                fact_tokens = set(re.findall(r"\w+", f"{f.fact} {f.category}".lower()))
                return len(hint_tokens & fact_tokens)
            facts.sort(key=_relevance, reverse=True)
        facts = facts[:limit]
    return facts


def delete_fact(fact_id: int) -> bool:
    _ensure_db()
    with _lock, _scope() as conn:
        return conn.execute(
            text("DELETE FROM user_facts WHERE id=:id"), {"id": fact_id}
        ).rowcount > 0


def update_fact(fact_id: int, fact: str | None = None, category: str | None = None) -> bool:
    _ensure_db()
    sets, params = [], {"id": fact_id}
    if fact:
        sets.append("fact=:fact")
        params["fact"] = fact.strip()
    if category in CATEGORIES:
        sets.append("category=:cat")
        params["cat"] = category
    if not sets:
        return False
    with _lock, _scope() as conn:
        return conn.execute(
            text(f"UPDATE user_facts SET {', '.join(sets)} WHERE id=:id"), params
        ).rowcount > 0


def fact_categories_summary(user_id: str) -> dict[str, int]:
    _ensure_db()
    with _scope() as conn:
        rows = conn.execute(
            text("SELECT category, COUNT(*) FROM user_facts WHERE user_id=:uid GROUP BY category"),
            {"uid": user_id},
        ).fetchall()
    return {r[0]: r[1] for r in rows}


# ─── Chat Summaries ───────────────────────────────────────────────────────────


def add_summary(
    *,
    user_id: str,
    summary: str,
    session_id: int | None = None,
    key_topics: list[str] | None = None,
    chart_data_hash: str = "",
) -> int:
    if not user_id or not summary.strip():
        raise ValueError("user_id and summary required")
    _ensure_db()
    topics_json = json.dumps(key_topics or [], ensure_ascii=False)
    with _lock, _scope() as conn:
        return conn.execute(
            text(f"""INSERT INTO chat_summaries
                    (user_id, session_id, summary, key_topics, chart_data_hash)
                    VALUES (:uid,:sid,:summary,{_json_expr('kt')},:hash) RETURNING id"""),
            {"uid": user_id, "sid": session_id, "summary": summary.strip(),
             "kt": topics_json, "hash": chart_data_hash},
        ).scalar()


def list_summaries(user_id: str, limit: int = 20) -> list[ChatSummary]:
    """Recent summaries first."""
    _ensure_db()
    with _scope() as conn:
        rows = conn.execute(
            text("""SELECT id, user_id, session_id, summary, key_topics,
                           COALESCE(chart_data_hash,''), created_at
                    FROM chat_summaries WHERE user_id=:uid ORDER BY id DESC LIMIT :lim"""),
            {"uid": user_id, "lim": limit},
        ).fetchall()
    return [_row_to_summary(r) for r in rows]


def _row_to_summary(r) -> ChatSummary:
    return ChatSummary(
        id=r[0], user_id=r[1], session_id=r[2], summary=r[3],
        key_topics=_as_list(r[4]), chart_data_hash=r[5], created_at=str(r[6]),
    )


def search_summaries(user_id: str, query: str, limit: int = 5) -> list[ChatSummary]:
    """Full-text search: Postgres GIN to_tsvector · SQLite FTS5; LIKE fallback."""
    _ensure_db()
    cols = ("s.id, s.user_id, s.session_id, s.summary, s.key_topics, "
            "COALESCE(s.chart_data_hash,''), s.created_at")
    with _scope() as conn:
        if _is_pg():
            # tsvector gộp summary + key_topics (parity với SQLite FTS — nếu chỉ
            # summary thì topic-only match bị mất). key_topics là JSONB → ::text.
            tsv = ("to_tsvector('simple', coalesce(s.summary,'') || ' ' || "
                   "coalesce(s.key_topics::text,''))")
            rows = conn.execute(
                text(f"""SELECT {cols} FROM chat_summaries s
                         WHERE s.user_id=:uid
                           AND {tsv} @@ plainto_tsquery('simple', :q)
                         ORDER BY ts_rank({tsv}, plainto_tsquery('simple', :q)) DESC
                         LIMIT :lim"""),
                {"uid": user_id, "q": query, "lim": limit},
            ).fetchall()
            if rows:
                return [_row_to_summary(r) for r in rows]
            # fallback LIKE (query rỗng/không match tsquery) — cũng phủ key_topics
            rows = conn.execute(
                text(f"SELECT {cols} FROM chat_summaries s WHERE s.user_id=:uid "
                     f"AND (s.summary ILIKE :pat OR s.key_topics::text ILIKE :pat) "
                     f"ORDER BY s.id DESC LIMIT :lim"),
                {"uid": user_id, "pat": f"%{query}%", "lim": limit},
            ).fetchall()
            return [_row_to_summary(r) for r in rows]
        # SQLite: FTS5, fallback LIKE
        try:
            rows = conn.execute(
                text(f"""SELECT {cols} FROM summaries_fts f
                         JOIN chat_summaries s ON s.id = f.rowid
                         WHERE summaries_fts MATCH :q AND s.user_id=:uid
                         ORDER BY rank LIMIT :lim"""),
                {"q": query, "uid": user_id, "lim": limit},
            ).fetchall()
        except Exception:
            rows = conn.execute(
                text(f"SELECT {cols.replace('s.','')} FROM chat_summaries "
                     f"WHERE user_id=:uid AND (summary LIKE :pat OR key_topics LIKE :pat) "
                     f"ORDER BY id DESC LIMIT :lim"),
                {"uid": user_id, "pat": f"%{query}%", "lim": limit},
            ).fetchall()
    return [_row_to_summary(r) for r in rows]


# ─── Glossary Views (tracking) ────────────────────────────────────────────────


def log_glossary_view(user_id: str, term_vi: str) -> None:
    if not user_id or not term_vi:
        return
    _ensure_db()
    with _lock, _scope() as conn:
        conn.execute(
            text("INSERT INTO glossary_views (user_id, term_vi) VALUES (:uid,:term)"),
            {"uid": user_id, "term": term_vi},
        )


def top_viewed_terms(user_id: str, limit: int = 10) -> list[tuple[str, int]]:
    _ensure_db()
    with _scope() as conn:
        rows = conn.execute(
            text("""SELECT term_vi, COUNT(*) c FROM glossary_views
                    WHERE user_id=:uid GROUP BY term_vi ORDER BY c DESC LIMIT :lim"""),
            {"uid": user_id, "lim": limit},
        ).fetchall()
    return [(r[0], r[1]) for r in rows]


# ─── Context injection for chat ───────────────────────────────────────────────


def build_memory_context(user_id: str, query_hint: str = "") -> str:
    """Build a memory context block for system prompt injection."""
    if not user_id:
        return ""

    facts = list_facts(user_id, limit=5, query_hint=query_hint)
    summaries = (
        search_summaries(user_id, query_hint, limit=3)
        if query_hint else list_summaries(user_id, limit=3)
    )
    top_terms = top_viewed_terms(user_id, limit=5)

    if not (facts or summaries or top_terms):
        return ""

    parts = ["## Bộ nhớ về user (Memory)"]
    if facts:
        parts.append("**Facts nhớ được:**")
        for f in facts:
            parts.append(f"- [{f.category}] {f.fact} (conf {f.confidence:.1f})")
    if summaries:
        parts.append("**Tóm tắt phiên trước:**")
        for s in summaries:
            topics_str = f" ({', '.join(s.key_topics)})" if s.key_topics else ""
            parts.append(f"- {s.summary}{topics_str}")
    if top_terms:
        terms_str = ", ".join(f"{t}×{c}" for t, c in top_terms)
        parts.append(f"**User hay xem terms:** {terms_str}")
    return "\n".join(parts)


def session_signals_from_turns(turns: list[dict]) -> dict:
    """Heuristically extract soul-evolution signals from a finished chat session."""
    schools_map = {
        "tử vi": "tu_vi", "tu vi": "tu_vi",
        "bát tự": "bat_tu", "bat tu": "bat_tu",
        "liên hoa": "lien_hoa", "lien hoa": "lien_hoa",
        "lục hào": "luc_hao", "luc hao": "luc_hao",
        "mai hoa": "mai_hoa",
        "hà lạc": "ha_lac", "ha lac": "ha_lac",
        "chiêm tinh": "western", "western": "western",
    }
    visited = set()
    for t in turns:
        content = (t.get("content") or "").lower()
        for keyword, sch in schools_map.items():
            if keyword in content:
                visited.add(sch)

    short_keywords = ("ngắn hơn", "tóm lại", "đừng dài", "ngắn gọn")
    long_keywords = ("chi tiết hơn", "kỹ hơn", "đầy đủ hơn")
    tone_signal = None
    user_turns = [t for t in turns if t.get("role") == "user"]
    for ut in user_turns[-3:]:
        content = (ut.get("content") or "").lower()
        if any(k in content for k in short_keywords):
            tone_signal = "shorter"
        elif any(k in content for k in long_keywords):
            tone_signal = "longer"

    return {
        "schools_visited": list(visited),
        "tone_signal": tone_signal,
        "new_traits": [],
    }


def compute_chart_hash(chart_data: dict) -> str:
    """Stable hash for chart_data — used to correlate summaries."""
    try:
        s = json.dumps(chart_data, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        s = str(chart_data)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]
