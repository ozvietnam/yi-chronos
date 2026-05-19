"""Decade trajectory — life-stage walk through 12 lines (6 Tiên thiên + 6 Hậu thiên).

Convention:
- Each yang line = 9 years, each yin line = 6 years.
- Walk starts at line 1 of Tiên thiên at age 1.
- After line 6 of Tiên thiên, continue to line 1 of Hậu thiên through line 6.
- Total span typically 84-90 years depending on hexagram parity composition.
- The nguyên đường line of each hexagram is the dominant/key decade.
"""

from __future__ import annotations

from .constants import YEARS_PER_YANG_YAO, YEARS_PER_YIN_YAO


def build_trajectory(
    tien_binary: str,
    hau_binary: str,
    nguyen_duong_tien: int,
    nguyen_duong_hau: int,
    start_age: int = 1,
) -> list[dict]:
    """Build the 12-line decade trajectory.

    Returns a list of 12 dicts, each:
        {
          "stage_index": 1..12,
          "hexagram": "tien" / "hau",
          "line_position": 1..6,
          "polarity": "yang" / "yin",
          "years_span": 9 or 6,
          "age_start": int,
          "age_end": int,
          "is_nguyen_duong": bool,
          "label": str  # Vietnamese description
        }
    """
    out: list[dict] = []
    current_age = start_age

    def _add(stage_idx: int, hex_label: str, binary_top_down: str, line_pos: int,
             nguyen_duong_pos: int) -> None:
        nonlocal current_age
        # Convert top-down binary index for this line position.
        # Line pos 1 = bottom = string index 5; line pos 6 = top = index 0.
        idx = 6 - line_pos
        bit = binary_top_down[idx]
        polarity = "yang" if bit == "1" else "yin"
        years = YEARS_PER_YANG_YAO if bit == "1" else YEARS_PER_YIN_YAO
        is_nd = line_pos == nguyen_duong_pos
        out.append({
            "stage_index": stage_idx,
            "hexagram": hex_label,
            "line_position": line_pos,
            "polarity": polarity,
            "years_span": years,
            "age_start": current_age,
            "age_end": current_age + years - 1,
            "is_nguyen_duong": is_nd,
            "label": (
                f"{'Tiên thiên' if hex_label == 'tien' else 'Hậu thiên'} hào {line_pos} "
                f"({polarity}, {years} năm)"
                + (" — Nguyên đường" if is_nd else "")
            ),
        })
        current_age += years

    stage = 1
    # Tiên thiên: line 1 → line 6
    for line in range(1, 7):
        _add(stage, "tien", tien_binary, line, nguyen_duong_tien)
        stage += 1
    # Hậu thiên: line 1 → line 6
    for line in range(1, 7):
        _add(stage, "hau", hau_binary, line, nguyen_duong_hau)
        stage += 1

    return out
