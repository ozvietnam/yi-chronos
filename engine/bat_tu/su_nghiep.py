"""Sự Nghiệp (事業) — career / vocation analysis from Bát Tự chart.

Paradigm (Iron Rule #4+6): Phân tích Sự nghiệp KHÔNG dự đoán "anh sẽ thành công
nghề X" hoặc "đi học ngành Y sẽ giàu". Phân tích đọc **cấu trúc khí của Cách Cục +
Dụng Thần + Thập Thần dominant** → recommend **hành** và **hướng** nghề nghiệp
phù hợp với cấu trúc khí bẩm sinh.

Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (rải rác Q. 4-7 về Cách
Cục → nghề nghiệp, Lục Thân → đồng nghiệp/cấp trên, Dụng Thần → "Bổ" hướng nghiệp).

Algorithm:
1. **Cách Cục** → đặc tính sự nghiệp cốt lõi (đã có essence + favorable từ engine).
2. **Dụng Thần** → bổ hướng nghề (hành nào thuận để hoạt động trong).
3. **Thập Thần dominant**:
   - Quan vượng + có Ấn hộ → công chức / chức vụ chính thống
   - Thực Thương vượng → sáng tạo / nghệ thuật / kinh doanh tự do
   - Tài vượng + Day Master vượng → thương mại / kinh doanh
   - Sát + có chế (Thực Thần) → quân đội / công an / leadership áp lực cao
   - Ấn vượng → học thuật / nghiên cứu / giáo dục
   - Tỉ/Kiếp vượng → khởi nghiệp + đối tác / lao động độc lập
4. **Recommend** top 5 ngành nghề từ Dụng + Hỷ Thần.
5. **Cảnh báo** ngành nên tránh (theo Kỵ Thần).
6. **Thời điểm phát triển**: Đại Vận đi vào Dụng/Hỷ Thần.
"""

from __future__ import annotations

from .constants import BRANCH_ELEMENT, STEM_ELEMENT


# ─── Reference tables ────────────────────────────────────────────────────────

