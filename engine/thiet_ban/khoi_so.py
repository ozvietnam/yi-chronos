"""KHỞI SỐ Thiết Bản — NỀN SỐ kiểm-được (Hà Đồ – Lạc Thư) của phép 起数.

⚠ ĐÂY KHÔNG phải engine "bát tự → số điều văn". Phần ráp số (八卦加则) + 考刻
(neo khắc bằng bát tự cha mẹ + sự kiện đời) là khẩu quyết bí truyền / OCR mờ và
KHÔNG có cặp kiểm để validate → KHÔNG cơ học hoá ở đây (tránh bói giả-chính-xác,
Iron Rule #4/#6/#8). Xem `docs/design/THIET-BAN-KHOI-SO.md`.

Module này chỉ phơi các BẢNG KIỂM-ĐƯỢC (nguồn: 邵康节说易·铁板神数, Càn Tập p0008-09;
khớp Hà Đồ-Lạc Thư của Chương 9): để dùng lại + làm nền khi sau này có OCR sạch + cặp kiểm.
"""
from __future__ import annotations

# Địa chi → số ngũ hành theo HÀ ĐỒ (p0009) — khớp Hà Đồ Chương 9
DIA_CHI_HA_DO = {
    "Hợi": (1, "Thủy"), "Tý": (6, "Thủy"),
    "Dần": (3, "Mộc"), "Mão": (8, "Mộc"),
    "Tỵ": (2, "Hỏa"), "Ngọ": (7, "Hỏa"),
    "Thân": (4, "Kim"), "Dậu": (9, "Kim"),
    "Thìn": (5, "Thổ"), "Tuất": (10, "Thổ"), "Sửu": (5, "Thổ"), "Mùi": (10, "Thổ"),
}

# Địa chi → quái + số LẠC THƯ (Hậu Thiên, chuẩn; OCR bản này đảo 7/8 — dùng chuẩn)
LAC_THU_QUAI = {
    "Tý": ("Khảm", 1), "Mùi": ("Khôn", 2), "Mão": ("Chấn", 3), "Thìn": ("Tốn", 4),
    "Tuất": ("Càn", 6), "Dậu": ("Đoài", 7), "Sửu": ("Cấn", 8), "Ngọ": ("Ly", 9),
    # 2 chi còn lại theo phương Hậu Thiên: Tỵ→Tốn(4), Thân→Khôn(2)/Càn... (đa trị, KHÔNG ép)
}

# Tứ hóa theo can năm — KIỂM CHÉO khớp engine/tu_vi/do_nam_svg (p0011)
# (giữ tham chiếu; nguồn chuẩn dùng ở do_nam_svg.TU_HOA)

NOT_IMPLEMENTED = (
    "Phép ráp số điều văn (八卦加则 + 考刻) CHƯA cơ học hoá: khẩu quyết bí truyền, "
    "OCR mờ, thiếu cặp kiểm. Xem docs/design/THIET-BAN-KHOI-SO.md."
)


def phoi_so_dia_chi(chi: str) -> dict:
    """Nền số kiểm-được của 1 địa chi (Hà Đồ + Lạc Thư). KHÔNG ra số điều văn."""
    ha = DIA_CHI_HA_DO.get(chi)
    lt = LAC_THU_QUAI.get(chi)
    return {
        "chi": chi,
        "ha_do_so": ha[0] if ha else None,
        "ngu_hanh": ha[1] if ha else None,
        "lac_thu_quai": lt[0] if lt else None,
        "lac_thu_so": lt[1] if lt else None,
        "note": NOT_IMPLEMENTED,
    }
