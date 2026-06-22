"""#55/#56 — lớp dịch vụ liên-phái: trừ 30 xu + cache "một việc một lần" (Iron #4)
+ HOÀN xu khi engine lỗi + thiếu xu → insufficient_xu.

Test LÕI charging (mock cache/save/ví) — KHÔNG cần DB thật cho nhánh quyết định tiền.
"""
from __future__ import annotations

import engine.cross_paradigm.service as S


def _patch_store(monkeypatch, cached=None):
    """Mock cache + save (thay DB). cached=None → miss."""
    saved: dict = {}
    monkeypatch.setattr(S, "_cached", lambda uid, m, sig, ttl=S.CACHE_TTL_SEC:
                        ((7, cached) if cached is not None else (None, None)))
    monkeypatch.setattr(S, "_save", lambda uid, m, sig, result: saved.setdefault("id", 42))
    return saved


def _patch_wallet(monkeypatch, ok=True, balance=70):
    calls: dict = {"spend": [], "grant": []}

    def spend(uid, amount, reason, ref=None):
        calls["spend"].append((uid, amount, reason))
        return ({"ok": True, "balance": balance} if ok
                else {"ok": False, "need": amount, "have": 5, "reason": "insufficient_xu"})

    def grant(uid, amount, reason, ref=None):
        calls["grant"].append((uid, amount, reason))
        return balance + amount

    monkeypatch.setattr(S.xu_wallet, "spend", spend)
    monkeypatch.setattr(S.xu_wallet, "grant", grant)
    return calls


def test_charge_30_xu_va_luu(monkeypatch):
    saved = _patch_store(monkeypatch)
    calls = _patch_wallet(monkeypatch, ok=True, balance=70)
    out = S._charge_and_run(1, "cross_paradigm_hon_nhan", "sig",
                            lambda: {"method_id": "x", "paradigm_ok": True})
    assert out["charged_xu"] == 30 and out["gia_xu"] == 30
    assert out["cached"] is False and out["xu_balance"] == 70
    assert calls["spend"] and calls["spend"][0][1] == 30, "phải trừ đúng 30 xu"
    assert saved.get("id") == 42, "phải lưu lịch sử (cache)"


def test_cache_khong_tru_lai(monkeypatch):
    """Iron #4 'một việc một lần': cùng input trong TTL → cache hit, KHÔNG trừ xu lại."""
    _patch_store(monkeypatch, cached={"method_id": "x", "paradigm_ok": True})
    calls = _patch_wallet(monkeypatch, ok=True)
    out = S._charge_and_run(1, "cross_paradigm_hon_nhan", "sig",
                            lambda: {"never": "called"})
    assert out["cached"] is True and out["charged_xu"] == 0
    assert not calls["spend"], "cache hit KHÔNG được trừ xu lại"


def test_hoan_xu_khi_engine_loi(monkeypatch):
    """Engine ném lỗi SAU khi đã trừ → HOÀN xu (tiền không nuốt)."""
    _patch_store(monkeypatch)
    calls = _patch_wallet(monkeypatch, ok=True)

    def boom():
        raise RuntimeError("engine lỗi")

    import pytest
    with pytest.raises(RuntimeError):
        S._charge_and_run(1, "cross_paradigm_couple_sync", "sig", boom)
    assert calls["spend"] and calls["grant"], "lỗi engine phải HOÀN xu"
    assert calls["grant"][0][1] == 30, "hoàn đúng 30 xu đã trừ"


def test_thieu_xu_khong_chay_engine(monkeypatch):
    _patch_store(monkeypatch)
    calls = _patch_wallet(monkeypatch, ok=False)
    ran = {"v": False}

    def run():
        ran["v"] = True
        return {}

    out = S._charge_and_run(1, "cross_paradigm_hon_nhan", "sig", run)
    assert out["status"] == "insufficient_xu" and out["gia_xu"] == 30
    assert ran["v"] is False, "thiếu xu → KHÔNG chạy engine"
    assert not calls["grant"], "chưa trừ được thì không hoàn"
