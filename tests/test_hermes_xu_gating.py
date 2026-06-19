"""Ví xu trung tâm wire vào Hermes: hết lượt free → TIÊU XU; lỗi → HOÀN XU.

Khẳng định contract mới (Anh chốt 2026-06-19 — YI = ví trung tâm):
  free quota → xu (quick 1 / council 5) → denied(insufficient_xu).
"""
import pytest
from sqlalchemy import text

import engine.db as db
import engine.hermes_service as hs
import engine.ratelimit as rl
import engine.xu_wallet as xu

Q = "Lá số Tử Vi của em nói gì về hướng sự nghiệp?"


def _ans_ok(q, p, u):
    return {"answer": "Cung Quan có Thái Dương — anh thấy điều đó thế nào?",
            "sage": "tu_vi", "provider": "mock", "cost_usd": 0.0, "tokens": {}}


def _ans_boom(q, p, u):
    raise RuntimeError("LLM sập giữa chừng")


def _seed(uid="uid_x"):
    with db.session_scope(service=True) as conn:
        user_id = conn.execute(
            text("INSERT INTO users(email,display_name,password_hash,password_salt,"
                 "role,firebase_uid,created_at) VALUES (:e,'U','h','s','user',:u,1) "
                 "RETURNING user_id"), {"e": f"{uid}@x", "u": uid}).scalar()
        conn.execute(text("INSERT INTO user_persons(user_id,person_key,name,gender,"
                          "birth_datetime_local,timezone,created_at) VALUES "
                          "(:u,'self','U','nam','1990-02-03T08:00:00','Asia/Ho_Chi_Minh',1)"),
                     {"u": user_id})
    return user_id


@pytest.fixture
def backend(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "50")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'u.sqlite3'}")
    db.get_engine.cache_clear()
    import api.sync as sync
    sync._ensure_schema()
    db.get_engine.cache_clear()
    rl.reset()
    yield
    db.get_engine.cache_clear()


def _exhaust_free_quick(uid="uid_x"):
    for i in range(hs.FREE_DAILY_QUICK):
        assert hs.run_quick(uid, f"{Q} (free {i})", answer=_ans_ok)["status"] == "done"


def test_quick_spends_xu_after_free_exhausted(backend):
    user_id = _seed()
    xu.grant(user_id, 5, "topup")
    _exhaust_free_quick()
    r = hs.run_quick("uid_x", f"{Q} (xu 1)", answer=_ans_ok)
    assert r["status"] == "done" and r["tier"] == "xu"
    assert r["xu_cost"] == 1 and r["xu_balance"] == 4
    assert xu.get_balance(user_id) == 4


def test_quick_denied_when_no_free_no_xu(backend):
    _seed()  # 0 xu
    _exhaust_free_quick()
    r = hs.run_quick("uid_x", f"{Q} (cuối)", answer=_ans_ok)
    assert r["status"] == "denied" and r["reason"] == "insufficient_xu"
    assert r["xu_cost"] == 1 and r["have"] == 0


def test_quick_refunds_xu_on_llm_failure(backend):
    user_id = _seed()
    xu.grant(user_id, 3, "topup")
    _exhaust_free_quick()
    with pytest.raises(RuntimeError):
        hs.run_quick("uid_x", f"{Q} (boom)", answer=_ans_boom)
    # đã trừ ở gate nhưng LLM sập → phải hoàn lại nguyên vẹn
    assert xu.get_balance(user_id) == 3


def test_council_spends_5_xu_after_free(backend):
    user_id = _seed()
    xu.grant(user_id, 10, "topup")
    for i in range(hs.FREE_DAILY_COUNCIL):
        rl.allow(f"council_free:{user_id}", hs.FREE_DAILY_COUNCIL, hs._DAY)
    # free đã hết → council tiêu 5 xu
    def _council_ok(q, p, u):
        return {"synthesis": "Đa phái đồng quy về chữ Tâm.", "agents": ["tu_vi", "bat_tu"],
                "provider": "mock", "cost_usd": 0.0}
    r = hs.run_council("uid_x", Q, consult=_council_ok)
    assert r["status"] == "done" and r["tier"] == "xu"
    assert r["xu_cost"] == 5 and r["xu_balance"] == 5
    assert xu.get_balance(user_id) == 5
