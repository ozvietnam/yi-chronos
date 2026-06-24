"""Wire tình duyên: service.run_tinh_duyen (charge 30 xu + cache Iron #4) + narrate
(sage 'tu_vi' theo khẩu vị giao tiếp, provider mock) + import API OK.

Theo mẫu test_cross_paradigm_service.py: mock cache/save/ví → KHÔNG cần DB thật cho
nhánh quyết định tiền. Narrate dùng provider 'mock' (deterministic, không key thật).
"""
from __future__ import annotations

import engine.cross_paradigm.service as S

# Lá có Mệnh chính tinh (Liêm Trinh + Thất Sát) → personality.profiles có khẩu vị giao tiếp.
_BIRTH_NU = "1990-08-20T14:00"
_PERSON = {"birth_datetime_local": _BIRTH_NU, "gender": "nữ",
           "timezone": "Asia/Ho_Chi_Minh"}


def _patch_store(monkeypatch, cached=None):
    saved: dict = {}
    monkeypatch.setattr(S, "_cached", lambda uid, m, sig, ttl=S.CACHE_TTL_SEC:
                        ((7, cached) if cached is not None else (None, None)))
    monkeypatch.setattr(S, "_save", lambda uid, m, sig, result: saved.setdefault("id", 99))
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


# ── 1) service.run_tinh_duyen ────────────────────────────────────────────────
def test_run_tinh_duyen_charge_30_xu(monkeypatch):
    saved = _patch_store(monkeypatch)
    calls = _patch_wallet(monkeypatch, ok=True, balance=70)
    out = S.run_tinh_duyen(1, _PERSON)
    assert out["charged_xu"] == 30 and out["gia_xu"] == 30
    assert out["cached"] is False
    assert out["method_id"] == "tinh_duyen_nu_menh_v1"
    # engine output thật phải có các block contract.
    assert "personality" in out and "stage" in out and "cung_phu_the_tuvi" in out
    assert calls["spend"] and calls["spend"][0][1] == 30
    # _charge_and_run prefixes 'cross_paradigm_' lên method (method đã là cross_paradigm_tinh_duyen).
    assert calls["spend"][0][2] == "cross_paradigm_cross_paradigm_tinh_duyen"
    assert saved.get("id") == 99


def test_run_tinh_duyen_cache_khong_tru_lai(monkeypatch):
    _patch_store(monkeypatch, cached={"method_id": "tinh_duyen_nu_menh_v1",
                                      "paradigm_ok": True})
    calls = _patch_wallet(monkeypatch, ok=True)
    out = S.run_tinh_duyen(1, _PERSON)
    assert out["cached"] is True and out["charged_xu"] == 0
    assert not calls["spend"], "cache hit KHÔNG được trừ xu lại"


def test_run_tinh_duyen_thieu_xu(monkeypatch):
    _patch_store(monkeypatch)
    calls = _patch_wallet(monkeypatch, ok=False)
    out = S.run_tinh_duyen(1, _PERSON)
    assert out["status"] == "insufficient_xu" and out["gia_xu"] == 30
    assert not calls["grant"]


def test_run_tinh_duyen_gioi_tinh_khac_co_note(monkeypatch):
    """Gender khác nữ → vẫn chạy nhưng gắn note 'tối ưu cho nữ mệnh'."""
    _patch_store(monkeypatch)
    _patch_wallet(monkeypatch, ok=True)
    person_nam = dict(_PERSON, gender="nam")
    out = S.run_tinh_duyen(1, person_nam)
    assert out.get("nu_menh_note"), "gender không phải nữ phải có note tối ưu nữ mệnh"
    assert "nữ mệnh" in out["nu_menh_note"].lower()


# ── 2) narrate (provider mock) ───────────────────────────────────────────────
def test_narrate_tinh_duyen_tra_text_provider_mock(monkeypatch):
    """Ép provider 'mock' → narrate trả text khác rỗng, hệ thống không sập."""
    from engine.ai.registry import get_registry
    from engine.cross_paradigm import narrate as N
    from engine.tinh_duyen.reading import read_tinh_duyen

    mock = get_registry().get("mock")
    # Ép _get_agent_provider → mock (deterministic, không phụ thuộc key thật trong env).
    import engine.ai.council as C
    monkeypatch.setattr(C, "_get_agent_provider",
                        lambda agent_id, prefer_reasoning=False: (mock, "mock-v1"))

    td = read_tinh_duyen(birth_datetime_local=_BIRTH_NU, gender="nữ")
    # Chốt tiền đề: lá này phải có khẩu vị giao tiếp để narrate có gì để bám.
    profs = td["personality"]["profiles"]
    assert profs and profs[0].get("khau_vi_giao_tiep"), "lá test phải có khẩu vị giao tiếp"

    txt = N.narrate_tinh_duyen(_PERSON, td)
    assert isinstance(txt, str) and txt.strip(), "narrate phải trả text khác rỗng"
    # mock agent gắn nhãn [MOCK • Agent …] → xác nhận đi qua run_agent.
    assert "MOCK" in txt or "Agent" in txt


def test_narrate_system_prompt_theo_khau_vi():
    """System-prompt phải nhúng khẩu vị (giọng/nên/tránh) + chặng tuổi (paradigm)."""
    from engine.cross_paradigm.narrate import _build_system_prompt
    from engine.tinh_duyen.reading import read_tinh_duyen

    td = read_tinh_duyen(birth_datetime_local=_BIRTH_NU, gender="nữ")
    sp = _build_system_prompt(_PERSON, td)
    assert "KHẨU VỊ GIAO TIẾP" in sp and "CHẶNG TUỔI" in sp
    # Giọng thật của sao (Liêm Trinh) phải xuất hiện trong prompt.
    giong0 = td["personality"]["profiles"][0]["khau_vi_giao_tiep"]["giong"]
    assert giong0[:15] in sp, "system-prompt phải nhúng giọng từ khẩu vị giao tiếp"
    # Tuổi của chặng phải có mặt (16t khác 35t).
    assert str(td["stage"]["tuoi"]) in sp
    # Hàng rào paradigm.
    assert "mệnh là" in sp.lower() and "ly hôn" in sp.lower()


def test_narrate_loi_llm_tra_chuoi_rong(monkeypatch):
    """Lỗi LLM → narrate trả '' (không sập)."""
    from engine.cross_paradigm import narrate as N
    import engine.ai.council as C

    def boom(agent_id, prefer_reasoning=False):
        raise RuntimeError("registry lỗi")

    monkeypatch.setattr(C, "_get_agent_provider", boom)
    txt = N.narrate_tinh_duyen(_PERSON, {"stage": {"tuoi": 30}, "personality": {}})
    assert txt == "", "lỗi LLM phải trả chuỗi rỗng, không raise"


# ── 3) import API OK + route đăng ký ─────────────────────────────────────────
def test_import_api_va_routes_dang_ky():
    from api.cross_paradigm import router as cp_router
    from api.sync import router as sync_router

    cp_paths = {r.path for r in cp_router.routes}
    assert "/api/cross-paradigm/tinh-duyen" in cp_paths
    assert "/api/cross-paradigm/tinh-duyen/narrate" in cp_paths

    sync_paths = {r.path for r in sync_router.routes}
    # sync router có prefix riêng; path tương đối là '/tinh-duyen'.
    assert any(p.endswith("/tinh-duyen") for p in sync_paths)
