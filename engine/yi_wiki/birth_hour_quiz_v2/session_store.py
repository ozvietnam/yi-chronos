"""SQLite-backed quiz session storage."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid


_SCHEMA = """
CREATE TABLE IF NOT EXISTS birth_hour_quiz_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER,
    birth_date TEXT NOT NULL,
    timezone TEXT NOT NULL,
    hour_range_start INTEGER,
    hour_range_end INTEGER,
    gender TEXT,
    candidates_initial TEXT NOT NULL,
    candidates_remaining TEXT NOT NULL,
    strategy TEXT NOT NULL,
    rounds_data TEXT NOT NULL,
    accumulated_scores TEXT NOT NULL,
    final_result TEXT,
    status TEXT NOT NULL DEFAULT 'in_progress',
    created_at INTEGER NOT NULL,
    completed_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user
    ON birth_hour_quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_status
    ON birth_hour_quiz_sessions(status);
"""


def init_schema(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.executescript(_SCHEMA)
        con.commit()
    finally:
        con.close()


def create_session(
    db_path: str,
    *,
    user_id: int | None,
    birth_date: str,
    timezone: str,
    hour_range: tuple[int, int] | None,
    gender: str | None,
    candidates_initial: list[str],
    strategy: str,
) -> str:
    sid = str(uuid.uuid4())
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            INSERT INTO birth_hour_quiz_sessions
              (session_id, user_id, birth_date, timezone,
               hour_range_start, hour_range_end, gender,
               candidates_initial, candidates_remaining, strategy,
               rounds_data, accumulated_scores, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_progress', ?)
            """,
            (
                sid, user_id, birth_date, timezone,
                hour_range[0] if hour_range else None,
                hour_range[1] if hour_range else None,
                gender,
                json.dumps(candidates_initial),
                json.dumps(candidates_initial),
                strategy,
                json.dumps([]),
                json.dumps({c: 0.0 for c in candidates_initial}),
                int(time.time()),
            ),
        )
        con.commit()
    finally:
        con.close()
    return sid


def get_session(db_path: str, session_id: str) -> dict | None:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute(
            "SELECT * FROM birth_hour_quiz_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    finally:
        con.close()

    if not row:
        return None

    out = dict(row)
    out["candidates_initial"] = json.loads(out["candidates_initial"])
    out["candidates_remaining"] = json.loads(out["candidates_remaining"])
    out["rounds_data"] = json.loads(out["rounds_data"])
    out["accumulated_scores"] = json.loads(out["accumulated_scores"])
    if out["final_result"]:
        out["final_result"] = json.loads(out["final_result"])
    if out["hour_range_start"] is not None:
        out["hour_range"] = (out["hour_range_start"], out["hour_range_end"])
    else:
        out["hour_range"] = None
    return out


def update_session(
    db_path: str,
    session_id: str,
    *,
    candidates_remaining: list[str] | None = None,
    accumulated_scores: dict[str, float] | None = None,
    rounds_data: list[dict] | None = None,
) -> None:
    sets, args = [], []
    if candidates_remaining is not None:
        sets.append("candidates_remaining = ?")
        args.append(json.dumps(candidates_remaining))
    if accumulated_scores is not None:
        sets.append("accumulated_scores = ?")
        args.append(json.dumps(accumulated_scores))
    if rounds_data is not None:
        sets.append("rounds_data = ?")
        args.append(json.dumps(rounds_data))
    if not sets:
        return
    args.append(session_id)
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            f"UPDATE birth_hour_quiz_sessions SET {', '.join(sets)} WHERE session_id = ?",
            args,
        )
        con.commit()
    finally:
        con.close()


def mark_final(db_path: str, session_id: str, *, final_result: dict) -> None:
    con = sqlite3.connect(db_path)
    try:
        con.execute(
            """
            UPDATE birth_hour_quiz_sessions
            SET status = 'final', final_result = ?, completed_at = ?
            WHERE session_id = ?
            """,
            (json.dumps(final_result), int(time.time()), session_id),
        )
        con.commit()
    finally:
        con.close()
