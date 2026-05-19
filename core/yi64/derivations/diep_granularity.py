"""Lá/cánh hoa (diệp) — sub-hexagram per fraction of an hour.

Per Liên Hoa Dịch Số convention, refine the hour-level Mai Hoa quẻ down
to "diệp" — petal-level moments. The default is 5 diệp per giờ (each
giờ ≈ 120 minutes Vietnamese; default project hour = 60 min, so 5 diệp
of 12 min each).

For each diệp, recompute Mai Hoa NNTT but with diệp index folded into
the trigram + moving-line arithmetic. This produces 5 distinct sub-quẻ
per hour while keeping all values deterministic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from core.chronos import ChronosState, calculate_chronos_state
from core.hexagram import TRIGRAM_BITS

from .derived_hexagrams import compute_all_derived, derived_summary_dict
from .mai_hoa_nntt import (
    METHOD_ID,
    SOURCE_REF,
    TIEN_THIEN_TRIGRAMS,
    _branch_idx_from_pillar,
    _mod6,
    _mod8,
    _parse_lunar_date,
)


DEFAULT_DIEP_COUNT = 5
DEFAULT_DIEP_MINUTES = 12  # 60 / 5


@dataclass(frozen=True)
class DiepEntry:
    diep_index: int                  # 0-based within the hour
    minute_start: int                # 0..59 within the giờ
    minute_end: int                  # 0..59 within the giờ
    upper_num: int
    upper_trigram: str
    lower_num: int
    lower_trigram: str
    moving_line: int
    primary_binary: str
    primary_name: str
    primary_king_wen: int
    derived_hexagrams: dict          # {chanh, ho, bien, giao, phuc, bao}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DiepSequence:
    method_id: str
    source_ref: str
    base_state: dict                 # year/month/day/hour info
    diep_count: int
    diep_minutes: int
    entries: tuple[DiepEntry, ...]

    def to_dict(self) -> dict:
        return {
            "method_id": self.method_id,
            "source_ref": self.source_ref + " (mở rộng diệp granularity)",
            "base_state": self.base_state,
            "diep_count": self.diep_count,
            "diep_minutes": self.diep_minutes,
            "entries": [e.to_dict() for e in self.entries],
        }


def _compute_diep_entry(
    year_branch_idx: int,
    lunar_month: int,
    lunar_day: int,
    hour_branch_idx: int,
    diep_index: int,
    diep_minutes: int,
) -> DiepEntry:
    """Compute one diệp's Mai Hoa quẻ + derived charts.

    Modifier: add (diep_index + 1) into the upper/lower/moving sums so
    diệp 0 ≠ raw NNTT, ensuring all 5 diệp differ.
    """
    diep_offset = diep_index + 1
    upper_num = _mod8(year_branch_idx + lunar_month + lunar_day + diep_offset)
    lower_num = _mod8(
        year_branch_idx + lunar_month + lunar_day + hour_branch_idx + diep_offset
    )
    moving_line = _mod6(
        year_branch_idx + lunar_month + lunar_day + hour_branch_idx + diep_offset
    )

    upper_trigram = TIEN_THIEN_TRIGRAMS[upper_num - 1]
    lower_trigram = TIEN_THIEN_TRIGRAMS[lower_num - 1]
    primary_binary = f"{TRIGRAM_BITS[upper_trigram]}{TRIGRAM_BITS[lower_trigram]}"

    derived = compute_all_derived(primary_binary, (moving_line,))
    primary = derived["chanh"]

    return DiepEntry(
        diep_index=diep_index,
        minute_start=diep_index * diep_minutes,
        minute_end=min((diep_index + 1) * diep_minutes - 1, 59),
        upper_num=upper_num,
        upper_trigram=upper_trigram,
        lower_num=lower_num,
        lower_trigram=lower_trigram,
        moving_line=moving_line,
        primary_binary=primary_binary,
        primary_name=primary.name_vi,
        primary_king_wen=primary.king_wen_index,
        derived_hexagrams=derived_summary_dict(primary_binary, (moving_line,)),
    )


def compute_diep_sequence(
    state: ChronosState,
    diep_count: int = DEFAULT_DIEP_COUNT,
) -> DiepSequence:
    """Given an hourly chronos state, expand into N diệp sub-hexagrams."""
    if diep_count < 1 or diep_count > 12:
        raise ValueError("diep_count must be between 1 and 12")
    if 60 % diep_count != 0:
        raise ValueError("diep_count must divide 60 evenly (1, 2, 3, 4, 5, 6, 10, 12)")

    year_branch_idx = _branch_idx_from_pillar(state.ganzhi.year)
    lunar_day, lunar_month = _parse_lunar_date(state.almanac.lunar_date)
    hour_branch_idx = _branch_idx_from_pillar(state.ganzhi.hour)

    diep_minutes = 60 // diep_count
    entries = tuple(
        _compute_diep_entry(
            year_branch_idx,
            lunar_month,
            lunar_day,
            hour_branch_idx,
            i,
            diep_minutes,
        )
        for i in range(diep_count)
    )

    base_state = {
        "year_pillar": state.ganzhi.year,
        "year_branch_idx": year_branch_idx,
        "lunar_date": state.almanac.lunar_date,
        "hour_pillar": state.ganzhi.hour,
        "hour_branch_idx": hour_branch_idx,
    }

    return DiepSequence(
        method_id=METHOD_ID,
        source_ref=SOURCE_REF,
        base_state=base_state,
        diep_count=diep_count,
        diep_minutes=diep_minutes,
        entries=entries,
    )


def compute_diep_sequence_for_datetime(
    datetime_local: str | None,
    timezone_name: str = "Asia/Ho_Chi_Minh",
    diep_count: int = DEFAULT_DIEP_COUNT,
) -> DiepSequence:
    state = calculate_chronos_state(datetime_local, timezone_name)
    return compute_diep_sequence(state, diep_count=diep_count)
