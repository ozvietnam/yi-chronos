"""Niên Mệnh + Đắc Thể paradigm (Hoàng Tuấn p65-72).

Bổ sung cho engine Hà Lạc — 2 lớp đánh giá mà Xuân Cang chỉ nói qua loa:

1. **Niên Mệnh × Quẻ Tiên Thiên** (nạp âm vs hành quẻ chính):
   - Đồng hành = rất tốt
   - Tương sinh (Niên Mệnh sinh quẻ TT) = SINH NHẬP = rất tốt
   - Tương sinh (quẻ TT sinh Niên Mệnh) = SINH XUẤT = bất lợi (hao mệnh)
   - Tương khắc = bất lợi tiền vận

2. **Đắc Thể** = Niên Mệnh × Quẻ Cung Thiên Can năm sinh:
   - Quẻ cung Lạc Thư cố định (Càn-6, Khảm-1, Cấn-8, Chấn-3, Tốn-4, Ly-9, Khôn-2, Đoài-7)
   - Đồng hành / Sinh nhập = ĐẮC THỂ
   - Sinh xuất / Khắc = KHÔNG ĐẮC THỂ

Trường hợp founder (1988-06-05, Mậu Thìn):
- Niên Mệnh = Đại Lâm Mộc
- Quẻ Tiên Thiên = Tiết (Khảm trên Đoài dưới — quẻ chính thuộc nhóm Khảm-Thủy)
- THỦY SINH MỘC → Quẻ TT SINH Niên Mệnh = SINH XUẤT = bất lợi (hao mệnh)
  Wait, kiểm tra: Niên Mệnh là Mộc, quẻ TT là Thủy. Thủy sinh Mộc.
  → Quẻ TT (Thủy) sinh Niên Mệnh (Mộc) = "Thủy → Mộc" = Niên Mệnh được sinh
  → THỰC TẾ: đây là "Niên Mệnh sinh nhập" (được sinh) = RẤT TỐT cho anh

Convention "sinh nhập / sinh xuất" theo góc nhìn NIÊN MỆNH:
- Sinh nhập: Quẻ TT sinh Niên Mệnh (Niên Mệnh nhận) → TỐT
- Sinh xuất: Niên Mệnh sinh Quẻ TT (Niên Mệnh cho) → HAO

⚠️ Hoàng Tuấn p65 ghi rõ: "Sinh nhập rất tốt, sinh xuất hao tốn" — góc nhìn Niên Mệnh.
"""

from __future__ import annotations


# ── Hành của 10 Thiên Can + 12 Địa Chi (Hoàng Tuấn p70) ──────────────────
HANH_THIEN_CAN: dict[str, str] = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hỏa", "Đinh": "Hỏa",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thủy", "Quý": "Thủy",
}

HANH_DIA_CHI: dict[str, str] = {
    "Tý": "Thủy", "Hợi": "Thủy",
    "Sửu": "Thổ", "Thìn": "Thổ", "Mùi": "Thổ", "Tuất": "Thổ",
    "Dần": "Mộc", "Mão": "Mộc",
    "Tỵ": "Hỏa", "Ngọ": "Hỏa",
    "Thân": "Kim", "Dậu": "Kim",
}


# ── Quẻ cung Lạc Thư (Hậu Thiên Bát Quái) cho Thiên Can ───────────────────
# Source: Hoàng Tuấn p69-70 + Lạc Thư cổ
# Mậu Kỷ ở Trung Cung (5) — không có quẻ cố định, dùng quẻ phù trợ
QUE_CUNG_THIEN_CAN: dict[str, dict] = {
    "Giáp": {"cung": 3, "que": "Chấn", "hanh": "Mộc"},
    "Ất":   {"cung": 4, "que": "Tốn",  "hanh": "Mộc"},
    "Bính": {"cung": 9, "que": "Ly",   "hanh": "Hỏa"},
    "Đinh": {"cung": 2, "que": "Khôn", "hanh": "Thổ"},
    "Mậu":  {"cung": 5, "que": "Cấn",  "hanh": "Thổ"},   # Trung cung → dùng Cấn-Thổ
    "Kỷ":   {"cung": 5, "que": "Khôn", "hanh": "Thổ"},   # Trung cung → dùng Khôn-Thổ
    "Canh": {"cung": 6, "que": "Càn",  "hanh": "Kim"},
    "Tân":  {"cung": 7, "que": "Đoài", "hanh": "Kim"},
    "Nhâm": {"cung": 1, "que": "Khảm", "hanh": "Thủy"},
    "Quý":  {"cung": 5, "que": "Càn",  "hanh": "Kim"},   # Trung cung → dùng Càn (cách 2)
}


