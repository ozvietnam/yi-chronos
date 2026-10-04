"""Test luận cung TẬT ÁCH – NÔ BỘC: bộ sao thời-điểm hư-hao (Thiên Thương / Thiên Sứ)
+ tạng phủ theo ngũ hành cung bệnh.

Rút từ 1 ca luận hồi cứu (2026-07-22): cổ thư đánh dấu "hạn" bằng THIÊN THƯƠNG (cố định
Nô Bộc) + THIÊN SỨ (cố định Tật Ách) — KHÔNG phải Thất Sát. Iron #9: cảnh báo để DƯỠNG,
chỉ "động" khi vận tới + hội sát; không bịa ở cung thường, không suy diễn tử vong.
"""
from engine.tu_vi import van_han as vh
from engine.tu_vi.from_birth import cast_la_so_from_birth

# Lá số ca mẫu: Nam, DL 1947-10-01, giờ Mùi (Nô Bộc @Mùi có Thiên Thương+Kình+Bạch Hổ;
# Tật Ách @Dậu, hành Kim, có Thiên Sứ nhưng KHÔNG sát cùng cung).
_LA_SO = cast_la_so_from_birth(birth_datetime_local="1947-10-01T13:00", gender="nam")


def test_thien_thuong_hoi_sat_bat_canh_bao():
    """Đại Vận 8 (Nô Bộc/Mùi) có Thiên Thương + hội Bạch Hổ/Kình Dương → có cảnh báo."""
    b = vh.dai_van_block(_LA_SO, 8)
    cb = b.get("thuong_su_canh_bao")
    assert cb is not None
    assert "Thiên Thương" in cb["sao_thoi_diem"]
    assert set(cb["hoi_sat"]) & {"Kình Dương", "Bạch Hổ"}
    assert "phá bại" in cb["rule"].lower()
    assert "tử vong" in cb["rule"].lower()   # có ranh giới Iron #9 trong chính rule
    assert cb["nguon"]


def test_tat_ach_ra_tang_ngu_hanh():
    """Cung Tật Ách làm cung vận → 'phần dẫn xuất' tạng phủ theo ngũ hành CHI."""
    # Dậu (index 9) = cung Tật Ách của lá số này, hành Kim.
    tb = vh._the_dung_block(_LA_SO, 9, "Lưu Niên")
    assert tb["cung_the"] == "Tật Ách"
    tnh = tb.get("tang_ngu_hanh")
    assert tnh and tnh["hanh"] == "Kim"
    assert "phổi" in tnh["tang"]


def test_thuong_su_khong_hoi_sat_thi_khong_bat():
    """Có Thiên Sứ (Tật Ách/Dậu) nhưng KHÔNG sát cùng cung → KHÔNG cảnh báo (không bịa)."""
    assert vh._thuong_su_canh_bao(_LA_SO, 9) is None   # Dậu: Thiên Sứ, không sát tinh


def test_cung_thuong_khong_bi_gan_canh_bao():
    """Cung không có Thiên Thương/Sứ (Mệnh @Dần) → không cảnh báo, không tạng ngũ hành."""
    mb = vh._the_dung_block(_LA_SO, 2, "Đại Vận")   # Dần = Mệnh
    assert mb.get("thuong_su_canh_bao") is None
    assert mb.get("tang_ngu_hanh") is None


def test_tang_theo_ngu_hanh_du_5_hanh():
    """Bảng tạng phủ phủ đủ 5 hành, không rỗng."""
    for chi, hanh in (("Dần", "Mộc"), ("Ngọ", "Hỏa"), ("Thân", "Kim"),
                      ("Tý", "Thủy"), ("Thìn", "Thổ")):
        idx = vh.BRANCHES_TVI.index(chi)
        t = vh._tat_ach_tang(idx)
        assert t["hanh"] == hanh and t["tang"]
