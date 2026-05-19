"""Tứ Trụ — extract 4 pillars from a birth datetime via core.chronos.

Each pillar = (Thiên Can, Địa Chi) pair. Day Master = stem of the Day pillar.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.chronos import calculate_chronos_state

from .constants import (
    BRANCH_ELEMENT,
    BRANCH_HIDDEN_STEMS,
    BRANCH_POLARITY,
    PILLAR_DOMAIN,
    PILLAR_NAMES_VI,
    STEM_ELEMENT,
    STEM_POLARITY,
)


@dataclass(frozen=True)
class Pillar:
    """One trụ (pillar) — stem + branch + derived metadata."""

    position: str              # 'year' / 'month' / 'day' / 'hour'
    position_vi: str           # Localized label
    domain_vi: str             # Life domain
    stem: str                  # Thiên Can
    branch: str                # Địa Chi
    stem_element: str
    branch_element: str
    stem_polarity: str         # 'dương' / 'âm'
    branch_polarity: str
    hidden_stems: list[str]    # 地支藏干 — stems inside the branch

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_ganzhi(combined: str) -> tuple[str, str]:
    """Split a 'Stem-Branch' string like 'Giáp Tý' into (stem, branch).

    The chronos output uses space-separated form.
    """
    parts = combined.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Cannot parse GanZhi: {combined!r}")
    return parts[0], parts[1]


def _build_pillar(position: str, ganzhi_combined: str) -> Pillar:
    stem, branch = _parse_ganzhi(ganzhi_combined)
    if stem not in STEM_ELEMENT:
        raise ValueError(f"Unknown stem {stem!r} in {ganzhi_combined!r}")
    if branch not in BRANCH_ELEMENT:
        raise ValueError(f"Unknown branch {branch!r} in {ganzhi_combined!r}")
    return Pillar(
        position=position,
        position_vi=PILLAR_NAMES_VI[position],
        domain_vi=PILLAR_DOMAIN[position],
        stem=stem,
        branch=branch,
        stem_element=STEM_ELEMENT[stem],
        branch_element=BRANCH_ELEMENT[branch],
        stem_polarity=STEM_POLARITY[stem],
        branch_polarity=BRANCH_POLARITY[branch],
        hidden_stems=list(BRANCH_HIDDEN_STEMS[branch]),
    )


def extract_tu_tru(birth_datetime_local: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Extract Tứ Trụ from a birth datetime string.

    Returns a dict with 4 Pillar dicts + the Day Master stem.
    """
    chronos = calculate_chronos_state(birth_datetime_local, timezone)
    gz = chronos.ganzhi

    year_pillar = _build_pillar("year", gz.year)
    month_pillar = _build_pillar("month", gz.month)
    day_pillar = _build_pillar("day", gz.day)
    hour_pillar = _build_pillar("hour", gz.hour)

    return {
        "birth_datetime_local": birth_datetime_local,
        "timezone": timezone,
        "ganzhi_raw": {
            "year": gz.year,
            "month": gz.month,
            "day": gz.day,
            "hour": gz.hour,
        },
        "pillars": {
            "year": year_pillar.to_dict(),
            "month": month_pillar.to_dict(),
            "day": day_pillar.to_dict(),
            "hour": hour_pillar.to_dict(),
        },
        "day_master": {
            "stem": day_pillar.stem,
            "element": day_pillar.stem_element,
            "polarity": day_pillar.stem_polarity,
        },
        "solar_term": {
            "id": chronos.solar_term.id,
            "name_vi": chronos.solar_term.name_vi,
        },
    }
