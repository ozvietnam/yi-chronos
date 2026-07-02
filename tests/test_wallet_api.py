"""API ví Xu trung tâm — kênh AppChat (service-keyed): balance / grant / claim-daily."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

UID = "_test_xu_uid_"
KEY = "test-xu-key"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}
    c.post("/api/sync/upsert-from-firebase",
           json={"firebase_uid": UID, "display_name": "T", "email": UID + "@t.local",
                 "birth": {"datetime_local": "1990-08-20T09:30:00", "gender": "nữ"}},
           headers=H)
    yield c, H
    from engine.db import session_scope
    with session_scope(service=True) as conn:
        r = conn.execute(text("SELECT user_id FROM users WHERE firebase_uid=:u"),
                         {"u": UID}).fetchone()
        if r:
            for t in ("xu_ledger", "xu_wallet"):
                conn.execute(text(f"DELETE FROM {t} WHERE user_id=:i"), {"i": r[0]})
            conn.execute(text("DELETE FROM user_persons WHERE user_id=:i"), {"i": r[0]})
            conn.execute(text("DELETE FROM users WHERE user_id=:i"), {"i": r[0]})


def test_balance_zero_then_grant(client):
    c, H = client
    r = c.get(f"/api/sync/wallet/{UID}", headers=H).json()
    assert r["found"] is True and r["balance"] == 0
    assert r["xu_cost"] == {"quick": 1, "council": 5, "deep": 99}
    assert r["free_quick_per_day"] == 10

    g = c.post("/api/sync/wallet/grant",
               json={"firebase_uid": UID, "amount": 100, "reason": "topup", "ref": "rc_1"},
               headers=H).json()
    assert g["status"] == "ok" and g["balance"] == 100
    assert c.get(f"/api/sync/wallet/{UID}", headers=H).json()["balance"] == 100


def test_grant_requires_service_key(client):
    c, _ = client
    resp = c.post("/api/sync/wallet/grant", json={"firebase_uid": UID, "amount": 5})
    assert resp.status_code == 401


def test_grant_unknown_uid_404(client):
    c, H = client
    resp = c.post("/api/sync/wallet/grant",
                  json={"firebase_uid": "nope_uid", "amount": 5}, headers=H)
    assert resp.status_code == 404


def test_grant_rejects_nonpositive(client):
    c, H = client
    resp = c.post("/api/sync/wallet/grant",
                  json={"firebase_uid": UID, "amount": 0}, headers=H)
    assert resp.status_code == 400


def test_claim_daily_grants_within_window(client):
    c, H = client
    r = c.post("/api/sync/wallet/claim-daily", json={"firebase_uid": UID}, headers=H).json()
    assert r["claimed"] is True and r["xu"] == 10
    r2 = c.post("/api/sync/wallet/claim-daily", json={"firebase_uid": UID}, headers=H).json()
    assert r2["claimed"] is False and r2["reason"] == "already_claimed"


def test_balance_unknown_uid(client):
    c, H = client
    assert c.get("/api/sync/wallet/nope_uid", headers=H).json() == {"found": False}
