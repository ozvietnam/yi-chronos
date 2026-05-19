"""Returns Engine.

Computes Solar Returns (and optionally Lunar Returns) — the moments when
the Sun (or Moon) returns to its exact natal ecliptic longitude.

Each Solar Return marks the start of a "personal year" in Western astrology
and produces a chart that is read alongside the natal chart.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from engine.sky import (
    BODY_EPHEMERIS_KEYS,
    SkyChart,
    _ecliptic_longitude,
    _load_ephemeris,
    calculate_sky_chart,
)


def _signed_diff(a: float, b: float) -> float:
    return (a - b + 540.0) % 360.0 - 180.0


def _bisect_to_target(eph, ts, body_key: str, target: float, t_low: datetime, t_high: datetime, max_iter: int = 50) -> datetime:
    def diff_at(dt: datetime) -> float:
        lon, _ = _ecliptic_longitude(eph, body_key, ts.from_datetime(dt))
        return _signed_diff(lon, target)

    lo, hi = t_low, t_high
    d_lo = diff_at(lo)
    for _ in range(max_iter):
        if (hi - lo).total_seconds() < 60:
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


@dataclass
class SolarReturn:
    age: int
    date_utc: str
    chart: SkyChart

    def to_dict(self) -> dict:
        return {
            "age": self.age,
            "date_utc": self.date_utc,
            "chart": self.chart.to_dict(),
        }


def compute_solar_returns(
    birth_dt: datetime,
    lat: float | None = None,
    lon: float | None = None,
    span_years: int = 90,
) -> list[SolarReturn]:
    """Compute exact Solar Return moments and charts for each year of life."""
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()
    sun_key = BODY_EPHEMERIS_KEYS["sun"]
    natal_sun_lon, _ = _ecliptic_longitude(eph, sun_key, ts.from_datetime(birth_dt))

    out: list[SolarReturn] = []
    for age in range(0, span_years + 1):
        # Approximate return = birth + age * tropical year.
        approx = birth_dt + timedelta(days=365.2422 * age)
        # Search window ±3 days catches even worst-case offsets.
        t_low = approx - timedelta(days=3)
        t_high = approx + timedelta(days=3)
        exact = _bisect_to_target(eph, ts, sun_key, natal_sun_lon, t_low, t_high)
        chart = calculate_sky_chart(dt_utc=exact, lat=lat, lon=lon)
        out.append(
            SolarReturn(
                age=age,
                date_utc=exact.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                chart=chart,
            )
        )
    return out
