"""ADR 3-tầng (task 2) — `system_meta` key/value toàn hệ + versioning.

`knowledge_version` (T1 — KIẾN THỨC CHUNG): bump mỗi khi evolve_gate DUYỆT cập nhật
chạm tri thức chung (sách/lăng kính/sage mới). Đưa vào KHOÁ CACHE T3 (xem
hermes_service._cached) → sách mới ⇒ cache cũ tự vô hiệu ⇒ lần hỏi sau luận lại
bằng kiến thức mới (ADR §3). `profile_schema_version` (T2): version cấu trúc dữ kiện.

Dual-driver (engine.db). Idempotent _ensure.
"""
from __future__ import annotations

import time
from typing import Optional

from sqlalchemy import text

from engine.db import session_scope

_DDL = """
CREATE TABLE IF NOT EXISTS system_meta (
    key        TEXT PRIMARY KEY,
    value      TEXT,
    updated_at BIGINT
)
"""

KEY_KNOWLEDGE_VERSION = "knowledge_version"
KEY_PROFILE_SCHEMA_VERSION = "profile_schema_version"


def _ensure(conn) -> None:
    conn.execute(text(_DDL))


def get_meta(key: str, default: Optional[str] = None) -> Optional[str]:
    with session_scope(service=True) as conn:
        _ensure(conn)
        row = conn.execute(
            text("SELECT value FROM system_meta WHERE key = :k"), {"k": key}
        ).fetchone()
    return row[0] if row and row[0] is not None else default


def set_meta(key: str, value: str) -> None:
    """Upsert (dual-driver: dùng DELETE+INSERT để khỏi lệ thuộc ON CONFLICT/UPSERT)."""
    now = int(time.time())
    with session_scope(service=True) as conn:
        _ensure(conn)
        conn.execute(text("DELETE FROM system_meta WHERE key = :k"), {"k": key})
        conn.execute(
            text("INSERT INTO system_meta (key, value, updated_at) VALUES (:k,:v,:t)"),
            {"k": key, "v": str(value), "t": now},
        )


def _get_int(key: str, default: int) -> int:
    v = get_meta(key)
    if v is None:
        return default
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def get_knowledge_version() -> int:
    """Version tri thức CHUNG (T1). Mặc định 1 (chưa có cập nhật nào duyệt)."""
    return _get_int(KEY_KNOWLEDGE_VERSION, 1)


def bump_knowledge_version() -> int:
    """Tăng knowledge_version (gọi khi evolve_gate DUYỆT cập nhật chạm T1). Trả version mới.
    → cache T3 theo version tự vô hiệu, lần hỏi sau luận bằng kiến thức mới (ADR §3)."""
    new_v = get_knowledge_version() + 1
    set_meta(KEY_KNOWLEDGE_VERSION, str(new_v))
    return new_v


def get_profile_schema_version() -> int:
    """Version cấu trúc dữ kiện T2 (bump khi thêm trường facts mới)."""
    return _get_int(KEY_PROFILE_SCHEMA_VERSION, 1)


def get_meta_updated_at(key: str) -> int:
    """Thời điểm (epoch) key được set lần cuối; 0 nếu chưa có."""
    with session_scope(service=True) as conn:
        _ensure(conn)
        row = conn.execute(
            text("SELECT updated_at FROM system_meta WHERE key = :k"), {"k": key}
        ).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def knowledge_version_updated_at() -> int:
    """Thời điểm bump knowledge_version gần nhất → mốc vô hiệu cache T3 (ADR §3):
    entry cache tạo TRƯỚC mốc này = luận bằng kiến thức CŨ → coi như miss."""
    return get_meta_updated_at(KEY_KNOWLEDGE_VERSION)
