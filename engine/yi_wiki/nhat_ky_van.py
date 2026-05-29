"""Nhật ký vận — gắn việc thực vào timestamp + auto-snapshot 7 vòng quẻ.

Theo GOAL: docs/design/MAI-HOA-LUU-VAN-GOAL.md (Phase 2A).

⚠️ Iron Rule #4: KHÔNG predict cát/hung. Đây là **SỔ GHI**, không phải máy đoán.
User ghi việc → snapshot quẻ tại thời điểm. Sau N tháng → pattern mining (Phase 3).

Schema:
  nhat_ky_van (
    id, user_id, happened_at_iso (solar), happened_at_unix,
    title, body, tags_json, importance, sentiment, outcome,
    luu_van_snapshot_json,  -- snapshot 7 vòng tại happened_at
    created_at, updated_at
  )
"""
from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_chronos.sqlite3"


@dataclass
class NhatKyEntry:
    """1 entry nhật ký việc thực + snapshot 7 quẻ."""
    id: int | None = None
    user_id: str = "founder"             # ai sở hữu entry này
    happened_at_iso: str = ""             # "YYYY-MM-DD HH:MM" solar
    happened_at_unix: int = 0
    title: str = ""                       # "Ký deal X", "Privacy incident"
    body: str = ""                        # nội dung dài
    tags: list[str] = field(default_factory=list)  # ["deal", "thuan"]
    importance: int = 3                   # 1 (nhỏ) - 5 (định mệnh)
    sentiment: str = "chua_ro"           # thuan | nghich | binh | chua_ro
    outcome: str = ""                     # ghi sau khi việc đã xong
    luu_van_snapshot: dict | None = None  # 7 vòng tại happened_at
    birth_solar: str | None = None        # birth của user (để re-snapshot nếu cần)
    created_at: int = 0
    updated_at: int = 0


def _ensure_db() -> None:
    """Tạo bảng nếu chưa có."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nhat_ky_van (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         TEXT NOT NULL DEFAULT 'founder',
                happened_at_iso TEXT NOT NULL,
                happened_at_unix INTEGER NOT NULL,
                title           TEXT NOT NULL,
                body            TEXT DEFAULT '',
                tags_json       TEXT DEFAULT '[]',
                importance      INTEGER DEFAULT 3,
                sentiment       TEXT DEFAULT 'chua_ro',
                outcome         TEXT DEFAULT '',
                luu_van_snapshot_json TEXT DEFAULT '{}',
                birth_solar     TEXT,
                created_at      INTEGER NOT NULL,
                updated_at      INTEGER NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nky_user ON nhat_ky_van(user_id, happened_at_unix DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nky_time ON nhat_ky_van(happened_at_unix DESC)")


def _row_to_entry(row: sqlite3.Row) -> NhatKyEntry:
    return NhatKyEntry(
        id=row["id"],
        user_id=row["user_id"],
        happened_at_iso=row["happened_at_iso"],
        happened_at_unix=row["happened_at_unix"],
        title=row["title"],
        body=row["body"] or "",
        tags=json.loads(row["tags_json"] or "[]"),
        importance=row["importance"] or 3,
        sentiment=row["sentiment"] or "chua_ro",
        outcome=row["outcome"] or "",
        luu_van_snapshot=json.loads(row["luu_van_snapshot_json"] or "{}"),
        birth_solar=row["birth_solar"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def create_entry(
    *,
    user_id: str,
    happened_at_iso: str,         # "YYYY-MM-DD HH:MM" solar
    title: str,
    body: str = "",
    tags: list[str] | None = None,
    importance: int = 3,
    sentiment: str = "chua_ro",
    birth_solar: str | None = None,  # cần để compute snapshot
) -> NhatKyEntry:
    """Tạo nhật ký + auto-snapshot 7 vòng quẻ.

    Args:
        happened_at_iso: solar datetime của việc xảy ra
        birth_solar: solar datetime sinh của user (cần để compute Lưu Vận)
    """
    _ensure_db()
    now = int(time.time())
    import datetime as _dt
    try:
        if "T" in happened_at_iso:
            dt = _dt.datetime.fromisoformat(happened_at_iso.replace("T", " "))
        else:
            dt = _dt.datetime.strptime(happened_at_iso[:16], "%Y-%m-%d %H:%M")
        happened_unix = int(dt.timestamp())
    except Exception:
        happened_unix = now

    # Auto-snapshot 7 vòng quẻ
    snapshot = {}
    if birth_solar:
        try:
            from engine.yi_wiki.lich_conversion import parse_solar_string, solar_to_lunar
            from engine.yi_wiki.luu_van import (
                BirthInfo, NowInfo, quan_sat_luu_van,
            )
            bs = parse_solar_string(birth_solar)
            bl = solar_to_lunar(bs)
            birth = BirthInfo(
                year_chi=bl.year_chi, lunar_month=bl.lunar_month,
                lunar_day=bl.lunar_day, hour_chi=bl.hour_chi,
            )
            ns = parse_solar_string(happened_at_iso)
            nl = solar_to_lunar(ns)
            now_info = NowInfo(
                year_chi=nl.year_chi, lunar_month=nl.lunar_month,
                lunar_day=nl.lunar_day, hour_chi=nl.hour_chi,
            )
            snapshot = quan_sat_luu_van(birth, now_info)
        except Exception as e:
            snapshot = {"error": f"Snapshot failed: {e}"}

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            """INSERT INTO nhat_ky_van
               (user_id, happened_at_iso, happened_at_unix, title, body,
                tags_json, importance, sentiment, outcome,
                luu_van_snapshot_json, birth_solar, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, happened_at_iso, happened_unix, title, body,
             json.dumps(tags or [], ensure_ascii=False), importance, sentiment, "",
             json.dumps(snapshot, ensure_ascii=False), birth_solar, now, now),
        )
        entry_id = cur.lastrowid

    return get_entry(entry_id)


