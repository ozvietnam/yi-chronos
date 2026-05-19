"""Energy patterns from TCM organ clock (Domain 3, 3 traits)."""
from __future__ import annotations

# Per hour chi, derived from TCM organ that governs.
WAKE_TIME = {
    "Tý":   "muon",     "Sửu":  "truoc_5h", "Dần":  "truoc_5h",
    "Mão":  "5_7h",     "Thìn": "7_9h",     "Tỵ":   "9_11h",
    "Ngọ":  "9_11h",    "Mùi":  "9_11h",    "Thân": "9_11h",
    "Dậu":  "muon",     "Tuất": "muon",     "Hợi":  "muon",
}

ENERGY_PEAK = {
    "Tý":   "dem",     "Sửu":  "sang",   "Dần":  "sang",
    "Mão":  "sang",    "Thìn": "sang",   "Tỵ":   "sang",
    "Ngọ":  "trua",    "Mùi":  "chieu",  "Thân": "chieu",
    "Dậu":  "chieu",   "Tuất": "toi",    "Hợi":  "toi",
}

SLEEP_PATTERN = {
    "Tý":   "sau_1h",    "Sửu":  "truoc_22h", "Dần":  "truoc_22h",
    "Mão":  "truoc_22h", "Thìn": "22_23h",    "Tỵ":   "22_23h",
    "Ngọ":  "22_23h",    "Mùi":  "22_23h",    "Thân": "22_23h",
    "Dậu":  "23_1h",     "Tuất": "23_1h",     "Hợi":  "23_1h",
}


def derive_energy_traits(pillars: dict) -> dict[str, str]:
    """Compute 3 energy traits from hour chi (TCM organ clock)."""
    hour_chi = pillars["hour"]["branch"]
    return {
        "wake_natural_time":  WAKE_TIME[hour_chi],
        "energy_peak_period": ENERGY_PEAK[hour_chi],
        "sleep_pattern":      SLEEP_PATTERN[hour_chi],
    }
