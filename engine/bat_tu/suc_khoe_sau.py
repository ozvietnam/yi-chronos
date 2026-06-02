"""Sức Khỏe SÂU — tích hợp Bát Tự + Phù-Ức + Nguyên Lưu + chấn thương cụ thể.

Anh duyệt 2026-06-02 chiều (sau Bát Tự engine "Ấn Tỷ ánh sáng"):
> "anh mới đứt gân đầu gối 3 năm trước, mới mổ cách đây 5 tháng.
>  chân giờ rất yếu. anh quan tâm tới sức khỏe nữa.
>  nên mở thêm trang sức khỏe đi em."

Paradigm CỐT (Hoàng Đế Nội Kinh + Iron Rule #4+6):
- Mộc → Can/Đởm → chủ GÂN
- Hỏa → Tâm/Tiểu Trường → chủ MẠCH + HUYẾT
- Thổ → Tỳ/Vị → chủ CƠ THỊT
- Kim → Phế/Đại Trường → chủ DA + KHÍ HÔ HẤP
- Thủy → Thận/Bàng Quang → chủ XƯƠNG + TỦY + TAI + SINH KHÍ

Engine tích hợp:
1. Cơ bản (cũ): Ngũ hành thừa/thiếu → tạng phủ
2. Phù-Ức sâu: Day Master yếu → tạng tương ứng yếu
3. Nguyên Lưu: mạch tắc → nơi nào trong chu trình tạng phủ tắc
4. Chấn thương cụ thể (user input): cá nhân hóa lời khuyên
5. Đại Vận hiện tại: vận hồi phục có thuận không?

⚠️ KHÔNG predict "khi nào hồi phục" — chỉ đọc cấu trúc.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── Tạng phủ chuyên sâu cho từng element ────────────────────────────────────

ELEMENT_HEALTH_DEEP: dict[str, dict] = {
    "mộc": {
        "tang": "Can (Gan)",
        "phu": "Đởm (Mật)",
        "the": "GÂN",
        "khieu": "Mắt",
        "than": "Hồn",
        "emotion": "Giận",
        "season": "Xuân",
        "vi": "Chua",
        "mau": "Xanh",
        "khi_yeu_bieu_hien": [
            "Gân yếu, dễ chuột rút, dễ chấn thương khớp",
            "Đứt gân — biểu hiện nặng của Mộc nhược",
            "Mắt khô, mỏi, kém sáng",
            "Dễ giận, dễ uất ức không nói ra",
            "Mất ngủ vì lo nghĩ",
            "Cứng khớp buổi sáng",
        ],
        "thuc_an_duong": [
            "Đậu xanh, rau lá xanh đậm (rau ngót, rau muống, cải bó xôi)",
            "Quả mọng có vị chua (mơ, dâu, việt quất)",
            "Mộc nhĩ đen + nấm hương",
            "Hạt sen, kỷ tử",
            "Gừng tươi (sáng) — kích hoạt khí Can",
        ],
        "tranh_an": [
            "Rượu mạnh — Can sợ rượu",
            "Đồ cay nóng quá (ớt cay)",
            "Mỡ động vật quá nhiều",
            "Cà phê đậm uống chiều/tối",
        ],
        "van_dong": [
            "Đi bộ chậm trên đất phẳng — nuôi gân nhẹ nhàng",
            "Yoga tư thế giãn (hatha) — giãn gân",
            "Khí công + thái cực quyền — Mộc nhược cần khí thuận",
            "TRÁNH: chạy nhảy mạnh, nâng tạ nặng, va đập (gân yếu sợ va)",
        ],
        "gio_duong": "23h-3h (giờ Tý-Sửu) — giờ Can-Đởm — phải NGỦ trong giờ này",
    },
    "hỏa": {
        "tang": "Tâm (Tim)",
        "phu": "Tiểu Trường",
        "the": "MẠCH + HUYẾT",
        "khieu": "Lưỡi",
        "than": "Thần",
        "emotion": "Vui mừng quá",
        "season": "Hạ",
        "vi": "Đắng",
        "mau": "Đỏ",
        "khi_yeu_bieu_hien": [
            "Tim hồi hộp, mất ngủ, mộng nhiều",
            "Lưỡi khô, miệng lở loét",
            "Mạch yếu, huyết áp thấp",
            "Tinh thần khó tập trung",
        ],
        "thuc_an_duong": [
            "Đậu đỏ, quả táo đỏ, nho đen",
            "Tim heo (cẩn thận đạm)",
            "Trà sen, trà đắng (mướp đắng)",
            "Long nhãn, táo tàu",
        ],
        "tranh_an": [
            "Đường tinh luyện quá nhiều",
            "Chất kích thích (rượu mạnh, năng lượng cao)",
        ],
        "van_dong": [
            "Aerobic vừa phải — nuôi mạch",
            "Tránh tập quá khuya làm Tâm động",
        ],
        "gio_duong": "11h-13h (giờ Ngọ) — giờ Tâm — nghỉ trưa 15-30 phút",
    },
    "thổ": {
        "tang": "Tỳ (Lá lách)",
        "phu": "Vị (Dạ dày)",
        "the": "CƠ + THỊT",
        "khieu": "Miệng",
        "than": "Ý",
        "emotion": "Lo nghĩ quá",
        "season": "Cuối hạ (giao mùa)",
        "vi": "Ngọt",
        "mau": "Vàng",
        "khi_yeu_bieu_hien": [
            "Cơ nhão, mệt mỏi không lý do",
            "Tiêu hóa kém, ăn không ngon",
            "Bụng đầy hơi, phân lỏng",
            "Mất khẩu vị",
        ],
        "thuc_an_duong": [
            "Gạo lứt, ngô vàng, bí đỏ",
            "Khoai lang, củ cải vàng",
            "Mật ong tự nhiên",
            "Chè đậu các loại",
        ],
        "tranh_an": [
            "Đồ lạnh sống (uống đá)",
            "Đồ tanh sống",
            "Bỏ bữa, ăn không đúng giờ",
        ],
        "van_dong": [
            "Vận động vừa phải sau ăn",
            "Massage bụng theo chiều kim đồng hồ",
        ],
        "gio_duong": "7h-11h (giờ Thìn-Tỵ) — giờ Tỳ-Vị — ăn sáng đủ",
    },
    "kim": {
        "tang": "Phế (Phổi)",
        "phu": "Đại Trường",
        "the": "DA + KHÍ HÔ HẤP",
        "khieu": "Mũi",
        "than": "Phách",
        "emotion": "Buồn / bi thương",
        "season": "Thu",
        "vi": "Cay",
        "mau": "Trắng",
        "khi_yeu_bieu_hien": [
            "Ho khan, hơi ngắn",
            "Da khô, dị ứng",
            "Mũi nghẹt, viêm xoang",
            "Táo bón, đại tràng yếu",
            "Buồn vô cớ",
        ],
        "thuc_an_duong": [
            "Lê, củ cải trắng, hạnh nhân",
            "Mộc nhĩ trắng (tuyết nhĩ)",
            "Tỏi, hành trắng (cay nhẹ)",
            "Mật ong + chanh ấm",
        ],
        "tranh_an": [
            "Đồ chiên rán nhiều dầu mỡ",
            "Khói thuốc + không khí ô nhiễm",
        ],
        "van_dong": [
            "Thở bụng sâu (khí công)",
            "Đi bộ vùng cây xanh, không khí trong",
        ],
        "gio_duong": "3h-7h (giờ Dần-Mão) — giờ Phế-Đại Trường — dậy sớm thở khí",
    },
    "thủy": {
        "tang": "Thận (Thận + thận âm)",
        "phu": "Bàng Quang",
        "the": "XƯƠNG + TỦY + RĂNG + TÓC",
        "khieu": "Tai",
        "than": "Chí (ý chí)",
        "emotion": "Sợ hãi",
        "season": "Đông",
        "vi": "Mặn",
        "mau": "Đen",
        "khi_yeu_bieu_hien": [
            "Lưng đau, gối yếu — XƯƠNG KHỚP không vững",
            "Tóc bạc sớm, rụng tóc",
            "Răng lung lay sớm",
            "Tai ù, nghe kém",
            "Sinh khí yếu (sinh lý)",
            "Sợ lạnh, chân tay lạnh",
        ],
        "thuc_an_duong": [
            "Đậu đen — NHẤT cho Thận",
            "Mè đen, óc chó",
            "Hải sản (tôm, cua nhẹ) — bổ tinh",
            "Hà thủ ô, thục địa (trà thuốc)",
            "Thịt dê (mùa đông)",
        ],
        "tranh_an": [
            "Đồ mặn quá (làm Thận quá tải)",
            "Đồ lạnh — Thận sợ lạnh",
        ],
        "van_dong": [
            "Vỗ thận buổi sáng (đứng vỗ nhẹ vùng eo)",
            "Đi bộ lùi (dưỡng Thận)",
            "TRÁNH dầm mưa, ngâm chân lạnh lâu",
        ],
        "gio_duong": "17h-19h (giờ Dậu) — giờ Thận — ăn tối nhẹ, đi ngủ sớm",
    },
}


# ─── Chấn thương cụ thể → mapping element ──────────────────────────────────

CHAN_THUONG_MAP: dict[str, dict] = {
    "gân": {
        "element": "mộc",
        "y_nghia": (
            "Gân thuộc MỘC — Can chủ gân. Đứt gân / gân yếu = Mộc nhược "
            "(Day Master Mộc thiếu gốc, hoặc Mộc bị Kim khắc quá mạnh)."
        ),
        "kem_theo": ["Thủy yếu (Thận không nuôi Mộc)", "Can khí uất"],
    },
    "đầu gối": {
        "element": "mộc + thủy",
        "y_nghia": (
            "Đầu gối = khớp + gân + xương. Gân thuộc MỘC, Xương khớp thuộc THỦY. "
            "Đứt gân đầu gối = cả Mộc + Thủy đều cần dưỡng."
        ),
        "kem_theo": ["Can Thận hư"],
    },
    "khớp": {
        "element": "mộc + thủy",
        "y_nghia": "Khớp = nơi gân (Mộc) gắn vào xương (Thủy).",
        "kem_theo": ["Cả Mộc + Thủy"],
    },
    "xương": {
        "element": "thủy",
        "y_nghia": "Xương thuộc THỦY — Thận chủ cốt.",
        "kem_theo": ["Tủy yếu"],
    },
    "lưng": {
        "element": "thủy",
        "y_nghia": "Lưng = vùng Thận — đau lưng = Thận khí yếu.",
        "kem_theo": [],
    },
    "tim": {
        "element": "hỏa",
        "y_nghia": "Tim thuộc HỎA — Tâm.",
        "kem_theo": [],
    },
    "phổi": {
        "element": "kim",
        "y_nghia": "Phổi thuộc KIM — Phế.",
        "kem_theo": [],
    },
    "dạ dày": {
        "element": "thổ",
        "y_nghia": "Dạ dày thuộc THỔ — Vị.",
        "kem_theo": [],
    },
    "gan": {
        "element": "mộc",
        "y_nghia": "Gan thuộc MỘC — Can.",
        "kem_theo": [],
    },
}


@dataclass
class SucKhoeSauResult:
    """Kết quả phân tích sức khỏe sâu."""

    day_master_element: str
    constitution_tang: str         # Tạng chủ bẩm sinh
    constitution_the: str          # Thể (gân/mạch/cơ/da/xương)
    constitution_strength: str     # mạnh / vừa / yếu

    chan_thuong_input: str         # User input
    chan_thuong_analysis: dict     # Element + ý nghĩa

    weakness_tang_list: list[dict] # Các tạng yếu (từ Phù-Ức + Nguyên Lưu)
    overall_paradigm: str          # Tổng paradigm thân thể

    dietary_duong: list[str]       # Nuôi tạng yếu nhất
    dietary_tranh: list[str]       # Tránh
    lifestyle: list[str]           # Vận động + giờ giấc

    dai_van_hoi_phuc: str          # Đại vận hiện tại có thuận hồi phục không
    iron_rule_note: str            # Iron Rule guard

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_suc_khoe_sau(
    tu_tru: dict,
    chan_thuong: str = "",
    current_age: int | None = None,
) -> SucKhoeSauResult:
    """Engine chính — phân tích sức khỏe sâu cho founder + user.

    Args:
        tu_tru: pillars
        chan_thuong: text mô tả chấn thương đang có (vd "đứt gân đầu gối")
        current_age: tuổi hiện tại để lookup đại vận

    Returns: SucKhoeSauResult
    """
    from .phu_uc_route import STEM_ELEMENT, route_phu_uc, _count_pressure, ELEMENT_RELATION
    from .nguyen_luu_trace import trace_nguyen_luu
    from .thong_can import summarize_day_master_thong_can

    pillars = tu_tru["pillars"]
    dm_stem = pillars["day"]["stem"]
    dm_el = STEM_ELEMENT.get(dm_stem, "")

    # 1. Constitution bẩm sinh (Day Master tạng)
    health = ELEMENT_HEALTH_DEEP.get(dm_el, {})
    constitution_tang = health.get("tang", "")
    constitution_the = health.get("the", "")

    tc = summarize_day_master_thong_can(pillars)
    tc_score = tc.get("score", 0)
    if tc_score >= 4.0:
        constitution_strength = "mạnh"
    elif tc_score >= 2.0:
        constitution_strength = "vừa"
    else:
        constitution_strength = "yếu"

    # 2. Chấn thương analysis
    chan_thuong_lower = chan_thuong.lower()
    chan_thuong_analysis = {"input": chan_thuong, "matches": []}
    matched_elements = set()
    for keyword, info in CHAN_THUONG_MAP.items():
        if keyword in chan_thuong_lower:
            chan_thuong_analysis["matches"].append({
                "keyword": keyword,
                "element": info["element"],
                "y_nghia": info["y_nghia"],
                "kem_theo": info["kem_theo"],
            })
            # Track elements để dưỡng
            for el in info["element"].split(" + "):
                matched_elements.add(el.strip())

    # 3. Weakness tang_list (từ Phù-Ức + Nguyên Lưu)
    pressure = _count_pressure(pillars, dm_el)
    rel = ELEMENT_RELATION.get(dm_el, {})
    weakness_list = []

    # DM nhược → Tạng DM yếu
    if constitution_strength != "mạnh":
        weakness_list.append({
            "tang": constitution_tang,
            "the": constitution_the,
            "element": dm_el,
            "reason": f"Day Master {dm_el.title()} {constitution_strength} (thông căn score {tc_score})",
            "bieu_hien": health.get("khi_yeu_bieu_hien", [])[:4],
        })

    # Ấn yếu → Tạng sinh DM yếu
    an_el = rel.get("ấn", "")
    if an_el and pressure.get("ấn", 0) < 1.5:
        an_health = ELEMENT_HEALTH_DEEP.get(an_el, {})
        weakness_list.append({
            "tang": an_health.get("tang", ""),
            "the": an_health.get("the", ""),
            "element": an_el,
            "reason": f"Ấn ({an_el.title()}) yếu — tạng sinh DM không nuôi đủ",
            "bieu_hien": an_health.get("khi_yeu_bieu_hien", [])[:3],
        })

    # Nguyên Lưu tắc → element bị thiếu
    try:
        nl = trace_nguyen_luu(tu_tru)
        if nl.chan_tro_element:
            blocked_health = ELEMENT_HEALTH_DEEP.get(nl.chan_tro_element, {})
            weakness_list.append({
                "tang": blocked_health.get("tang", ""),
                "the": blocked_health.get("the", ""),
                "element": nl.chan_tro_element,
                "reason": f"Nguyên Lưu tắc mạch tại {nl.chan_tro_element.title()} — chu trình ngũ hành đứt đoạn",
                "bieu_hien": blocked_health.get("khi_yeu_bieu_hien", [])[:3],
            })
    except Exception:
        pass

    # 4. Overall paradigm
    parts = [
        f"Day Master **{dm_el.title()}** ({dm_stem}) cường độ **{constitution_strength}**.",
        f"Tạng chủ bẩm sinh: **{constitution_tang}** — chủ về **{constitution_the}**.",
    ]
    if chan_thuong_analysis["matches"]:
        parts.append("\n**Chấn thương Anh đang có khớp đúng paradigm lá số:**")
        for m in chan_thuong_analysis["matches"]:
            parts.append(f"- _{m['keyword']}_ thuộc hành **{m['element']}** — {m['y_nghia']}")
    parts.append(f"\n**Số tạng cần dưỡng:** {len(weakness_list)}")
    overall_paradigm = "\n".join(parts)

    # 5. Dietary recommendations — ưu tiên element của chấn thương + tạng yếu
    target_elements = list(matched_elements)
    for w in weakness_list:
        if w["element"] not in target_elements:
            target_elements.append(w["element"])

    dietary_duong = []
    dietary_tranh = []
    lifestyle = []
    seen_dietary = set()
    seen_lifestyle = set()

    for el in target_elements:
        info = ELEMENT_HEALTH_DEEP.get(el, {})
        for food in info.get("thuc_an_duong", []):
            if food not in seen_dietary:
                dietary_duong.append(f"[{el.title()}] {food}")
                seen_dietary.add(food)
        for food in info.get("tranh_an", []):
            if food not in seen_dietary:
                dietary_tranh.append(f"[{el.title()}] {food}")
                seen_dietary.add(food)
        for v in info.get("van_dong", []):
            if v not in seen_lifestyle:
                lifestyle.append(f"[{el.title()}] {v}")
                seen_lifestyle.add(v)
        # Giờ dưỡng
        gio = info.get("gio_duong", "")
        if gio and gio not in seen_lifestyle:
            lifestyle.append(f"[{el.title()}] Giờ dưỡng: {gio}")
            seen_lifestyle.add(gio)

    # 6. Đại Vận hồi phục
    dai_van_text = ""
    if current_age:
        # Đơn giản hóa: lookup vận hiện tại từ tu_tru's dai_van nếu có
        # Để engine return generic guidance
        if target_elements:
            primary_el = target_elements[0]
            dai_van_text = (
                f"Anh hiện ở tuổi {current_age}. "
                f"Cần check Đại Vận hiện tại — nếu vận có hành {primary_el.title()} "
                f"thì hồi phục thuận. Nếu vận có hành Khắc {primary_el.title()} thì chậm hơn."
            )
        else:
            dai_van_text = f"Anh hiện ở tuổi {current_age}. Cần check Đại Vận để biết vận hồi phục."
    else:
        dai_van_text = "Để biết vận hồi phục, cần input tuổi hiện tại."

    return SucKhoeSauResult(
        day_master_element=dm_el,
        constitution_tang=constitution_tang,
        constitution_the=constitution_the,
        constitution_strength=constitution_strength,
        chan_thuong_input=chan_thuong,
        chan_thuong_analysis=chan_thuong_analysis,
        weakness_tang_list=weakness_list,
        overall_paradigm=overall_paradigm,
        dietary_duong=dietary_duong[:15],  # Limit
        dietary_tranh=dietary_tranh[:10],
        lifestyle=lifestyle[:12],
        dai_van_hoi_phuc=dai_van_text,
        iron_rule_note=(
            "🪷 Iron Rule #4+6: Engine ra cấu trúc thân thể theo paradigm Đông y "
            "+ Bát Tự. KHÔNG dự đoán 'sẽ hồi phục năm X'. Hành động vẫn của Anh: "
            "ăn đúng + ngủ đúng giờ + vận động hợp. Đức năng thắng số."
        ),
    )


def render_suc_khoe_sau_markdown(result: SucKhoeSauResult) -> str:
    """Render markdown."""
    lines = [
        "# 🌿 Sức Khỏe Sâu — Bát Tự × Đông Y\n",
        "## 1. Tạng phủ bẩm sinh\n",
        f"- **Day Master:** {result.day_master_element.title()}",
        f"- **Tạng chủ:** {result.constitution_tang}",
        f"- **Thể (chủ về):** {result.constitution_the}",
        f"- **Cường độ:** {result.constitution_strength.upper()}\n",
        "## 2. Chấn thương hiện tại\n",
    ]
    if result.chan_thuong_input:
        lines.append(f"_Anh chia sẻ:_ **{result.chan_thuong_input}**\n")
        for m in result.chan_thuong_analysis.get("matches", []):
            lines.append(f"- **{m['keyword']}** (hành {m['element']}): {m['y_nghia']}")
        if not result.chan_thuong_analysis.get("matches"):
            lines.append("_(Không match keyword nào trong bảng — engine chỉ phân tích cấu trúc tổng)_")
    else:
        lines.append("_(Anh chưa nhập chấn thương đang có — engine phân tích cấu trúc tổng)_")

    lines.append("\n## 3. Tạng cần dưỡng\n")
    for i, w in enumerate(result.weakness_tang_list, 1):
        lines.append(f"### Tạng {i}: **{w['tang']}** (chủ {w['the']}, hành {w['element']})")
        lines.append(f"- _Lý do:_ {w['reason']}")
        lines.append("- _Biểu hiện khi yếu:_")
        for b in w.get("bieu_hien", []):
            lines.append(f"  - {b}")
        lines.append("")

    lines.append("## 4. Lời khuyên thực tiễn\n")
    lines.append("### ✅ Nên ăn (dưỡng tạng yếu)")
    for f in result.dietary_duong:
        lines.append(f"- {f}")
    lines.append("\n### ❌ Tránh")
    for f in result.dietary_tranh:
        lines.append(f"- {f}")
    lines.append("\n### 🚶 Vận động + giờ giấc")
    for v in result.lifestyle:
        lines.append(f"- {v}")

    lines.append(f"\n## 5. Đại Vận hồi phục\n{result.dai_van_hoi_phuc}\n")
    lines.append(f"---\n\n{result.iron_rule_note}")
    return "\n".join(lines)
