"""Relationship graph — cross-references between Persons.

Each edge has:
- rel_type: family / professional / social / romantic / spiritual subcategory
- closeness: 0-1 (strength of bond)
- since: when relationship started (year or date)
- context: where/how (Công ty X, Đại học Y)
- quality: positive | neutral | negative | complex
- frequency: daily | weekly | monthly | rarely | dormant
- trust: high | medium | low
- bidirectional: if True, also create reverse edge

Plus auto-computed cosmology compatibility (from charts, see engine.ai.dyad_analysis).

Storage: same `persons.sqlite3` — `relationships` table.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .persons import _DB_PATH


# Standard rel types (extensible — not enforced)
REL_TYPES: tuple[str, ...] = (
    # Family
    "spouse", "ex_spouse", "parent", "child", "sibling", "grandparent", "grandchild",
    "in_law", "extended_family",
    # Professional
    "boss", "subordinate", "colleague", "client", "vendor", "investor", "advisor",
    "mentor", "mentee", "competitor", "partner", "cofounder",
    # Social
    "friend", "best_friend", "acquaintance", "neighbor", "classmate",
    # Romantic
    "lover", "crush", "ex_lover",
    # Spiritual
    "teacher", "student", "guru",
    # Default
    "other",
)


@dataclass
class Relationship:
    """One directed edge in the person graph."""

    rel_id: int | None
    from_person_id: str
    to_person_id: str
    rel_type: str
    closeness: float = 0.5          # 0..1
    since: str | None = None         # year or ISO date
    context: str | None = None       # "Công ty X", "Đại học Y"
    quality: str = "neutral"         # positive | neutral | negative | complex
    frequency: str = "monthly"       # daily | weekly | monthly | rarely | dormant
    trust: str = "medium"            # high | medium | low
    notes: str | None = None
    bidirectional: bool = True
    # Auto-computed compat snapshot (refreshed on demand)
    cosmology_compat: dict | None = None
    created_at: int = 0
    updated_at: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


# ─── DB ──────────────────────────────────────────────────────────────────────


def _ensure_rel_db() -> None:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_DB_PATH) as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                rel_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                from_person_id  TEXT NOT NULL,
                to_person_id    TEXT NOT NULL,
                rel_type        TEXT NOT NULL,
                closeness       REAL NOT NULL DEFAULT 0.5,
                since           TEXT,
                context         TEXT,
                quality         TEXT NOT NULL DEFAULT 'neutral',
                frequency       TEXT NOT NULL DEFAULT 'monthly',
                trust           TEXT NOT NULL DEFAULT 'medium',
                notes           TEXT,
                bidirectional   INTEGER NOT NULL DEFAULT 1,
                cosmology_compat_json TEXT,
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER NOT NULL,
                FOREIGN KEY (from_person_id) REFERENCES persons(person_id),
                FOREIGN KEY (to_person_id)   REFERENCES persons(person_id),
                UNIQUE (from_person_id, to_person_id, rel_type)
            );
            CREATE INDEX IF NOT EXISTS idx_rel_from ON relationships(from_person_id);
            CREATE INDEX IF NOT EXISTS idx_rel_to   ON relationships(to_person_id);
            CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(rel_type);
            """
        )


