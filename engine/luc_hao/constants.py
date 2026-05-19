"""All data tables used across the Lục Hào package.

Pure data — no logic. Importing this module is cheap.
"""

from __future__ import annotations


EARTHLY_BRANCHES = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)

BRANCH_ELEMENT = {
    "Tý": "thủy",
    "Sửu": "thổ",
    "Dần": "mộc",
    "Mão": "mộc",
    "Thìn": "thổ",
    "Tỵ": "hỏa",
    "Ngọ": "hỏa",
    "Mùi": "thổ",
    "Thân": "kim",
    "Dậu": "kim",
    "Tuất": "thổ",
    "Hợi": "thủy",
}

TRIGRAM_BY_NUMBER = {
    1: ("Càn", "kim"),
    2: ("Đoài", "kim"),
    3: ("Ly", "hỏa"),
    4: ("Chấn", "mộc"),
    5: ("Tốn", "mộc"),
    6: ("Khảm", "thủy"),
    7: ("Cấn", "thổ"),
    8: ("Khôn", "thổ"),
}

TRIGRAM_ROLE_MAP = {
    "Càn": "chủ động dẫn hướng",
    "Đoài": "duyệt hòa và đối thoại",
    "Ly": "minh định và làm rõ",
    "Chấn": "khởi động và bứt tốc",
    "Tốn": "thẩm thấu và nhập cục",
    "Khảm": "vượt hiểm và quản trị rủi ro",
    "Cấn": "dừng đúng lúc, chặn sai số",
    "Khôn": "nâng đỡ và dưỡng nền",
}

PAIR_DYNAMICS_MAP = {
    ("Chấn", "Tốn"): "thunder_wind",
    ("Tốn", "Chấn"): "thunder_wind",
    ("Khảm", "Ly"): "water_fire",
    ("Ly", "Khảm"): "water_fire",
    ("Cấn", "Đoài"): "mountain_lake",
    ("Đoài", "Cấn"): "mountain_lake",
}

VIRTUE_ANCHOR_HEXAGRAMS = {
    "Lý": "Nền của Đức: giữ chuẩn mực và trật tự hành xử.",
    "Khiêm": "Cán của Đức: hạ mình đúng lúc để giữ vận bền.",
    "Phục": "Gốc của Đức: quay về nền tảng và tự chỉnh.",
    "Hằng": "Bền của Đức: duy trì nhịp đều, không dao động cực đoan.",
    "Tổn": "Sửa của Đức: bớt đúng chỗ để giữ cốt lõi.",
    "Ích": "Khoan của Đức: tăng trưởng có lợi cho toàn cục.",
    "Khốn": "Xét của Đức: cùng mà thông, giảm oán trách.",
    "Tỉnh": "Nơi của Đức: nuôi dưỡng nguồn gốc tại chỗ.",
    "Tốn": "Pháp của Đức: thẩm thấu, kín đáo và linh hoạt.",
}

ELEMENT_GENERATES = {
    "mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc",
}
ELEMENT_CONTROLS = {
    "mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc",
}

RELATION_BY_ELEMENT = {
    "same": "Huynh Đệ",
    "generated_by_day": "Tử Tôn",
    "generates_day": "Phụ Mẫu",
    "controlled_by_day": "Thê Tài",
    "controls_day": "Quan Quỷ",
}

QUESTION_DOMAIN_RELATION_MAP = [
    (("tiền", "tien", "hợp đồng", "hop dong", "lương", "luong", "doanh thu", "chi phí", "chi phi"), "Thê Tài"),
    (
        (
            "công việc",
            "cong viec",
            "sự nghiệp",
            "su nghiep",
            "chức",
            "chuc",
            "kiện",
            "kien",
            "pháp lý",
            "phap ly",
            "dự án",
            "du an",
        ),
        "Quan Quỷ",
    ),
    (("sức khỏe", "suc khoe", "bệnh", "benh", "đau", "dau", "điều trị", "dieu tri"), "Quan Quỷ"),
    (("gia đình", "gia dinh", "nhà", "nha", "cha mẹ", "cha me", "hôn nhân", "hon nhan"), "Phụ Mẫu"),
    (("con cái", "con cai", "vui", "du lịch", "du lich", "an nhàn", "an nhan"), "Tử Tôn"),
]

CLASH_BRANCH = {
    "Tý": "Ngọ", "Sửu": "Mùi", "Dần": "Thân", "Mão": "Dậu",
    "Thìn": "Tuất", "Tỵ": "Hợi", "Ngọ": "Tý", "Mùi": "Sửu",
    "Thân": "Dần", "Dậu": "Mão", "Tuất": "Thìn", "Hợi": "Tỵ",
}

HARMONY_BRANCH = {
    "Tý": "Sửu", "Sửu": "Tý", "Dần": "Hợi", "Mão": "Tuất",
    "Thìn": "Dậu", "Tỵ": "Thân", "Ngọ": "Mùi", "Mùi": "Ngọ",
    "Thân": "Tỵ", "Dậu": "Thìn", "Tuất": "Mão", "Hợi": "Dần",
}

TIMING_FUNNEL_MATRIX_V2 = (
    {"trigger_type": "moving_to_harmony", "condition": "dung_than_moving", "priority": 1},
    {"trigger_type": "static_to_clash", "condition": "dung_than_static", "priority": 1},
    {"trigger_type": "void_release", "condition": "dung_than_void", "priority": 1},
    {"trigger_type": "void_clash_activation", "condition": "dung_than_void", "priority": 2},
    {"trigger_type": "break_recovery_by_harmony", "condition": "month_or_day_break", "priority": 2},
    {"trigger_type": "mai_hoa_formula", "condition": "fallback_formula", "priority": 3},
)

VOID_BRANCHES_BY_DAY_STEM = {
    "Giáp": ("Tuất", "Hợi"),
    "Ất": ("Tuất", "Hợi"),
    "Bính": ("Thân", "Dậu"),
    "Đinh": ("Thân", "Dậu"),
    "Mậu": ("Ngọ", "Mùi"),
    "Kỷ": ("Ngọ", "Mùi"),
    "Canh": ("Thìn", "Tỵ"),
    "Tân": ("Thìn", "Tỵ"),
    "Nhâm": ("Dần", "Mão"),
    "Quý": ("Dần", "Mão"),
}
