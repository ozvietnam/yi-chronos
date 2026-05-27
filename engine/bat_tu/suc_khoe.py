"""Sức Khỏe (健康) — health analysis from Bát Tự chart, cross-referenced with Trung y.

Paradigm (Iron Rule #4+6): KHÔNG dự đoán "anh sẽ bị bệnh X năm Y". Đọc cấu trúc
ngũ hành thừa/thiếu → tạng phủ tương ứng (Trung y mapping) → cảnh báo phòng ngừa
+ dietary + lifestyle recommendations.

Source: Thiệu Vĩ Hoa Q1 ch.1 ("Trung y + chiêm bốc cùng paradigm âm dương ngũ hành")
+ classical Trung y (Hoàng Đế Nội Kinh):
- Mộc ↔ Can/Đởm + mắt + gân
- Hỏa ↔ Tâm/Tiểu Trường + lưỡi + mạch
- Thổ ↔ Tỳ/Vị + miệng + cơ
- Kim ↔ Phế/Đại Trường + mũi + da
- Thủy ↔ Thận/Bàng Quang + tai + xương

Algorithm:
1. Ngũ hành count → identify thừa/thiếu
2. Map thừa/thiếu → tạng phủ + symptoms tiềm ẩn
3. Day Master strength → tinh khí thần overall
4. Đại Vận → cảnh báo tạng phủ khi vào Kỵ element
5. Dietary recommendations theo Dụng Thần (5 flavors + 5 colors)
6. Lifestyle recommendations theo cấu hình
"""

from __future__ import annotations

from .constants import BRANCH_ELEMENT, STEM_ELEMENT


# ─── Trung y mapping tables ──────────────────────────────────────────────────

# Ngũ hành ↔ Tạng phủ (Hoàng Đế Nội Kinh)
ELEMENT_TANG_PHU: dict[str, dict] = {
    "mộc": {
        "tang": "Can",  # Gan
        "phu": "Đởm",  # Mật
        "khieu": "mắt",
        "the": "gân",
        "vi": "chua",
        "mau": "xanh",
        "than": "Hồn (Linh hồn)",
        "emotion": "giận / nóng nảy",
        "season": "xuân",
    },
    "hỏa": {
        "tang": "Tâm",  # Tim
        "phu": "Tiểu Trường",  # Ruột non
        "khieu": "lưỡi",
        "the": "mạch + huyết",
        "vi": "đắng",
        "mau": "đỏ",
        "than": "Thần (tinh thần)",
        "emotion": "vui mừng / hứng phấn",
        "season": "hạ",
    },
    "thổ": {
        "tang": "Tỳ",  # Lá lách
        "phu": "Vị",  # Dạ dày
        "khieu": "miệng",
        "the": "cơ + thịt",
        "vi": "ngọt",
        "mau": "vàng",
        "than": "Ý (suy nghĩ)",
        "emotion": "tư duy quá / lo lắng",
        "season": "cuối hạ (giao mùa)",
    },
    "kim": {
        "tang": "Phế",  # Phổi
        "phu": "Đại Trường",  # Ruột già
        "khieu": "mũi",
        "the": "da + lông",
        "vi": "cay",
        "mau": "trắng",
        "than": "Phách (sức sống)",
        "emotion": "buồn / bi thương",
        "season": "thu",
    },
    "thủy": {
        "tang": "Thận",  # Thận
        "phu": "Bàng Quang",  # Bàng quang
        "khieu": "tai",
        "the": "xương + tủy",
        "vi": "mặn",
        "mau": "đen",
        "than": "Chí (ý chí)",
        "emotion": "sợ hãi / kinh hoàng",
        "season": "đông",
    },
}

# Khí THỪA (quá vượng) → bệnh tiềm ẩn
ELEMENT_EXCESS_SYMPTOMS: dict[str, str] = {
    "mộc": "Gan nóng, đau đầu, mất ngủ, dễ cáu kỉnh, mắt đỏ, gân co rút. "
           "Cao huyết áp, đau đầu nửa bên.",
    "hỏa": "Tim đập nhanh, huyết áp cao, viêm mạch, nóng trong người, lưỡi đỏ, "
           "miệng khát, mất ngủ. Bệnh tim mạch.",
    "thổ": "Tiêu hóa kém, đầy bụng, dạ dày nhão, lo nghĩ nhiều, mệt mỏi. "
           "Tiểu đường, béo phì, đau dạ dày.",
    "kim": "Ho khan, phổi khô, da khô + ngứa, đại tràng táo bón, mũi tắc. "
           "Hen suyễn, viêm phổi, bệnh da.",
    "thủy": "Thận ứ, phù nề, đau lưng, tai ù, sợ lạnh, sinh dục yếu. "
           "Sỏi thận, suy thận, vô sinh.",
}

