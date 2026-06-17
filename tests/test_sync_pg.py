"""P0-2b — bridge sync/history chạy trên Postgres thật (gated YI_TEST_PG_DSN).

Chứng minh sau khi chuyển api/sync.py sang engine.db: toàn luồng cầu (upsert →
save casting/favorite → history → resolve) hoạt động trên Postgres (JSONB cast +
RETURNING + RLS service-mode). CI không có PG → skip.
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
pytestmark = pytest.mark.skipif(not PG_DSN, reason="cần YI_TEST_PG_DSN (Postgres)")
HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(monkeypatch):
    import engine.db as db
    monkeypatch.setenv("DATABASE_URL", PG_DSN)
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    db.get_engine.cache_clear()
    with db.get_engine().begin() as conn:
        db.apply_schema(conn)
    with db.session_scope(service=True) as conn:
        conn.execute(text("TRUNCATE user_castings, user_favorites, user_persons, "
                          "user_subscriptions, users RESTART IDENTITY CASCADE"))
    from api.main import app
    yield TestClient(app)
    db.get_engine.cache_clear()


def test_full_bridge_flow_on_postgres(client):
    # 1. upsert (tạo shadow user + person self)
    r = client.post("/api/sync/upsert-from-firebase", json={
        "firebase_uid": "uid_pg", "display_name": "PG User",
        "birth": {"datetime_local": "1990-08-20T09:30:00", "gender": "nữ", "birth_place": "HN"},
    }, headers=HDR)
    assert r.status_code == 200, r.text
    assert r.json()["created"] is True
    uid = r.json()["yi_user_id"]

    # idempotent
    r2 = client.post("/api/sync/upsert-from-firebase", json={
        "firebase_uid": "uid_pg", "display_name": "PG User 2"}, headers=HDR)
    assert r2.json()["created"] is False and r2.json()["yi_user_id"] == uid

    # 2. resolve trả person self (birth canonical)
    rs = client.get("/api/sync/resolve/uid_pg", headers=HDR).json()
    assert rs["found"] and rs["self_person"]["birth_datetime_local"] == "1990-08-20T09:30:00"

    # 3. save casting (JSONB cast + RETURNING id + algo_version)
    rc = client.post("/api/sync/castings", json={
        "firebase_uid": "uid_pg", "method": "tu_vi", "question": "Lá số?",
        "result_json": {"cung_menh": "Tử Phủ"}}, headers=HDR)
    assert rc.status_code == 200 and rc.json()["id"] >= 1
    assert rc.json()["algo_version"].endswith("tu_vi-1")

    # 4. save favorite (couple_match)
    rf = client.post("/api/sync/favorites", json={
        "firebase_uid": "uid_pg", "kind": "couple_match", "label": "M",
        "payload_json": {"score": 82}}, headers=HDR)
    assert rf.status_code == 200 and rf.json()["id"] >= 1

    # 5. history hợp nhất, mới nhất trước, JSONB parse đúng
    h = client.get("/api/sync/history/uid_pg", headers=HDR).json()
    assert h["found"] and h["count"] == 2
    kinds = {it["type"] for it in h["items"]}
    assert kinds == {"casting", "favorite"}
    casting = next(it for it in h["items"] if it["type"] == "casting")
    assert casting["result"]["cung_menh"] == "Tử Phủ"   # JSONB → dict OK

    # 6. unknown uid → 404 / not found
    assert client.post("/api/sync/castings", json={
        "firebase_uid": "nope", "method": "tu_vi", "result_json": {}},
        headers=HDR).status_code == 404
    assert client.get("/api/sync/history/nope", headers=HDR).json()["found"] is False
