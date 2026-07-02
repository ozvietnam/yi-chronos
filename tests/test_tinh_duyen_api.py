"""Wire tình duyên: service.run_tinh_duyen (charge 30 xu + cache Iron #4) + narrate
(sage 'tu_vi' theo khẩu vị giao tiếp, provider mock) + import API OK.

Theo mẫu test_cross_paradigm_service.py: mock cache/save/ví → KHÔNG cần DB thật cho
nhánh quyết định tiền. Narrate dùng provider 'mock' (deterministic, không key thật).
"""
from __future__ import annotations

import json

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
def test_narrate_chan_mock_khong_ro_ra_user(monkeypatch):
    """Provider mock-fallback (thiếu key/lỗi tạm) KHÔNG được lộ '[MOCK…]' cho user trả phí.
    MỌI provider trong chuỗi trả mock-content → bị chặn → '' (UX fallback bản cấu trúc).

    Pha A: narrate đi qua CHUỖI fallback [deepseek, minimax, gemini] + import run_agent
    bên trong (from engine.ai.agents import run_agent) → patch tại NGUỒN. Mock-content ở
    mọi provider → guard mock-leak chặn từng cái → hết chuỗi → ''."""
    import engine.ai.agents as A
    from engine.cross_paradigm import narrate as N
    from engine.tinh_duyen.reading import read_tinh_duyen

    class _MockResp:
        content = "[MOCK] Mock response — please paste api key in Settings."
        provider = "mock"
        model = "mock-v1"

    monkeypatch.setattr(A, "run_agent", lambda **kw: _MockResp())

    td = read_tinh_duyen(birth_datetime_local=_BIRTH_NU, gender="nữ")
    profs = td["personality"]["profiles"]
    assert profs and profs[0].get("khau_vi_giao_tiep"), "lá test phải có khẩu vị giao tiếp"

    txt = N.narrate_tinh_duyen(_PERSON, td)
    assert txt == "", "narrate PHẢI chặn mock (không rò '[MOCK]' cho user) → trả ''"


def test_narrate_passthrough_text_sach(monkeypatch):
    """LLM trả text SẠCH (paradigm-safe) → narrate cho qua nguyên văn (qua guard)."""
    import engine.ai.agents as A
    from engine.cross_paradigm import narrate as N
    from engine.tinh_duyen.reading import read_tinh_duyen

    clean = ("Cấu trúc của em vận hành tốt nhất khi em chủ động chọn người tôn trọng "
             "sự độc lập của mình. Đây là khí mạnh để em tự quyết, không phải bản án.")

    class _Resp:
        content = clean
        provider = "stub"
        model = "stub-v1"

    # run_agent được import BÊN TRONG narrate (from engine.ai.agents import run_agent)
    # → patch tại NGUỒN engine.ai.agents.run_agent.
    monkeypatch.setattr(A, "run_agent", lambda **kw: _Resp())
    td = read_tinh_duyen(birth_datetime_local=_BIRTH_NU, gender="nữ")
    txt = N.narrate_tinh_duyen(_PERSON, td)
    # Text sạch giữ NGUYÊN VĂN phần đầu; narrate ĐƯỢC PHÉP nối disclaimer Iron #9
    # ("...không thay tu học hay y tế") — hành vi đúng đạo, test cũ viết trước disclaimer.
    assert txt.startswith(clean), "text LLM sạch phải được narrate giữ nguyên văn phần đầu"
    assert txt == clean or "tu học" in txt or "y tế" in txt, \
        "phần nối thêm (nếu có) phải là disclaimer Iron #9"


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
    """Lỗi bất kỳ (registry/provider/LLM) → narrate trả '' (không sập).

    Pha A: get_registry là điểm vào của chuỗi fallback → cho nó raise để mô phỏng lỗi
    hạ tầng. narrate phải nuốt exception + trả '' (caller fallback bản cấu trúc)."""
    from engine.cross_paradigm import narrate as N
    import engine.ai.registry as R

    def boom():
        raise RuntimeError("registry lỗi")

    monkeypatch.setattr(R, "get_registry", boom)
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


