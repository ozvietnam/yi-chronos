"""Phác hoạ chân dung BIỂU TƯỢNG người phối ngẫu — deterministic + paradigm-safe.

PARADIGM (Iron #4/#6/#8): hồ sơ grounded vào bảng #4 + 形性赋 (qua tuong_mao_phoi_ngau.json),
KHÔNG cát/hung, KHÔNG cá nhân hoá. Prompt mô tả 1 KIỂU người (a type), tiếng Anh. Vẽ ảnh
graceful khi không có key (không sập). Route đăng ký + disclaimer có mặt.
"""
from __future__ import annotations

import re

from engine.tu_vi.from_birth import cast_la_so_from_birth
from engine.bat_tu.cast import cast_bat_tu
from engine.tinh_duyen import phac_hoa_phoi_ngau as P

_BIRTH = "1990-08-20T14:00"
_TZ = "Asia/Ho_Chi_Minh"


def _chart(gender="nữ"):
    ls = cast_la_so_from_birth(birth_datetime_local=_BIRTH, timezone=_TZ, gender=gender)
    bt = cast_bat_tu(birth_datetime_local=_BIRTH, timezone=_TZ, gender=gender)
    return ls, bt


# ── 1) lập hồ sơ deterministic + grounded ────────────────────────────────────
def test_lap_ho_so_du_field_va_grounded():
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ", vung_mien="bắc", do_tuoi="30")
    # đủ field theo contract.
    for k in ("gioi_tinh_phoi_ngau", "khuon_mat", "chieu_cao", "dang_nguoi", "da",
              "mat", "mui", "toc", "nghe", "moi_truong", "phong_cach", "bieu_cam",
              "_nguon", "_disclaimer"):
        assert k in hs and hs[k], f"thiếu/ rỗng field {k}"
    # giới phối ngẫu NGƯỢC với user (nữ → nam).
    assert hs["gioi_tinh_phoi_ngau"] == "nam"
    # grounded: sao chủ Phu Thê có thật trong bảng #4.
    assert hs["sao_chu_phu_the"] in P.KL.get("tuong_mao_phoi_ngau")["chinh_tinh_phu_the"]
    # nguồn ghi rõ bảng #4 + 形性赋.
    assert "#4" in hs["_nguon"] and "形性赋" in hs["_nguon"]


def test_lap_ho_so_deterministic():
    """Cùng input → cùng hồ sơ (không random)."""
    ls, bt = _chart("nữ")
    a = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")
    b = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")
    assert a == b


def test_gioi_phoi_nguoc_khi_user_nam():
    ls, bt = _chart("nam")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nam")
    assert hs["gioi_tinh_phoi_ngau"] == "nữ"


def test_hanh_quan_sat_khac_nhat_chu():
    """官杀 = hành KHẮC nhật chủ (nhật chủ Hỏa → 官杀 Thủy)."""
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")
    dm = bt["ngu_hanh"]["day_master_assessment"]["day_master_element"]
    assert dm == "hỏa" and hs["hanh_quan_sat"] == "Thủy"


# ── 2) build prompt: tiếng Anh hợp lệ, mô tả TYPE ────────────────────────────
def test_build_prompt_tieng_anh_hop_le():
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ", vung_mien="bắc", do_tuoi="30")
    prompt = P.build_prompt_anh(hs, "bắc", None, "30")
    # tiếng Anh: có các từ khoá nền text-to-image.
    assert "Portrait of a" in prompt
    assert "Vietnamese" in prompt
    assert "photorealistic" in prompt
    assert "northern" in prompt.lower()
    # mô tả TYPE, KHÔNG cá nhân hoá thành "người sẽ cưới".
    assert "archetype" in prompt.lower()
    assert "not a specific real individual" in prompt.lower()
    assert "will marry" not in prompt.lower() and "your future" not in prompt.lower()
    # gender phối ngẫu (nam) phản ánh đúng.
    assert " man" in prompt


def test_build_prompt_khong_lan_tieng_viet_co_dau():
    """Prompt nên thuần Anh ở các nét chính (không lẫn dấu tiếng Việt ở từ khoá đã dịch)."""
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ", vung_mien="bắc", do_tuoi="30")
    prompt = P.build_prompt_anh(hs, "bắc", None, "30")
    # không còn cụm "mặt vuông"/"da hơi ngăm" thô (đã dịch sang Anh).
    assert "mặt" not in prompt and "da hơi" not in prompt


