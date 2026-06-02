"""Quẻ Hỗ reference mapping — Xuân Cang p.72.

Paradigm:
> "Quẻ Hỗ phản ánh MẶT ĐỘNG của quẻ chính, nói cách khác nó nhấn mạnh
>  và làm đậm thêm PHẦN HỒN của quẻ chính."

Khi dự đoán hào X của quẻ chính, BẮT BUỘC tham khảo hào của quẻ Hỗ
theo mapping sau (Xuân Cang p.72):

  Hào 1 quẻ chính: (không có tham khảo — hào 1 không tạo Hỗ)
  Hào 2 quẻ chính → hào 1 quẻ Hỗ
  Hào 3 quẻ chính → hào 2 VÀ hào 4 quẻ Hỗ
  Hào 4 quẻ chính → hào 3 VÀ hào 5 quẻ Hỗ
  Hào 5 quẻ chính → hào 6 quẻ Hỗ
  Hào 6 quẻ chính: (không có tham khảo — hào 6 không tạo Hỗ)

Lý do (Xuân Cang giải thích p.72):
- Hỗ sinh ra từ hào 2,3,4,5 quẻ chính
- Hào 3,4,5 → hào 4,5,6 quẻ Hỗ (Thượng/Ngoại)
- Hào 2,3,4 → hào 1,2,3 quẻ Hỗ (Hạ/Nội)
- Vì hào 3, 4 lặp lại 2 lần trong Hỗ + trùng vị trí trung tâm (2, 5) và
  chuyển tiếp (3, 4) trong quẻ chính → Hỗ phản chiếu mặt động.

Ứng dụng:
- Khi quẻ chính có hào động (Nguyên đường) ở vị trí 2-5 → tra mapping
  → đọc lời hào tham khảo bổ sung.
- Nếu Hóa Công / TNK / ĐNK rơi vào quẻ Hỗ thì VẪN tính như có trong
  Cấu Trúc Hà Lạc (xem hoa_cong.py — đã handle).
"""

from __future__ import annotations


# Mapping: hào X quẻ chính → list[hào quẻ Hỗ tham khảo]
QUE_CHINH_TO_HO_REF: dict[int, list[int]] = {
    1: [],         # hào 1 không tạo Hỗ
    2: [1],
    3: [2, 4],
    4: [3, 5],
    5: [6],
    6: [],         # hào 6 không tạo Hỗ
}


def get_ho_lines_for(que_chinh_line: int) -> list[int]:
    """Lookup hào quẻ Hỗ cần tham khảo khi đoán hào X của quẻ chính."""
    if que_chinh_line < 1 or que_chinh_line > 6:
        raise ValueError(f"Invalid line {que_chinh_line}")
    return QUE_CHINH_TO_HO_REF[que_chinh_line]


def explain_ho_reference(que_chinh_line: int) -> str:
    """Trả về narrative Việt thuần giải thích tham khảo quẻ Hỗ."""
    refs = get_ho_lines_for(que_chinh_line)
    if not refs:
        return (
            f"Hào {que_chinh_line} của quẻ chính KHÔNG có tham khảo quẻ Hỗ "
            f"(hào 1 và 6 không tạo Hỗ — Hỗ chỉ sinh từ hào 2-5)."
        )
    if len(refs) == 1:
        return (
            f"Khi đoán hào {que_chinh_line} quẻ chính, BẮT BUỘC tham khảo "
            f"hào {refs[0]} quẻ Hỗ để thấy phần ĐỘNG (phần hồn) ẩn bên trong."
        )
    return (
        f"Khi đoán hào {que_chinh_line} quẻ chính, BẮT BUỘC tham khảo "
        f"hào {refs[0]} VÀ hào {refs[1]} quẻ Hỗ — đây là vị trí chuyển tiếp, "
        f"cần đọc cả 2 lời hào Hỗ để hiểu mặt động."
    )
