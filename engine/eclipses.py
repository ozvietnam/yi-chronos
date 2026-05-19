"""Eclipses Engine.

Finds solar and lunar eclipses across a lifespan and identifies which
ones "activate" the natal chart by falling within orb of a natal point.

A solar eclipse occurs when the Moon's ecliptic latitude is small at
New Moon. A lunar eclipse occurs when the Moon's latitude is small at
Full Moon. We use latitude thresholds rather than computing nodes, which
captures every eclipse including partials.
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
)  # noqa: F401  (ecliptic_frame imported via skyfield)


SOLAR_ECLIPSE_LAT_THRESHOLD = 1.5
LUNAR_ECLIPSE_LAT_THRESHOLD = 1.0
ACTIVATION_ORB_MAJOR = 3.0
ACTIVATION_ORB_MEDIUM = 6.0

NATAL_PERSONAL_POINTS = ("sun", "moon", "mercury", "venus", "mars")


@dataclass
class EclipseActivation:
    natal_point: str
    orb_deg: float
    importance: str  # "major" | "medium"


@dataclass
class Eclipse:
    date_utc: str
    age_years: float
    eclipse_type: str  # "solar" | "lunar"
    eclipse_subtype: str  # "total"|"annular"|"partial" (solar) ; "total"|"partial"|"penumbral" (lunar)
    eclipse_longitude: float
    eclipse_sign: str
    eclipse_sign_degree: float
    moon_latitude: float
    activations: list[EclipseActivation]
    importance: str  # "major" if any major activation else "medium" if any medium else "minor"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["activations"] = [asdict(a) for a in self.activations]
        return d


def _signed_diff(a: float, b: float) -> float:
    return (a - b + 540.0) % 360.0 - 180.0


def _bulk_lon_lat(eph, ts, body_key: str, datetimes: list[datetime]):
    times = ts.from_datetimes(datetimes)
    earth = eph["earth"]
    body = eph[body_key]
    apparent = earth.at(times).observe(body).apparent()
    lat, lon, _ = apparent.frame_latlon(ecliptic_frame)
    return [v % 360.0 for v in lon.degrees.tolist()], list(lat.degrees.tolist())


def _classify_solar_subtype(abs_lat: float) -> str:
    if abs_lat < 0.45:
        return "total_or_annular"
    return "partial"


def _classify_lunar_subtype(abs_lat: float) -> str:
    if abs_lat < 0.4:
        return "total"
    if abs_lat < 0.7:
        return "partial"
    return "penumbral"


def _activations_for_eclipse(eclipse_lon: float, natal_lons: dict[str, float]) -> tuple[list[EclipseActivation], str]:
    luminaries = {"sun", "moon", "ascendant", "midheaven"}
    activations: list[EclipseActivation] = []
    overall = "minor"
    for name, n_lon in natal_lons.items():
        orb = abs(_signed_diff(eclipse_lon, n_lon))
        if orb <= ACTIVATION_ORB_MAJOR and name in luminaries:
            activations.append(EclipseActivation(name, round(orb, 3), "major"))
            overall = "major"
        elif orb <= ACTIVATION_ORB_MEDIUM:
            importance = "medium" if name in luminaries else "minor"
            activations.append(EclipseActivation(name, round(orb, 3), importance))
            if overall == "minor" and importance == "medium":
                overall = "medium"
    activations.sort(key=lambda a: a.orb_deg)
    return activations, overall


def compute_eclipses(
    birth_dt: datetime,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
    only_activated: bool = True,
) -> list[Eclipse]:
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
    step = timedelta(days=1)
    while cur <= end_dt:
        sample_dts.append(cur)
        cur = cur + step

    sun_lons, _ = _bulk_lon_lat(eph, ts, BODY_EPHEMERIS_KEYS["sun"], sample_dts)
    moon_lons, moon_lats = _bulk_lon_lat(eph, ts, BODY_EPHEMERIS_KEYS["moon"], sample_dts)
    phases = [(m - s) % 360.0 for m, s in zip(moon_lons, sun_lons)]

    eclipses: list[Eclipse] = []

    for i in range(1, len(phases)):
        prev_p = phases[i - 1]
        cur_p = phases[i]

        # New Moon detection: phase wraps from > 270 down through 360 to < 90.
        new_moon = prev_p > 270.0 and cur_p < 90.0
        # Full Moon detection: phase crosses 180 going up.
        full_moon = prev_p < 180.0 <= cur_p

        if not new_moon and not full_moon:
            continue

        # Linear interpolate the exact crossing within the 1-day window.
        if new_moon:
            unwrapped_prev = prev_p - 360.0  # so it's negative, near 0
            target = 0.0
            frac = (target - unwrapped_prev) / (cur_p - unwrapped_prev) if cur_p != unwrapped_prev else 0.0
        else:
            target = 180.0
            frac = (target - prev_p) / (cur_p - prev_p) if cur_p != prev_p else 0.0
        frac = max(0.0, min(1.0, frac))
        delta = sample_dts[i] - sample_dts[i - 1]
        exact = sample_dts[i - 1] + delta * frac

        # Interpolate moon longitude/latitude at that fraction (handle wrap for lon).
        prev_moon_lon = moon_lons[i - 1]
        cur_moon_lon = moon_lons[i]
        if cur_moon_lon < prev_moon_lon - 180.0:
            cur_moon_lon += 360.0
        moon_lon_at = (prev_moon_lon + (cur_moon_lon - prev_moon_lon) * frac) % 360.0
        moon_lat_at = moon_lats[i - 1] + (moon_lats[i] - moon_lats[i - 1]) * frac

        abs_lat = abs(moon_lat_at)
        if new_moon and abs_lat > SOLAR_ECLIPSE_LAT_THRESHOLD:
            continue
        if full_moon and abs_lat > LUNAR_ECLIPSE_LAT_THRESHOLD:
            continue

        eclipse_lon = moon_lon_at  # at conjunction/opposition, moon's longitude is the eclipse longitude
        sign, sign_deg = _longitude_to_sign(eclipse_lon)
        activations, overall_importance = _activations_for_eclipse(eclipse_lon, natal_lons)

        if only_activated and not activations:
            continue

        age = (exact - birth_dt).total_seconds() / (365.25 * 86400.0)
        eclipses.append(
            Eclipse(
                date_utc=exact.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                age_years=round(age, 3),
                eclipse_type="solar" if new_moon else "lunar",
                eclipse_subtype=_classify_solar_subtype(abs_lat) if new_moon else _classify_lunar_subtype(abs_lat),
                eclipse_longitude=round(eclipse_lon, 4),
                eclipse_sign=sign,
                eclipse_sign_degree=round(sign_deg, 3),
                moon_latitude=round(moon_lat_at, 4),
                activations=activations,
                importance=overall_importance,
            )
        )

    eclipses.sort(key=lambda e: e.age_years)
    return eclipses
