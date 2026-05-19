from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Hexagram:
    id: int  # legacy ID in binary order
    king_wen_index: int
    binary: str
    name_vi: str
    name_en: str
    upper_trigram: str
    lower_trigram: str
    source_ref: str

SOURCE_REF = (
    "Kinh Dịch Trọn Bộ - Ngô Tất Tố - khoahoctamlinh.vn.pdf"
    " (Mục lục + phần Chu Dịch Thượng/Hạ Kinh, pages 2-4 trong bản số hóa)"
)

TRIGRAM_BITS = {
    "Càn": "111",
    "Khôn": "000",
    "Chấn": "001",
    "Tốn": "110",
    "Khảm": "010",
    "Ly": "101",
    "Cấn": "100",
    "Đoài": "011",
}

# King Wen order (1..64), aligned with terminology in Ngô Tất Tố edition.
KING_WEN_TABLE = (
    (1, "Kiền", "Qian", "Càn", "Càn"),
    (2, "Khôn", "Kun", "Khôn", "Khôn"),
    (3, "Truân", "Zhun", "Khảm", "Chấn"),
    (4, "Mông", "Meng", "Cấn", "Khảm"),
    (5, "Nhu", "Xu", "Khảm", "Càn"),
    (6, "Tụng", "Song", "Càn", "Khảm"),
    (7, "Sư", "Shi", "Khôn", "Khảm"),
    (8, "Tỷ", "Bi", "Khảm", "Khôn"),
    (9, "Tiểu Súc", "Xiao Chu", "Tốn", "Càn"),
    (10, "Lý", "Lu", "Càn", "Đoài"),
    (11, "Thái", "Tai", "Khôn", "Càn"),
    (12, "Bĩ", "Pi", "Càn", "Khôn"),
    (13, "Đồng Nhân", "Tong Ren", "Càn", "Ly"),
    (14, "Đại Hữu", "Da You", "Ly", "Càn"),
    (15, "Khiêm", "Qian-Modesty", "Khôn", "Cấn"),
    (16, "Dự", "Yu", "Chấn", "Khôn"),
    (17, "Tùy", "Sui", "Đoài", "Chấn"),
    (18, "Cổ", "Gu", "Cấn", "Tốn"),
    (19, "Lâm", "Lin", "Khôn", "Đoài"),
    (20, "Quán", "Guan", "Tốn", "Khôn"),
    (21, "Phệ Hạp", "Shi He", "Ly", "Chấn"),
    (22, "Bí", "Bi-Grace", "Cấn", "Ly"),
    (23, "Bác", "Bo", "Cấn", "Khôn"),
    (24, "Phục", "Fu", "Khôn", "Chấn"),
    (25, "Vô Vọng", "Wu Wang", "Càn", "Chấn"),
    (26, "Đại Súc", "Da Chu", "Cấn", "Càn"),
    (27, "Di", "Yi-Nourish", "Cấn", "Chấn"),
    (28, "Đại Quá", "Da Guo", "Đoài", "Tốn"),
    (29, "Tập Khảm", "Kan", "Khảm", "Khảm"),
    (30, "Ly", "Li", "Ly", "Ly"),
    (31, "Hàm", "Xian", "Đoài", "Cấn"),
    (32, "Hằng", "Heng", "Chấn", "Tốn"),
    (33, "Độn", "Dun", "Càn", "Cấn"),
    (34, "Đại Tráng", "Da Zhuang", "Chấn", "Càn"),
    (35, "Tấn", "Jin", "Ly", "Khôn"),
    (36, "Minh Di", "Ming Yi", "Khôn", "Ly"),
    (37, "Gia Nhân", "Jia Ren", "Tốn", "Ly"),
    (38, "Khuê", "Kui", "Ly", "Đoài"),
    (39, "Kiển", "Jian-Obstruction", "Khảm", "Cấn"),
    (40, "Giải", "Xie", "Chấn", "Khảm"),
    (41, "Tổn", "Sun-Decrease", "Cấn", "Đoài"),
    (42, "Ích", "Yi-Increase", "Tốn", "Chấn"),
    (43, "Quải", "Guai", "Đoài", "Càn"),
    (44, "Cấu", "Gou", "Càn", "Tốn"),
    (45, "Tụy", "Cui", "Đoài", "Khôn"),
    (46, "Thăng", "Sheng", "Khôn", "Tốn"),
    (47, "Khốn", "Kun-Oppression", "Đoài", "Khảm"),
    (48, "Tỉnh", "Jing", "Khảm", "Tốn"),
    (49, "Cách", "Ge", "Đoài", "Ly"),
    (50, "Đỉnh", "Ding", "Ly", "Tốn"),
    (51, "Chấn", "Zhen", "Chấn", "Chấn"),
    (52, "Cấn", "Gen", "Cấn", "Cấn"),
    (53, "Tiệm", "Jian-Gradual", "Tốn", "Cấn"),
    (54, "Quy Muội", "Gui Mei", "Chấn", "Đoài"),
    (55, "Phong", "Feng-Abundance", "Chấn", "Ly"),
    (56, "Lữ", "Lu-Wanderer", "Ly", "Cấn"),
    (57, "Tốn", "Xun", "Tốn", "Tốn"),
    (58, "Đoài", "Dui", "Đoài", "Đoài"),
    (59, "Hoán", "Huan", "Tốn", "Khảm"),
    (60, "Tiết", "Jie", "Khảm", "Đoài"),
    (61, "Trung Phu", "Zhong Fu", "Tốn", "Đoài"),
    (62, "Tiểu Quá", "Xiao Guo", "Chấn", "Cấn"),
    (63, "Ký Tế", "Ji Ji", "Khảm", "Ly"),
    (64, "Vị Tế", "Wei Ji", "Ly", "Khảm"),
)