# ── 4) API-LEVEL: response THỰC chứa display['sections'] (khoá contract #3) ───
_BIRTH = "1990-08-20T14:00"
_PERSON_DB = {"birth_datetime_local": _BIRTH, "gender": "nữ",
              "timezone": "Asia/Ho_Chi_Minh"}


def test_endpoint_cross_paradigm_tra_display_sections(monkeypatch):
    """POST /api/cross-paradigm/tinh-duyen → resp['display']['sections'] non-rỗng,
    JSON thuần (không HTML), gender-aware (nữ → 'chồng')."""
    import re
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    import api.cross_paradigm as CP
    from api.service_auth import require_caller
    from engine.tinh_duyen.reading import read_tinh_duyen

    # Engine output thật (deterministic) — chỉ tránh đụng DB/ví.
    real = read_tinh_duyen(birth_datetime_local=_BIRTH, gender="nữ")
    monkeypatch.setattr(CP, "_person", lambda uid, key: dict(_PERSON_DB))
    monkeypatch.setattr(
        "engine.cross_paradigm.service.run_tinh_duyen",
        lambda uid, person: dict(real, charged_xu=30, cached=False),
    )

    app = FastAPI()
    app.include_router(CP.router)
    app.dependency_overrides[require_caller] = lambda: {
        "source": "session", "user_id": "1", "is_owner": False,
    }
    c = TestClient(app)
    r = c.post("/api/cross-paradigm/tinh-duyen", json={"person_key": "self"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert "display" in out, "endpoint phải gắn key 'display'"
    disp = out["display"]
    assert disp["sections"], "display['sections'] phải non-rỗng"
    assert disp["meta"]["phoi_ngau"] == "chồng"   # nữ mệnh → người chồng
    assert disp["sections"][0]["id"] == "cap_do"  # KILLER lên đầu
    # JSON thuần, không HTML.
    assert not re.findall(r"</?[a-zA-Z][^>]*>", json.dumps(disp, ensure_ascii=False))
    # ADDITIVE — giữ nguyên key engine cũ.
    assert "cung_phu_the_tuvi" in out and "stage" in out


def test_endpoint_sync_tinh_duyen_tra_display_sections(monkeypatch):
    """POST /api/sync/tinh-duyen (AppChat) → resp['display']['sections'] gender-aware
    (nam → 'vợ'), JSON thuần. Mock service-key + helper DB."""
    import re
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    import api.sync as SY
    from engine.tinh_duyen.reading import read_tinh_duyen

    real = read_tinh_duyen(birth_datetime_local=_BIRTH, gender="nam")
    monkeypatch.setattr(SY, "_require_service_key", lambda key: None)
    monkeypatch.setattr(SY, "_ensure_schema", lambda: None)

    class _Conn:
        pass

    import contextlib

    @contextlib.contextmanager
    def _scope(service=False):
        yield _Conn()

    monkeypatch.setattr(SY, "session_scope", _scope)
    monkeypatch.setattr(SY, "_user_id_for_uid", lambda conn, uid: 1)
    monkeypatch.setattr(
        SY, "_person_by_key",
        lambda conn, uid, key: {"birth_datetime_local": _BIRTH, "gender": "nam",
                                "timezone": "Asia/Ho_Chi_Minh"},
    )
    monkeypatch.setattr(
        "engine.cross_paradigm.service.run_tinh_duyen",
        lambda uid, person: dict(real, charged_xu=30, cached=False),
    )

    app = FastAPI()
    app.include_router(SY.router)
    c = TestClient(app)
    r = c.post("/api/sync/tinh-duyen",
               json={"firebase_uid": "u1", "person_key": "self"},
               headers={"X-API-Key": "x"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert "display" in out
    disp = out["display"]
    assert disp["sections"]
    assert disp["meta"]["phoi_ngau"] == "vợ"   # nam mệnh → người vợ
    assert "vợ" in disp["meta"]["title"]
    assert not re.findall(r"</?[a-zA-Z][^>]*>", json.dumps(disp, ensure_ascii=False))
