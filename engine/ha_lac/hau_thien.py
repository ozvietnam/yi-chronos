"""Derive Hậu thiên quái (後天卦) from Tiên thiên + nguyên đường.

Rules (Chen Tuan / Học Năng canon):
1. Flip the nguyên đường line's polarity (yang↔yin) in Tiên thiên.
2. Swap upper and lower trigrams.
3. Recompute nguyên đường for the new hexagram (same birth-hour rule).

Special case (low-confidence):
- Chí-tôn-quái (Khảm-vi-Thủy #29, Thủy-Lôi Truân #3, Thủy-Sơn Kiển #39) at
  nguyên đường line 5 or 6 — sources give variant tables; v1 flags but proceeds
  with standard transformation. Manual scholar review recommended.
"""

from __future__ import annotations

from core.hexagram import get_hexagram_by_binary

from .nguyen_duong import nguyen_duong_line
from .quai_assembly import TRIGRAM_BINARY, HexagramRef


CHI_TON_KING_WEN: frozenset[int] = frozenset({29, 3, 39})


# Inverse map: 3-bit binary → trigram name
BINARY_TO_TRIGRAM: dict[str, str] = {v: k for k, v in TRIGRAM_BINARY.items()}


def _flip_line(binary_top_down: str, line_position_1based: int) -> str:
    """Flip the polarity of one yao (1-indexed bottom-up) in a top-down binary string."""
    idx = 6 - line_position_1based   # bottom = string index 5, top = index 0
    chars = list(binary_top_down)
    chars[idx] = "1" if chars[idx] == "0" else "0"
    return "".join(chars)


def derive_hau_thien(
    tien_thien: HexagramRef,
    nguyen_duong_tien: int,
    hour_branch: str,
) -> tuple[HexagramRef, int, list[str]]:
    """Derive Hậu thiên from Tiên thiên + nguyên đường.

    Returns (HexagramRef, nguyen_duong_hau_thien, notes).
    """
    notes: list[str] = []
    tien_bin = tien_thien.binary_top_down

    # Step 1: flip nguyên đường line.
    flipped = _flip_line(tien_bin, nguyen_duong_tien)

    # Special-case flag: chí-tôn-quái + line 5/6 nguyên đường.
    if tien_thien.king_wen_index in CHI_TON_KING_WEN and nguyen_duong_tien in (5, 6):
        notes.append(
            f"Cảnh báo: Tiên thiên là chí-tôn-quái (Khảm/Truân/Kiển) "
            f"với nguyên đường hào {nguyen_duong_tien} — truyền thống cổ có bảng "
            "biến đổi đặc biệt, sách Học Năng và sách Trung Quốc khác biệt. "
            "Phiên bản này dùng quy tắc cơ bản (lật + đổi thượng/hạ) — "
            "khuyến nghị tham vấn bậc thầy nếu kết quả không khớp với sách."
        )

    # Step 2: swap upper and lower trigrams.
    new_upper = flipped[3:6]   # old lower becomes new upper
    new_lower = flipped[0:3]   # old upper becomes new lower
    new_binary = new_upper + new_lower

    new_upper_name = BINARY_TO_TRIGRAM[new_upper]
    new_lower_name = BINARY_TO_TRIGRAM[new_lower]
    hex_obj = get_hexagram_by_binary(new_binary)

    hau_thien = HexagramRef(
        king_wen_index=hex_obj.king_wen_index,
        name_vi=hex_obj.name_vi,
        binary_top_down=new_binary,
        upper_trigram=new_upper_name,
        lower_trigram=new_lower_name,
        tien_number_reduced=tien_thien.tien_number_reduced,
        dia_number_reduced=tien_thien.dia_number_reduced,
        upper_source="derived_from_tien_thien",
        notes=notes,
    )

    # Step 3: nguyên đường for Hậu thiên.
    nguyen_duong_hau, hau_notes = nguyen_duong_line(new_binary, hour_branch)
    notes.extend(hau_notes)

    return hau_thien, nguyen_duong_hau, notes
