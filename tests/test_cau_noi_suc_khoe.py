"""Test CẦU NỐI sức khỏe hai mắt: Tử Vi (CÁI GÌ) × Bát Tự/Đông y (KHI NÀO).

Ghép hai hệ SẴN CÓ (không tự tính lại) + đối chiếu chéo tạng. Iron #9: dưỡng-phòng.
"""
from engine.dong_y import cau_noi_suc_khoe as bridge

# Founder: hai mắt đều chỉ Thận/Thủy (đồng thuận).
_R = bridge.cau_noi_suc_khoe(birth_datetime_local="1988-06-05T23:30", gender="nam", year=2026)


def test_mat_tu_vi_ra_tang_va_benh():
    tv = bridge.mat_tu_vi("1988-06-05T23:30", "nam")
    assert tv["available"]
    assert tv["hanh_tang"] == "Thủy"
    assert "thận" in tv["tang"]
    assert tv["benh_co_nguon"] and tv["benh_co_nguon"][0]["nguon"]   # bệnh CÓ NGUỒN


def test_hai_mat_dong_thuan_than():
    """Tử Vi (Tật Ách Thủy) và Bát Tự (thể trạng Thận nhược) cùng chỉ Thủy → tin cao."""
    dt = _R["dong_thuan_tang"]
    assert dt["khop_tang"] is True
    assert dt["tang_tu_vi"] == "Thủy" and dt["tang_bat_tu"] == "Thủy"
    assert "cao" in dt["do_tin"]


def test_cau_noi_ghep_cai_gi_va_khi_nao():
    """Cầu nối phải có cả CÁI GÌ (Tử Vi) và KHI NÀO (Bát Tự) + đối chiếu."""
    assert _R["status"] == "ok"
    joined = " ".join(_R["cau_noi"])
    assert "Tử Vi" in joined and "Bát Tự" in joined
    assert _R["hai_mat"]["tu_vi_CAI_GI"]["available"]
    assert _R["hai_mat"]["bat_tu_KHI_NAO"]["available"]


def test_disclaimer_iron9_khong_doan_tu():
    dis = _R["disclaimer"].lower()
    assert "dưỡng" in dis and "không đoán" in dis
    # không rò từ bói tử vong trong cầu nối
    assert "sẽ chết" not in " ".join(_R["cau_noi"]).lower()


def test_mat_bat_tu_nham_van_tra_mat_tu_vi():
    """Nếu mắt Bát Tự lỗi/nhắm, cầu nối vẫn trả mắt Tử Vi (không vỡ)."""
    # ngày hợp lệ nhưng ép year lạ vẫn phải ra status ok + mắt tu_vi
    r = bridge.cau_noi_suc_khoe(birth_datetime_local="1988-06-05T23:30", gender="nam", year=2030)
    assert r["status"] == "ok"
    assert r["hai_mat"]["tu_vi_CAI_GI"]["available"]
