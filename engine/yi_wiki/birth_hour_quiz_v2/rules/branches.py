"""Twelve Earthly Branches — element, hour ranges, TCM organ clock."""
from __future__ import annotations

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
            "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

BRANCH_ELEMENTS = {
    "Tý": "Thuỷ",   "Sửu": "Thổ",  "Dần": "Mộc",  "Mão": "Mộc",
    "Thìn": "Thổ",  "Tỵ": "Hoả",   "Ngọ": "Hoả",  "Mùi": "Thổ",
    "Thân": "Kim",  "Dậu": "Kim",  "Tuất": "Thổ", "Hợi": "Thuỷ",
}

# (start_hour, end_hour) — Tý spans 23h-1h (wraps midnight).
HOUR_RANGES = {
    "Tý":   (23, 1),
    "Sửu":  (1, 3),
    "Dần":  (3, 5),
    "Mão":  (5, 7),
    "Thìn": (7, 9),
    "Tỵ":   (9, 11),
    "Ngọ":  (11, 13),
    "Mùi":  (13, 15),
    "Thân": (15, 17),
    "Dậu":  (17, 19),
    "Tuất": (19, 21),
    "Hợi":  (21, 23),
}

# TCM organ clock — each 2-hour period governs an organ.
TCM_ORGAN = {
    "Tý": "thận",         "Sửu": "can",   "Dần": "phế",       "Mão": "đại trường",
    "Thìn": "vị",         "Tỵ": "tỳ",     "Ngọ": "tâm",       "Mùi": "tiểu trường",
    "Thân": "bàng quang", "Dậu": "thận",  "Tuất": "tâm bào",  "Hợi": "tam tiêu",
}


def hour_to_chi(hour: int) -> str:
    """Convert 0-23 hour to Earthly Branch."""
    for chi, (start, end) in HOUR_RANGES.items():
        if start > end:  # Tý wraps midnight
            if hour >= start or hour < end:
                return chi
        elif start <= hour < end:
            return chi
    raise ValueError(f"hour {hour} out of range")
