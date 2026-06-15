"""Tests engine Hoàng Cực — mốc quy chiếu từ sách phải khớp tuyệt đối.

Neo lại 2026: 304 CN (Giáp Tý, Lưu Uyên xưng Hán) = thế 2245, vận 188, hội Ngọ 7.
Nguồn: tự tự bộ trọn Thượng-Hạ, dẫn 何氏皇极经世解知要 以运经世 (PDF p16).
"""
import pytest

from engine.hoang_cuc.constants import NAM_MOI_NGUYEN, NGUYEN_START_ASTRO, can_chi_year
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year, timeline
from engine.hoang_cuc.nam_que import (
    NAM_QUE_2020_2103,
    NAM_QUE_CHINH_VAN,
    nam_que,
)


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


# ── Năm-quẻ (值年卦) ──────────────────────────────────────────

def test_nam_que_kiem_cheo_chinh_van():
    """KIỂM CHÉO cốt lõi: chính văn 304-313 ≡ bảng hiện đại 2025-2034."""
    a = [NAM_QUE_CHINH_VAN[y] for y in range(304, 314)]
    b = [NAM_QUE_2020_2103[y] for y in range(2025, 2035)]
    assert a == b == ["革", "同人", "临", "损", "节", "中孚", "归妹", "睽", "兑", "履"]


def test_nam_que_long_theo_van_the():
    """Cùng Giáp Tý mà khác quẻ → không phải vòng can-chi cố định."""
    assert nam_que(304)["han"] == "革"      # Giáp Tý
    assert nam_que(2044)["han"] == "大过"    # Giáp Tý khác → khác quẻ


def test_nam_que_dung_60_que():
    """Bảng dùng đúng 60 quẻ (64 bỏ 4 thuần 乾坤坎离)."""
    assert len(set(NAM_QUE_2020_2103.values())) == 60
    assert not ({"乾", "坤", "坎", "离"} & set(NAM_QUE_2020_2103.values()))


def test_nam_que_trung_thuc_none():
    """Ngoài nguồn xác → None (không bịa). 2026 = Đồng Nhân."""
    assert nam_que(1988) is None      # quá khứ Anh, chưa có nguồn
    assert nam_que(1500) is None
    assert nam_que(2026)["viet"] == "Đồng Nhân"
    assert nam_que(2044)["suspect"] is True  # nghi lỗi bảng
