"""Mai Hoa Dịch Số — Niên-Nguyệt-Nhật-Thời derivation.

Source: Thiệu Khang Tiết, "Mai Hoa Dịch Số Toàn Tập", quyển 1, chương "Niên Nguyệt Nhật Thời Khởi Quái Pháp".

Rules:
- Năm = 地支 of năm (1=Tý, 2=Sửu, ..., 12=Hợi).
- Tháng = âm lịch tháng (1-12; for leap months, use the regular month number).
- Ngày = âm lịch ngày (1-30).
- Giờ = 地支 of giờ (1=Tý, ..., 12=Hợi).
- Thượng quái = (Năm + Tháng + Ngày) mod 8; if 0 → 8.
- Hạ quái = (Năm + Tháng + Ngày + Giờ) mod 8; if 0 → 8.
- Hào động = (Năm + Tháng + Ngày + Giờ) mod 6; if 0 → 6.
- Trigram order is Tiên Thiên (Phục Hy): 1.Càn, 2.Đoài, 3.Ly, 4.Chấn, 5.Tốn, 6.Khảm, 7.Cấn, 8.Khôn.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.chronos import ChronosState
from core.hexagram import TRIGRAM_BITS

from ..model import LineState, MotionState, Polarity


TIEN_THIEN_TRIGRAMS = (
    "Càn",   # 1
    "Đoài",  # 2
    "Ly",    # 3
    "Chấn",  # 4
    "Tốn",   # 5
    "Khảm",  # 6
    "Cấn",   # 7
    "Khôn",  # 8
)

EARTHLY_BRANCHES = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)

METHOD_ID = "mai_hoa_nntt_v1"
SOURCE_REF = (
    "Thiệu Khang Tiết — Mai Hoa Dịch Số Toàn Tập, "
    "Niên Nguyệt Nhật Thời Khởi Quái Pháp."
)


@dataclass(frozen=True)
class NntDerivationInputs:
    year_branch_idx: int   # 1..12
    lunar_month: int       # 1..12
    lunar_day: int         # 1..30
    hour_branch_idx: int   # 1..12


def _branch_idx_from_pillar(pillar: str) -> int:
    """Parse 'Stem Branch' → branch index 1..12."""
    parts = pillar.strip().split()
    if len(parts) != 2:
        raise ValueError(f"invalid Can-Chi pillar: {pillar!r}")
    branch = parts[1]
    if branch not in EARTHLY_BRANCHES:
        raise ValueError(f"unknown branch in pillar: {branch!r}")
    return EARTHLY_BRANCHES.index(branch) + 1  # 1-based


def _parse_lunar_date(lunar_date_str: str) -> tuple[int, int]:
    """Parse 'DD/MM/YYYY' → (day, month)."""
    parts = lunar_date_str.split("/")
    if len(parts) != 3:
        raise ValueError(f"invalid lunar date string: {lunar_date_str!r}")
    return int(parts[0]), int(parts[1])


def derive_inputs_from_chronos(state: ChronosState) -> NntDerivationInputs:
    year_branch_idx = _branch_idx_from_pillar(state.ganzhi.year)
    lunar_day, lunar_month = _parse_lunar_date(state.almanac.lunar_date)
    hour_branch_idx = _branch_idx_from_pillar(state.ganzhi.hour)
    return NntDerivationInputs(
        year_branch_idx=year_branch_idx,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch_idx=hour_branch_idx,
    )


def _mod8(value: int) -> int:
    rem = value % 8
    return rem if rem != 0 else 8


def _mod6(value: int) -> int:
    rem = value % 6
    return rem if rem != 0 else 6


def derive_line_states(state: ChronosState) -> list[LineState]:
    """Compute 6 LineStates from chronos via Mai Hoa NNTT."""
    inputs = derive_inputs_from_chronos(state)
    upper_num = _mod8(inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day)
    lower_num = _mod8(
        inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day + inputs.hour_branch_idx
    )
    moving_line = _mod6(
        inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day + inputs.hour_branch_idx
    )

    upper_trigram = TIEN_THIEN_TRIGRAMS[upper_num - 1]
    lower_trigram = TIEN_THIEN_TRIGRAMS[lower_num - 1]

    # binary[0] is top line (line 6); binary[5] is bottom line (line 1).
    binary = f"{TRIGRAM_BITS[upper_trigram]}{TRIGRAM_BITS[lower_trigram]}"

    line_states: list[LineState] = []
    for line_position in range(1, 7):
        idx_from_top = 6 - line_position
        polarity = Polarity.YANG if binary[idx_from_top] == "1" else Polarity.YIN
        motion = MotionState.MOVING if line_position == moving_line else MotionState.STATIC
        line_states.append(
            LineState(
                line_position=line_position,
                polarity=polarity,
                motion=motion,
                origin_value=upper_num if line_position > 3 else lower_num,
            )
        )
    return line_states


def derivation_summary(state: ChronosState) -> dict:
    """Return raw NNT inputs and computed numbers for trace/debugging."""
    inputs = derive_inputs_from_chronos(state)
    upper_num = _mod8(inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day)
    lower_num = _mod8(
        inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day + inputs.hour_branch_idx
    )
    moving_line = _mod6(
        inputs.year_branch_idx + inputs.lunar_month + inputs.lunar_day + inputs.hour_branch_idx
    )
    return {
        "method_id": METHOD_ID,
        "year_branch_idx": inputs.year_branch_idx,
        "lunar_month": inputs.lunar_month,
        "lunar_day": inputs.lunar_day,
        "hour_branch_idx": inputs.hour_branch_idx,
        "upper_num": upper_num,
        "upper_trigram": TIEN_THIEN_TRIGRAMS[upper_num - 1],
        "lower_num": lower_num,
        "lower_trigram": TIEN_THIEN_TRIGRAMS[lower_num - 1],
        "moving_line": moving_line,
        "source_ref": SOURCE_REF,
    }
