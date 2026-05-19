"""Auto-extract `improve_system` items from sage outputs → SQLite store.

When a sage kanban task completes with output formatted as:

    ## IMPROVE
    ### improve_system
    - target: engine.bat_tu.than_sat
      suggestion: thêm Khôi Cương, Văn Xương vào output
      priority: medium
      rationale: hiện chỉ có 6/15 sao phụ

…this module parses the bullet items and stores them in
`data/hermes_yi/engine_critiques.sqlite3` so the founder can review the
engine self-improvement queue (`/api/ai/council/critiques`).

The parser is intentionally loose — sage may format slightly off and we
still try to extract `target`, `suggestion`, `priority`, `rationale`.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CRITIQUE_DB = PROJECT_ROOT / "data" / "hermes_yi" / "engine_critiques.sqlite3"


_VALID_PRIORITIES = {"low", "medium", "high"}


# ─── Schema ──────────────────────────────────────────────────────────────────


def _ensure_db() -> None:
    CRITIQUE_DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CRITIQUE_DB) as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS critiques (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                root_id     TEXT,
                sage_tag    TEXT NOT NULL,
                task_id     TEXT NOT NULL,
                target      TEXT NOT NULL,
                suggestion  TEXT NOT NULL,
                priority    TEXT,
                rationale   TEXT,
                status      TEXT NOT NULL DEFAULT 'open',
                created_at  INTEGER NOT NULL,
                resolved_at INTEGER,
                resolution  TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_crit_status   ON critiques(status);
            CREATE INDEX IF NOT EXISTS idx_crit_target   ON critiques(target);
            CREATE INDEX IF NOT EXISTS idx_crit_root     ON critiques(root_id);
            CREATE INDEX IF NOT EXISTS idx_crit_priority ON critiques(priority);

            CREATE TABLE IF NOT EXISTS harvested_tasks (
                task_id      TEXT PRIMARY KEY,
                harvested_at INTEGER NOT NULL,
                n_critiques  INTEGER NOT NULL DEFAULT 0
            );
            """
        )


def _already_harvested(task_id: str) -> bool:
    _ensure_db()
    with sqlite3.connect(CRITIQUE_DB) as c:
        row = c.execute(
            "SELECT 1 FROM harvested_tasks WHERE task_id = ?", (task_id,)
        ).fetchone()
    return row is not None


def _mark_harvested(task_id: str, n: int) -> None:
    with sqlite3.connect(CRITIQUE_DB) as c:
        c.execute(
            "INSERT OR REPLACE INTO harvested_tasks (task_id, harvested_at, n_critiques) "
            "VALUES (?, ?, ?)",
            (task_id, int(time.time()), n),
        )


# ─── Parser ──────────────────────────────────────────────────────────────────


@dataclass
class ParsedCritique:
    target: str
    suggestion: str
    priority: str | None
    rationale: str | None

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "suggestion": self.suggestion,
            "priority": self.priority,
            "rationale": self.rationale,
        }


# Find the improve_system section in sage output
_IMPROVE_SYSTEM_HEADER = re.compile(
    r"###\s*improve_system\s*\n",
    re.IGNORECASE,
)
# Next section that ends the improve_system block
_NEXT_HEADER = re.compile(r"^\s*(?:#|##|###)\s+", re.MULTILINE)


def _extract_improve_system_block(text: str) -> str:
    """Return the raw text under '### improve_system' header, or empty."""
    if not text:
        return ""
    m = _IMPROVE_SYSTEM_HEADER.search(text)
    if not m:
        return ""
    start = m.end()
    # Find next markdown header (#, ##, ###) after start
    rest = text[start:]
    nxt = _NEXT_HEADER.search(rest)
    if nxt:
        return rest[: nxt.start()]
    return rest


