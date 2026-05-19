"""Đại Vận (大運) — 10-year luck cycles + Tiểu Vận (小運) yearly.

Classical 子平 rule:
- Đại Vận starts from the Month pillar (the canonical "vận khởi" pillar).
- Direction:
    * Dương Nam (yang-year male) or Âm Nữ (yin-year female) → walk FORWARD
      through the 60-jiazi cycle starting after Month pillar.
    * Âm Nam (yin-year male) or Dương Nữ (yang-year female) → walk BACKWARD.
- Starting age: based on days between birth and the nearest tiết khí (solar term).
  Forward direction → days to NEXT tiết khí; Backward → days to PREVIOUS.
  Rule of thumb: every 3 days = 1 year. So starting_age = round(days / 3).
- Each Đại Vận = 10 years.
- 8 cycles cover ~80 years.

Tiểu Vận (Lesser Cycle):
- A yearly stem-branch starting from Tý for the first lunar year of life.
- Less commonly used than Đại Vận; we include it as a secondary layer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from .constants import EARTHLY_BRANCHES, HEAVENLY_STEMS, STEM_POLARITY


# 60-jiazi cycle (Thiên Can + Địa Chi pairs)
def _build_jiazi_cycle() -> tuple[tuple[str, str], ...]:
    return tuple((HEAVENLY_STEMS[i % 10], EARTHLY_BRANCHES[i % 12]) for i in range(60))


JIAZI_CYCLE: tuple[tuple[str, str], ...] = _build_jiazi_cycle()


def _jiazi_index(stem: str, branch: str) -> int:
    """Find index 0..59 in the 60-jiazi cycle for a given stem+branch combo."""
    for i, (s, b) in enumerate(JIAZI_CYCLE):
        if s == stem and b == branch:
            return i
    raise ValueError(f"Invalid stem-branch combo: {stem} {branch}")


def _next_jiazi(stem: str, branch: str, direction: int) -> tuple[str, str]:
    """Get the next or previous stem-branch in the 60-cycle.

    direction: +1 = forward, -1 = backward.
    """
    idx = _jiazi_index(stem, branch)
    new_idx = (idx + direction) % 60
    return JIAZI_CYCLE[new_idx]


def determine_direction(year_stem: str, gender: str) -> int:
    """Return +1 (forward) or -1 (backward) for Đại Vận walk.

    - Dương nam (yang year + male) → forward
    - Âm nữ (yin year + female) → forward
    - Âm nam (yin year + male) → backward
    - Dương nữ (yang year + female) → backward
    """
    year_is_yang = STEM_POLARITY[year_stem] == "dương"
    if (year_is_yang and gender == "nam") or (not year_is_yang and gender == "nữ"):
        return +1
    return -1


@dataclass(frozen=True)
class DaiVan:
    """One 10-year Đại Vận cycle."""

    cycle_index: int                # 1-based: 1st, 2nd, ...
    stem: str
    branch: str
    start_age: int
    end_age: int

    def to_dict(self) -> dict:
        return asdict(self)


def compute_dai_van(
    *,
    month_pillar_stem: str,
    month_pillar_branch: str,
    year_stem: str,
    gender: str,
    starting_age: int,
    num_cycles: int = 8,
) -> list[dict]:
    """Compute Đại Vận trajectory: list of 8 cycles starting at `starting_age`.

    Each cycle stem+branch is the NEXT (or previous) jiazi from the Month pillar.
    The first Đại Vận stem-branch is the jiazi AFTER (or BEFORE) the month pillar.
    """
    direction = determine_direction(year_stem, gender)
    cycles: list[DaiVan] = []
    current_stem, current_branch = month_pillar_stem, month_pillar_branch
    current_age = starting_age
    for i in range(num_cycles):
        # Walk to next jiazi in direction.
        current_stem, current_branch = _next_jiazi(current_stem, current_branch, direction)
        cycles.append(DaiVan(
            cycle_index=i + 1,
            stem=current_stem,
            branch=current_branch,
            start_age=current_age,
            end_age=current_age + 9,
        ))
        current_age += 10
    return [c.to_dict() for c in cycles]


def estimate_starting_age(
    birth_datetime: datetime,
    direction: int,
    solar_term_dates_around_birth: list[datetime] | None = None,
) -> int:
    """Estimate Đại Vận starting age via the "3 days = 1 year" rule.

    Args:
        birth_datetime: native birth.
        direction: +1 → count days to next tiết khí; -1 → count days to previous.
        solar_term_dates_around_birth: list of nearby tiết khí dates. If None,
            use a rough fallback (default starting age 3 for forward, 7 for backward).

    Returns the integer age (1..10) when Đại Vận first cycle begins.
    """
    if not solar_term_dates_around_birth:
        # Defensive fallback — typical values per Vietnamese popular tradition.
        return 3 if direction > 0 else 7

    if direction > 0:
        future = [d for d in solar_term_dates_around_birth if d > birth_datetime]
        if not future:
            return 3
        delta_days = (min(future) - birth_datetime).total_seconds() / 86400
    else:
        past = [d for d in solar_term_dates_around_birth if d <= birth_datetime]
        if not past:
            return 7
        delta_days = (birth_datetime - max(past)).total_seconds() / 86400

    age = round(delta_days / 3)
    return max(1, min(10, age))   # clamp to 1..10


def compute_tieu_van(year_branch: str, gender: str, span: int = 96) -> list[dict]:
    """Compute Tiểu Vận (yearly cycle).

    Convention: starts at Tỵ for boys (dương) and Thân for girls (âm),
    advances by 1 each year. Cycle repeats every 12 years.

    v2 (2026-05-12, critique #9): span extended 12 → 96 so adult ages are covered.
    """
    start_branch = "Tỵ" if gender == "nam" else "Thân"
    start_idx = EARTHLY_BRANCHES.index(start_branch)
    out: list[dict] = []
    for i in range(span):
        idx = (start_idx + i) % 12
        out.append({
            "year_index": i + 1,
            "branch": EARTHLY_BRANCHES[idx],
            "age": i + 1,
        })
    return out


def get_tieu_van_for_age(tieu_van: list[dict], age: int) -> dict | None:
    """Return the Tiểu Vận entry for a specific age, or None if out of range."""
    for entry in tieu_van:
        if entry["age"] == age:
            return entry
    return None


def build_dai_van_chart(
    *,
    pillars: dict,
    year_stem: str,
    gender: str,
    birth_datetime: datetime | None = None,
) -> dict:
    """Top-level Đại Vận chart builder.

    If `birth_datetime` is provided, computes the starting age via the
    canonical "3 days = 1 year" rule against real tiết khí dates.
    Otherwise falls back to the rough default (3 thuận / 7 nghịch).
    """
    direction = determine_direction(year_stem, gender)

    if birth_datetime is not None:
        # Use accurate tiết khí computation.
        from .starting_age import compute_starting_age
        sa_info = compute_starting_age(birth_datetime, direction)
        starting_age = sa_info["starting_age"]
        estimation_method = sa_info["estimation_method"]
        distance_days = sa_info["distance_days"]
        reference_tiet_khi_date = sa_info["reference_tiet_khi_date"]
        reference_tiet_khi_longitude = sa_info["reference_tiet_khi_longitude"]
    else:
        starting_age = 3 if direction > 0 else 7
        estimation_method = "rough_default"
        distance_days = None
        reference_tiet_khi_date = None
        reference_tiet_khi_longitude = None

    cycles = compute_dai_van(
        month_pillar_stem=pillars["month"]["stem"],
        month_pillar_branch=pillars["month"]["branch"],
        year_stem=year_stem,
        gender=gender,
        starting_age=starting_age,
    )

    tieu_van = compute_tieu_van(pillars["year"]["branch"], gender)

    # ─── v2: current Đại Vận pointer (critique #17 from bat_tu sage) ────────
    # Compute current age (in completed years) from birth → today.
    current_dai_van: dict | None = None
    next_dai_van: dict | None = None
    second_next_dai_van: dict | None = None
    current_age: int | None = None
    if birth_datetime is not None:
        from datetime import datetime as _dt
        from zoneinfo import ZoneInfo as _ZI

        now = _dt.now(_ZI("Asia/Ho_Chi_Minh"))
        # birth_datetime may be naive — make aware
        b = birth_datetime
        if b.tzinfo is None:
            b = b.replace(tzinfo=_ZI("Asia/Ho_Chi_Minh"))
        years_elapsed = (now - b).days / 365.25
        current_age = int(years_elapsed)

        for i, c in enumerate(cycles):
            if c["start_age"] <= current_age <= c["end_age"]:
                current_dai_van = {**c, "tuổi_hiện_tại": current_age}
                if i + 1 < len(cycles):
                    next_dai_van = cycles[i + 1]
                if i + 2 < len(cycles):
                    second_next_dai_van = cycles[i + 2]
                break

    return {
        "direction": direction,
        "direction_label": "thuận" if direction > 0 else "nghịch",
        "starting_age": starting_age,
        "starting_age_estimation": estimation_method,
        "distance_days_to_reference_tiet_khi": distance_days,
        "reference_tiet_khi_date": reference_tiet_khi_date,
        "reference_tiet_khi_longitude": reference_tiet_khi_longitude,
        "cycles": cycles,
        "tieu_van": tieu_van,
        # v2 pointer fields:
        "current_age": current_age,
        "current_dai_van": current_dai_van,
        "next_dai_van": next_dai_van,
        "second_next_dai_van": second_next_dai_van,
        "current_tieu_van": get_tieu_van_for_age(tieu_van, current_age) if current_age else None,
        "starting_age_note": (
            "Tuổi bắt đầu vận = số ngày từ sinh đến tiết khí kế tiếp (thuận) hoặc "
            "tiết khí trước (nghịch), chia 3 (quy tắc 3 ngày = 1 năm), kết quả ∈ [1,10]."
            if estimation_method == "tiet_khi_3day_rule"
            else "Tuổi bắt đầu vận dùng mặc định (3 thuận / 7 nghịch) — cần truyền birth_datetime để tính chính xác."
        ),
    }