# Khí THIẾU (bất cập) → suy nhược tiềm ẩn
ELEMENT_DEFICIENT_SYMPTOMS: dict[str, str] = {
    "mộc": "Gan suy, mỏi mắt + nhìn mờ, gân yếu + chuột rút, thiếu quyết đoán. "
           "Mệt mỏi mãn tính, dễ chóng mặt.",
    "hỏa": "Tim đập yếu, sợ lạnh, tuần hoàn kém, mạch yếu, lưỡi nhạt. "
           "Huyết áp thấp, thiếu máu, trầm cảm.",
    "thổ": "Tiêu hóa kém + chán ăn, sút cân, cơ nhão, tay chân yếu, "
           "lo lắng quá. Loét dạ dày, kém hấp thu.",
    "kim": "Phổi yếu + dễ cảm, dị ứng, da xấu + thiếu sắc, đại tràng tiêu chảy. "
           "Suy giảm miễn dịch, hen dị ứng.",
    "thủy": "Thận yếu, tai ù + thính lực giảm, xương khớp yếu, lưng đau, "
           "sinh dục suy. Loãng xương, lưng mỏi.",
}

# Dietary by Dụng Thần (5 elements)
DIETARY_BY_ELEMENT: dict[str, dict] = {
    "mộc": {
        "vi": "chua nhẹ + tươi",
        "thuc_pham": ["rau xanh lá", "trái cây tươi (cam/chanh/mơ)",
                      "đậu xanh", "trà xanh", "giấm táo", "ngũ cốc nguyên cám"],
        "tranh": "đồ chiên rán, thực phẩm nhiều dầu mỡ",
    },
    "hỏa": {
        "vi": "đắng + cay nhẹ",
        "thuc_pham": ["khổ qua (mướp đắng)", "rau cải đắng", "trà đen",
                      "cà phê vừa phải", "hạt cay (gừng, tỏi nhẹ)", "thực phẩm đỏ"],
        "tranh": "đồ lạnh, nước đá quá nhiều",
    },
    "thổ": {
        "vi": "ngọt vừa (tự nhiên) + tinh bột",
        "thuc_pham": ["gạo lứt", "khoai lang", "bí đỏ", "ngũ cốc",
                      "mật ong nhẹ", "trái cây ngọt vừa", "đậu nành"],
        "tranh": "đồ ngọt nhân tạo, đồ ăn lạnh sống",
    },
    "kim": {
        "vi": "cay nhẹ + thanh đạm",
        "thuc_pham": ["hành/tỏi/gừng vừa", "rau trắng (cải bắp, cải thảo)",
                      "nấm trắng", "lê", "sữa đậu nành", "thực phẩm tráng dương phế"],
        "tranh": "đồ chiên rán, thực phẩm khô cứng",
    },
    "thủy": {
        "vi": "mặn nhẹ + đậm",
        "thuc_pham": ["thủy sản (cá, tôm)", "tảo biển/rong biển", "đậu đen",
                      "hạt đen (vừng đen, đậu đen)", "nấm đen", "thịt thận bổ"],
        "tranh": "muối quá mặn, đường tinh chế",
    },
}

