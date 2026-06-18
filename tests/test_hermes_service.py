"""H6.0 slice 2 — orchestration Hội Đồng (scope guard + gate + ngân sách + post-filter)."""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.hermes_service as hs
import engine.llm_spend as llm_spend
import engine.ratelimit as rl
import engine.subscriptions as subs

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])
Q = "Lá số Tử Vi của em nói gì về hướng sự nghiệp?"   # in_scope


def _consult_ok(q, person, uid):
    return {"synthesis": "Cấu trúc lá số vận hành tốt khi anh chủ động — anh thấy sao?",
            "agents": ["tu_vi", "bat_tu"], "provider": "mock", "cost_usd": 0.0}


def _consult_predictive(q, person, uid):
    return {"synthesis": "Năm 2027 anh chắc chắn sẽ giàu to.", "agents": ["tu_vi"],
            "provider": "mock", "cost_usd": 0.0}


def _consult_must_not_call(q, person, uid):
    raise AssertionError("consult KHÔNG được gọi (cổng phải chặn trước)")


def _seed(uid="uid_h6", *, birth=True, sub=True, remaining=1):
    with db.session_scope(service=True) as conn:
        user_id = conn.execute(
            text("INSERT INTO users(email,display_name,password_hash,password_salt,"
                 "role,firebase_uid,created_at) VALUES (:e,'U','h','s','user',:u,1) "
                 "RETURNING user_id"), {"e": f"{uid}@x", "u": uid}).scalar()
        if birth:
            conn.execute(text("INSERT INTO user_persons(user_id,person_key,name,gender,"
                              "birth_datetime_local,timezone,created_at) VALUES "
                              "(:u,'self','U','nam','1990-02-03T08:00:00','Asia/Ho_Chi_Minh',1)"),
                         {"u": user_id})
    if sub:
        subs.grant_subscription(user_id, hs.FEATURE, tier="vip1", remaining_uses=remaining)
    return user_id


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "50")
    if request.param == "sqlite":
        path = tmp_path / "users.sqlite3"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
        db.get_engine.cache_clear()
        import api.sync as sync
        sync._ensure_schema()
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.get_engine().begin() as c:
            db.apply_schema(c)
        with db.session_scope(service=True) as c:
            c.execute(text("TRUNCATE users, user_persons, user_castings, "
                           "user_subscriptions, llm_spend RESTART IDENTITY CASCADE"))
    db.get_engine.cache_clear()
    rl.reset()                       # free-tier counter sạch giữa các test
    yield request.param
    db.get_engine.cache_clear()


# ── cổng rẻ (chưa cần DB/sub) ────────────────────────────────────────────────

def test_out_of_scope_blocks_before_everything():
    r = hs.run_council("anyone", "Viết hộ em đoạn code Python", consult=_consult_must_not_call)
    assert r["status"] == "out_of_scope" and r["reply"]


def test_needs_focus_when_vague():
    r = hs.run_council("anyone", "alo", consult=_consult_must_not_call)
    assert r["status"] == "needs_focus"


# ── orchestration ────────────────────────────────────────────────────────────

def test_happy_path(backend):
    _seed(remaining=1)
    r = hs.run_council("uid_h6", Q, consult=_consult_ok)
    assert r["status"] == "done" and r["casting_id"] >= 1
    assert r["paradigm_ok"] is True and r["remaining_uses"] == 0
    assert llm_spend.day_total() > 0
    with db.session_scope(service=True) as c:
        row = c.execute(text("SELECT method, tags FROM user_castings WHERE id=:i"),
                        {"i": r["casting_id"]}).fetchone()
    assert row[0] == "hermes_council" and "council" in row[1]


def test_post_filter_flags_predictive(backend):
    _seed(remaining=1)
    r = hs.run_council("uid_h6", Q, consult=_consult_predictive)
    assert r["status"] == "done" and r["paradigm_ok"] is False
    with db.session_scope(service=True) as c:
        vd = c.execute(text("SELECT verdict FROM user_castings WHERE id=:i"),
                       {"i": r["casting_id"]}).scalar()
    assert vd == "paradigm_flag"


def test_free_tier_3_per_day_then_denied(backend):
    _seed(sub=False)                 # không gói → free tier 3 lượt/ngày
    for _ in range(hs.FREE_DAILY_COUNCIL):
        r = hs.run_council("uid_h6", Q, consult=_consult_ok)
        assert r["status"] == "done" and r["tier"] == "free"
    # hết lượt free → từ chối, KHÔNG gọi council
    r = hs.run_council("uid_h6", Q, consult=_consult_must_not_call)
    assert r["status"] == "denied" and r["reason"] == "no_subscription_and_free_exhausted"


def test_paid_tier_consumes_grant(backend):
    _seed(remaining=1)
    r = hs.run_council("uid_h6", Q, consult=_consult_ok)
    assert r["status"] == "done" and r["tier"] == "paid" and r["remaining_uses"] == 0