# ── 3) vẽ ảnh fallback an toàn (không key) ───────────────────────────────────
def test_ve_anh_fallback_khong_key(monkeypatch):
    """Không có key / backend lỗi → trả image_b64=None + note, KHÔNG raise."""
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")

    # ép backend lỗi (giả lập thiếu key).
    import engine.yi_publishing.image_redraw_gemini as G

    def boom(*a, **kw):
        raise RuntimeError("no key")

    monkeypatch.setattr(G, "generate_redraw_gemini", boom, raising=False)
    if hasattr(G, "generate_image_gemini"):
        monkeypatch.setattr(G, "generate_image_gemini", boom, raising=False)

    out = P.ve_anh_phoi_ngau(hs)
    assert out["image_b64"] is None
    assert out["note"] == "chưa tạo được ảnh"
    assert out["prompt"] and "Portrait of a" in out["prompt"]
    assert out["ho_so"] == hs
    assert out["_disclaimer"]


def test_ve_anh_thanh_cong_mock(monkeypatch, tmp_path):
    """Backend trả ảnh → ve_anh đọc file, trả image_b64 + image_path."""
    import base64
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")

    fake_png = tmp_path / "fake.png"
    fake_png.write_bytes(b"\x89PNG\r\n_fake_image_bytes_")

    import engine.yi_publishing.image_redraw_gemini as G

    def fake_gen(prompt, *args, output_path=None, **kw):
        return {"output_path": str(fake_png), "prompt": prompt}

    monkeypatch.setattr(G, "generate_redraw_gemini", fake_gen, raising=False)

    out = P.ve_anh_phoi_ngau(hs)
    assert out["image_path"] == str(fake_png)
    assert out["image_b64"] == base64.b64encode(fake_png.read_bytes()).decode("ascii")
    assert out["_disclaimer"]


# ── 4) disclaimer paradigm BẮT BUỘC ──────────────────────────────────────────
def test_disclaimer_paradigm_co_mat():
    ls, bt = _chart("nữ")
    hs = P.lap_ho_so_tuong_mao(ls, bt, gender="nữ")
    d = hs["_disclaimer"].lower()
    assert "biểu tượng" in d
    assert "không phải gương mặt" in d
    assert "tiên đoán" in d or "cát/hung" in d


# ── 5) route đăng ký ─────────────────────────────────────────────────────────
def test_route_phac_hoa_dang_ky():
    from api.cross_paradigm import router as cp_router
    paths = {r.path for r in cp_router.routes}
    assert "/api/cross-paradigm/tinh-duyen/phac-hoa" in paths


# ── 6) service charge 50 xu + cache (mock ví/store) ──────────────────────────
def test_service_phac_hoa_charge_50_xu(monkeypatch):
    import engine.cross_paradigm.service as S

    saved: dict = {}
    monkeypatch.setattr(S, "_cached", lambda uid, m, sig, ttl=S.CACHE_TTL_SEC: (None, None))
    monkeypatch.setattr(S, "_save", lambda uid, m, sig, result: saved.setdefault("id", 5))

    calls = {"spend": []}

    def spend(uid, amount, reason, ref=None):
        calls["spend"].append((uid, amount, reason))
        return {"ok": True, "balance": 100}

    monkeypatch.setattr(S.xu_wallet, "spend", spend)
    monkeypatch.setattr(S.xu_wallet, "grant", lambda *a, **k: 0)

    person = {"birth_datetime_local": _BIRTH, "gender": "nữ", "timezone": _TZ}
    out = S.run_phac_hoa_phoi_ngau(1, person, vung_mien="bắc", do_tuoi="30", gen_anh=False)
    assert out["charged_xu"] == 50 and out["gia_xu"] == 50
    assert out["method_id"] == "phac_hoa_phoi_ngau_v1"
    assert out["ho_so"]["gioi_tinh_phoi_ngau"] == "nam"
    assert out["disclaimer"]
    assert "Portrait of a" in out["prompt"]
    assert calls["spend"] and calls["spend"][0][1] == 50


def test_service_phac_hoa_cache_khong_tru_lai(monkeypatch):
    import engine.cross_paradigm.service as S

    monkeypatch.setattr(S, "_cached", lambda uid, m, sig, ttl=S.CACHE_TTL_SEC:
                        (9, {"method_id": "phac_hoa_phoi_ngau_v1", "paradigm_ok": True}))
    calls = {"spend": []}
    monkeypatch.setattr(S.xu_wallet, "spend",
                        lambda *a, **k: calls["spend"].append(a) or {"ok": True, "balance": 1})

    person = {"birth_datetime_local": _BIRTH, "gender": "nữ", "timezone": _TZ}
    out = S.run_phac_hoa_phoi_ngau(1, person, gen_anh=False)
    assert out["cached"] is True and out["charged_xu"] == 0
    assert not calls["spend"], "cache hit KHÔNG được trừ xu lại"
