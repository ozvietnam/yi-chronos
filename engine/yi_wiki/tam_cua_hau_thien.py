"""Tám Cửa (Bát Môn) trong Hậu Thiên Bát Quái — Tổ sư Khang Tiết / Thiệu Vĩ Hoa.

Paradigm: Mỗi quẻ trong Hậu Thiên BQ ứng với 1 trong 8 cửa, biểu thị trạng thái
sự việc khi cast Mai Hoa rơi vào quẻ đó.

Reference: Thiệu Vĩ Hoa — Chu Dịch Dự Đoán Học p31.

⚠ Iron Rule: KHÔNG predict cát/hung cá nhân. Paradigm trạng thái.
"""

from __future__ import annotations

BAT_MON = {
    "Khai": {"loai": "cát", "y_nghia": "Cửa mở — cát môn, thuận chiều, nên khởi sự"},
    "Sinh": {"loai": "cát", "y_nghia": "Cửa sinh — cát môn, hành thông, có sinh khí"},
    "Hưu": {"loai": "trung", "y_nghia": "Cửa nghỉ — chờ thời cơ, không nên động"},
    "Thương": {"loai": "hung", "y_nghia": "Kinh hoàng vì thương tổn, lo sợ"},
    "Đỗ": {"loai": "hung", "y_nghia": "Trắc trở không thông, không thuận lợi"},
    "Cảnh": {"loai": "hung", "y_nghia": "Cửa cảnh — vật hư, giả, ảo tưởng"},
    "Tử": {"loai": "đại hung", "y_nghia": "Cửa tử — đại xấu, dữ"},
    "Binh": {"loai": "hung", "y_nghia": "Nguy hiểm, kinh hoàng, sự cố"},
}

# Map 8 quẻ Hậu Thiên → 8 cửa (cần verify với bảng Kỳ Môn Độn Giáp lần sau)
# Đây là sắp xếp Thiệu Vĩ Hoa dùng (p31)
QUE_TO_MON = {
    "Khảm": "Hưu",   # Bắc — quẻ Khảm
    "Khôn": "Tử",    # Tây Nam
    "Chấn": "Thương", # Đông
    "Tốn": "Đỗ",     # Đông Nam
    "Càn": "Khai",   # Tây Bắc — Khai môn
    "Đoài": "Kinh", # Tây — Binh môn (kinh)
    "Cấn": "Sinh",   # Đông Bắc — Sinh môn (cát)
    "Ly": "Cảnh",    # Nam
}


def get_mon_for_que(que_name: str) -> dict | None:
    """Tra cửa cho quẻ Hậu Thiên (vd: 'Càn' → Khai môn cát)."""
    mon = QUE_TO_MON.get(que_name)
    if not mon:
        return None
    info = BAT_MON.get(mon, {})
    return {"que": que_name, "mon": mon, **info}


def get_all_cat_mon() -> list[str]:
    """Danh sách quẻ Hậu Thiên có cát môn (Khai, Sinh)."""
    return [q for q, m in QUE_TO_MON.items() if BAT_MON.get(m, {}).get("loai") == "cát"]


__all__ = ["BAT_MON", "QUE_TO_MON", "get_mon_for_que", "get_all_cat_mon"]
