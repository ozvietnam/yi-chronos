"""Hỗ Quái (互卦) — Interlocked hexagram derivation.

Paradigm Xuân Cang (Bát Tự Hà Lạc & Quỹ đạo đời người, p4):
> "Từ hai quẻ Tiên Thiên và Hậu Thiên tìm ra hai quẻ Hỗ (trong nhóm
>  từ hỗ trợ) phản ánh bổ sung cho hai quẻ nói trên."

Hỗ quái rule (kinh điển):
Cho 1 quẻ 6 hào, đếm từ dưới lên (1=initial, 6=top):
- **Nội Hỗ (Lower Nuclear)** = hào 2, 3, 4
- **Ngoại Hỗ (Upper Nuclear)** = hào 3, 4, 5

Hỗ quái 6 hào = [hào2, hào3, hào4, hào3, hào4, hào5] đọc từ dưới.

Ví dụ: Quẻ Tiết (節) binary top-down = "010011"
       → bottom-up = "110010" → hào 1=1, 2=1, 3=0, 4=0, 5=1, 6=0
       → Nội Hỗ = (2,3,4) = (1,0,0) → Cấn (山)
       → Ngoại Hỗ = (3,4,5) = (0,0,1) → Chấn (雷)
       → Hỗ Quái = Chấn trên Cấn dưới = Lôi Sơn Tiểu Quá (小過)

⚠️ Hỗ quái BỔ SUNG ý nghĩa cho quẻ chính — không thay thế.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


# Map 3-bit binary (top-down, "abc") → Bát Quái name
TRIGRAM_FROM_BINARY: dict[str, str] = {
    "111": "Càn",   # ☰ Thiên
    "110": "Đoài",  # ☱ Trạch
    "101": "Ly",    # ☲ Hỏa
    "100": "Chấn",  # ☳ Lôi
    "011": "Tốn",   # ☴ Phong
    "010": "Khảm",  # ☵ Thủy
    "001": "Cấn",   # ☶ Sơn
    "000": "Khôn",  # ☷ Địa
}

# Trigram name → Element + Tượng
TRIGRAM_META: dict[str, dict] = {
    "Càn": {"element": "kim", "tuong": "Thiên (Trời)", "polarity": "dương"},
    "Đoài": {"element": "kim", "tuong": "Trạch (Đầm)", "polarity": "âm"},
    "Ly": {"element": "hỏa", "tuong": "Hỏa (Lửa)", "polarity": "âm"},
    "Chấn": {"element": "mộc", "tuong": "Lôi (Sấm)", "polarity": "dương"},
    "Tốn": {"element": "mộc", "tuong": "Phong (Gió)", "polarity": "âm"},
    "Khảm": {"element": "thủy", "tuong": "Thủy (Nước)", "polarity": "dương"},
    "Cấn": {"element": "thổ", "tuong": "Sơn (Núi)", "polarity": "dương"},
    "Khôn": {"element": "thổ", "tuong": "Địa (Đất)", "polarity": "âm"},
}


@dataclass(frozen=True)
class HoQuaiResult:
    """Hỗ quái + meta."""

    source_quai: str               # tên quẻ gốc (Tiết, Tập Khảm, ...)
    source_binary: str             # binary top-down quẻ gốc
    noi_ho_trigram: str            # Nội Hỗ trigram
    ngoai_ho_trigram: str          # Ngoại Hỗ trigram
    ho_binary: str                 # binary top-down quẻ Hỗ
    ho_name_vi: str | None         # tên quẻ Hỗ (lookup từ 64 quẻ)
    noi_ho_element: str
    ngoai_ho_element: str
    narrative: str

    def to_dict(self) -> dict:
        return asdict(self)


def derive_ho_quai(source_binary_top_down: str, source_name: str = "") -> HoQuaiResult:
    """Tính Hỗ quái từ 1 quẻ 6 hào.

    Args:
        source_binary_top_down: 6 ký tự "0"/"1", đọc từ TRÊN xuống dưới
            (vd "010011" = hào 6=0, hào 5=1, hào 4=0, hào 3=0, hào 2=1, hào 1=1)
        source_name: tên quẻ gốc (optional)

    Returns: HoQuaiResult
    """
    if len(source_binary_top_down) != 6 or not all(c in "01" for c in source_binary_top_down):
        raise ValueError(f"Invalid binary: {source_binary_top_down}")

    # Convert top-down → bottom-up to access hào 1, 2, 3, 4, 5, 6
    bu = source_binary_top_down[::-1]  # "010011" → "110010"
    hao = [bu[i] for i in range(6)]    # hao[0]=hào 1, hao[1]=hào 2, ...

    # Nội Hỗ = hào (2, 3, 4) đọc bottom-up = "hao[1], hao[2], hao[3]"
    # Trigram binary (top-down): top hào (4) trước, đáy hào (2) sau
    noi_ho_binary_td = hao[3] + hao[2] + hao[1]
    # Ngoại Hỗ = hào (3, 4, 5)
    ngoai_ho_binary_td = hao[4] + hao[3] + hao[2]

    noi_ho_trigram = TRIGRAM_FROM_BINARY.get(noi_ho_binary_td, "?")
    ngoai_ho_trigram = TRIGRAM_FROM_BINARY.get(ngoai_ho_binary_td, "?")

    # Hỗ quái binary 6 hào = ngoại + nội (top-down)
    ho_binary_td = ngoai_ho_binary_td + noi_ho_binary_td

    # Lookup tên quẻ Hỗ
    ho_name_vi = _lookup_hexagram_by_binary(ho_binary_td)

    noi_ho_meta = TRIGRAM_META.get(noi_ho_trigram, {})
    ngoai_ho_meta = TRIGRAM_META.get(ngoai_ho_trigram, {})

    narrative = (
        f"**Hỗ quái của {source_name or source_binary_top_down}**:\n\n"
        f"- Nội Hỗ (hào 2-3-4) = **{noi_ho_trigram}** ({noi_ho_meta.get('tuong','?')}) — "
        f"hành {noi_ho_meta.get('element','?').title()}\n"
        f"- Ngoại Hỗ (hào 3-4-5) = **{ngoai_ho_trigram}** ({ngoai_ho_meta.get('tuong','?')}) — "
        f"hành {ngoai_ho_meta.get('element','?').title()}\n"
        f"- Hỗ Quái = **{ngoai_ho_trigram}-{noi_ho_trigram}**"
        + (f" = {ho_name_vi}" if ho_name_vi else "") + "\n\n"
        f"Theo Xuân Cang: 'Hỗ quái phản ánh BỔ SUNG cho quẻ chính' — đây là KHÍ ẨN "
        "bên trong quẻ, dòng chảy ngầm dưới biểu hiện rõ ràng."
    )

    return HoQuaiResult(
        source_quai=source_name or "?",
        source_binary=source_binary_top_down,
        noi_ho_trigram=noi_ho_trigram,
        ngoai_ho_trigram=ngoai_ho_trigram,
        ho_binary=ho_binary_td,
        ho_name_vi=ho_name_vi,
        noi_ho_element=noi_ho_meta.get("element", "?"),
        ngoai_ho_element=ngoai_ho_meta.get("element", "?"),
        narrative=narrative,
    )


_HEXAGRAM_CACHE: dict[str, str] | None = None


def _lookup_hexagram_by_binary(binary_td: str) -> str | None:
    """Lookup tên 64 quẻ từ binary top-down. Load từ data/seeds/hexagrams_master.json."""
    global _HEXAGRAM_CACHE
    if _HEXAGRAM_CACHE is None:
        import json
        from pathlib import Path
        try:
            data_path = Path(__file__).resolve().parent.parent.parent / "data" / "seeds" / "hexagrams_master.json"
            if data_path.exists():
                with open(data_path, encoding="utf-8") as f:
                    data = json.load(f)
                _HEXAGRAM_CACHE = {
                    rec["binary"]: rec["name_vi"]
                    for rec in data.get("records", [])
                    if "binary" in rec and "name_vi" in rec
                }
            else:
                _HEXAGRAM_CACHE = {}
        except Exception:
            _HEXAGRAM_CACHE = {}
    return _HEXAGRAM_CACHE.get(binary_td)
