"""H6.0 slice 2 — orchestration Hội Đồng (scope guard + gate + ngân sách + post-filter)."""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.hermes_service as hs
import engine.llm_spend as llm_spend
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


def test_denied_without_subscription(backend):
    _seed(sub=False)
    r = hs.run_council("uid_h6", Q, consult=_consult_must_not_call)
    assert r["status"] == "denied" and r["reason"] == "no_subscription"


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
