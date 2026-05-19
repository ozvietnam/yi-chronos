"""Hà Lạc number pool computation — Thiên số / Địa số from Tứ Trụ.

Algorithm:
1. Extract 4 stems + 4 branches from the chart.
2. Each stem → 1 Hà Đồ number; each branch → 2 numbers (sinh số + thành số).
3. Split all 12 numbers by parity: odd = Thiên số pool, even = Địa số pool.
4. Sum each pool; reduce to single digit 1..9.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import (
    BRANCH_NUMBER_PAIRS,
    DIA_THRESHOLD,
    STEM_NUMBERS,
    TIEN_THRESHOLD,
)


@dataclass(frozen=True)
class NumberPools:
    """Raw and reduced Thiên số / Địa số."""

    odd_numbers: list[int]       # all odd numbers contributing
    even_numbers: list[int]      # all even numbers
    tien_raw: int                # sum of odd
    dia_raw: int                 # sum of even
    tien_reduced: int            # 1..9 (or 0/5 — flag for jì-gōng)
    dia_reduced: int

    def to_dict(self) -> dict:
        return asdict(self)


def _reduce(total: int, threshold: int) -> int:
    """Reduce a sum by subtracting threshold while > threshold, then take ones digit if ≥ 10."""
    n = total
    while n > threshold:
        n -= threshold
    if n >= 10:
        n = n % 10
    return n


def compute_number_pools(pillars: dict) -> NumberPools:
    """Build the Hà Lạc number pools from 4 pillars.

    `pillars` shape: {'year': {'stem': str, 'branch': str, ...}, 'month': ..., 'day': ..., 'hour': ...}
    """
    all_numbers: list[int] = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        stem = p["stem"]
        branch = p["branch"]
        all_numbers.append(STEM_NUMBERS[stem])
        sinh, thanh = BRANCH_NUMBER_PAIRS[branch]
        all_numbers.extend([sinh, thanh])

    odd = [n for n in all_numbers if n % 2 == 1]
    even = [n for n in all_numbers if n % 2 == 0]
    tien_raw = sum(odd)
    dia_raw = sum(even)

    return NumberPools(
        odd_numbers=odd,
        even_numbers=even,
        tien_raw=tien_raw,
        dia_raw=dia_raw,
        tien_reduced=_reduce(tien_raw, TIEN_THRESHOLD),
        dia_reduced=_reduce(dia_raw, DIA_THRESHOLD),
    )