def _row_to_rel(row: sqlite3.Row) -> Relationship:
    cc = row["cosmology_compat_json"]
    return Relationship(
        rel_id=row["rel_id"],
        from_person_id=row["from_person_id"],
        to_person_id=row["to_person_id"],
        rel_type=row["rel_type"],
        closeness=row["closeness"],
        since=row["since"],
        context=row["context"],
        quality=row["quality"],
        frequency=row["frequency"],
        trust=row["trust"],
        notes=row["notes"],
        bidirectional=bool(row["bidirectional"]),
        cosmology_compat=json.loads(cc) if cc else None,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ─── Public API ──────────────────────────────────────────────────────────────


def add_relationship(
    *,
    from_person_id: str,
    to_person_id: str,
    rel_type: str,
    closeness: float = 0.5,
    since: str | None = None,
    context: str | None = None,
    quality: str = "neutral",
    frequency: str = "monthly",
    trust: str = "medium",
    notes: str | None = None,
    bidirectional: bool = True,
) -> Relationship:
    """Add (or replace) a directed edge. If bidirectional, also adds reverse."""
    _ensure_rel_db()
    now = int(time.time())

    def _upsert(a: str, b: str) -> Relationship:
        with sqlite3.connect(_DB_PATH) as c:
            c.row_factory = sqlite3.Row
            # Upsert via DELETE + INSERT (avoids partial-update edge cases)
            c.execute(
                "DELETE FROM relationships WHERE from_person_id=? AND to_person_id=? AND rel_type=?",
                (a, b, rel_type),
            )
            cur = c.execute(
                """INSERT INTO relationships (
                    from_person_id, to_person_id, rel_type, closeness, since,
                    context, quality, frequency, trust, notes,
                    bidirectional, cosmology_compat_json,
                    created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    a, b, rel_type, closeness, since,
                    context, quality, frequency, trust, notes,
                    int(bidirectional), None,
                    now, now,
                ),
            )
            new_id = cur.lastrowid
            row = c.execute(
                "SELECT * FROM relationships WHERE rel_id = ?", (new_id,)
            ).fetchone()
            return _row_to_rel(row)

    primary = _upsert(from_person_id, to_person_id)
    if bidirectional and from_person_id != to_person_id:
        # Mirror — same closeness/quality/etc, reverse direction
        _upsert(to_person_id, from_person_id)
    return primary


def list_relationships(
    *,
    person_id: str | None = None,
    rel_type: str | None = None,
    direction: str = "from",          # 'from' | 'to' | 'either'
    limit: int = 100,
) -> list[Relationship]:
    _ensure_rel_db()
    sql = "SELECT * FROM relationships WHERE 1=1"
    args: list = []
    if person_id:
        if direction == "from":
            sql += " AND from_person_id = ?"
            args.append(person_id)
        elif direction == "to":
            sql += " AND to_person_id = ?"
            args.append(person_id)
        else:
            sql += " AND (from_person_id = ? OR to_person_id = ?)"
            args.extend([person_id, person_id])
    if rel_type:
        sql += " AND rel_type = ?"
        args.append(rel_type)
    sql += " ORDER BY updated_at DESC LIMIT ?"
    args.append(limit)
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, args).fetchall()
    return [_row_to_rel(r) for r in rows]


def get_relationship(from_id: str, to_id: str, rel_type: str | None = None) -> Relationship | None:
    _ensure_rel_db()
    sql = "SELECT * FROM relationships WHERE from_person_id=? AND to_person_id=?"
    args = [from_id, to_id]
    if rel_type:
        sql += " AND rel_type=?"
        args.append(rel_type)
    sql += " ORDER BY updated_at DESC LIMIT 1"
    with sqlite3.connect(_DB_PATH) as c:
        c.row_factory = sqlite3.Row
        row = c.execute(sql, args).fetchone()
    return _row_to_rel(row) if row else None


def update_compat(rel_id: int, compat: dict) -> bool:
    """Store auto-computed cosmology compatibility snapshot."""
    _ensure_rel_db()
    with sqlite3.connect(_DB_PATH) as c:
        cur = c.execute(
            "UPDATE relationships SET cosmology_compat_json=?, updated_at=? WHERE rel_id=?",
            (json.dumps(compat, ensure_ascii=False), int(time.time()), rel_id),
        )
        return cur.rowcount > 0


def delete_relationship(rel_id: int) -> bool:
    _ensure_rel_db()
    with sqlite3.connect(_DB_PATH) as c:
        cur = c.execute("DELETE FROM relationships WHERE rel_id=?", (rel_id,))
        return cur.rowcount > 0


# ─── Network query — anh's social graph ──────────────────────────────────────


def founder_network(founder_id: str = "_founder", *, depth: int = 1) -> dict:
    """Return a graph snapshot centered on the founder.

    Depth 1: direct edges only (founder ↔ X for all X).
    Depth 2 (future): also include X ↔ Y where X is in founder's first ring.
    """
    from .persons import get_person  # local to avoid cycle

    founder = get_person(founder_id)
    if not founder:
        return {"founder": None, "edges": [], "persons": []}

    edges = list_relationships(person_id=founder_id, direction="from", limit=500)
    person_ids = {e.to_person_id for e in edges}
    persons = [get_person(pid) for pid in person_ids]

    return {
        "founder": founder.to_dict(),
        "edges": [e.to_dict() for e in edges],
        "persons": [p.to_dict() for p in persons if p],
    }