# A single critique item — formatted as either YAML-ish bullets or inline.
# We support two flavours:
#   1. multi-line:
#      - target: engine.bat_tu.than_sat
#        suggestion: ...
#        priority: high
#        rationale: ...
#   2. single-line:
#      - target=engine.x, suggestion=..., priority=...
_BULLET_START = re.compile(r"^\s*-\s+", re.MULTILINE)
# Allow optional markdown emphasis (** or *) and backticks around field names + values.
# Underscores are NOT stripped because identifiers like engine.bat_tu.than_sat use them.
_FIELD = re.compile(
    r"(?:[*`]+)?\s*(?P<key>target|suggestion|priority|rationale)\s*(?:[*`]+)?\s*[:=]\s*(?:[*`]+)?\s*(?P<val>.+?)(?=\n\s*(?:[-*]\s*)?(?:[*`]+)?(?:target|suggestion|priority|rationale)(?:[*`]+)?\s*[:=]|\n\s*-\s|\Z)",
    re.DOTALL | re.IGNORECASE,
)
# Strip ** *and `` `` only — underscores must be preserved for engine path identifiers
_STRIP_MD = re.compile(r"[*`]+")


def _clean_value(raw: str) -> str:
    """Strip markdown emphasis (** and backticks) + trailing punctuation from a value.

    Underscores are preserved (engine paths use them).
    """
    val = raw.strip()
    val = _STRIP_MD.sub("", val)
    val = val.strip().strip(",").rstrip(".").strip()
    return val


def _parse_one_bullet(bullet_text: str) -> ParsedCritique | None:
    """Parse one bullet body into a ParsedCritique, or None if no target found."""
    fields: dict[str, str] = {}
    for m in _FIELD.finditer(bullet_text):
        key = m.group("key").lower().strip()
        val = _clean_value(m.group("val"))
        if val and key not in fields:
            fields[key] = val

    target = fields.get("target")
    suggestion = fields.get("suggestion")
    if not target or not suggestion:
        return None

    priority = fields.get("priority")
    if priority and priority.lower() not in _VALID_PRIORITIES:
        priority = None
    elif priority:
        priority = priority.lower()

    return ParsedCritique(
        target=target,
        suggestion=suggestion,
        priority=priority,
        rationale=fields.get("rationale"),
    )


def parse_critiques(sage_output: str) -> list[ParsedCritique]:
    """Extract all improve_system items from a sage output markdown string.

    Handles two formats:
    1. Nested (one bullet per critique):
         - target: ...
           suggestion: ...
    2. Flat (one bullet per field, group bounded by 'target:'):
         - target: ...
         - suggestion: ...
         - priority: ...
         - rationale: ...
    """
    block = _extract_improve_system_block(sage_output)
    if not block.strip():
        return []

    # Heuristic: count how many bullets begin with "target:" — that's the
    # critique count regardless of nested/flat. We collect each group
    # spanning from "- target:" to the next "- target:" (or end).
    # Tolerates markdown emphasis: `- **target:** ...`, `* target: ...`, `- \`target\`: ...`
    _line_strip_md = re.compile(r"[*_`]+")

    def _is_target_bullet(s: str) -> bool:
        # Strip leading "- " or "* "
        if s.startswith("- "):
            s = s[2:]
        elif s.startswith("* "):
            s = s[2:]
        elif s.startswith("-") and len(s) > 1:
            s = s[1:]
        # Strip markdown emphasis chars from the front
        s = _line_strip_md.sub("", s).strip()
        return s.lower().startswith("target:") or s.lower().startswith("target ")

    lines = block.splitlines()
    groups: list[str] = []
    current: list[str] = []
    in_group = False
    for line in lines:
        stripped = line.strip()
        if _is_target_bullet(stripped):
            if current:
                groups.append("\n".join(current))
            # Drop leading "- " or "* " (or just "-")
            payload = stripped
            for prefix in ("- ", "* "):
                if payload.startswith(prefix):
                    payload = payload[len(prefix):].strip()
                    break
            else:
                if payload.startswith("-") and len(payload) > 1:
                    payload = payload[1:].strip()
            current = [payload]
            in_group = True
        elif in_group:
            # Strip optional leading "- " or "* " for flat-format sibling fields
            for prefix in ("- ", "* "):
                if stripped.startswith(prefix):
                    stripped = stripped[len(prefix):].strip()
                    break
            else:
                if stripped.startswith("-") and len(stripped) > 1:
                    stripped = stripped[1:].strip()
            current.append(stripped)
    if current:
        groups.append("\n".join(current))

    out: list[ParsedCritique] = []
    for g in groups:
        parsed = _parse_one_bullet(g)
        if parsed:
            out.append(parsed)
    return out