def get_entry(entry_id: int) -> NhatKyEntry | None:
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM nhat_ky_van WHERE id = ?", (entry_id,)).fetchone()
        return _row_to_entry(row) if row else None


def list_entries(
    *,
    user_id: str,
    from_unix: int | None = None,
    to_unix: int | None = None,
    limit: int = 100,
) -> list[NhatKyEntry]:
    _ensure_db()
    sql = "SELECT * FROM nhat_ky_van WHERE user_id = ?"
    args = [user_id]
    if from_unix:
        sql += " AND happened_at_unix >= ?"
        args.append(from_unix)
    if to_unix:
        sql += " AND happened_at_unix <= ?"
        args.append(to_unix)
    sql += " ORDER BY happened_at_unix DESC LIMIT ?"
    args.append(limit)
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, args).fetchall()
    return [_row_to_entry(r) for r in rows]


def update_outcome(entry_id: int, *, outcome: str, sentiment: str | None = None) -> NhatKyEntry | None:
    """Update outcome sau khi việc đã xong."""
    _ensure_db()
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as conn:
        if sentiment:
            conn.execute(
                "UPDATE nhat_ky_van SET outcome=?, sentiment=?, updated_at=? WHERE id=?",
                (outcome, sentiment, now, entry_id),
            )
        else:
            conn.execute(
                "UPDATE nhat_ky_van SET outcome=?, updated_at=? WHERE id=?",
                (outcome, now, entry_id),
            )
    return get_entry(entry_id)


def delete_entry(entry_id: int, *, user_id: str) -> bool:
    """Xóa entry — verify user_id để tránh cross-user delete."""
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "DELETE FROM nhat_ky_van WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        )
        return cur.rowcount > 0


def get_stats(user_id: str) -> dict:
    """Stats để hiển thị dashboard."""
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM nhat_ky_van WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        by_sentiment = dict(conn.execute(
            "SELECT sentiment, COUNT(*) FROM nhat_ky_van WHERE user_id = ? GROUP BY sentiment",
            (user_id,),
        ).fetchall())
        by_importance = dict(conn.execute(
            "SELECT importance, COUNT(*) FROM nhat_ky_van WHERE user_id = ? GROUP BY importance",
            (user_id,),
        ).fetchall())
    return {
        "total": total,
        "by_sentiment": by_sentiment,
        "by_importance": by_importance,
    }


def entry_to_dict(e: NhatKyEntry) -> dict:
    """Convert entry → dict cho JSON response."""
    return {
        "id": e.id,
        "user_id": e.user_id,
        "happened_at_iso": e.happened_at_iso,
        "happened_at_unix": e.happened_at_unix,
        "title": e.title,
        "body": e.body,
        "tags": e.tags,
        "importance": e.importance,
        "sentiment": e.sentiment,
        "outcome": e.outcome,
        "luu_van_snapshot": e.luu_van_snapshot,
        "birth_solar": e.birth_solar,
        "created_at": e.created_at,
        "updated_at": e.updated_at,
    }