# ── Hành của 8 quẻ Bát Quái ───────────────────────────────────────────────
HANH_QUE: dict[str, str] = {
    "Càn": "Kim", "Đoài": "Kim",
    "Ly": "Hỏa",
    "Chấn": "Mộc", "Tốn": "Mộc",
    "Khảm": "Thủy",
    "Cấn": "Thổ", "Khôn": "Thổ",
}


# ── 60 Giáp Tý nạp âm — Niên Mệnh ────────────────────────────────────────
# Source: Trần Đoàn 60 Giáp Tý (đầy đủ)
NIEN_MENH_60: dict[str, dict] = {
    "Giáp Tý":   {"nap_am": "Hải Trung Kim",   "hanh": "Kim"},
    "Ất Sửu":    {"nap_am": "Hải Trung Kim",   "hanh": "Kim"},
    "Bính Dần":  {"nap_am": "Lô Trung Hỏa",    "hanh": "Hỏa"},
    "Đinh Mão":  {"nap_am": "Lô Trung Hỏa",    "hanh": "Hỏa"},
    "Mậu Thìn":  {"nap_am": "Đại Lâm Mộc",     "hanh": "Mộc"},  # 1928, 1988 — anh!
    "Kỷ Tỵ":     {"nap_am": "Đại Lâm Mộc",     "hanh": "Mộc"},
    "Canh Ngọ":  {"nap_am": "Lộ Bàng Thổ",     "hanh": "Thổ"},
    "Tân Mùi":   {"nap_am": "Lộ Bàng Thổ",     "hanh": "Thổ"},
    "Nhâm Thân": {"nap_am": "Kiếm Phong Kim",  "hanh": "Kim"},
    "Quý Dậu":   {"nap_am": "Kiếm Phong Kim",  "hanh": "Kim"},
    "Giáp Tuất": {"nap_am": "Sơn Đầu Hỏa",     "hanh": "Hỏa"},
    "Ất Hợi":    {"nap_am": "Sơn Đầu Hỏa",     "hanh": "Hỏa"},
    "Bính Tý":   {"nap_am": "Giản Hạ Thủy",    "hanh": "Thủy"},
    "Đinh Sửu":  {"nap_am": "Giản Hạ Thủy",    "hanh": "Thủy"},
    "Mậu Dần":   {"nap_am": "Thành Đầu Thổ",   "hanh": "Thổ"},
    "Kỷ Mão":    {"nap_am": "Thành Đầu Thổ",   "hanh": "Thổ"},
    "Canh Thìn": {"nap_am": "Bạch Lạp Kim",    "hanh": "Kim"},
    "Tân Tỵ":    {"nap_am": "Bạch Lạp Kim",    "hanh": "Kim"},
    "Nhâm Ngọ":  {"nap_am": "Dương Liễu Mộc",  "hanh": "Mộc"},
    "Quý Mùi":   {"nap_am": "Dương Liễu Mộc",  "hanh": "Mộc"},
    "Giáp Thân": {"nap_am": "Tuyền Trung Thủy","hanh": "Thủy"},
    "Ất Dậu":    {"nap_am": "Tuyền Trung Thủy","hanh": "Thủy"},
    "Bính Tuất": {"nap_am": "Ốc Thượng Thổ",   "hanh": "Thổ"},
    "Đinh Hợi":  {"nap_am": "Ốc Thượng Thổ",   "hanh": "Thổ"},
    "Mậu Tý":    {"nap_am": "Tích Lịch Hỏa",   "hanh": "Hỏa"},
    "Kỷ Sửu":    {"nap_am": "Tích Lịch Hỏa",   "hanh": "Hỏa"},
    "Canh Dần":  {"nap_am": "Tùng Bách Mộc",   "hanh": "Mộc"},
    "Tân Mão":   {"nap_am": "Tùng Bách Mộc",   "hanh": "Mộc"},
    "Nhâm Thìn": {"nap_am": "Trường Lưu Thủy", "hanh": "Thủy"},
    "Quý Tỵ":    {"nap_am": "Trường Lưu Thủy", "hanh": "Thủy"},
    "Giáp Ngọ":  {"nap_am": "Sa Trung Kim",    "hanh": "Kim"},
    "Ất Mùi":    {"nap_am": "Sa Trung Kim",    "hanh": "Kim"},
    "Bính Thân": {"nap_am": "Sơn Hạ Hỏa",      "hanh": "Hỏa"},
    "Đinh Dậu":  {"nap_am": "Sơn Hạ Hỏa",      "hanh": "Hỏa"},
    "Mậu Tuất":  {"nap_am": "Bình Địa Mộc",    "hanh": "Mộc"},
    "Kỷ Hợi":    {"nap_am": "Bình Địa Mộc",    "hanh": "Mộc"},
    "Canh Tý":   {"nap_am": "Bích Thượng Thổ", "hanh": "Thổ"},
    "Tân Sửu":   {"nap_am": "Bích Thượng Thổ", "hanh": "Thổ"},
    "Nhâm Dần":  {"nap_am": "Kim Bạc Kim",     "hanh": "Kim"},
    "Quý Mão":   {"nap_am": "Kim Bạc Kim",     "hanh": "Kim"},
    "Giáp Thìn": {"nap_am": "Phúc Đăng Hỏa",   "hanh": "Hỏa"},
    "Ất Tỵ":     {"nap_am": "Phúc Đăng Hỏa",   "hanh": "Hỏa"},
    "Bính Ngọ":  {"nap_am": "Thiên Hà Thủy",   "hanh": "Thủy"},
    "Đinh Mùi":  {"nap_am": "Thiên Hà Thủy",   "hanh": "Thủy"},
    "Mậu Thân":  {"nap_am": "Đại Trạch Thổ",   "hanh": "Thổ"},
    "Kỷ Dậu":    {"nap_am": "Đại Trạch Thổ",   "hanh": "Thổ"},
    "Canh Tuất": {"nap_am": "Thoa Xuyến Kim",  "hanh": "Kim"},
    "Tân Hợi":   {"nap_am": "Thoa Xuyến Kim",  "hanh": "Kim"},
    "Nhâm Tý":   {"nap_am": "Tang Đố Mộc",     "hanh": "Mộc"},
    "Quý Sửu":   {"nap_am": "Tang Đố Mộc",     "hanh": "Mộc"},
    "Giáp Dần":  {"nap_am": "Đại Khê Thủy",    "hanh": "Thủy"},
    "Ất Mão":    {"nap_am": "Đại Khê Thủy",    "hanh": "Thủy"},
    "Bính Thìn": {"nap_am": "Sa Trung Thổ",    "hanh": "Thổ"},
    "Đinh Tỵ":   {"nap_am": "Sa Trung Thổ",    "hanh": "Thổ"},
    "Mậu Ngọ":   {"nap_am": "Thiên Thượng Hỏa","hanh": "Hỏa"},
    "Kỷ Mùi":    {"nap_am": "Thiên Thượng Hỏa","hanh": "Hỏa"},
    "Canh Thân": {"nap_am": "Thạch Lựu Mộc",   "hanh": "Mộc"},
    "Tân Dậu":   {"nap_am": "Thạch Lựu Mộc",   "hanh": "Mộc"},
    "Nhâm Tuất": {"nap_am": "Đại Hải Thủy",    "hanh": "Thủy"},
    "Quý Hợi":   {"nap_am": "Đại Hải Thủy",    "hanh": "Thủy"},
}


