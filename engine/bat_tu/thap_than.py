"""Thập Thần — 10 god classifier relative to Day Master (日干).

Classical 子平 rule: every other stem in the chart is one of 10 "gods" relative to
the Day Master, based on element relation + polarity match.
"""

from __future__ import annotations

from .constants import (
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    STEM_ELEMENT,
    STEM_POLARITY,
)


def thap_than_of(day_master: str, target_stem: str) -> str:
    """Return the Thập Thần of `target_stem` relative to `day_master`.

    Both arguments must be Vietnamese stem names (Giáp, Ất, ..., Quý).
    """
    if day_master not in STEM_ELEMENT or target_stem not in STEM_ELEMENT:
        raise ValueError(f"Unknown stem: day={day_master!r}, target={target_stem!r}")

    day_el = STEM_ELEMENT[day_master]
    target_el = STEM_ELEMENT[target_stem]
    day_polarity = STEM_POLARITY[day_master]
    target_polarity = STEM_POLARITY[target_stem]
    same_polarity = day_polarity == target_polarity

    # Same element
    if day_el == target_el:
        return "Tỷ Kiên" if same_polarity else "Kiếp Tài"

    # Day 生 target (target is Day's child) → Thực / Thương
    if ELEMENT_GENERATES[day_el] == target_el:
        return "Thực Thần" if same_polarity else "Thương Quan"

    # Day 尅 target (target is Day's "wealth")
    if ELEMENT_CONTROLS[day_el] == target_el:
        return "Thiên Tài" if same_polarity else "Chính Tài"

    # Target 尅 Day (target is "official/authority")
    if ELEMENT_CONTROLS[target_el] == day_el:
        return "Thất Sát" if same_polarity else "Chính Quan"

    # Target 生 Day (target is "seal/印")
    if ELEMENT_GENERATES[target_el] == day_el:
        return "Thiên Ấn" if same_polarity else "Chính Ấn"

    raise ValueError(f"No relation found for day={day_master} target={target_stem}")


def thap_than_short(name: str) -> str:
    """Short Vietnamese category for UI tags."""
    short_map = {
        "Tỷ Kiên": "Tỷ",
        "Kiếp Tài": "Kiếp",
        "Thực Thần": "Thực",
        "Thương Quan": "Thương",
        "Thiên Tài": "T.Tài",
        "Chính Tài": "C.Tài",
        "Thất Sát": "Sát",
        "Chính Quan": "Quan",
        "Thiên Ấn": "T.Ấn",
        "Chính Ấn": "C.Ấn",
    }
    return short_map.get(name, name)


# Convenience: classifying a 6-親 (Lục thân) family-style for cross-reference
# with Lục Hào (when the user asks "where's my wealth in Bát Tự").
THAP_THAN_FAMILY: dict[str, str] = {
    "Tỷ Kiên":  "Huynh đệ",        # 兄弟
    "Kiếp Tài": "Huynh đệ",
    "Thực Thần": "Con cái / cấp dưới",
    "Thương Quan": "Con cái / cấp dưới",
    "Thiên Tài": "Cha / tài phụ",
    "Chính Tài": "Vợ chính / tài chính ổn định",
    "Thất Sát":  "Quyền / kẻ địch",
    "Chính Quan": "Chồng / cấp trên",
    "Thiên Ấn":  "Mẹ kế / quý nhân",
    "Chính Ấn":  "Mẹ ruột / học vấn",
}
