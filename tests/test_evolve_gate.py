"""H6.2 — cổng duyệt tự tiến hoá theo độ tự tin (engine/evolve_gate)."""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.evolve_gate as eg

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'e.sqlite3'}")
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.session_scope(service=True) as c:
            eg._ensure(c)
            c.execute(text("DELETE FROM evolve_proposals"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_decide_matrix():
    assert eg.decide(0.95, "low") == "auto_approved"     # tin cao + tác động nhỏ
    assert eg.decide(0.95, "high") == "pending"          # trường phái mới → luôn anh duyệt
    assert eg.decide(0.50, "low") == "pending"           # tin thấp → anh quyết
    assert eg.decide(0.85, "low") == "auto_approved"     # đúng ngưỡng


def test_auto_approve_high_conf_low_impact(backend):
    r = eg.submit_proposal(kind="wiki_atom", payload={"term": "Lộc Tồn"},
                           confidence=0.92, impact="low", title="thêm trích dẫn")
    assert r["status"] == "auto_approved"
    assert eg.get_proposal(r["id"])["reviewer"] == "ai-auto"
    assert eg.list_pending() == []                        # không nằm hàng đợi anh


def test_new_school_always_pending(backend):
    r = eg.submit_proposal(kind="new_school", payload={"name": "Tử Vi Nam Phái"},
                           confidence=0.99, impact="high", title="trường phái mới")
    assert r["status"] == "pending"
    assert any(p["id"] == r["id"] for p in eg.list_pending())


def test_low_conf_pending_then_anh_review(backend):
    r = eg.submit_proposal(kind="skill_edit", payload={"x": 1}, confidence=0.4, impact="low")
    assert r["status"] == "pending"
    out = eg.review(r["id"], approve=True, reviewer="ceo@ngantin.vn", note="ok")
    assert out["status"] == "approved" and out["updated"] is True
    assert eg.get_proposal(r["id"])["status"] == "approved"
    # duyệt lại không còn pending
    assert eg.review(r["id"], approve=False, reviewer="x")["status"] == "not_pending"


def test_reject(backend):
    r = eg.submit_proposal(kind="skill_edit", payload={}, confidence=0.3)
    out = eg.review(r["id"], approve=False, reviewer="ceo@ngantin.vn", note="sai paradigm")
    assert out["status"] == "rejected"
    assert eg.get_proposal(r["id"])["status"] == "rejected"
