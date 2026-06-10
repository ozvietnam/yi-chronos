"""3 Vòng lớn — Cụ Thiên Lương p7.

Lá số Tử Vi gồm 3 vòng lớn chi phối số mệnh:

1. **Vòng Lộc Tồn** (an theo Can) = HẠNH PHÚC, tài lộc, hưởng thụ
2. **Vòng Thái Tuế** (an theo Chi) = VỊ TRÍ XÃ HỘI, vị thế "tứ thế"
3. **Vòng Tràng Sinh** (an theo Cục Mệnh) = CHÍNH ĐƯƠNG SỐ (Thân, năng lực thực)

Tổng quan: Thiên (Lộc Tồn) - Địa (Thái Tuế) - Nhân (Tràng Sinh).

Em chỉ wire OVERVIEW + index — chi tiết an sao đã có sẵn ở engine/tu_vi/an_sao.py.
Mục đích module này: tổng hợp 3 vòng vào 1 dict, render trong UI.

Nguồn: tlnl.S1.Q08, tlnl.S6.Q91 ("3 vòng xương sống")
"""
from __future__ import annotations

VONG_NAMES = {
    "loc_ton":    "Vòng Lộc Tồn (Thiên) — hạnh phúc, tài lộc",
    "thai_tue":   "Vòng Thái Tuế (Địa) — vị trí xã hội, vị thế tứ thế",
    "trang_sinh": "Vòng Tràng Sinh (Nhân) — chính đương số, năng lực thân",
}

CITATION = "Cụ Thiên Lương Nghiệm Lý p7, p154 (3 vòng xương sống)"


def vong_loc_ton(can: str) -> dict:
    """Index of Lộc Tồn an theo Can."""
    from .tam_hop_loc import LOC_TON_VI_TRI
    chi = LOC_TON_VI_TRI.get(can.lower())
    return {
        "name": "Lộc Tồn",
        "vi_tri": chi,
        "mo_ta": "Hạnh phúc / tài lộc tự nhiên",
        "citation": CITATION,
    }


def vong_thai_tue(chi: str) -> dict:
    """Vòng Thái Tuế an theo Chi năm sinh (tự đứng tại cung chi đó)."""
    return {
        "name": "Thái Tuế",
        "vi_tri": chi.lower(),
        "mo_ta": "Vị trí xã hội, chính nghĩa, hành động nêu cao",
        "citation": CITATION,
    }


def vong_trang_sinh(cuc: str, gender: str = "M") -> dict:
    """Vòng Tràng Sinh an theo Cục Mệnh (Thủy Nhị/Mộc Tam/Kim Tứ/Thổ Ngũ/Hỏa Lục cục).

    Args:
        cuc: canonical (vd "thuy_nhi_cuc", "moc_tam_cuc", ...)
        gender: "M" or "F" — ảnh hưởng chiều thuận/nghịch của vòng

    Returns:
        dict overview
    """
    return {
        "name": "Tràng Sinh",
        "cuc": cuc.lower(),
        "gender": gender,
        "mo_ta": "Chính đương số, năng lực thực của Thân",
        "citation": CITATION,
    }


def ba_vong_lon(can: str, chi: str, cuc: str, gender: str = "M") -> dict:
    """Tổng hợp 3 vòng lớn của lá số.

    Args:
        can: Can năm sinh (vd "giap", "mau", ...)
        chi: Chi năm sinh (vd "ngo", "tuat", ...)
        cuc: Cục Mệnh (vd "thuy_nhi_cuc", ...)
        gender: "M" or "F"

    Returns:
        dict {loc_ton, thai_tue, trang_sinh, citation}
    """
    return {
        "loc_ton":    vong_loc_ton(can),
        "thai_tue":   vong_thai_tue(chi),
        "trang_sinh": vong_trang_sinh(cuc, gender),
        "paradigm":   "3 vòng xương sống Thiên-Địa-Nhân",
        "citation":   CITATION,
    }
