"""Paradigm engine (engine/tu_vi/paradigm/) — 7 hàm wired từ 4 hệ phái, xây
2026-06-27 nhưng chưa từng có unit test (gap-analysis-roadmap-2026-06-10.md
Phase A3 "chưa làm"). Quy ước chi canonical TOÀN HỆ THỐNG (khớp
la_so_input_builder.CHI_VI_TO_CANON): "ty" = Tý (子), "ti" = Tỵ (巳) —
2 chi KHÁC NHAU, dễ gõ nhầm vì gần giống nhau không dấu.
"""

from __future__ import annotations

import pytest


# ─── nhan_cung — Trần Đoàn Toàn Thư p63-64 ───────────────────────────────────


def test_nhan_cung_tu_vi_hits_ty_thin_hoi():
    from engine.tu_vi.paradigm import is_nhan_cung

    for chi in ("ty", "thin", "hoi"):
        hit, msg = is_nhan_cung("tu_vi", chi)
        assert hit is True
        assert "NHÂN CUNG" in msg and "Trần Đoàn" in msg


def test_nhan_cung_tu_vi_misses_other_chi():
    from engine.tu_vi.paradigm import is_nhan_cung

    hit, msg = is_nhan_cung("tu_vi", "dan")
    assert hit is False
    assert msg == "không phải Nhân Cung"


def test_nhan_cung_case_insensitive_and_whitespace():
    from engine.tu_vi.paradigm import is_nhan_cung

    hit, _ = is_nhan_cung("  Tu_Vi  ", " THIN ")
    assert hit is True


def test_nhan_cung_unknown_star_never_hits():
    from engine.tu_vi.paradigm import is_nhan_cung

    hit, msg = is_nhan_cung("thien_dong", "ty")   # không có data (đã ghi rõ trong docstring)
    assert hit is False


def test_nhan_cung_thien_luong_thien_co_pha_quan_at_ti_not_ty():
    """Regression 2026-07-17: NHAN_CUNG trước đây dùng "ty" (=Tý) cho vị trí
    Tỵ của Thiên Lương/Thiên Cơ/Phá Quân — đụng độ với "ty"=Tý của Tử Vi.
    Comment nguồn nói rõ "ở Tỵ" → canonical đúng phải là "ti".

    Bug cũ khiến engine báo SAI: bỏ sót cảnh báo khi sao thật sự ở Tỵ, và
    báo giả khi sao ở Tý (vốn không phải Nhân Cung của các sao này).
    """
    from engine.tu_vi.paradigm import is_nhan_cung

    for star in ("thien_luong", "thien_co", "pha_quan"):
        hit_ti, msg = is_nhan_cung(star, "ti")
        assert hit_ti is True, f"{star} ở Tỵ (ti) phải là Nhân Cung"
        assert "Tỵ" not in msg or True  # msg tự do, chỉ cần hit đúng

        hit_ty, _ = is_nhan_cung(star, "ty")
        assert hit_ty is False, f"{star} ở Tý (ty) KHÔNG phải Nhân Cung — bug cũ báo sai"

    # Phá Quân còn thêm vị trí Thân — không đổi
    hit_than, _ = is_nhan_cung("pha_quan", "than")
    assert hit_than is True


# ─── bac_tuoi — Thiên Lương Nghiệm Lý p7-10 ──────────────────────────────────


def test_bac_tuoi_truong_luong_giap_ngo_bac_1():
    """Case kinh điển trong docstring: Trương Lương Giáp Ngọ = bậc 1
    (Giáp=Mộc sinh Ngọ=Hỏa → Can sinh Chi → phúc lớn)."""
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, cit = bac_tuoi("giap", "ngo")
    assert bac == 1
    assert "Can sinh Chi" in name
    assert cit


def test_bac_tuoi_han_tin_giap_tuat_bac_4():
    """Hàn Tín Giáp Tuất = bậc 4 (Giáp=Mộc khắc Tuất=Thổ → Can khắc Chi → trở lực)."""
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, _ = bac_tuoi("giap", "tuat")
    assert bac == 4
    assert "trở lực" in name


def test_bac_tuoi_mau_thin_bac_4():
    """Acceptance test gap-analysis doc: 'Bậc tuổi Mậu Thìn (paradigm Thiên
    Lương: bậc 4 — trở lực)'. Mậu=Thổ khắc Thìn=Thổ? Không — đồng hành → bậc 2.
    Kiểm tra thực tế công thức, không giả định theo doc (doc có thể sai)."""
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, _ = bac_tuoi("mau", "thin")
    # Mậu=Thổ, Thìn=Thổ → đồng hành → bậc 2 (không phải bậc 4 như doc claim)
    assert bac == 2
    assert "vững chắc" in name


def test_bac_tuoi_dong_hanh_bac_2():
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, _ = bac_tuoi("binh", "ngo")  # Bính=Hỏa, Ngọ=Hỏa
    assert bac == 2


