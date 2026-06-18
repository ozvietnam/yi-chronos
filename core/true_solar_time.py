"""True-solar-time correction by birth longitude (Y4 / issue #35).

The civil clock for Vietnam (Asia/Ho_Chi_Minh, UTC+7) is anchored to the 105°E
meridian. A birth east/west of 105°E happens at a different *true solar time* than
the clock shows — and the hour (giờ) is the most boundary-sensitive pillar, so a
~10-20 min shift can flip the Hour branch at a canh boundary.

True solar time = civil time + longitude correction + equation of time:
  Δ(minutes) = (longitude − 105.0) × 4  +  EoT(date)

Everything here is OPT-IN: callers that don't supply a longitude get the unchanged
civil-time behavior (backward-compatible). `birth_longitude` is exact; the province
map is a convenience for app forms that only collected a province name.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

VN_CIVIL_MERIDIAN = 105.0  # Asia/Ho_Chi_Minh = UTC+7

# Approx longitude (°E) of province/city centres. birth_longitude overrides this;
# extend freely. Keys are lowercased + accent-insensitive via _norm().
_PROVINCE_LON: dict[str, float] = {
    "ha noi": 105.85, "hai phong": 106.69, "hai duong": 106.33, "hung yen": 106.05,
    "bac ninh": 106.08, "bac giang": 106.20, "thai nguyen": 105.85, "lang son": 106.76,
    "cao bang": 106.26, "ha giang": 104.98, "tuyen quang": 105.22, "lao cai": 103.97,
    "yen bai": 104.87, "phu tho": 105.22, "vinh phuc": 105.60, "bac kan": 105.83,
    "thai binh": 106.34, "nam dinh": 106.18, "ha nam": 105.92, "ninh binh": 105.97,
    "quang ninh": 107.08, "dien bien": 103.02, "lai chau": 103.46, "son la": 103.92,
    "hoa binh": 105.34, "thanh hoa": 105.78, "nghe an": 105.68, "ha tinh": 105.90,
    "quang binh": 106.62, "quang tri": 107.19, "thua thien hue": 107.58, "hue": 107.58,
    "da nang": 108.22, "quang nam": 108.02, "quang ngai": 108.80, "binh dinh": 109.22,
    "phu yen": 109.30, "khanh hoa": 109.18, "ninh thuan": 108.99, "binh thuan": 108.10,
    "kon tum": 108.00, "gia lai": 108.00, "dak lak": 108.05, "dak nong": 107.69,
    "lam dong": 108.45, "binh phuoc": 106.91, "tay ninh": 106.13, "binh duong": 106.66,
    "dong nai": 106.82, "ba ria vung tau": 107.08, "vung tau": 107.08,
    "ho chi minh": 106.70, "tphcm": 106.70, "sai gon": 106.70, "saigon": 106.70,
    "long an": 106.41, "tien giang": 106.34, "ben tre": 106.48, "tra vinh": 106.34,
    "vinh long": 105.97, "dong thap": 105.63, "an giang": 105.12, "kien giang": 105.08,
    "can tho": 105.78, "hau giang": 105.64, "soc trang": 105.97, "bac lieu": 105.72,
    "ca mau": 105.15,
}


def _norm(s: str) -> str:
    """Lowercase + strip Vietnamese accents for forgiving province lookup."""
    import unicodedata

    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().replace("đ", "d").split())


def province_longitude(province: str | None) -> float | None:
    if not province:
        return None
    return _PROVINCE_LON.get(_norm(province))


def resolve_longitude(
    *, birth_longitude: float | None = None, birth_province: str | None = None
) -> float | None:
    """birth_longitude (exact) wins; else map the province name; else None."""
    if birth_longitude is not None:
        try:
            lon = float(birth_longitude)
        except (TypeError, ValueError):
            return None
        return lon if -180.0 <= lon <= 180.0 else None
    return province_longitude(birth_province)


def equation_of_time_minutes(dt: datetime) -> float:
    """Equation of time (minutes), standard day-of-year approximation (±~16 min)."""
    n = dt.timetuple().tm_yday
    b = 2.0 * math.pi * (n - 81) / 364.0
    return 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)


def solar_offset_minutes(longitude: float, dt: datetime) -> float:
    """Minutes to ADD to VN civil time to get true solar time at `longitude`."""
    return (longitude - VN_CIVIL_MERIDIAN) * 4.0 + equation_of_time_minutes(dt)


def adjust_datetime(birth_datetime_local: str, longitude: float | None) -> str:
    """Shift an ISO local datetime to true solar time. None longitude → unchanged."""
    if longitude is None:
        return birth_datetime_local
    try:
        dt = datetime.fromisoformat(birth_datetime_local)
    except ValueError:
        return birth_datetime_local
    shifted = dt + timedelta(minutes=round(solar_offset_minutes(longitude, dt)))
    return shifted.replace(microsecond=0).isoformat()
