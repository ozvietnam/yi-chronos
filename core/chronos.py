from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from core.config import ALGORITHM_VERSION


STEMS = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")
BRANCHES = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")
SOLAR_TERMS = (
    "Xuân phân",
    "Thanh minh",
    "Cốc vũ",
    "Lập hạ",
    "Tiểu mãn",
    "Mang chủng",
    "Hạ chí",
    "Tiểu thử",
    "Đại thử",
    "Lập thu",
    "Xử thử",
    "Bạch lộ",
    "Thu phân",
    "Hàn lộ",
    "Sương giáng",
    "Lập đông",
    "Tiểu tuyết",
    "Đại tuyết",
    "Đông chí",
    "Tiểu hàn",
    "Đại hàn",
    "Lập xuân",
    "Vũ thủy",
    "Kinh trập",
)
WEEKDAY_VI = ("Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật")
TRUC_SEQUENCE = ("Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp", "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế")
FORTUNE_LABELS = ("Cát", "Bình", "Hung")


class GanZhi(BaseModel):
    year: str
    month: str
    day: str
    hour: str


class SolarTerm(BaseModel):
    id: int
    name_vi: str
    solar_longitude: float


class MoonPhase(BaseModel):
    name: str
    illumination: float
    phase_norm: float


class AlmanacInfo(BaseModel):
    lunar_date: str
    lunar_is_leap_month: bool
    weekday_vi: str
    truc_of_day: str
    annual_fortune: str
    monthly_fortune: str
    daily_fortune: str
    hourly_fortune: str


class ChronosState(BaseModel):
    timestamp_utc: str
    timezone: str
    local_datetime: str
    ganzhi: GanZhi
    solar_term: SolarTerm
    moon_phase: MoonPhase
    almanac: AlmanacInfo
    cycle_60_idx: int
    algorithm_version: str = ALGORITHM_VERSION
    # Day pillar transition convention (critique #19 from lien_hoa sage):
    #   "julian_noon"      → engine current default (Julian Day midpoint at noon UTC)
    #   "tradition_23h"    → classical 干支 reckoning (day starts at giờ Tý 23:00)
    #   "western_midnight" → 00:00 local time
    # NOTE: v1 engine uses Julian Day → consumers should be aware mid-day shift.
    day_pillar_convention: str = "julian_noon"


