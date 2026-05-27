"""Solar ↔ Lunar conversion + stem/branch helpers.

Dùng sxtwl (寿星天文历) — chính xác theo lịch Trung Hoa.

Trong Mai Hoa Lưu Vận:
- Birth: user nhập ngày DƯƠNG, engine convert → lunar + chi năm/giờ
- Now: server tự lấy ngày dương → convert → lunar + chi
- UI hiển thị SONG SONG cả 2 lịch
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import sxtwl

# Thiên Can (0-9)
TG_NAMES = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
# Địa Chi (0-11)
DZ_NAMES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


@dataclass
class SolarDateTime:
    """Ngày-giờ dương lịch."""
    year: int
    month: int
    day: int
    hour: int = 0      # 0-23
    minute: int = 0


@dataclass
class LunarDateTime:
    """Ngày-giờ âm lịch + can chi."""
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool
    # Can chi
    year_can: str          # "Mậu"
    year_chi: str          # "Thìn"
    year_can_chi: str      # "Mậu Thìn"
    hour_chi: str          # "Tý" — chi giờ
    # Tham chiếu nguồn
    solar_year: int
    solar_month: int
    solar_day: int
    solar_hour: int
    solar_minute: int


def solar_to_lunar(s: SolarDateTime) -> LunarDateTime:
    """Convert ngày-giờ dương → âm lịch + can chi.

    Quy ước giờ Tý SỚM (23:00-01:00) = GIỜ TÝ của NGÀY ÂM TIẾP THEO (Mai Hoa Khang Tiết).
    Vd: dương 1988-06-05 23:30 → giờ Tý của ngày âm 1988-06-06 → lunar tháng 4 ngày 22.

    sxtwl tính lunar theo ngày dương đó (chưa qua 23:00 thì cùng ngày).
    Nếu hour >= 23 → coi như ngày dương kế tiếp.
    """
    # Sang ngày dương kế tiếp nếu giờ ≥ 23 (đã vào giờ Tý sớm = ngày mới)
    import datetime
    dt = datetime.datetime(s.year, s.month, s.day, s.hour, s.minute)
    if s.hour >= 23:
        dt = dt + datetime.timedelta(days=1)

    day_obj = sxtwl.fromSolar(dt.year, dt.month, dt.day)
    year_gz = day_obj.getYearGZ()
    # Chi giờ: 23-1 → Tý(0), 1-3 → Sửu(1), ..., 21-23 → Hợi(11)
    hour_chi_idx = ((s.hour + 1) // 2) % 12

    return LunarDateTime(
        lunar_year=day_obj.getLunarYear(),
        lunar_month=day_obj.getLunarMonth(),
        lunar_day=day_obj.getLunarDay(),
        is_leap_month=day_obj.isLunarLeap(),
        year_can=TG_NAMES[year_gz.tg],
        year_chi=DZ_NAMES[year_gz.dz],
        year_can_chi=f"{TG_NAMES[year_gz.tg]} {DZ_NAMES[year_gz.dz]}",
        hour_chi=DZ_NAMES[hour_chi_idx],
        solar_year=s.year,
        solar_month=s.month,
        solar_day=s.day,
        solar_hour=s.hour,
        solar_minute=s.minute,
    )


def parse_solar_string(solar_str: str) -> SolarDateTime:
    """Parse 'YYYY-MM-DD HH:MM' → SolarDateTime."""
    if "T" in solar_str:
        date_part, time_part = solar_str.split("T", 1)
    elif " " in solar_str:
        date_part, time_part = solar_str.split(" ", 1)
    else:
        date_part = solar_str
        time_part = "00:00"
    y, m, d = map(int, date_part.split("-"))
    if ":" in time_part:
        h, mi = map(int, time_part.split(":")[:2])
    else:
        h = int(time_part)
        mi = 0
    return SolarDateTime(year=y, month=m, day=d, hour=h, minute=mi)
