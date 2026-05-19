"""Pointer-signal interaction + deterministic 6-coin casting helpers.

Public:
- InteractionSignal — frozen dataclass for raw pointer signals
- _extract_stem_branch — split "Stem Branch" pillar text
- _lcg / _coin_face / _line_from_coin_sum / _line_branch — internal RNG + line builders
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .constants import EARTHLY_BRANCHES, VOID_BRANCHES_BY_DAY_STEM


@dataclass(frozen=True)
class InteractionSignal:
    hold_duration_ms: int
    move_event_count: int
    path_length_px: float
    release_timestamp_ms: int


def _extract_stem_branch(ganzhi_text: str) -> tuple[str, str]:
    stem = ""
    branch = ""
    for token in ganzhi_text.replace("-", " ").split():
        if token in VOID_BRANCHES_BY_DAY_STEM:
            stem = token
        if token in EARTHLY_BRANCHES:
            branch = token
    return stem, branch


def _lcg(seed: int) -> int:
    return (1664525 * seed + 1013904223) % (2**32)


def _coin_face(seed: int) -> tuple[int, int]:
    next_seed = _lcg(seed)
    # 0 -> tails(2), 1 -> heads(3)
    value = 3 if next_seed % 2 else 2
    return value, next_seed


def _line_from_coin_sum(total: int) -> dict[str, Any]:
    if total == 6:
        return {"polarity": "yin", "moving": True, "symbol": "老陰"}
    if total == 7:
        return {"polarity": "yang", "moving": False, "symbol": "少陽"}
    if total == 8:
        return {"polarity": "yin", "moving": False, "symbol": "少陰"}
    return {"polarity": "yang", "moving": True, "symbol": "老陽"}


def _line_branch(line_position: int, day_branch: str) -> str:
    base_idx = EARTHLY_BRANCHES.index(day_branch) if day_branch in EARTHLY_BRANCHES else 0
    return EARTHLY_BRANCHES[(base_idx + line_position - 1) % 12]
