"""Chuẩn hóa tên + quy đổi chữ cái → số.

Bản địa hóa tiếng Việt (CHỐT 2026-06-05):
- Bỏ dấu thanh + dấu phụ (á→A, ê→E, ơ→O, ư→U, ...). Đ→D.
- Pythagoras map theo CHỮ LATIN GỐC ⇒ "có dấu" và "không dấu" cho CÙNG kết quả số
  (ô và o đều = O). Nên chuẩn hóa bỏ dấu là method chuẩn, không mất thông tin số học.
- KHÔNG tách ghép phụ âm (Ng/Nh/Tr/Ph/Th...): tính từng chữ Latin. "Nguyễn"=N-G-U-Y-E-N.
"""
from __future__ import annotations

import unicodedata

from .constants import PURE_VOWELS, letter_maps


def normalize_vietnamese(name: str) -> str:
    """'Nguyễn Văn An' → 'NGUYEN VAN AN' (A-Z + space). Đ→D, bỏ mọi dấu."""
    # Map Đ/đ trước (NFD không tách đ thành d + dấu).
    name = name.replace("Đ", "D").replace("đ", "d")
    # Tách dấu tổ hợp rồi bỏ ký tự combining (Mn = mark, nonspacing).
    decomposed = unicodedata.normalize("NFD", name)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    upper = stripped.upper()
    return "".join(c if c.isalpha() and c.isascii() else (" " if c.isspace() else "") for c in upper)


def letters_only(name: str) -> str:
    """Bỏ khoảng trắng — chỉ giữ A-Z đã chuẩn hóa."""
    return "".join(c for c in normalize_vietnamese(name) if c.isalpha())


def is_vowel(letters: str, index: int) -> bool:
    """Y-rule (xấp xỉ có ghi chú): A/E/I/O/U luôn nguyên âm.
    Y là nguyên âm khi KHÔNG kề trực tiếp một nguyên âm khác (đóng vai âm nguyên âm
    duy nhất: Lynn, Mary, Yvonne, Betty). Nếu kề nguyên âm khác → phụ âm (Maloney, Yoda).

    LƯU Ý: đây là heuristic engine (không syllabify hoàn hảo — vd 'Bryan').
    Số Sứ Mệnh (toàn bộ chữ) KHÔNG phụ thuộc rule này nên luôn vững;
    chỉ Soul Urge / Personality bị ảnh hưởng ở các tên hiếm có Y mơ hồ.
    """
    ch = letters[index]
    if ch in PURE_VOWELS:
        return True
    if ch != "Y":
        return False
    prev_is_vowel = index > 0 and letters[index - 1] in PURE_VOWELS
    next_is_vowel = index + 1 < len(letters) and letters[index + 1] in PURE_VOWELS
    return not (prev_is_vowel or next_is_vowel)


def letter_value(ch: str, system: str = "pythagorean") -> int:
    """Giá trị 1 chữ cái. Chaldean không có số 9 (→ trả 0 nếu thiếu)."""
    return letter_maps()[system].get(ch.upper(), 0)


def name_breakdown(name: str, system: str = "pythagorean") -> list[dict]:
    """Phân rã từng chữ: {letter, value, is_vowel}. Dùng cho transparency UI + debug."""
    letters = letters_only(name)
    out: list[dict] = []
    for i, ch in enumerate(letters):
        out.append(
            {
                "letter": ch,
                "value": letter_value(ch, system),
                "is_vowel": is_vowel(letters, i),
            }
        )
    return out
