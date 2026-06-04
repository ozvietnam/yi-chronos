"""YI-Hermes Memory — cross-session knowledge about user.

3 layers of memory:

1. **User Facts** — discrete facts extracted from chat
   ("Anh chuyển việc 2017", "Vợ anh tên Hoa, sinh 1987")
   Each fact has category, confidence, source session.

2. **Chat Summaries** — short summary of each session, with FTS5 full-text search
   for retrieval: "anh đã hỏi gì về sự nghiệp tháng trước?"

3. **Glossary Views** — log which terms user viewed/asked about
   Drives Soul.focus_schools evolution.

Schema designed to be queryable by LLM for context injection on next session.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "memory.sqlite3"
_lock = Lock()


# Fact categories
CATEGORY_EVENT = "event"          # "Đã cưới 2010", "Mất bố 2020"
CATEGORY_PREFERENCE = "preference" # "Thích ngành công nghệ", "Tránh đầu cơ"
CATEGORY_RELATION = "relation"    # "Vợ tên Hoa, sinh 1987"
CATEGORY_BELIEF = "belief"        # "Tin vào số mệnh", "Hoài nghi chiêm tinh"
CATEGORY_GOAL = "goal"            # "Muốn mua nhà 2027"
CATEGORY_HEALTH = "health"        # nhạy cảm, "Bệnh tim 2023"
CATEGORY_OTHER = "other"

CATEGORIES = (
    CATEGORY_EVENT, CATEGORY_PREFERENCE, CATEGORY_RELATION,
    CATEGORY_BELIEF, CATEGORY_GOAL, CATEGORY_HEALTH, CATEGORY_OTHER,
)


@dataclass(frozen=True)
class UserFact:
    id: int | None
    user_id: str
    fact: str                # "Anh chuyển việc 6/2017"
    category: str            # one of CATEGORIES
    confidence: float        # 0.0..1.0
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
    summary: str             # ~3 sentences
    key_topics: list[str]    # ['sự nghiệp', 'Tử Vi', 'Đại Vận']
    chart_data_hash: str     # hash of chart user was viewing
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS user_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                fact TEXT NOT NULL,
                category TEXT,
                confidence REAL DEFAULT 0.8,
                source_session_id INTEGER,
                notes TEXT,
                extracted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_user ON user_facts(user_id)"
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS chat_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_id INTEGER,
                summary TEXT NOT NULL,
                key_topics TEXT,         -- JSON list
                chart_data_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_summaries_user ON chat_summaries(user_id)"
        )

        # FTS5 virtual table for full-text search on summaries.
        # Skip silently if FTS5 not available (rare on stock Python SQLite).
        try:
            conn.execute(
                """CREATE VIRTUAL TABLE IF NOT EXISTS summaries_fts USING fts5(
                    summary, key_topics,
                    content='chat_summaries', content_rowid='id'
                )"""
            )
            # Trigger to keep FTS in sync.
            conn.execute(
                """CREATE TRIGGER IF NOT EXISTS summaries_ai AFTER INSERT ON chat_summaries
                   BEGIN
                     INSERT INTO summaries_fts(rowid, summary, key_topics)
                     VALUES (new.id, new.summary, new.key_topics);
                   END"""
            )
            conn.execute(
                """CREATE TRIGGER IF NOT EXISTS summaries_ad AFTER DELETE ON chat_summaries
                   BEGIN
                     INSERT INTO summaries_fts(summaries_fts, rowid, summary, key_topics)
                     VALUES('delete', old.id, old.summary, old.key_topics);
                   END"""
            )
            # AFTER UPDATE — keep the external-content FTS5 set complete (#20). Summaries
            # are append-only today, but without this an edit would desync the index
            # (old terms stay searchable, new terms unindexed).
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
                user_id TEXT NOT NULL,
                term_vi TEXT NOT NULL,
                viewed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
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
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO user_facts
               (user_id, fact, category, confidence, source_session_id, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, fact.strip(), category, confidence, source_session_id, notes),
        )
        return cur.lastrowid


def list_facts(
    user_id: str,
    *,
    category: str | None = None,
    limit: int = 50,
    query_hint: str = "",
) -> list[UserFact]:
    """Recent facts first; when `query_hint` is given, blend recency with relevance
    (token overlap) so an older-but-relevant fact isn't dropped by recency alone (#20)."""
    _ensure_db()
    # When ranking by relevance, pull a larger recent pool to re-rank from.
    fetch = max(limit * 4, 40) if query_hint.strip() else limit
    with sqlite3.connect(_DB_PATH) as conn:
        if category:
            rows = conn.execute(
                """SELECT id, user_id, fact, category, confidence,
                          source_session_id, extracted_at, COALESCE(notes, '')
                   FROM user_facts WHERE user_id=? AND category=?
                   ORDER BY extracted_at DESC LIMIT ?""",
                (user_id, category, fetch),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, user_id, fact, category, confidence,
                          source_session_id, extracted_at, COALESCE(notes, '')
                   FROM user_facts WHERE user_id=?
                   ORDER BY extracted_at DESC LIMIT ?""",
                (user_id, fetch),
            ).fetchall()
    facts = [
        UserFact(
            id=r[0], user_id=r[1], fact=r[2], category=r[3],
            confidence=r[4], source_session_id=r[5],
            extracted_at=r[6], notes=r[7],
        )
        for r in rows
    ]
    if query_hint.strip() and facts:
        hint_tokens = {t for t in re.findall(r"\w+", query_hint.lower()) if len(t) > 1}
        if hint_tokens:
            def _relevance(f: UserFact) -> int:
                fact_tokens = set(re.findall(r"\w+", f"{f.fact} {f.category}".lower()))
                return len(hint_tokens & fact_tokens)
            # Stable sort: relevance desc, then recency desc (rows already recency-ordered).
            facts.sort(key=_relevance, reverse=True)
        facts = facts[:limit]
    return facts


def delete_fact(fact_id: int) -> bool:
    _ensure_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute("DELETE FROM user_facts WHERE id=?", (fact_id,))
        return cur.rowcount > 0


def update_fact(fact_id: int, fact: str | None = None, category: str | None = None) -> bool:
    _ensure_db()
    fields, vals = [], []
    if fact:
        fields.append("fact=?")
        vals.append(fact.strip())
    if category in CATEGORIES:
        fields.append("category=?")
        vals.append(category)
    if not fields:
        return False
    vals.append(fact_id)
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute(
            f"UPDATE user_facts SET {', '.join(fields)} WHERE id=?", vals
        )
        return cur.rowcount > 0


def fact_categories_summary(user_id: str) -> dict[str, int]:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        rows = conn.execute(
            "SELECT category, COUNT(*) FROM user_facts WHERE user_id=? GROUP BY category",
            (user_id,),
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
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO chat_summaries
               (user_id, session_id, summary, key_topics, chart_data_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, session_id, summary.strip(), topics_json, chart_data_hash),
        )
        return cur.lastrowid


def list_summaries(user_id: str, limit: int = 20) -> list[ChatSummary]:
    """Recent summaries first."""
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        rows = conn.execute(
            """SELECT id, user_id, session_id, summary, key_topics,
                      COALESCE(chart_data_hash, ''), created_at
               FROM chat_summaries WHERE user_id=?
               ORDER BY id DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    out: list[ChatSummary] = []
    for r in rows:
        try:
            topics = json.loads(r[4])
        except json.JSONDecodeError:
            topics = []
        out.append(ChatSummary(
            id=r[0], user_id=r[1], session_id=r[2], summary=r[3],
            key_topics=topics, chart_data_hash=r[5], created_at=r[6],
        ))
    return out


def search_summaries(user_id: str, query: str, limit: int = 5) -> list[ChatSummary]:
    """FTS5 search; falls back to LIKE if FTS unavailable."""
    _ensure_db()
    out: list[ChatSummary] = []
    with sqlite3.connect(_DB_PATH) as conn:
        # Try FTS5
        try:
            rows = conn.execute(
                """SELECT s.id, s.user_id, s.session_id, s.summary, s.key_topics,
                          COALESCE(s.chart_data_hash, ''), s.created_at
                   FROM summaries_fts f
                   JOIN chat_summaries s ON s.id = f.rowid
                   WHERE summaries_fts MATCH ? AND s.user_id=?
                   ORDER BY rank LIMIT ?""",
                (query, user_id, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            # FTS5 not enabled — fall back to LIKE
            rows = conn.execute(
                """SELECT id, user_id, session_id, summary, key_topics,
                          COALESCE(chart_data_hash, ''), created_at
                   FROM chat_summaries
                   WHERE user_id=? AND (summary LIKE ? OR key_topics LIKE ?)
                   ORDER BY id DESC LIMIT ?""",
                (user_id, f"%{query}%", f"%{query}%", limit),
            ).fetchall()
    for r in rows:
        try:
            topics = json.loads(r[4])
        except json.JSONDecodeError:
            topics = []
        out.append(ChatSummary(
            id=r[0], user_id=r[1], session_id=r[2], summary=r[3],
            key_topics=topics, chart_data_hash=r[5], created_at=r[6],
        ))
    return out


# ─── Glossary Views (tracking) ────────────────────────────────────────────────


def log_glossary_view(user_id: str, term_vi: str) -> None:
    if not user_id or not term_vi:
        return
    _ensure_db()
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO glossary_views (user_id, term_vi) VALUES (?, ?)",
            (user_id, term_vi),
        )


def top_viewed_terms(user_id: str, limit: int = 10) -> list[tuple[str, int]]:
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        rows = conn.execute(
            """SELECT term_vi, COUNT(*) c FROM glossary_views
               WHERE user_id=? GROUP BY term_vi
               ORDER BY c DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    return [(r[0], r[1]) for r in rows]


# ─── Context injection for chat ───────────────────────────────────────────────


def build_memory_context(user_id: str, query_hint: str = "") -> str:
    """Build a memory context block for system prompt injection.

    Includes:
    - Top 5 facts (relevance-ranked on query_hint if provided, else recent)
    - Top 3 relevant past chat summaries (FTS on query_hint if provided)
    - Top viewed glossary terms (signals interest)
    """
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
    """Heuristically extract soul-evolution signals from a finished chat session.

    Returns dict with:
    - schools_visited: schools mentioned
    - tone_signal: "shorter" / "longer" / None
    - new_traits: empty for v1 (need LLM)
    """
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

    # Tone signal: if user keeps asking shorter answers
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