# Lifestyle by element imbalance
LIFESTYLE_RECOMMENDATIONS: dict[str, str] = {
    "mộc": "Tập tỉnh tâm + thiền sáng, đi bộ rừng/công viên, ngủ trước 23h (giờ Tý gan giải độc).",
    "hỏa": "Tập aerobic vừa phải, không kích thích thần kinh quá đêm, "
           "giữ tâm bình ổn, thiền + thở chậm.",
    "thổ": "Ăn đúng giờ + nhai kỹ, đi bộ sau ăn, tránh suy nghĩ lan man, "
           "Yoga + Khí công giúp tỳ vị.",
    "kim": "Tập thở sâu (Khí công), giữ ấm mũi phổi, không khí trong sạch, "
           "đi bộ trong rừng (negative ions tốt cho phế).",
    "thủy": "Ngủ đủ + sớm (thận chính khí), giữ ấm vùng lưng + bàn chân, "
           "uống đủ nước ấm, tránh stress kéo dài.",
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _identify_imbalance(element_counts: dict[str, float]) -> dict:
    """Identify excess + deficient elements."""
    total = sum(element_counts.values()) or 1
    excess = []
    deficient = []
    for el, count in element_counts.items():
        pct = count / total
        if count >= 3 or pct >= 0.35:
            excess.append({"element": el, "count": count, "pct": round(pct * 100)})
        elif count <= 0.5 or pct <= 0.08:
            deficient.append({"element": el, "count": count, "pct": round(pct * 100)})
    return {
        "excess": excess,
        "deficient": deficient,
        "balance_score": 1.0 - sum(abs(c/total - 0.2) for c in element_counts.values()),
    }


def _tang_phu_warnings(imbalance: dict) -> list[dict]:
    """Compose tạng phủ warnings cho excess + deficient."""
    out = []
    for ex in imbalance["excess"]:
        el = ex["element"]
        tp = ELEMENT_TANG_PHU[el]
        out.append({
            "type": "excess",
            "element": el,
            "tang": tp["tang"],
            "phu": tp["phu"],
            "polarity": "cảnh báo",
            "symptoms": ELEMENT_EXCESS_SYMPTOMS[el],
            "narrative": (
                f"**{el.title()} THỪA** ({ex['count']:.1f}/{ex['pct']}%) → "
                f"Tạng {tp['tang']} + Phủ {tp['phu']} dễ quá vượng. "
                f"Cảnh báo: {ELEMENT_EXCESS_SYMPTOMS[el]}"
            ),
        })
    for df in imbalance["deficient"]:
        el = df["element"]
        tp = ELEMENT_TANG_PHU[el]
        out.append({
            "type": "deficient",
            "element": el,
            "tang": tp["tang"],
            "phu": tp["phu"],
            "polarity": "thiếu",
            "symptoms": ELEMENT_DEFICIENT_SYMPTOMS[el],
            "narrative": (
                f"**{el.title()} THIẾU** ({df['count']:.1f}/{df['pct']}%) → "
                f"Tạng {tp['tang']} + Phủ {tp['phu']} dễ suy nhược. "
                f"Cảnh báo: {ELEMENT_DEFICIENT_SYMPTOMS[el]}"
            ),
        })
    return out


def _dai_van_health_warnings(dai_van_cycles: list[dict],
                              ky_element: str) -> list[dict]:
    """Cảnh báo tạng phủ khi Đại Vận vào Kỵ element."""
    out = []
    if not ky_element:
        return out
    tp = ELEMENT_TANG_PHU.get(ky_element)
    if not tp:
        return out
    for c in dai_van_cycles:
        stem_el = STEM_ELEMENT.get(c.get("stem", ""))
        branch_el = BRANCH_ELEMENT.get(c.get("branch", ""))
        if stem_el == ky_element or branch_el == ky_element:
            out.append({
                "cycle_index": c["cycle_index"],
                "stem": c["stem"],
                "branch": c["branch"],
                "age_range": f"{c['start_age']}-{c['end_age']}",
                "ky_element": ky_element,
                "tang_at_risk": tp["tang"],
                "narrative": (
                    f"V{c['cycle_index']} ({c['stem']} {c['branch']}, "
                    f"tuổi {c['start_age']}-{c['end_age']}) có khí "
                    f"{ky_element.title()} = Kỵ Thần → đề phòng tạng "
                    f"{tp['tang']} + phủ {tp['phu']}."
                ),
            })
    return out


def _day_master_constitution(dm_tag: str, dm_element: str) -> dict:
    """Tinh khí thần overall theo Day Master strength + element."""
    tp = ELEMENT_TANG_PHU[dm_element]
    if dm_tag == "strong":
        narrative = (
            f"Day Master {dm_element.title()} VƯỢNG → tinh khí thần dồi dào, "
            f"sức bền tốt. Tạng chủ ({tp['tang']}) hoạt động mạnh. "
            f"Cảnh báo: nếu vượng quá → cần tiết khí ra (tập thể thao, "
            f"sáng tạo) để tránh nội nhiệt."
        )
    elif dm_tag == "weak":
        narrative = (
            f"Day Master {dm_element.title()} NHƯỢC → tinh khí thần thiếu hụt, "
            f"dễ mệt mỏi. Tạng chủ ({tp['tang']}) yếu. "
            f"Bồi dưỡng: nghỉ ngơi đủ, dinh dưỡng đủ chất {tp['vi']}, "
            f"tránh stress kéo dài."
        )
    else:
        narrative = (
            f"Day Master {dm_element.title()} TRUNG HÒA → tinh khí thần "
            f"cân bằng. Tạng chủ ({tp['tang']}) ổn định. Duy trì lối sống "
            f"điều độ, tránh extremes."
        )
    return {
        "tag": dm_tag,
        "element": dm_element,
        "primary_tang": tp["tang"],
        "primary_phu": tp["phu"],
        "khieu": tp["khieu"],
        "the": tp["the"],
        "than": tp["than"],
        "narrative": narrative,
    }


def _dietary_recommendations(dung_than_el: str, hy_than_el: str,
                              imbalance: dict) -> dict:
    """Dietary recommendations theo Dụng Thần + Hỷ Thần + imbalance."""
    dung_diet = DIETARY_BY_ELEMENT.get(dung_than_el, {})
    hy_diet = DIETARY_BY_ELEMENT.get(hy_than_el, {})

    bo_thieu = []
    for df in imbalance["deficient"]:
        el = df["element"]
        diet = DIETARY_BY_ELEMENT.get(el, {})
        if diet:
            bo_thieu.append({
                "element": el,
                "vi": diet["vi"],
                "thuc_pham_examples": diet["thuc_pham"][:3],
            })

    return {
        "by_dung_than": {
            "element": dung_than_el,
            "vi": dung_diet.get("vi", ""),
            "thuc_pham": dung_diet.get("thuc_pham", []),
            "tranh": dung_diet.get("tranh", ""),
        },
        "by_hy_than": {
            "element": hy_than_el,
            "vi": hy_diet.get("vi", ""),
            "thuc_pham": hy_diet.get("thuc_pham", []),
        },
        "bo_thieu": bo_thieu,
        "narrative": (
            f"Bổ dưỡng theo Dụng Thần **{dung_than_el.title()}** + "
            f"Hỷ Thần **{hy_than_el.title()}**. "
            f"Ưu tiên vị {dung_diet.get('vi', '')}. "
            + (f"Bồi khí thiếu: {', '.join(b['element'].title() for b in bo_thieu)}." if bo_thieu else "")
        ),
    }


def _lifestyle_recommendations(imbalance: dict, dm_element: str) -> str:
    """Lifestyle recommendations."""
    points = []
    # Focus on excess elements
    for ex in imbalance["excess"]:
        rec = LIFESTYLE_RECOMMENDATIONS.get(ex["element"], "")
        if rec:
            points.append(f"({ex['element'].title()} thừa) {rec}")
    # Then on day master constitution
    if not points:
        rec = LIFESTYLE_RECOMMENDATIONS.get(dm_element, "")
        if rec:
            points.append(f"(Day Master {dm_element.title()}) {rec}")
    return " ".join(points) if points else "Lối sống điều độ, ngủ đủ, ăn đúng giờ, vận động nhẹ hằng ngày."


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_suc_khoe_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa Q1 ch.1 + Hoàng Đế Nội Kinh (Trung y kinh điển). "
    "Ngũ hành ↔ tạng phủ + cảnh báo Đại Vận."
)


