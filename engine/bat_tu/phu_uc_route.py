"""Phù-Ức Routing — 8 path Trợ vs Sinh theo Trích Thiên Tủy.

Anh duyệt 2026-06-02 paradigm "Ấn Tỷ ánh sáng": mỗi keyword Bát Tự phải
sáng tỏ qua (định nghĩa + trích sách + diễn giải case + hành động cụ thể).

Engine này route lá số đến 1 trong 8 path dựa trên 2 trục:
- Day Master strength: VƯỢNG / NHƯỢC / TRUNG HÒA
- Áp lực dominant trong 4 trụ: Tài / Quan-Sát / Thực-Thương / Ấn-Kiêu

Mỗi path return:
- dung_than (chính): thần nên dùng
- ky_than: thần phải tránh
- ly_do_sach: lý do paradigm cổ
- trich_dan: nguyên văn trích
- hanh_dong: gợi ý hành động cụ thể (không predict)
- sach_nguon: 3 sách đối chiếu (TTT + Thiệu Vĩ Hoa + Tử Bình)

⚠️ Iron Rule #4+6: KHÔNG predict tĩnh. Engine ra hỉ-kỵ thần,
diễn giải dạng đồng dạng-học (mirror, không fortune).

Sources verified trong corpus YI-Chronos:
- trich-thien-tuy-binh-chu-nham-thiet-tieu/content.md (dòng 1676, 1682, 1683)
- du-doan-tu-tru-thieu-vy-hoa/content.md (chương Lục Thân + Hỉ Kỵ)
- du-bao-theo-tu-binh/content.md (chương Vượng-Suy + Dụng Thần)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── Element mapping Hán-Việt ────────────────────────────────────────────────

STEM_ELEMENT: dict[str, str] = {
    "Giáp": "mộc", "Ất": "mộc",
    "Bính": "hỏa", "Đinh": "hỏa",
    "Mậu": "thổ", "Kỷ": "thổ",
    "Canh": "kim", "Tân": "kim",
    "Nhâm": "thủy", "Quý": "thủy",
}

# 10 Thần ↔ Element relation
# Day Master element vs thần element:
ELEMENT_RELATION: dict[str, dict[str, str]] = {
    # khi DM = mộc: Ấn=thủy, Tỷ=mộc, Thực Thương=hỏa, Tài=thổ, Quan Sát=kim
    "mộc": {"ấn": "thủy", "tỷ": "mộc", "thực_thương": "hỏa", "tài": "thổ", "quan_sát": "kim"},
    "hỏa": {"ấn": "mộc", "tỷ": "hỏa", "thực_thương": "thổ", "tài": "kim", "quan_sát": "thủy"},
    "thổ": {"ấn": "hỏa", "tỷ": "thổ", "thực_thương": "kim", "tài": "thủy", "quan_sát": "mộc"},
    "kim": {"ấn": "thổ", "tỷ": "kim", "thực_thương": "thủy", "tài": "mộc", "quan_sát": "hỏa"},
    "thủy": {"ấn": "kim", "tỷ": "thủy", "thực_thương": "mộc", "tài": "hỏa", "quan_sát": "thổ"},
}


@dataclass
class PhuUcResult:
    """Kết quả routing Phù-Ức."""

    day_master_stem: str
    day_master_element: str
    strength_tag: str            # "vượng" / "nhược" / "trung_hòa"
    pressure_dominant: str       # "tài" / "quan_sát" / "thực_thương" / "ấn" / "tỷ" / "cân_bằng"
    path_id: str                 # vd "NHƯỢC_TÀI_KHẮC_ẤN"
    dung_than: list[str]         # vd ["Tỷ Kiếp", "Ấn"]
    dung_than_elements: list[str]  # vd ["mộc", "thủy"]
    ky_than: list[str]           # vd ["Tài", "Quan Sát"]
    ky_than_elements: list[str]
    ly_do_sach: str              # paradigm explanation
    trich_dan: list[dict]        # [{sach, dong, noi_dung}]
    hanh_dong: list[str]         # gợi ý concrete
    sach_nguon: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ─── 8 PATHS theo Trích Thiên Tủy ────────────────────────────────────────────

PATH_NHUOC_TAI_KHAC_AN = {
    "path_id": "NHƯỢC_TÀI_TRÙNG_ĐIỆP_ẤN_BỊ_KHẮC",
    "condition": "Day Master nhược + Tài tinh trùng điệp + Ấn bị khắc",
    "dung_than": ["Tỷ Kiên", "Kiếp Tài"],
    "ky_than": ["Tài"],
    "ly_do_sach": (
        "Trích Thiên Tủy TH1: Ấn đã bị Tài khắc thành vô dụng → không thể dựa Ấn sinh thân. "
        "Phải dùng Tỷ Kiếp trợ thân + khắc Tài đoạt lại tài lực mới cát."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 1682,
            "noi_dung": (
                "Trường hợp 1: Nhật Chủ suy nhược, trong trụ Tài Tinh trùng điệp, "
                "Ấn Thụ bị khắc nên không có gốc để sinh Nhật Chủ. "
                "Dụng Tỷ Kiếp trợ Nhật Chủ thì cát, dụng Ấn sinh Nhật Chủ tất hung vậy."
            ),
        },
        {
            "sach": "Dự báo theo Tử Bình",
            "dong": None,
            "noi_dung": (
                "Nếu can ngày nhược mà gặp được Tỷ Kiên sẽ được trợ giúp thân; "
                "Tài, Quan nhiều nhờ Tỷ Kiên giúp cho thân khỏi mất của."
            ),
        },
    ],
    "hanh_dong": [
        "Tìm 1-3 đồng đạo / đồng nghiệp cùng tần số (Tỷ Kiếp ngang vai)",
        "Hợp tác — KHÔNG solo, KHÔNG ôm hết việc",
        "Tránh đu trend làm giàu nhanh (Tài Thổ càng khắc Ấn → đứt mạch học)",
        "Tránh mở rộng quy mô vội vàng",
    ],
}

PATH_NHUOC_QUAN_VUONG = {
    "path_id": "NHƯỢC_QUAN_SÁT_VƯỢNG",
    "condition": "Day Master nhược + Quan Sát thừa vượng",
    "dung_than": ["Chính Ấn", "Thiên Ấn"],
    "ky_than": ["Quan Sát"],
    "ly_do_sach": (
        "Trích Thiên Tủy TH2: Quan Sát mạnh khắc thân trực tiếp. "
        "Tỷ Kiếp trợ thân sẽ phản khắc vô tình (cùng hành chống lại). "
        "Phải dùng Ấn — Ấn hóa Quan Sát thành dinh dưỡng nuôi thân."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 1683,
            "noi_dung": (
                "Trường hợp 2: Nhật Chủ suy yếu, trong trụ Quan Sát thừa vượng. "
                "Tỷ Kiếp trợ Nhật Chủ sẽ gây phản khắc vô tình; "
                "không bằng Ấn Thụ hóa Quan Sát sinh Nhật Chủ."
            ),
        },
        {
            "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
            "dong": None,
            "noi_dung": (
                "Nhật Can yếu mà Quan Sát mạnh thì Ấn Tinh làm xì hơi Quan Sát "
                "và sinh thân. Chính Ấn nói chung là cát thần."
            ),
        },
        {
            "sach": "Dự báo theo Tử Bình",
            "dong": None,
            "noi_dung": "Nếu thân nhược sát vượng thì phải dựa vào Ấn để hóa giải.",
        },
    ],
    "hanh_dong": [
        "Học vấn — đọc kinh điển, dưỡng nội lực (Chính Ấn ưu tiên hơn Kiêu Thần)",
        "Tìm thầy / cố vấn có Ấn dưỡng (người sinh hành Ấn của Day Master)",
        "Tránh nhận trách nhiệm vượt năng lực (Quan Sát thêm)",
        "Tránh đối đầu trực diện với người quyền lực",
    ],
}

PATH_NHUOC_THUC_THUONG_TIET = {
    "path_id": "NHƯỢC_THỰC_THƯƠNG_TIẾT_NHIỀU",
    "condition": "Day Master nhược + Thực Thương tiết khí nhiều",
    "dung_than": ["Chính Ấn"],
    "ky_than": ["Thực Thương"],
    "ly_do_sach": (
        "Thiệu Vĩ Hoa: Nhật Can yếu mà Thực Thương mạnh → Ấn Tinh chống lại Thực Thương "
        "(Ấn khắc Thực Thương) + sinh thân. Hai công dụng cùng lúc."
    ),
    "trich_dan": [
        {
            "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
            "dong": None,
            "noi_dung": (
                "Nhật Can yếu mà thực thương mạnh thì Chính Ấn chống lại thương, thực. "
                "Chính Ấn nói chung là cát thần."
            ),
        },
    ],
    "hanh_dong": [
        "Bớt show off / sáng tạo phóng tay (Thực Thương)",
        "Nghỉ ngơi, thu khí (Ấn)",
        "Học cổ điển — không sáng tạo mới khi chưa nạp đủ",
    ],
}

PATH_NHUOC_TAI_NHIEU_AN_MANH = {
    "path_id": "NHƯỢC_TÀI_NHIỀU_NHƯNG_ẤN_CÒN_GỐC",
    "condition": "Day Master nhược + Tài nhiều + Ấn vẫn có gốc (không bị khắc tuyệt)",
    "dung_than": ["Tỷ Kiên", "Kiếp Tài"],
    "ky_than": ["Tài"],
    "ly_do_sach": (
        "Trích Thiên Tủy: Khi Tài còn áp lực nhưng Ấn chưa tuyệt, vẫn ưu tiên "
        "Tỷ Kiếp khắc Tài để cứu Ấn. Ấn cần được bảo vệ trước, chứ không phải lao thẳng vào."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 1676,
            "noi_dung": (
                "Trợ thì dùng Tỷ Kiếp, sinh thì dùng Ấn Thụ. Điều là suy mà có khi "
                "trợ lại hung, sinh thì được cát; cho nên trợ hay sinh cũng nên "
                "phân biệt tỏ tường để dụng."
            ),
        },
    ],
    "hanh_dong": [
        "Đồng đạo > tự gồng",
        "Giữ Ấn (học vấn / mentor) khỏi bị 'tiền bạc' kéo đi",
    ],
}

PATH_VUONG_TAI_QUAN_LO = {
    "path_id": "VƯỢNG_GẶP_TÀI_QUAN_LỘ",
    "condition": "Day Master vượng + Tài Quan có khí",
    "dung_than": ["Chính Tài", "Chính Quan"],
    "ky_than": ["Tỷ Kiếp", "Ấn"],
    "ly_do_sach": (
        "Trích Thiên Tủy: Nhật Chủ vượng + có Tài + có Quan = lấy Tài Quan làm dụng. "
        "Thân vượng cần Tài Quan tiết khí ra ngoài + tạo thành tựu, đừng thêm Tỷ Ấn."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 1678,
            "noi_dung": (
                "Nhật Chủ vượng tướng, trong trụ tải Quan vô khí suy nhược, tiết hóa "
                "tất Quan Tinh sẽ bị thương tổn, nên dụng khắc chế thì có lợi, "
                "dụng tiết hóa thì có hại (tức là lấy Tài làm dụng thì cát còn lấy "
                "Thực Thương làm dụng thì hung)."
            ),
        },
    ],
    "hanh_dong": [
        "Nhận trách nhiệm danh chính (Chính Quan)",
        "Mở rộng kinh doanh / tài chính (Chính Tài)",
        "Tránh tụ tập anh em quá nhiều (Tỷ Kiếp đoạt Tài)",
    ],
}

PATH_VUONG_TY_KIEP_NHIEU = {
    "path_id": "VƯỢNG_TỶ_KIẾP_TRÙNG_ĐIỆP",
    "condition": "Day Master vượng + Tỷ Kiếp trùng điệp + không có Tài",
    "dung_than": ["Thực Thần", "Thương Quan"],
    "ky_than": ["Tài (vì sẽ bị Tỷ Kiếp đoạt)", "Quan Sát (vô lực)"],
    "ly_do_sach": (
        "Trích Thiên Tủy: Cục toàn Tỷ Kiếp, không có Tài để khắc → dụng khắc chế "
        "tất có hại; phải tiết hóa thuận theo khí thế (Thực Thương) mới lợi."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 1680,
            "noi_dung": (
                "Nhật Chủ vượng tướng, trụ không có tải Quan, cục toàn Tỷ Kiếp, "
                "dụng khắc chế tất có hại, dụng tiết hóa thuận theo khí thế lại có lợi "
                "(tức là lấy Tài làm dụng thì hung còn lấy Thực Thương làm dụng thì cát)."
            ),
        },
    ],
    "hanh_dong": [
        "Phát tiết qua sáng tạo / nghệ thuật / dạy học (Thực Thương)",
        "Tránh ép kiếm tiền — Tỷ Kiếp đoạt Tài",
    ],
}

PATH_VUONG_AN_DANG_TIET = {
    "path_id": "VƯỢNG_ẤN_QUÁ_NHIỀU",
    "condition": "Day Master vượng + Ấn trùng điệp (Mộc nhiều Thủy)",
    "dung_than": ["Chính Tài"],
    "ky_than": ["Ấn"],
    "ly_do_sach": (
        "Ấn quá nhiều thân càng vượng + bị 'mẹ ôm con quá chặt' (mẫu từ mẹt tử). "
        "Phải dùng Tài để chế Ấn — Tài khắc Ấn cắt bớt sinh khí dư thừa."
    ),
    "trich_dan": [
        {
            "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
            "dong": None,
            "noi_dung": (
                "Nhật Can vượng và Chính Ấn vượng thì Chính Tài làm hỏng Chính Ấn "
                "(phá Ấn bớt sinh khí dư thừa)."
            ),
        },
    ],
    "hanh_dong": [
        "Bớt học lý thuyết — bước ra ứng dụng thực tế (Tài)",
        "Tránh nuông chiều bản thân quá đà",
    ],
}

PATH_TRUNG_HOA = {
    "path_id": "TRUNG_HÒA_LƯU_THÔNG",
    "condition": "Day Master cân bằng + ngũ hành lưu thông",
    "dung_than": ["thần nào lưu thông khí thế"],
    "ky_than": ["thần nào nghẹt mạch"],
    "ly_do_sach": (
        "Trích Thiên Tủy: Cục cân bằng → tìm thần lưu thông sinh hóa, "
        "khởi từ Tỷ Kiếp kết thúc ở Tài Quan, hoặc ngược lại."
    ),
    "trich_dan": [
        {
            "sach": "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "dong": 2560,
            "noi_dung": (
                "Nguyên lưu, tức vượng thần trong Tứ Trụ vậy, bất luận Tài, Quan, "
                "Ấn, Thụ, Thực Thương, Tỷ Kiếp, đều có thể là nguyên lưu vậy. "
                "Tổn quát cân lưu thông sinh hóa, đắc cục đắc mỹ thì cát."
            ),
        },
    ],
    "hanh_dong": [
        "Giữ nhịp, không tham một hướng",
        "Quan-vật-trace-tính theo từng giai đoạn",
    ],
}


ALL_PATHS = [
    PATH_NHUOC_TAI_KHAC_AN,
    PATH_NHUOC_QUAN_VUONG,
    PATH_NHUOC_THUC_THUONG_TIET,
    PATH_NHUOC_TAI_NHIEU_AN_MANH,
    PATH_VUONG_TAI_QUAN_LO,
    PATH_VUONG_TY_KIEP_NHIEU,
    PATH_VUONG_AN_DANG_TIET,
    PATH_TRUNG_HOA,
]


def _count_pressure(pillars: dict, day_master_element: str) -> dict:
    """Đếm áp lực 5 nhóm thần trong 4 trụ (loại trừ day pillar stem)."""
    from .constants import BRANCH_ELEMENT

    rel = ELEMENT_RELATION.get(day_master_element, {})
    counts = {"tài": 0, "quan_sát": 0, "thực_thương": 0, "ấn": 0, "tỷ": 0}

    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        # Count stem (skip day stem = self)
        if pos != "day":
            stem = p.get("stem")
            if stem:
                stem_el = STEM_ELEMENT.get(stem)
                for category, el in rel.items():
                    if stem_el == el:
                        counts[category] += 1
                        break
        # Count branch element
        branch = p.get("branch")
        if branch:
            br_el = BRANCH_ELEMENT.get(branch, "").lower()
            for category, el in rel.items():
                if br_el == el:
                    counts[category] += 0.7  # branch weight < stem
                    break
    return counts


def _classify_strength(thong_can_score: float, pressure: dict) -> str:
    """Phân loại Day Master strength dựa trên thông căn + áp lực."""
    # Thông căn score: 0=hư phù, 1-2=yếu, 2-4=có gốc, 4+=vượng
    pho_tro = pressure.get("ấn", 0) + pressure.get("tỷ", 0)
    khac_tiet = (pressure.get("tài", 0) + pressure.get("quan_sát", 0)
                 + pressure.get("thực_thương", 0))

    # Tổng cường độ
    total_strength = thong_can_score + pho_tro * 1.2

    if total_strength < 3.0 or thong_can_score < 1.0:
        return "nhược"
    elif total_strength > 7.0 and pho_tro > khac_tiet:
        return "vượng"
    elif khac_tiet > pho_tro + 2 and thong_can_score < 4.0:
        return "nhược"
    else:
        return "trung_hòa"


def _route_path(strength: str, pressure: dict, thong_can_score: float) -> dict:
    """Route lá số → 1 trong 8 path."""
    if strength == "nhược":
        # Áp lực cao nhất là gì?
        tai = pressure.get("tài", 0)
        quan = pressure.get("quan_sát", 0)
        thuc = pressure.get("thực_thương", 0)

        if quan > 2.0 and quan >= tai:
            return PATH_NHUOC_QUAN_VUONG
        elif tai > 2.0:
            # Tài trùng điệp — kiểm Ấn có còn không
            if pressure.get("ấn", 0) < 1.0:
                return PATH_NHUOC_TAI_KHAC_AN
            else:
                return PATH_NHUOC_TAI_NHIEU_AN_MANH
        elif thuc > 1.5:
            return PATH_NHUOC_THUC_THUONG_TIET
        else:
            return PATH_NHUOC_TAI_KHAC_AN  # default cho nhược
    elif strength == "vượng":
        an = pressure.get("ấn", 0)
        ty = pressure.get("tỷ", 0)
        tai_quan = pressure.get("tài", 0) + pressure.get("quan_sát", 0)

        if an > 2.5:
            return PATH_VUONG_AN_DANG_TIET
        elif ty > 2.5 and tai_quan < 1.5:
            return PATH_VUONG_TY_KIEP_NHIEU
        else:
            return PATH_VUONG_TAI_QUAN_LO
    else:
        return PATH_TRUNG_HOA


def route_phu_uc(tu_tru: dict) -> PhuUcResult:
    """Routing chính — đầu vào tu_tru full → đầu ra PhuUcResult.

    Args:
        tu_tru: output từ engine.bat_tu.cast.extract_tu_tru()
                Cần pillars + day_master info.

    Returns: PhuUcResult với dung/ky thần + trích sách + hành động.
    """
    pillars = tu_tru["pillars"]
    day_master_stem = pillars["day"]["stem"]
    day_master_element = STEM_ELEMENT.get(day_master_stem, "?")

    # 1. Thông căn của Day Master
    from .thong_can import summarize_day_master_thong_can
    tc_summary = summarize_day_master_thong_can(pillars)
    thong_can_score = tc_summary.get("score", 0)

    # 2. Áp lực 5 nhóm
    pressure = _count_pressure(pillars, day_master_element)

    # 3. Strength
    strength = _classify_strength(thong_can_score, pressure)

    # 4. Pressure dominant
    if pressure:
        pressure_dominant = max(pressure, key=pressure.get)
        if pressure[pressure_dominant] < 1.0:
            pressure_dominant = "cân_bằng"
    else:
        pressure_dominant = "cân_bằng"

    # 5. Route
    path = _route_path(strength, pressure, thong_can_score)

    # 6. Resolve dung/ky thần elements (Hán-Việt → element)
    rel = ELEMENT_RELATION.get(day_master_element, {})
    dung_elements = []
    for dt in path["dung_than"]:
        if "Tỷ" in dt or "Kiếp" in dt:
            dung_elements.append(rel.get("tỷ"))
        elif "Ấn" in dt or "Kiêu" in dt:
            dung_elements.append(rel.get("ấn"))
        elif "Tài" in dt:
            dung_elements.append(rel.get("tài"))
        elif "Quan" in dt or "Sát" in dt:
            dung_elements.append(rel.get("quan_sát"))
        elif "Thực" in dt or "Thương" in dt:
            dung_elements.append(rel.get("thực_thương"))

    ky_elements = []
    for kt in path["ky_than"]:
        if "Tỷ" in kt or "Kiếp" in kt:
            ky_elements.append(rel.get("tỷ"))
        elif "Ấn" in kt or "Kiêu" in kt:
            ky_elements.append(rel.get("ấn"))
        elif "Tài" in kt:
            ky_elements.append(rel.get("tài"))
        elif "Quan" in kt or "Sát" in kt:
            ky_elements.append(rel.get("quan_sát"))
        elif "Thực" in kt or "Thương" in kt:
            ky_elements.append(rel.get("thực_thương"))

    return PhuUcResult(
        day_master_stem=day_master_stem,
        day_master_element=day_master_element,
        strength_tag=strength,
        pressure_dominant=pressure_dominant,
        path_id=path["path_id"],
        dung_than=path["dung_than"],
        dung_than_elements=[e for e in dung_elements if e],
        ky_than=path["ky_than"],
        ky_than_elements=[e for e in ky_elements if e],
        ly_do_sach=path["ly_do_sach"],
        trich_dan=path["trich_dan"],
        hanh_dong=path["hanh_dong"],
        sach_nguon=[
            "Trích Thiên Tủy bình chú (Nhậm Thiết Tiều)",
            "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
            "Dự báo theo Tử Bình",
        ],
    )


def render_phu_uc_markdown(result: PhuUcResult) -> str:
    """Render PhuUcResult → markdown đầy đủ ánh sáng."""
    lines = [
        f"## 🔆 Phù-Ức Route — {result.path_id}\n",
        f"**Day Master**: {result.day_master_stem} ({result.day_master_element.title()})  ",
        f"**Cường độ**: **{result.strength_tag.upper()}**  ",
        f"**Áp lực dominant**: {result.pressure_dominant}\n",
        f"### ✅ Dụng Thần (Hỉ — cần dùng)",
        f"- **{' + '.join(result.dung_than)}** (hành: {' + '.join(result.dung_than_elements)})\n",
        f"### ❌ Kỵ Thần (tránh)",
        f"- **{' + '.join(result.ky_than)}** (hành: {' + '.join(result.ky_than_elements)})\n",
        f"### 📚 Lý do theo sách cổ\n",
        f"{result.ly_do_sach}\n",
        f"### 📖 Trích nguyên văn",
    ]
    for td in result.trich_dan:
        dong_str = f" (dòng {td['dong']})" if td.get("dong") else ""
        lines.append(f"\n> _{td['noi_dung']}_  ")
        lines.append(f"> — **{td['sach']}**{dong_str}")

    lines.append("\n### 🎯 Hành động cụ thể (KHÔNG predict — paradigm đồng-dạng)")
    for hd in result.hanh_dong:
        lines.append(f"- {hd}")

    lines.append("\n### 🪷 Iron Rule #4+6")
    lines.append(
        "Engine ra Hỉ-Kỵ thần dựa trên paradigm cổ — KHÔNG dự đoán \"sẽ thành/bại\". "
        "Lá số = phản chiếu cấu trúc khí; hành động là của anh."
    )
    return "\n".join(lines)
