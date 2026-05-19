"""Độn Pháp — gia số [+4, +6, +4] mod (8,8,6) chain.

Book rules (p.17-22):
- Một bước gia số = +4 thượng (rút bớt 8 nếu > 8), +6 hạ (rút bớt 8 nếu > 8),
  +4 hào động (rút bớt 6 nếu > 6).
- Bốn bước gia số = MỘT ĐỢT ĐỘN → sinh 4 hậu đề (cộng tiên đề thành 5 không thời).
- Sau 1 đợt: chánh quái return về tiên đề chánh, hào động lệch (+4 mod 6).
- "Hoàn thành" khi TA quái ở không thời cuối KHÔNG bị động.
- Số đợt cần để hoàn thành:
    hào 3 hoặc 6 → 1 đợt (5 không thời)
    hào 4 hoặc 1 → 2 đợt (9 không thời)
    hào 5 hoặc 2 → 3 đợt (13 không thời)
"""

from __future__ import annotations

from dataclasses import dataclass

from .constants import DOT_COUNT_BY_HAO, KHONG_THOI_COUNT_BY_DOT
from .quai_ops import hao_side


def step_don(upper: int, lower: int, hao: int) -> tuple[int, int, int]:
    """One step gia số [+4 thượng, +6 hạ, +4 hào]."""
    u = upper + 4
    if u > 8:
        u -= 8
    l = lower + 6
    if l > 8:
        l -= 8
    h = hao + 4
    if h > 6:
        h -= 6
    return u, l, h


def expected_dot_count(initial_hao: int) -> int:
    """Số đợt độn cần để hoàn thành, theo hào động Tiên đề."""
    return DOT_COUNT_BY_HAO[initial_hao]


def expected_khong_thoi_count(initial_hao: int) -> int:
    """Số không thời sự (Tiên đề + Hậu đề) sẽ sinh ra."""
    return KHONG_THOI_COUNT_BY_DOT[expected_dot_count(initial_hao)]


@dataclass(frozen=True)
class DonStep:
    step_index: int          # 1..(4*dot_count)
    upper: int
    lower: int
    hao: int
    is_dot_boundary: bool    # True at end of each đợt


def compute_don_chain(initial_upper: int, initial_lower: int, initial_hao: int) -> list[DonStep]:
    """Sinh chuỗi gia số từ Tiên đề đến không thời cuối của đợt độn hoàn thành.

    Returns list of DonStep (does NOT include Tiên đề itself — only hậu đề).
    Length = 4 * dot_count.
    """
    ta_side_initial = "lower" if hao_side(initial_hao) == "upper" else "upper"
    dot_count = expected_dot_count(initial_hao)
    steps: list[DonStep] = []
    u, l, h = initial_upper, initial_lower, initial_hao
    for dot in range(1, dot_count + 1):
        for s in range(1, 5):
            u, l, h = step_don(u, l, h)
            steps.append(
                DonStep(
                    step_index=(dot - 1) * 4 + s,
                    upper=u,
                    lower=l,
                    hao=h,
                    is_dot_boundary=(s == 4),
                )
            )
    return steps


def check_completion(steps: list[DonStep], ta_side: str) -> tuple[bool, int]:
    """Check if at the end of which đợt the TA side becomes bất động.

    Returns (completed, dot_at_completion). If never completed within `steps`,
    returns (False, dot_count_attempted).
    """
    for step in steps:
        if step.is_dot_boundary:
            current_side = hao_side(step.hao)
            if current_side != ta_side:
                return True, step.step_index // 4
    return False, len(steps) // 4