# Cách Cục → 3 hướng nghề top recommend (compose từ CACH_DETAILS + Chương 2 sách)
CACH_CUC_TO_NGHE: dict[str, dict] = {
    "Chính Quan cách (正官格)": {
        "career_style": "công chức / chức vụ chính thống / quản lý",
        "industries": [
            "Cơ quan nhà nước / công chức",
            "Quản lý / lãnh đạo cấp trung-cao",
            "Pháp luật / kỷ luật / hành chính",
            "Tổ chức phi lợi nhuận có khuôn khổ",
        ],
        "narrative": (
            "Chính Quan cách → cấu trúc khí hợp với CHỨC TƯỚC CHÍNH THỐNG, "
            "danh tiếng + kỷ luật. Cần Ấn bảo hộ thì dễ thăng tiến."
        ),
    },
    "Thất Sát cách (七殺格)": {
        "career_style": "quyền lực + áp lực cao / leadership / chế đối thủ",
        "industries": [
            "Quân đội / công an / an ninh",
            "Kinh doanh mạo hiểm / khởi nghiệp đột phá",
            "Lãnh đạo + ra quyết định trong môi trường cạnh tranh",
            "Quản lý khủng hoảng / điều phối + kỷ luật",
            "Phẫu thuật / nha khoa / nghề cần dũng cảm",
        ],
        "narrative": (
            "Thất Sát cách → áp lực + quyền lực dữ dội. CẦN Thực Thần CHẾ Sát "
            "hoặc Ấn HÓA Sát → biến áp lực thành sức mạnh. Không chế hóa → tai họa."
        ),
    },
    "Chính Tài cách (正財格)": {
        "career_style": "tài chính ổn định / kinh doanh truyền thống / quản lý tài chính",
        "industries": [
            "Tài chính / kế toán / ngân hàng",
            "Kinh doanh truyền thống dài hạn",
            "Bất động sản (cho thuê / quản lý)",
            "Lương cứng + chức vụ ổn định",
            "Quản lý vốn + tích lũy",
        ],
        "narrative": (
            "Chính Tài cách → tài lộc ỔN ĐỊNH. Day Master vượng + Tài vượng → đại phú. "
            "Cần Thực Thương sinh Tài. Kỵ Kiếp Tài cướp đoạt."
        ),
    },
    "Thiên Tài cách (偏財格)": {
        "career_style": "kinh doanh đa lĩnh vực / đầu cơ / môi giới / tài lộc bất ngờ",
        "industries": [
            "Kinh doanh đa lĩnh vực / startup",
            "Đầu cơ / chứng khoán / forex",
            "Môi giới / brokerage / agency",
            "Truyền thông / marketing có sức hút",
            "Du lịch + xuất nhập khẩu",
        ],
        "narrative": (
            "Thiên Tài cách → tài lộc BẤT NGỜ + sức hút + đào hoa. "
            "Hợp khởi nghiệp đa lĩnh vực. Kỵ Tỉ Kiếp cướp Tài."
        ),
    },
    "Thực Thần cách (食神格)": {
        "career_style": "sáng tạo + hưởng thụ / nghệ thuật / ẩm thực / giáo dục",
        "industries": [
            "Nghệ thuật / âm nhạc / điện ảnh / thiết kế",
            "Ẩm thực / nhà hàng / nấu ăn / thực phẩm",
            "Giáo dục / huấn luyện / coaching",
            "Sáng tạo nội dung / viết / xuất bản",
            "Y tế thư giãn / spa / chăm sóc sức khỏe",
        ],
        "narrative": (
            "Thực Thần cách → sao SÁNG TẠO + ăn lộc. Hợp ngành liên quan đến "
            "sáng tạo + hưởng thụ. Kỵ Kiêu Thần (Thiên Ấn) đoạt Thực Thần."
        ),
    },
    "Thương Quan cách (傷官格)": {
        "career_style": "tài năng phá cách / nghệ sĩ độc đáo / khởi nghiệp đột phá",
        "industries": [
            "Nghệ thuật độc đáo / avant-garde",
            "Startup tech / breakthrough innovation",
            "Truyền thông / báo chí / ngôn ngữ tài",
            "Tư vấn / công nghệ / AI / khoa học",
            "Diễn xuất / biểu diễn / influencer",
        ],
        "narrative": (
            "Thương Quan cách → tài năng VƯỢT KHUÔN KHỔ. Cần Chính Ấn để "
            "'Thương Quan phối Ấn' → tài năng có khuôn. "
            "Kỵ 'Thương Quan kiến Quan' khi Day Master nhược → đại hung."
        ),
    },
    "Chính Ấn cách (正印格)": {
        "career_style": "học thuật / nghiên cứu / giáo dục / từ thiện",
        "industries": [
            "Giáo dục / giảng dạy / huấn luyện",
            "Học thuật / nghiên cứu / khoa học",
            "Từ thiện / NGO / công tác xã hội",
            "Tâm lý / tư vấn / chữa lành",
            "Văn hóa / lịch sử / bảo tàng / thư viện",
        ],
        "narrative": (
            "Chính Ấn cách → sao MẸ + học vấn + bảo hộ. Hợp ngành học thuật, "
            "từ thiện. Kỵ Chính Tài đoạt Ấn. Quá nhiều Ấn → ỷ lại, lười hành động."
        ),
    },
    "Thiên Ấn cách (偏印格)": {
        "career_style": "trí tuệ phi truyền thống / nghiên cứu lập dị / công nghệ",
        "industries": [
            "Thiền / tôn giáo / tâm linh / chiêm tinh",
            "Nghiên cứu lập dị / khoa học cận biên",
            "Công nghệ / lập trình / AI / data science",
            "Tâm lý chuyên sâu / phân tâm học",
            "Phong thủy / chiêm bốc / mệnh lý (như YI-Chronos)",
        ],
        "narrative": (
            "Thiên Ấn (Kiêu Thần) → trí tuệ PHI TRUYỀN THỐNG, quý nhân ngầm. "
            "Hợp lĩnh vực sâu, ít người làm. Kỵ Thiên Ấn đoạt Thực Thần."
        ),
    },
    "Kiến Lộc cách (建祿格) — đặc biệt": {
        "career_style": "tự lập + lao động độc lập / chuyên môn cao",
        "industries": [
            "Freelance / chuyên gia độc lập",
            "Lao động thủ công có chuyên môn cao",
            "Tự kinh doanh quy mô nhỏ + bền vững",
            "Tư vấn cá nhân / cố vấn",
        ],
        "narrative": (
            "Kiến Lộc → Day Master đắc lệnh tại Trụ Tháng. Tự lập, có sức + chuyên môn. "
            "Cần Tài hoặc Quan để hóa khí — không thì cô đơn vô dụng."
        ),
    },
    "Dương Nhận cách (羊刃格) — đặc biệt": {
        "career_style": "tướng quân + nghề mạo hiểm / áp lực cao",
        "industries": [
            "Tướng quân / leadership chiến đấu",
            "Phẫu thuật / cấp cứu",
            "Kinh doanh mạo hiểm cao",
            "Thể thao + sức mạnh",
            "An ninh / bảo vệ / điều tra",
        ],
        "narrative": (
            "Dương Nhận = Kiếp Tài cực vượng — sao quyền + tai nạn. "
            "Hợp tướng quân / mạo hiểm / phẫu thuật. "
            "Sợ Thất Sát phối Nhận (羊刃逢沖) → tai nạn lớn."
        ),
    },
}

