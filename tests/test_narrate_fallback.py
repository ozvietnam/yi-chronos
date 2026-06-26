"""Tests cho CHUỖI FALLBACK PROVIDER của narrate_tinh_duyen (Pha A 2026-06-26).

"Lời thầy" tình duyên là sản phẩm TRẢ PHÍ (30 xu) → KHÔNG được phụ thuộc 1 provider.
narrate_tinh_duyen thử lần lượt [deepseek, minimax, gemini]; provider cho kết quả
SẠCH + non-empty đầu tiên → DÙNG; provider rỗng/mock/vi-phạm-không-cứu-được → THỬ kế;
hết chuỗi vẫn fail → '' (UI fallback bản cấu trúc).

Test mock toàn bộ run_agent + registry → KHÔNG gọi LLM thật, chạy nhanh + deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

import engine.cross_paradigm.narrate as narrate_mod
from engine.cross_paradigm.narrate import _NARRATE_PROVIDER_CHAIN, narrate_tinh_duyen


# ── Fakes ────────────────────────────────────────────────────────────────────
@dataclass
class _FakeResp:
    content: str


class _FakeProvider:
    def __init__(self, name: str, configured: bool = True):
        self.name = name
        self.is_configured = configured
        self.default_model = f"{name}-default"


class _FakeRegistry:
    """Registry giả: mọi provider configured, không cái nào unhealthy (trừ khi set)."""

    def __init__(self, configured=None, unhealthy=None):
        self._configured = configured if configured is not None else {
            n: True for n in _NARRATE_PROVIDER_CHAIN
        }
        self._unhealthy = set(unhealthy or [])
        # mock luôn có (an toàn).
        self._providers = {n: _FakeProvider(n, self._configured.get(n, True))
                           for n in _NARRATE_PROVIDER_CHAIN}
        self._providers["mock"] = _FakeProvider("mock", True)

    def get(self, name):
        if name not in self._providers:
            raise KeyError(name)
        return self._providers[name]

    def is_unhealthy(self, name):
        return name in self._unhealthy


# Minimal td/person — đủ để _build_system_prompt + _td_payload_for_llm chạy không crash.
_TD = {
    "input": {"gender": "nữ"},
    "stage": {"tuoi": 30, "giong_van": "chững chạc"},
    "personality": {"profiles": []},
    "cung_phu_the_tuvi": {},
    "batu_hon_nhan": {},
    "song_phai_reconcile": {},
    "cach_cuc": {},
    "dinh_thoi": {},
    "cau_hoi_tuoi": [],
    "chan_doan_cap_do": {},
    "quy_trinh_day_du": {},
    "_disclaimer": "x",
}
_PERSON = {"gender": "nữ"}

# Lời thầy SẠCH (paradigm-safe, không predict) — sẽ qua reframe_check.
_CLEAN = (
    "Cấu trúc của em vận hành tốt nhất khi em chủ động chăm sóc cung phối ngẫu. "
    "Đây là một TÍNH cần ý thức, không phải định mệnh."
)


def _patch(monkeypatch, *, run_agent_fn, registry):
    """Patch run_agent (import bên trong hàm từ engine.ai.agents) + get_registry."""
    import engine.ai.agents as agents_mod
    import engine.ai.registry as registry_mod

    monkeypatch.setattr(agents_mod, "run_agent", run_agent_fn)
    monkeypatch.setattr(registry_mod, "get_registry", lambda: registry)


# ── Tests ────────────────────────────────────────────────────────────────────
def test_provider1_mock_then_provider2_clean_is_used(monkeypatch):
    """provider1 (deepseek) trả mock-leak → fallback; provider2 (minimax) trả sạch → DÙNG."""
    calls = []

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        if provider.name == "deepseek":
            return _FakeResp(content="[MOCK] paste api key")  # mock-leak → bị chặn → ''
        if provider.name == "minimax":
            return _FakeResp(content=_CLEAN)
        return _FakeResp(content=_CLEAN)

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    out = narrate_tinh_duyen(_PERSON, _TD)

    assert out == _CLEAN
    # deepseek thử trước (rớt), minimax thắng. gemini KHÔNG được gọi.
    assert calls[0] == "deepseek"
    assert "minimax" in calls
    assert "gemini" not in calls


def test_first_clean_provider_wins_no_further_calls(monkeypatch):
    """provider1 (deepseek) trả sạch ngay → DÙNG; minimax/gemini KHÔNG bị gọi."""
    calls = []

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        return _FakeResp(content=_CLEAN)

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    out = narrate_tinh_duyen(_PERSON, _TD)

    assert out == _CLEAN
    assert calls == ["deepseek"]  # thắng ngay, không thử tiếp


def test_all_providers_fail_returns_empty(monkeypatch):
    """Tất cả provider trả rỗng/mock → hết chuỗi → '' (UI fallback bản cấu trúc)."""
    calls = []

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        return _FakeResp(content="")  # rỗng → fail

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    out = narrate_tinh_duyen(_PERSON, _TD)

    assert out == ""
    # Cả chuỗi đều được thử (không cái nào thắng) — theo đúng thứ tự _NARRATE_PROVIDER_CHAIN
    # (BUG6: chuỗi dài hơn để 1 provider chết không làm rỗng lời thầy).
    assert calls == list(_NARRATE_PROVIDER_CHAIN)


def test_unconfigured_and_unhealthy_providers_skipped(monkeypatch):
    """deepseek chưa cấu hình + minimax unhealthy → bỏ qua, chỉ gemini được thử."""
    calls = []

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        return _FakeResp(content=_CLEAN)

    reg = _FakeRegistry(
        configured={"deepseek": False, "minimax": True, "gemini": True},
        unhealthy={"minimax"},
    )
    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=reg)
    out = narrate_tinh_duyen(_PERSON, _TD)

    assert out == _CLEAN
    assert calls == ["gemini"]  # deepseek (chưa config) + minimax (unhealthy) bị skip


def test_violation_uncurable_falls_through_to_next(monkeypatch):
    """provider1 vi phạm paradigm cả 2 pass → fail; provider2 sạch → DÙNG."""
    calls = []
    PREDICT = "Năm 2030 em chắc chắn sẽ khắc chồng và ly hôn."  # giọng tiên tri → dính

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        if provider.name == "deepseek":
            return _FakeResp(content=PREDICT)  # cả pass-1 + pass-2 đều dính
        return _FakeResp(content=_CLEAN)

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    out = narrate_tinh_duyen(_PERSON, _TD)

    assert out == _CLEAN
    # deepseek gọi 2 lần (pass-1 + pass-2 regenerate), vẫn dính → minimax thắng.
    assert calls.count("deepseek") == 2
    assert "minimax" in calls


# ── BUG5: cắt sạch ở ranh giới câu hoàn chỉnh ────────────────────────────────
def test_trim_to_last_sentence_cuts_dangling_fragment():
    """Lời thầy bị cụt giữa câu ('…sẽ tìm n') → lùi về câu hoàn chỉnh cuối."""
    from engine.cross_paradigm.narrate import _trim_to_last_sentence
    cut = ("Em ơi, cấu trúc của em vận hành tốt nhất khi em chủ động. "
           "Đây là điều cần ý thức, nếu không sẽ tìm n")
    out = _trim_to_last_sentence(cut)
    assert out.endswith("chủ động.")
    assert "sẽ tìm n" not in out


def test_trim_to_last_sentence_keeps_complete_text():
    """Text đã kết câu sạch → giữ NGUYÊN (không cắt nhầm)."""
    from engine.cross_paradigm.narrate import _trim_to_last_sentence
    full = "Câu một hoàn chỉnh. Câu hai cũng hoàn chỉnh!"
    assert _trim_to_last_sentence(full) == full


def test_trim_to_last_sentence_single_uncut_kept():
    """Cả bài là 1 câu cụt (không có ranh giới câu) → giữ nguyên, thà có hơn mất."""
    from engine.cross_paradigm.narrate import _trim_to_last_sentence
    one = "Một câu duy nhất bị cụt giữa chừng vì hết token nên"
    assert _trim_to_last_sentence(one) == one


def test_narrate_trims_cutoff_output(monkeypatch):
    """Integration BUG5: provider trả text cụt → narrate cắt sạch ở câu cuối."""
    cut = ("Cấu trúc của em vận hành tốt nhất khi em chủ động chăm sóc quan hệ. "
           "Đây là một tính cần ý thức, không phải định mệnh. "
           "Còn một điều nữa em nên nhớ, nếu không thì sẽ tìm n")

    def fake_run_agent(*, provider, model, **kw):
        return _FakeResp(content=cut)

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    out = narrate_tinh_duyen(_PERSON, _TD)
    assert "sẽ tìm n" not in out               # đuôi cụt bị bỏ
    assert out.endswith("không phải định mệnh.")  # cắt tại câu hoàn chỉnh cuối
    assert out.rstrip()[-1] in ".!?…。！？"


# ── BUG7: timeout mỗi lượt → provider treo bị bỏ, nhảy kế, không treo tổng ────
def test_hung_provider_times_out_and_next_wins(monkeypatch):
    """Provider treo (vượt timeout) bị BỎ → provider kế thắng; tổng KHÔNG treo."""
    import time as _t
    monkeypatch.setattr(narrate_mod, "_NARRATE_CALL_TIMEOUT_S", 0.5)
    calls = []

    def fake_run_agent(*, provider, model, **kw):
        calls.append(provider.name)
        if provider.name == "deepseek":
            _t.sleep(5)  # treo > timeout → bị bỏ
            return _FakeResp(content="never")
        return _FakeResp(content=_CLEAN)

    _patch(monkeypatch, run_agent_fn=fake_run_agent, registry=_FakeRegistry())
    t0 = _t.time()
    out = narrate_tinh_duyen(_PERSON, _TD)
    elapsed = _t.time() - t0

    assert out == _CLEAN
    assert calls[0] == "deepseek"          # đã thử (và treo)
    assert "minimax" in calls              # nhảy sang provider kế
    assert elapsed < 4.0                   # KHÔNG chờ trọn 5s của deepseek