def analyze_suc_khoe(bat_tu_state: dict) -> dict:
    """Phân tích Sức Khỏe + Trung y cross-ref.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.

    Returns:
        Dict 8 sections.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    element_counts = bat_tu_state["ngu_hanh"]["counts"]
    dm_tag = bat_tu_state["ngu_hanh"]["day_master_assessment"]["strength_tag"]
    dm_element = bat_tu_state["tu_tru"]["day_master"]["element"]
    dai_van_cycles = bat_tu_state.get("dai_van", {}).get("cycles", [])
    dung_than = bat_tu_state.get("dung_than", {})
    dung_el = dung_than.get("dung_than_element", "")
    hy_el = dung_than.get("hy_than_element", "")
    ky_el = dung_than.get("ky_than_element", "")

    imbalance = _identify_imbalance(element_counts)
    tang_phu_warnings = _tang_phu_warnings(imbalance)
    constitution = _day_master_constitution(dm_tag, dm_element)
    dietary = _dietary_recommendations(dung_el, hy_el, imbalance)
    lifestyle = _lifestyle_recommendations(imbalance, dm_element)
    dai_van_warnings = _dai_van_health_warnings(dai_van_cycles, ky_el)

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Phân tích Sức Khỏe KHÔNG dự đoán anh sẽ bị bệnh X năm Y. "
            "Đọc cấu trúc ngũ hành thừa/thiếu → tạng phủ tương ứng (Trung y) → "
            "cảnh báo phòng ngừa + dietary + lifestyle. "
            "Cross-paradigm: Trung y + Tử Bình cùng dùng âm dương ngũ hành."
        ),
        "imbalance": imbalance,
        "tang_phu_warnings": tang_phu_warnings,
        "constitution": constitution,
        "dai_van_health_warnings": dai_van_warnings,
        "dietary": dietary,
        "lifestyle_narrative": lifestyle,
        "ngu_hanh_table": [
            {
                "element": el,
                "count": element_counts.get(el, 0),
                **ELEMENT_TANG_PHU[el],
            }
            for el in ("mộc", "hỏa", "thổ", "kim", "thủy")
        ],
        "closing": (
            "Sức khỏe = cân bằng khí ngũ hành. Lá số chỉ cấu hình tiềm ẩn — "
            "thực tế phụ thuộc lối sống + dinh dưỡng + tâm tính. "
            "Hợp tác bác sĩ khi có triệu chứng — Bát Tự CHỈ bổ sung góc nhìn paradigm."
        ),
    }
