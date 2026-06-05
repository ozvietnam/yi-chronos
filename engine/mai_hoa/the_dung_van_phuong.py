"""Quẻ Thể, Quẻ Dụng, Vạn Phương Đoán Quẻ (Thiệu Vĩ Hoa p119-128).

Paradigm:
- Thể = mình; Dụng = người khác / sự việc
- Thể khắc Dụng = CÁT (mình thắng)
- Dụng khắc Thể = HUNG
- Thể sinh Dụng = hao tổn
- Dụng sinh Thể = tin mừng
- Thể ngang Dụng = trăm việc thuận
"""

from __future__ import annotations

# Quan hệ Thể-Dụng theo Ngũ Hành
NGU_HANH_SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
NGU_HANH_KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}

# Map quẻ → ngũ hành
QUE_NGU_HANH = {
    "Càn": "Kim", "Đoài": "Kim",
    "Ly": "Hỏa",
    "Chấn": "Mộc", "Tốn": "Mộc",
    "Khảm": "Thủy",
    "Cấn": "Thổ", "Khôn": "Thổ",
}

# 14 quẻ Thể-Dụng NGANG NHAU (cùng ngũ hành)
QUE_NGANG_NHAU = [
    "Càn vi Thiên", "Khảm vi Thủy", "Cấn vi Sơn", "Chấn vi Lôi",
    "Tốn vi Phong", "Ly vi Hỏa", "Khôn vi Địa", "Đoài vi Trạch",
    "Lý", "Quải", "Khiêm", "Bốc", "Hằng", "Ích",
]


def quan_he_the_dung(que_the: str, que_dung: str) -> dict:
    """Tính quan hệ Thể-Dụng + đoán cát/hung.

    Args:
        que_the, que_dung: 1 trong 8 quẻ đơn

    Returns:
        dict {ngu_hanh_the, ngu_hanh_dung, quan_he, cat_hung, dien_giai}
    """
    nh_the = QUE_NGU_HANH.get(que_the)
    nh_dung = QUE_NGU_HANH.get(que_dung)
    if not nh_the or not nh_dung:
        return {}

    if nh_the == nh_dung:
        return {
            "ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung,
            "quan_he": "Ngang nhau", "cat_hung": "CÁT",
            "dien_giai": "Thể và Dụng cùng ngũ hành — trăm việc thuận lợi",
        }
    if NGU_HANH_KHAC.get(nh_the) == nh_dung:
        return {
            "ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung,
            "quan_he": "Thể khắc Dụng", "cat_hung": "CÁT",
            "dien_giai": "Mình khắc người/việc — chủ động thắng",
        }
    if NGU_HANH_KHAC.get(nh_dung) == nh_the:
        return {
            "ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung,
            "quan_he": "Dụng khắc Thể", "cat_hung": "HUNG",
            "dien_giai": "Người/việc khắc mình — bị hại",
        }
    if NGU_HANH_SINH.get(nh_the) == nh_dung:
        return {
            "ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung,
            "quan_he": "Thể sinh Dụng", "cat_hung": "HAO TỔN",
            "dien_giai": "Mình sinh cho người — hao tổn, cho đi",
        }
    if NGU_HANH_SINH.get(nh_dung) == nh_the:
        return {
            "ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung,
            "quan_he": "Dụng sinh Thể", "cat_hung": "TIN MỪNG",
            "dien_giai": "Người sinh cho mình — nhận về, tin mừng",
        }
    return {"ngu_hanh_the": nh_the, "ngu_hanh_dung": nh_dung, "quan_he": "Khác", "cat_hung": "—"}


def thoi_gian_ung_nghiem_theo_dong_tinh(trang_thai: str, so_que: int) -> float:
    """Tính thời gian ứng nghiệm dựa trạng thái động/tĩnh người đến đoán.

    Args:
        trang_thai: "di" | "dung" | "ngoi" | "nam"
        so_que: số của quẻ (Càn=1...Khôn=8)

    Returns: số ngày/tháng/năm (đơn vị tự xác định theo độ lớn việc)
    """
    if trang_thai == "di":
        return so_que / 2  # nhanh
    if trang_thai == "dung":
        return so_que  # giữ nguyên
    if trang_thai == "ngoi":
        return so_que  # bình thường
    if trang_thai == "nam":
        return so_que * 2  # chậm
    return so_que


def la_que_ngang_nhau(que_kep_name: str) -> bool:
    """Check quẻ kép có thuộc 14 quẻ Thể-Dụng NGANG NHAU."""
    return any(name in que_kep_name for name in QUE_NGANG_NHAU)


__all__ = [
    "NGU_HANH_SINH", "NGU_HANH_KHAC", "QUE_NGU_HANH", "QUE_NGANG_NHAU",
    "quan_he_the_dung", "thoi_gian_ung_nghiem_theo_dong_tinh", "la_que_ngang_nhau",
]