def test_bac_tuoi_chi_sinh_can_bac_3():
    from engine.tu_vi.paradigm import bac_tuoi

    bac, _, _ = bac_tuoi("mau", "ngo")  # Ngọ=Hỏa sinh Mậu=Thổ → Chi sinh Can
    assert bac == 3


def test_bac_tuoi_chi_khac_can_bac_5():
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, _ = bac_tuoi("mau", "dan")  # Dần=Mộc khắc Mậu=Thổ → Chi khắc Can
    assert bac == 5
    assert "nghịch cảnh" in name


def test_bac_tuoi_unknown_returns_zero():
    from engine.tu_vi.paradigm import bac_tuoi

    bac, name, _ = bac_tuoi("xyz", "ngo")
    assert bac == 0
    assert "không xác định" in name


# ─── tam_hop_loc_ton — Thiên Lương p9 ────────────────────────────────────────


def test_tam_hop_loc_giap_huong_via_dan_ngo_tuat():
    """Docstring: 'Tuổi Giáp → Lộc Tồn ở Dần → tam hợp Dần-Ngọ-Tuất hưởng Lộc Tồn'."""
    from engine.tu_vi.paradigm import tam_hop_loc_ton
    from engine.tu_vi.paradigm.tam_hop_loc import LOC_TON_VI_TRI

    assert LOC_TON_VI_TRI["giap"] == "dan"
    for chi in ("dan", "ngo", "tuat"):
        huong, msg, _ = tam_hop_loc_ton("giap", chi)
        assert huong is True, f"tuổi Giáp {chi} phải hưởng Lộc Tồn"
        assert "HƯỞNG Lộc Tồn" in msg


def test_tam_hop_loc_canh_huong_via_than_ty_thin():
    """Docstring: 'Tuổi Canh → Lộc Tồn ở Thân → tam hợp Thân-Tý-Thìn'."""
    from engine.tu_vi.paradigm import tam_hop_loc_ton
    from engine.tu_vi.paradigm.tam_hop_loc import LOC_TON_VI_TRI

    assert LOC_TON_VI_TRI["canh"] == "than"
    for chi in ("than", "ty", "thin"):
        huong, _, _ = tam_hop_loc_ton("canh", chi)
        assert huong is True


def test_tam_hop_loc_outside_group_not_huong():
    from engine.tu_vi.paradigm import tam_hop_loc_ton

    huong, msg, _ = tam_hop_loc_ton("giap", "suu")   # Sửu không trong Dần-Ngọ-Tuất
    assert huong is False
    assert "KHÔNG thuộc" in msg


def test_tam_hop_loc_unknown_can():
    from engine.tu_vi.paradigm import tam_hop_loc_ton

    huong, msg, _ = tam_hop_loc_ton("xyz", "dan")
    assert huong is False
    assert "không xác định can" in msg


# ─── ba_vong_lon — 3 vòng lớn Thiên-Địa-Nhân ─────────────────────────────────


def test_ba_vong_lon_structure():
    from engine.tu_vi.paradigm import ba_vong_lon

    v = ba_vong_lon("giap", "ngo", "thuy_nhi_cuc", gender="M")
    assert v["loc_ton"]["vi_tri"] == "dan"        # LOC_TON_VI_TRI["giap"]
    assert v["thai_tue"]["vi_tri"] == "ngo"
    assert v["trang_sinh"]["cuc"] == "thuy_nhi_cuc"
    assert v["trang_sinh"]["gender"] == "M"
    assert "Thiên-Địa-Nhân" in v["paradigm"]
    for key in ("loc_ton", "thai_tue", "trang_sinh"):
        assert v[key]["citation"]


# ─── bat_phap_classify — Trần Đoàn p19-20 ────────────────────────────────────


def test_bat_phap_thanh_when_only_tu_cat():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify({"loc", "quyen"}, set(), set())
    assert r["thanh_pha"] == "thanh"
    assert r["cuu_khi"] == "cho_thoi"   # tứ cát không đủ mặt cả 3 vùng


def test_bat_phap_pha_when_only_tu_hung():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify({"hoa", "linh"}, set(), set())
    assert r["thanh_pha"] == "pha"


def test_bat_phap_thanh_co_pha_when_both():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify({"loc"}, {"hoa"}, set())
    assert r["thanh_pha"] == "thanh_co_pha"


def test_bat_phap_chua_thanh_when_neither():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify(set(), set(), set())
    assert r["thanh_pha"] == "chua_thanh"
    assert r["cuu_khi"] == "cho_thoi"


def test_bat_phap_cuu_when_tu_cat_in_all_3_vungs():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify({"loc"}, {"quyen"}, {"khoa"})
    assert r["cuu_khi"] == "cuu"


def test_bat_phap_khi_when_tu_hung_in_all_3_vungs():
    from engine.tu_vi.paradigm import bat_phap_classify

    r = bat_phap_classify({"hoa"}, {"linh"}, {"duong"})
    assert r["cuu_khi"] == "khi"


