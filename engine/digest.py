"""H7 (#40) — digest tuần (proactive cho gói trả phí). Tổng hợp hoạt động 7 ngày của
user từ user_castings (KHÔNG cần LLM → rẻ) → lưu lại (pull) + đẩy notifyUser (push, khi
prvchat#36 sẵn sàng). Chạy bởi Celery Beat (thứ Hai 06:00). Chỉ user có gói
(subscription enabled). Idempotent theo tuần. Dual-driver (engine.db)."""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from typing import Callable, Optional

from sqlalchemy import text

from engine.db import is_postgres, session_scope

logger = logging.getLogger(__name__)
WEB_BASE = os.environ.get("YI_WEB_BASE", "https://kinhdich.online")
NotifyFn = Callable[[str, dict], bool]  # (firebase_uid, payload) -> đã đẩy?


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


def _firebase_uid(conn, user_id: int) -> Optional[str]:
    row = conn.execute(text("SELECT firebase_uid FROM users WHERE user_id=:i"),
                       {"i": user_id}).fetchone()
    return row[0] if row and row[0] else None


def _already_sent_this_week(conn, user_id: int, now: int) -> bool:
    """Idempotent: đã có digest trong 6 ngày gần đây? (Beat tuần/Mon + chống retry/manual)."""
    row = conn.execute(
        text("""SELECT 1 FROM user_castings WHERE user_id=:u AND method='weekly_digest'
                AND created_at >= :since LIMIT 1"""),
        {"u": user_id, "since": now - 6 * 86400},
    ).fetchone()
    return row is not None


def _teaser(digest: dict) -> dict:
    """Rút digest đầy → payload teaser (1-3 ý + deeplink), KHÔNG luận đầy."""
    n, by = digest["n"], digest.get("by_method", {})
    methods = ", ".join(f"{k}×{v}" for k, v in by.items()) or "nhiều môn"
    items = [f"Tuần qua bạn có {n} lượt chiêm nghiệm ({methods})."]
    if digest.get("highlights"):
        q = (digest["highlights"][0].get("question") or "").strip()
        if q:
            items.append(f"Gần nhất: “{q[:80]}”.")
    items.append("Mở YI xem bản đầy đủ — mỗi tuần một khám phá.")
    return {"kind": "weekly_digest", "items": items[:3],
            "deeplink": f"{WEB_BASE}/?from=digest"}


def _real_notify(firebase_uid: str, payload: dict) -> bool:
    """Đẩy qua AppChat notifyUser (HTTP). Chờ prvchat#36 cấp URL → set
    YI_APPCHAT_NOTIFY_URL + YI_NOTIFY_API_KEY. Chưa có URL → skip (chưa delivered)."""
    url = os.environ.get("YI_APPCHAT_NOTIFY_URL", "")
    if not url:
        logger.info("digest: YI_APPCHAT_NOTIFY_URL chưa set → store-only (chờ prvchat#36)")
        return False
    body = json.dumps({"uid": firebase_uid, "type": "yi", "payload": payload}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-API-Key": os.environ.get("YI_NOTIFY_API_KEY", ""),
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return 200 <= r.status < 300
    except Exception as e:
        logger.warning("digest notify fail uid=%s: %s", firebase_uid, e)
        return False


def run_weekly_digest_all(now: Optional[int] = None,
                          notify_fn: Optional[NotifyFn] = None) -> dict:
    """Beat job: mỗi user CÓ GÓI enabled + có hoạt động tuần qua + CHƯA gửi tuần này →
    dựng digest → lưu (pull, AppChat đọc được) + đẩy notifyUser (push). Idempotent.
    notify_fn inject để test; mặc định _real_notify (no-op tới khi prvchat#36 cấp URL)."""
    now = now or int(time.time())
    notify_fn = notify_fn or _real_notify
    with session_scope(service=True) as conn:
        uids = [r[0] for r in conn.execute(
            text("SELECT DISTINCT user_id FROM user_subscriptions WHERE enabled=1")
        ).fetchall()]
    sent = 0
    skipped_already = 0
    for uid in uids:
        with session_scope(service=True) as conn:
            if _already_sent_this_week(conn, uid, now):
                skipped_already += 1
                continue
        d = build_weekly_digest(uid, now=now)
        if d["n"] <= 0:
            continue                       # không hoạt động → không làm phiền
        with session_scope(service=True) as conn:
            _store_digest(conn, uid, d, now)          # pull (AppChat đọc qua history)
            fb = _firebase_uid(conn, uid)
        if fb:
            try:
                notify_fn(fb, _teaser(d))             # push (best-effort, không chặn)
            except Exception as e:
                logger.warning("digest push fail uid=%s: %s", uid, e)
        sent += 1
    return {"vip": len(uids), "sent": sent, "skipped_already": skipped_already}
