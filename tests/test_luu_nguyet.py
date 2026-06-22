"""TDD: engine.tu_vi.luu_nguyet — NHỊP THÁNG (lưu nguyệt) đa-năm.

La bàn chú-ý: qua nhiều năm, MỖI THÁNG âm lịch, Tứ Hóa của tháng rơi vào cung
chức nào của đương số. KHÔNG phải bói — chỉ là cung nào được cấu trúc rọi sáng.

Neo vào lá số founder (1988-06-05 23:30 +07, Hà Nội):
- Mệnh tại Tỵ; Thiên Đồng natal ở Tuất = Nô Bộc.
- 2026 (Bính), tháng 7 (can Bính) → Lộc = Thiên Đồng → Tuất → Nô Bộc (mốc vàng).
"""
from datetime import datetime, timedelta, timezone

import pytest

from engine.tu_vi.luu_nguyet import luu_nguyet_rhythm

VN = timezone(timedelta(hours=7))
FOUNDER = datetime(1988, 6, 5, 23, 30, tzinfo=VN)
LAT, LON = 21.03, 105.85


def _founder(year_start: int, year_end: int) -> dict:
    return luu_nguyet_rhythm(FOUNDER, LAT, LON, year_start, year_end)


def test_founder_menh_ty():
    """Lá số gốc của founder: Mệnh tại Tỵ."""
    out = _founder(2026, 2026)
    assert out["natal"]["menh_chi"] == "Tỵ"


def test_2026_thang7_loc_no_boc():
    """Mốc vàng: 2026 (Bính), tháng 7 (can Bính) → Lộc = Thiên Đồng @ Tuất = Nô Bộc."""
    out = _founder(2026, 2026)
    year = next(y for y in out["years"] if y["year"] == 2026)
    assert year["year_stem"] == "Bính"
    m7 = next(m for m in year["months"] if m["month"] == 7)
    loc = m7["hoa"]["Lộc"]
    assert loc["star"] == "Thiên Đồng"
    assert loc["branch"] == "Tuất"
    assert loc["palace"] == "Nô Bộc"


def test_cyclic_month11_equals_month1():
    """Can tháng lặp sau 10 → hoa tháng 11 == hoa tháng 1 (cùng năm)."""
    out = _founder(2026, 2026)
    year = out["years"][0]
    m1 = next(m for m in year["months"] if m["month"] == 1)
    m11 = next(m for m in year["months"] if m["month"] == 11)
    assert m1["hoa"] == m11["hoa"]


def test_multiyear_length():
    """year_start=2026, year_end=2030 → 5 năm, mỗi năm 12 tháng."""
    out = luu_nguyet_rhythm(FOUNDER, LAT, LON, 2026, 2030)
    assert len(out["years"]) == 5
    for y in out["years"]:
        assert len(y["months"]) == 12


def test_requires_tzinfo():
    """birth_local không có tzinfo → raise."""
    naive = datetime(1988, 6, 5, 23, 30)
    with pytest.raises(ValueError):
        luu_nguyet_rhythm(naive, LAT, LON, 2026, 2026)


def test_span_too_large_raises():
    """year_end - year_start > 30 → raise ValueError."""
    with pytest.raises(ValueError):
        luu_nguyet_rhythm(FOUNDER, LAT, LON, 2000, 2031)
