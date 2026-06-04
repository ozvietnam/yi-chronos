"""Lục Thân theo Ngũ Hành — 5 quan hệ cốt (Thiệu Vĩ Hoa p81).

Paradigm: Lấy hành của NGÀY SINH làm "tôi", các hành khác xếp 5 quan hệ:
- Cha mẹ (Phụ Mẫu) = cái SINH tôi
- Con cháu (Tử Tôn) = cái TÔI SINH
- Quan Quỷ = cái KHẮC tôi
- Thê Tài = cái TÔI KHẮC
- Anh em (Huynh Đệ) = ngang vai

Ví dụ: Ngày Canh (Kim) → Thổ=Phụ Mẫu, Hỏa=Quan Quỷ, Mộc=Thê Tài, Thủy=Tử Tôn, Kim=Huynh Đệ
"""

from __future__ import annotations

# Quy luật tương sinh
SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
# Quy luật tương khắc
KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}

# Tính cách theo Ngũ Hành (Thiệu Vĩ Hoa p91)
TINH_CACH = {
    "Kim": {
        "ban_chat": "Nghĩa khí, cứng cỏi",
        "khi_vuong_qua": "Cứng dễ gãy, tự thiệt",
    },
    "Hỏa": {
        "ban_chat": "Có lễ, dùng lý luận",
        "khi_vuong_qua": "Nóng nảy, dễ làm hỏng việc",
    },
    "Thổ": {
        "ban_chat": "Giữ chữ tín, nói được làm được",
        "khi_vuong_qua": "Thích tĩnh, không thích động, mất thời cơ",
    },
    "Mộc": {
        "ban_chat": "Hiền từ, tấm lòng tốt",
        "khi_vuong_qua": "Không khuất phục — 'thà chết đứng không sống quỳ'. Hợp với binh ngũ, trinh sát.",
    },
    "Thủy": {
        "ban_chat": "Mưu trí, thông minh, ham học",
        "khi_vuong_qua": "Nóng nảy, hung bạo, dễ gây tai họa",
    },
}


def luc_than_for_toi(toi_hanh: str) -> dict[str, str]:
    """Tính 5 quan hệ Lục Thân khi 'tôi' là hành toi_hanh.

    Args:
        toi_hanh: Mộc/Hỏa/Thổ/Kim/Thủy (thường là hành của Nhật Trụ - ngày sinh)

    Returns:
        dict {hanh: quan_he} với 5 cặp
    """
    all_hanh = ["Mộc", "Hỏa", "Thổ", "Kim", "Thủy"]
    if toi_hanh not in all_hanh:
        return {}

    result = {}
    for hanh in all_hanh:
        if hanh == toi_hanh:
            result[hanh] = "Huynh Đệ (anh em ngang vai)"
        elif SINH.get(hanh) == toi_hanh:
            # hanh sinh ra tôi
            result[hanh] = "Phụ Mẫu (cái SINH tôi)"
        elif SINH.get(toi_hanh) == hanh:
            # tôi sinh ra hanh
            result[hanh] = "Tử Tôn (cái TÔI SINH)"
        elif KHAC.get(hanh) == toi_hanh:
            # hanh khắc tôi
            result[hanh] = "Quan Quỷ (cái KHẮC tôi)"
        elif KHAC.get(toi_hanh) == hanh:
            # tôi khắc hanh
            result[hanh] = "Thê Tài (cái TÔI KHẮC)"
    return result


def get_tinh_cach(menh_hanh: str) -> dict | None:
    """Lấy tính cách + cảnh báo theo mệnh Ngũ Hành."""
    return TINH_CACH.get(menh_hanh)


__all__ = ["SINH", "KHAC", "TINH_CACH", "luc_than_for_toi", "get_tinh_cach"]
