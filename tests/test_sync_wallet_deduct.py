"""POST /api/sync/wallet/deduct — trừ xu (PRVchat lì xì / hong bao).

Đối xứng /wallet/grant. Hợp đồng team AppChat (docs yi-hongbao-api-guide):
  200 {balance}  ·  402 {error:insufficient_funds, balance}  ·
  404 {error:user_not_found}  ·  400 {error:invalid_request, message}
IDEMPOTENT theo `ref`: Cloud Function retry (timeout) KHÔNG trừ trùng tiền
→ chống double-charge người gửi lì xì.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    """App nối vào users.sqlite3 tạm + service key đã biết (giống test_sync_firebase)."""
    db = tmp_path / "users.sqlite3"
    import api.auth as auth
    import engine.db as _db
    monkeypatch.setattr(auth, "AUTH_DB", db)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    _db.get_engine.cache_clear()
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    from api.main import app
    yield TestClient(app)
    _db.get_engine.cache_clear()


def _mk_user(client, uid: str) -> None:
    r = client.post("/api/sync/upsert-from-firebase",
                    json={"firebase_uid": uid, "display_name": "T"}, headers=HDR)
    assert r.status_code == 200, r.text


def _grant(client, uid: str, amount: int) -> None:
    r = client.post("/api/sync/wallet/grant",
                    json={"firebase_uid": uid, "amount": amount, "reason": "topup"},
                    headers=HDR)
    assert r.status_code == 200, r.text


def _balance(client, uid: str) -> int:
    return client.get(f"/api/sync/wallet/{uid}", headers=HDR).json()["balance"]


def test_route_registered():
    from api import sync as S
    assert "/api/sync/wallet/deduct" in {r.path for r in S.router.routes}


def test_deduct_ok_returns_new_balance(client):
    _mk_user(client, "u_send")
    _grant(client, "u_send", 500)
    r = client.post("/api/sync/wallet/deduct",
                    json={"firebase_uid": "u_send", "amount": 50,
                          "reason": "hong_bao_send", "ref": "hongBao_1"}, headers=HDR)
    assert r.status_code == 200, r.text
    assert r.json() == {"balance": 450}          # đúng hợp đồng: chỉ {balance}
    assert _balance(client, "u_send") == 450


def test_deduct_insufficient_402_no_change(client):
    _mk_user(client, "u_poor")
    _grant(client, "u_poor", 20)
    r = client.post("/api/sync/wallet/deduct",
                    json={"firebase_uid": "u_poor", "amount": 50, "ref": "hb"}, headers=HDR)
    assert r.status_code == 402, r.text
    j = r.json()
    assert j["error"] == "insufficient_funds" and j["balance"] == 20
    assert _balance(client, "u_poor") == 20      # KHÔNG trừ


def test_deduct_unknown_user_404(client):
    r = client.post("/api/sync/wallet/deduct",
                    json={"firebase_uid": "ghost", "amount": 10}, headers=HDR)
    assert r.status_code == 404, r.text
    assert r.json() == {"error": "user_not_found"}


def test_deduct_bad_amount_400(client):
    _mk_user(client, "u_bad")
    _grant(client, "u_bad", 100)
    for amt in (0, -5):
        r = client.post("/api/sync/wallet/deduct",
                        json={"firebase_uid": "u_bad", "amount": amt}, headers=HDR)
        assert r.status_code == 400, (amt, r.text)
        assert r.json()["error"] == "invalid_request"
    assert _balance(client, "u_bad") == 100      # không đụng số dư


def test_deduct_idempotent_same_ref(client):
    """Retry cùng ref (hongBaoId) → trừ 1 lần duy nhất. Chống double-charge."""
    _mk_user(client, "u_idem")
    _grant(client, "u_idem", 100)
    body = {"firebase_uid": "u_idem", "amount": 30,
            "reason": "hong_bao_send", "ref": "hongBao_dup"}
    r1 = client.post("/api/sync/wallet/deduct", json=body, headers=HDR)
    assert r1.status_code == 200 and r1.json()["balance"] == 70
    r2 = client.post("/api/sync/wallet/deduct", json=body, headers=HDR)   # retry
    assert r2.status_code == 200 and r2.json()["balance"] == 70            # KHÔNG trừ lần 2
    assert _balance(client, "u_idem") == 70


def test_deduct_requires_service_key(client):
    _mk_user(client, "u_auth")
    _grant(client, "u_auth", 50)
    assert client.post("/api/sync/wallet/deduct",
                       json={"firebase_uid": "u_auth", "amount": 10}).status_code == 401
    assert client.post("/api/sync/wallet/deduct",
                       json={"firebase_uid": "u_auth", "amount": 10},
                       headers={"X-API-Key": "wrong"}).status_code == 401
    assert _balance(client, "u_auth") == 50      # auth fail → không trừ


def test_grant_deduct_round_trip_hong_bao(client):
    """Luồng lì xì đủ vòng: A gửi 50 (trừ A) → B mở (cộng B) → hết hạn hoàn A."""
    _mk_user(client, "A")
    _mk_user(client, "B")
    _grant(client, "A", 200)
    # A gửi lì xì 50
    assert client.post("/api/sync/wallet/deduct",
                       json={"firebase_uid": "A", "amount": 50,
                             "reason": "hong_bao_send", "ref": "hb_9"},
                       headers=HDR).json()["balance"] == 150
    # B mở → +50 (grant, ref riêng)
    assert client.post("/api/sync/wallet/grant",
                       json={"firebase_uid": "B", "amount": 50,
                             "reason": "hong_bao_open", "ref": "open_hb_9"},
                       headers=HDR).json()["balance"] == 50
    assert _balance(client, "A") == 150 and _balance(client, "B") == 50