# Element → 5 ngành nghề specific (more detailed than ELEMENT_BO_HUONG in luan_giai)
ELEMENT_TO_DETAILED_NGHE: dict[str, list[dict]] = {
    "mộc": [
        {"category": "Trồng trọt / lâm nghiệp", "examples": "Nông nghiệp hữu cơ, trồng cây/hoa, lâm nghiệp"},
        {"category": "Giấy + sản phẩm gỗ", "examples": "Xuất bản, in ấn, đồ gỗ, thủ công mỹ nghệ"},
        {"category": "Giáo dục + đào tạo", "examples": "Giáo viên, huấn luyện, coaching, sách"},
        {"category": "Y học + dược thảo", "examples": "Đông y, herbal, thực phẩm chức năng"},
        {"category": "Văn hóa + nghệ thuật mềm", "examples": "Văn học, nhiếp ảnh, thiết kế xanh"},
    ],
    "hỏa": [
        {"category": "Chiếu sáng + năng lượng", "examples": "Điện, quang học, năng lượng mặt trời"},
        {"category": "Ẩm thực + thực phẩm nóng", "examples": "Nhà hàng, đồ ăn nướng, đồ uống"},
        {"category": "Văn nghệ + truyền thông", "examples": "Diễn xuất, điện ảnh, MC, ca sĩ"},
        {"category": "Trang sức + cosmetic", "examples": "Đồ trang sức, cắt tóc, mỹ phẩm"},
        {"category": "Giáo dục + xuất bản", "examples": "Giảng dạy, in ấn, văn phòng phẩm"},
    ],
    "thổ": [
        {"category": "Bất động sản + đất đai", "examples": "Mua bán nhà ở, kiến trúc, quản lý dự án"},
        {"category": "Nông nghiệp + chăn nuôi", "examples": "Chăn nuôi gia cầm, thổ sản, nông trại"},
        {"category": "Vải vóc + thêu dệt", "examples": "Thời trang, vải, may mặc, thêu"},
        {"category": "Trung gian / tư vấn", "examples": "Môi giới, luật sư, cố vấn, quản lý"},
        {"category": "Đá + xi măng + vật liệu", "examples": "Khai thác đá, xi măng, gạch ngói"},
    ],
    "thủy": [
        {"category": "Hàng hải + thủy sản", "examples": "Vận tải biển, đánh cá, thủy sản, du thuyền"},
        {"category": "Y học + dược phẩm", "examples": "Y tá, bác sĩ, dược liệu, chữa bệnh"},
        {"category": "Du lịch + di chuyển", "examples": "Du lịch, hàng không, vận tải, kí giả"},
        {"category": "Khoa học + công nghệ", "examples": "Nghiên cứu, lập trình, data science"},
        {"category": "Chiêm bốc + tâm linh", "examples": "Tử Bình, phong thủy, tâm lý, tarot"},
    ],
    "kim": [
        {"category": "Kim loại + cơ khí", "examples": "Cơ khí, kim hoàn, ô tô, công nghiệp nặng"},
        {"category": "Quản lý + lãnh đạo", "examples": "Quan thanh liêm, tổng quản, CEO, giám đốc"},
        {"category": "Võ thuật + an ninh", "examples": "Quân đội, công an, võ thuật, vệ sĩ"},
        {"category": "Giám định + kỹ thuật", "examples": "Kiểm định chất lượng, đánh giá, công chứng"},
        {"category": "Tài chính cứng", "examples": "Kế toán, audit, ngân hàng, vàng bạc"},
    ],
}