NAME_ALIASES = {
    "kiền": "Kiền",
    "càn": "Kiền",
    "quẻ kiền": "Kiền",
    "quẻ càn": "Kiền",
    "khôn": "Khôn",
    "tỵ": "Tỷ",
    "quẻ tỵ": "Tỷ",
    "quy muội": "Quy Muội",
    "qui muội": "Quy Muội",
}


def _build_hexagrams() -> tuple[Hexagram, ...]:
    by_binary_id = {format(number, "06b"): number + 1 for number in range(64)}
    items: list[Hexagram] = []
    for king_wen_index, name_vi, name_en, upper_trigram, lower_trigram in KING_WEN_TABLE:
        binary = f"{TRIGRAM_BITS[upper_trigram]}{TRIGRAM_BITS[lower_trigram]}"
        items.append(
            Hexagram(
                id=by_binary_id[binary],
                king_wen_index=king_wen_index,
                binary=binary,
                name_vi=name_vi,
                name_en=name_en,
                upper_trigram=upper_trigram,
                lower_trigram=lower_trigram,
                source_ref=SOURCE_REF,
            )
        )
    return tuple(items)


HEXAGRAMS = _build_hexagrams()
_BY_BINARY = {item.binary: item for item in HEXAGRAMS}
_BY_NAME = {item.name_vi.lower(): item for item in HEXAGRAMS}
_BY_NAME.update({item.name_en.lower(): item for item in HEXAGRAMS})
for alias, canonical in NAME_ALIASES.items():
    if canonical.lower() in _BY_NAME:
        _BY_NAME[alias.lower()] = _BY_NAME[canonical.lower()]


def _validate_binary(binary: str) -> None:
    if len(binary) != 6 or any(char not in "01" for char in binary):
        raise ValueError("hexagram binary must contain exactly six 0/1 characters")


def compose_hexagram_binary(upper_trigram: str, lower_trigram: str) -> str:
    if upper_trigram not in TRIGRAM_BITS or lower_trigram not in TRIGRAM_BITS:
        raise KeyError("unknown trigram name")
    return f"{TRIGRAM_BITS[upper_trigram]}{TRIGRAM_BITS[lower_trigram]}"


def list_hexagrams() -> tuple[Hexagram, ...]:
    return HEXAGRAMS


def get_hexagram_by_binary(binary: str) -> Hexagram:
    _validate_binary(binary)
    return _BY_BINARY[binary]


def get_hexagram_by_name(name: str) -> Hexagram:
    key = name.strip().lower()
    if key not in _BY_NAME:
        raise KeyError(f"unknown hexagram name: {name}")
    return _BY_NAME[key]


def flip_line(binary: str, line: int) -> str:
    """Flip a line using Yi convention: line 1 is bottom, line 6 is top."""
    _validate_binary(binary)
    if line < 1 or line > 6:
        raise ValueError("line must be between 1 and 6")
    index = 6 - line
    replacement = "0" if binary[index] == "1" else "1"
    return binary[:index] + replacement + binary[index + 1 :]


def generate_transitions(binary: str) -> dict[int, str]:
    _validate_binary(binary)
    return {line: flip_line(binary, line) for line in range(1, 7)}


def apply_moving_lines(binary: str, moving_lines: Iterable[int]) -> str:
    _validate_binary(binary)
    transformed = binary
    deduped = sorted(set(moving_lines))
    for line in deduped:
        transformed = flip_line(transformed, line)
    return transformed


def classify_moving_lines(moving_lines: Iterable[int]) -> str:
    """
    Zhu Xi style summary for practical reporting:
    - 0 lines: read original hexagram judgement
    - 1-2 lines: focus moving line texts
    - 3 lines: read both original and transformed
    - 4-5 lines: focus transformed perspective
    - 6 lines: transformed hexagram takes precedence
    """
    count = len(set(moving_lines))
    if count == 0:
        return "original_judgement"
    if count <= 2:
        return "moving_line_texts"
    if count == 3:
        return "dual_hexagram_context"
    if count <= 5:
        return "transformed_focus"
    return "fully_transformed"


def yin_yang_ratio(binary: str) -> dict[str, float]:
    _validate_binary(binary)
    yang = binary.count("1") / 6
    return {"yin": 1 - yang, "yang": yang}


def hexagram_to_vector(binary: str) -> list[float]:
    _validate_binary(binary)
    ratios = yin_yang_ratio(binary)
    lines = [1.0 if char == "1" else 0.0 for char in binary]
    return lines + [ratios["yin"], ratios["yang"]]
