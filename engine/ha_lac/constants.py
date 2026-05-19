"""Constants for Bát Tự Hà Lạc Lý Số.

Source: Học Năng, *Bát Tự Hà Lạc Lược Khảo*, Saigon 1974, cross-verified with
Chen Tuan (陈抟) lineage Chinese sources (yi-fengshui.com, k366.com, CSDN).

Reference: see docs/upgrade-plan-from-kabalavn-research.md mục 5.1.
"""

from __future__ import annotations


# Thiên Can → Hà Đồ number
STEM_NUMBERS: dict[str, int] = {
    "Giáp":  6,
    "Ất":    2,
    "Bính":  8,
    "Đinh":  7,
    "Mậu":   1,
    "Kỷ":    9,
    "Canh":  3,
    "Tân":   4,
    "Nhâm":  6,
    "Quý":   2,
}

# Địa Chi → (sinh số, thành số) pair
BRANCH_NUMBER_PAIRS: dict[str, tuple[int, int]] = {
    "Hợi":  (1, 6),
    "Tý":   (1, 6),
    "Dần":  (3, 8),
    "Mão":  (3, 8),
    "Tỵ":   (2, 7),
    "Ngọ":  (2, 7),
    "Thân": (4, 9),
    "Dậu":  (4, 9),
    "Thìn": (5, 10),
    "Tuất": (5, 10),
    "Sửu":  (5, 10),
    "Mùi":  (5, 10),
}

# Lạc Thư trigram map (5 reserved as centre).
NUMBER_TO_TRIGRAM: dict[int, str] = {
    1: "Khảm",
    2: "Khôn",
    3: "Chấn",
    4: "Tốn",
    # 5 = centre (jì-gōng special handling)
    6: "Càn",
    7: "Đoài",
    8: "Cấn",
    9: "Ly",
}

# Yang stems (used to determine year-polarity)
YANG_STEMS: frozenset[str] = frozenset(["Giáp", "Bính", "Mậu", "Canh", "Nhâm"])
YIN_STEMS: frozenset[str] = frozenset(["Ất", "Đinh", "Kỷ", "Tân", "Quý"])

# Yang and yin earthly branches (for birth-hour parity)
YANG_BRANCHES: tuple[str, ...] = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ")
YIN_BRANCHES: tuple[str, ...] = ("Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")

# Reduction thresholds
TIEN_THRESHOLD = 25     # Thiên số: subtract 25 while > 25
DIA_THRESHOLD = 30      # Địa số: subtract 30 while > 30

# Years per yao for decade trajectory
YEARS_PER_YANG_YAO = 9
YEARS_PER_YIN_YAO = 6

# 5 jì-gōng fallback (low-confidence; users see this caveat)
FIVE_FALLBACK_YANG = "Ly"   # popular Vietnamese variant
FIVE_FALLBACK_YIN = "Đoài"
