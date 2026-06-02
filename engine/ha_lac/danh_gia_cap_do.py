"""6 cấp đánh giá Hà Lạc + 4 đức quẻ + phương hướng (Xuân Cang p.73-74).

Paradigm:
- 4 đức của quẻ (Tứ Đức): Nguyên - Hành - Lợi - Trinh
  - Chỉ 7 quẻ có đủ 4 đức (tiêu biểu Càn)
  - Còn lại: 3-4 đức, 1-2 đức, hoặc không có đức nào
- 6 cấp đánh giá lời hào: Tốt - Xấu - Hối - Ấn nản - Vô cữu - (Phương hướng)
- Phương hướng: Đông Bắc (tiến) / Tây Nam (thoái)

Bảng nặng nhẹ:
  Xấu > Ấn nản > Hối
  Vô cữu = trung tính (không hay cũng không dở)
"""

from __future__ import annotations

from dataclasses import dataclass


# 4 đức (Tứ Đức) — chỉ 7 quẻ có đủ 4
QUE_DU_4_DUC: frozenset[str] = frozenset({
    "Càn",
    "Khôn",
    "Đại Hữu",        # Hỏa Thiên — sáng lớn
    "Hàm",            # Trạch Sơn — cảm
    "Hằng",           # Lôi Phong — bền
    "Tổn",            # Sơn Trạch — bớt
    "Ích",            # Phong Lôi — thêm
})


TU_DUC_NGHIA: dict[str, str] = {
    "Nguyên": "Đầu tiên, lớn, trùm mọi điều thiện — như gieo hạt giống xuống đất, gốc của vạn vật",
    "Hành":   "Hành thông, thuận tiện, tập hợp các điều hay — như Trời sinh ra cây cỏ, làm mưa cho muôn loài sinh trưởng",
    "Lợi":   "Nên, thỏa thích, hòa hợp các điều phải, thích đáng",
    "Trinh":  "Chính đáng, bền chắc, gốc của mọi việc — như cây kết trái, hạt rơi xuống thành cây mới (trở lại Nguyên)",
}


# 6 cấp đánh giá lời hào (Xuân Cang p.73-74)
CAP_DO_DANH_GIA: dict[str, dict] = {
    "tot": {
        "label": "Tốt",
        "lời_kinh": "Cát (吉)",
        "nghia": "Lành, thuận lẽ trời, lẽ đời, đem lợi ích, may mắn đến cho người",
        "muc_do": 5,  # cao nhất
    },
    "xau": {
        "label": "Xấu",
        "lời_kinh": "Hung (凶)",
        "nghia": "Dữ, ngược lại với Tốt",
        "muc_do": -3,  # nặng nhất
    },
    "hoi": {
        "label": "Hối",
        "lời_kinh": "Hối (悔)",
        "nghia": "Phiền muộn vì lỗi nhỏ, tật mọn",
        "muc_do": -1,  # nhẹ nhất trong 3 cấp xấu
    },
    "an_nan": {
        "label": "Ấn nản (Lận)",
        "lời_kinh": "Lận (吝)",
        "nghia": "Phạm lẽ phải, phàn nàn, đáng tiếc",
        "muc_do": -2,  # giữa Hối và Xấu
    },
    "vo_cuu": {
        "label": "Vô cữu",
        "lời_kinh": "Vô Cữu (无咎)",
        "nghia": "Không sẽ phạm, không trách ai được, không đổ lỗi cho ai được — không hay cũng không dở",
        "muc_do": 0,  # trung tính
    },
    "phuong_huong": {
        "label": "Phương hướng",
        "lời_kinh": "Đông Bắc / Tây Nam",
        "nghia": "Phương vị khuyên nhủ — Đông Bắc khuyên tiến, đương đầu khó khăn; Tây Nam khuyên thoái lui",
        "muc_do": None,
    },
}

# Thứ tự nặng → nhẹ trong các cấp tiêu cực
THU_TU_NANG_NHE_TIEU_CUC = ["xau", "an_nan", "hoi", "vo_cuu"]


