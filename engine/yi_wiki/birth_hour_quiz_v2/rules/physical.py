"""Derive 7 physical traits from bát tự pillars (Domain 1)."""
from __future__ import annotations

from .stems import STEM_ELEMENTS, DAY_MASTER_BASELINE
from .branches import BRANCH_ELEMENTS

# Hour chi → physiognomy mark pattern (Tướng Pháp Cổ).
CHI_HOUR_PHYSIOGNOMY = {
    "Tý": "1_xoay", "Ngọ": "1_xoay", "Mão": "1_xoay", "Dậu": "1_xoay",
    "Dần": "2_xoay", "Thìn": "2_xoay", "Thân": "2_xoay", "Tuất": "2_xoay",
    "Sửu": "vung_dac_biet", "Mùi": "vung_dac_biet",
    "Tỵ": "vung_dac_biet",  "Hợi": "vung_dac_biet",
}


def _derive_eyes(pillars: dict) -> str:
    """Eye features by Hỏa-Thủy presence across all pillars."""
    elements = []
    for p in pillars.values():
        elements.append(STEM_ELEMENTS[p["stem"]])
        elements.append(BRANCH_ELEMENTS[p["branch"]])
    fire = elements.count("Hoả")
    water = elements.count("Thuỷ")
    if fire >= 3:
        return "sang_to"
    if water >= 3:
        return "hien_min"
    if fire > water:
        return "sac_net"
    return "sau_hep"


def derive_physical_traits(pillars: dict) -> dict[str, str]:
    """Compute 7 physical traits from full pillars.

    Args:
        pillars: {year, month, day, hour} each with {stem, branch}

    Returns:
        Dict with keys: body_height, body_build, face_shape, skin_tone,
        hair_quality, eye_features, physiognomy_marks.
    """
    day_master = pillars["day"]["stem"]
    baseline = DAY_MASTER_BASELINE[day_master]

    # face_shape: blend baseline with hour chi element
    hour_element = BRANCH_ELEMENTS[pillars["hour"]["branch"]]
    face = baseline["face_shape"]
    if hour_element == "Thổ" and face in {"oval", "dai"}:
        face = "vuong"
    elif hour_element == "Thuỷ" and face == "vuong":
        face = "tron"

    # skin_tone: baseline + năm chi water modifier
    skin = baseline["skin_tone"]
    if BRANCH_ELEMENTS[pillars["year"]["branch"]] == "Thuỷ" and skin == "sam":
        skin = "vua"

    return {
        "body_height":       baseline["body_height"],
        "body_build":        baseline["body_build"],
        "face_shape":        face,
        "skin_tone":         skin,
        "hair_quality":      baseline["hair_quality"],
        "eye_features":      _derive_eyes(pillars),
        "physiognomy_marks": CHI_HOUR_PHYSIOGNOMY[pillars["hour"]["branch"]],
    }
