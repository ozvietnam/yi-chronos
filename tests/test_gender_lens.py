"""Tests cho engine.tinh_duyen.gender_lens — phân biệt Nam-Nữ TRIỆT ĐỂ.

Nữ = flagship (canonical, giữ nguyên); Nam = mirror ĐÚNG cơ học (财/khắc thê).
"""
from __future__ import annotations

import pytest

from engine.tinh_duyen.gender_lens import (
    apply_gender,
    cau_hoi_gender,
    co_than_qua_tu,
    gioi_phoi_ngau,
    is_female,
    is_male,
    khac_phoi_ngau,
    norm_gender,
    phoi_ngau_label,
    phu_the_thap_than,
    term_map,
)


# ── Chuẩn hoá giới ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("g", ["nam", "Nam", "male", "M", "trai", "boy"])
def test_norm_male(g):
    assert norm_gender(g) == "nam"
    assert is_male(g) and not is_female(g)


@pytest.mark.parametrize("g", ["nu", "nữ", "female", "F", "gái", None, "", "xyz"])
def test_norm_female_default(g):
    assert norm_gender(g) == "nu"
    assert is_female(g) and not is_male(g)


# ── Sao phối ngẫu: 官杀 (nữ) vs 财 (nam) ─────────────────────────────────────
def test_phu_the_thap_than_nu():
    assert phu_the_thap_than("nu") == ["Chính Quan", "Thất Sát"]


def test_phu_the_thap_than_nam():
    assert phu_the_thap_than("nam") == ["Chính Tài", "Thiên Tài"]


def test_sao_phoi_ngau_khac_nhau():
    assert phu_the_thap_than("nu") != phu_the_thap_than("nam")


# ── Khắc phối ngẫu: Thương Quan (nữ) vs Tỷ Kiếp (nam) ───────────────────────
def test_khac_nu_thuong_quan():
    k = khac_phoi_ngau("nu")
    assert "Thương Quan" in k["ke_khac"]
    assert "Chính Quan" in k["bi_khac"]
    assert "Thương Quan" in k["ke_khac_list"]
    assert k["han"]["bi_khac"] == "官"
    assert any("Ấn" in c for c in k["che_hoa"])
    assert any("thông quan" in c for c in k["che_hoa"])


def test_khac_nam_ti_kiep():
    k = khac_phoi_ngau("nam")
    assert "Tỷ Kiếp" in k["ke_khac"]
    assert "Chính Tài" in k["bi_khac"]
    assert "Kiếp Tài" in k["ke_khac_list"]
    assert k["han"]["bi_khac"] == "财"
    assert any("Tỷ Kiếp" in c for c in k["che_hoa"])
    assert any("Quan Sát chế" in c for c in k["che_hoa"])


def test_khac_phoi_ngau_doi_xung():
    assert khac_phoi_ngau("nu")["ke_khac"] != khac_phoi_ngau("nam")["ke_khac"]
    assert khac_phoi_ngau("nu")["bi_khac"] != khac_phoi_ngau("nam")["bi_khac"]


# ── Cô đơn: Quả Tú (nữ) vs Cô Thần (nam) ────────────────────────────────────
def test_co_than_qua_tu():
    assert co_than_qua_tu("nu") == "Quả Tú"
    assert co_than_qua_tu("nam") == "Cô Thần"


# ── Term-map ────────────────────────────────────────────────────────────────
def test_term_map_nu_rong():
    assert term_map("nu") == {}


def test_term_map_nam_co_du_cap():
    tm = term_map("nam")
    assert tm["chồng"] == "vợ"
    assert tm["phu tinh"] == "thê tinh"
    assert tm["khắc chồng"] == "khắc vợ"
    assert tm["khắc phu"] == "khắc thê"
    assert tm["lấy chồng"] == "lấy vợ"
    assert tm["người chồng"] == "người vợ"
    assert tm["sao chồng"] == "sao vợ"
    assert tm["官杀"] == "财"


# ── apply_gender: nữ giữ nguyên, nam thay đúng, dài-trước-ngắn ───────────────
def test_apply_nu_giu_nguyen():
    s = "Sao chồng là 官杀, người chồng đoan chính, khắc chồng cần hoá giải."
    assert apply_gender(s, "nu") == s


def test_apply_nam_thay_dung():
    s = "Sao chồng là 官杀, lấy chồng muộn, khắc phu cần hoá giải."
    out = apply_gender(s, "nam")
    assert "sao vợ" in out.lower()
    assert "财" in out
    assert "lấy vợ" in out
    assert "khắc thê" in out
    assert "chồng" not in out
    assert "官杀" not in out


def test_apply_nam_dai_truoc_ngan():
    # 'người chồng' phải thành 'người vợ', KHÔNG phải 'người vợ' bị hỏng
    out = apply_gender("người chồng của em", "nam")
    assert out == "người vợ của em"


def test_apply_nam_giu_hoa_thuong():
    assert apply_gender("Chồng", "nam") == "Vợ"
    assert apply_gender("CHỒNG", "nam") == "VỢ"
    assert apply_gender("chồng", "nam") == "vợ"


def test_apply_none():
    assert apply_gender(None, "nam") == ""
    assert apply_gender(None, "nu") == ""


# ── Nhãn + giới phối ngẫu ───────────────────────────────────────────────────
def test_phoi_ngau_label():
    assert phoi_ngau_label("nu") == "chồng"
    assert phoi_ngau_label("nam") == "vợ"


def test_gioi_phoi_ngau_nguoc():
    # phối ngẫu = giới NGƯỢC user (dùng cho phác hoạ chân dung)
    assert gioi_phoi_ngau("nu") == "nam"
    assert gioi_phoi_ngau("nam") == "nu"


# ── cau_hoi_gender ──────────────────────────────────────────────────────────
def test_cau_hoi_nu_giu():
    assert cau_hoi_gender("chồng em thế nào?", "nu") == "chồng em thế nào?"


def test_cau_hoi_nam_doi():
    assert cau_hoi_gender("chồng em thế nào?", "nam") == "vợ em thế nào?"
    assert cau_hoi_gender("khi nào lấy chồng?", "nam") == "khi nào lấy vợ?"


# ── ANTI: KHÔNG BAO GIỜ phán 'tái hôn/khắc chồng' cho nam ───────────────────
def test_nam_khong_co_khac_chong():
    """Mọi văn bản nữ về 'khắc chồng' khi mirror sang nam phải thành 'khắc vợ'."""
    nu_text = "Cấu trúc Thương Quan khắc chồng, dễ tái hôn nếu khắc phu nặng."
    out = apply_gender(nu_text, "nam")
    assert "khắc chồng" not in out
    assert "khắc phu" not in out
    assert "khắc vợ" in out
    assert "khắc thê" in out