# Thập Thần dominant → career style nuance
THAP_THAN_CAREER_STYLE: dict[str, str] = {
    "Tỷ Kiên": "Tự lập + đối tác ngang vai. Hợp khởi nghiệp + freelance + đồng nghiệp.",
    "Kiếp Tài": "Quyết liệt + tranh đua. Hợp môi trường cạnh tranh + ra ngoài bươn chải.",
    "Thực Thần": "Sáng tạo + hưởng thụ. Hợp nghệ thuật, ẩm thực, giáo dục.",
    "Thương Quan": "Tài năng đột phá + phá cách. Hợp startup, công nghệ, sáng tạo độc đáo.",
    "Thiên Tài": "Kinh doanh đa lĩnh vực + môi giới + tài lộc bất ngờ.",
    "Chính Tài": "Tài chính ổn định + kinh doanh truyền thống.",
    "Thất Sát": "Quyền lực + áp lực cao. Hợp quân đội, leadership, mạo hiểm.",
    "Chính Quan": "Chức vụ chính thống + công chức + danh tiếng.",
    "Thiên Ấn": "Trí tuệ phi truyền thống + tâm linh + nghiên cứu lập dị.",
    "Chính Ấn": "Học thuật + giáo dục + từ thiện + danh tiếng học giả.",
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _detect_career_pattern(thap_than_dist: dict, day_master_tag: str) -> list[dict]:
    """Detect dominant career patterns from Thập Thần distribution + DM strength."""
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0

    patterns = []

    # Pattern 1: Quan vượng + Ấn hộ
    quan_strength = combined.get("Chính Quan", 0) + combined.get("Thất Sát", 0)
    an_strength = combined.get("Chính Ấn", 0) + combined.get("Thiên Ấn", 0)
    if quan_strength >= 2 and an_strength >= 1:
        patterns.append({
            "name": "Quan Ấn tương sinh",
            "narrative": "Quan tinh + Ấn hộ → cấu hình QUÝ HIỂN, hợp chức vụ chính thống. "
                        "Day Master được Ấn bảo + Quan dẫn → leadership chính danh.",
            "career_hint": "công chức cấp cao / quản lý / chính trị / học thuật + danh tiếng",
        })

    # Pattern 2: Thực Thương vượng + Tài
    thuc_thuong = combined.get("Thực Thần", 0) + combined.get("Thương Quan", 0)
    tai = combined.get("Chính Tài", 0) + combined.get("Thiên Tài", 0)
    if thuc_thuong >= 2 and tai >= 1:
        patterns.append({
            "name": "Thực Thương sinh Tài",
            "narrative": "Thực Thần / Thương Quan sinh ra Tài → cấu hình PHÚ. "
                        "Sáng tạo + kinh doanh = tài lộc bền vững.",
            "career_hint": "kinh doanh sáng tạo / nghệ thuật + thương mại / startup",
        })

    # Pattern 3: Sát + Thực Chế Sát
    if combined.get("Thất Sát", 0) >= 1 and combined.get("Thực Thần", 0) >= 1:
        patterns.append({
            "name": "Thực Thần chế Sát",
            "narrative": "Sát có chế → Sát biến thành QUYỀN. "
                        "Hợp nghề áp lực cao + lãnh đạo + có kỷ luật + sáng tạo.",
            "career_hint": "quân đội / công an / kinh doanh mạo hiểm + có chiến lược",
        })

    # Pattern 4: Tỷ Kiếp vượng + Day Master nhược → khởi nghiệp nhờ đối tác
    ty_kiep = combined.get("Tỷ Kiên", 0) + combined.get("Kiếp Tài", 0)
    if ty_kiep >= 2 and day_master_tag == "weak":
        patterns.append({
            "name": "Tỷ Kiếp trợ thân",
            "narrative": "Day Master nhược + Tỷ Kiếp vượng → cần đối tác / cộng sự cùng vai. "
                        "Khó làm 1 mình — hợp khởi nghiệp nhóm, partnership.",
            "career_hint": "khởi nghiệp nhóm / partnership / co-founder",
        })

    # Pattern 5: Tài vượng + Day Master nhược → KHÔNG hợp commerce trực tiếp
    if tai >= 3 and day_master_tag == "weak":
        patterns.append({
            "name": "Tài đa thân nhược",
            "narrative": "Tài quá vượng + Day Master nhược → CÓ Tài cũng không gánh nổi. "
                        "Tránh tự kinh doanh áp lực cao, ưu tiên lương cứng + xây nội lực.",
            "career_hint": "tránh: tự kinh doanh áp lực cao. Nên: lương cứng + tích nội lực",
        })

    # Pattern 6: Ấn nhiều + không Tài → ỷ lại
    if an_strength >= 3 and tai == 0:
        patterns.append({
            "name": "Ấn nhiều thiếu Tài",
            "narrative": "Ấn quá vượng + thiếu Tài → trí tuệ giàu nhưng dễ ỷ lại, ít hành động. "
                        "Cần Tài làm động lực thực hành.",
            "career_hint": "học thuật + kết hợp ứng dụng thực tế / chuyển giao",
        })

    return patterns


def _recommend_industries(dung_than_el: str, hy_than_el: str,
                           cach_name: str) -> dict:
    """Top recommendations dựa trên Dụng + Hỷ + Cách."""
    cach_data = CACH_CUC_TO_NGHE.get(cach_name, {})
    out = {
        "from_cach_cuc": cach_data.get("industries", []),
        "cach_career_style": cach_data.get("career_style", ""),
        "cach_narrative": cach_data.get("narrative", ""),
        "from_dung_than": ELEMENT_TO_DETAILED_NGHE.get(dung_than_el, []),
        "from_hy_than": ELEMENT_TO_DETAILED_NGHE.get(hy_than_el, []),
    }
    return out


def _avoid_industries(ky_than_el: str) -> dict:
    """Industries to limit (Kỵ Thần) — không phải tránh hoàn toàn."""
    return {
        "from_ky_than": ELEMENT_TO_DETAILED_NGHE.get(ky_than_el, []),
        "narrative": (
            f"Khí Kỵ Thần = {ky_than_el.title()}. "
            f"KHÔNG phải tránh hoàn toàn, nhưng cần giảm liều lượng / "
            f"không làm hoạt động chính trong môi trường này lâu dài."
        ),
    }


def _suggest_career_timing(dai_van_cycles: list[dict],
                             dung_than_el: str, hy_than_el: str,
                             ky_than_el: str) -> list[dict]:
    """Đánh giá từng Đại Vận cycle vs Dụng/Hỷ/Kỵ Thần."""
    out = []
    for c in dai_van_cycles:
        stem_el = STEM_ELEMENT.get(c.get("stem", ""))
        branch_el = BRANCH_ELEMENT.get(c.get("branch", ""))
        elements = {stem_el, branch_el}
        if dung_than_el in elements and ky_than_el not in elements:
            verdict = "thuận lợi"
            mark = "✦"
        elif ky_than_el in elements and dung_than_el not in elements:
            verdict = "thử thách"
            mark = "⚠"
        elif hy_than_el in elements and ky_than_el not in elements:
            verdict = "tích lũy"
            mark = "✧"
        elif dung_than_el in elements and ky_than_el in elements:
            verdict = "hỗn tạp"
            mark = "⚖"
        else:
            verdict = "trung"
            mark = "·"
        out.append({
            **c,
            "verdict": verdict,
            "mark": mark,
            "stem_element": stem_el,
            "branch_element": branch_el,
        })
    return out


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_su_nghiep_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ. Cách Cục → ngành nghề + "
    "Dụng Thần → bổ hướng (Q. 2 + Q. 4)."
)


