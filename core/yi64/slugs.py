"""Hexagram slug helpers — encode 64 quẻ into shareable URL-safe slugs.

Convention (matches kabala.vn community style):
    {king_wen}-{upper_element}-{lower_element}-{name_no_diacritics}

Examples:
    Quẻ 1 (Kiền, Càn/Càn)     → "1-thien-thien-kien"
    Quẻ 3 (Truân, Khảm/Chấn)  → "3-thuy-loi-truan"
    Quẻ 11 (Thái, Khôn/Càn)   → "11-dia-thien-thai"

Element naming follows the "elemental" tradition used in Vietnamese hexagram naming:
    Càn → Thiên, Đoài → Trạch, Ly → Hỏa, Chấn → Lôi,
    Tốn → Phong, Khảm → Thủy, Cấn → Sơn, Khôn → Địa.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache

from core.hexagram import HEXAGRAMS


# Trigram → elemental name (used in 上卦下卦 naming convention).
TRIGRAM_ELEMENT_VI: dict[str, str] = {
    "Càn": "Thiên",
    "Đoài": "Trạch",
    "Ly": "Hỏa",
    "Chấn": "Lôi",
    "Tốn": "Phong",
    "Khảm": "Thủy",
    "Cấn": "Sơn",
    "Khôn": "Địa",
}


def _strip_diacritics(text: str) -> str:
    """Remove Vietnamese diacritics; convert 'đ' → 'd'."""
    nfkd = unicodedata.normalize("NFD", text)
    no_marks = "".join(c for c in nfkd if not unicodedata.combining(c))
    return no_marks.replace("đ", "d").replace("Đ", "D")


def to_slug_segment(text: str) -> str:
    """Normalize a Vietnamese segment to URL-safe slug.

    'Thủy' → 'thuy'; 'Đại Hữu' → 'dai-huu'.
    """
    plain = _strip_diacritics(text).lower()
    # Replace any non-alphanumeric with dash, collapse repeats.
    out: list[str] = []
    prev_dash = False
    for ch in plain:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append("-")
            prev_dash = True
    return "".join(out).strip("-")


@lru_cache(maxsize=1)
def slug_table() -> dict[int, str]:
    """Build {king_wen_index: slug} for all 64 hexagrams."""
    out: dict[int, str] = {}
    for h in HEXAGRAMS:
        kw = h.king_wen_index
        upper_el = TRIGRAM_ELEMENT_VI.get(h.upper_trigram, h.upper_trigram)
        lower_el = TRIGRAM_ELEMENT_VI.get(h.lower_trigram, h.lower_trigram)
        slug = (
            f"{kw}-"
            f"{to_slug_segment(upper_el)}-"
            f"{to_slug_segment(lower_el)}-"
            f"{to_slug_segment(h.name_vi)}"
        )
        out[kw] = slug
    return out


@lru_cache(maxsize=1)
def reverse_slug_table() -> dict[str, int]:
    """Build {slug: king_wen_index} for fast lookup."""
    return {slug: kw for kw, slug in slug_table().items()}


def slug_for(king_wen: int) -> str:
    """Get the slug for a given King-Wen number (1..64)."""
    table = slug_table()
    if king_wen not in table:
        raise ValueError(f"Invalid King-Wen number: {king_wen}")
    return table[king_wen]


def king_wen_from_slug(slug: str) -> int | None:
    """Resolve a slug back to its King-Wen number, or None if unknown.

    Tolerant matching:
    - Strips trailing/leading dashes.
    - Tries exact match first.
    - Then tries match by leading integer prefix (e.g. "3-anything" → 3).
    """
    if not slug:
        return None
    s = slug.strip().strip("-").lower()
    table = reverse_slug_table()
    if s in table:
        return table[s]
    # Fallback: split on first dash, parse leading int.
    prefix, _, _ = s.partition("-")
    if prefix.isdigit():
        kw = int(prefix)
        if 1 <= kw <= 64:
            return kw
    return None
