"""Regression: founder-network endpoints phải OWNER-ONLY.

Lỗ hổng 2026-06-13: /api/auth/persons + /api/auth/switch-person chỉ require_user
→ user thường (kể cả mới đăng ký) thấy toàn bộ persons.sqlite3 (network + DOB của anh)
và có thể switch-person sang '_founder' để xem lá số anh. Đã gate owner-only.
"""
import sqlite3
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api import auth

client = TestClient(app)


def _session_for(role: str) -> str | None:
    db = sqlite3.connect(auth.AUTH_DB)
    row = db.execute("SELECT user_id FROM users WHERE role=? LIMIT 1", (role,)).fetchone()
    db.close()
    if not row:
        return None
    return auth._create_session(row[0])


def _del_session(tok: str) -> None:
    db = sqlite3.connect(auth.AUTH_DB)
    db.execute("DELETE FROM sessions WHERE token=?", (tok,))
    db.commit()
    db.close()


def test_auth_persons_owner_only():
    """GET /api/auth/persons: no-auth 401, non-owner 403, owner 200."""
    assert client.get("/api/auth/persons").status_code == 401

    tok_user = _session_for("user")
    if tok_user:
        try:
            assert client.get("/api/auth/persons",
                              headers={"X-Session-Token": tok_user}).status_code == 403
        finally:
            _del_session(tok_user)

    tok_owner = _session_for("owner")
    assert tok_owner, "cần 1 owner trong users.sqlite3"
    try:
        r = client.get("/api/auth/persons", headers={"X-Session-Token": tok_owner})
        assert r.status_code == 200
    finally:
        _del_session(tok_owner)


def test_switch_person_owner_only():
    """POST /api/auth/switch-person: non-owner KHÔNG được impersonate '_founder'."""
    assert client.post("/api/auth/switch-person", json={"person_id": "_founder"}).status_code == 401

    tok_user = _session_for("user")
    if tok_user:
        try:
            r = client.post("/api/auth/switch-person", json={"person_id": "_founder"},
                            headers={"X-Session-Token": tok_user})
            assert r.status_code == 403, "non-owner phải bị chặn switch sang _founder"
        finally:
            _del_session(tok_user)
