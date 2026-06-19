"""ADR 3-tầng (task 1) — T2: hồ sơ mệnh-lý DỮ KIỆN TẤT ĐỊNH (an sao/tứ trụ/cách cục).

Pre-compute + cache để đọc TỨC THÌ (KHÔNG LLM, rẻ — engine tất định). RIÊNG user
(RLS theo user_id). Tính lúc sync giờ sinh (hoặc job nền). T3 (luận prose LLM) ghép
T1 (kiến thức chung) × T2 (hồ sơ này) — lazy + cache, KHÔNG pre-gen.

Idempotent. Dual-driver (engine.db).
"""
from __future__ import annotations

import json
import time
from typing import Optional

from sqlalchemy import text

from engine.db import is_postgres, session_scope
from engine.system_meta import get_profile_schema_version

_DDL = """
CREATE TABLE IF NOT EXISTS user_menh_profile (
    user_id        BIGINT PRIMARY KEY,
    schema_version INTEGER,
    facts_json     {json_type},
    computed_at    BIGINT
)
"""


def _ensure(conn) -> None:
    conn.execute(text(_DDL.format(json_type="JSONB" if is_postgres() else "TEXT")))


def _load_self(conn, user_id: int) -> Optional[dict]:
    """Person 'self' của user (dual-driver, RLS user_id)."""
    row = conn.execute(
        text("""SELECT name, gender, birth_datetime_local, timezone, birth_place
                FROM user_persons WHERE user_id=:u AND person_key='self' LIMIT 1"""),
        {"u": user_id},
    ).fetchone()
    if not row:
        return None
    return {"name": row[0], "gender": row[1], "birth_datetime_local": row[2],
            "timezone": row[3] or "Asia/Ho_Chi_Minh", "birth_place": row[4]}


def build_profile(user_id: int) -> dict:
    """Tính T2 facts (cast bat_tu + tu_vi cho self của user) → lưu user_menh_profile.

    Idempotent: gọi lại → tính lại + thay thế. Trả summary (status/has_*). KHÔNG LLM.
    """
    with session_scope(service=True) as conn:
        _ensure(conn)
        person = _load_self(conn, user_id)
    if not person or not person.get("birth_datetime_local"):
        return {"status": "skipped", "reason": "no_birth", "user_id": user_id}

    # Tái dùng builder facts của hermes_service (lazy import — tránh kéo nặng lúc import
    # module; cùng nguồn 1 chỗ cast bat_tu/tu_vi, KHÔNG nhân bản).
    from engine.hermes_service import _build_chart_data
    facts = _build_chart_data(person)        # {birth, gender, timezone, bat_tu, tu_vi}
    sv = get_profile_schema_version()
    now = int(time.time())
    res_expr = "CAST(:f AS JSONB)" if is_postgres() else ":f"
    with session_scope(service=True) as conn:
        _ensure(conn)
        conn.execute(text("DELETE FROM user_menh_profile WHERE user_id=:u"), {"u": user_id})
        conn.execute(
            text(f"""INSERT INTO user_menh_profile (user_id, schema_version, facts_json, computed_at)
                     VALUES (:u,:sv,{res_expr},:t)"""),
            {"u": user_id, "sv": sv, "f": json.dumps(facts, ensure_ascii=False), "t": now},
        )
    return {"status": "ok", "user_id": user_id, "schema_version": sv, "computed_at": now,
            "has_bat_tu": "bat_tu" in facts, "has_tu_vi": "tu_vi" in facts}


def get_profile(user_id: int) -> Optional[dict]:
    """Đọc T2 facts đã cache (TỨC THÌ, không LLM). None nếu chưa build."""
    import json as _j
    with session_scope(service=True) as conn:
        _ensure(conn)
        row = conn.execute(
            text("""SELECT schema_version, facts_json, computed_at
                    FROM user_menh_profile WHERE user_id=:u"""), {"u": user_id},
        ).fetchone()
    if not row:
        return None
    facts = row[1] if isinstance(row[1], (dict, list)) else (_j.loads(row[1]) if row[1] else {})
    return {"user_id": user_id, "schema_version": row[0], "facts": facts,
            "computed_at": row[2]}
