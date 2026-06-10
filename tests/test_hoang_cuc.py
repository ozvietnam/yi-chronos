"""Tests engine Hoàng Cực — mốc quy chiếu từ sách phải khớp tuyệt đối."""
import pytest

from engine.hoang_cuc.constants import NAM_MOI_NGUYEN, NGUYEN_START_ASTRO, can_chi_year
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year, timeline


def test_anchor_1980_khop_sach():
    """tr.149 & tr.185: 1980 Canh Thân = hội Ngọ 7, vận 186, thế 2227, năm 16."""
    loc = locate_year(1980)
    assert loc["can_chi"] == "Canh Thân"
    assert loc["hoi"]["so"] == 7 and loc["hoi"]["chi"] == "Ngọ"
    assert loc["van"]["so_toan_nguyen"] == 186
    assert loc["the"]["so_toan_nguyen"] == 2227
    assert loc["the"]["nam_trong_the"] == 16


def test_nghieu_giap_thin_cuoi_hoi_ti():
    """tr.149: Nghiêu Giáp Thìn (2357 TCN = astro -2356) thuộc hội Tỵ."""
    loc = locate_year(-2356)
    assert loc["hoi"]["chi"] == "Tỵ"
    assert loc["can_chi"] == "Giáp Thìn"


def test_2026_binh_ngo_hoi_ngo():
    loc = locate_year(2026)
    assert loc["can_chi"] == "Bính Ngọ"
    assert loc["hoi"]["chi"] == "Ngọ"
    assert loc["van"]["so_toan_nguyen"] == 186
    assert loc["the"]["so_toan_nguyen"] == 2229


def test_cau_truc_so_hoc():
    """Quan hệ tầng: thế→vận→hội nhất quán trên năm bất kỳ."""
    loc = locate_year(1)
    assert loc["nguyen"]["nam_trong_nguyen"] == 1 - NGUYEN_START_ASTRO + 1
    the_g = loc["the"]["so_toan_nguyen"]
    van_g = loc["van"]["so_toan_nguyen"]
    assert (the_g - 1) // 12 + 1 == van_g
    assert (van_g - 1) // 30 + 1 == loc["hoi"]["so"]


def test_ngoai_nguyen_raise():
    with pytest.raises(ValueError):
        locate_year(NGUYEN_START_ASTRO - 1)
    with pytest.raises(ValueError):
        locate_year(NGUYEN_START_ASTRO + NAM_MOI_NGUYEN)


def test_can_chi():
    assert can_chi_year(1984) == "Giáp Tý"
    assert can_chi_year(1988) == "Mậu Thìn"  # năm sinh founder


def test_timeline_marks():
    marks = timeline(1900, 2100)
    assert 6 <= len(marks) <= 9
    assert all(m["hoi_chi"] == "Ngọ" for m in marks)
