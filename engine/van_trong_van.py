"""Vận trong vận — 30-day forward outlook.

For each day in a window (default 30 days starting today), compute the
day's Mai Hoa NNTT hexagram and score its resonance with the natal
hexagram. Identify the best Vietnamese giờ within each day.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from core.chronos import calculate_chronos_state

from .personal_quai import (
    CompatibilityBreakdown,
    NatalHexagram,
    score_compatibility,
)


# Vietnamese giờ midpoints in 24h clock (each giờ spans 2 hours).
VN_HOUR_MIDPOINTS = {
    "Tý": 0,
    "Sửu": 2,
    "Dần": 4,
    "Mão": 6,
    "Thìn": 8,
    "Tỵ": 10,
    "Ngọ": 12,
    "Mùi": 14,
    "Thân": 16,
    "Dậu": 18,
    "Tuất": 20,
    "Hợi": 22,
}
HOUR_BRANCH_ORDER = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)


@dataclass(frozen=True)
class HourSlotScore:
    branch: str
    midpoint_hour: int
    score: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DayOutlook:
    date_local: str               # YYYY-MM-DD
    day_pillar: str               # Can-Chi day
    lunar_date: str
    solar_term: str
    primary_name: str
    primary_king_wen: int
    primary_binary: str
    day_compatibility: CompatibilityBreakdown
    best_hour_branch: str
    best_hour_midpoint: int
    best_hour_score: int
    worst_hour_branch: str
    worst_hour_score: int
    all_hour_scores: tuple[HourSlotScore, ...]
    # Family integration (optional). Empty when no family provided.
    family_overlay: tuple = ()           # tuple[BranchInteraction, ...]
    family_avg_score: int = 0            # mean of per-member scores
    final_score_with_family: int | None = None  # Blended 70/30 with personal.

    def to_dict(self) -> dict:
        return {
            "date_local": self.date_local,
            "day_pillar": self.day_pillar,
            "lunar_date": self.lunar_date,
            "solar_term": self.solar_term,
            "primary_name": self.primary_name,
            "primary_king_wen": self.primary_king_wen,
            "primary_binary": self.primary_binary,
            "day_compatibility": self.day_compatibility.to_dict(),
            "best_hour_branch": self.best_hour_branch,
            "best_hour_midpoint": self.best_hour_midpoint,
            "best_hour_score": self.best_hour_score,
            "worst_hour_branch": self.worst_hour_branch,
            "worst_hour_score": self.worst_hour_score,
            "all_hour_scores": [s.to_dict() for s in self.all_hour_scores],
            "family_overlay": [i.to_dict() for i in self.family_overlay],
            "family_avg_score": self.family_avg_score,
            "final_score_with_family": self.final_score_with_family,
        }


@dataclass(frozen=True)
class VanTrongVanResult:
    natal: dict
    timezone: str
    start_date: str
    span_days: int
    days: tuple[DayOutlook, ...]

    def to_dict(self) -> dict:
        return {
            "natal": self.natal,
            "timezone": self.timezone,
            "start_date": self.start_date,
            "span_days": self.span_days,
            "days": [d.to_dict() for d in self.days],
        }


def _format_local_iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _compute_one_day(
    natal: NatalHexagram,
    day_date: datetime,
    timezone_name: str,
) -> DayOutlook:
    # Day-level state: anchor at midnight + 12h (Ngọ midpoint).
    noon_dt = day_date.replace(hour=12, minute=0, second=0, microsecond=0)
    noon_state = calculate_chronos_state(_format_local_iso(noon_dt), timezone_name)
    day_compat = score_compatibility(natal, noon_state)

    # Iterate 12 Vietnamese giờ — score at each midpoint.
    hour_scores: list[HourSlotScore] = []
    for branch in HOUR_BRANCH_ORDER:
        midpoint = VN_HOUR_MIDPOINTS[branch]
        slot_dt = day_date.replace(hour=midpoint, minute=0, second=0, microsecond=0)
        slot_state = calculate_chronos_state(_format_local_iso(slot_dt), timezone_name)
        slot_compat = score_compatibility(natal, slot_state)
        hour_scores.append(HourSlotScore(branch=branch, midpoint_hour=midpoint, score=slot_compat.final_score))

    best = max(hour_scores, key=lambda s: s.score)
    worst = min(hour_scores, key=lambda s: s.score)

    return DayOutlook(
        date_local=day_date.strftime("%Y-%m-%d"),
        day_pillar=noon_state.ganzhi.day,
        lunar_date=noon_state.almanac.lunar_date,
        solar_term=noon_state.solar_term.name_vi,
        primary_name="",  # Placeholder — filled below.
        primary_king_wen=0,
        primary_binary="",
        day_compatibility=day_compat,
        best_hour_branch=best.branch,
        best_hour_midpoint=best.midpoint_hour,
        best_hour_score=best.score,
        worst_hour_branch=worst.branch,
        worst_hour_score=worst.score,
        all_hour_scores=tuple(hour_scores),
    )


def _blend_with_family(personal_score: int, family_avg: int) -> int:
    """Blend personal score (0..100) with family avg score (-25..+18) → 0..100."""
    # Map family_avg from [-25, +18] roughly to [0, 100] via linear shift.
    family_normalized = max(0, min(100, 50 + family_avg * 2))  # -25 → 0, +18 → 86, 0 → 50
    blended = round(personal_score * 0.7 + family_normalized * 0.3)
    return max(0, min(100, blended))


def compute_van_trong_van(
    natal: NatalHexagram,
    start_date: datetime | None = None,
    span_days: int = 30,
    timezone_name: str = "Asia/Ho_Chi_Minh",
    family_members: list | None = None,
) -> VanTrongVanResult:
    """Compute span_days days of compatibility outlook starting from start_date.

    Optional `family_members`: a list of FamilyMember. If provided, each day
    includes family_overlay (per-member branch interactions vs day branch)
    and final_score_with_family blending personal 70% + family 30%.
    """
    from zoneinfo import ZoneInfo

    if start_date is None:
        start_date = datetime.now(tz=ZoneInfo(timezone_name)).replace(microsecond=0)
    elif start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=ZoneInfo(timezone_name))

    has_family = bool(family_members)
    if has_family:
        from engine.family_system import compute_family_overlay_for_branch

    days: list[DayOutlook] = []
    cur = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    for _ in range(span_days):
        # Compute primary quẻ at noon for headline display.
        noon_state = calculate_chronos_state(_format_local_iso(cur.replace(hour=12)), timezone_name)
        from core.yi64.derivations.derived_hexagrams import compute_all_derived
        from core.yi64.derivations.mai_hoa_nntt import derive_line_states
        from core.yi64.transforms import lines_to_binary, moving_lines_from_states
        line_states = derive_line_states(noon_state)
        primary_binary = lines_to_binary(line_states)
        moving = moving_lines_from_states(line_states)
        primary = compute_all_derived(primary_binary, moving)["chanh"]

        outlook = _compute_one_day(natal, cur, timezone_name)

        # Family overlay: compare each member's year branch to today's day-pillar branch.
        family_overlay: tuple = ()
        family_avg = 0
        final_with_family = None
        if has_family:
            day_branch = outlook.day_pillar.split()[1] if " " in outlook.day_pillar else ""
            if day_branch:
                family_overlay, family_avg = compute_family_overlay_for_branch(
                    family_members, day_branch
                )
                final_with_family = _blend_with_family(
                    outlook.day_compatibility.final_score, family_avg
                )

        days.append(
            DayOutlook(
                date_local=outlook.date_local,
                day_pillar=outlook.day_pillar,
                lunar_date=outlook.lunar_date,
                solar_term=outlook.solar_term,
                primary_name=primary.name_vi,
                primary_king_wen=primary.king_wen_index,
                primary_binary=primary_binary,
                day_compatibility=outlook.day_compatibility,
                best_hour_branch=outlook.best_hour_branch,
                best_hour_midpoint=outlook.best_hour_midpoint,
                best_hour_score=outlook.best_hour_score,
                worst_hour_branch=outlook.worst_hour_branch,
                worst_hour_score=outlook.worst_hour_score,
                all_hour_scores=outlook.all_hour_scores,
                family_overlay=family_overlay,
                family_avg_score=family_avg,
                final_score_with_family=final_with_family,
            )
        )
        cur = cur + timedelta(days=1)

    return VanTrongVanResult(
        natal={
            "primary_name": natal.primary_name,
            "primary_king_wen": natal.primary_king_wen,
            "primary_binary": natal.primary_binary,
            "upper_trigram": natal.upper_trigram,
            "lower_trigram": natal.lower_trigram,
            "natal_ganzhi": natal.natal_ganzhi,
            "natal_solar_term": natal.natal_solar_term,
        },
        timezone=timezone_name,
        start_date=start_date.strftime("%Y-%m-%d"),
        span_days=span_days,
        days=tuple(days),
    )
