"""5 Bậc Tuổi Can-Chi paradigm — Cụ Thiên Lương Nghiệm Lý Toàn Thư p7-10.

Phép tính bậc tuổi dựa trên sinh-khắc Ngũ Hành giữa Can và Chi của năm sinh.

- Bậc 1: Can sinh Chi = PHÚC ĐỨC LỚN, căn bản hơn người
- Bậc 2: Can = Chi = vững chắc, năng lực khá đầy đủ
- Bậc 3: Chi sinh Can = may nhiều hơn thực lực
- Bậc 4: Can khắc Chi = đời gặp nhiều trở lực
- Bậc 5: Chi khắc Can = NGHỊCH CẢNH ĐẦY RẪY CHUA CAY

> "Can là gốc là Phúc đức, Chi là ngọn là Thân thế." — Thiên Lương p11

Case kinh điển: Trương Lương Giáp Ngọ (bậc 1) vs Hàn Tín Giáp Tuất (bậc 4).
Cùng tuổi Giáp, cùng đắc Tử Phủ Sát Phá Tham + tam hợp Thái Tuế, nhưng
cuộc đời khác hẳn vì bậc tuổi khác.
"""
from __future__ import annotations

CAN_NGU_HANH: dict[str, str] = {
    "giap": "moc", "at": "moc",
    "binh": "hoa", "dinh": "hoa",
    "mau": "tho", "ky": "tho",
    "canh": "kim", "tan": "kim",
    "nham": "thuy", "quy": "thuy",
}

CHI_NGU_HANH: dict[str, str] = {
    "ty": "thuy", "hoi": "thuy",
    "dan": "moc", "mao": "moc",
    "ngo": "hoa", "tÿ": "hoa", "ti": "hoa",  # Tỵ = ti or tÿ
    "than": "kim", "dau": "kim",
    "thin": "tho", "tuat": "tho", "suu": "tho", "mui": "tho",
}

# Quan hệ sinh-khắc Ngũ Hành (a → b)
NGU_HANH_SINH = {("moc","hoa"), ("hoa","tho"), ("tho","kim"), ("kim","thuy"), ("thuy","moc")}
NGU_HANH_KHAC = {("moc","tho"), ("tho","thuy"), ("thuy","hoa"), ("hoa","kim"), ("kim","moc")}

BAC_TUOI_NAMES: dict[int, str] = {
    1: "Can sinh Chi — phúc đức quá lớn, căn bản hơn người",
    2: "Can = Chi — năng lực khá đầy đủ, vững chắc",
    3: "Chi sinh Can — đời gặp may nhiều hơn thực lực",
    4: "Can khắc Chi — đời gặp nhiều trở lực",
    5: "Chi khắc Can — nghịch cảnh đầy rẫy chua cay",
}

CITATION = "Cụ Thiên Lương Nghiệm Lý p7-10 (atoms tlnl.S1.Q12-Q17)"


def bac_tuoi(can: str, chi: str) -> tuple[int, str, str]:
    """Tính bậc tuổi từ Can + Chi.

    Args:
        can: canonical can name (vd "giap", "at", ..., "quy")
        chi: canonical chi name (vd "ty", "suu", ..., "hoi")

    Returns:
        (bac: int 1-5, name: str, citation: str)
    """
    can_norm = can.lower().strip()
    chi_norm = chi.lower().strip()

    can_h = CAN_NGU_HANH.get(can_norm)
    chi_h = CHI_NGU_HANH.get(chi_norm)

    if not can_h or not chi_h:
        return 0, f"không xác định can/chi: {can}/{chi}", CITATION

    # Bậc 2: đồng hành
    if can_h == chi_h:
        return 2, BAC_TUOI_NAMES[2], CITATION

    # Bậc 1: Can sinh Chi
    if (can_h, chi_h) in NGU_HANH_SINH:
        return 1, BAC_TUOI_NAMES[1], CITATION

    # Bậc 4: Can khắc Chi
    if (can_h, chi_h) in NGU_HANH_KHAC:
        return 4, BAC_TUOI_NAMES[4], CITATION

    # Bậc 3: Chi sinh Can
    if (chi_h, can_h) in NGU_HANH_SINH:
        return 3, BAC_TUOI_NAMES[3], CITATION

    # Bậc 5: Chi khắc Can
    if (chi_h, can_h) in NGU_HANH_KHAC:
        return 5, BAC_TUOI_NAMES[5], CITATION

    return 0, "không match pattern Ngũ Hành", CITATION
