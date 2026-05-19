"""YI-Hermes Glossary — Vietnamese terminology dictionary across 7 modules.

Source: data/yi_hermes/glossary_seed.json (hand-curated, ~50 canonical terms).
Auto-extraction (Phase 1.5) will scan code + Persona prompts for additional terms.

Storage: SQLite for fast indexed search + user edits.
Default content loaded from seed JSON on first call.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from threading import Lock


_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "glossary.sqlite3"
_SEED_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_hermes" / "glossary_seed.json"


@dataclass(frozen=True)
class GlossaryTerm:
    term_vi: str
    term_zh: str
    module: str
    short_def: str
    long_def: str
    example: str = ""
    see_also: list[str] | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["see_also"] is None:
            d["see_also"] = []
        return d


_lock = Lock()


def _ensure_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS terms (
                term_vi TEXT PRIMARY KEY,
                term_zh TEXT,
                module TEXT,
                short_def TEXT NOT NULL,
                long_def TEXT NOT NULL,
                example TEXT,
                see_also TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        # Index for fuzzy substring search.
        conn.execute("CREATE INDEX IF NOT EXISTS idx_terms_module ON terms(module)")


def _seed_if_empty() -> int:
    """Load seed JSON into DB if empty. Returns count of seeded terms."""
    _ensure_db()
    with sqlite3.connect(_DB_PATH) as conn:
        existing = conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]
        if existing > 0:
            return 0

    if not _SEED_PATH.exists():
        return 0

    seed = json.loads(_SEED_PATH.read_text(encoding="utf-8"))
    count = 0
    with _lock, sqlite3.connect(_DB_PATH) as conn:
        for t in seed.get("terms", []):
            try:
                conn.execute(
                    """INSERT INTO terms
                    (term_vi, term_zh, module, short_def, long_def, example, see_also)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        t["term_vi"],
                        t.get("term_zh", ""),
                        t["module"],
                        t["short_def"],
                        t["long_def"],
                        t.get("example", ""),
                        json.dumps(t.get("see_also", []), ensure_ascii=False),
                    ),
                )
                count += 1
            except sqlite3.IntegrityError:
                # Duplicate term_vi — skip.
                continue
    return count


def _row_to_term(row: tuple) -> GlossaryTerm:
    see_also_raw = row[6] or "[]"
    try:
        see_also = json.loads(see_also_raw)
    except json.JSONDecodeError:
        see_also = []
    return GlossaryTerm(
        term_vi=row[0],
        term_zh=row[1] or "",
        module=row[2],
        short_def=row[3],
        long_def=row[4],
        example=row[5] or "",
        see_also=see_also,
    )


class GlossaryStore:
    """Public CRUD + search interface."""

    def __init__(self):
        _ensure_db()
        _seed_if_empty()

    def list_all(self, module: str | None = None) -> list[GlossaryTerm]:
        with sqlite3.connect(_DB_PATH) as conn:
            if module:
                rows = conn.execute(
                    "SELECT term_vi, term_zh, module, short_def, long_def, example, see_also "
                    "FROM terms WHERE module=? ORDER BY term_vi",
                    (module,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT term_vi, term_zh, module, short_def, long_def, example, see_also "
                    "FROM terms ORDER BY module, term_vi"
                ).fetchall()
        return [_row_to_term(r) for r in rows]

    def get(self, term_vi: str) -> GlossaryTerm | None:
        with sqlite3.connect(_DB_PATH) as conn:
            row = conn.execute(
                "SELECT term_vi, term_zh, module, short_def, long_def, example, see_also "
                "FROM terms WHERE term_vi=?",
                (term_vi,),
            ).fetchone()
        return _row_to_term(row) if row else None

    def search(self, query: str, limit: int = 30) -> list[GlossaryTerm]:
        """Fuzzy search by Vietnamese name or short_def (LIKE %query%)."""
        q = f"%{query}%"
        with sqlite3.connect(_DB_PATH) as conn:
            rows = conn.execute(
                """SELECT term_vi, term_zh, module, short_def, long_def, example, see_also
                   FROM terms
                   WHERE term_vi LIKE ? OR short_def LIKE ? OR long_def LIKE ?
                   ORDER BY
                     CASE WHEN term_vi LIKE ? THEN 0 ELSE 1 END,
                     term_vi
                   LIMIT ?""",
                (q, q, q, q, limit),
            ).fetchall()
        return [_row_to_term(r) for r in rows]

    def upsert(self, term: GlossaryTerm) -> None:
        """Insert or update."""
        with _lock, sqlite3.connect(_DB_PATH) as conn:
            conn.execute(
                """INSERT INTO terms
                (term_vi, term_zh, module, short_def, long_def, example, see_also)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(term_vi) DO UPDATE SET
                  term_zh=excluded.term_zh,
                  module=excluded.module,
                  short_def=excluded.short_def,
                  long_def=excluded.long_def,
                  example=excluded.example,
                  see_also=excluded.see_also,
                  updated_at=CURRENT_TIMESTAMP""",
                (
                    term.term_vi, term.term_zh, term.module,
                    term.short_def, term.long_def, term.example,
                    json.dumps(term.see_also or [], ensure_ascii=False),
                ),
            )

    def delete(self, term_vi: str) -> bool:
        with _lock, sqlite3.connect(_DB_PATH) as conn:
            cur = conn.execute("DELETE FROM terms WHERE term_vi=?", (term_vi,))
            return cur.rowcount > 0

    def count(self) -> int:
        with sqlite3.connect(_DB_PATH) as conn:
            return conn.execute("SELECT COUNT(*) FROM terms").fetchone()[0]

    def modules_summary(self) -> dict[str, int]:
        with sqlite3.connect(_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT module, COUNT(*) FROM terms GROUP BY module ORDER BY 2 DESC"
            ).fetchall()
        return {r[0]: r[1] for r in rows}


_store: GlossaryStore | None = None


def get_glossary_store() -> GlossaryStore:
    global _store
    if _store is None:
        _store = GlossaryStore()
    return _store