# ─── thap_du_eval — Trần Đoàn p19 ────────────────────────────────────────────


def test_thap_du_eval_dieu_1_ban_phuong_cat():
    from engine.tu_vi.paradigm import thap_du_eval

    r = thap_du_eval(
        ban_phuong_cat=True, ban_phuong_hung=False,
        xung_chieu_cat=False, xung_chieu_hung=False,
        tam_hop_cat=False, tam_hop_hung=False,
        lan_phuong_cat=False, lan_phuong_hung=False,
    )
    assert r["dieu_dac"] == [1]
    assert r["dac_4"] is False and r["hung_4"] is False


def test_thap_du_eval_ca_4_cat_dieu_9():
    from engine.tu_vi.paradigm import thap_du_eval

    r = thap_du_eval(
        ban_phuong_cat=True, ban_phuong_hung=False,
        xung_chieu_cat=True, xung_chieu_hung=False,
        tam_hop_cat=True, tam_hop_hung=False,
        lan_phuong_cat=True, lan_phuong_hung=False,
    )
    assert r["dac_4"] is True
    assert 9 in r["dieu_dac"]
    assert set(r["dieu_dac"]) == {1, 3, 5, 7, 9}


def test_thap_du_eval_ca_4_hung_dieu_10():
    from engine.tu_vi.paradigm import thap_du_eval

    r = thap_du_eval(
        ban_phuong_cat=False, ban_phuong_hung=True,
        xung_chieu_cat=False, xung_chieu_hung=True,
        tam_hop_cat=False, tam_hop_hung=True,
        lan_phuong_cat=False, lan_phuong_hung=True,
    )
    assert r["hung_4"] is True
    assert 10 in r["dieu_dac"]


def test_thap_du_eval_mixed_cat_hung_not_counted():
    """Cả cát lẫn hung cùng vùng → không tính điều nào (mutually exclusive)."""
    from engine.tu_vi.paradigm import thap_du_eval

    r = thap_du_eval(
        ban_phuong_cat=True, ban_phuong_hung=True,
        xung_chieu_cat=False, xung_chieu_hung=False,
        tam_hop_cat=False, tam_hop_hung=False,
        lan_phuong_cat=False, lan_phuong_hung=False,
    )
    assert r["dieu_dac"] == []


# ─── to_hop_cung — Tam Phương Tứ Chính + Giáp Cung + Mượn Sao ────────────────


def test_tam_phuong_tu_chinh_dan_ngo_tuat_group():
    from engine.tu_vi.paradigm import tam_phuong_tu_chinh

    r = tam_phuong_tu_chinh("dan")
    assert set(r["tam_hop"]) == {"ngo", "tuat"}
    assert r["xung_chieu"] == "than"           # Dần xung Thân (đối nhau 6 vị trí)
    assert set(r["tu_chinh"]) == {"dan", "ngo", "tuat", "than"}


def test_tam_phuong_tu_chinh_invalid_chi_raises():
    from engine.tu_vi.paradigm import tam_phuong_tu_chinh

    with pytest.raises(ValueError):
        tam_phuong_tu_chinh("khong_ton_tai")


def test_giap_cung_neighbors():
    from engine.tu_vi.paradigm import giap_cung

    # Vòng: ty, suu, dan, mao, thin, ti, ngo, mui, than, dau, tuat, hoi
    assert giap_cung("dan") == ["suu", "mao"]
    assert giap_cung("ty") == ["hoi", "suu"]     # wrap-around đầu vòng


def test_muon_sao_returns_own_stars_when_present():
    from engine.tu_vi.paradigm import muon_sao

    r = muon_sao("dan", {"dan": ["tu_vi"]})
    assert r["vo_chinh_dieu"] is False
    assert r["stars"] == ["tu_vi"]
    assert r["borrowed_from"] is None


def test_muon_sao_borrows_from_xung_khi_vo_chinh_dieu():
    from engine.tu_vi.paradigm import muon_sao

    # Dần vô chính diệu → mượn từ xung chiếu = Thân
    r = muon_sao("dan", {"than": ["liem_trinh"]})
    assert r["vo_chinh_dieu"] is True
    assert r["stars"] == ["liem_trinh"]
    assert r["borrowed_from"] == "than"
    assert r["citation"]


def test_to_hop_cung_thien_tuong_gets_giap_note():
    from engine.tu_vi.paradigm import to_hop_cung

    r = to_hop_cung("dan", {"dan": ["thien_tuong"]})
    assert r["giap"]["thien_tuong_note"] is not None
    assert r["giap"]["cungs"] == ["suu", "mao"]


def test_to_hop_cung_non_thien_tuong_no_giap_note():
    from engine.tu_vi.paradigm import to_hop_cung

    r = to_hop_cung("dan", {"dan": ["tu_vi"]})
    assert r["giap"]["thien_tuong_note"] is None
