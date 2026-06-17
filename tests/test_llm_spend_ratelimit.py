"""P0-5 — llm_spend ledger (dual-driver) + rate-limit (in-memory fallback)."""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

import engine.db as db
import engine.llm_spend as spend
import engine.ratelimit as rl

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'s.db'}")
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.session_scope(service=True) as conn:
            spend._ensure(conn)
            conn.execute(text("DELETE FROM llm_spend"))
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "1.0")
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_record_and_day_total(backend):
    assert spend.day_total() == 0.0
    spend.record_spend(provider="deepseek", cost_usd=0.30, feature="h5", model="flash")
    spend.record_spend(provider="gemini", cost_usd=0.20, feature="h6")
    assert abs(spend.day_total() - 0.50) < 1e-6
    assert spend.over_daily_budget() is False    # 0.5 < budget 1.0


def test_budget_hard_stop(backend):
    spend.record_spend(provider="deepseek", cost_usd=0.7, feature="h5")
    assert spend.over_daily_budget() is False
    spend.record_spend(provider="deepseek", cost_usd=0.5, feature="h5")  # tổng 1.2 ≥ 1.0
    assert spend.over_daily_budget() is True


def test_spend_summary_breakdown(backend):
    spend.record_spend(provider="deepseek", cost_usd=0.1)
    spend.record_spend(provider="deepseek", cost_usd=0.1)
    spend.record_spend(provider="gemini", cost_usd=0.2)
    s = spend.spend_summary()
    assert s["by_provider"]["deepseek"]["calls"] == 2
    assert abs(s["total_usd"] - 0.4) < 1e-6
    assert s["budget_usd"] == 1.0


# ─── rate-limit (in-memory fallback; không cần Redis daemon) ─────────────────

def test_ratelimit_allows_up_to_limit_then_blocks():
    rl.reset("u:test")
    assert all(rl.allow("u:test", limit=3, window_sec=60) for _ in range(3))
    assert rl.allow("u:test", limit=3, window_sec=60) is False   # lượt 4 → chặn


def test_ratelimit_remaining_and_zero_limit():
    rl.reset("u:rem")
    rl.allow("u:rem", limit=5, window_sec=60)
    assert rl.remaining("u:rem", limit=5, window_sec=60) == 4
    assert rl.allow("u:zero", limit=0) is False                  # limit 0 → luôn chặn


def test_ratelimit_keys_independent():
    rl.reset()
    assert rl.allow("a", 1) is True
    assert rl.allow("a", 1) is False
    assert rl.allow("b", 1) is True                              # key khác độc lập
