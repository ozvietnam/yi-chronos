"""Assemble Tiên thiên hexagram from reduced Thiên/Địa numbers.

Rules (Học Năng / Chen Tuan canon):
- Number → trigram via Lạc Thư map (1=Khảm, 2=Khôn, ..., 9=Ly, 5=centre).
- Upper/lower assignment by gender × year-stem polarity:
    * Dương nam / Âm nữ: Thiên → upper, Địa → lower
    * Âm nam / Dương nữ: Địa → upper, Thiên → lower
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.hexagram import get_hexagram_by_binary

from .constants import (
    FIVE_FALLBACK_YANG,
    FIVE_FALLBACK_YIN,
    NUMBER_TO_TRIGRAM,
    YANG_STEMS,
)


# Top-down 3-bit binary per trigram (matches core.hexagram convention)
TRIGRAM_BINARY: dict[str, str] = {
    "Càn":  "111",
    "Đoài": "011",
    "Ly":   "101",
    "Chấn": "001",
    "Tốn":  "110",
    "Khảm": "010",
    "Cấn":  "100",
    "Khôn": "000",
}


@dataclass(frozen=True)
class HexagramRef:
    """A hexagram with full provenance for Hà Lạc."""

    king_wen_index: int
    name_vi: str
    binary_top_down: str
    upper_trigram: str
    lower_trigram: str
    tien_number_reduced: int   # 1..9 (or 5/0)
    dia_number_reduced: int
    upper_source: str          # 'thien' or 'dia'
    notes: list[str]           # any flagged caveats (5 jì-gōng, edge cases)

    def to_dict(self) -> dict:
        return asdict(self)


def number_to_trigram(n: int, prefer_yang: bool, notes: list[str]) -> str:
    """Map a reduced number to a trigram, handling 5 jì-gōng fallback."""
    if n == 5 or n == 0:
        # Centre palace — low-confidence fallback per Vietnamese popular convention.
        fallback = FIVE_FALLBACK_YANG if prefer_yang else FIVE_FALLBACK_YIN
        notes.append(
            f"Số rút gọn = {n} (trung cung 5 jì-gōng) — dùng dự phòng {fallback}. "
            "Truyền thống cổ chuẩn cần Tam-nguyên (上/中/下元) — đánh giá thấp tin cậy."
        )
        return fallback
    if n not in NUMBER_TO_TRIGRAM:
        raise ValueError(f"Cannot map number {n} to trigram")
    return NUMBER_TO_TRIGRAM[n]


def assemble_tien_thien(
    pools_tien_reduced: int,
    pools_dia_reduced: int,
    year_stem: str,
    gender: str,
) -> HexagramRef:
    """Build the Tiên thiên (先天) hexagram from number pools and birth metadata."""
    notes: list[str] = []
    year_is_yang = year_stem in YANG_STEMS

    # Tradition: Dương nam / Âm nữ → Thiên upper; Âm nam / Dương nữ → Địa upper.
    if (year_is_yang and gender == "nam") or (not year_is_yang and gender == "nữ"):
        upper_source = "thien"
        upper_trigram = number_to_trigram(pools_tien_reduced, prefer_yang=True, notes=notes)
        lower_trigram = number_to_trigram(pools_dia_reduced, prefer_yang=False, notes=notes)
    else:
        upper_source = "dia"
        upper_trigram = number_to_trigram(pools_dia_reduced, prefer_yang=False, notes=notes)
        lower_trigram = number_to_trigram(pools_tien_reduced, prefer_yang=True, notes=notes)

    upper_bin = TRIGRAM_BINARY[upper_trigram]
    lower_bin = TRIGRAM_BINARY[lower_trigram]
    binary = upper_bin + lower_bin
    hex_obj = get_hexagram_by_binary(binary)

    return HexagramRef(
        king_wen_index=hex_obj.king_wen_index,
        name_vi=hex_obj.name_vi,
        binary_top_down=binary,
        upper_trigram=upper_trigram,
        lower_trigram=lower_trigram,
        tien_number_reduced=pools_tien_reduced,
        dia_number_reduced=pools_dia_reduced,
        upper_source=upper_source,
        notes=notes,
    )
