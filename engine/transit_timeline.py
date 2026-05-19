"""Transit Timeline Engine.

Computes when slow transiting planets (Jupiter, Saturn, Uranus, Neptune, Pluto)
form major aspects (conjunction, sextile, square, trine, opposition) with
natal personal points (Sun, Moon, Mercury, Venus, Mars, plus Ascendant/MC if
location is supplied).

Uses skyfield bulk ephemeris evaluation for performance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from skyfield.framelib import ecliptic_frame

from engine.sky import (
    BODY_EPHEMERIS_KEYS,
    _ascendant_midheaven,
    _ecliptic_longitude,
    _load_ephemeris,
    _longitude_to_sign,
)


NATAL_PERSONAL_POINTS = ("sun", "moon", "mercury", "venus", "mars")
TRANSIT_SLOW_BODIES = ("jupiter", "saturn", "uranus", "neptune", "pluto")
TRANSIT_ASPECTS = (
    ("conjunction", 0.0),
    ("sextile", 60.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
)
HARD_ASPECTS = {"conjunction", "square", "opposition"}


@dataclass
class TransitHit:
    date_utc: str
    age_years: float
    transit_body: str
    natal_point: str
    aspect_type: str
    aspect_angle: float
    transit_sign: str
    transit_degree: float
    importance: str  # "major" | "medium" | "minor"

    def to_dict(self) -> dict:
        return asdict(self)


def _signed_diff(a: float, b: float) -> float:
    return (a - b + 540.0) % 360.0 - 180.0


def _bulk_longitudes(eph, ts, body_key: str, datetimes: list[datetime]):
    """Vectorized geocentric apparent ecliptic longitudes (degrees)."""
    times = ts.from_datetimes(datetimes)
    earth = eph["earth"]
    body = eph[body_key]
    apparent = earth.at(times).observe(body).apparent()
    _lat, lon, _dist = apparent.frame_latlon(ecliptic_frame)
    return [v % 360.0 for v in lon.degrees.tolist()]


def _bisect_aspect(eph, ts, body_key: str, target_point: float, t_low: datetime, t_high: datetime, max_iter: int = 40) -> datetime:
    def diff_at(dt: datetime) -> float:
        lon, _ = _ecliptic_longitude(eph, body_key, ts.from_datetime(dt))
        return _signed_diff(lon, target_point)

    lo, hi = t_low, t_high
    d_lo = diff_at(lo)
    for _ in range(max_iter):
        if (hi - lo).total_seconds() < 3600:
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


def _classify_importance(transit: str, natal: str, aspect: str) -> str:
    luminaries = {"sun", "moon", "ascendant", "midheaven"}
    heavyweights = {"saturn", "uranus", "pluto"}
    if natal in luminaries and transit in heavyweights and aspect in HARD_ASPECTS:
        return "major"
    if natal in luminaries or transit in heavyweights:
        return "medium"
    return "minor"


def compute_transit_hits(
    birth_dt: datetime,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
    step_days: int = 15,
) -> list[TransitHit]:
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()
    natal_t = ts.from_datetime(birth_dt)

    natal_lons: dict[str, float] = {}
    for name in NATAL_PERSONAL_POINTS:
        natal_lons[name], _ = _ecliptic_longitude(eph, BODY_EPHEMERIS_KEYS[name], natal_t)

    if lat is not None and lon is not None:
        asc, mc = _ascendant_midheaven(eph, ts, birth_dt, lat, lon)
        natal_lons["ascendant"] = asc.ecliptic_longitude
        natal_lons["midheaven"] = mc.ecliptic_longitude

    end_dt = birth_dt + timedelta(days=365.25 * span_years)
    sample_dts: list[datetime] = []
    cur = birth_dt
    step = timedelta(days=step_days)
    while cur <= end_dt:
        sample_dts.append(cur)
        cur = cur + step

    hits: list[TransitHit] = []
    for transit_name in TRANSIT_SLOW_BODIES:
        transit_key = BODY_EPHEMERIS_KEYS[transit_name]
        transit_lons = _bulk_longitudes(eph, ts, transit_key, sample_dts)

        for natal_name, natal_lon in natal_lons.items():
            for aspect_name, aspect_angle in TRANSIT_ASPECTS:
                target = (natal_lon + aspect_angle) % 360.0
                diffs = [_signed_diff(l, target) for l in transit_lons]

                for i in range(1, len(diffs)):
                    prev_d = diffs[i - 1]
                    cur_d = diffs[i]
                    if prev_d * cur_d < 0 and abs(prev_d) < 25.0 and abs(cur_d) < 25.0:
                        exact = _bisect_aspect(eph, ts, transit_key, target, sample_dts[i - 1], sample_dts[i])
                        age = (exact - birth_dt).total_seconds() / (365.25 * 86400.0)
                        if age < 0 or age > span_years:
                            continue
                        lon_at, _ = _ecliptic_longitude(eph, transit_key, ts.from_datetime(exact))
                        sign, sign_deg = _longitude_to_sign(lon_at)
                        date_iso = exact.replace(microsecond=0).isoformat().replace("+00:00", "Z")
                        hits.append(
                            TransitHit(
                                date_utc=date_iso,
                                age_years=round(age, 3),
                                transit_body=transit_name,
                                natal_point=natal_name,
                                aspect_type=aspect_name,
                                aspect_angle=float(aspect_angle),
                                transit_sign=sign,
                                transit_degree=round(sign_deg, 3),
                                importance=_classify_importance(transit_name, natal_name, aspect_name),
                            )
                        )

    hits.sort(key=lambda h: h.age_years)
    return hits