# Phương hướng (lời Kinh) — Xuân Cang p.74
PHUONG_HUONG_NGHIA: dict[str, str] = {
    "Đông Bắc": (
        "Hướng khí Dương BẮT ĐẦU TIẾN. Quẻ khuyên nên hành động mau, "
        "nên tiến, đương đầu với khó khăn. Đông Bắc là phía ĐỘNG của khí Dương."
    ),
    "Tây Nam": (
        "Hướng khí Dương BẮT ĐẦU SUY. Quẻ khuyên nên dừng lại, thoái lui, "
        "không nên tiến cũng không nên đương đầu. Tây Nam là phía TĨNH của khí Dương."
    ),
}


# 3 giới đoán riêng (Xuân Cang p.76)
GIOI_DOAN: dict[str, str] = {
    "quan": "Giới Quan chức (bao gồm CEO, manager, công chức, lãnh đạo tổ chức)",
    "si":   "Giới Sĩ (học sinh, sinh viên, học giả, nhà nghiên cứu)",
    "thuong": "Người thường (kinh doanh, lao động ngành nghề, nội trợ, trẻ em)",
}


@dataclass(frozen=True)
class HaoEvaluation:
    """Kết quả đánh giá 1 hào."""

    cap_do: str           # key in CAP_DO_DANH_GIA
    label: str
    nghia: str
    muc_do: int | None
    raw_text: str         # original phrase from sách

    def to_dict(self) -> dict:
        return {
            "cap_do": self.cap_do,
            "label": self.label,
            "nghia": self.nghia,
            "muc_do": self.muc_do,
            "raw_text": self.raw_text,
        }


def classify_loi_hao(text: str) -> HaoEvaluation:
    """Classify a hào text into one of 6 evaluation tiers.

    Heuristic dựa trên Lời Kinh chuẩn:
    - "cát", "tốt" → tot
    - "hung", "xấu", "dữ" → xau
    - "hối" → hoi
    - "lận", "đáng tiếc", "ấn nản" → an_nan
    - "vô cữu", "không lỗi" → vo_cuu
    """
    t = text.lower()
    if any(w in t for w in ("vô cữu", "không lỗi", "không trách")):
        key = "vo_cuu"
    elif any(w in t for w in ("cát", "tốt", "lợi", "thành")):
        key = "tot"
    elif any(w in t for w in ("hung", "xấu", "dữ", "tai họa")):
        key = "xau"
    elif "lận" in t or "đáng tiếc" in t or "ấn nản" in t:
        key = "an_nan"
    elif "hối" in t:
        key = "hoi"
    else:
        key = "vo_cuu"  # default trung tính

    meta = CAP_DO_DANH_GIA[key]
    return HaoEvaluation(
        cap_do=key,
        label=meta["label"],
        nghia=meta["nghia"],
        muc_do=meta["muc_do"],
        raw_text=text,
    )


def get_tu_duc_for(quai_name: str, declared_duc: list[str] | None = None) -> dict:
    """Đánh giá Tứ Đức cho 1 quẻ.

    Args:
        quai_name: tên quẻ (vd "Càn")
        declared_duc: list các đức được khai báo cho quẻ này
            (lấy từ wiki / hexagram_lines_ha_lac.json)

    Returns: dict {has_4_duc, count, duc_list, narrative}
    """
    has_full_4 = quai_name in QUE_DU_4_DUC
    if has_full_4:
        return {
            "has_4_duc": True,
            "count": 4,
            "duc_list": ["Nguyên", "Hành", "Lợi", "Trinh"],
            "narrative": (
                f"Quẻ {quai_name} có ĐỦ 4 ĐỨC (Nguyên-Hành-Lợi-Trinh) — "
                f"thuộc 7 quẻ tiêu biểu (Càn, Khôn, Đại Hữu, Hàm, Hằng, Tổn, Ích). "
                f"Đây là quẻ trọn vẹn nhất trong Kinh Dịch."
            ),
        }
    if declared_duc:
        return {
            "has_4_duc": False,
            "count": len(declared_duc),
            "duc_list": declared_duc,
            "narrative": f"Quẻ {quai_name} có {len(declared_duc)} đức: {', '.join(declared_duc)}",
        }
    return {
        "has_4_duc": False,
        "count": None,
        "duc_list": [],
        "narrative": f"Quẻ {quai_name} — chưa khai báo Tứ Đức (cần wiki citation)",
    }
