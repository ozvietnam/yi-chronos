"""H5 — luận sâu DeepSeek: orchestration THỐNG NHẤT XU (2026-07-27):
cache (đã luận → miễn phí) → trừ 99 xu (owner miễn) → sinh (MOCK) → lưu → HOÀN nếu lỗi.
Chạy 2 driver, generation MOCK (không gọi DeepSeek thật) + endpoint gating.
"""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.deep_reading as dr
import engine.llm_spend as llm_spend
import engine.xu_wallet as xu_wallet

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])
HDR = {"X-API-Key": "test-secret"}


def _stub_ok(person, uid):
    return {"status": "ok", "provider": "mock", "model": "stub",
            "phe_menh": "Cấu trúc lá số vận hành tốt khi…", "sections": [1, 2, 3]}


def _stub_must_not_call(person, uid):
    raise AssertionError("generate KHÔNG được gọi (cache/xu/ngân sách phải chặn trước)")


def _seed(uid="uid_h5", *, birth=True, xu=500):
    """Tạo user (role=user) + person self + nạp `xu` vào ví (thay gói VIP cũ)."""
    with db.session_scope(service=True) as conn:
        user_id = conn.execute(
            text("INSERT INTO users(email,display_name,password_hash,password_salt,"
                 "role,firebase_uid,created_at) VALUES (:e,:d,'h','s','user',:u,1) "
                 "RETURNING user_id"),
            {"e": f"{uid}@x", "d": "U", "u": uid},
        ).scalar()
        if birth:
            conn.execute(
                text("INSERT INTO user_persons(user_id,person_key,name,gender,"
                     "birth_datetime_local,timezone,created_at) VALUES "
                     "(:u,'self','U','nam','1988-06-05T23:30:00','Asia/Ho_Chi_Minh',1)"),
                {"u": user_id},
            )
    if xu:
        xu_wallet.grant(user_id, xu, "test_seed")
    return user_id


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "50")
    if request.param == "sqlite":
        path = tmp_path / "users.sqlite3"
        monkeypatch.setattr(__import__("api.auth", fromlist=["AUTH_DB"]), "AUTH_DB", path)
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
        db.get_engine.cache_clear()
        import api.sync as sync
        sync._ensure_schema()                       # tạo users(+firebase_uid)/persons/...
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.get_engine().begin() as conn:
            db.apply_schema(conn)
        with db.session_scope(service=True) as conn:
            conn.execute(text("TRUNCATE users, user_persons, user_castings, "
                              "user_subscriptions, xu_wallet, xu_ledger, llm_spend "
                              "RESTART IDENTITY CASCADE"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


# ─── orchestration ───────────────────────────────────────────────────────────

def test_happy_path_charges_xu_and_saves(backend):
    uid = _seed(xu=500)
    r = dr.run_deep_reading("uid_h5", generate=_stub_ok)
    assert r["status"] == "done" and r["casting_id"] >= 1
    assert r["cached"] is False
    assert xu_wallet.get_balance(uid) == 500 - dr.DEEP_XU     # trừ đúng 99 xu
    assert llm_spend.day_total() > 0                          # record_spend (cost-safety)
    with db.session_scope(service=True) as conn:
        row = conn.execute(text("SELECT method, tags FROM user_castings WHERE id=:i"),
                           {"i": r["casting_id"]}).fetchone()
    assert row[0] == "tu_vi" and "deep" in row[1]


def test_cache_reload_does_not_charge_again(backend):
    """GỐC bug Anh 2026-07-27: mở lại KHÔNG được trừ xu lần nữa."""
    uid = _seed(xu=500)
    r1 = dr.run_deep_reading("uid_h5", generate=_stub_ok)
    assert r1["cached"] is False and xu_wallet.get_balance(uid) == 500 - dr.DEEP_XU
    # gọi LẠI (không force) → trả bản cũ, KHÔNG trừ thêm, KHÔNG sinh lại
    r2 = dr.run_deep_reading("uid_h5", generate=_stub_must_not_call)
    assert r2["status"] == "done" and r2["cached"] is True
    assert xu_wallet.get_balance(uid) == 500 - dr.DEEP_XU     # y nguyên, không trừ lần 2
    # get_latest cũng trả bản cũ, không trừ
    assert dr.get_latest(user_id=uid)["phe_menh"]
    assert xu_wallet.get_balance(uid) == 500 - dr.DEEP_XU


def test_force_reruns_and_charges(backend):
    uid = _seed(xu=500)
    dr.run_deep_reading("uid_h5", generate=_stub_ok)
    r = dr.run_deep_reading("uid_h5", force=True, generate=_stub_ok)   # luận lại → trừ tiếp
    assert r["cached"] is False
    assert xu_wallet.get_balance(uid) == 500 - 2 * dr.DEEP_XU


def test_owner_free(backend):
    """Chủ tài khoản (role=owner) luận sâu KHÔNG trừ xu."""
    uid = _seed(xu=0)
    with db.session_scope(service=True) as conn:
        conn.execute(text("UPDATE users SET role='owner' WHERE user_id=:u"), {"u": uid})
    r = dr.run_deep_reading("uid_h5", generate=_stub_ok)
    assert r["status"] == "done" and xu_wallet.get_balance(uid) == 0


def test_user_id_path_web(backend):
    uid = _seed(xu=500)
    pc = dr.precheck(user_id=uid)
    assert pc["ok"] is True and pc["user_id"] == uid
    r = dr.run_deep_reading(user_id=uid, generate=_stub_ok)
    assert r["status"] == "done" and r.get("phe_menh")


def test_records_real_provider_cost(backend):
    _seed(xu=500)
    def gen(person, uid):
        return {"status": "ok", "provider": "anthropic", "cost_usd": 0.42,
                "tokens": {"prompt": 1200, "completion": 800}, "phe_menh": "…"}
    r = dr.run_deep_reading("uid_h5", generate=gen)
    assert r["status"] == "done"
    assert abs(llm_spend.day_total() - 0.42) < 1e-6


def test_denied_without_xu(backend):
    uid = _seed(xu=0)
    r = dr.run_deep_reading("uid_h5", generate=_stub_must_not_call)
    assert r["status"] == "denied" and r["reason"] == "insufficient_xu"
    assert r["need"] == dr.DEEP_XU


def test_budget_hard_stop_refunds_xu(backend, monkeypatch):
    uid = _seed(xu=500)
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "0")   # ngân sách 0 → luôn over
    r = dr.run_deep_reading("uid_h5", generate=_stub_must_not_call)
    assert r["status"] == "budget_exceeded"
    assert xu_wallet.get_balance(uid) == 500          # xu đã trừ được HOÀN


def test_not_synced(backend):
    r = dr.run_deep_reading("nobody", generate=_stub_must_not_call)
    assert r["status"] == "error" and r["reason"] == "not_synced"


def test_missing_birth(backend):
    _seed(birth=False, xu=500)
    r = dr.run_deep_reading("uid_h5", generate=_stub_must_not_call)
    assert r["status"] == "error" and r["reason"] == "missing_birth"


def test_generation_error_refunds_xu(backend):
    uid = _seed(xu=500)
    r = dr.run_deep_reading("uid_h5", generate=lambda p, u: {"status": "error", "message": "x"})
    assert r["status"] == "error" and r["reason"] == "generation_failed"
    assert xu_wallet.get_balance(uid) == 500          # HOÀN xu khi sinh lỗi
    assert llm_spend.day_total() == 0


# ─── endpoint gating (pre-check, không cần broker) ──────────────────────────

@pytest.fixture
def client(backend):
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_endpoint_requires_service_key(client):
    r = client.post("/api/sync/deep-reading", json={"firebase_uid": "x"})
    assert r.status_code == 401


def test_endpoint_404_not_synced(client):
    r = client.post("/api/sync/deep-reading", json={"firebase_uid": "ghost"}, headers=HDR)
    assert r.status_code == 404


def test_endpoint_402_no_xu(client):
    _seed(xu=0)
    r = client.post("/api/sync/deep-reading", json={"firebase_uid": "uid_h5"}, headers=HDR)
    assert r.status_code == 402


def test_endpoint_enqueue_eager(client, monkeypatch):
    _seed(xu=500)
    from engine.tasks.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    monkeypatch.setattr(dr, "run_deep_reading",
                        lambda *a, **k: {"status": "done", "casting_id": 1})
    try:
        r = client.post("/api/sync/deep-reading", json={"firebase_uid": "uid_h5"}, headers=HDR)
        assert r.status_code == 200 and r.json()["status"] == "processing"
        assert r.json()["job_id"]
    finally:
        celery_app.conf.task_always_eager = False
