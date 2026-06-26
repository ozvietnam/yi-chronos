"""Iron #9 (Brahmajāla) — DISCLAIMER PHẢI gắn vào output CUỐI mọi sản phẩm sage.

Tuyên ngôn Iron #9: Tử Vi chỉ MƯỢN khung Phật để SOI TÂM, không phải giáo lý chính
thống → user luôn phải THẤY dòng disclaimer ở cuối lời thầy / hội đồng / lời nhanh.

Wire điểm (M1-A3):
  • engine.cross_paradigm.narrate.narrate_tinh_duyen  → lời thầy tình duyên
  • engine.hermes_service.run_quick                   → trả lời nhanh 1-sage
  • engine.hermes_service.run_council                 → tổng hợp hội đồng

Mọi điểm gọi guard.with_disclaimer(...) (idempotent — không nhân đôi). Test mock
toàn bộ LLM (inject callable answer/consult, fake run_agent) → nhanh + deterministic.
"""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.hermes_service as hs
import engine.ratelimit as rl
import engine.subscriptions as subs
from engine.hermes_guard import DISCLAIMER, with_disclaimer

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])
Q = "Lá số Tử Vi của em nói gì về hướng sự nghiệp?"

# Lời sạch, paradigm-safe (qua guard) — KHÔNG sẵn disclaimer.
_BODY = "Cung Quan có Thái Dương — anh thiên dẫn dắt; anh thấy điều đó thế nào?"


# ── 1. Đơn vị: with_disclaimer (hợp đồng idempotent) ─────────────────────────

def test_with_disclaimer_appends_once():
    out = with_disclaimer(_BODY)
    assert out.startswith(_BODY)
    assert out.rstrip().endswith(DISCLAIMER)
    assert out.count(DISCLAIMER) == 1


def test_with_disclaimer_idempotent_no_double():
    once = with_disclaimer(_BODY)
    twice = with_disclaimer(once)
    assert once == twice                 # gọi lại KHÔNG nhân đôi
    assert twice.count(DISCLAIMER) == 1


def test_with_disclaimer_empty_returns_disclaimer():
    assert with_disclaimer("") == DISCLAIMER
    assert with_disclaimer(None) == DISCLAIMER


# ── 2. Tích hợp: hermes_service (quick + council) ────────────────────────────

def _seed(uid="uid_d", *, birth=True):
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


def _ans(q, p, u):
    return {"answer": _BODY, "sage": "tu_vi", "provider": "mock",
            "cost_usd": 0.0, "tokens": {}}


def _consult(q, p, u):
    return {"synthesis": _BODY, "agents": ["tu_vi"], "provider": "mock",
            "cost_usd": 0.0, "raw": {"round_1_outputs": []}}


def test_run_quick_appends_disclaimer(backend):
    _seed()
    r = hs.run_quick("uid_d", Q, answer=_ans)
    assert r["status"] == "done"
    assert r["answer"].startswith(_BODY)
    assert r["answer"].rstrip().endswith(DISCLAIMER)
    assert r["answer"].count(DISCLAIMER) == 1


def test_run_quick_cached_also_has_disclaimer(backend):
    """Cache hit (Iron #4 'một việc một lần') vẫn phải kèm disclaimer, không nhân đôi."""
    _seed()
    r1 = hs.run_quick("uid_d", Q, answer=_ans)
    r2 = hs.run_quick("uid_d", Q, answer=lambda *a: (_ for _ in ()).throw(
        AssertionError("answer KHÔNG được gọi lại — phải cache")))
    assert r2["cached"] is True
    assert r2["answer"].rstrip().endswith(DISCLAIMER)
    assert r2["answer"].count(DISCLAIMER) == 1
    assert r2["answer"] == r1["answer"]


def test_run_council_appends_disclaimer(backend):
    _seed()
    r = hs.run_council("uid_d", Q, consult=_consult)
    assert r["status"] == "done"
    assert r["synthesis"].startswith(_BODY)
    assert r["synthesis"].rstrip().endswith(DISCLAIMER)
    assert r["synthesis"].count(DISCLAIMER) == 1


def test_run_council_cached_also_has_disclaimer(backend):
    _seed()
    r1 = hs.run_council("uid_d", Q, consult=_consult)
    r2 = hs.run_council("uid_d", Q, consult=lambda *a: (_ for _ in ()).throw(
        AssertionError("consult KHÔNG được gọi lại — phải cache")))
    assert r2["cached"] is True
    assert r2["synthesis"].rstrip().endswith(DISCLAIMER)
    assert r2["synthesis"].count(DISCLAIMER) == 1
    assert r2["synthesis"] == r1["synthesis"]


def test_run_quick_paradigm_guard_runs_on_body_not_disclaimer(backend):
    """Guard soi giọng tiên tri trên THÂN bài (trước khi gắn disclaimer) → disclaimer
    trung tính KHÔNG làm sai paradigm_ok; thân sạch ⇒ paradigm_ok=True."""
    _seed()
    r = hs.run_quick("uid_d", Q, answer=_ans)
    assert r["paradigm_ok"] is True
    assert r["answer"].rstrip().endswith(DISCLAIMER)


# ── 3. CHOKEPOINT ENGINE: consult_council.final_synthesis (M1-FIX-B) ──────────
# Lỗ hổng M1: /api/ai/council/consult gọi THẲNG consult_council, KHÔNG qua
# hermes_service.run_council → trước đây synthesis tới user KHÔNG có disclaimer.
# Vá CỨNG tại _orchestrator_synthesize → mọi caller (direct API, async job, session
# đọc-lại) đều có. Test mock toàn bộ provider (force_mock_council) → nhanh.

def test_consult_council_synthesis_has_disclaimer(force_mock_council):
    """final_synthesis (output engine, KHÔNG qua hermes_service) PHẢI kèm disclaimer."""
    from engine.ai.council import consult_council
    r = consult_council(
        question=Q, chart_data={"day_master": "Kỷ"},
        explicit_agents=["tu_vi"], skip_challenge=True, persist=False,
    )
    syn = r["final_synthesis"]
    assert syn, "phải có synthesis"
    assert DISCLAIMER in syn
    assert syn.rstrip().endswith(DISCLAIMER)
    assert syn.count(DISCLAIMER) == 1


def test_consult_council_synthesis_disclaimer_not_doubled_by_hermes(force_mock_council, backend):
    """Idempotent xuyên 2 lớp: engine gắn 1 lần; hermes_service.run_council gắn lại
    cũng KHÔNG nhân đôi (with_disclaimer thấy đã có → bỏ qua)."""
    from engine.ai.council import consult_council
    _seed()

    def _consult_real(q, p, u):
        s = consult_council(question=q, chart_data={}, explicit_agents=["tu_vi"],
                            skip_challenge=True, persist=False)
        return {"synthesis": s["final_synthesis"], "agents": ["tu_vi"],
                "provider": "mock", "cost_usd": 0.0, "raw": {"round_1_outputs": []}}

    r = hs.run_council("uid_d", Q, consult=_consult_real)
    assert r["status"] == "done"
    assert r["synthesis"].rstrip().endswith(DISCLAIMER)
    assert r["synthesis"].count(DISCLAIMER) == 1   # KHÔNG nhân đôi xuyên 2 lớp