def analyze_su_nghiep(bat_tu_state: dict) -> dict:
    """Phân tích Sự nghiệp từ lá số Bát Tự.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.

    Returns:
        Structured dict với 5 sections.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    cach_cuc = bat_tu_state.get("cach_cuc", {})
    cach_name = cach_cuc.get("cach_name", "")
    dung_than = bat_tu_state.get("dung_than", {})
    dung_el = dung_than.get("dung_than_element", "")
    hy_el = dung_than.get("hy_than_element", "")
    ky_el = dung_than.get("ky_than_element", "")
    thap_than_dist = bat_tu_state.get("thap_than_distribution", {})
    dm_tag = bat_tu_state["ngu_hanh"]["day_master_assessment"]["strength_tag"]
    dai_van = bat_tu_state.get("dai_van", {})

    # 1. Career patterns
    patterns = _detect_career_pattern(thap_than_dist, dm_tag)

    # 2. Recommendations
    recommendations = _recommend_industries(dung_el, hy_el, cach_name)

    # 3. Cảnh báo
    avoid = _avoid_industries(ky_el)

    # 4. Timing
    timing_cycles = _suggest_career_timing(dai_van.get("cycles", []), dung_el, hy_el, ky_el)

    # 5. Career style narrative — composite
    dom_tt_styles = []
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0
    sorted_tt = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    for tt, w in sorted_tt[:3]:
        if w >= 2.0 and tt in THAP_THAN_CAREER_STYLE:
            dom_tt_styles.append({"name": tt, "style": THAP_THAN_CAREER_STYLE[tt]})

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Phân tích Sự nghiệp KHÔNG dự đoán anh sẽ thành công nghề X. "
            "Đọc cấu trúc khí của Cách Cục + Dụng Thần + Thập Thần dominant → "
            "recommend HÀNH và HƯỚNG nghề nghiệp phù hợp với khí bẩm sinh."
        ),
        "cach_cuc_summary": {
            "name": cach_name,
            "career_style": recommendations.get("cach_career_style"),
            "narrative": recommendations.get("cach_narrative"),
        },
        "career_patterns": patterns,
        "dominant_thap_than_styles": dom_tt_styles,
        "recommendations": {
            "by_cach_cuc": recommendations["from_cach_cuc"],
            "by_dung_than": {
                "element": dung_el,
                "industries": recommendations["from_dung_than"],
            },
            "by_hy_than": {
                "element": hy_el,
                "industries": recommendations["from_hy_than"],
            },
        },
        "avoid": avoid,
        "timing_by_dai_van": timing_cycles,
        "closing": (
            f"Sự nghiệp KHÔNG quyết định bởi 'số mệnh'. Lá số chỉ cho thấy "
            f"HÀNH thuận + cách cục → hướng nghiệp phù hợp. "
            f"Chìa khóa = chọn ngành thuộc {dung_el.title()} hoặc {hy_el.title()}, "
            f"phối hợp với Đại Vận đi đúng Dụng Thần để phát huy mạnh nhất."
        ),
    }
