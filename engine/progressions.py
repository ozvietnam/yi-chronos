"""Secondary Progressions Engine.

Symbolic technique: 1 day after birth = 1 year of life.

For age N years, the "progressed chart" is the actual sky on day N
after birth. Progressed Sun moves ~1°/year; progressed Moon ~13°/year.
The Moon's progressed sign changes every ~2.5 years and is the primary
emotional/inner-state arc Western astrology reads from this technique.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from engine.sky import (
    BODY_EPHEMERIS_KEYS,
    SkyChart,
    _ecliptic_longitude,
    _load_ephemeris,
    _longitude_to_sign,
    calculate_sky_chart,
)


def _progressed_dt(birth_dt: datetime, age_years: float) -> datetime:
    return birth_dt + timedelta(days=age_years)


def compute_progressed_chart(
    birth_dt: datetime,
    at_age_years: float,
    lat: float | None = None,
    lon: float | None = None,
) -> SkyChart:
    """Return the progressed chart at given age (1 day = 1 year)."""
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)
    return calculate_sky_chart(_progressed_dt(birth_dt, at_age_years), lat=lat, lon=lon)


@dataclass
class ProgressedMoonPhase:
    age_start: float
    age_end: float | None
    sign: str
    date_start_utc: str
    date_end_utc: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def compute_progressed_moon_timeline(birth_dt: datetime, span_years: int = 90) -> list[ProgressedMoonPhase]:
    """Track the progressed Moon's sign across the lifespan."""
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()
    moon_key = BODY_EPHEMERIS_KEYS["moon"]

    def moon_sign_at(age_years: float) -> tuple[str, float]:
        progressed = _progressed_dt(birth_dt, age_years)
        lon, _ = _ecliptic_longitude(eph, moon_key, ts.from_datetime(progressed))
        return _longitude_to_sign(lon)

    phases: list[ProgressedMoonPhase] = []
    age_step = 0.083  # ~1 month of life sampling
    age = 0.0
    cur_sign, _ = moon_sign_at(age)
    phase_start_age = 0.0

    while age < span_years:
        next_age = age + age_step
        next_sign, _ = moon_sign_at(next_age)
        if next_sign != cur_sign:
            # Bisect within (age, next_age) to find exact crossing.
            lo, hi = age, next_age
            for _ in range(30):
                mid = (lo + hi) / 2
                mid_sign, _ = moon_sign_at(mid)
                if mid_sign == cur_sign:
                    lo = mid
                else:
                    hi = mid
            cross_age = (lo + hi) / 2
            life_date = birth_dt + timedelta(days=365.2422 * cross_age)
            phase_end_iso = life_date.replace(microsecond=0).isoformat().replace("+00:00", "Z")
            phase_start_iso = (birth_dt + timedelta(days=365.2422 * phase_start_age)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            phases.append(
                ProgressedMoonPhase(
                    age_start=round(phase_start_age, 3),
                    age_end=round(cross_age, 3),
                    sign=cur_sign,
                    date_start_utc=phase_start_iso,
                    date_end_utc=phase_end_iso,
                )
            )
            phase_start_age = cross_age
            cur_sign = next_sign
        age = next_age

    # Final open-ended phase.
    phase_start_iso = (birth_dt + timedelta(days=365.2422 * phase_start_age)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    phases.append(
        ProgressedMoonPhase(
            age_start=round(phase_start_age, 3),
            age_end=None,
            sign=cur_sign,
            date_start_utc=phase_start_iso,
            date_end_utc=None,
        )
    )
    return phases
