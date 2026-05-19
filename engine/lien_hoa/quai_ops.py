"""Primitives for building Chánh / Hổ / Biến quái + line indexing.

All indexing follows book convention:
- Lines numbered 1..6 bottom-up (hào 1 dưới cùng, hào 6 trên cùng).
- Lines 1..3 thuộc hạ quái, lines 4..6 thuộc thượng quái.
- "Hổ quái" lấy hào [5,4,3] làm thượng, hào [4,3,2] làm hạ — i.e. middle 4 lines.

Internal binary string is top-down (index 0 = line 6, index 5 = line 1), matching
core.hexagram.get_hexagram_by_binary.
"""

from __future__ import annotations

from core.hexagram import get_hexagram_by_binary

from .constants import TIEN_THIEN_TRIGRAMS, TRIGRAM_BITS


def mod_quai(value: int) -> int:
    """Map any positive integer to 1..8 (Tiên thiên quái số).

    Book rule (p.5): if value ≤ 8 → as-is. If > 8 → chia 8 lấy dư số. Dư số = 0 → 8.
    """
    rem = value % 8
    return rem if rem != 0 else 8


def mod_hao(value: int) -> int:
    """Map any positive integer to 1..6 (hào số). Dư số = 0 → 6."""
    rem = value % 6
    return rem if rem != 0 else 6


def trigram_from_num(num: int) -> str:
    """1..8 → Tiên thiên trigram name."""
    if not (1 <= num <= 8):
        raise ValueError(f"trigram num must be 1..8, got {num}")
    return TIEN_THIEN_TRIGRAMS[num - 1]


def chanh_binary(upper_num: int, lower_num: int) -> str:
    """Top-down 6-bit binary of Chánh quái — upper trên, lower dưới."""
    upper = trigram_from_num(upper_num)
    lower = trigram_from_num(lower_num)
    return TRIGRAM_BITS[upper] + TRIGRAM_BITS[lower]


def ho_binary(chanh_bin: str) -> str:
    """Hổ quái: upper from lines [5,4,3], lower from lines [4,3,2] of chánh.

    Top-down indices of chánh: 0=line6, 1=line5, 2=line4, 3=line3, 4=line2, 5=line1.
    So line[5,4,3] = chanh[1,2,3], line[4,3,2] = chanh[2,3,4].
    """
    if len(chanh_bin) != 6:
        raise ValueError("chanh_bin must be 6 chars")
    return chanh_bin[1] + chanh_bin[2] + chanh_bin[3] + chanh_bin[2] + chanh_bin[3] + chanh_bin[4]


def flip_hao(chanh_bin: str, hao_num: int) -> str:
    """Flip one line (1..6 bottom-up) of chánh to produce Biến quái binary."""
    if not (1 <= hao_num <= 6):
        raise ValueError(f"hao_num must be 1..6, got {hao_num}")
    idx_top_down = 6 - hao_num
    curr = chanh_bin[idx_top_down]
    flipped = "0" if curr == "1" else "1"
    return chanh_bin[:idx_top_down] + flipped + chanh_bin[idx_top_down + 1:]


def upper_trigram_of(binary: str) -> str:
    """Extract the upper trigram (top 3 lines) name from a 6-bit binary."""
    bits = binary[:3]
    for name, t_bits in TRIGRAM_BITS.items():
        if t_bits == bits:
            return name
    raise ValueError(f"unknown trigram bits: {bits}")


def lower_trigram_of(binary: str) -> str:
    bits = binary[3:]
    for name, t_bits in TRIGRAM_BITS.items():
        if t_bits == bits:
            return name
    raise ValueError(f"unknown trigram bits: {bits}")


def hao_side(hao_num: int) -> str:
    """Return 'upper' if hào in upper trigram (4-6), else 'lower'."""
    return "upper" if hao_num in (4, 5, 6) else "lower"


def hexagram_info(binary: str) -> dict:
    """Look up hexagram metadata by binary."""
    hx = get_hexagram_by_binary(binary)
    return {
        "name_vi": hx.name_vi,
        "name_en": hx.name_en,
        "king_wen_index": hx.king_wen_index,
        "binary": hx.binary,
        "upper_trigram": hx.upper_trigram,
        "lower_trigram": hx.lower_trigram,
    }
