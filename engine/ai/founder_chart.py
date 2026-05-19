"""Founder's verified Bát Tự chart — manual override for engine UTC bug.

Engine `engine.bat_tu.cast` uses UTC day boundary which gives WRONG day pillar
for the founder's 23:00 birth under 早子時 (early Tý) convention.

This module ships the verified V2B chart (body-indicator confirmed 2026-05-12)
as a reusable precast bundle. Use it whenever spawning a council on behalf of
the founder.

See `data/yi_hermes/founder_profile.md` for the full chart + verification.
See `docs/v3-roadmap.md` — engine fix for 早子時 convention is in v3 backlog.
"""

from __future__ import annotations

from engine.bat_tu.cach_cuc import classify_cach_cuc
from engine.bat_tu.constants import (
    BRANCH_ELEMENT,
    BRANCH_HIDDEN_STEMS,
    BRANCH_POLARITY,
    STEM_ELEMENT,
    STEM_POLARITY,
)
from engine.bat_tu.dung_than import determine_dung_than
from engine.bat_tu.ngu_hanh import count_elements, day_master_strength
from engine.bat_tu.than_sat import detect_than_sat
from engine.bat_tu.thap_than import thap_than_of


FOUNDER_BIRTH = {
    "birth_datetime_local": "1988-06-05T23:30:00",
    "timezone": "Asia/Ho_Chi_Minh",
    "gender": "nam",
    "day_pillar_convention": "早子時 (early Tý)",
}

# Verified Tứ Trụ — V2B body-indicator match 2026-05-12
FOUNDER_PILLARS_RAW = {
    "year":  ("Mậu", "Thìn"),
    "month": ("Đinh", "Tỵ"),
    "day":   ("Ất", "Hợi"),     # 早子時 — sang ngày kế
    "hour":  ("Bính", "Tý"),
}


def _build_pillar(pos: str, stem: str, branch: str) -> dict:
    return {
        "position": pos,
        "stem": stem,
        "branch": branch,
        "stem_element": STEM_ELEMENT[stem],
        "branch_element": BRANCH_ELEMENT[branch],
        "stem_polarity": STEM_POLARITY[stem],
        "branch_polarity": BRANCH_POLARITY[branch],
        "hidden_stems": list(BRANCH_HIDDEN_STEMS[branch]),
    }


def build_founder_pillars() -> dict[str, dict]:
    """Return the 4 pillars dict in the same shape as engine.bat_tu.tu_tru."""
    return {pos: _build_pillar(pos, s, b) for pos, (s, b) in FOUNDER_PILLARS_RAW.items()}


def cast_founder_bat_tu() -> dict:
    """Compose the full founder Bát Tự chart (V2B verified).

    Mirrors `engine.bat_tu.cast.cast_bat_tu` output shape but with correct
    Day pillar (Ất Hợi instead of Giáp Tuất per UTC bug).
    """
    pillars = build_founder_pillars()
    day_master = pillars["day"]["stem"]      # Ất
    day_element = pillars["day"]["stem_element"]  # mộc

    element_counts = count_elements(pillars)
    dm_assessment = day_master_strength(day_element, element_counts)
    dung_than = determine_dung_than(
        day_element=day_element,
        element_counts=element_counts,
        strength_tag=dm_assessment["strength_tag"],
        month_branch_element=BRANCH_ELEMENT[pillars["month"]["branch"]],
        day_stem=day_master,
        month_branch=pillars["month"]["branch"],
    )
    cach_cuc = classify_cach_cuc(pillars, day_master)
    than_sat = detect_than_sat(pillars, day_master)

    # Annotate thap_than per pillar
    for pos in ("year", "month", "hour"):
        s = pillars[pos]["stem"]
        pillars[pos]["thap_than"] = thap_than_of(day_master, s)
    pillars["day"]["thap_than"] = "Bản thân"

    return {
        "method_id": "founder_chart_v1_manual",
        "source_ref": "Verified body-indicator V2B 2026-05-12",
        "birth_datetime_local": FOUNDER_BIRTH["birth_datetime_local"],
        "timezone": FOUNDER_BIRTH["timezone"],
        "gender": FOUNDER_BIRTH["gender"],
        "day_pillar_convention": FOUNDER_BIRTH["day_pillar_convention"],
        "tu_tru": {
            "pillars": pillars,
            "day_master": {
                "stem": day_master,
                "element": day_element,
                "polarity": pillars["day"]["stem_polarity"],
            },
        },
        "ngu_hanh": {
            "counts": element_counts,
            "day_master_assessment": dm_assessment,
        },
        "dung_than": dung_than.to_dict(),
        "cach_cuc": cach_cuc,
        "than_sat": than_sat,
        "dai_van_current": {
            "stem": "Tân", "branch": "Dậu",
            "start_age": 34, "end_age": 43,
            "current_age": 37,
            "note": "Đại vận Tân Dậu — Kim khắc Mộc Day Master → đại vận thử thách. Kế: Nhâm Tuất (44-53) Thủy sinh Mộc → hồi phục.",
        },
        "engine_note": (
            "Chart này được build TAY do engine.bat_tu.cast có bug UTC boundary "
            "không hỗ trợ 早子時 convention. Khi engine fix (v3 roadmap), "
            "có thể thay bằng cast_bat_tu() native."
        ),
    }
