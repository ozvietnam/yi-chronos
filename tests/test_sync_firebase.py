"""Tests for Firebase ↔ YI-Chronos identity sync (api/sync.py).

Covers the lazy-provisioning contract used by AppChat's Cloud Functions:
service-key auth, shadow-user creation keyed by firebase_uid, idempotent
re-link, and birth-profile upsert into the user's 'self' person.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    """App wired to an isolated empty users.sqlite3 + a known service key."""
    db = tmp_path / "users.sqlite3"
    import api.auth as auth
    monkeypatch.setattr(auth, "AUTH_DB", db)
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    from api.main import app
    return TestClient(app)


def test_requires_service_key(client):
    r = client.post("/api/sync/upsert-from-firebase", json={"firebase_uid": "uid1"})
    assert r.status_code == 401


def test_wrong_service_key(client):
    r = client.post(
        "/api/sync/upsert-from-firebase",
        json={"firebase_uid": "uid1"},
        headers={"X-API-Key": "nope"},
    )
    assert r.status_code == 401


def test_first_upsert_creates_shadow_user(client):
    r = client.post(
        "/api/sync/upsert-from-firebase",
        json={
            "firebase_uid": "uid_abc",
            "phone": "+84901234567",
            "display_name": "An",
            "birth": {
                "datetime_local": "1990-08-20T09:30:00",
                "gender": "nữ",
                "birth_place": "Hà Nội",
            },
        },
        headers=HDR,
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["created"] is True
    assert j["yi_user_id"] >= 1
    assert j["person_key"] == "self"
    assert j["firebase_uid"] == "uid_abc"


def test_idempotent_relink_same_uid(client):
    payload = {"firebase_uid": "uid_x", "display_name": "A"}
    r1 = client.post("/api/sync/upsert-from-firebase", json=payload, headers=HDR).json()
    r2 = client.post(
        "/api/sync/upsert-from-firebase",
        json={**payload, "display_name": "A2"},
        headers=HDR,
    ).json()
    assert r2["created"] is False
    assert r1["yi_user_id"] == r2["yi_user_id"]


def test_birth_stored_in_self_person(client):
    client.post(
        "/api/sync/upsert-from-firebase",
        json={
            "firebase_uid": "uid_b",
            "birth": {"datetime_local": "1988-03-15T07:30:00", "gender": "nam"},
        },
        headers=HDR,
    )
    r = client.get("/api/sync/resolve/uid_b", headers=HDR)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["found"] is True
    assert j["self_person"]["birth_datetime_local"] == "1988-03-15T07:30:00"
    assert j["self_person"]["gender"] == "nam"


def test_resolve_unknown_uid(client):
    r = client.get("/api/sync/resolve/does_not_exist", headers=HDR)
    assert r.status_code == 200
    assert r.json()["found"] is False


def test_link_existing_email_user(client):
    """A user that already exists by email (e.g. registered on YI web) gets
    linked to the firebase_uid rather than duplicated."""
    # Seed a user directly via the auth DB with a known email, no firebase_uid.
    import api.auth as auth
    db = auth._connect()
    auth._init_schema(db)
    pw, salt = auth._hash_password("x")
    db.execute(
        "INSERT INTO users (email, display_name, password_hash, password_salt, role, created_at) "
        "VALUES ('web@example.com','Web','" + pw + "','" + salt + "','user', 1)"
    )
    db.commit()
    uid_row = db.execute("SELECT user_id FROM users WHERE email='web@example.com'").fetchone()
    existing_id = uid_row[0]
    db.close()

    r = client.post(
        "/api/sync/upsert-from-firebase",
        json={"firebase_uid": "uid_web", "email": "web@example.com", "display_name": "Web"},
        headers=HDR,
    ).json()
    assert r["yi_user_id"] == existing_id
    assert r["created"] is False
