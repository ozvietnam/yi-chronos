"""H1 + H2 — lịch sử user chảy qua cầu (service-keyed) và đọc hợp nhất.

H1: AppChat (qua Cloud Functions, cầm service key) đẩy mỗi lần cast / so khớp
    vào YI → lưu `user_castings` / `user_favorites`, **đóng dấu `algo_version`**.
H2: AppChat đọc lại lịch sử hợp nhất (castings + favorites) theo firebase_uid,
    mới nhất trước, phân trang + lọc.

Cùng hợp đồng auth service-to-service như api/sync.py (X-API-Key + firebase_uid).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(monkeypatch, tmp_path):
    db = tmp_path / "users.sqlite3"
    import api.auth as auth
    monkeypatch.setattr(auth, "AUTH_DB", db)
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    from api.main import app
    return TestClient(app)


def _sync_user(client, uid="uid_hist"):
    r = client.post(
        "/api/sync/upsert-from-firebase",
        json={"firebase_uid": uid, "display_name": "Tester"},
        headers=HDR,
    )
    assert r.status_code == 200, r.text
    return r.json()["yi_user_id"]


# ─── H1: save casting via bridge ────────────────────────────────────────────

def test_save_casting_requires_service_key(client):
    r = client.post("/api/sync/castings", json={"firebase_uid": "x", "method": "tu_vi",
                                                 "result_json": {}})
    assert r.status_code == 401


def test_save_casting_unknown_uid_404(client):
    r = client.post(
        "/api/sync/castings",
        json={"firebase_uid": "never_synced", "method": "tu_vi", "result_json": {"a": 1}},
        headers=HDR,
    )
    assert r.status_code == 404


def test_save_casting_stamps_algo_version(client):
    _sync_user(client)
    r = client.post(
        "/api/sync/castings",
        json={
            "firebase_uid": "uid_hist",
            "method": "tu_vi",
            "question": "Lá số của tôi?",
            "result_json": {"cung_menh": "Tử Phủ"},
        },
        headers=HDR,
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "ok" and j["id"] >= 1
    # The reading records WHICH version computed it — the heart of freshness.
    from engine.algo_version import algo_version
    assert j["algo_version"] == algo_version("tu_vi")


# ─── H1: save favorite (e.g. gieo duyên couple_match) via bridge ─────────────

def test_save_favorite_via_bridge(client):
    _sync_user(client)
    r = client.post(
        "/api/sync/favorites",
        json={
            "firebase_uid": "uid_hist",
            "kind": "couple_match",
            "label": "Tôi × Lan Anh",
            "payload_json": {"score": 82},
        },
        headers=HDR,
    )
    assert r.status_code == 200, r.text
    assert r.json()["id"] >= 1


# ─── H2: unified history read ───────────────────────────────────────────────

def test_history_merges_castings_and_favorites_newest_first(client):
    _sync_user(client)
    client.post("/api/sync/castings", json={
        "firebase_uid": "uid_hist", "method": "tu_vi", "result_json": {"n": 1}}, headers=HDR)
    client.post("/api/sync/castings", json={
        "firebase_uid": "uid_hist", "method": "luc_hao", "result_json": {"n": 2}}, headers=HDR)
    client.post("/api/sync/favorites", json={
        "firebase_uid": "uid_hist", "kind": "couple_match", "label": "M",
        "payload_json": {"score": 70}}, headers=HDR)

    r = client.get("/api/sync/history/uid_hist", headers=HDR)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["found"] is True
    assert j["count"] == 3
    items = j["items"]
    # Newest first (created_at descending).
    ts = [it["created_at"] for it in items]
    assert ts == sorted(ts, reverse=True)
    # Both record types present, each tagged.
    kinds = {it["type"] for it in items}
    assert kinds == {"casting", "favorite"}


def test_history_filter_by_method(client):
    _sync_user(client)
    client.post("/api/sync/castings", json={
        "firebase_uid": "uid_hist", "method": "tu_vi", "result_json": {}}, headers=HDR)
    client.post("/api/sync/castings", json={
        "firebase_uid": "uid_hist", "method": "bat_tu", "result_json": {}}, headers=HDR)
    r = client.get("/api/sync/history/uid_hist?method=tu_vi", headers=HDR)
    j = r.json()
    assert j["count"] == 1
    assert all(it["type"] == "casting" and it["method"] == "tu_vi" for it in j["items"])


def test_history_pagination(client):
    _sync_user(client)
    for i in range(5):
        client.post("/api/sync/castings", json={
            "firebase_uid": "uid_hist", "method": "tu_vi", "result_json": {"i": i}}, headers=HDR)
    r = client.get("/api/sync/history/uid_hist?limit=2&offset=0", headers=HDR)
    assert r.json()["count"] == 2


def test_history_unknown_uid(client):
    r = client.get("/api/sync/history/nobody", headers=HDR)
    assert r.status_code == 200
    assert r.json()["found"] is False


def test_history_requires_service_key(client):
    r = client.get("/api/sync/history/uid_hist")
    assert r.status_code == 401
