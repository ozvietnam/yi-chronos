"""TDD: engine.natal_universe.build_natal — gộp bầu trời THẬT + địa bàn KÝ HIỆU.

Kiểm bằng lá số founder (1988-06-05 23:30 +07, Hà Nội):
- bầu trời thật: Mặt Trời ~75° Song Tử (gemini), Asc Xử Nữ (virgo), 10 thiên thể.
- địa bàn ký hiệu: Mệnh tại Tỵ, năm Mậu Thìn, giờ Tý (khớp Bát Tự đã biết).
"""
from datetime import datetime, timedelta, timezone

from engine.natal_universe import build_natal

VN = timezone(timedelta(hours=7))
FOUNDER = datetime(1988, 6, 5, 23, 30, tzinfo=VN)


def test_real_sky_from_ephemeris():
    n = build_natal(FOUNDER, lat=21.03, lon=105.85)
    bodies = {b["name"]: b for b in n["sky"]["bodies"]}
    assert len(bodies) == 10
    assert 74.0 < bodies["sun"]["ecliptic_longitude"] < 77.0  # ~75.2
    assert bodies["sun"]["sign"] == "gemini"
    assert n["sky"]["ascendant"]["sign"] == "virgo"
    assert n["sky"]["sun_longitude"] == bodies["sun"]["ecliptic_longitude"]
    # Thủy + Kim nghịch hành lúc Anh sinh
    assert bodies["mercury"]["is_retrograde"] is True
    assert bodies["venus"]["is_retrograde"] is True


def test_symbolic_dia_ban():
    n = build_natal(FOUNDER, lat=21.03, lon=105.85)
    d = n["dia_ban"]
    assert d["menh_chi"] == "Tỵ"
    assert d["year_can_chi"] == "Mậu Thìn"
    assert d["hour_chi"] == "Tý"
    assert d["lunar_month"] == 4
    assert len(d["cung"]) == 12
    menh = [c for c in d["cung"] if c["is_menh"]]
    assert len(menh) == 1 and menh[0]["chi"] == "Tỵ"
    # mỗi cung có toạ độ hoàng đạo (neo tiết khí) + ngũ hành
    ty = next(c for c in d["cung"] if c["chi"] == "Tý")
    assert ty["lon_center"] == 270.0 and ty["hanh"] == "thuy"


def test_chinh_tinh_an_sao_computable():
    """14 chính tinh đặt TẤT ĐỊNH từ thời điểm sinh + mỗi sao mang ngũ hành."""
    n = build_natal(FOUNDER, lat=21.03, lon=105.85)
    d = n["dia_ban"]
    assert d["cuc"] == 5  # Thổ ngũ cục
    assert d["tu_vi_chi"] == "Mão"
    # đủ 14 chính tinh trải trên 12 cung
    total = sum(len(c["chinh_tinh"]) for c in d["cung"])
    assert total == 14
    # Mệnh (Tỵ) = Thiên Tướng, ngũ hành thủy (khớp lá số thật founder 91/91)
    ty = next(c for c in d["cung"] if c["chi"] == "Tỵ")
    assert [s["name"] for s in ty["chinh_tinh"]] == ["Thiên Tướng"]
    assert ty["chinh_tinh"][0]["ngu_hanh"] == "thủy"
    # Mão = Tử Vi (thổ) + Tham Lang (đồng cung)
    mao = next(c for c in d["cung"] if c["chi"] == "Mão")
    assert {s["name"] for s in mao["chinh_tinh"]} == {"Tử Vi", "Tham Lang"}
    tuvi = next(s for s in mao["chinh_tinh"] if s["name"] == "Tử Vi")
    assert tuvi["ngu_hanh"] == "thổ"


def test_tu_hoa_deterministic_by_can():
    """Tứ Hóa = hàm tất định của CAN năm (Mậu → Lộc:Tham Lang, Quyền:Thái Âm, Kỵ:Thiên Cơ)."""
    n = build_natal(FOUNDER, lat=21.03, lon=105.85)
    th = n["dia_ban"]["tu_hoa"]
    assert th["Lộc"] == "Tham Lang"
    assert th["Quyền"] == "Thái Âm"
    assert th["Kỵ"] == "Thiên Cơ"
    # Tham Lang (đồng cung Mão) mang Hóa Lộc; chính tinh không hóa → hoa=None
    mao = next(c for c in n["dia_ban"]["cung"] if c["chi"] == "Mão")
    assert next(s for s in mao["chinh_tinh"] if s["name"] == "Tham Lang")["hoa"] == "Lộc"
    ty = next(c for c in n["dia_ban"]["cung"] if c["chi"] == "Tỵ")
    assert ty["chinh_tinh"][0]["hoa"] is None  # Thiên Tướng (Mệnh) không hóa


def test_do_sang_by_position():
    """Độ sáng = HÀM của vị trí (đắc/hãm địa)."""
    n = build_natal(FOUNDER, lat=21.03, lon=105.85)
    ty = next(c for c in n["dia_ban"]["cung"] if c["chi"] == "Tỵ")
    assert ty["chinh_tinh"][0]["do_sang"] == "đắc"  # Thiên Tướng đắc tại Tỵ (Mệnh founder)
    tu = next(c for c in n["dia_ban"]["cung"] if c["chi"] == "Tý")
    td = next(s for s in tu["chinh_tinh"] if s["name"] == "Thái Dương")
    assert td["do_sang"] == "hãm"  # Thái Dương lạc tại Tý


def test_requires_tzinfo():
    import pytest
    with pytest.raises(ValueError):
        build_natal(datetime(1988, 6, 5, 23, 30), lat=21.0, lon=105.0)
