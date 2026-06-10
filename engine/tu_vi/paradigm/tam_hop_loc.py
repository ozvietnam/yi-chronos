"""Tam Hợp Tuổi hưởng Lộc Tồn — Cụ Thiên Lương p9.

Mỗi Can có Lộc Tồn an ở 1 chi cụ thể. Tam hợp của chi đó = 3 tuổi cùng hưởng
Lộc Tồn (tâm thái phú quý). Người sinh năm tuổi nằm trong tam hợp ấy được
"hạnh phúc do định mệnh phác hoạ".

Ví dụ: Tuổi Giáp → Lộc Tồn ở Dần → tam hợp Dần-Ngọ-Tuất hưởng Lộc Tồn.
Tuổi Canh → Lộc Tồn ở Thân → tam hợp Thân-Tý-Thìn hưởng Lộc Tồn.

Nguồn: tlnl.S1.Q62-Q65
"""
from __future__ import annotations

# Mapping: Can → chi an Lộc Tồn
LOC_TON_VI_TRI: dict[str, str] = {
    "giap": "dan",   # Lộc Tồn an Dần
    "at":   "mao",
    "binh": "ti",    # Tỵ
    "dinh": "ngo",
    "mau":  "ti",    # Đồng Bính
    "ky":   "ngo",   # Đồng Đinh
    "canh": "than",
    "tan":  "dau",
    "nham": "hoi",
    "quy":  "ty",    # Tý
}

# Tam hợp 4 cục
TAM_HOP_THUY = ["than", "ty", "thin"]   # Thân Tý Thìn — Thủy cục
TAM_HOP_HOA  = ["dan", "ngo", "tuat"]   # Dần Ngọ Tuất — Hỏa cục
TAM_HOP_KIM  = ["ti", "dau", "suu"]     # Tỵ Dậu Sửu — Kim cục
TAM_HOP_MOC  = ["hoi", "mao", "mui"]    # Hợi Mão Mùi — Mộc cục

CHI_TO_TAM_HOP: dict[str, list[str]] = {}
for cuc in [TAM_HOP_THUY, TAM_HOP_HOA, TAM_HOP_KIM, TAM_HOP_MOC]:
    for chi in cuc:
        CHI_TO_TAM_HOP[chi] = cuc

# Final mapping: Can → tam hợp tuổi hưởng Lộc Tồn
LOC_TON_TAM_HOP_BY_CAN: dict[str, list[str]] = {
    can: CHI_TO_TAM_HOP.get(chi, [chi])
    for can, chi in LOC_TON_VI_TRI.items()
}

CITATION = "Cụ Thiên Lương Nghiệm Lý p9 (atoms tlnl.S1.Q62-Q65)"


def tam_hop_loc_ton(can: str, chi: str) -> tuple[bool, str, str]:
    """Check nếu tuổi (can+chi) thuộc tam hợp hưởng Lộc Tồn của can đó.

    Args:
        can: canonical can name của năm sinh
        chi: canonical chi name của năm sinh

    Returns:
        (huong_loc, msg, citation)
    """
    can_norm = can.lower().strip()
    chi_norm = chi.lower().strip()

    tam_hop = LOC_TON_TAM_HOP_BY_CAN.get(can_norm)
    if not tam_hop:
        return False, f"không xác định can: {can}", CITATION

    loc_ton_chi = LOC_TON_VI_TRI[can_norm]
    if chi_norm in tam_hop:
        return True, (
            f"✓ Tuổi {can} {chi} thuộc tam hợp {'-'.join(tam_hop)} "
            f"→ HƯỞNG Lộc Tồn (an Lộc Tồn tại {loc_ton_chi}). "
            f"Hạnh phúc do định mệnh phác hoạ."
        ), CITATION

    return False, (
        f"Tuổi {can} {chi} KHÔNG thuộc tam hợp {'-'.join(tam_hop)} "
        f"→ không hưởng Lộc Tồn tự nhiên. "
        f"Cần luận thêm vòng Thái Tuế + Tràng Sinh."
    ), CITATION
