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


def test_requires_tzinfo():
    import pytest
    with pytest.raises(ValueError):
        build_natal(datetime(1988, 6, 5, 23, 30), lat=21.0, lon=105.0)