def parse_local_datetime(value: str | None, tz_name: str) -> datetime:
    zone = ZoneInfo(tz_name)
    if value is None:
        return datetime.now(zone).replace(microsecond=0)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def to_utc_string(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sexagenary_name(index: int) -> str:
    return f"{STEMS[index % 10]} {BRANCHES[index % 12]}"


def estimate_solar_longitude(local_dt: datetime) -> float:
    day_start = datetime(local_dt.year, 1, 1, tzinfo=local_dt.tzinfo)
    elapsed_days = (local_dt - day_start).total_seconds() / 86400
    tropical_year = 365.2422
    # Approximate 0 degrees near March equinox for MVP v1.
    return round(((elapsed_days - 79.0) / tropical_year * 360.0) % 360.0, 2)


def estimate_moon_phase(local_dt: datetime) -> MoonPhase:
    known_new_moon = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    days = (local_dt.astimezone(timezone.utc) - known_new_moon).total_seconds() / 86400
    phase = (days % 29.53058867) / 29.53058867
    illumination = round((1 - abs(phase * 2 - 1)), 3)
    if phase < 0.03 or phase > 0.97:
        name = "new_moon"
    elif phase < 0.25:
        name = "waxing_crescent"
    elif phase < 0.28:
        name = "first_quarter"
    elif phase < 0.50:
        name = "waxing_gibbous"
    elif phase < 0.53:
        name = "full_moon"
    elif phase < 0.75:
        name = "waning_gibbous"
    elif phase < 0.78:
        name = "last_quarter"
    else:
        name = "waning_crescent"
    return MoonPhase(name=name, illumination=illumination, phase_norm=round(phase, 4))


def _fortune_from_index(index: int) -> str:
    return FORTUNE_LABELS[index % len(FORTUNE_LABELS)]


# 早子時 (early Zi-hour) convention: hour ≥ 23:00 begins the NEW day.
# Sourced from the project's chosen Bát Tự master Thiệu Vĩ Hoa (《Dự đoán theo Tứ
# trụ》): "Giờ Tí là ranh giới giữa ngày hôm trước và ngày hôm sau, mà 23 giờ đã là
# giờ Tí rồi". Corroborated by `bat-tu-ha-lac` + `can-chi-thong-luan`. Configurable
# via env YI_ZI_CONVENTION = "early" (default, 23:00→next day) | "late" (00:00 boundary).
_EARLY_ZI = os.environ.get("YI_ZI_CONVENTION", "early").lower() != "late"


def _lunar_via_sxtwl(local_dt: datetime, early_zi: bool = _EARLY_ZI) -> tuple[int, int, int, bool]:
    """Lunar (day, month, year, is_leap) via sxtwl — single calendar source (#15).

    Unifies the lunar date on sxtwl (same system Tử Vi an-sao + the can-chi pillars
    use), with the 早子時 day-roll so it matches the day pillar + Tử Vi lunar_day.
    """
    import sxtwl

    eff_date = local_dt.date()
    if early_zi and local_dt.hour >= 23:
        eff_date = eff_date + timedelta(days=1)
    d = sxtwl.fromSolar(eff_date.year, eff_date.month, eff_date.day)
    return d.getLunarDay(), d.getLunarMonth(), d.getLunarYear(), bool(d.isLunarLeap())


def build_almanac(local_dt: datetime, cycle_idx: int, month_idx: int, hour_idx: int) -> AlmanacInfo:
    l_day, l_month, l_year, l_leap = _lunar_via_sxtwl(local_dt)
    weekday_vi = WEEKDAY_VI[local_dt.weekday()]
    truc = TRUC_SEQUENCE[cycle_idx % len(TRUC_SEQUENCE)]
    return AlmanacInfo(
        lunar_date=f"{l_day:02d}/{l_month:02d}/{l_year}",
        lunar_is_leap_month=l_leap,
        weekday_vi=weekday_vi,
        truc_of_day=truc,
        annual_fortune=_fortune_from_index((local_dt.year - 1984) % 60),
        monthly_fortune=_fortune_from_index(month_idx),
        daily_fortune=_fortune_from_index(cycle_idx),
        hourly_fortune=_fortune_from_index(hour_idx),
    )



def _cycle_index_from_gz(tg: int, dz: int) -> int:
    """60-cycle index (0..59) from sxtwl stem(0..9) + branch(0..11) via CRT."""
    return (6 * tg - 5 * dz) % 60


def _ganzhi_via_sxtwl(local_dt: datetime, early_zi: bool = _EARLY_ZI) -> tuple[int, int, int, int, int]:
    """Compute (year_idx, month_idx, day_idx, hour_idx, day_stem) as 60-cycle indices
    using sxtwl — astronomically correct can-chi.

    - Year boundary = 立春 (Lập Xuân), month boundary = 節 (12 tiết lệnh) — both via
      sxtwl getYearGZ()/getMonthGZ(). Fixes the old solar-calendar-month bug (#17).
    - Day boundary = continuous 60-day cycle via sxtwl getDayGZ() — fixes the old
      wrong-epoch bug (engine wrongly assumed 1970-01-01 = Giáp Tý).
    - 早子時: hour ≥ 23 rolls to the next civil day for the day/hour pillar.
    - Hour stem via 五鼠遁 (five-rat) from the (possibly rolled) day stem.
    """
    import sxtwl

    eff_date = local_dt.date()
    if early_zi and local_dt.hour >= 23:
        eff_date = eff_date + timedelta(days=1)

    day_obj = sxtwl.fromSolar(eff_date.year, eff_date.month, eff_date.day)
    ygz = day_obj.getYearGZ()
    mgz = day_obj.getMonthGZ()
    dgz = day_obj.getDayGZ()

    year_idx = _cycle_index_from_gz(ygz.tg, ygz.dz)
    month_idx = _cycle_index_from_gz(mgz.tg, mgz.dz)
    day_idx = _cycle_index_from_gz(dgz.tg, dgz.dz)

    # Hour branch: 23-1→Tý(0), 1-3→Sửu(1), …, 21-23→Hợi(11).
    hour_branch = ((local_dt.hour + 1) // 2) % 12
    # 五鼠遁: hour stem = (day_stem * 2 + hour_branch) mod 10.
    hour_stem = (dgz.tg * 2 + hour_branch) % 10
    hour_idx = _cycle_index_from_gz(hour_stem, hour_branch)
    return year_idx, month_idx, day_idx, hour_idx, dgz.tg


def calculate_chronos_state(datetime_local: str | None = None, timezone_name: str = "Asia/Ho_Chi_Minh") -> ChronosState:
    local_dt = parse_local_datetime(datetime_local, timezone_name)
    # Can-chi (year/month/day/hour) computed via sxtwl — astronomically correct
    # (立春 year boundary, 節 month boundary, continuous day cycle, 早子時 day-roll).
    year_idx, month_idx, cycle_idx, hour_idx, _day_stem = _ganzhi_via_sxtwl(local_dt)
    # Solar-term display still uses the linear estimate (cosmetic; does NOT feed can-chi).
    solar_longitude = estimate_solar_longitude(local_dt)
    solar_term_id = int(solar_longitude // 15) + 1

    return ChronosState(
        timestamp_utc=to_utc_string(local_dt),
        timezone=timezone_name,
        local_datetime=local_dt.replace(microsecond=0).isoformat(),
        ganzhi=GanZhi(
            year=sexagenary_name(year_idx),
            month=sexagenary_name(month_idx),
            day=sexagenary_name(cycle_idx),
            hour=sexagenary_name(hour_idx),
        ),
        solar_term=SolarTerm(
            id=solar_term_id,
            name_vi=SOLAR_TERMS[(solar_term_id - 1) % 24],
            solar_longitude=solar_longitude,
        ),
        moon_phase=estimate_moon_phase(local_dt),
        almanac=build_almanac(local_dt, cycle_idx, month_idx, hour_idx),
        cycle_60_idx=cycle_idx,
        day_pillar_convention="sxtwl_zao_zi" if _EARLY_ZI else "sxtwl_wan_zi",
    )