# ── Quan hệ sinh-khắc ngũ hành ───────────────────────────────────────────
NGU_HANH_SINH: dict[str, str] = {  # A sinh B
    "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc",
}

NGU_HANH_KHAC: dict[str, str] = {  # A khắc B
    "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc",
}


def quan_he_ngu_hanh(hanh_a: str, hanh_b: str) -> str:
    """Trả về quan hệ 2 hành: 'đồng_hành' | 'a_sinh_b' | 'b_sinh_a' | 'a_khắc_b' | 'b_khắc_a'."""
    if hanh_a == hanh_b:
        return "đồng_hành"
    if NGU_HANH_SINH.get(hanh_a) == hanh_b:
        return "a_sinh_b"
    if NGU_HANH_SINH.get(hanh_b) == hanh_a:
        return "b_sinh_a"
    if NGU_HANH_KHAC.get(hanh_a) == hanh_b:
        return "a_khắc_b"
    if NGU_HANH_KHAC.get(hanh_b) == hanh_a:
        return "b_khắc_a"
    return "unknown"


def evaluate_nien_menh_vs_que_tien_thien(
    can_chi_nam: str,
    que_tien_thien_upper: str,
) -> dict:
    """Đánh giá Niên Mệnh × Quẻ Tiên Thiên (Hoàng Tuấn p67-68).

    Góc nhìn TỪ NIÊN MỆNH:
    - Đồng hành = rất tốt
    - Sinh nhập (Quẻ TT sinh Niên Mệnh) = rất tốt
    - Sinh xuất (Niên Mệnh sinh Quẻ TT) = hao mệnh
    - Khắc nhập (Quẻ TT khắc Niên Mệnh) = bất lợi
    - Khắc xuất (Niên Mệnh khắc Quẻ TT) = thuận
    """
    nm = NIEN_MENH_60.get(can_chi_nam)
    if not nm:
        return {"_error": f"Không có Niên Mệnh cho {can_chi_nam}"}

    hanh_que = HANH_QUE.get(que_tien_thien_upper, "?")
    hanh_nm = nm["hanh"]
    qh = quan_he_ngu_hanh(hanh_nm, hanh_que)

    grade_map = {
        "đồng_hành": ("đồng_hành", "RẤT TỐT — đồng hành, hợp nhau, tiền vận nhiều thuận lợi"),
        "a_sinh_b": ("sinh_xuất", "BẤT LỢI — Niên Mệnh SINH XUẤT (cho Quẻ TT) → hao mệnh, tốn sức"),
        "b_sinh_a": ("sinh_nhập", "RẤT TỐT — Quẻ TT SINH NHẬP cho Niên Mệnh → tiền vận được sinh, nhiều phúc"),
        "a_khắc_b": ("khắc_xuất", "TRUNG TÍNH — Niên Mệnh khắc Quẻ TT → phải dụng công nhưng làm chủ được"),
        "b_khắc_a": ("khắc_nhập", "BẤT LỢI — Quẻ TT khắc Niên Mệnh → tiền vận trở ngại, thời cuộc khó"),
    }
    grade, narrative = grade_map.get(qh, ("unknown", "Không xác định"))

    return {
        "can_chi_nam": can_chi_nam,
        "nap_am": nm["nap_am"],
        "hanh_nien_menh": hanh_nm,
        "que_tien_thien": que_tien_thien_upper,
        "hanh_que": hanh_que,
        "quan_he": qh,
        "grade": grade,
        "narrative": narrative,
    }


