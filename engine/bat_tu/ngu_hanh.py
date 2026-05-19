"""Ngũ hành balance — count element distribution across all 8 characters.

Weights:
- Visible stems (4 stems in 4 pillars): weight 1.0 each
- Visible branches (4 branches): weight 1.0 each on branch's primary element
- Hidden stems (地支藏干): each hidden stem adds 0.3 partial weight

This is a *simplified* tally for Day Master strength assessment. Classical 子平
uses a more nuanced scoring (month-seal weight, root vs not-rooted, etc.) which
we can layer on later.
"""

from __future__ import annotations

from .constants import (
    BRANCH_ELEMENT,
    BRANCH_HIDDEN_STEMS,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    FIVE_ELEMENTS,
    STEM_ELEMENT,
)


VISIBLE_WEIGHT = 1.0
HIDDEN_WEIGHT = 0.3


def count_elements(pillars: dict) -> dict:
    """Return weighted count of each element across the chart.

    `pillars` is the dict from extract_tu_tru['pillars'] — keys 'year'/'month'/'day'/'hour'.
    """
    counts: dict[str, float] = {e: 0.0 for e in FIVE_ELEMENTS}

    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        counts[p["stem_element"]] += VISIBLE_WEIGHT
        counts[p["branch_element"]] += VISIBLE_WEIGHT
        for hidden_stem in p["hidden_stems"]:
            hidden_el = STEM_ELEMENT[hidden_stem]
            counts[hidden_el] += HIDDEN_WEIGHT

    return {k: round(v, 2) for k, v in counts.items()}


def day_master_strength(day_master_element: str, element_counts: dict) -> dict:
    """Assess Day Master strength from element distribution.

    Rules (simplified 子平):
    - Day Master strong = lots of same element (Tỷ/Kiếp) + lots of generating element (Ấn).
    - Day Master weak  = lots of controlling element (Quan/Sát) + draining (Thực/Thương) + Tài.
    """
    dm = day_master_element
    supporting = element_counts[dm]                        # 比 (same)
    seal = element_counts[_element_generating(dm)]         # 印 (generates DM)
    output = element_counts[ELEMENT_GENERATES[dm]]         # 食 (DM generates)
    wealth = element_counts[ELEMENT_CONTROLS[dm]]          # 財 (DM controls)
    pressure = element_counts[_element_controlling(dm)]    # 官殺 (controls DM)

    support_score = supporting + seal
    drain_score = output + wealth + pressure

    if support_score == 0 and drain_score == 0:
        strength_tag = "neutral"
        strength_label = "Cân bằng"
    elif support_score > drain_score * 1.3:
        strength_tag = "strong"
        strength_label = "Vượng (nhật chủ mạnh)"
    elif drain_score > support_score * 1.3:
        strength_tag = "weak"
        strength_label = "Nhược (nhật chủ yếu)"
    else:
        strength_tag = "balanced"
        strength_label = "Trung bình"

    return {
        "day_master_element": dm,
        "support_score": round(support_score, 2),
        "drain_score": round(drain_score, 2),
        "breakdown": {
            "ti_kiep_support": round(supporting, 2),
            "an_seal": round(seal, 2),
            "thuc_thuong_output": round(output, 2),
            "tai_wealth": round(wealth, 2),
            "quan_sat_pressure": round(pressure, 2),
        },
        "strength_tag": strength_tag,
        "strength_label": strength_label,
    }


def _element_generating(target: str) -> str:
    """Return the element that generates `target` (i.e. parent in Sinh cycle)."""
    for el, child in ELEMENT_GENERATES.items():
        if child == target:
            return el
    raise ValueError(f"Unknown element: {target}")


def _element_controlling(target: str) -> str:
    """Return the element that controls `target`."""
    for el, victim in ELEMENT_CONTROLS.items():
        if victim == target:
            return el
    raise ValueError(f"Unknown element: {target}")
