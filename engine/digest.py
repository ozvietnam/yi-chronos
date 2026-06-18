"""H7 — digest tuần (proactive cho gói trả phí). Tổng hợp hoạt động 7 ngày của user từ
user_castings (KHÔNG cần LLM → rẻ) → lưu lại để AppChat đẩy FCM. Chạy bởi Celery Beat
(thứ Hai 06:00). Chỉ user có gói (subscription enabled). Dual-driver (engine.db)."""
from __future__ import annotations

import json
import time
from typing import Optional

from sqlalchemy import text

from engine.db import is_postgres, session_scope


def build_weekly_digest(user_id: int, days: int = 7, now: Optional[int] = None) -> dict:
    """Tổng hợp hoạt động `days` ngày của 1 user (đếm theo method + vài highlight).
    KHÔNG gọi LLM — chỉ đọc lịch sử đã lưu."""
    now = now or int(time.time())
    cutoff = now - days * 86400
    with session_scope(service=True) as conn:
        rows = conn.execute(
            text("""SELECT method, question, created_at FROM user_castings
                    WHERE user_id=:u AND created_at>=:c ORDER BY id DESC"""),
            {"u": user_id, "c": cutoff},
        ).fetchall()
    by_method: dict[str, int] = {}
    for m, _q, _t in rows:
        by_method[m] = by_method.get(m, 0) + 1
    return {
        "user_id": user_id, "period_days": days, "n": len(rows),
        "by_method": by_method,
        "highlights": [{"method": r[0], "question": r[1], "at": r[2]} for r in rows[:3]],
        "generated_at": now,
    }


def _store_digest(conn, user_id: int, digest: dict, now: int) -> int:
    res_expr = "CAST(:res AS JSONB)" if is_postgres() else ":res"
    return conn.execute(
        text(f"""INSERT INTO user_castings
                (user_id, method, subject_person_key, question, result_json, verdict,
                 tags, note, algo_version, created_at)
                VALUES (:u,'weekly_digest','self','Digest tuần',{res_expr},NULL,'digest',NULL,
                        'h7-v1',:now) RETURNING id"""),
        {"u": user_id, "res": json.dumps(digest, ensure_ascii=False), "now": now},
    ).scalar()


def run_weekly_digest_all(now: Optional[int] = None) -> dict:
    """Beat job: với mỗi user CÓ GÓI (subscription enabled) + có hoạt động tuần qua →
    dựng digest + lưu (AppChat đọc rồi đẩy FCM). Trả {vip, sent}."""
    now = now or int(time.time())
    with session_scope(service=True) as conn:
        uids = [r[0] for r in conn.execute(
            text("SELECT DISTINCT user_id FROM user_subscriptions WHERE enabled=1")
        ).fetchall()]
    sent = 0
    for uid in uids:
        d = build_weekly_digest(uid, now=now)
        if d["n"] <= 0:
            continue                       # không hoạt động → không làm phiền
        with session_scope(service=True) as conn:
            _store_digest(conn, uid, d, now)
        sent += 1
    return {"vip": len(uids), "sent": sent}
