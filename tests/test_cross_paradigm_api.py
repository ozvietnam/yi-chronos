"""#55/#56 — hồi quy PRIVACY + contract API liên-phái.

Khoá: KHÁCH ẩn danh KHÔNG gọi được endpoint luận (401), service-keyed từ chối thiếu/
sai khoá. Đây là class lỗi đã leak 3 lần (audit 2026-05-27) — gỡ gate là test đỏ.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def client():
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=False)


# ── authed-self (web): khách ẩn danh → 401 ───────────────────────────────────

def test_hon_nhan_self_guest_401(client):
    r = client.post("/api/cross-paradigm/hon-nhan", json={"person_key": "self"})
    assert r.status_code == 401, f"khách phải bị chặn, nhận {r.status_code}"


def test_couple_sync_self_guest_401(client):
    r = client.post("/api/couple-sync", json={"person_key": "self"})
    assert r.status_code == 401, f"khách phải bị chặn, nhận {r.status_code}"


# ── service-keyed (AppChat): thiếu/sai khoá KHÔNG bao giờ 200 ─────────────────

def test_hon_nhan_bridge_missing_key_blocked(client):
    r = client.post("/api/sync/hon-nhan-song-phai",
                    json={"firebase_uid": "fb_x", "person_key": "self"})
    assert r.status_code in (401, 503), f"thiếu service key phải bị chặn, nhận {r.status_code}"


def test_couple_sync_bridge_invalid_key_blocked(client, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-correct")
    r = client.post("/api/sync/couple-sync",
                    json={"firebase_uid": "fb_x"},
                    headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401, f"sai service key phải 401, nhận {r.status_code}"


# ── contract: khoá đúng nhưng uid chưa sync → 404 (gate qua, tới logic) ───────

def test_bridge_valid_key_unsynced_uid_404(client, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "secret-correct")
    r = client.post("/api/sync/hon-nhan-song-phai",
                    json={"firebase_uid": "fb_never_synced_zzz", "person_key": "self"},
                    headers={"X-API-Key": "secret-correct"})
    assert r.status_code == 404, f"uid chưa sync phải 404, nhận {r.status_code}"
