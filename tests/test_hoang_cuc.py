"""Tests engine Hoàng Cực — mốc quy chiếu từ sách phải khớp tuyệt đối.

Neo lại 2026: 304 CN (Giáp Tý, Lưu Uyên xưng Hán) = thế 2245, vận 188, hội Ngọ 7.
Nguồn: tự tự bộ trọn Thượng-Hạ, dẫn 何氏皇极经世解知要 以运经世 (PDF p16).
"""
import pytest

from engine.hoang_cuc.constants import NAM_MOI_NGUYEN, NGUYEN_START_ASTRO, can_chi_year
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year, timeline


def test_anchor_304_khop_sach():
    """Mốc neo: 304 CN Giáp Tý = hội Ngọ 7, vận 188, thế 2245, năm 1."""
    loc = locate_year(304)
    assert loc["can_chi"] == "Giáp Tý"
    assert loc["hoi"]["so"] == 7 and loc["hoi"]["chi"] == "Ngọ"
    assert loc["van"]["so_toan_nguyen"] == 188
    assert loc["the"]["so_toan_nguyen"] == 2245
    assert loc["the"]["nam_trong_the"] == 1


def test_nghieu_giap_thin_cuoi_hoi_ti():
    """tr.185: 'trước Ngọ hội, ngôi Nghiêu Thuấn' → Nghiêu (2357 TCN) ở hội Tỵ.
    Can chi phải là Giáp Thìn ('Nghiêu Giáp Thìn')."""
    loc = locate_year(-2356)  # 2357 TCN astronomical
    assert loc["hoi"]["chi"] == "Tỵ"
    assert loc["can_chi"] == "Giáp Thìn"


def test_ha_vu_dau_hoi_ngo():
    """tr.185: '午会由禹至今' → Hạ Vũ (~2071 TCN) ở đầu hội Ngọ (vận 181)."""
    loc = locate_year(-2070)  # 2071 TCN
    assert loc["hoi"]["chi"] == "Ngọ"
    assert loc["van"]["so_toan_nguyen"] == 181  # vận đầu tiên của hội Ngọ


def test_2026_binh_ngo_hoi_ngo():
    loc = locate_year(2026)
    assert loc["can_chi"] == "Bính Ngọ"
    assert loc["hoi"]["chi"] == "Ngọ"
    assert loc["van"]["so_toan_nguyen"] == 192
    assert loc["the"]["so_toan_nguyen"] == 2302


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
