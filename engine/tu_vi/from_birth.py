"""Cast lá số Tử Vi TỪ giờ sinh dương lịch (orchestrator nhỏ, DRY).

`cast_la_so` (an_sao) nhận lunar_month/day + hour_branch + year ganzhi — KHÔNG nhận
birth_datetime. Helper này convert (true-solar → âm lịch + can-chi năm + giờ chi) rồi
gọi cast_la_so. Dùng chung: `/api/tu-vi/cast` (inline) + `_build_chart_data` (Hermes
sage) + `menh_profile` (T2).

⚠️ Vá bug 2026-06-19: `_build_chart_data` gọi `cast_la_so(birth_datetime_local=...)`
SAI signature → tu_vi luôn raise âm thầm (try/except nuốt) → council/quick sage bấy nay
luận THIẾU lá số Tử Vi. Helper này khắc phục triệt để.
"""
from __future__ import annotations

from datetime import datetime as _dt
from typing import Optional

# Giờ 0..23 → địa chi. (23h "早子時" → Tý của ngày mới đã được solar_to_lunar xử lý ở
# bước chuyển âm lịch; bảng này chỉ map giờ→chi.)
_HOUR_BRANCH_BY_HOUR = (
    "Tý", "Sửu", "Sửu", "Dần", "Dần", "Mão", "Mão",
    "Thìn", "Thìn", "Tỵ", "Tỵ", "Ngọ", "Ngọ",
    "Mùi", "Mùi", "Thân", "Thân", "Dậu", "Dậu",
    "Tuất", "Tuất", "Hợi", "Hợi", "Tý",
)


def hour_branch_from_hour(hour: int) -> str:
    """Map giờ 0..23 → địa chi giờ."""
    return _HOUR_BRANCH_BY_HOUR[hour % 24]


def cast_la_so_from_birth(*, birth_datetime_local: str,
                          timezone: str = "Asia/Ho_Chi_Minh",
                          gender: str = "nam",
                          birth_longitude: Optional[float] = None,
                          birth_province: Optional[str] = None) -> dict:
    """Cast lá số Tử Vi đầy đủ từ giờ sinh dương lịch (đã hiệu chỉnh giờ mặt trời thật).
    Lazy import để tránh chu trình import lúc nạp module."""
    from core.chronos import calculate_chronos_state
    from core.true_solar_time import adjust_datetime, resolve_longitude
    from engine.yi_wiki.lich_conversion import SolarDateTime, solar_to_lunar
    from engine.tu_vi.an_sao import cast_la_so

    lon = resolve_longitude(birth_longitude=birth_longitude, birth_province=birth_province)
    bdt = adjust_datetime(birth_datetime_local, lon)        # true solar time
    chronos = calculate_chronos_state(bdt, timezone)
    local_dt = _dt.fromisoformat(bdt)
    solar = SolarDateTime(year=local_dt.year, month=local_dt.month, day=local_dt.day,
                          hour=local_dt.hour, minute=local_dt.minute)
    lunar = solar_to_lunar(solar)                            # xử lý 早子時 (#13)
    year_parts = chronos.ganzhi.year.split()
    return cast_la_so(
        lunar_month=lunar.lunar_month,
        lunar_day=lunar.lunar_day,
        hour_branch=hour_branch_from_hour(local_dt.hour),
        year_stem=year_parts[0],
        year_branch=year_parts[1],
        gender=gender,
    )
