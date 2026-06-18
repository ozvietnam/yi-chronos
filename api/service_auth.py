"""Y3 (#34) — dual-auth + rate-limit cho endpoint AppChat gọi server-to-server.

Endpoint cast/quiz/compat cho phép HAI đường vào (dual-auth):
  1. Web user đã đăng nhập — session cookie (api.auth.get_current_user).
  2. AppChat server-to-server — header `X-API-Key` == env `YI_SYNC_API_KEY` +
     `X-User-Id` (Firebase UID, đã xác thực phía AppChat → ta TIN, không verify lại
     SĐT/email). Khớp pattern api/sync.py (_require_service_key, compare_digest).
Ẩn danh (không session, không key) → 401. Đóng lỗ "endpoint public" (#34, bài học
privacy audit 2026-05-27 — gate đúng namespace).

Rate-limit theo X-User-Id qua engine.ratelimit (sliding-window, Redis prod / in-mem
dev). Đặc biệt quiz tốn LLM → siết chặt (N session/ngày/user).
"""
from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, Request

import api.auth as _auth  # module-ref → tôn trọng monkeypatch (fixture as_owner)
from engine import ratelimit


def _valid_service_key(x_api_key: Optional[str]) -> bool:
    """True nếu X-API-Key khớp YI_SYNC_API_KEY (timing-safe). False nếu key chưa
    cấu hình hoặc không khớp."""
    expected = os.environ.get("YI_SYNC_API_KEY", "")
    if not expected or not x_api_key:
        return False
    return secrets.compare_digest(x_api_key, expected)


def require_caller(
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
) -> dict:
    """Dual-auth dependency. Trả identity của caller hoặc raise 401/400.

    Returns: {"source": "session"|"service", "user_id": str, "is_owner": bool}
    """
    # 1) Service-to-service (AppChat) — ưu tiên nếu có X-API-Key.
    if x_api_key is not None:
        if not _valid_service_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid X-API-Key")
        if not x_user_id:
            raise HTTPException(
                status_code=400, detail="X-User-Id required with X-API-Key"
            )
        return {"source": "service", "user_id": str(x_user_id), "is_owner": False}
    # 2) Web session (cookie / X-Session-Token).
    user = _auth.get_current_user(request)
    if user:
        return {
            "source": "session",
            "user_id": str(user["user_id"]),
            "is_owner": user.get("role") == "owner",
        }
    # 3) Ẩn danh → chặn.
    raise HTTPException(
        status_code=401,
        detail="Authentication required (web session hoặc X-API-Key + X-User-Id)",
    )


def rate_limit_caller(
    caller: dict, *, bucket: str, limit: int, window_sec: int
) -> None:
    """Rate-limit theo user_id. Raise 429 nếu vượt cửa sổ trượt.

    Owner web được miễn (tránh tự chặn khi founder test/dùng). Service + user web
    thường đều bị tính.
    """
    if caller.get("source") == "session" and caller.get("is_owner"):
        return
    key = f"{bucket}:{caller.get('user_id', 'anon')}"
    if not ratelimit.allow(key, limit=limit, window_sec=window_sec):
        raise HTTPException(
            status_code=429,
            detail=f"Vượt giới hạn {bucket}: tối đa {limit} lần / {window_sec}s. Thử lại sau.",
        )
