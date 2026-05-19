"""Rule-derived personality hints (Trait 10 + Trait 17 helpers)."""
from __future__ import annotations

from .stems import STEM_YIN_YANG


def derive_yin_yang_ratio(pillars: dict) -> str:
    """Count Dương vs Âm stems across 4 pillars → introvert/extrovert hint.

    Returns: 'mostly_intro' | 'mid' | 'mostly_extro'
    """
    yang_count = sum(
        1 for p in pillars.values() if STEM_YIN_YANG[p["stem"]] == "Dương"
    )
    if yang_count >= 3:
        return "mostly_extro"
    if yang_count <= 1:
        return "mostly_intro"
    return "mid"


# Năm chi 'đào hoa' positions traditionally associated with elder-sibling.
_CA_YEAR_CHI = {"Tý", "Ngọ", "Mão", "Dậu"}
_GIUA_YEAR_CHI = {"Dần", "Thân", "Tỵ", "Hợi"}
_UT_YEAR_CHI = {"Thìn", "Tuất", "Sửu", "Mùi"}


def derive_sibling_position_hint(pillars: dict) -> str:
    """Heuristic: năm chi → sibling position likelihood.

    Returns: 'ca' | 'giua' | 'ut' | 'duy_nhat'
    """
    year_chi = pillars["year"]["branch"]
    if year_chi in _CA_YEAR_CHI:
        return "ca"
    if year_chi in _GIUA_YEAR_CHI:
        return "giua"
    return "ut"
