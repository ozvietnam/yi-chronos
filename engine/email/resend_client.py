"""Gửi email transactional (reset mật khẩu...) qua Resend API.

Key persistence theo đúng pattern `data/ai_keys.json` (engine/ai/registry.py):
gitignored, chmod 600, nhập qua tab ⚙️ Cài đặt — KHÔNG qua chat. Resolution
order: env var RESEND_API_KEY trước (prod), rồi tới file (Anh nhập qua UI).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_KEYS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "service_keys.json"
_RESEND_API_URL = "https://api.resend.com/emails"

# Domain gửi mặc định — Anh cần verify domain này trong Resend dashboard trước
# khi email gửi thật sự tới được hộp thư (không verify thì Resend chỉ cho gửi
# tới chính email đăng ký tài khoản Resend, hữu ích để test).
DEFAULT_FROM = os.environ.get("RESEND_FROM_EMAIL", "YI-CHRONOS <noreply@kinhdich.online>")
PUBLIC_BASE_URL = os.environ.get("YI_CHRONOS_PUBLIC_URL", "https://kinhdich.online")


def _load_keys() -> dict:
    try:
        if _KEYS_PATH.exists():
            return json.loads(_KEYS_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def get_api_key() -> Optional[str]:
    env_key = os.environ.get("RESEND_API_KEY")
    if env_key:
        return env_key
    return _load_keys().get("resend")


def set_api_key(key: str) -> None:
    """Persist Resend API key to disk (chmod 600). Empty key wipes it."""
    _KEYS_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_keys()
    if key:
        existing["resend"] = key
    else:
        existing.pop("resend", None)
    _KEYS_PATH.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        _KEYS_PATH.chmod(0o600)
    except Exception:
        pass


def is_configured() -> bool:
    return bool(get_api_key())


def send_email(*, to: str, subject: str, html: str, from_email: Optional[str] = None) -> dict:
    """Gửi 1 email qua Resend. Trả {"ok": bool, "error": str|None}.

    KHÔNG raise — lỗi gửi email (key sai, domain chưa verify, rate limit của
    Resend...) không được làm sập luồng nghiệp vụ gọi nó (forgot-password vẫn
    phải trả response nhất quán cho client dù email lỗi, để không lộ email nào
    tồn tại dựa vào response khác nhau).
    """
    key = get_api_key()
    if not key:
        logger.warning("Resend chưa cấu hình API key — bỏ qua gửi email tới %s", to)
        return {"ok": False, "error": "resend_not_configured"}
    try:
        resp = requests.post(
            _RESEND_API_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"from": from_email or DEFAULT_FROM, "to": [to], "subject": subject, "html": html},
            timeout=10,
        )
        if resp.status_code >= 400:
            logger.warning("Resend gửi email lỗi %s: %s", resp.status_code, resp.text[:300])
            return {"ok": False, "error": f"resend_http_{resp.status_code}"}
        return {"ok": True, "error": None}
    except Exception as e:
        logger.warning("Resend gửi email exception: %s", e)
        return {"ok": False, "error": str(e)}


def send_password_reset_email(*, to_email: str, display_name: str, token: str) -> dict:
    reset_url = f"{PUBLIC_BASE_URL}/?reset_token={token}"
    html = f"""
    <div style="font-family: -apple-system, sans-serif; max-width: 480px; margin: 0 auto; color: #1e293b;">
      <h2 style="color:#0f172a;">🔑 Đặt lại mật khẩu YI-CHRONOS</h2>
      <p>Chào {display_name},</p>
      <p>Có yêu cầu đặt lại mật khẩu cho tài khoản <b>{to_email}</b>. Nếu không phải Anh/Chị yêu cầu, bỏ qua email này — mật khẩu hiện tại vẫn giữ nguyên.</p>
      <p style="margin: 24px 0;">
        <a href="{reset_url}" style="background:#2563eb;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;">Đặt lại mật khẩu</a>
      </p>
      <p style="font-size: 13px; color:#64748b;">Liên kết hết hạn sau 30 phút. Nếu nút trên không bấm được, dán đường dẫn này vào trình duyệt:<br>
      <a href="{reset_url}">{reset_url}</a></p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;">
      <p style="font-size:12px;color:#94a3b8;">YI-CHRONOS · Hệ mô hình hóa trạng thái thời gian</p>
    </div>
    """
    return send_email(to=to_email, subject="Đặt lại mật khẩu YI-CHRONOS", html=html)
