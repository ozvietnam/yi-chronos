"""Push best-effort sang AppChat (notifyUser) — ví/xu đổi → app cập nhật số dư TỨC THÌ.

Khi web cộng/trừ xu (đổi mã, admin chỉnh) → bắn 1 notify để AppChat refresh số dư ngay,
không phải chờ user mở lại app. Dùng YI_APPCHAT_NOTIFY_URL + YI_NOTIFY_API_KEY (chung digest).
Chưa set URL (chờ prvchat#36) → no-op. TUYỆT ĐỐI không raise — best-effort, không chặn luồng tiền.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Optional

from sqlalchemy import text

from engine.db import session_scope

logger = logging.getLogger("yi.appchat_notify")


def push(firebase_uid: str, type_: str, payload: dict) -> bool:
    """POST tới AppChat notifyUser. Trả True nếu 2xx. Chưa cấu hình URL → False (no-op)."""
    url = os.environ.get("YI_APPCHAT_NOTIFY_URL", "")
    if not url or not firebase_uid:
        return False
    body = json.dumps({"uid": firebase_uid, "type": type_, "payload": payload}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "X-API-Key": os.environ.get("YI_NOTIFY_API_KEY", ""),
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return 200 <= r.status < 300
    except Exception:
        return False


def _firebase_uid(user_id: int) -> Optional[str]:
    try:
        with session_scope(service=True) as conn:
            r = conn.execute(text("SELECT firebase_uid FROM users WHERE user_id=:u"),
                             {"u": int(user_id)}).fetchone()
        return r[0] if r and r[0] else None
    except Exception:
        return None


def notify_wallet(user_id: int, balance: int, *, delta: int = 0, reason: str = "") -> bool:
    """Báo AppChat ví của user đã đổi (số dư mới) → app refresh tức thì. Best-effort."""
    fb = _firebase_uid(user_id)
    if not fb:
        return False
    return push(fb, "wallet", {"balance": int(balance), "delta": int(delta), "reason": reason})
