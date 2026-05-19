"""Mai Hoa Dịch Số — Auto-interpret quẻ theo 5 bước Thiệu Khang Tiết.

Implementation: Mai Hoa trang 117-120 (Chiêm Bốc Tổng Quyết) + 64-90 (case studies).

Đầu vào: kết quả gieo từ cast.py (Chính + Hỗ + Biến + Động hào)
Đầu ra: 5-step structured analysis với:
  - Lời quẻ Chu Dịch (placeholder — em chưa nối Kinh Dịch)
  - Thể-Dụng phân tích đầy đủ
  - Quái Khí Vượng/Suy mùa
  - Pattern khắc ứng + timing

Em là HỌC TRÒ — output là STRUCTURED ANALYSIS, không phải lời tiên đoán.
Anh là người ra quyết định cuối.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from engine.yi_wiki.cast import CastResult
from engine.yi_wiki.hexagrams_64 import lookup as hex_lookup, hao_lookup


# Ngũ hành 8 quẻ (sách trang 23)
QUAI_NGU_HANH = {
    "Càn": "Kim",  "Đoài": "Kim",
    "Khôn": "Thổ", "Cấn": "Thổ",
    "Chấn": "Mộc", "Tốn": "Mộc",
    "Khảm": "Thuỷ",
    "Ly": "Hoả",
}

# Tượng tự nhiên 8 quẻ (trang 33 + 60-61)
QUAI_TUONG_TU_NHIEN = {
    "Càn": "Trời", "Khôn": "Đất",
    "Chấn": "Sấm", "Tốn": "Gió",
    "Khảm": "Nước/Trăng", "Ly": "Lửa/Mặt trời",
    "Cấn": "Núi", "Đoài": "Đầm",
}

QUAI_GIA_DINH = {
    "Càn": "Cha", "Khôn": "Mẹ",
    "Chấn": "Trưởng nam", "Khảm": "Trung nam", "Cấn": "Thiếu nam",
    "Tốn": "Trưởng nữ", "Ly": "Trung nữ", "Đoài": "Thiếu nữ",
}

# Bát Quái Vận Vật (rút gọn từ trang 60-61, dành cho diễn giải nhanh)
QUAI_VAN_VAT = {
    "Càn": "vàng, ngọc, vật tròn, đầu, ngựa, cha, vua quan, vật cứng",
    "Khôn": "đất, vải bố, bụng, trâu, mẹ, dân thường, vật vuông",
    "Chấn": "rồng, sấm, chân, tóc, tre trúc, ngựa nhanh, nhạc khí",
    "Tốn": "gió, gà vịt, đùi, dây thừng, vật thẳng, mùi thơm",
    "Khảm": "lợn, nước, tai, máu, kẻ cướp, xe, vật có lõi",
    "Ly": "lửa, trĩ, mắt, văn thư, lò, vỏ cứng, áo giáp",
    "Cấn": "núi, chó, tay, ngón, quả dưa, chùa miếu, đường",
    "Đoài": "đầm, dê, lưỡi, vật vỡ, đồ có miệng, nô bộc",
}


# Bảng sinh khắc ngũ hành (trang 18-19)
NGU_HANH_SINH = {
    "Kim": "Thuỷ", "Thuỷ": "Mộc", "Mộc": "Hoả",
    "Hoả": "Thổ", "Thổ": "Kim",
}
NGU_HANH_KHAC = {
    "Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thuỷ",
    "Thuỷ": "Hoả", "Hoả": "Kim",
}


# ⭐ 8 quẻ làm SINH Thể — outcomes cụ thể (sách trang 135-138)
QUE_SINH_THE_OUTCOMES = {
    "Càn": "Việc công môn có mừng / công danh tốt / kiện tụng thắng / kim ngọc lợi / "
           "người già tôn trưởng cho của / có quan vui",
    "Khôn": "Vui mừng về ruộng đất / được hàng xóm bạn bè giúp / hoa quả ngũ cốc bội thu / "
            "có vải vóc lụa là",
    "Chấn": "Lợi sơn lâm / được tài từ phương Đông / thu lợi giao dịch gỗ / "
            "người tên thảo mộc giúp",
    "Tốn": "Lợi sơn lâm / tài từ Đông Nam / nghề thảo mộc đem lợi / "
           "trà quả rau tươi đem điều mừng",
    "Khảm": "Mừng từ phương Bắc / nhận của cải phương Bắc / người sống bên nước giúp / "
            "lợi cá muối rượu / văn thư giao dịch tốt",
    "Ly": "Tài phương Nam / văn thư có điều mừng / lợi từ lò nấu / "
          "người tên Hoả đem của",
    "Cấn": "Tài phương Đông Bắc / vui về ruộng núi / người tôn quý / "
           "việc có trước có sau, yên ổn",
    "Đoài": "Tài phương Tây / mừng vui / vàng ngọc lợi / "
            "chủ-khách giảng tập vui / bạn bè đến",
}


# ⭐ 8 quẻ làm KHẮC Thể — outcomes cụ thể (sách trang 138-141)
QUE_KHAC_THE_OUTCOMES = {
    "Càn": "Việc công phiền nhiễu / mất vật báu / tổn thất kim cốc / "
           "tức giận người lớn / có tội với quý nhân",
    "Khôn": "Ruộng đất tổn hại / có người xâm chiếm / kẻ tiểu nhân làm hại / "
            "mất vải vóc / không lợi thóc gạo",
    "Chấn": "Kinh sợ hốt hoảng / thân tâm bất an / nhà gặp yêu ma / "
            "người tên thảo mộc xâm hại / sơn lâm mất mát",
    "Tốn": "Người thảo mộc gây hại / sơn lâm sinh ưu / mưu Đông Nam khó thành / "
           "tai nạn từ đàn bà (tiểu khẩu âm)",
    "Khảm": "Vu khống / kẻ cướp cản đường / thất ý người bên nước / "
            "hoạ vì rượu / âm mưu phương Bắc",
    "Ly": "Khó khăn phương Nam / hoả tai / người tên Hoả đến hại / "
          "tiêu thư phiền nhiễu",
    "Cấn": "Phiền nhiễu liên tục / việc gì cũng không thành / sơn lâm điền thổ mất / "
           "phần mộ không yên",
    "Đoài": "Tây bất lợi / khẩu thiệt phân tranh / bị bẻ gãy / "
            "ẩm thực sinh ưu phiền",
}


# ⭐ Intent mapping — 14 Nhân Sự Chiêm (sách trang 150-170)
INTENT_REGISTRY = {
    "thien_thoi": {
        "label": "Thiên thời (mưa nắng)",
        "the": "trạng thái thời tiết quan tâm",
        "dung": "khí tượng tự nhiên",
        "extra": "Khảm sinh Thể → có mưa | Ly sinh Thể → nắng | Càn → trời quang",
    },
    "gia_trach": {
        "label": "Gia trạch (nhà cửa)",
        "the": "nhà của anh",
        "dung": "ngoại cảnh, hàng xóm, sự kiện ngoài",
    },
    "hon_nhan": {
        "label": "Hôn nhân",
        "the": "nhà người xem (anh)",
        "dung": "nhà đối tượng hôn nhân",
        "extra": "Dụng sinh Thể → hôn nhân dễ thành, được tài. Tỉ hoà → lương phối vô nghi.",
    },
    "sinh_san": {
        "label": "Sinh sản",
        "the": "người mẹ",
        "dung": "đứa con",
        "extra": "Cả Thể và Dụng đều nên VƯỢNG. Quẻ dương + hào dương nhiều → sinh nam.",
    },
    "muu_cau": {
        "label": "Mưu cầu (việc muốn làm)",
        "the": "anh",
        "dung": "sự việc mưu cầu",
    },
    "cau_danh": {
        "label": "Cầu danh (công danh, chức vụ)",
        "the": "anh",
        "dung": "danh / chức",
        "extra": "Đang nhậm chức gặp Dụng khắc Thể → coi chừng mất chức/quan.",
    },
    "cau_tai": {
        "label": "Cầu tài (tiền bạc)",
        "the": "anh",
        "dung": "tài muốn cầu",
        "extra": "Thể khắc Dụng → có tài. Dụng sinh Thể → tài tăng vui. Thể sinh Dụng → phá tài.",
    },
    "giao_dich": {
        "label": "Giao dịch (buôn bán)",
        "the": "anh",
        "dung": "đối tác / hàng hoá",
    },
    "xuat_hanh": {
        "label": "Xuất hành (đi xa, công tác)",
        "the": "anh",
        "dung": "ứng của chuyến đi",
        "extra": ("Thể Càn/Chấn → đa chủ động (nên đi). Khôn/Cấn → bất động (nên ở). "
                  "Khảm → phòng thất thoát. Đoài → có phân tranh."),
    },
    "hanh_nhan": {
        "label": "Hành nhân (người đang đi xa, khi nào về)",
        "the": "anh (người chờ)",
        "dung": "người đang đi xa",
        "extra": "Dụng sinh Thể → người sắp về. Dụng khắc Thể → về chậm.",
    },
    "yet_kien": {
        "label": "Yết kiến (gặp người quan trọng)",
        "the": "anh (người đi gặp)",
        "dung": "người được gặp",
    },
    "that_vat": {
        "label": "Thất vật (mất đồ)",
        "the": "anh",
        "dung": "đồ bị mất",
    },
    "benh_tat": {
        "label": "Bệnh tật",
        "the": "bệnh nhân",
        "dung": "bệnh chứng",
        "extra": ("Thể nên VƯỢNG, không nên SUY. Thể phùng khắc + suy → nguy hiểm. "
                  "Ly sinh Thể → thuốc nóng. Khảm sinh Thể → thuốc lạnh. "
                  "Cấn → ôn bổ. Càn/Đoài → thuốc mát."),
    },
    "quan_tung": {
        "label": "Quan tụng (kiện tụng)",
        "the": "anh",
        "dung": "đối phương / công đường",
    },
    "general": {
        "label": "Tổng quát (không có loại cụ thể)",
        "the": "anh (chủ thể)",
        "dung": "việc / ngoại cảnh",
    },
}


# Quái Khí Vượng theo mùa (trang 24-27)
def quai_khi_season(month: int) -> dict:
    if month in (1, 2): return {"season": "Xuân", "vuong": ["Chấn", "Tốn"], "suy": ["Khôn", "Cấn"]}
    if month in (4, 5): return {"season": "Hạ", "vuong": ["Ly"], "suy": ["Càn", "Đoài"]}
    if month in (7, 8): return {"season": "Thu", "vuong": ["Càn", "Đoài"], "suy": ["Chấn", "Tốn"]}
    if month in (10, 11): return {"season": "Đông", "vuong": ["Khảm"], "suy": ["Ly"]}
    return {"season": "Tháng đất (Thìn/Tuất/Sửu/Mùi)",
            "vuong": ["Khôn", "Cấn"], "suy": ["Khảm"]}


@dataclass
class TheDungAnalysis:
    the_que: str            # quẻ Thể
    dung_que: str           # quẻ Dụng
    the_position: str       # "thượng" hoặc "hạ"
    the_hanh: str           # ngũ hành Thể
    dung_hanh: str
    relationship: str       # "dụng_sinh_the" | "the_khac_dung" | "ti_hoa" | "the_sinh_dung" | "dung_khac_the"
    auspice: str            # "cát" | "hung" | "bình"
    explanation: str
    detail: str


@dataclass
class InterpretationResult:
    """Kết quả 5-step phân tích."""
    cast: CastResult

    # Bước 1
    cast_summary: str

    # Bước 2 (placeholder — chưa nối Kinh Dịch)
    chu_dich_hint: str

    # Bước 3 ⭐
    the_dung: TheDungAnalysis

    # Bước 4
    quai_khi: dict
    the_quaikhi: str        # "vượng" | "suy" | "bình"

    # Tượng + diễn giải
    chinh_tuong: str
    bien_tuong: str
    ho_tuong: str
    overall: str
    warnings: list[str] = field(default_factory=list)

    # ⭐ PHASE C — Intent-aware
    intent: str = "general"
    intent_label: str = ""
    intent_mapping: str = ""             # Thể = X, Dụng = Y
    intent_extra: str = ""               # Quy tắc đặc biệt cho intent

    # ⭐ Đằng vũ — cấu kết hành
    the_dang_vu_count: int = 0           # số quẻ cùng hành với Thể trong Hỗ+Biến
    dung_dang_vu_count: int = 0

    # ⭐ Specific outcomes from 8 quẻ Sinh/Khắc Thể
    sinh_the_outcomes: list[str] = field(default_factory=list)
    khac_the_outcomes: list[str] = field(default_factory=list)

    # ⭐ 64 Hexagram names (King Wen)
    chinh_hexagram: dict = field(default_factory=dict)
    bien_hexagram: dict = field(default_factory=dict)
    ho_hexagram: dict = field(default_factory=dict)

    # ⭐ Lời hào tại vị trí động
    moving_haotu: str = ""

    # ⭐ Trùng Phùng (Thầy chỉ đạo A6) — quẻ Thuần
    trung_phung_chinh: bool = False
    trung_phung_bien: bool = False
    trung_phung_meaning: str = ""

    # ⭐ Bảng thuốc benh_tat (Thầy chỉ đạo B4)
    benh_tat_thuoc: str = ""

    # ⭐⭐ CẢI TIẾN #1 — ỨNG KỲ 3 GIAI ĐOẠN (Mai Hoa TR.133 + TR.235)
    # "Quẻ gốc = bắt đầu | Quẻ hỗ = giữa | Quẻ biến = kết cục"
    ung_ky_dau: str = ""                 # Chính quẻ — mở đầu sự việc
    ung_ky_giua: str = ""                # Hỗ quẻ — trung gian khắc ứng
    ung_ky_cuoi: str = ""                # Biến quẻ — kết cục cuối

    # ⭐⭐ CẢI TIẾN #2 — HỖ-CỦA-THỂ vs HỖ-CỦA-DỤNG (Mai Hoa TR.235)
    # "Hỗ của Thể vô cùng quan trọng. Hỗ của Dụng chỉ là thứ yếu."
    ho_the_que: str = ""                 # Quẻ Hỗ-của-Thể (cùng vị trí với Thể trong bộ Hỗ)
    ho_dung_que: str = ""                # Quẻ Hỗ-của-Dụng
    ho_the_hanh: str = ""
    ho_the_relationship: str = ""        # quan hệ Hỗ-Thể vs Thể: sinh/khắc/tỉ hoà
    ho_the_meaning: str = ""             # diễn giải tầm quan trọng

    # ⭐⭐⭐ Gap 2 (Thầy Q3 tr.112-114): BƯỚC 3 — NGOẠI ỨNG
    external_omen_input: str = ""        # raw text user kể
    external_omen_category: str = "none" # "cát" | "hung" | "hỗn hợp" | "trung tính" | "none"
    external_omen_weight: int = 0        # -2..+2
    external_omen_note: str = ""
    # Thập ứng (Mai Hoa Q2) — phân loại nguồn ứng
    external_omen_source: str = "none"   # "thiên thời" | "địa lý" | "nhân sự" | "vật loại" | "thanh âm" | "hành chỉ" | "ngoại (chung)" | "none"
    external_omen_thap_ung: str = ""     # nhãn Thập ứng (vd "Thiên thời ứng")

    # ⭐⭐⭐ Gap 3 (Thầy Q3 tr.114): BƯỚC 4 — TƯ THẾ THÂN THỂ
    posture_input: str = ""              # nằm/ngồi/đứng/đi/chạy
    posture_speed: str = ""              # chậm nhất/chậm trễ/trung bình/nhanh/rất nhanh
    posture_note: str = ""

    # ⭐ Quy trình 4 bước hoàn chỉnh — flag cho UI
    four_steps_complete: bool = False    # True nếu đầy đủ 4 bước

    # ⭐ Cảnh báo từ cast (Hỗ Thuần Càn/Khôn)
    ho_warning: str = ""

    # ⭐⭐⭐ PARADIGM SHIFT (Vận Pháp Thi tr.78 + chu trình Tính-Thần-Số-Tượng-Khí tr.69)
    # Mai Hoa = ĐỌC ĐỒNG DẠNG, không phải predict outcome.
    # Output paradigm: quan vật → trace ngược về Tính, đọc tâm vị trí, đọc tiếng vũ trụ.
    paradigm_mirror_reading: str = ""    # "Khoảnh khắc Anh hỏi phản chiếu..."
    paradigm_quan_vat_trace: list[str] = field(default_factory=list)  # Khí → Tượng → Số → Thần → Tính
    paradigm_tam_position: str = ""      # "Tâm Anh đang ở..."
    paradigm_universe_message: str = ""  # "Vũ trụ đang nói..."


TRUNG_PHUNG_MEANINGS = {
    "Càn": "Thuần Càn — trời cao thượng, chính nhân quân tử, quyền lực tối thượng",
    "Khôn": "Thuần Khôn — đất nuôi, nhu thuận tuyệt đối",
    "Chấn": "Thuần Chấn — sấm trên sấm, chấn động liên hồi",
    "Tốn": "Thuần Tốn — gió vào gió, thâm nhập từng kẽ",
    "Khảm": "Thuần Khảm — hiểm trong hiểm, ★ ĐẠI NGUY",
    "Ly": "Thuần Ly — sáng trên sáng, văn minh rực rỡ",
    "Cấn": "Thuần Cấn — ngăn trong ngăn, đứng yên hoàn toàn",
    "Đoài": "Thuần Đoài — vui trong vui, đa khẩu thiệt",
}

BENH_TAT_THUOC_MAP = {
    "Ly": "💊 Thuốc NÓNG (Ly sinh Thể)",
    "Khảm": "💊 Thuốc LẠNH (Khảm sinh Thể)",
    "Cấn": "💊 Thuốc ÔN BỔ (Cấn sinh Thể)",
    "Càn": "💊 Thuốc MÁT (Càn sinh Thể)",
    "Đoài": "💊 Thuốc MÁT (Đoài sinh Thể)",
}


# ⭐ Gap 3 fix (Thầy Q3 tr.114): TƯ THẾ THÂN THỂ khi khởi quẻ → tốc độ thành công
POSTURE_TIMING = {
    "nằm":    {"label": "Nằm trên giường",  "speed": "chậm nhất",  "weight": -2,
               "note": "Thân tĩnh hoàn toàn → việc thành công bị chậm trễ nhất."},
    "ngồi":   {"label": "Ngồi",             "speed": "chậm trễ",   "weight": -1,
               "note": "Thân tĩnh → việc thành công bị chậm trễ."},
    "đứng":   {"label": "Đứng yên",         "speed": "trung bình", "weight": 0,
               "note": "Thân trung bình → việc tiến vừa phải."},
    "đi":     {"label": "Đi bộ",            "speed": "nhanh",      "weight": 1,
               "note": "Thân động vừa → việc thành công nhanh."},
    "chạy":   {"label": "Chạy bộ",          "speed": "rất nhanh",  "weight": 2,
               "note": "Thân động mạnh → việc tiến tới với tốc độ rất nhanh."},
}


# ⭐ Gap 2 fix (Thầy Q3 tr.112-114): NGOẠI ỨNG khi khởi quẻ → cát/hung modifier
# Keyword-based simple classifier. Em ghi nhận chỉ là gợi ý, không quyết định.
OMEN_POSITIVE = (
    "tròn", "hoàn chỉnh", "đầy", "sáng",
    "chim đậu", "chim hót", "hoa nở", "hoa khai", "ánh sáng",
    "lời chúc", "lời tốt", "tiếng cười", "tiếng hát", "tiếng chuông",
    "khách quý", "quý nhân", "mây lành", "rồng", "phượng",
    "vật quý", "vàng", "ngọc",
)
OMEN_NEGATIVE = (
    "vỡ", "khuyết", "rách", "thiếu", "rơi", "ngã", "đổ",
    "tiếng động", "tiếng la", "tiếng khóc", "tiếng cãi", "tiếng động xấu",
    "vật rơi", "lá rơi", "cành gãy",
    "lời dữ", "lời chửi", "lời cãi", "lời tang", "lời xui",
    "máu", "tang", "khói đen", "âm u",
    "quạ kêu", "chó sủa dữ", "rắn", "chuột",
)


def compute_paradigm_reading(
    cast: "CastResult",
    the_que: str, dung_que: str,
    the_h: str, dung_h: str,
    the_quaikhi: str,
    omen_category: str, omen_text: str,
    posture_data: dict | None,
    intent_label: str,
) -> dict:
    """⭐ Paradigm shift Q3 tr.69+78: tính các fields đọc-đồng-dạng.

    Mai Hoa = ĐỌC ĐỒNG DẠNG, KHÔNG predict.
    Theo Tổ sư: Tính → Thần → Số → Tượng → Khí → quy về Thần.
    Mai Hoa đọc ngược: Khí (quan vật) → Tượng → Số → Thần → Tính.
    """
    chinh = cast.chinh_quai
    bien = cast.bien_quai
    ho = cast.ho_quai

    # 1. Mirror reading — khoảnh khắc phản chiếu cái gì
    mirror = (
        f"Khoảnh khắc Anh hỏi (thân thể {posture_data['label'] if posture_data else 'chưa rõ'}) "
        f"phản chiếu vũ trụ qua quẻ {chinh.name}. "
        f"Theo Vận Pháp Thi (Tổ sư): 'Một vật vốn có một thân, một thân lại có một trời đất' — "
        f"khoảnh khắc này là TIỂU VŨ TRỤ chứa đầy đủ quy luật của ĐẠI VŨ TRỤ vận hành."
    )

    # 2. Quan vật trace: chu trình Tính-Thần-Số-Tượng-Khí (đọc ngược từ Khí về Tính)
    # KHÍ (vật chất / năng lượng vũ trụ lúc hỏi)
    khi_parts = []
    if omen_text:
        khi_parts.append(f"ngoại ứng: {omen_text[:80]}")
    if posture_data:
        khi_parts.append(f"thân thế: {posture_data['label']}")
    khi_parts.append(f"thời điểm: {cast.inputs}")
    khi = "KHÍ (vật chất hiện tại): " + " | ".join(khi_parts)

    # TƯỢNG (hình ảnh quẻ)
    tuong = (
        f"TƯỢNG (quẻ Chính): {chinh.name} = "
        f"{QUAI_TUONG_TU_NHIEN.get(chinh.upper_que,'')} trên "
        f"{QUAI_TUONG_TU_NHIEN.get(chinh.lower_que,'')}"
    )

    # SỐ (cấu trúc số học)
    so = (
        f"SỐ: thượng={chinh.upper_num} / hạ={chinh.lower_num} / "
        f"động hào={cast.moving_line} → biến {bien.name}, hỗ {ho.name}"
    )

    # THẦN (động lực Thể-Dụng + thịnh suy)
    quaikhi_label = {"vượng": "đang VƯỢNG", "suy": "đang SUY", "bình": "ở thế bình"}.get(the_quaikhi, "")
    than = (
        f"THẦN (động lực): Thể={the_que}({the_h}) {quaikhi_label}, "
        f"Dụng={dung_que}({dung_h}). Tương tác Ngũ Hành quyết định độ thuận."
    )

    # TÍNH (bản chất khoảnh khắc — kết đọng)
    if the_h == dung_h:
        tinh_essence = "tỉ hoà — bản chất khoảnh khắc là ĐỒNG ĐIỆU, không xung đột"
    elif NGU_HANH_SINH.get(dung_h) == the_h:
        tinh_essence = "được nuôi — bản chất khoảnh khắc là ĐANG ĐƯỢC HỖ TRỢ từ ngoài"
    elif NGU_HANH_KHAC.get(the_h) == dung_h:
        tinh_essence = "chế ngự — bản chất khoảnh khắc là CHỦ ĐỘNG ÁP DỤNG nội lực ra ngoài"
    elif NGU_HANH_SINH.get(the_h) == dung_h:
        tinh_essence = "cho đi — bản chất khoảnh khắc là TIẾT KHÍ, mất sức cho ngoại cảnh"
    elif NGU_HANH_KHAC.get(dung_h) == the_h:
        tinh_essence = "bị ép — bản chất khoảnh khắc là CHỊU LỰC từ ngoài"
    else:
        tinh_essence = "trung tính"
    tinh = f"TÍNH (bản chất): {tinh_essence}"

    quan_vat_trace = [khi, tuong, so, than, tinh]

    # 3. Tam position — Anh đang ở đâu
    posture_meta = ""
    if posture_data:
        speed_label = posture_data.get("speed", "")
        posture_meta = f"; thân thể {posture_data['label']} → động lực {speed_label}"
    if the_quaikhi == "vượng":
        position_meta = "Thể đang VƯỢNG (mạnh)"
    elif the_quaikhi == "suy":
        position_meta = "Thể đang SUY (yếu)"
    else:
        position_meta = "Thể ở thế bình"
    tam = (
        f"Tâm Anh đang ở vị trí: {the_que} ({QUAI_GIA_DINH.get(the_que,'')}, "
        f"hành {the_h}), {position_meta}{posture_meta}. "
        f"Tình huống ({intent_label}) phản chiếu qua quẻ {dung_que} ({dung_h})."
    )

    # 4. Universe message — synthesis (không verdict)
    omen_phrase = ""
    if omen_category == "cát":
        omen_phrase = " Khí lành quanh Anh."
    elif omen_category == "hung":
        omen_phrase = " Khí dữ quanh Anh — cần để ý."
    elif omen_category == "hỗn hợp":
        omen_phrase = " Khí xung quanh hỗn hợp — Anh tự nhận định."

    # Universe message dùng tượng tự nhiên kết hợp
    nature_upper = QUAI_TUONG_TU_NHIEN.get(chinh.upper_que, "")
    nature_lower = QUAI_TUONG_TU_NHIEN.get(chinh.lower_que, "")
    nature_bien = QUAI_TUONG_TU_NHIEN.get(bien.upper_que if cast.moving_line >= 4 else bien.lower_que, "")
    universe = (
        f"Vũ trụ đang nói qua khoảnh khắc này: "
        f"\"{nature_upper} trên {nature_lower}\" — tình huống hiện tại. "
        f"Hào {cast.moving_line} động → chuyển sang \"{nature_bien}\" — hướng biến hoá.{omen_phrase} "
        f"Đây KHÔNG phải dự đoán tương lai — đây là **đọc đồng dạng** giữa Anh và vũ trụ. "
        f"Anh quyết định cách phản hồi với vũ trụ qua hành động + tâm."
    )

    return {
        "mirror_reading": mirror,
        "quan_vat_trace": quan_vat_trace,
        "tam_position": tam,
        "universe_message": universe,
    }


def classify_omen(omen_text: str) -> dict:
    """Phân loại ngoại ứng (free-text) thành cát/hung/trung tính.

    Args:
        omen_text: text mô tả ngoại ứng user kể (vd "lúc nghĩ về việc này, có chim đậu trên cành")

    Returns:
        dict {category, weight (-2..+2), matched_keywords, note}
    """
    if not omen_text or not omen_text.strip():
        return {"category": "none", "weight": 0, "matched_keywords": [], "note": ""}

    text = omen_text.lower()
    pos_matches = [kw for kw in OMEN_POSITIVE if kw in text]
    neg_matches = [kw for kw in OMEN_NEGATIVE if kw in text]

    if pos_matches and not neg_matches:
        return {
            "category": "cát",
            "weight": 1 + (1 if len(pos_matches) >= 2 else 0),
            "matched_keywords": pos_matches,
            "note": f"Điềm lành ({', '.join(pos_matches[:3])}) → ngoại ứng CÁT.",
        }
    if neg_matches and not pos_matches:
        return {
            "category": "hung",
            "weight": -1 - (1 if len(neg_matches) >= 2 else 0),
            "matched_keywords": neg_matches,
            "note": f"Điềm dữ ({', '.join(neg_matches[:3])}) → ngoại ứng HUNG.",
        }
    if pos_matches and neg_matches:
        return {
            "category": "hỗn hợp",
            "weight": 0,
            "matched_keywords": pos_matches + neg_matches,
            "note": (
                f"Ngoại ứng hỗn hợp: có cả điềm lành ({pos_matches[0]}) "
                f"và điềm dữ ({neg_matches[0]}). Cần Anh tự nhận định."
            ),
        }
    return {
        "category": "trung tính",
        "weight": 0,
        "matched_keywords": [],
        "note": "Em chưa nhận diện được điềm rõ ràng trong mô tả. Anh tự cân nhắc.",
    }


# ─── THẬP ỨNG — 10 loại ngoại ứng (từ Mai Hoa Q2 thâm nhuần 2026-05-19) ─────
#
# Reference: Mai Hoa Dịch Số Quyển 2 — Chiêm bốc huyền cơ
# Sách dạy phân biệt 10 loại "ứng" (signals) khi đoán quẻ:
#   1. Chính ứng — Ứng trực tiếp câu hỏi (Thể-Dụng)
#   2. Biến ứng — Ứng theo Quẻ Biến
#   3. Nhật ứng — Ứng theo Can-Chi ngày hiện hành
#   4. Ngoại ứng — Môi trường khách quan (generic)
#   5. Thiên thời ứng — Thời tiết, mưa, gió, sấm, mặt trời, trăng
#   6. Địa lý ứng — Địa hình, vị trí, núi sông, đường
#   7. Nhân sự ứng — Người gặp, người đến, người đi
#   8. Vật loại ứng — Vật (chim, côn trùng, thú, vật rơi)
#   9. Thanh âm ứng — Âm thanh (chuông, sủa, khóc, hát, sấm)
#  10. Hành chỉ ứng — Tư thế thân thể người hỏi (ngồi/đứng/nằm/đi)

THAP_UNG_KEYWORDS = {
    "thiên thời": [
        "mưa", "gió", "sấm", "chớp", "nắng", "mây", "tuyết", "sương", "mù",
        "mặt trời", "trăng", "sao", "thiên hà", "bão", "lốc", "trời quang",
        "nóng", "lạnh", "ấm", "mát", "trời",
    ],
    "địa lý": [
        "núi", "sông", "biển", "đầm", "ruộng", "rừng", "đường", "cầu", "hồ",
        "đất", "đá", "vực", "thung lũng", "đỉnh", "chân núi", "bờ",
    ],
    "nhân sự": [
        "người đến", "người gặp", "khách", "đàn ông", "đàn bà", "trẻ em",
        "ông già", "bà già", "tăng", "đạo sĩ", "thầy", "trò", "bạn",
        "kẻ lạ", "kẻ ăn xin", "vua", "quan", "công nhân", "thương nhân",
    ],
    "vật loại": [
        "chim", "rồng", "rắn", "rùa", "cá", "côn trùng", "ong", "ruồi",
        "chó", "mèo", "trâu", "bò", "ngựa", "lợn", "dê", "gà", "vịt",
        "vật rơi", "đồ vỡ", "lá rơi", "bay qua", "đậu", "bò ra",
    ],
    "thanh âm": [
        "tiếng", "âm", "kêu", "hú", "khóc", "cười", "hát", "chuông",
        "sấm", "nổ", "gãy", "đổ", "vang", "rền", "rít",
    ],
    "hành chỉ": [
        "ngồi", "đứng", "nằm", "đi", "chạy", "quỳ", "cúi", "ngẩng",
        "tư thế", "cử động", "thân thể",
    ],
}


def classify_omen_thap_ung(omen_text: str) -> dict:
    """Phân loại ngoại ứng theo 10 loại Mai Hoa Q2.

    Mở rộng classify_omen() để xác định **loại** ứng (source) bên cạnh
    cát/hung. Output có thêm:
      - omen_source: 1 trong ['thiên thời', 'địa lý', 'nhân sự', 'vật loại',
                              'thanh âm', 'hành chỉ', 'ngoại (chung)']
      - thap_ung_label: tên trong Thập ứng
    """
    base = classify_omen(omen_text)
    if base["category"] == "none":
        return {**base, "omen_source": "none", "thap_ung_label": "Không có"}

    text = (omen_text or "").lower()
    # Score mỗi source
    scores = {src: sum(1 for kw in kws if kw in text) for src, kws in THAP_UNG_KEYWORDS.items()}
    top_source = max(scores, key=scores.get) if max(scores.values()) > 0 else None

    if top_source is None:
        return {
            **base,
            "omen_source": "ngoại (chung)",
            "thap_ung_label": "Ngoại ứng (chung)",
        }

    # Map source → Thập ứng label
    THAP_UNG_LABEL_MAP = {
        "thiên thời": "Thiên thời ứng",
        "địa lý": "Địa lý ứng",
        "nhân sự": "Nhân sự ứng",
        "vật loại": "Vật loại ứng",
        "thanh âm": "Thanh âm ứng",
        "hành chỉ": "Hành chỉ ứng",
    }
    return {
        **base,
        "omen_source": top_source,
        "thap_ung_label": THAP_UNG_LABEL_MAP[top_source],
        "scores": scores,
    }


def tam_yeu_summary(
    *,
    the_que: str, dung_que: str,
    relationship: str, auspice: str,
    the_quaikhi: str,
    external_omen_category: str = "none",
    external_omen_weight: int = 0,
    external_omen_thap_ung: str = "",
) -> dict:
    """Tam yếu — 3 yếu tố cốt lõi khi xem quẻ Mai Hoa.

    Reference: Mai Hoa Q1 thâm nhuần (2026-05-19) — `data/yi_publishing/mai_hoa_thamnhuan/master`
    Tam yếu (3 yếu): tóm tắt 3 thành tố then chốt cho mọi luận quẻ.

    Args:
        the_que/dung_que: quẻ Thể, Dụng (vd "Càn", "Khôn")
        relationship: từ TheDungAnalysis.relationship
        auspice: "cát"/"hung"/"bình"
        the_quaikhi: "vượng"/"suy"/"bình" — quái khí Thể theo mùa
        external_omen_*: từ classify_omen_thap_ung()

    Returns:
        dict 3 yếu + verdict tổng hợp.
    """
    # Yếu 1: Thể-Dụng (Quẻ Chánh)
    yeu_1 = {
        "name": "Quẻ Chánh — Thể & Dụng",
        "the": the_que,
        "dung": dung_que,
        "relationship": relationship,
        "auspice": auspice,
        "interpretation": _interpret_yeu_1(relationship, auspice),
    }

    # Yếu 2: Quái khí (mùa) — Thể vượng/suy ảnh hưởng kết quả
    yeu_2 = {
        "name": "Quái Khí (Thể theo mùa)",
        "the_quaikhi": the_quaikhi,
        "interpretation": _interpret_yeu_2(the_quaikhi),
    }

    # Yếu 3: Ngoại ứng (Khắc ứng + Thập ứng)
    yeu_3 = {
        "name": "Khắc Ứng (Ngoại ứng - Thập ứng)",
        "omen_category": external_omen_category,
        "omen_weight": external_omen_weight,
        "thap_ung_label": external_omen_thap_ung,
        "interpretation": _interpret_yeu_3(external_omen_category, external_omen_thap_ung),
    }

    # Tổng hợp Verdict
    score = 0
    if auspice == "cát":
        score += 2
    elif auspice == "hung":
        score -= 2
    if the_quaikhi == "vượng":
        score += 1
    elif the_quaikhi == "suy":
        score -= 1
    score += external_omen_weight

    if score >= 2:
        verdict = "ĐẠI CÁT — 3/3 yếu thuận"
    elif score >= 1:
        verdict = "CÁT — đa số thuận"
    elif score <= -2:
        verdict = "ĐẠI HUNG — 3/3 yếu nghịch"
    elif score <= -1:
        verdict = "HUNG — đa số nghịch"
    else:
        verdict = "BÌNH — cát hung lẫn, cần xét thêm Tâm"

    return {
        "yeu_1_que_chanh": yeu_1,
        "yeu_2_quai_khi": yeu_2,
        "yeu_3_khac_ung": yeu_3,
        "score": score,
        "verdict": verdict,
        "note": "Tam yếu = 3 chân kiềng. Yếu nào yếu hơn → khoảnh khắc đó là gốc rễ.",
    }


def _interpret_yeu_1(rel: str, ausp: str) -> str:
    table = {
        "dung_sinh_the": "Ngoại cảnh nuôi mình — CÁT nhất, vận thuận đến",
        "the_khac_dung": "Mình thắng việc, có quyền kiểm soát",
        "ti_hoa":        "Tỷ hoà — bình ổn, không thay đổi lớn",
        "the_sinh_dung": "Mình cho đi sức / tài / công — tổn",
        "dung_khac_the": "Ngoại cảnh đè mình — bất lợi, cần phòng",
    }
    return table.get(rel, f"Quan hệ Thể-Dụng: {rel} ({ausp})")


def _interpret_yeu_2(qk: str) -> str:
    return {
        "vượng": "Thể đang VƯỢNG theo mùa — sức mạnh nội tại tốt, khả năng thực hiện cao",
        "suy":   "Thể đang SUY theo mùa — yếu, cần phòng tổn / chờ thời",
        "bình":  "Thể ở thế BÌNH — không cản trở nhưng cũng không thúc đẩy",
    }.get(qk, "Quái khí không xác định")


def _interpret_yeu_3(cat: str, label: str) -> str:
    if cat == "cát":
        return f"Ngoại ứng CÁT ({label}) — vũ trụ gửi tín hiệu thuận, củng cố quẻ"
    if cat == "hung":
        return f"Ngoại ứng HUNG ({label}) — vũ trụ gửi tín hiệu nghịch, cảnh báo"
    if cat == "hỗn hợp":
        return f"Ngoại ứng HỖN HỢP ({label}) — tín hiệu trộn lẫn, cần xét Tâm"
    if cat == "trung tính":
        return "Ngoại ứng trung tính — không rõ điềm"
    return "Không có ngoại ứng"


def _phase_meaning(phase_label: str, que_name: str, upper: str, lower: str,
                   the_h: str, dung_h: str | None = None) -> str:
    """Diễn giải 1 giai đoạn ứng kỳ (đầu/giữa/cuối)."""
    upper_h = QUAI_NGU_HANH[upper]
    lower_h = QUAI_NGU_HANH[lower]
    parts = [f"{phase_label}: {que_name} ({upper}/{lower})"]

    # Quan hệ với Thể
    for h, pos in ((upper_h, "trên"), (lower_h, "dưới")):
        if NGU_HANH_SINH.get(h) == the_h:
            parts.append(f"{pos}={h} sinh Thể ({the_h}) → có cứu trợ")
        elif NGU_HANH_KHAC.get(h) == the_h:
            parts.append(f"{pos}={h} khắc Thể ({the_h}) → bất lợi")
        elif h == the_h:
            parts.append(f"{pos}={h} tỉ hoà Thể → bình")
    return " | ".join(parts)


def compute_ung_ky_three_phases(cast: CastResult, the_h: str) -> tuple[str, str, str]:
    """Cải tiến #1: Trả về 3 chuỗi mô tả 3 giai đoạn ứng kỳ.

    Cơ sở: Mai Hoa TR.133 ("ứng kỳ quẻ gốc là bắt đầu sự vật, ứng kỳ của quẻ hỗ
    là thời khắc ở trong sự kiện, ứng kỳ của quẻ biến là điểm cuối cùng kết cục")
    + TR.235 ("quẻ dụng là mở đầu, quẻ hỗ là giữa, quẻ biến là sau rốt").
    """
    dau = _phase_meaning(
        "⏱ ĐẦU sự việc", cast.chinh_quai.name,
        cast.chinh_quai.upper_que, cast.chinh_quai.lower_que, the_h,
    )
    giua = _phase_meaning(
        "⏱ GIỮA sự việc (trung gian khắc ứng)", cast.ho_quai.name,
        cast.ho_quai.upper_que, cast.ho_quai.lower_que, the_h,
    )
    cuoi = _phase_meaning(
        "⏱ KẾT CỤC", cast.bien_quai.name,
        cast.bien_quai.upper_que, cast.bien_quai.lower_que, the_h,
    )
    return dau, giua, cuoi


def compute_ho_the_dung(cast: CastResult, the_position: str, the_h: str) -> dict:
    """Cải tiến #2: Tách Hỗ thành Hỗ-của-Thể và Hỗ-của-Dụng.

    Cơ sở: Mai Hoa TR.235 — "Nếu Thể ở quẻ dưới thì Hỗ dưới = Hỗ của Thể,
    Hỗ trên = Hỗ của Dụng. Hỗ của Thể vô cùng quan trọng. Hỗ của Dụng chỉ
    là thứ yếu."
    """
    if the_position == "hạ":
        ho_the_q = cast.ho_quai.lower_que
        ho_dung_q = cast.ho_quai.upper_que
    else:
        ho_the_q = cast.ho_quai.upper_que
        ho_dung_q = cast.ho_quai.lower_que

    ho_the_h = QUAI_NGU_HANH[ho_the_q]

    # Quan hệ Hỗ-Thể ↔ Thể
    if ho_the_h == the_h:
        rel = "tỉ hoà"
        meaning = (
            f"Hỗ-của-Thể là {ho_the_q} ({ho_the_h}) tỉ hoà với Thể → "
            f"giữa kỳ thuận, không trở ngại lớn"
        )
    elif NGU_HANH_SINH.get(ho_the_h) == the_h:
        rel = "sinh Thể"
        meaning = (
            f"Hỗ-của-Thể là {ho_the_q} ({ho_the_h}) SINH Thể ({the_h}) → "
            f"★ giữa kỳ có cứu trợ quan trọng — đây là tín hiệu mạnh"
        )
    elif NGU_HANH_KHAC.get(ho_the_h) == the_h:
        rel = "khắc Thể"
        meaning = (
            f"Hỗ-của-Thể là {ho_the_q} ({ho_the_h}) KHẮC Thể ({the_h}) → "
            f"⚠️ giữa kỳ có lực ép quan trọng từ tượng {ho_the_q} "
            f"({QUAI_VAN_VAT[ho_the_q]})"
        )
    elif NGU_HANH_SINH.get(the_h) == ho_the_h:
        rel = "Thể sinh"
        meaning = (
            f"Hỗ-của-Thể là {ho_the_q} ({ho_the_h}) được Thể SINH → "
            f"giữa kỳ Thể phải cho đi sức nuôi tình huống — mất sức"
        )
    elif NGU_HANH_KHAC.get(the_h) == ho_the_h:
        rel = "Thể khắc"
        meaning = (
            f"Hỗ-của-Thể là {ho_the_q} ({ho_the_h}) bị Thể KHẮC → "
            f"giữa kỳ Thể chế ngự được tình huống"
        )
    else:
        rel = "không rõ"
        meaning = ""

    return {
        "ho_the_que": ho_the_q,
        "ho_dung_que": ho_dung_q,
        "ho_the_hanh": ho_the_h,
        "ho_the_relationship": rel,
        "ho_the_meaning": meaning,
    }


def analyze(cast: CastResult, month: Optional[int] = None,
            intent: str = "general",
            external_omen: Optional[str] = None,
            posture: Optional[str] = None) -> InterpretationResult:
    """Phân tích kết quả gieo quẻ theo 4 BƯỚC Thiệu Khang Tiết (Q3 tr.112-114).

    BƯỚC 1: Đối chiếu lời quẻ + lời hào (hex_lookup, hao_lookup)
    BƯỚC 2: Thể-Dụng + Ngũ Hành sinh khắc
    BƯỚC 3: Ngoại ứng (Khắc-Ứng) — TỪ external_omen text
    BƯỚC 4: Tư thế thân thể — TỪ posture

    Quy tắc PRIORITY (tr.114): "Quẻ chủ, khắc ứng thứ".

    Args:
        cast: kết quả từ cast_by_time()
        month: tháng (1-12) để xét Quái Khí Vượng/Suy
        intent: loại việc hỏi (key trong INTENT_REGISTRY)
        external_omen: text mô tả hiện tượng bất thường lúc khởi quẻ
            (vd: "có chim đậu trên cành", "vật rơi vỡ", "tiếng cười xa")
        posture: tư thế Anh khi khởi quẻ — "nằm" | "ngồi" | "đứng" | "đi" | "chạy"
    """
    m = month or cast.inputs.get("month", 1)
    moving = cast.moving_line
    intent_meta = INTENT_REGISTRY.get(intent, INTENT_REGISTRY["general"])

    # ── Bước 3: Thể-Dụng ──
    # Hào 1-3 = quẻ dưới, 4-6 = quẻ trên
    # Quẻ chứa hào động = DỤNG
    dung_is_upper = moving >= 4
    if dung_is_upper:
        the_que = cast.chinh_quai.lower_que
        dung_que = cast.chinh_quai.upper_que
        the_pos = "hạ"
    else:
        the_que = cast.chinh_quai.upper_que
        dung_que = cast.chinh_quai.lower_que
        the_pos = "thượng"

    the_h = QUAI_NGU_HANH[the_que]
    dung_h = QUAI_NGU_HANH[dung_que]

    if the_h == dung_h:
        rel = "ti_hoa"
        auspice = "cát"
        explain = f"Thể-Dụng cùng hành ({the_h}) → TỈ HOÀ → bình thuận"
        detail = "Tỉ hoà là 1/3 quan hệ cát — thuận lợi tự nhiên, không trở ngại."
    elif NGU_HANH_SINH.get(dung_h) == the_h:
        rel = "dung_sinh_the"
        auspice = "cát"
        explain = f"DỤNG sinh THỂ ({dung_h} → {the_h}) → CÁT NHẤT"
        detail = "Ngoại cảnh nuôi mình. Tốt nhất trong 5 quan hệ."
    elif NGU_HANH_KHAC.get(the_h) == dung_h:
        rel = "the_khac_dung"
        auspice = "cát"
        explain = f"THỂ khắc DỤNG ({the_h} → {dung_h}) → CÁT"
        detail = "Ta thắng việc, khắc chế được ngoại cảnh."
    elif NGU_HANH_SINH.get(the_h) == dung_h:
        rel = "the_sinh_dung"
        auspice = "hung"
        explain = f"THỂ sinh DỤNG ({the_h} → {dung_h}) → HUNG (mất sức)"
        detail = "Mình cho đi sức — ngoại cảnh hưởng lợi từ mình."
    elif NGU_HANH_KHAC.get(dung_h) == the_h:
        rel = "dung_khac_the"
        auspice = "hung"
        explain = f"DỤNG khắc THỂ ({dung_h} → {the_h}) → HUNG"
        detail = "Ngoại cảnh đè ta — bất lợi."
    else:
        rel = "unknown"
        auspice = "bình"
        explain = "Quan hệ không rõ"
        detail = ""

    the_dung = TheDungAnalysis(
        the_que=the_que, dung_que=dung_que,
        the_position=the_pos,
        the_hanh=the_h, dung_hanh=dung_h,
        relationship=rel, auspice=auspice,
        explanation=explain, detail=detail,
    )

    # ── Bước 4 phụ: Quái Khí ──
    qk = quai_khi_season(m)
    if the_que in qk["vuong"]:
        the_qk = "vượng"
    elif the_que in qk["suy"]:
        the_qk = "suy"
    else:
        the_qk = "bình"

    # ── Tượng (đọc theo Bát Quái Vận Vật) ──
    def _tuong(q: str) -> str:
        return f"{q} ({QUAI_TUONG_TU_NHIEN[q]}, {QUAI_GIA_DINH[q]}): {QUAI_VAN_VAT[q]}"

    chinh_tuong = (
        f"{cast.chinh_quai.upper_que}/{cast.chinh_quai.lower_que} — "
        f"Trên: {_tuong(cast.chinh_quai.upper_que)}\n"
        f"Dưới: {_tuong(cast.chinh_quai.lower_que)}"
    )
    bien_tuong = (
        f"{cast.bien_quai.upper_que}/{cast.bien_quai.lower_que} — "
        f"Hào {moving} động → "
        f"{cast.chinh_quai.upper_que if dung_is_upper else cast.chinh_quai.lower_que} "
        f"đổi thành {cast.bien_quai.upper_que if dung_is_upper else cast.bien_quai.lower_que}"
    )
    ho_tuong = (
        f"{cast.ho_quai.upper_que}/{cast.ho_quai.lower_que} (quẻ ẩn từ hào 2-3-4 + 3-4-5)"
    )

    # ⭐⭐⭐ PARADIGM SHIFT — Compute đọc-đồng-dạng fields TRƯỚC khi build overall
    _posture_data_for_paradigm = POSTURE_TIMING.get(posture.lower() if posture else "", None)
    _omen_info_preview = classify_omen(external_omen or "")
    _paradigm = compute_paradigm_reading(
        cast, the_que, dung_que, the_h, dung_h,
        the_quaikhi="vượng" if the_que in qk["vuong"] else ("suy" if the_que in qk["suy"] else "bình"),
        omen_category=_omen_info_preview["category"],
        omen_text=external_omen or "",
        posture_data=_posture_data_for_paradigm,
        intent_label=intent_meta["label"],
    )

    # ── Overall + warnings ──
    warnings: list[str] = []
    overall_parts = []

    # 🌸 LEAD bằng paradigm Tổ sư (KHÔNG phải fortune-telling)
    overall_parts.append("🌸 **ĐỌC ĐỒNG DẠNG** (Vận Pháp Thi — Tổ sư Q3 tr.78):")
    overall_parts.append(f"   {_paradigm['mirror_reading']}")
    overall_parts.append("")
    overall_parts.append("🪞 **QUAN VẬT → TÍNH** (chu trình Q3 tr.69):")
    for trace_line in _paradigm["quan_vat_trace"]:
        overall_parts.append(f"   {trace_line}")
    overall_parts.append("")
    overall_parts.append(f"🎯 **TÂM ANH**: {_paradigm['tam_position']}")
    overall_parts.append("")
    overall_parts.append(f"🌌 **VŨ TRỤ ĐANG NÓI**: {_paradigm['universe_message']}")
    overall_parts.append("")
    overall_parts.append("─" * 60)
    overall_parts.append("📊 Chi tiết kỹ thuật (cho engine + sage reference):")
    overall_parts.append("")
    # Giữ technical detail cũ — vẫn cần cho sage và UI legacy
    overall_parts.append(f"⚡ Tương tác Thể-Dụng: **{auspice.upper()}** — {explain}.")

    if the_qk == "vượng":
        overall_parts.append(f"Thể ({the_que}) đang VƯỢNG trong mùa {qk['season']} → mạnh.")
    elif the_qk == "suy":
        overall_parts.append(f"Thể ({the_que}) đang SUY trong mùa {qk['season']} → yếu.")
        warnings.append("Thể yếu — cần cẩn trọng hơn dù phân tích sinh khắc là cát.")

    # Xét biến quái
    bien_upper_h = QUAI_NGU_HANH[cast.bien_quai.upper_que]
    bien_lower_h = QUAI_NGU_HANH[cast.bien_quai.lower_que]
    bien_h = bien_upper_h if dung_is_upper else bien_lower_h
    # Nếu biến tạo quan hệ tốt hơn với Thể → kết tốt
    if NGU_HANH_SINH.get(bien_h) == the_h:
        overall_parts.append(f"Quẻ Biến sinh Thể ({bien_h}→{the_h}) → kết cục có cứu.")
    elif NGU_HANH_KHAC.get(bien_h) == the_h:
        overall_parts.append(f"Quẻ Biến khắc Thể ({bien_h}→{the_h}) → kết xấu thêm.")
        warnings.append("Biến quái khắc Thể — kết cục có thể nghiêm trọng hơn.")

    # ── Xét hỗ quái + Đằng vũ (cấu kết hành) ──
    ho_upper_h = QUAI_NGU_HANH[cast.ho_quai.upper_que]
    ho_lower_h = QUAI_NGU_HANH[cast.ho_quai.lower_que]
    bien_upper_h_full = QUAI_NGU_HANH[cast.bien_quai.upper_que]
    bien_lower_h_full = QUAI_NGU_HANH[cast.bien_quai.lower_que]

    # Đằng vũ — đếm số hành trùng với Thể/Dụng trong bộ Hỗ + Biến
    extra_hanhs = [ho_upper_h, ho_lower_h, bien_upper_h_full, bien_lower_h_full]
    the_dang_vu = sum(1 for h in extra_hanhs if h == the_h)
    dung_dang_vu = sum(1 for h in extra_hanhs if h == dung_h)

    if the_dang_vu >= 2:
        overall_parts.append(f"Đằng vũ: {the_dang_vu} quẻ ngoài cùng hành Thể → Thể thế lực MẠNH.")
    if dung_dang_vu >= 2:
        overall_parts.append(f"Đằng vũ: {dung_dang_vu} quẻ ngoài cùng hành Dụng → Thể thế YẾU.")
        warnings.append("Đằng vũ Dụng quá nhiều → bao vây Thể.")

    ho_khac_the = [h for h in (ho_upper_h, ho_lower_h)
                   if NGU_HANH_KHAC.get(h) == the_h]
    if ho_khac_the and auspice == "hung":
        warnings.append(f"Hỗ quái cũng có {len(ho_khac_the)} hành khắc Thể — bất lợi nhiều phía.")

    # ── Specific outcomes 8 quẻ Sinh/Khắc Thể ──
    sinh_the_outcomes = []
    khac_the_outcomes = []
    # Duyệt toàn bộ 6 quẻ trong bộ chiêm (Chính trên/dưới, Hỗ trên/dưới, Biến trên/dưới)
    all_quai = [
        cast.chinh_quai.upper_que, cast.chinh_quai.lower_que,
        cast.ho_quai.upper_que, cast.ho_quai.lower_que,
        cast.bien_quai.upper_que, cast.bien_quai.lower_que,
    ]
    seen_sinh = set()
    seen_khac = set()
    for q in all_quai:
        if q == the_que:
            continue
        qh = QUAI_NGU_HANH[q]
        if NGU_HANH_SINH.get(qh) == the_h and q not in seen_sinh:
            sinh_the_outcomes.append(f"{q} sinh Thể → {QUE_SINH_THE_OUTCOMES[q]}")
            seen_sinh.add(q)
        elif NGU_HANH_KHAC.get(qh) == the_h and q not in seen_khac:
            khac_the_outcomes.append(f"{q} khắc Thể → {QUE_KHAC_THE_OUTCOMES[q]}")
            seen_khac.add(q)

    # ⭐⭐ CẢI TIẾN #1 + #2 — Compute trước khi return
    _three_phase = compute_ung_ky_three_phases(cast, the_h)
    _ho_split = compute_ho_the_dung(cast, the_pos, the_h)

    # Append vào overall: cảnh báo nếu Hỗ-Thể khắc Thể (giữa kỳ có lực ép)
    if _ho_split["ho_the_relationship"] == "khắc Thể":
        warnings.append(
            f"Hỗ-của-Thể khắc Thể — giữa kỳ có lực ép quan trọng "
            f"(tượng {_ho_split['ho_the_que']})"
        )

    overall_parts.append("")
    overall_parts.append("📅 ỨNG KỲ THEO TRÌNH TỰ (Mai Hoa TR.133 + TR.235):")
    overall_parts.append(f"  {_three_phase[0]}")
    overall_parts.append(f"  {_three_phase[1]}")
    overall_parts.append(f"  {_three_phase[2]}")
    if _ho_split["ho_the_meaning"]:
        overall_parts.append("")
        overall_parts.append(f"🎯 {_ho_split['ho_the_meaning']}")

    # ⭐⭐⭐ Gap 2 (BƯỚC 3 — Khắc Ứng / Ngoại ứng) — Q3 tr.112-114
    omen_info = classify_omen(external_omen or "")
    if omen_info["category"] != "none":
        overall_parts.append("")
        overall_parts.append(f"🔮 BƯỚC 3 — NGOẠI ỨNG: {omen_info['note']}")
        if omen_info["category"] == "cát":
            overall_parts.append(
                f"   → Ngoại ứng CÁT củng cố phán đoán. "
                f"Nếu Quẻ cát + Khắc ứng cát → ĐẠI CÁT ĐẠI LỢI."
            )
            if auspice == "hung":
                overall_parts.append(
                    f"   ⚖️ Quẻ HUNG nhưng Ngoại ứng CÁT → có cứu. "
                    f"Theo nguyên tắc 'Quẻ chủ, Khắc ứng thứ' (tr.114): vẫn lấy quẻ làm chính."
                )
        elif omen_info["category"] == "hung":
            warnings.append(
                f"Ngoại ứng HUNG ({', '.join(omen_info['matched_keywords'][:2])}) — "
                f"cần cẩn trọng thêm."
            )
            if auspice == "cát":
                overall_parts.append(
                    f"   ⚖️ Quẻ CÁT nhưng Ngoại ứng HUNG → bớt thuận. "
                    f"Vẫn theo 'Quẻ chủ' nhưng đề phòng."
                )

    # ⭐⭐⭐ Gap 3 (BƯỚC 4 — Tư thế thân thể) — Q3 tr.114
    posture_data = POSTURE_TIMING.get(posture.lower() if posture else "", None)
    if posture_data:
        overall_parts.append("")
        overall_parts.append(
            f"🏃 BƯỚC 4 — TƯ THẾ THÂN THỂ: Anh đang **{posture_data['label']}** "
            f"khi khởi quẻ → việc thành công **{posture_data['speed']}**."
        )
        overall_parts.append(f"   {posture_data['note']}")
    else:
        overall_parts.append("")
        overall_parts.append(
            f"⚪ BƯỚC 4 — TƯ THẾ THÂN THỂ: chưa cung cấp. "
            f"Anh có thể thêm `posture=` để hoàn thiện phân tích "
            f"(ngồi/đi/chạy/nằm → tốc độ thành công)."
        )

    # Flag four steps complete
    four_steps_complete = bool(external_omen and posture)

    if cast.ho_warning:
        overall_parts.append("")
        overall_parts.append(f"⚠️ {cast.ho_warning}")

    overall_parts.append("")
    overall_parts.append(
        "🪷 Mai Hoa = ĐỌC ĐỒNG DẠNG, KHÔNG phải predict outcome. "
        "Output trên là **đối thoại với Tổ sư** — không phải verdict cát/hung. "
        "Anh là người ra quyết định cuối — vũ trụ chỉ nói, Anh chọn phản hồi."
    )

    return InterpretationResult(
        cast=cast,
        cast_summary=(
            f"Chính {cast.chinh_quai.name} | "
            f"Biến {cast.bien_quai.name} (hào {moving}) | "
            f"Hỗ {cast.ho_quai.name}"
        ),
        chu_dich_hint=(
            f"Lời quẻ Chu Dịch cho '{cast.chinh_quai.name}' — chưa link Kinh Dịch. "
            f"Anh có thể tham khảo bản Ngô Tất Tố trong thư viện."
        ),
        the_dung=the_dung,
        quai_khi=qk,
        the_quaikhi=the_qk,
        chinh_tuong=chinh_tuong,
        bien_tuong=bien_tuong,
        ho_tuong=ho_tuong,
        overall="\n".join(overall_parts),
        warnings=warnings,
        intent=intent,
        intent_label=intent_meta["label"],
        intent_mapping=f"Thể = {intent_meta['the']} | Dụng = {intent_meta['dung']}",
        intent_extra=intent_meta.get("extra", ""),
        the_dang_vu_count=the_dang_vu,
        dung_dang_vu_count=dung_dang_vu,
        sinh_the_outcomes=sinh_the_outcomes,
        khac_the_outcomes=khac_the_outcomes,
        chinh_hexagram=hex_lookup(cast.chinh_quai.upper_que, cast.chinh_quai.lower_que) or {},
        bien_hexagram=hex_lookup(cast.bien_quai.upper_que, cast.bien_quai.lower_que) or {},
        ho_hexagram=hex_lookup(cast.ho_quai.upper_que, cast.ho_quai.lower_que) or {},
        moving_haotu=hao_lookup(
            hex_lookup(cast.chinh_quai.upper_que, cast.chinh_quai.lower_que).get("number", 0) if hex_lookup(cast.chinh_quai.upper_que, cast.chinh_quai.lower_que) else 0,
            moving,
        ),
        # ⭐ Trùng Phùng (Thầy chỉ đạo A6)
        trung_phung_chinh=(cast.chinh_quai.upper_que == cast.chinh_quai.lower_que),
        trung_phung_bien=(cast.bien_quai.upper_que == cast.bien_quai.lower_que),
        trung_phung_meaning=(
            TRUNG_PHUNG_MEANINGS.get(cast.chinh_quai.upper_que, "")
            if cast.chinh_quai.upper_que == cast.chinh_quai.lower_que
            else (
                TRUNG_PHUNG_MEANINGS.get(cast.bien_quai.upper_que, "") + " (ở Biến)"
                if cast.bien_quai.upper_que == cast.bien_quai.lower_que
                else ""
            )
        ),
        # ⭐ Bệnh tật — bảng thuốc (Thầy chỉ đạo B4)
        benh_tat_thuoc=(
            "; ".join(
                BENH_TAT_THUOC_MAP.get(q, "")
                for q in {
                    cast.chinh_quai.upper_que, cast.chinh_quai.lower_que,
                    cast.ho_quai.upper_que, cast.ho_quai.lower_que,
                    cast.bien_quai.upper_que, cast.bien_quai.lower_que,
                }
                if BENH_TAT_THUOC_MAP.get(q) and
                NGU_HANH_SINH.get(QUAI_NGU_HANH[q]) == the_h
            )
            if intent == "benh_tat" else ""
        ),
        # ⭐⭐ CẢI TIẾN #1 — Ứng kỳ 3 giai đoạn
        ung_ky_dau=_three_phase[0],
        ung_ky_giua=_three_phase[1],
        ung_ky_cuoi=_three_phase[2],
        # ⭐⭐ CẢI TIẾN #2 — Hỗ-Thể vs Hỗ-Dụng
        ho_the_que=_ho_split["ho_the_que"],
        ho_dung_que=_ho_split["ho_dung_que"],
        ho_the_hanh=_ho_split["ho_the_hanh"],
        ho_the_relationship=_ho_split["ho_the_relationship"],
        ho_the_meaning=_ho_split["ho_the_meaning"],
        # ⭐⭐⭐ Gap 2 — Ngoại ứng (BƯỚC 3)
        external_omen_input=external_omen or "",
        external_omen_category=omen_info["category"],
        external_omen_weight=omen_info["weight"],
        external_omen_note=omen_info["note"],
        external_omen_source=classify_omen_thap_ung(external_omen or "")["omen_source"],
        external_omen_thap_ung=classify_omen_thap_ung(external_omen or "")["thap_ung_label"],
        # ⭐⭐⭐ Gap 3 — Tư thế thân thể (BƯỚC 4)
        posture_input=(posture or "").lower(),
        posture_speed=posture_data["speed"] if posture_data else "",
        posture_note=posture_data["note"] if posture_data else "",
        # Flags
        four_steps_complete=four_steps_complete,
        ho_warning=cast.ho_warning,
        # ⭐⭐⭐ Paradigm shift fields
        paradigm_mirror_reading=_paradigm["mirror_reading"],
        paradigm_quan_vat_trace=_paradigm["quan_vat_trace"],
        paradigm_tam_position=_paradigm["tam_position"],
        paradigm_universe_message=_paradigm["universe_message"],
    )


def demo():
    """Demo với Prediction #1 — chuyến công tác."""
    from engine.yi_wiki.cast import cast_by_time
    cast = cast_by_time("Ngọ", 5, 15, "Thân")
    r = analyze(cast, month=5)

    print("═" * 60)
    print("🔍 PHÂN TÍCH 5 BƯỚC THIỆU KHANG TIẾT")
    print("═" * 60)
    print(f"\n📜 Quẻ: {r.cast_summary}")
    print(f"\n📖 Bước 2 — Lời Chu Dịch:")
    print(f"  {r.chu_dich_hint}")

    td = r.the_dung
    print(f"\n⚡ Bước 3 — Thể-Dụng:")
    print(f"  THỂ: {td.the_que} ({td.the_hanh}) — ở {td.the_position}")
    print(f"  DỤNG: {td.dung_que} ({td.dung_hanh})")
    print(f"  → {td.explanation}")
    print(f"  → {td.detail}")

    print(f"\n🌤 Bước 4 — Quái Khí mùa {r.quai_khi['season']}:")
    print(f"  Thể {td.the_que} = {r.the_quaikhi.upper()}")

    print(f"\n🎴 Tượng:")
    print(f"  Chính: {r.chinh_tuong}")
    print(f"  Biến:  {r.bien_tuong}")
    print(f"  Hỗ:   {r.ho_tuong}")

    print(f"\n💎 Phán đoán tổng quan:")
    print(r.overall)

    if r.warnings:
        print(f"\n⚠️ Cảnh báo:")
        for w in r.warnings:
            print(f"  • {w}")


if __name__ == "__main__":
    demo()
