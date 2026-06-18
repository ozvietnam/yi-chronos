"""H6.0 — đường trả lời nhanh 1-sage (run_quick): scope + gate free/paid + post-filter."""
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
Q = "Lá số Tử Vi của em nói gì về hướng sự nghiệp?"


def _ans_ok(q, p, u):
    return {"answer": "Cung Quan có Thái Dương — anh thiên dẫn dắt; anh thấy điều đó thế nào?",
            "sage": "tu_vi", "provider": "mock", "cost_usd": 0.0, "tokens": {}}


def _ans_predictive(q, p, u):
    return {"answer": "Năm 2027 anh chắc chắn sẽ giàu to.", "sage": "tu_vi",
            "provider": "mock", "cost_usd": 0.0, "tokens": {}}


def _ans_must_not_call(q, p, u):
    raise AssertionError("answer KHÔNG được gọi (cổng phải chặn trước)")


def _seed(uid="uid_q", *, birth=True, sub=False, remaining=1):
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
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'u.sqlite3'}")
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
    rl.reset()
    yield request.param
    db.get_engine.cache_clear()


def test_out_of_scope_blocks():
    r = hs.run_quick("x", "Viết hộ em code Python", answer=_ans_must_not_call)
    assert r["status"] == "out_of_scope" and r["reply"]


def test_free_tier_quick_happy(backend):
    _seed(sub=False)
    r = hs.run_quick("uid_q", Q, answer=_ans_ok)
    assert r["status"] == "done" and r["tier"] == "free" and r["sage"] == "tu_vi"
    assert r["paradigm_ok"] is True
    with db.session_scope(service=True) as c:
        m = c.execute(text("SELECT method FROM user_castings WHERE id=:i"),
                      {"i": r["casting_id"]}).scalar()
    assert m == "hermes_quick"


def test_free_quick_cap_then_denied(backend):
    _seed(sub=False)
    for i in range(hs.FREE_DAILY_QUICK):     # câu KHÁC nhau → không cache, tiêu quota thật
        assert hs.run_quick("uid_q", f"{Q} (câu {i})", answer=_ans_ok)["status"] == "done"
    r = hs.run_quick("uid_q", f"{Q} (câu cuối)", answer=_ans_must_not_call)
    assert r["status"] == "denied"


def test_post_filter_flags_predictive(backend):
    _seed(sub=False)
    r = hs.run_quick("uid_q", Q, answer=_ans_predictive)
    assert r["status"] == "done" and r["paradigm_ok"] is False


def test_budget_blocks(backend, monkeypatch):
    _seed(sub=False)
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "0")
    r = hs.run_quick("uid_q", Q, answer=_ans_must_not_call)
    assert r["status"] == "budget_exceeded"


def test_answer_failed_no_charge(backend):
    _seed(sub=False)
    r = hs.run_quick("uid_q", Q, answer=lambda q, p, u: {"answer": ""})
    assert r["status"] == "error" and r["reason"] == "answer_failed"
    assert llm_spend.day_total() == 0


def test_not_synced(backend):
    r = hs.run_quick("ghost", Q, answer=_ans_must_not_call)
    assert r["status"] == "error" and r["reason"] == "not_synced"


def test_cache_one_question_once(backend):
    """'Một việc một lần' (Iron #4): hỏi lại cùng câu → cache hit, KHÔNG gọi LLM/tính tiền."""
    _seed(sub=False)
    r1 = hs.run_quick("uid_q", Q, answer=_ans_ok)
    assert r1["status"] == "done" and not r1.get("cached")
    spent = llm_spend.day_total()
    r2 = hs.run_quick("uid_q", Q, answer=_ans_must_not_call)   # answer KHÔNG được gọi
    assert r2["status"] == "done" and r2["cached"] is True
    assert r2["casting_id"] == r1["casting_id"]                # trả lại đúng kết quả cũ
    assert llm_spend.day_total() == spent                     # KHÔNG tính tiền lần 2


# ── endpoint ─────────────────────────────────────────────────────────────────

HDR = {"X-API-Key": "test-secret"}


@pytest.fixture
def client(backend, monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", "test-secret")
    from api.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_endpoint_requires_key(client):
    assert client.post("/api/sync/hermes-quick", json={"firebase_uid": "x", "question": Q}).status_code == 401


def test_endpoint_out_of_scope_reply(client):
    r = client.post("/api/sync/hermes-quick",
                    json={"firebase_uid": "x", "question": "Làm hộ em bài tập toán"}, headers=HDR)
    assert r.status_code == 200 and r.json()["status"] == "out_of_scope"


def test_endpoint_404(client):
    r = client.post("/api/sync/hermes-quick",
                    json={"firebase_uid": "ghost", "question": Q}, headers=HDR)
    assert r.status_code == 404


# ── A1: đường WEB (user đăng nhập gọi trực tiếp theo user_id) ─────────────────

def test_run_quick_by_user_id(backend):
    """Web entry: resolve theo user_id (không firebase_uid)."""
    uid = _seed(sub=False)
    r = hs.run_quick("", Q, user_id=uid, answer=_ans_ok)
    assert r["status"] == "done" and r["sage"] == "tu_vi"


def test_web_endpoint_requires_login(client):
    # /api/hermes/ask cần đăng nhập (require_user) → guest 401
    assert client.post("/api/hermes/ask", json={"question": Q}).status_code == 401