def test_budget_blocks_before_council(backend, monkeypatch):
    _seed(remaining=5)
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "0")
    r = hs.run_council("uid_h6", Q, consult=_consult_must_not_call)
    assert r["status"] == "budget_exceeded"


def test_council_failed_no_charge(backend):
    uid = _seed(remaining=1)
    r = hs.run_council("uid_h6", Q, consult=lambda q, p, u: {"synthesis": ""})
    assert r["status"] == "error" and r["reason"] == "council_failed"
    assert subs.check_access(uid, hs.FEATURE)["subscription"]["remaining_uses"] == 1
    assert llm_spend.day_total() == 0


def test_not_synced(backend):
    r = hs.run_council("ghost", Q, consult=_consult_must_not_call)
    assert r["status"] == "error" and r["reason"] == "not_synced"


# ── E2E: chuỗi thật run_council → _real_consult → council (mock provider) ────────

def test_e2e_real_council_path_with_mock_provider(backend, monkeypatch):
    """Không inject consult → đi qua _real_consult thật (cast chart + consult_council).
    Ép provider mock cho deterministic + free. Verify nguyên chuỗi sinh synthesis + lưu."""
    _seed(remaining=1)
    from engine.ai import council
    from engine.ai.registry import get_registry
    mock = get_registry().get("mock")
    monkeypatch.setattr(council, "_get_agent_provider", lambda aid: (mock, "mock"))
    monkeypatch.setattr(council, "_get_orchestrator_provider", lambda: (mock, "mock"))

    r = hs.run_council("uid_h6", Q)          # REAL path, không stub
    assert r["status"] == "done" and r["tier"] == "paid"
    assert r["synthesis"] and r["casting_id"] >= 1 and r["agents"]
    with db.session_scope(service=True) as c:
        n = c.execute(text("SELECT count(*) FROM user_castings WHERE user_id=:u "
                           "AND method='hermes_council'"), {"u": _uid_of("uid_h6")}).scalar()
    assert n == 1


def _uid_of(fb_uid: str) -> int:
    with db.session_scope(service=True) as c:
        return c.execute(text("SELECT user_id FROM users WHERE firebase_uid=:u"),
                         {"u": fb_uid}).scalar()


# ── slice 4: council dùng SOUL sâu (bơm profiles/*/SOUL.md vào prompt_overrides) ─

def test_sync_souls_from_profiles_makes_council_use_deep_soul(tmp_path, monkeypatch):
    from engine.ai import prompt_store
    monkeypatch.setattr(prompt_store, "_DB_PATH", tmp_path / "ai_prompts.sqlite3")
    synced = hs.sync_souls_from_profiles()
    # các sage có profile track → được sync, SOUL sâu (>500 ký tự, không mỏng)
    assert synced.get("tu_vi", 0) > 500 and synced.get("bat_tu", 0) > 300
    assert "than_so" in synced                      # Thần số học vào roster council (Phase-1)
    # council (qua get_prompt) giờ trả SOUL sâu thay persona mặc định
    assert len(prompt_store.get_prompt("tu_vi")) == synced["tu_vi"]


# ── endpoint gating (mirror H5) ──────────────────────────────────────────────

HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(backend, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_endpoint_requires_service_key(client):
    r = client.post("/api/sync/hermes-council", json={"firebase_uid": "x", "question": Q})
    assert r.status_code == 401


def test_endpoint_out_of_scope_returns_reply_no_enqueue(client):
    r = client.post("/api/sync/hermes-council",
                    json={"firebase_uid": "x", "question": "Viết hộ em code Python"}, headers=HDR)
    assert r.status_code == 200 and r.json()["status"] == "out_of_scope" and r.json()["reply"]


def test_endpoint_404_not_synced(client):
    r = client.post("/api/sync/hermes-council",
                    json={"firebase_uid": "ghost", "question": Q}, headers=HDR)
    assert r.status_code == 404


def test_endpoint_403_when_free_exhausted(client):
    uid = _seed(sub=False)
    for _ in range(hs.FREE_DAILY_COUNCIL):       # tiêu hết lượt free
        rl.allow(f"council_free:{uid}", hs.FREE_DAILY_COUNCIL, hs._DAY)
    r = client.post("/api/sync/hermes-council",
                    json={"firebase_uid": "uid_h6", "question": Q}, headers=HDR)
    assert r.status_code == 403


def test_endpoint_enqueue_eager(client, monkeypatch):
    _seed(remaining=1)
    from engine.tasks.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    monkeypatch.setattr(hs, "run_council",
                        lambda uid, q, pk="self": {"status": "done", "casting_id": 1})
    try:
        r = client.post("/api/sync/hermes-council",
                        json={"firebase_uid": "uid_h6", "question": Q}, headers=HDR)
        assert r.status_code == 200 and r.json()["status"] == "processing" and r.json()["job_id"]
    finally:
        celery_app.conf.task_always_eager = False
