"""Tests cho #36 (Y5) — sync person store: lưu đối tượng so khớp per firebase_uid."""
import pytest
from fastapi.testclient import TestClient

UID = "_test36_uid_"
KEY = "test-sync-key-36"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}
    # setup: user đã sync + person 'self'
    c.post(
        "/api/sync/upsert-from-firebase",
        json={"firebase_uid": UID, "display_name": "T", "email": UID + "@t.local",
              "birth": {"datetime_local": "1990-08-20T09:30:00", "gender": "nữ"}},
        headers=H,
    )
    yield c, H
    # teardown
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        r = conn.execute(text("SELECT user_id FROM users WHERE firebase_uid=:u"),
                         {"u": UID}).fetchone()
        if r:
            conn.execute(text("DELETE FROM user_persons WHERE user_id=:i"), {"i": r[0]})
            conn.execute(text("DELETE FROM users WHERE user_id=:i"), {"i": r[0]})


def test_upsert_person_idempotent(client):
    c, H = client
    body = {"firebase_uid": UID, "person_key": "partner", "name": "P", "gender": "nam",
            "birth_datetime_local": "1988-03-15T07:30:00"}
    assert c.post("/api/sync/persons", json=body, headers=H).json()["created"] is True
    assert c.post("/api/sync/persons", json=body, headers=H).json()["created"] is False


def test_list_persons_includes_self_and_others(client):
    c, H = client
    c.post("/api/sync/persons", json={"firebase_uid": UID, "person_key": "partner",
           "name": "P", "gender": "nam", "birth_datetime_local": "1988-03-15T07:30:00"},
           headers=H)
    r = c.get(f"/api/sync/persons/{UID}", headers=H).json()
    assert r["found"] is True
    assert {p["person_key"] for p in r["persons"]} == {"self", "partner"}


def test_delete_person_and_guard_self(client):
    c, H = client
    c.post("/api/sync/persons",
           json={"firebase_uid": UID, "person_key": "partner", "name": "P"}, headers=H)
    assert c.delete(f"/api/sync/persons/{UID}/partner", headers=H).json()["deleted"] is True
    # 'self' KHÔNG được xóa (hồ sơ gốc)
    assert c.delete(f"/api/sync/persons/{UID}/self", headers=H).status_code == 400


def test_upsert_unsynced_user_404(client):
    c, H = client
    r = c.post("/api/sync/persons",
               json={"firebase_uid": "_nonexistent_uid_", "person_key": "x", "name": "X"},
               headers=H)
    assert r.status_code == 404


def test_persons_require_service_key(client):
    c, _ = client
    assert c.get(f"/api/sync/persons/{UID}").status_code == 401
    assert c.post("/api/sync/persons",
                  json={"firebase_uid": UID, "person_key": "x", "name": "X"}).status_code == 401
