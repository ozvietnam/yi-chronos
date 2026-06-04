"""Hà Đồ + Lạc Thư — Số Trời Đất 55 + Thiên Can hóa hợp.

Paradigm Thiệu Vĩ Hoa p33: Số trời đất trong Hệ Từ rất có thể từ Thập Thiên Can.
- 5 Can dương (Giáp/Bính/Mậu/Canh/Nhâm) tổng 25 = số TRỜI
- 5 Can âm (Ất/Đinh/Kỷ/Tân/Quý) tổng 30 = số ĐẤT
- Tổng 55 = Hà Đồ

6 cặp Ngũ Hành hợp (Hà Đồ):
- 1+6 = Thủy (Bắc)
- 2+7 = Hỏa (Nam)
- 3+8 = Mộc (Đông)
- 4+9 = Kim (Tây)
- 5+10 = Thổ (Trung)

Reference: Thiệu Vĩ Hoa, p33.
"""

from __future__ import annotations

# Thập Thiên Can với số tương ứng
THIEN_CAN_SO = {
    "Giáp": 1, "Ất": 2, "Bính": 3, "Đinh": 4, "Mậu": 5,
    "Kỷ": 6, "Canh": 7, "Tân": 8, "Nhâm": 9, "Quý": 10,
}

# Cặp Ngũ Hành hợp (Hà Đồ)
NGU_HANH_HOP = {
    "Thủy": (1, 6, "Bắc"),
    "Hỏa": (2, 7, "Nam"),
    "Mộc": (3, 8, "Đông"),
    "Kim": (4, 9, "Tây"),
    "Thổ": (5, 10, "Trung"),
}

# Tổng số trời/đất
SO_TROI = sum(n for c, n in THIEN_CAN_SO.items() if c in ("Giáp", "Bính", "Mậu", "Canh", "Nhâm"))  # 25
SO_DAT = sum(n for c, n in THIEN_CAN_SO.items() if c in ("Ất", "Đinh", "Kỷ", "Tân", "Quý"))  # 30
TONG_HA_DO = SO_TROI + SO_DAT  # 55


def get_ngu_hanh_for_so(n: int) -> str | None:
    """Tra ngũ hành từ số (vd: 1 → Thủy, 7 → Hỏa)."""
    for nh, (sm, slon, _) in NGU_HANH_HOP.items():
        if n == sm or n == slon:
            return nh
    return None


def get_phuong_for_ngu_hanh(ngu_hanh: str) -> str | None:
    """Tra phương cho ngũ hành."""
    info = NGU_HANH_HOP.get(ngu_hanh)
    return info[2] if info else None


__all__ = [
    "THIEN_CAN_SO", "NGU_HANH_HOP", "SO_TROI", "SO_DAT", "TONG_HA_DO",
    "get_ngu_hanh_for_so", "get_phuong_for_ngu_hanh",
]
