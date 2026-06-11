"""An vòng Tràng Sinh 12 sao — mở khóa cách cục Tử Mã / Chiết Túc / Mộ Trung Thai Tọa.

Công thức TỪ SÁCH (atoms kho, Vũ Tài Lục + Thiên Lương):
- "Thủy và Thổ cục tràng sinh ở Thân / Hỏa lục cục tràng sinh ở Dần /
   Kim tứ cục tràng sinh ở Tỵ / Mộc tam cục tràng sinh ở Hợi"
- "dương nam và âm nữ theo chiều hướng thuận, nghịch lý âm dương đi ngược"

12 sao thứ tự: Tràng Sinh, Mộc Dục, Quan Đới, Lâm Quan, Đế Vượng,
Suy, Bệnh, Tử, Mộ, Tuyệt, Thai, Dưỡng.
Canonical prefix ts_ để tránh trùng (ts_tu ≠ tử tức, ts_thai ≠ sao Thai Phụ).

Built 2026-06-11 (Anh duyệt fix 11 cách).
"""
from __future__ import annotations

CHI_RING = ["ty", "suu", "dan", "mao", "thin", "ti",
            "ngo", "mui", "than", "dau", "tuat", "hoi"]

# Cục → chi khởi Tràng Sinh (nguồn: atoms Vũ Tài Lục)
TRANG_SINH_KHOI: dict[str, str] = {
    "thuy_nhi_cuc": "than",
    "tho_ngu_cuc": "than",   # Thủy Thổ đồng vòng
    "hoa_luc_cuc": "dan",
    "kim_tu_cuc": "ti",
    "moc_tam_cuc": "hoi",
}

# 12 sao vòng Tràng Sinh theo thứ tự thuận
TRANG_SINH_SAO = [
    "ts_trang_sinh", "ts_moc_duc", "ts_quan_doi", "ts_lam_quan",
    "ts_de_vuong", "ts_suy", "ts_benh", "ts_tu",
    "ts_mo", "ts_tuyet", "ts_thai", "ts_duong",
]

TRANG_SINH_VI = {
    "ts_trang_sinh": "Tràng Sinh", "ts_moc_duc": "Mộc Dục",
    "ts_quan_doi": "Quan Đới", "ts_lam_quan": "Lâm Quan",
    "ts_de_vuong": "Đế Vượng", "ts_suy": "Suy", "ts_benh": "Bệnh",
    "ts_tu": "Tử", "ts_mo": "Mộ", "ts_tuyet": "Tuyệt",
    "ts_thai": "Thai", "ts_duong": "Dưỡng",
}

DUONG_CAN = {"giap", "binh", "mau", "canh", "nham"}


def an_trang_sinh(cuc: str, can: str, gender: str = "M") -> dict[str, str]:
    """An 12 sao vòng Tràng Sinh.

    Args:
        cuc: cục canonical (thuy_nhi_cuc...)
        can: can năm sinh canonical (xác định dương/âm)
        gender: M | F

    Returns: {sao_canonical: chi} — rỗng nếu cục lạ.
    """
    khoi = TRANG_SINH_KHOI.get(cuc)
    if khoi is None:
        return {}
    duong_nam_am_nu = (can in DUONG_CAN) == (gender == "M")
    step = 1 if duong_nam_am_nu else -1  # thuận lý âm dương → thuận chiều
    start = CHI_RING.index(khoi)
    return {
        sao: CHI_RING[(start + step * i) % 12]
        for i, sao in enumerate(TRANG_SINH_SAO)
    }
