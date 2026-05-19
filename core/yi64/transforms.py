from __future__ import annotations

from typing import Iterable

from core.hexagram import apply_moving_lines, get_hexagram_by_binary

from .model import HexagramIdentity, LineState, MotionState, Polarity


def lines_to_binary(line_states: Iterable[LineState]) -> str:
    # Input line states are bottom-up; binary format in this repo is top-down.
    ordered = sorted(line_states, key=lambda item: item.line_position)
    bottom_up = "".join("1" if line.polarity == Polarity.YANG else "0" for line in ordered)
    return bottom_up[::-1]


def line_flip_transform(base_binary: str, moving_lines: Iterable[int]) -> str:
    return apply_moving_lines(base_binary, moving_lines)


def binary_to_hexagram_identity(binary_code: str) -> HexagramIdentity:
    hx = get_hexagram_by_binary(binary_code)
    return HexagramIdentity(
        king_wen_index=hx.king_wen_index,
        binary_code=hx.binary,
        name_vi=hx.name_vi,
        upper_trigram=hx.upper_trigram,
        lower_trigram=hx.lower_trigram,
    )


def moving_lines_from_states(line_states: Iterable[LineState]) -> tuple[int, ...]:
    return tuple(
        line.line_position
        for line in sorted(line_states, key=lambda item: item.line_position)
        if line.motion == MotionState.MOVING
    )