def evaluate_dac_the(can_nam: str, can_chi_nam: str) -> dict:
    """Đánh giá ĐẮC THỂ — Niên Mệnh × Quẻ Cung Thiên Can năm sinh (Hoàng Tuấn p70).

    Đắc thể = Niên Mệnh đồng hành/sinh nhập với Quẻ cung Lạc Thư của Thiên Can.
    """
    nm = NIEN_MENH_60.get(can_chi_nam)
    if not nm:
        return {"_error": f"Không có Niên Mệnh cho {can_chi_nam}"}

    cung_info = QUE_CUNG_THIEN_CAN.get(can_nam)
    if not cung_info:
        return {"_error": f"Không có quẻ cung cho Can {can_nam}"}

    hanh_nm = nm["hanh"]
    hanh_que_cung = cung_info["hanh"]
    qh = quan_he_ngu_hanh(hanh_nm, hanh_que_cung)

    if qh == "đồng_hành" or qh == "b_sinh_a":
        dac_the = True
        grade = "đắc_thể"
        narrative = f"ĐẮC THỂ — Niên Mệnh {nm['nap_am']} ({hanh_nm}) {qh} với quẻ cung {cung_info['que']} ({hanh_que_cung}). Phú quý, tốt."
    elif qh == "a_sinh_b":
        dac_the = False
        grade = "không_đắc_thể_sinh_xuất"
        narrative = f"KHÔNG ĐẮC THỂ — Niên Mệnh SINH XUẤT cho quẻ cung. Hao mệnh."
    else:
        dac_the = False
        grade = "không_đắc_thể_khắc"
        narrative = f"KHÔNG ĐẮC THỂ — Niên Mệnh tương khắc với quẻ cung. Bất lợi."

    return {
        "can_chi_nam": can_chi_nam,
        "nap_am": nm["nap_am"],
        "hanh_nien_menh": hanh_nm,
        "can_nam": can_nam,
        "cung_lac_thu": cung_info["cung"],
        "que_cung": cung_info["que"],
        "hanh_que_cung": hanh_que_cung,
        "quan_he": qh,
        "dac_the": dac_the,
        "grade": grade,
        "narrative": narrative,
        "source": "Hoàng Tuấn — Lý Thuyết Tượng Số p70",
    }


def evaluate_founder() -> dict:
    """Test cho founder 1988-06-05 23:30 (Mậu Thìn)."""
    return {
        "nien_menh_vs_TT_Tiet": evaluate_nien_menh_vs_que_tien_thien(
            can_chi_nam="Mậu Thìn",
            que_tien_thien_upper="Khảm",  # Tiết = Khảm trên Đoài dưới — quẻ chính Khảm
        ),
        "dac_the": evaluate_dac_the(can_nam="Mậu", can_chi_nam="Mậu Thìn"),
    }
