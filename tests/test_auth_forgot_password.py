"""Tests for POST /api/auth/forgot-password + /api/auth/reset-password.

Không dùng `as_owner` — 2 endpoint này PUBLIC (người quên mật khẩu chưa đăng
nhập được). Test tự tạo 1 user tạm (email ngẫu nhiên) qua thẳng DB, dọn sạch ở
cuối để không rác data/yi_users/users.sqlite3 thật (không có DB test cô lập
riêng cho auth.py — xem tests/conftest.py).
"""

from __future__ import annotations

import time
import uuid

import pytest
from fastapi.testclient import TestClient

import api.auth as auth
from api.main import app
from engine import ratelimit

client = TestClient(app)


@pytest.fixture
def temp_user():
    """Tạo 1 user tạm trực tiếp qua DB, dọn sạch (user + token + session) sau test."""
    email = f"test-forgot-pw-{uuid.uuid4().hex[:10]}@example.com"
    password = "OldPassw0rd!"
    pw_hash, salt = auth._hash_password(password)
    db = auth._connect()
    try:
        cur = db.execute(
            """INSERT INTO users (email, display_name, password_hash, password_salt,
                                   role, created_at, must_change_password)
               VALUES (?, ?, ?, ?, 'user', ?, 0)""",
            (email, "Test Forgot PW", pw_hash, salt, int(time.time())),
        )
        db.commit()
        user_id = cur.lastrowid
    finally:
        db.close()

    yield {"user_id": user_id, "email": email, "password": password}

    db = auth._connect()
    try:
        db.execute("DELETE FROM password_reset_tokens WHERE user_id=?", (user_id,))
        db.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        db.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        db.commit()
    finally:
        db.close()
    ratelimit.reset(f"forgot_password:{email}")


def _latest_token_for(user_id: int) -> str:
    db = auth._connect()
    try:
        row = db.execute(
            "SELECT token FROM password_reset_tokens WHERE user_id=? ORDER BY created_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        db.close()
    assert row, "expected a reset token row to exist"
    return row[0]


def test_forgot_password_known_email_creates_token(temp_user):
    resp = client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    token = _latest_token_for(temp_user["user_id"])
    assert token


def test_forgot_password_unknown_email_same_generic_response(temp_user):
    """Không lộ email tồn tại hay không — response phải GIỐNG HỆT nhau."""
    r_known = client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    r_unknown = client.post("/api/auth/forgot-password", json={"email": "khong-ton-tai-xyz@example.com"})
    assert r_known.status_code == r_unknown.status_code == 200
    assert r_known.json()["message"] == r_unknown.json()["message"]


def test_forgot_password_unknown_email_creates_no_token():
    email = f"never-registered-{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200
    db = auth._connect()
    try:
        n = db.execute(
            "SELECT COUNT(*) FROM password_reset_tokens t JOIN users u ON u.user_id=t.user_id WHERE u.email=?",
            (email,),
        ).fetchone()[0]
    finally:
        db.close()
    assert n == 0
    ratelimit.reset(f"forgot_password:{email}")


def test_reset_password_with_valid_token_changes_password_and_kills_sessions(temp_user):
    client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    token = _latest_token_for(temp_user["user_id"])

    # Giả lập user đang có 1 session sống (trước khi reset) — phải bị xoá sau reset.
    old_session_token = auth._create_session(temp_user["user_id"])

    new_password = "BrandNewPassw0rd!"
    resp = client.post("/api/auth/reset-password", json={"token": token, "new_password": new_password})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Mật khẩu cũ không đăng nhập được nữa, mật khẩu mới đăng nhập được.
    r_old = client.post("/api/auth/login", json={"email": temp_user["email"], "password": temp_user["password"]})
    assert r_old.status_code == 401
    r_new = client.post("/api/auth/login", json={"email": temp_user["email"], "password": new_password})
    assert r_new.status_code == 200

    # Session cũ (trước khi reset) phải đã bị xoá.
    assert auth._resolve_session(old_session_token) is None


def test_reset_password_token_is_single_use(temp_user):
    client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    token = _latest_token_for(temp_user["user_id"])

    r1 = client.post("/api/auth/reset-password", json={"token": token, "new_password": "FirstNewPass1!"})
    assert r1.status_code == 200

    r2 = client.post("/api/auth/reset-password", json={"token": token, "new_password": "SecondNewPass2!"})
    assert r2.status_code == 400


def test_reset_password_expired_token_rejected(temp_user):
    client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    token = _latest_token_for(temp_user["user_id"])

    # Giả lập token đã hết hạn — lùi expires_at về quá khứ.
    db = auth._connect()
    try:
        db.execute("UPDATE password_reset_tokens SET expires_at=? WHERE token=?", (int(time.time()) - 10, token))
        db.commit()
    finally:
        db.close()

    resp = client.post("/api/auth/reset-password", json={"token": token, "new_password": "ShouldNotWork1!"})
    assert resp.status_code == 400


def test_reset_password_garbage_token_rejected():
    resp = client.post("/api/auth/reset-password", json={"token": "not-a-real-token", "new_password": "Whatever1!"})
    assert resp.status_code == 400


def test_reset_password_too_short_rejected(temp_user):
    client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    token = _latest_token_for(temp_user["user_id"])
    resp = client.post("/api/auth/reset-password", json={"token": token, "new_password": "short"})
    assert resp.status_code == 400


def test_forgot_password_rate_limited_after_3_requests(temp_user):
    ratelimit.reset(f"forgot_password:{temp_user['email']}")
    for _ in range(3):
        r = client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
        assert r.status_code == 200
    # 4th request within the window is throttled internally but still returns
    # the same generic 200 (no leak) — verify via audit_log instead of response.
    r4 = client.post("/api/auth/forgot-password", json={"email": temp_user["email"]})
    assert r4.status_code == 200
    db = auth._connect()
    try:
        n = db.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='forgot_password_rate_limited' AND target_email=?",
            (temp_user["email"],),
        ).fetchone()[0]
    finally:
        db.close()
    assert n >= 1
