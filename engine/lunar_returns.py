"""Lunar Returns Engine.

Moon returns to its natal ecliptic longitude every ~27.32 days (sidereal
month). Each return marks the start of a "personal month" — granular
mood/inner-state arc.
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


SIDEREAL_MONTH_DAYS = 27.32166


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
class LunarReturn:
    index: int
    date_utc: str
    chart: SkyChart

    def to_dict(self) -> dict:
        return {"index": self.index, "date_utc": self.date_utc, "chart": self.chart.to_dict()}


def compute_lunar_returns(
    birth_dt: datetime,
    from_dt: datetime | None = None,
    count: int = 12,
    lat: float | None = None,
    lon: float | None = None,
) -> list[LunarReturn]:
    """Compute the next `count` lunar returns starting at or after `from_dt`."""
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    else:
        birth_dt = birth_dt.astimezone(timezone.utc)

    if from_dt is None:
        from_dt = datetime.now(tz=timezone.utc)
    elif from_dt.tzinfo is None:
        from_dt = from_dt.replace(tzinfo=timezone.utc)
    else:
        from_dt = from_dt.astimezone(timezone.utc)

    eph, ts = _load_ephemeris()
    moon_key = BODY_EPHEMERIS_KEYS["moon"]
    natal_moon_lon, _ = _ecliptic_longitude(eph, moon_key, ts.from_datetime(birth_dt))

    # Index of the lunar return cycle right before from_dt.
    elapsed_days = (from_dt - birth_dt).total_seconds() / 86400.0
    start_index = max(0, int(elapsed_days / SIDEREAL_MONTH_DAYS))

    results: list[LunarReturn] = []
    idx = start_index
    while len(results) < count:
        approx = birth_dt + timedelta(days=SIDEREAL_MONTH_DAYS * idx)
        # Search window ±2 days because Moon's true period varies up to ~6 hours/cycle.
        t_low = approx - timedelta(days=2)
        t_high = approx + timedelta(days=2)
        exact = _bisect_to_target(eph, ts, moon_key, natal_moon_lon, t_low, t_high)
        if exact >= from_dt:
            chart = calculate_sky_chart(dt_utc=exact, lat=lat, lon=lon)
            results.append(
                LunarReturn(
                    index=idx,
                    date_utc=exact.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    chart=chart,
                )
            )
        idx += 1
    return results
