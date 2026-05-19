"""Sky Engine — Western astrology state mapping.

Computes deterministic positions of 10 classical bodies + lunar nodes in the
tropical zodiac, plus aspects, retrograde flags, and dignities.

Framing rule: this module produces STATE descriptions of the sky, not
predictions. See docs/spec-universe-now-western-astrology.md.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from skyfield.api import Loader


EPHEMERIS_DIR = Path(__file__).resolve().parent.parent / "data" / "ephemeris"
EPHEMERIS_FILE = "de440s.bsp"
EPHEMERIS_SOURCE = "JPL DE440s"

ZODIAC_SIGNS = (
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
)

SIGN_ELEMENTS = {
    "aries": "fire", "leo": "fire", "sagittarius": "fire",
    "taurus": "earth", "virgo": "earth", "capricorn": "earth",
    "gemini": "air", "libra": "air", "aquarius": "air",
    "cancer": "water", "scorpio": "water", "pisces": "water",
}

# Body name -> Skyfield ephemeris key. Pluto = pluto barycenter.
BODY_EPHEMERIS_KEYS = {
    "sun": "sun",
    "moon": "moon",
    "mercury": "mercury barycenter",
    "venus": "venus barycenter",
    "mars": "mars barycenter",
    "jupiter": "jupiter barycenter",
    "saturn": "saturn barycenter",
    "uranus": "uranus barycenter",
    "neptune": "neptune barycenter",
    "pluto": "pluto barycenter",
}

DEFAULT_BODIES = tuple(BODY_EPHEMERIS_KEYS.keys())

# Traditional rulerships (used for dignity).
RULERSHIPS = {
    "sun": ("leo",),
    "moon": ("cancer",),
    "mercury": ("gemini", "virgo"),
    "venus": ("taurus", "libra"),
    "mars": ("aries", "scorpio"),
    "jupiter": ("sagittarius", "pisces"),
    "saturn": ("capricorn", "aquarius"),
    # Modern rulers — informational only.
    "uranus": ("aquarius",),
    "neptune": ("pisces",),
    "pluto": ("scorpio",),
}

EXALTATIONS = {
    "sun": "aries",
    "moon": "taurus",
    "mercury": "virgo",
    "venus": "pisces",
    "mars": "capricorn",
    "jupiter": "cancer",
    "saturn": "libra",
}

# Major aspects: name -> (exact angle, default orb).
ASPECTS = (
    ("conjunction", 0.0, 8.0),
    ("opposition", 180.0, 8.0),
    ("trine", 120.0, 6.0),
    ("square", 90.0, 6.0),
    ("sextile", 60.0, 4.0),
)


@dataclass
class SkyBody:
    name: str
    ecliptic_longitude: float
    ecliptic_latitude: float
    sign: str
    sign_degree: float
    is_retrograde: bool
    speed_deg_per_day: float
    dignity: str | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SkyAspect:
    body_a: str
    body_b: str
    aspect_type: str
    angle_deg: float
    orb_deg: float
    applying: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SkyChart:
    timestamp_utc: str
    bodies: list[SkyBody]
    aspects: list[SkyAspect]
    sun_sign: str
    moon_sign: str
    dominant_element: str
    ascendant: SkyBody | None
    midheaven: SkyBody | None
    ephemeris_source: str

    def to_dict(self) -> dict:
        return {
            "timestamp_utc": self.timestamp_utc,
            "bodies": [b.to_dict() for b in self.bodies],
            "aspects": [a.to_dict() for a in self.aspects],
            "sun_sign": self.sun_sign,
            "moon_sign": self.moon_sign,
            "dominant_element": self.dominant_element,
            "ascendant": self.ascendant.to_dict() if self.ascendant else None,
            "midheaven": self.midheaven.to_dict() if self.midheaven else None,
            "ephemeris_source": self.ephemeris_source,
        }


@lru_cache(maxsize=1)
def _load_ephemeris():
    EPHEMERIS_DIR.mkdir(parents=True, exist_ok=True)
    loader = Loader(str(EPHEMERIS_DIR))
    eph = loader(EPHEMERIS_FILE)
    ts = loader.timescale()
    return eph, ts


def _longitude_to_sign(lon_deg: float) -> tuple[str, float]:
    lon = lon_deg % 360.0
    idx = int(lon // 30)
    return ZODIAC_SIGNS[idx], lon - idx * 30.0


def _dignity(body: str, sign: str) -> str | None:
    if sign in RULERSHIPS.get(body, ()):
        return "rulership"
    if EXALTATIONS.get(body) == sign:
        return "exaltation"
    # Detriment = opposite of rulership; fall = opposite of exaltation.
    rulers = RULERSHIPS.get(body, ())
    if rulers:
        opposite_signs = {ZODIAC_SIGNS[(ZODIAC_SIGNS.index(s) + 6) % 12] for s in rulers}
        if sign in opposite_signs:
            return "detriment"
    exalt = EXALTATIONS.get(body)
    if exalt:
        opposite = ZODIAC_SIGNS[(ZODIAC_SIGNS.index(exalt) + 6) % 12]
        if sign == opposite:
            return "fall"
    return None


def _ecliptic_longitude(eph, body_key: str, t):
    """Geocentric apparent ecliptic longitude/latitude in degrees at time t."""
    from skyfield.framelib import ecliptic_frame
    earth = eph["earth"]
    body = eph[body_key]
    astrometric = earth.at(t).observe(body).apparent()
    lat, lon, _ = astrometric.frame_latlon(ecliptic_frame)
    return lon.degrees % 360.0, lat.degrees


def _body_speed(eph, ts, body_key: str, dt_utc: datetime) -> float:
    """Approximate ecliptic longitude speed in deg/day using +/-12h sample."""
    from datetime import timedelta
    t_minus = ts.from_datetime(dt_utc - timedelta(hours=12))
    t_plus = ts.from_datetime(dt_utc + timedelta(hours=12))
    lon_minus, _ = _ecliptic_longitude(eph, body_key, t_minus)
    lon_plus, _ = _ecliptic_longitude(eph, body_key, t_plus)
    diff = (lon_plus - lon_minus + 540) % 360 - 180  # signed shortest delta
    return diff  # deg per day (24h between samples)


def _make_body(eph, ts, name: str, dt_utc: datetime) -> SkyBody:
    body_key = BODY_EPHEMERIS_KEYS[name]
    t = ts.from_datetime(dt_utc)
    lon, lat = _ecliptic_longitude(eph, body_key, t)
    sign, sign_deg = _longitude_to_sign(lon)
    speed = _body_speed(eph, ts, body_key, dt_utc)
    is_retro = speed < 0 and name not in ("sun", "moon")
    return SkyBody(
        name=name,
        ecliptic_longitude=round(lon, 4),
        ecliptic_latitude=round(lat, 4),
        sign=sign,
        sign_degree=round(sign_deg, 4),
        is_retrograde=bool(is_retro),
        speed_deg_per_day=round(speed, 4),
        dignity=_dignity(name, sign),
    )


def _angular_separation(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _detect_aspects(bodies: list[SkyBody]) -> list[SkyAspect]:
    aspects: list[SkyAspect] = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            sep = _angular_separation(a.ecliptic_longitude, b.ecliptic_longitude)
            for name, exact, max_orb in ASPECTS:
                orb = abs(sep - exact)
                if orb <= max_orb:
                    # Applying: separation decreasing toward exact.
                    # Approximate: faster body moving toward slower body.
                    # If a's longitude is increasing faster than b's, and a is "behind" b modulo aspect, applying.
                    speed_diff = a.speed_deg_per_day - b.speed_deg_per_day
                    delta = ((a.ecliptic_longitude - b.ecliptic_longitude) % 360.0)
                    # Convert delta into signed shortest path
                    if delta > 180.0:
                        delta -= 360.0
                    applying = (speed_diff * (-1 if delta > 0 else 1)) > 0
                    aspects.append(
                        SkyAspect(
                            body_a=a.name,
                            body_b=b.name,
                            aspect_type=name,
                            angle_deg=round(sep, 3),
                            orb_deg=round(orb, 3),
                            applying=bool(applying),
                        )
                    )
                    break  # Only one aspect type per pair (closest match).
    return aspects


def _dominant_element(bodies: list[SkyBody]) -> str:
    counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    for b in bodies:
        counts[SIGN_ELEMENTS[b.sign]] += 1
    return max(counts, key=lambda k: counts[k])


def _ascendant_midheaven(eph, ts, dt_utc: datetime, lat: float, lon: float) -> tuple[SkyBody, SkyBody]:
    """Compute Ascendant and Midheaven using GAST + standard formulas.

    Returns two SkyBody instances with name 'ascendant' and 'midheaven'.
    """
    import math
    from skyfield.framelib import ecliptic_frame  # noqa: F401  (validates import)

    t = ts.from_datetime(dt_utc)
    # Greenwich Apparent Sidereal Time, hours.
    gast_hours = t.gast
    lst_hours = (gast_hours + lon / 15.0) % 24.0
    lst_deg = lst_hours * 15.0

    # Obliquity of the ecliptic (mean), radians.
    # Skyfield exposes via earth_orientation but a constant ~23.4393° is fine here.
    eps = math.radians(23.4393)
    lat_rad = math.radians(lat)
    ramc = math.radians(lst_deg)

    # Midheaven (MC) ecliptic longitude.
    mc = math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps))) % 360.0

    # Ascendant.
    y = -math.cos(ramc)
    x = math.sin(ramc) * math.cos(eps) + math.tan(lat_rad) * math.sin(eps)
    asc = math.degrees(math.atan2(y, x)) % 360.0

    asc_sign, asc_deg = _longitude_to_sign(asc)
    mc_sign, mc_deg = _longitude_to_sign(mc)

    asc_body = SkyBody(
        name="ascendant",
        ecliptic_longitude=round(asc, 4),
        ecliptic_latitude=0.0,
        sign=asc_sign,
        sign_degree=round(asc_deg, 4),
        is_retrograde=False,
        speed_deg_per_day=0.0,
        dignity=None,
    )
    mc_body = SkyBody(
        name="midheaven",
        ecliptic_longitude=round(mc, 4),
        ecliptic_latitude=0.0,
        sign=mc_sign,
        sign_degree=round(mc_deg, 4),
        is_retrograde=False,
        speed_deg_per_day=0.0,
        dignity=None,
    )
    return asc_body, mc_body


def calculate_sky_chart(
    dt_utc: datetime | None = None,
    lat: float | None = None,
    lon: float | None = None,
    bodies: Iterable[str] = DEFAULT_BODIES,
) -> SkyChart:
    """Compute a deterministic sky chart for given UTC time + optional observer location.

    - dt_utc: datetime in UTC; defaults to now.
    - lat/lon: observer coordinates in degrees; if both provided, ASC/MC are computed.
    """
    if dt_utc is None:
        dt_utc = datetime.now(tz=timezone.utc)
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    eph, ts = _load_ephemeris()

    body_objs = [_make_body(eph, ts, name, dt_utc) for name in bodies]
    aspects = _detect_aspects(body_objs)

    sun = next((b for b in body_objs if b.name == "sun"), None)
    moon = next((b for b in body_objs if b.name == "moon"), None)

    asc = mc = None
    if lat is not None and lon is not None:
        asc, mc = _ascendant_midheaven(eph, ts, dt_utc, lat, lon)

    return SkyChart(
        timestamp_utc=dt_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        bodies=body_objs,
        aspects=aspects,
        sun_sign=sun.sign if sun else "",
        moon_sign=moon.sign if moon else "",
        dominant_element=_dominant_element(body_objs),
        ascendant=asc,
        midheaven=mc,
        ephemeris_source=EPHEMERIS_SOURCE,
    )
