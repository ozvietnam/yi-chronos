"""Solar Arc Directions Engine.

A symbolic technique: every natal point advances by the same rate as the
progressed Sun (~1°/year). When an arc-directed planet forms a major
aspect with a natal point, astrologers read it as a symbolic milestone.

The arc rate at age N is computed from the actual progressed Sun motion,
not the simple ~1°/year approximation, so dates are accurate to days.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from engine.sky import (
    BODY_EPHEMERIS_KEYS,
    _ascendant_midheaven,
    _ecliptic_longitude,
    _load_ephemeris,
    _longitude_to_sign,
)


DIRECTED_BODIES = (
    "sun", "moon", "mercury", "venus", "mars",
    "jupiter", "saturn", "uranus", "neptune", "pluto",
)
NATAL_TARGETS = (
    "sun", "moon", "mercury", "venus", "mars",
    "ascendant", "midheaven",
)
ASPECTS = (
    ("conjunction", 0.0),
    ("sextile", 60.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
)
HARD_ASPECTS = {"conjunction", "square", "opposition"}


@dataclass
class SolarArcHit:
    date_utc: str
    age_years: float
    directed_body: str
    natal_target: str
    aspect_type: str
    aspect_angle: float
    arc_value_deg: float
    importance: str

    def to_dict(self) -> dict:
        return asdict(self)


def _classify_importance(directed: str, target: str, aspect: str) -> str:
    luminaries = {"sun", "moon", "ascendant", "midheaven"}
    heavies = {"saturn", "uranus", "pluto"}
    if (directed in heavies and target in luminaries and aspect in HARD_ASPECTS) or \
       (directed in luminaries and target in luminaries and aspect in HARD_ASPECTS):
        return "major"
    if directed in heavies or target in luminaries or directed in luminaries:
        return "medium"
    return "minor"


def compute_solar_arc_hits(
    birth_dt: datetime,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
) -> list[SolarArcHit]:
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()

    natal_lons: dict[str, float] = {}
    natal_t = ts.from_datetime(birth_dt)
    for name, key in BODY_EPHEMERIS_KEYS.items():
        natal_lons[name], _ = _ecliptic_longitude(eph, key, natal_t)
    if lat is not None and lon is not None:
        asc, mc = _ascendant_midheaven(eph, ts, birth_dt, lat, lon)
        natal_lons["ascendant"] = asc.ecliptic_longitude
        natal_lons["midheaven"] = mc.ecliptic_longitude

    natal_sun_lon = natal_lons["sun"]
    sun_key = BODY_EPHEMERIS_KEYS["sun"]

    # Tabulate arc value (degrees) at integer ages 0..span_years.
    arc_table: list[tuple[float, float]] = []
    for age in range(span_years + 1):
        prog_dt = birth_dt + timedelta(days=age)
        prog_sun_lon, _ = _ecliptic_longitude(eph, sun_key, ts.from_datetime(prog_dt))
        arc = (prog_sun_lon - natal_sun_lon) % 360.0
        # Unwrap monotonically (arc grows from 0).
        if arc_table and arc < arc_table[-1][1] - 180:
            arc += 360.0
        arc_table.append((float(age), arc))

    max_arc = arc_table[-1][1]

    def age_at_arc(target_arc: float) -> float | None:
        if target_arc < 0 or target_arc > max_arc:
            return None
        for i in range(1, len(arc_table)):
            prev_age, prev_arc = arc_table[i - 1]
            cur_age, cur_arc = arc_table[i]
            if prev_arc <= target_arc <= cur_arc:
                if cur_arc == prev_arc:
                    return prev_age
                frac = (target_arc - prev_arc) / (cur_arc - prev_arc)
                return prev_age + frac * (cur_age - prev_age)
        return None

    hits: list[SolarArcHit] = []
    for directed in DIRECTED_BODIES:
        if directed not in natal_lons:
            continue
        for target in NATAL_TARGETS:
            if target not in natal_lons or directed == target:
                continue
            for aspect_name, aspect_angle in ASPECTS:
                # Arc value when directed reaches aspect with target:
                # natal_directed + arc = natal_target + aspect_angle (mod 360)
                raw = (natal_lons[target] - natal_lons[directed] + aspect_angle) % 360.0
                # Arc grows monotonically. Use raw value within [0, max_arc].
                age = age_at_arc(raw)
                if age is None or age < 0 or age > span_years:
                    continue
                exact_dt = birth_dt + timedelta(days=365.2422 * age)
                hits.append(
                    SolarArcHit(
                        date_utc=exact_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                        age_years=round(age, 3),
                        directed_body=directed,
                        natal_target=target,
                        aspect_type=aspect_name,
                        aspect_angle=float(aspect_angle),
                        arc_value_deg=round(raw, 3),
                        importance=_classify_importance(directed, target, aspect_name),
                    )
                )

    hits.sort(key=lambda h: h.age_years)
    return hits
