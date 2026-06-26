"""Test schema v3 (8 lớp) + engine get_star_v3 — M1-A1.

- Dataset Tử Vi có đủ 9 field v3, ngu_uan dict 5 uẩn GIỮ NGUYÊN (không thêm Xúc).
- get_star_v3 trả đủ 8 lớp.
- Lớp 4 (khí vượng/suy) CHỌN ĐỘNG nhánh đắc/hãm theo mieu_ham_level.
- Fallback None khi sao không có / web cũ không vỡ.
"""
from __future__ import annotations

from engine.tu_vi import ngu_uan


def test_dataset_tuvi_co_du_field_v3():
    rec = ngu_uan.get_star_profile("Tử Vi")
    assert rec is not None
    for f in ("am_duong_ngu_hanh", "goc_tham", "khi_vuong_suy",
              "theo_doi_nguoi", "khe_tinh_thuc", "duong_ra",
              "vi_du_song", "can_cu", "ngu_uan_v3"):
        assert rec.get(f), f"thiếu field v3: {f}"


def test_ngu_uan_dict_5_uan_giu_nguyen_khong_them_xuc():
    rec = ngu_uan.get_star_profile("Tử Vi")
    nu = rec["ngu_uan"]
    assert isinstance(nu, dict), "ngu_uan phải GIỮ dạng dict cũ (engine _uan_of)"
    assert set(nu.keys()) == {"sac", "tho", "tuong", "hanh", "thuc"}
    assert "xuc" not in nu


def test_get_star_v3_tra_du_8_lop():
    v3 = ngu_uan.get_star_v3("Tử Vi")
    assert v3 is not None
    assert v3["_has_v3"] is True
    assert v3["l1_am_duong_ngu_hanh"]
    assert v3["l2_goc_tham"]
    assert isinstance(v3["l3_ngu_uan"], list) and len(v3["l3_ngu_uan"]) == 5
    assert v3["l4_khi_vuong_suy"]
    assert set(v3["l5_theo_doi_nguoi"].keys()) == {
        "nho", "thieu_nien", "trung_nien", "ve_gia"}
    assert v3["l6_khe_tinh_thuc"]
    assert v3["l6_duong_ra"]
    assert v3["l7_vi_du_song"]
    assert v3["l8_can_cu"]


def test_lop4_chon_dong_nhanh_dac_dia():
    for level in ("miếu", "vượng", "đắc"):
        v3 = ngu_uan.get_star_v3("Tử Vi", mieu_ham_level=level)
        k = v3["l4_khi_vuong_suy"]
        assert k["active"] == "dac_dia", level
        assert k["active_text"] == k["dac_dia"]


def test_lop4_chon_dong_nhanh_ham_dia():
    for level in ("lạc", "hãm"):
        v3 = ngu_uan.get_star_v3("Tử Vi", mieu_ham_level=level)
        k = v3["l4_khi_vuong_suy"]
        assert k["active"] == "ham_dia", level
        assert k["active_text"] == k["ham_dia"]


def test_lop4_binh_va_none_khong_ep_nhanh():
    for level in ("bình", None, ""):
        v3 = ngu_uan.get_star_v3("Tử Vi", mieu_ham_level=level)
        k = v3["l4_khi_vuong_suy"]
        assert k["active"] is None
        assert k["active_text"] is None
        # cả hai nhánh vẫn còn để web hiển thị
        assert k["dac_dia"] and k["ham_dia"]


def test_fallback_sao_khong_co():
    assert ngu_uan.get_star_v3("Sao Không Tồn Tại XYZ") is None


def test_web_cu_khong_vo_get_star_profile_van_nguyen():
    # get_star_profile vẫn trả record nguyên (tom_gon, mieu_ham, ngu_uan dict)
    rec = ngu_uan.get_star_profile("Tử Vi")
    assert rec.get("tom_gon") is not None
    assert rec.get("mieu_ham")
    assert isinstance(rec.get("ngu_uan"), dict)
