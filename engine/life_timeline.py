"""Life Timeline Engine.

Given a birth datetime, compute the major astrological milestones across
a lifespan: Saturn/Jupiter/Uranus/Neptune/Pluto returns, squares, and
oppositions to their own natal positions, plus nodal returns.

Output is a deterministic list of dated events the user can correlate
against real-life memories. This is state mapping, not prediction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from engine.sky import (
    BODY_EPHEMERIS_KEYS,
    _ecliptic_longitude,
    _load_ephemeris,
    _longitude_to_sign,
)


# Each row: (transit_body, target_angle_deg, natal_body, label_vi, importance)
# Importance: "major" = life-defining; "medium" = significant; "minor" = soft.
MILESTONE_DEFS = [
    ("saturn",  0,   "saturn",  "Thổ Tinh hồi quy",                      "major"),
    ("saturn",  90,  "saturn",  "Thổ Tinh vuông Thổ Tinh sinh",          "medium"),
    ("saturn",  180, "saturn",  "Thổ Tinh đối Thổ Tinh sinh",            "medium"),
    ("jupiter", 0,   "jupiter", "Mộc Tinh hồi quy",                       "medium"),
    ("uranus",  90,  "uranus",  "Thiên Vương vuông Thiên Vương sinh",    "medium"),
    ("uranus",  180, "uranus",  "Thiên Vương đối Thiên Vương sinh",      "major"),
    ("neptune", 90,  "neptune", "Hải Vương vuông Hải Vương sinh",        "medium"),
    ("pluto",   90,  "pluto",   "Diêm Vương vuông Diêm Vương sinh",      "major"),
]

ASPECT_TYPE_VI = {
    0: "return",
    90: "square",
    180: "opposition",
}


@dataclass
class Milestone:
    date_utc: str
    age_years: float
    transit_body: str
    natal_body: str
    aspect_type: str
    aspect_angle: float
    label_vi: str
    importance: str
    transit_sign: str
    transit_degree: float

    def to_dict(self) -> dict:
        return asdict(self)


def _signed_diff(a: float, b: float) -> float:
    """Return signed shortest angular difference a - b in (-180, 180]."""
    return (a - b + 540.0) % 360.0 - 180.0


def _natal_longitudes(eph, ts, birth_dt: datetime) -> dict[str, float]:
    t = ts.from_datetime(birth_dt)
    out: dict[str, float] = {}
    for name, key in BODY_EPHEMERIS_KEYS.items():
        lon, _ = _ecliptic_longitude(eph, key, t)
        out[name] = lon
    return out


def _bisect_aspect_date(
    eph,
    ts,
    transit_key: str,
    natal_lon: float,
    target_angle_deg: float,
    t_low: datetime,
    t_high: datetime,
    max_iter: int = 50,
) -> datetime:
    target_point = (natal_lon + target_angle_deg) % 360.0

    def diff_at(dt: datetime) -> float:
        lon, _ = _ecliptic_longitude(eph, transit_key, ts.from_datetime(dt))
        return _signed_diff(lon, target_point)

    lo = t_low
    hi = t_high
    d_lo = diff_at(lo)
    for _ in range(max_iter):
        if (hi - lo).total_seconds() < 3600:  # 1 hour precision
            break
        mid = lo + (hi - lo) / 2
        d_mid = diff_at(mid)
        if d_lo == 0:
            return lo
        if d_lo * d_mid <= 0:
            hi = mid
        else:
            lo = mid
            d_lo = d_mid
    return lo + (hi - lo) / 2


def compute_life_timeline(
    birth_dt: datetime,
    span_years: int = 90,
    step_days: int = 30,
) -> list[Milestone]:
    """Compute major life milestones from birth_dt to birth_dt + span_years.

    birth_dt: timezone-aware datetime. Naive is treated as UTC.
    """
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()
    natal_lons = _natal_longitudes(eph, ts, birth_dt)

    end_dt = birth_dt + timedelta(days=365.25 * span_years)
    step = timedelta(days=step_days)

    milestones: list[Milestone] = []
    seen: set[tuple[str, str, float, str]] = set()

    for transit_name, target_angle, natal_name, label, importance in MILESTONE_DEFS:
        natal_lon = natal_lons[natal_name]
        transit_key = BODY_EPHEMERIS_KEYS[transit_name]
        target_point = (natal_lon + target_angle) % 360.0

        prev_dt = birth_dt
        prev_lon, _ = _ecliptic_longitude(eph, transit_key, ts.from_datetime(prev_dt))
        prev_diff = _signed_diff(prev_lon, target_point)
        cur_dt = prev_dt + step

        while cur_dt <= end_dt:
            cur_lon, _ = _ecliptic_longitude(eph, transit_key, ts.from_datetime(cur_dt))
            cur_diff = _signed_diff(cur_lon, target_point)

            crossed = (
                prev_diff * cur_diff < 0
                and abs(prev_diff) < 30.0
                and abs(cur_diff) < 30.0
            )
            if crossed:
                exact = _bisect_aspect_date(
                    eph, ts, transit_key, natal_lon, float(target_angle), prev_dt, cur_dt
                )
                age = (exact - birth_dt).total_seconds() / (365.25 * 86400.0)
                lon_at, _ = _ecliptic_longitude(eph, transit_key, ts.from_datetime(exact))
                sign, sign_deg = _longitude_to_sign(lon_at)
                date_iso = exact.replace(microsecond=0).isoformat().replace("+00:00", "Z")

                # Dedup: triple-crossings within ~10 days collapse to first.
                key = (transit_name, natal_name, float(target_angle), date_iso[:7])
                if key in seen:
                    pass  # keep all crossings — retrograde triple-hits are real
                seen.add(key)

                milestones.append(
                    Milestone(
                        date_utc=date_iso,
                        age_years=round(age, 3),
                        transit_body=transit_name,
                        natal_body=natal_name,
                        aspect_type=ASPECT_TYPE_VI[target_angle],
                        aspect_angle=float(target_angle),
                        label_vi=label,
                        importance=importance,
                        transit_sign=sign,
                        transit_degree=round(sign_deg, 3),
                    )
                )

            prev_dt = cur_dt
            prev_diff = cur_diff
            cur_dt = cur_dt + step

    milestones.sort(key=lambda m: m.age_years)
    return milestones
