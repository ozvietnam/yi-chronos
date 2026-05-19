"""Constants for Bát Tự / Tứ Trụ engine.

Sources:
- 10 Thiên can + 12 Địa chi: canonical (周易, 滴天髓).
- Element mapping: 五行 standard.
- Thập thần rules: 子平真詮 / 三命通會.

Convention: All names in Vietnamese unless otherwise noted.
"""

from __future__ import annotations


# 10 Thiên Can (heavenly stems)
HEAVENLY_STEMS: tuple[str, ...] = (
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
)

# 12 Địa Chi (earthly branches)
EARTHLY_BRANCHES: tuple[str, ...] = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)

# Stem → element + polarity (yang/yin)
STEM_ELEMENT: dict[str, str] = {
    "Giáp": "mộc", "Ất": "mộc",
    "Bính": "hỏa", "Đinh": "hỏa",
    "Mậu": "thổ", "Kỷ": "thổ",
    "Canh": "kim", "Tân": "kim",
    "Nhâm": "thủy", "Quý": "thủy",
}

STEM_POLARITY: dict[str, str] = {
    "Giáp": "dương", "Ất": "âm",
    "Bính": "dương", "Đinh": "âm",
    "Mậu": "dương", "Kỷ": "âm",
    "Canh": "dương", "Tân": "âm",
    "Nhâm": "dương", "Quý": "âm",
}

# Branch → primary element
BRANCH_ELEMENT: dict[str, str] = {
    "Tý": "thủy", "Sửu": "thổ",
    "Dần": "mộc", "Mão": "mộc",
    "Thìn": "thổ", "Tỵ": "hỏa",
    "Ngọ": "hỏa", "Mùi": "thổ",
    "Thân": "kim", "Dậu": "kim",
    "Tuất": "thổ", "Hợi": "thủy",
}

BRANCH_POLARITY: dict[str, str] = {
    "Tý": "dương", "Sửu": "âm",
    "Dần": "dương", "Mão": "âm",
    "Thìn": "dương", "Tỵ": "âm",
    "Ngọ": "dương", "Mùi": "âm",
    "Thân": "dương", "Dậu": "âm",
    "Tuất": "dương", "Hợi": "âm",
}

# 12 Địa chi tàng can (hidden stems within each branch).
# Each branch contains 1-3 stems (本氣 / 中氣 / 餘氣). For now use the primary set.
# Source: 子平真詮 standard chart.
BRANCH_HIDDEN_STEMS: dict[str, tuple[str, ...]] = {
    "Tý":  ("Quý",),
    "Sửu": ("Kỷ", "Quý", "Tân"),
    "Dần": ("Giáp", "Bính", "Mậu"),
    "Mão": ("Ất",),
    "Thìn": ("Mậu", "Ất", "Quý"),
    "Tỵ":  ("Bính", "Mậu", "Canh"),
    "Ngọ": ("Đinh", "Kỷ"),
    "Mùi": ("Kỷ", "Đinh", "Ất"),
    "Thân": ("Canh", "Nhâm", "Mậu"),
    "Dậu": ("Tân",),
    "Tuất": ("Mậu", "Tân", "Đinh"),
    "Hợi": ("Nhâm", "Giáp"),
}

# 5 elements
FIVE_ELEMENTS: tuple[str, ...] = ("kim", "mộc", "thủy", "hỏa", "thổ")

# Sinh (生 generates) — A 生 B means A nourishes B.
ELEMENT_GENERATES: dict[str, str] = {
    "mộc": "hỏa",
    "hỏa": "thổ",
    "thổ": "kim",
    "kim": "thủy",
    "thủy": "mộc",
}

# Khắc (尅 controls) — A 尅 B means A dominates B.
ELEMENT_CONTROLS: dict[str, str] = {
    "mộc": "thổ",
    "thổ": "thủy",
    "thủy": "hỏa",
    "hỏa": "kim",
    "kim": "mộc",
}


# Thập Thần (10 Gods) — relations from Day Master (日干) to another stem.
#
# Rule:
#   - Same element + same polarity   → Tỷ Kiên (比肩)
#   - Same element + opposite polarity → Kiếp Tài (劫財)
#   - Day generates target + same polarity → Thực Thần (食神)
#   - Day generates target + opposite     → Thương Quan (傷官)
#   - Day controls target + same polarity → Thiên Tài (偏財)
#   - Day controls target + opposite     → Chính Tài (正財)
#   - Target controls Day + same polarity → Thất Sát (七殺)
#   - Target controls Day + opposite     → Chính Quan (正官)
#   - Target generates Day + same polarity → Thiên Ấn (偏印) [aka Kiêu Thần]
#   - Target generates Day + opposite     → Chính Ấn (正印)

THAP_THAN_NAMES: tuple[str, ...] = (
    "Tỷ Kiên",
    "Kiếp Tài",
    "Thực Thần",
    "Thương Quan",
    "Thiên Tài",
    "Chính Tài",
    "Thất Sát",
    "Chính Quan",
    "Thiên Ấn",
    "Chính Ấn",
)

THAP_THAN_SHORT: dict[str, str] = {
    "Tỷ Kiên": "比",
    "Kiếp Tài": "劫",
    "Thực Thần": "食",
    "Thương Quan": "傷",
    "Thiên Tài": "偏財",
    "Chính Tài": "正財",
    "Thất Sát": "七殺",
    "Chính Quan": "正官",
    "Thiên Ấn": "偏印",
    "Chính Ấn": "正印",
}

# Short character meaning for UX labels.
THAP_THAN_MEANING: dict[str, str] = {
    "Tỷ Kiên":   "Anh em ngang vai, đồng nghiệp, cạnh tranh trực diện",
    "Kiếp Tài":  "Người cướp của, đối thủ ngầm, hao tổn tài lộc",
    "Thực Thần": "Tài năng sáng tạo, hưởng thụ, nuôi dưỡng",
    "Thương Quan": "Phá cách, nổi loạn, tài năng vượt khuôn khổ",
    "Thiên Tài":  "Tài lộc bất ngờ, đầu cơ, đào hoa",
    "Chính Tài":  "Tài chính ổn định, lương cứng, vợ chính (Nam)",
    "Thất Sát":   "Quyền lực, áp lực dữ dội, tướng quân, đối thủ mạnh",
    "Chính Quan": "Chức tước chính thống, kỷ luật, chồng (Nữ)",
    "Thiên Ấn":  "Quý nhân ngầm, mẹ kế, trí tuệ phi truyền thống",
    "Chính Ấn":  "Mẹ ruột, học vấn chính quy, ấn tín bảo hộ",
}


# Pillar position labels
PILLAR_NAMES: tuple[str, ...] = ("year", "month", "day", "hour")
PILLAR_NAMES_VI: dict[str, str] = {
    "year": "Trụ Năm",
    "month": "Trụ Tháng",
    "day": "Trụ Ngày",
    "hour": "Trụ Giờ",
}

# Pillar life-domain interpretation (子平 tradition).
PILLAR_DOMAIN: dict[str, str] = {
    "year": "Tổ tiên / vận sơ ấu (0-15 tuổi)",
    "month": "Cha mẹ / vận thanh xuân (16-30 tuổi)",
    "day": "Bản thân (Day Master) + vợ chồng (31-45 tuổi)",
    "hour": "Con cái / hậu vận (46+ tuổi)",
}
