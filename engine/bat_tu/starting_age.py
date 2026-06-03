"""Accurate Đại Vận starting-age via real tiết khí dates.

Classical 子平 rule (起運法):
- For thuận (forward) direction: count days from BIRTH to the NEXT 節 (tiết lệnh).
- For nghịch (backward) direction: count days from PREVIOUS 節 to BIRTH.
- 3 days = 1 year; final result clamped to [1, 10].

Implementation:
- Uses `core.chronos.estimate_solar_longitude` as the inverse-solvable model.
- 節 (tiết lệnh — the 12 "establishment" solar terms) are at longitude 15 + 30k
  (k=0..11): 15,45,75,105,135,165,195,225,255,285,315,345°.
- 中氣 (trung khí — the 12 secondary terms) are at 0+30k: 0,30,60,90,…,330°.
- Khởi vận uses ONLY 節, NOT 中氣 (step = 30°, origin = 15°).

This v2 algorithm replaces the rough default (3 thuận / 7 nghịch) used in v1.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import floor as _floor

from core.chronos import estimate_solar_longitude


# Tropical year (used inside estimate_solar_longitude as well).
TROPICAL_YEAR_DAYS = 365.2422


def _normalize_longitude(deg: float) -> float:
    """Wrap to [0, 360)."""
    return deg % 360.0


def _date_when_longitude_is(target_longitude: float, near_dt: datetime) -> datetime:
    """Solve for the datetime within a few days of `near_dt` where solar longitude
    equals `target_longitude`.

    Uses bisection: solar longitude advances ~0.985° per day.
    """
    # Search window: ±30 days from near_dt.
    low = near_dt - timedelta(days=30)
    high = near_dt + timedelta(days=30)

    def diff(dt: datetime) -> float:
        """Return signed angular distance from current longitude to target,
        wrapped to (-180, 180]."""
        cur = estimate_solar_longitude(dt)
        d = (target_longitude - cur) % 360
        if d > 180:
            d -= 360
        return d

    # If target is far from search window, expand once.
    if diff(low) * diff(high) > 0:
        # Same sign across whole window — expand.
        low = near_dt - timedelta(days=180)
        high = near_dt + timedelta(days=180)
        if diff(low) * diff(high) > 0:
            # Still no crossing → fall back to direct algebraic estimate.
            return _algebraic_estimate(target_longitude, near_dt)

    # Bisect.
    for _ in range(60):    # 60 iterations → microsecond precision
        mid = low + (high - low) / 2
        if diff(low) * diff(mid) <= 0:
            high = mid
        else:
            low = mid
        if (high - low).total_seconds() < 60:   # ~1 minute precision
            break
    return low + (high - low) / 2


def _algebraic_estimate(target_longitude: float, near_dt: datetime) -> datetime:
    """Fallback: use the closed-form inverse of estimate_solar_longitude.

    Formula:
        longitude = ((elapsed_days_in_year - 79) / 365.2422 * 360) % 360
        → elapsed_days = (longitude / 360 * 365.2422) + 79
    """
    # Find the year that gives the closest result.
    base = datetime(near_dt.year, 1, 1, tzinfo=near_dt.tzinfo)
    elapsed = (target_longitude / 360.0) * TROPICAL_YEAR_DAYS + 79.0
    if elapsed >= TROPICAL_YEAR_DAYS:
        elapsed -= TROPICAL_YEAR_DAYS
    candidate = base + timedelta(days=elapsed)
    # If candidate is far from near_dt, try adjusting year ±1.
    if (candidate - near_dt).days > 200:
        candidate -= timedelta(days=int(TROPICAL_YEAR_DAYS))
    elif (near_dt - candidate).days > 200:
        candidate += timedelta(days=int(TROPICAL_YEAR_DAYS))
    return candidate


def next_tiet_khi_date(birth_dt: datetime) -> datetime:
    """Find the next 節 (tiết lệnh, longitude 15+30k) AFTER birth.

    節 are at 15,45,75,105,...,345° (step 30°, NOT 15°).
    中氣 at 0,30,60,...,330° are excluded from khởi vận calculation.
    """
    cur_lon = estimate_solar_longitude(birth_dt)
    # Smallest 節 longitude strictly greater than cur_lon.
    # 節 = 15 + 30k → k = floor((cur_lon - 15) / 30) + 1
    k = _floor((cur_lon - 15) / 30) + 1
    next_boundary = (15 + 30 * k) % 360
    candidate = _date_when_longitude_is(next_boundary, birth_dt + timedelta(days=15))
    if candidate <= birth_dt:
        next_boundary = (next_boundary + 30) % 360
        candidate = _date_when_longitude_is(next_boundary, birth_dt + timedelta(days=35))
    return candidate


def prev_tiet_khi_date(birth_dt: datetime) -> datetime:
    """Find the previous 節 BEFORE birth.

    節 are at 15,45,75,105,...,345° (step 30°).
    """
    cur_lon = estimate_solar_longitude(birth_dt)
    # Largest 節 longitude strictly less than cur_lon.
    # 節 = 15 + 30k → k = floor((cur_lon - 15) / 30)
    k = _floor((cur_lon - 15) / 30)
    prev_boundary = (15 + 30 * k) % 360
    if abs(cur_lon - prev_boundary) < 0.001:
        # Birth IS exactly on a 節 → use the one before.
        prev_boundary = (prev_boundary - 30) % 360
    candidate = _date_when_longitude_is(prev_boundary, birth_dt - timedelta(days=15))
    if candidate >= birth_dt:
        prev_boundary = (prev_boundary - 30) % 360
        candidate = _date_when_longitude_is(prev_boundary, birth_dt - timedelta(days=35))
    return candidate


def compute_starting_age(birth_dt: datetime, direction: int) -> dict:
    """Compute Đại Vận starting age using the canonical 3-day-1-year rule.

    Args:
        birth_dt: birth datetime (timezone-aware).
        direction: +1 for thuận (forward), -1 for nghịch (backward).

    Returns:
        {
            'starting_age': int (clamped to 1..10),
            'distance_days': float,
            'reference_tiet_khi_date': ISO string,
            'estimation_method': 'tiet_khi_3day_rule',
        }
    """
    if direction > 0:
        ref = next_tiet_khi_date(birth_dt)
        delta_seconds = (ref - birth_dt).total_seconds()
    else:
        ref = prev_tiet_khi_date(birth_dt)
        delta_seconds = (birth_dt - ref).total_seconds()

    distance_days = delta_seconds / 86400
    age = round(distance_days / 3)
    age = max(1, min(10, age))

    return {
        "starting_age": age,
        "distance_days": round(distance_days, 2),
        "reference_tiet_khi_date": ref.isoformat() if ref else None,
        "reference_tiet_khi_longitude": round(estimate_solar_longitude(ref), 2) if ref else None,
        "estimation_method": "tiet_khi_3day_rule",
    }
