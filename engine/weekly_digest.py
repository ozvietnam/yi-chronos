"""H7 (#40) — digest tuần cho user gói trả phí: "mỗi tuần một khám phá".

Quét cái MỚI kể từ digest trước (thuật toán nâng cấp `algo_version`, suy ngẫm/summary
mới từ Hermes) → teaser 1-3 ý + deeplink → đẩy qua `notify_fn` (inject để test; mặc
định gọi AppChat notifyUser nếu cấu hình). Gate: CHỈ user có sub enabled & chưa hết
hạn. Idempotent theo tuần ISO qua bảng `weekly_digest_sent`.

Trigger: chạy 1 lần/tuần — qua Celery Beat (#41) HOẶC system-cron VPS:
    YI_APPCHAT_NOTIFY_URL=... .venv/bin/python3 -m engine.weekly_digest
Delivery thật chờ prvchat#36 (notifyUser Cloud Function); tới khi có URL thì set env.
"""
from __future__ import annotations

import json as _json
import logging
import os
import time
import urllib.request
from datetime import datetime, timezone
from typing import Callable, Optional

from sqlalchemy import text

from engine import subscriptions as subs  # noqa: F401 (gate dùng list query trực tiếp)
from engine.algo_version import algo_version
from engine.db import session_scope
from engine.yi_hermes import memory

logger = logging.getLogger(__name__)

WEB_BASE = os.environ.get("YI_WEB_BASE", "https://kinhdich.online")

# notify_fn(firebase_uid: str, payload: dict) -> bool (True = đã đẩy)
NotifyFn = Callable[[str, dict], bool]


def _ensure_table(conn) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS weekly_digest_sent ("
        "user_id INTEGER NOT NULL, period TEXT NOT NULL, sent_at BIGINT, "
        "last_algo_version TEXT, last_summary_id BIGINT, "
        "PRIMARY KEY (user_id, period))"
    ))


def iso_period(now: float) -> str:
    """Tuần ISO 'YYYY-Www' (mốc idempotent)."""
    y, w, _ = datetime.fromtimestamp(now, tz=timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def list_subscribed_users(conn, now: float) -> list[int]:
    """user_id có ÍT NHẤT 1 sub enabled & chưa hết hạn."""
    rows = conn.execute(text(
        "SELECT DISTINCT user_id FROM user_subscriptions "
        "WHERE enabled = 1 AND (expires_at IS NULL OR expires_at > :now)"
    ), {"now": int(now)}).fetchall()
    return [r[0] for r in rows]


def _firebase_uid(conn, user_id: int) -> Optional[str]:
    row = conn.execute(text("SELECT firebase_uid FROM users WHERE user_id = :i"),
                       {"i": user_id}).fetchone()
    return row[0] if row and row[0] else None


def build_digest_for_user(conn, user_id: int) -> Optional[dict]:
    """Teaser cái MỚI kể từ digest gần nhất. None nếu không có gì mới (→ không gửi).

    So sánh theo ID (DB-agnostic): summary id tăng đơn điệu; algo_version chuỗi.
    """
    _ensure_table(conn)
    prev = conn.execute(text(
        "SELECT last_algo_version, last_summary_id FROM weekly_digest_sent "
        "WHERE user_id = :i ORDER BY sent_at DESC LIMIT 1"
    ), {"i": user_id}).fetchone()
    last_algo = prev[0] if prev else None
    last_sum_id = (prev[1] if prev and prev[1] is not None else 0)

    items: list[str] = []
    cur_algo = algo_version("tu_vi")
    if last_algo and cur_algo != last_algo:
        items.append(
            f"Thuật toán luận Tử Vi vừa nâng cấp ({last_algo}→{cur_algo}) — "
            f"lá số của bạn có thể hé lộ điều mới."
        )

    summaries = memory.list_summaries(str(user_id), limit=50)
    ids = [int(s.id) for s in summaries if s.id is not None]
    max_sum_id = max(ids) if ids else 0
    new_summaries = sum(1 for i in ids if i > last_sum_id)
    if new_summaries:
        items.append(f"Bạn có {new_summaries} suy ngẫm mới cùng Hermes tuần qua.")

    if not items:
        return None
    return {
        "kind": "weekly_digest",
        "items": items[:3],          # teaser, KHÔNG luận đầy
        "deeplink": f"{WEB_BASE}/?from=digest",
        "_algo_version": cur_algo,    # nội bộ để ghi lại
        "_max_summary_id": max_sum_id,
    }


def _real_notify(firebase_uid: str, payload: dict) -> bool:
    """Đẩy qua AppChat notifyUser (HTTP). Chờ prvchat#36 cấp URL → set
    YI_APPCHAT_NOTIFY_URL + YI_NOTIFY_API_KEY. Chưa có URL → skip (chưa delivered)."""
    url = os.environ.get("YI_APPCHAT_NOTIFY_URL", "")
    if not url:
        logger.info("weekly_digest: YI_APPCHAT_NOTIFY_URL chưa set → skip delivery (chờ prvchat#36)")
        return False
    body = _json.dumps({"uid": firebase_uid, "type": "yi", "payload": payload}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-API-Key": os.environ.get("YI_NOTIFY_API_KEY", ""),
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return 200 <= r.status < 300
    except Exception as e:
        logger.warning("weekly_digest notify fail uid=%s: %s", firebase_uid, e)
        return False


def run_weekly_digest(notify_fn: Optional[NotifyFn] = None,
                      now: Optional[float] = None) -> dict:
    """Quét tất cả user sub-enabled, gửi digest (idempotent theo tuần). Trả thống kê."""
    notify_fn = notify_fn or _real_notify
    now = now if now is not None else time.time()
    period = iso_period(now)
    stats = {"period": period, "subscribed": 0, "sent": 0,
             "skipped_no_change": 0, "skipped_already": 0, "skipped_no_uid": 0,
             "skipped_not_delivered": 0}

    with session_scope(service=True) as conn:
        _ensure_table(conn)
        users = list_subscribed_users(conn, now)
        stats["subscribed"] = len(users)
        for uid in users:
            already = conn.execute(text(
                "SELECT 1 FROM weekly_digest_sent WHERE user_id=:i AND period=:p"
            ), {"i": uid, "p": period}).fetchone()
            if already:
                stats["skipped_already"] += 1
                continue
            fb = _firebase_uid(conn, uid)
            if not fb:
                stats["skipped_no_uid"] += 1
                continue
            digest = build_digest_for_user(conn, uid)
            if not digest:
                stats["skipped_no_change"] += 1
                continue
            payload = {k: v for k, v in digest.items() if not k.startswith("_")}
            if not notify_fn(fb, payload):
                stats["skipped_not_delivered"] += 1
                continue
            conn.execute(text(
                "INSERT INTO weekly_digest_sent "
                "(user_id, period, sent_at, last_algo_version, last_summary_id) "
                "VALUES (:i,:p,:t,:av,:sid)"
            ), {"i": uid, "p": period, "t": int(now),
                "av": digest["_algo_version"], "sid": digest["_max_summary_id"]})
            stats["sent"] += 1
    logger.info("weekly_digest done: %s", stats)
    return stats


if __name__ == "__main__":  # system-cron VPS (hoặc Celery Beat #41)
    logging.basicConfig(level=logging.INFO)
    print(run_weekly_digest())
