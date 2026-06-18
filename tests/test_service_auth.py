"""Tests cho #34 — dual-auth (service-key HOẶC web session) + rate-limit theo user."""
import pytest
from fastapi import HTTPException

from api.service_auth import require_caller, rate_limit_caller, _valid_service_key
from engine import ratelimit


class _FakeReq:
    """Stand-in tối thiểu cho Starlette Request (require_caller chỉ chạm
    get_current_user — đã patch hoặc trả None)."""
    cookies: dict = {}
    headers: dict = {}


# ─── _valid_service_key ────────────────────────────────────────────────────

def test_valid_service_key_match(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-abc")
    assert _valid_service_key("secret-abc") is True
    assert _valid_service_key("wrong") is False
    assert _valid_service_key(None) is False


def test_valid_service_key_unset_env_rejects(monkeypatch):
    """Key chưa cấu hình → từ chối mọi key (không fail-open)."""
    monkeypatch.delenv("YI_SYNC_API_KEY", raising=False)
    assert _valid_service_key("anything") is False


# ─── require_caller (dual-auth) ─────────────────────────────────────────────

def test_anonymous_blocked(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-abc")
    monkeypatch.setattr("api.auth.get_current_user", lambda req: None)
    with pytest.raises(HTTPException) as ei:
        require_caller(_FakeReq(), x_api_key=None, x_user_id=None)
    assert ei.value.status_code == 401


def test_service_key_ok(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-abc")
    caller = require_caller(_FakeReq(), x_api_key="secret-abc", x_user_id="fb-uid-1")
    assert caller == {"source": "service", "user_id": "fb-uid-1", "is_owner": False}


def test_wrong_key_401(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-abc")
    with pytest.raises(HTTPException) as ei:
        require_caller(_FakeReq(), x_api_key="WRONG", x_user_id="u")
    assert ei.value.status_code == 401


def test_key_without_user_id_400(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-abc")
    with pytest.raises(HTTPException) as ei:
        require_caller(_FakeReq(), x_api_key="secret-abc", x_user_id=None)
    assert ei.value.status_code == 400


def test_session_caller(monkeypatch):
    monkeypatch.setattr("api.auth.get_current_user",
                        lambda req: {"user_id": 7, "role": "owner"})
    caller = require_caller(_FakeReq(), x_api_key=None, x_user_id=None)
    assert caller == {"source": "session", "user_id": "7", "is_owner": True}


# ─── rate_limit_caller ──────────────────────────────────────────────────────

def test_rate_limit_blocks_over_limit():
    ratelimit.reset("rltest")
    caller = {"source": "service", "user_id": "u-rl", "is_owner": False}
    for _ in range(3):
        rate_limit_caller(caller, bucket="rltest", limit=3, window_sec=60)
    with pytest.raises(HTTPException) as ei:
        rate_limit_caller(caller, bucket="rltest", limit=3, window_sec=60)
    assert ei.value.status_code == 429
    ratelimit.reset("rltest")


def test_rate_limit_owner_exempt():
    ratelimit.reset("rltest_owner")
    owner = {"source": "session", "user_id": "1", "is_owner": True}
    for _ in range(50):  # owner web miễn → không bao giờ 429
        rate_limit_caller(owner, bucket="rltest_owner", limit=3, window_sec=60)
    ratelimit.reset("rltest_owner")
