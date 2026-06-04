"""Generate full bát tự per hour candidate by reusing engine.bat_tu cast."""
from __future__ import annotations

from .engine import generate_candidates_for_range
from .rules.branches import HOUR_RANGES


def _chi_midpoint_hour(chi: str) -> int:
    """Return a representative hour inside the chi range.

    Tý spans 23-1h → return 0 (chính Tý, 00:00). Others → start + 1 (e.g. Mão 5-7 → 6).

    KNOWN LIMITATION (#25): under the project's 早子時 convention the Tý window is NOT
    day-pillar-stable — 23:00 rolls to the next day (e.g. Nhâm Thìn) while 00:00–01:00
    stays on the current day (e.g. Tân Mão). A single midpoint (00:00) represents only
    the 正子 half. The root morning-hour bug (#12) is fixed (chronos now uses sxtwl, so
    00:00–06:59 candidates are correct); fully distinguishing Tý-sớm vs Tý-muộn would
    need a 13th candidate — tracked as a quiz-model follow-up.
    """
    start, end = HOUR_RANGES[chi]
    if start > end:  # Tý wraps midnight
        return 0
    return start + 1


def build_candidates(
    birth_date: str,
    timezone: str,
    hour_range: tuple[int, int] | None,
    gender: str = "nam",
) -> list[dict]:
    """Build candidate list with full pillars from real bat_tu cast.

    Args:
        birth_date: 'YYYY-MM-DD'
        timezone: e.g. 'Asia/Ho_Chi_Minh'
        hour_range: (start, end) inclusive, or None for all 12 chi.
        gender: 'nam' | 'nữ' (used by bat_tu engine for đại vận direction)

    Returns:
        [{"chi": "Mão", "pillars": {year/month/day/hour: {stem, branch}}}, ...]
    """
    if hour_range is None:
        chis = list(HOUR_RANGES.keys())
    else:
        chis = generate_candidates_for_range(hour_range[0], hour_range[1])

    # Lazy import — keeps tests not requiring bat_tu fast for the rules-only paths.
    from engine.bat_tu.cast import cast_bat_tu

    out = []
    for chi in chis:
        midpoint = _chi_midpoint_hour(chi)
        birth_dt = f"{birth_date}T{midpoint:02d}:00:00"
        chart = cast_bat_tu(
            birth_datetime_local=birth_dt,
            timezone=timezone,
            gender=gender,
        )
        tu_tru = chart["tu_tru"]["pillars"]
        out.append({
            "chi": chi,
            "pillars": {
                "year":  {"stem": tu_tru["year"]["stem"],  "branch": tu_tru["year"]["branch"]},
                "month": {"stem": tu_tru["month"]["stem"], "branch": tu_tru["month"]["branch"]},
                "day":   {"stem": tu_tru["day"]["stem"],   "branch": tu_tru["day"]["branch"]},
                "hour":  {"stem": tu_tru["hour"]["stem"],  "branch": tu_tru["hour"]["branch"]},
            },
        })
    return out