# ─── Storage ─────────────────────────────────────────────────────────────────


def store_critiques(
    *,
    root_id: str | None,
    sage_tag: str,
    task_id: str,
    critiques: list[ParsedCritique],
) -> list[int]:
    """Insert critiques into DB. Returns list of new row ids."""
    if not critiques:
        return []
    _ensure_db()
    now = int(time.time())
    ids: list[int] = []
    with sqlite3.connect(CRITIQUE_DB) as c:
        for cr in critiques:
            cur = c.execute(
                "INSERT INTO critiques "
                "(root_id, sage_tag, task_id, target, suggestion, priority, "
                "rationale, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)",
                (
                    root_id,
                    sage_tag,
                    task_id,
                    cr.target,
                    cr.suggestion,
                    cr.priority,
                    cr.rationale,
                    now,
                ),
            )
            ids.append(cur.lastrowid)
    return ids


def harvest_from_sage_task(
    *,
    root_id: str | None,
    sage_tag: str,
    task_id: str,
    sage_output: str,
) -> list[int]:
    """One-shot: parse + store from a completed sage task. Idempotent —
    if `task_id` already harvested, returns []."""
    if _already_harvested(task_id):
        return []
    parsed = parse_critiques(sage_output)
    ids = store_critiques(
        root_id=root_id, sage_tag=sage_tag, task_id=task_id, critiques=parsed
    )
    _mark_harvested(task_id, len(ids))
    return ids


# ─── Queries ─────────────────────────────────────────────────────────────────


def list_critiques(
    *,
    status: str | None = "open",
    priority: str | None = None,
    target_prefix: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """List critiques with optional filters."""
    _ensure_db()
    sql = "SELECT * FROM critiques WHERE 1=1"
    args: list = []
    if status:
        sql += " AND status = ?"
        args.append(status)
    if priority:
        sql += " AND priority = ?"
        args.append(priority)
    if target_prefix:
        sql += " AND target LIKE ?"
        args.append(target_prefix + "%")
    sql += " ORDER BY "
    sql += "CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 "
    sql += "WHEN 'low' THEN 2 ELSE 3 END, created_at DESC LIMIT ?"
    args.append(limit)
    with sqlite3.connect(CRITIQUE_DB) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


def resolve_critique(critique_id: int, *, resolution: str) -> bool:
    """Mark a critique as resolved with anh's note."""
    _ensure_db()
    with sqlite3.connect(CRITIQUE_DB) as c:
        cur = c.execute(
            "UPDATE critiques SET status='resolved', resolved_at=?, resolution=? "
            "WHERE id = ?",
            (int(time.time()), resolution, critique_id),
        )
        return cur.rowcount > 0


def dismiss_critique(critique_id: int, *, reason: str = "") -> bool:
    """Dismiss a critique (won't fix / not actionable)."""
    _ensure_db()
    with sqlite3.connect(CRITIQUE_DB) as c:
        cur = c.execute(
            "UPDATE critiques SET status='dismissed', resolved_at=?, resolution=? "
            "WHERE id = ?",
            (int(time.time()), reason, critique_id),
        )
        return cur.rowcount > 0


def stats() -> dict:
    """Dashboard summary."""
    _ensure_db()
    with sqlite3.connect(CRITIQUE_DB) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            "SELECT status, priority, COUNT(*) AS n FROM critiques GROUP BY status, priority"
        ).fetchall()
    summary: dict = {"open": {}, "resolved": {}, "dismissed": {}, "total": 0}
    for r in rows:
        bucket = summary.setdefault(r["status"], {})
        bucket[r["priority"] or "_unspec"] = r["n"]
        summary["total"] += r["n"]
    return summary
