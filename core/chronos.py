from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from core.config import ALGORITHM_VERSION
from core.lunar_calendar import solar_to_lunar


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


def build_almanac(local_dt: datetime, cycle_idx: int, month_idx: int, hour_idx: int) -> AlmanacInfo:
    offset_hours = local_dt.utcoffset().total_seconds() / 3600 if local_dt.utcoffset() else 7.0
    lunar = solar_to_lunar(local_dt.day, local_dt.month, local_dt.year, offset_hours)
    weekday_vi = WEEKDAY_VI[local_dt.weekday()]
    truc = TRUC_SEQUENCE[cycle_idx % len(TRUC_SEQUENCE)]
    return AlmanacInfo(
        lunar_date=f"{lunar.day:02d}/{lunar.month:02d}/{lunar.year}",
        lunar_is_leap_month=lunar.is_leap,
        weekday_vi=weekday_vi,
        truc_of_day=truc,
        annual_fortune=_fortune_from_index((local_dt.year - 1984) % 60),
        monthly_fortune=_fortune_from_index(month_idx),
        daily_fortune=_fortune_from_index(cycle_idx),
        hourly_fortune=_fortune_from_index(hour_idx),
    )


def calculate_chronos_state(datetime_local: str | None = None, timezone_name: str = "Asia/Ho_Chi_Minh") -> ChronosState:
    local_dt = parse_local_datetime(datetime_local, timezone_name)
    # Use LOCAL date (not UTC) to avoid UTC-boundary bug for 00:00–06:59 in UTC+7.
    # Apply 早子時 rollover: hour 23 belongs to the CAN-CHI of the NEXT day.
    local_date = local_dt.date()
    if local_dt.hour >= 23:
        local_date += timedelta(days=1)
    _EPOCH = date(1970, 1, 1)
    days_since_epoch = (local_date - _EPOCH).days
    cycle_idx = days_since_epoch % 60
    solar_longitude = estimate_solar_longitude(local_dt)
    solar_term_id = int(solar_longitude // 15) + 1
    year_idx = (local_dt.year - 1984) % 60
    month_idx = (year_idx * 12 + local_dt.month - 1) % 60
    hour_branch = ((local_dt.hour + 1) // 2) % 12
    hour_idx = (cycle_idx * 12 + hour_branch) % 60

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
    )
