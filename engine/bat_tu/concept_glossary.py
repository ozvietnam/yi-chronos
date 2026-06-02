"""Concept Glossary — registry thuật ngữ Bát Tự "tự sáng".

Anh duyệt 2026-06-02 paradigm "Ấn Tỷ ánh sáng": mỗi keyword phải có
- Định nghĩa ngắn (1-2 câu Việt thuần)
- Hán-Việt + giải thích vì sao gọi vậy
- Trích nguyên văn từ sách cổ (verified trong corpus)
- Diễn giải case (khi cần, set qua context)
- Cross-reference 10 thần / cách cục / paradigm khác

Sources verified:
- trich-thien-tuy-binh-chu-nham-thiet-tieu/content.md
- du-doan-tu-tru-thieu-vy-hoa/content.md
- du-bao-theo-tu-binh/content.md

Để generalize cho mọi lá số: gọi `glossary_explain(keyword, context=tu_tru)`.
Auto-detect keyword trong narrative → render tooltip / inline expansion.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class ConceptDef:
    """Định nghĩa 1 thuật ngữ — chùm ánh sáng."""

    key: str                          # vd "ấn_tỷ"
    ten_han_viet: str                 # vd "Ấn Tỷ"
    chu_han: str = ""                 # vd "印比"
    nghia_co_ban: str = ""            # 1-2 câu Việt thuần
    han_viet_explained: str = ""      # giải thích chữ Hán
    trich_sach: list[dict] = field(default_factory=list)   # [{sach, noi_dung, dong}]
    case_diengiai_fn: str = ""        # tên hàm diễn giải dynamic theo context
    related_concepts: list[str] = field(default_factory=list)
    iron_rule_link: str = ""          # link vào Iron Rule nào nếu có

    def to_dict(self) -> dict:
        return asdict(self)


# ─── GLOSSARY: 30+ thuật ngữ CỐT ─────────────────────────────────────────────

GLOSSARY: dict[str, ConceptDef] = {

    # ═══ 5 NHÓM 10 THẦN ═══

    "ấn_tỷ": ConceptDef(
        key="ấn_tỷ",
        ten_han_viet="Ấn Tỷ",
        chu_han="印比",
        nghia_co_ban=(
            "Nhóm 4 thần PHÙ TRỢ Day Master: Ấn (mẹ — sinh ra Tôi) + "
            "Tỷ (anh em — đồng hành Tôi). Khi Day Master nhược, cần Ấn Tỷ để phù thân."
        ),
        han_viet_explained=(
            "**Ấn (印)** = ấn tín, dấu của mẹ trao — hành sinh Day Master. "
            "**Tỷ (比)** = ngang vai, anh em đồng môn — cùng hành Day Master."
        ),
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "dong": 1676,
                "noi_dung": "Trợ thì dùng Tỷ Kiếp, sinh thì dùng Ấn Thụ.",
            },
        ],
        related_concepts=["chính_ấn", "thiên_ấn", "tỷ_kiên", "kiếp_tài", "phù_thân"],
    ),

    "chính_ấn": ConceptDef(
        key="chính_ấn",
        ten_han_viet="Chính Ấn",
        chu_han="正印",
        nghia_co_ban=(
            "Thần sinh Day Master, khác cực âm-dương với DM. "
            "Tượng MẸ ĐẺ — nuôi dưỡng chính thống, học vấn, danh dự."
        ),
        han_viet_explained="Chính = đúng cách, hợp lễ. Ấn = ấn tín mẹ trao.",
        trich_sach=[
            {
                "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
                "noi_dung": (
                    "Can Dương Nhật Chủ gặp can âm khác sinh ra tôi là Chính Ấn, là mẹ đẻ. "
                    "Chính Ấn nói chung là cát thần."
                ),
            },
        ],
        related_concepts=["thiên_ấn", "ấn_tỷ"],
    ),

    "thiên_ấn": ConceptDef(
        key="thiên_ấn",
        ten_han_viet="Thiên Ấn (Kiêu Thần)",
        chu_han="偏印 / 枭神",
        nghia_co_ban=(
            "Thần sinh Day Master, cùng cực âm-dương với DM (lệch). "
            "Tượng MẸ KẾ / MẸ NUÔI. Khi gặp Thực Thần → cướp ăn → gọi Kiêu Thần."
        ),
        han_viet_explained=(
            "**Thiên (偏)** = lệch, không chính. **Kiêu (枭)** = chim cú — cướp ăn của con. "
            "Cùng sinh Tôi nhưng không thuần như Chính Ấn."
        ),
        trich_sach=[
            {
                "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
                "noi_dung": (
                    "Thiên Ấn nói chung là hung thần. Thiên Ấn gặp thực thân thì "
                    "sẽ cướp đoạt nên gọi là Kiêu Thần."
                ),
            },
        ],
        related_concepts=["chính_ấn", "thực_thần", "ấn_tỷ"],
    ),

    "tỷ_kiên": ConceptDef(
        key="tỷ_kiên",
        ten_han_viet="Tỷ Kiên",
        chu_han="比肩",
        nghia_co_ban=(
            "Thần đồng hành Day Master, cùng cực âm-dương. "
            "Tượng ANH EM / ĐỒNG ĐẠO CÙNG TẦN SỐ — trợ thân khi nhược."
        ),
        han_viet_explained="**Tỷ Kiên (比肩)** = sánh vai, ngang vai cùng đường.",
        trich_sach=[
            {
                "sach": "Dự báo theo Tử Bình",
                "noi_dung": (
                    "Nếu can ngày nhược mà gặp được Tỷ Kiên sẽ được trợ giúp thân; "
                    "Tài, Quan nhiều nhờ Tỷ Kiên giúp cho thân khỏi mất của."
                ),
            },
        ],
        related_concepts=["kiếp_tài", "ấn_tỷ"],
    ),

    "kiếp_tài": ConceptDef(
        key="kiếp_tài",
        ten_han_viet="Kiếp Tài",
        chu_han="劫财",
        nghia_co_ban=(
            "Thần đồng hành Day Master nhưng KHÁC CỰC âm-dương. "
            "Tượng đồng đạo CÓ thể đoạt tiền của mình — trợ thân nhưng cẩn thận."
        ),
        han_viet_explained="**Kiếp (劫)** = cướp. **Tài (财)** = tiền của. Đồng đạo nhưng có thể cướp Tài.",
        trich_sach=[
            {
                "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
                "noi_dung": (
                    "Can Âm gặp tôi Dương, can Dương gặp tôi Âm là Kiếp Tài; "
                    "can âm gặp tôi Âm, can dương gặp tôi Dương là Ngang Vai (Tỷ Kiên)."
                ),
            },
        ],
        related_concepts=["tỷ_kiên", "ấn_tỷ", "tài"],
    ),

    # ═══ THẦN ÁP LỰC ═══

    "quan_sát": ConceptDef(
        key="quan_sát",
        ten_han_viet="Quan Sát",
        chu_han="官杀",
        nghia_co_ban=(
            "Nhóm thần KHẮC Day Master: Chính Quan (cấp trên hợp lễ) + "
            "Thất Sát (kẻ cường, áp lực mạnh). Day Master nhược thì kỵ, vượng thì cần."
        ),
        han_viet_explained="**Quan (官)** = chức danh. **Sát (杀)** = giết, áp đảo.",
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "dong": 1683,
                "noi_dung": (
                    "Nhật Chủ suy yếu, trong trụ Quan Sát thừa vượng. Tỷ Kiếp trợ "
                    "Nhật Chủ sẽ gây phản khắc vô tình; không bằng Ấn Thụ hóa Quan Sát."
                ),
            },
        ],
        related_concepts=["chính_quan", "thất_sát", "ấn", "tài"],
    ),

    "tài": ConceptDef(
        key="tài",
        ten_han_viet="Tài",
        chu_han="财",
        nghia_co_ban=(
            "Nhóm thần Day Master KHẮC: Chính Tài (vợ chính, tiền chính đáng) + "
            "Thiên Tài (vợ lẽ, tiền lệch). Cần Day Master mạnh để gánh Tài."
        ),
        han_viet_explained="**Tài (财)** = tiền của — Tôi khắc Thổ/Mộc/... được tài.",
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "dong": 1682,
                "noi_dung": (
                    "Nhật Chủ suy nhược, trong trụ Tài Tinh trùng điệp, Ấn Thụ bị khắc "
                    "nên không có gốc để sinh Nhật Chủ. Dụng Tỷ Kiếp trợ Nhật Chủ thì cát."
                ),
            },
        ],
        related_concepts=["chính_tài", "thiên_tài", "ấn", "tỷ_kiên"],
    ),

    "thực_thương": ConceptDef(
        key="thực_thương",
        ten_han_viet="Thực Thương",
        chu_han="食伤",
        nghia_co_ban=(
            "Nhóm thần Day Master SINH RA: Thực Thần (con cái dịu) + "
            "Thương Quan (sáng tạo, phát tiết mạnh). Tiết khí ra ngoài."
        ),
        han_viet_explained=(
            "**Thực (食)** = ăn, dưỡng. **Thương (伤)** = thương tổn — vì khắc Quan."
        ),
        trich_sach=[
            {
                "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa)",
                "noi_dung": (
                    "Nhật Can yếu mà thực thương mạnh thì Chính Ấn chống lại thương, thực."
                ),
            },
        ],
        related_concepts=["thực_thần", "thương_quan", "ấn", "tài"],
    ),

    # ═══ CƯỜNG ĐỘ DAY MASTER ═══

    "hư_phù": ConceptDef(
        key="hư_phù",
        ten_han_viet="Hư Phù",
        chu_han="虚浮",
        nghia_co_ban=(
            "Day Master 'có vẻ' mạnh trên Thiên Can nhưng KHÔNG có gốc trong Địa Chi. "
            "Khí rỗng, gặp khắc dễ vỡ. Trái với THÔNG CĂN."
        ),
        han_viet_explained="**Hư (虚)** = rỗng. **Phù (浮)** = nổi, không có rễ.",
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "noi_dung": (
                    "Nhật Chủ thông căn = bồi thân THẬT. Hư phù = thân 'có vẻ' mạnh "
                    "trên giấy (đếm tỉ kiếp lộ) nhưng thực ra rỗng — gặp khắc dễ vỡ."
                ),
            },
        ],
        related_concepts=["thông_căn", "lộc_vượng", "kho_mộ"],
    ),

    "thông_căn": ConceptDef(
        key="thông_căn",
        ten_han_viet="Thông Căn",
        chu_han="通根",
        nghia_co_ban=(
            "Day Master có GỐC trong Địa Chi — qua Lộc, Trường Sinh, Kho Mộ, "
            "hoặc chi cùng hành. Khí THẬT, có nền tảng."
        ),
        han_viet_explained="**Thông (通)** = xuyên. **Căn (根)** = rễ — Can xuyên xuống Chi tìm rễ.",
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "noi_dung": "Thiên Can phải có gốc ở Địa Chi mới VƯỢNG.",
            },
        ],
        related_concepts=["hư_phù", "lộc_vượng", "trường_sinh"],
    ),

    "lâm_quan": ConceptDef(
        key="lâm_quan",
        ten_han_viet="Lâm Quan",
        chu_han="临官",
        nghia_co_ban=(
            "Vị trí 12 Trường Sinh — khí của Can đạt đến vị trí 'lên chức', RẤT MẠNH. "
            "Còn gọi LỘC."
        ),
        han_viet_explained="**Lâm (临)** = đến. **Quan (官)** = chức — khí đạt chức cao.",
        trich_sach=[
            {
                "sach": "Dự báo theo Tử Bình",
                "noi_dung": (
                    "Can Ngày Giáp/Ất gặp chi tháng Dần/Mão = LÂM QUAN VƯỢNG. "
                    "Bính/Đinh tháng Tỵ/Ngọ. Mậu/Kỷ tháng Tỵ/Ngọ hoặc Thìn/Tuất/Sửu/Mùi. "
                    "Canh/Tân tháng Thân/Dậu. Nhâm/Quý tháng Hợi/Tý."
                ),
            },
        ],
        related_concepts=["đế_vượng", "trường_sinh", "12_trường_sinh"],
    ),

    "đế_vượng": ConceptDef(
        key="đế_vượng",
        ten_han_viet="Đế Vượng",
        chu_han="帝旺",
        nghia_co_ban="Vị trí 12 Trường Sinh — khí của Can ở ĐỈNH CAO. Mạnh nhất.",
        han_viet_explained="**Đế (帝)** = vua. **Vượng (旺)** = thịnh — khí đỉnh cao như vua.",
        related_concepts=["lâm_quan", "12_trường_sinh"],
    ),

    "bệnh": ConceptDef(
        key="bệnh",
        ten_han_viet="Bệnh",
        chu_han="病",
        nghia_co_ban="Vị trí 12 Trường Sinh — khí của Can SUY BỆNH, yếu.",
        han_viet_explained="**Bệnh (病)** = ốm, khí đang suy yếu.",
        related_concepts=["tử", "tuyệt", "12_trường_sinh"],
    ),

    # ═══ DỤNG THẦN + CÁCH ═══

    "dụng_thần": ConceptDef(
        key="dụng_thần",
        ten_han_viet="Dụng Thần",
        chu_han="用神",
        nghia_co_ban=(
            "Thần CHÍNH cần dùng để cân bằng lá số. Day Master vượng → tiết, "
            "nhược → phù. Tìm đúng Dụng Thần là cốt lõi Tử Bình."
        ),
        han_viet_explained="**Dụng (用)** = dùng. **Thần (神)** = năng lượng — thần để dùng.",
        related_concepts=["hỉ_thần", "kỵ_thần", "phù_ức"],
    ),

    "hỉ_thần": ConceptDef(
        key="hỉ_thần",
        ten_han_viet="Hỉ Thần",
        chu_han="喜神",
        nghia_co_ban="Thần hỗ trợ Dụng Thần. Cát.",
        han_viet_explained="**Hỉ (喜)** = mừng.",
        related_concepts=["dụng_thần", "kỵ_thần"],
    ),

    "kỵ_thần": ConceptDef(
        key="kỵ_thần",
        ten_han_viet="Kỵ Thần",
        chu_han="忌神",
        nghia_co_ban="Thần phá Dụng Thần. Hung. Phải tránh.",
        han_viet_explained="**Kỵ (忌)** = kiêng.",
        related_concepts=["dụng_thần", "hỉ_thần"],
    ),

    "phù_ức": ConceptDef(
        key="phù_ức",
        ten_han_viet="Phù Ức",
        chu_han="扶抑",
        nghia_co_ban=(
            "Paradigm cốt Tử Bình: nhược thì PHÙ (nâng), vượng thì ỨC (chế). "
            "Cân bằng là mục tiêu."
        ),
        han_viet_explained="**Phù (扶)** = nâng. **Ức (抑)** = chế.",
        trich_sach=[
            {
                "sach": "Trích Thiên Tủy bình chú",
                "dong": 1676,
                "noi_dung": (
                    "Trợ thì dùng Tỷ Kiếp, sinh thì dùng Ấn Thụ. Điều là suy mà có khi "
                    "trợ lại hung, sinh thì được cát; hoặc trợ thì được cát, sinh lại hung họa."
                ),
            },
        ],
        related_concepts=["dụng_thần", "ấn_tỷ", "vượng_suy"],
    ),

    "phù_thân": ConceptDef(
        key="phù_thân",
        ten_han_viet="Phù Thân",
        chu_han="扶身",
        nghia_co_ban="Nâng đỡ Day Master khi nhược. Dùng Ấn Tỷ.",
        related_concepts=["phù_ức", "ấn_tỷ"],
    ),

    "tiết_khí": ConceptDef(
        key="tiết_khí",
        ten_han_viet="Tiết Khí",
        chu_han="泄气",
        nghia_co_ban=(
            "Khi Day Master vượng quá → cần xả khí qua Thực Thương "
            "(con cháu sinh ra) hoặc Tài (Tôi khắc)."
        ),
        han_viet_explained="**Tiết (泄)** = xả. **Khí (气)** = năng lượng.",
        related_concepts=["thực_thương", "tài", "phù_ức"],
    ),

    # ═══ THUẬT NGỮ KHÁC ═══

    "vượng_suy": ConceptDef(
        key="vượng_suy",
        ten_han_viet="Vượng Suy",
        chu_han="旺衰",
        nghia_co_ban=(
            "Đánh giá Day Master mạnh hay yếu — gốc của mọi luận giải Tử Bình. "
            "Vượng = mạnh, Suy = yếu."
        ),
        han_viet_explained="**Vượng (旺)** = thịnh. **Suy (衰)** = giảm.",
        related_concepts=["thông_căn", "phù_ức", "12_trường_sinh"],
    ),

    "12_trường_sinh": ConceptDef(
        key="12_trường_sinh",
        ten_han_viet="12 Trường Sinh",
        chu_han="十二长生",
        nghia_co_ban=(
            "12 giai đoạn vòng đời khí của Thiên Can theo Địa Chi: "
            "Trường Sinh → Mộc Dục → Quan Đới → Lâm Quan → Đế Vượng → Suy → "
            "Bệnh → Tử → Mộ → Tuyệt → Thai → Dưỡng."
        ),
        han_viet_explained=(
            "**Trường Sinh (长生)** = sinh ra. **Đế Vượng** = đỉnh cao. **Tuyệt** = mất."
        ),
        trich_sach=[
            {
                "sach": "Dự đoán Tứ Trụ (Thiệu Vĩ Hoa) p730",
                "noi_dung": (
                    "Sinh ngày Giáp tháng Tý là LÂM QUAN. Sinh tháng Thân là TUYỆT. "
                    "Mười hai giai đoạn tượng trưng cho khí của mười hai tháng trong năm."
                ),
            },
        ],
        related_concepts=["lâm_quan", "đế_vượng", "bệnh", "tuyệt"],
    ),

    "đắc_lệnh": ConceptDef(
        key="đắc_lệnh",
        ten_han_viet="Đắc Lệnh",
        chu_han="得令",
        nghia_co_ban=(
            "Day Master sinh đúng vào tháng cùng hành — được THÁNG SINH ủng hộ. "
            "Vd Giáp Mộc sinh tháng Dần/Mão = đắc lệnh."
        ),
        han_viet_explained="**Đắc (得)** = được. **Lệnh (令)** = mệnh lệnh của tháng.",
        related_concepts=["lâm_quan", "vượng_suy"],
    ),

    "nguyệt_lệnh": ConceptDef(
        key="nguyệt_lệnh",
        ten_han_viet="Nguyệt Lệnh",
        chu_han="月令",
        nghia_co_ban="Mệnh lệnh của tháng sinh — chi tháng quyết định khí thế Day Master.",
        han_viet_explained="**Nguyệt (月)** = tháng. **Lệnh (令)** = mệnh lệnh.",
        related_concepts=["đắc_lệnh", "vượng_suy"],
    ),

    "thông_quan": ConceptDef(
        key="thông_quan",
        ten_han_viet="Thông Quan",
        chu_han="通关",
        nghia_co_ban=(
            "Khi 2 thần xung đột, thần thứ 3 đứng giữa hòa giải. "
            "Vd Tài Quan xung Ấn Tỷ → Ấn-Tỷ giữa hòa."
        ),
        han_viet_explained="**Thông (通)** = thông. **Quan (关)** = cửa ải.",
        related_concepts=["xung_khắc"],
    ),

    "nhật_chủ": ConceptDef(
        key="nhật_chủ",
        ten_han_viet="Nhật Chủ",
        chu_han="日主",
        nghia_co_ban=(
            "Thiên Can của ngày sinh = CHÍNH ANH/BẢN THÂN trong lá số. "
            "Day Master tiếng Anh."
        ),
        han_viet_explained="**Nhật (日)** = ngày. **Chủ (主)** = chủ.",
        related_concepts=["day_master", "tứ_trụ"],
    ),

    "thiên_nguyên_khí": ConceptDef(
        key="thiên_nguyên_khí",
        ten_han_viet="Thiên Nguyên Khí",
        chu_han="天元气",
        nghia_co_ban=(
            "Khí gốc trời ban — bẩm sinh không đổi. Trong Hà Lạc = quẻ Tiên Thiên + Niên Mệnh."
        ),
        related_concepts=["niên_mệnh", "đắc_thể"],
        iron_rule_link="Iron Rule #6 (Tử Vi đồng dạng)",
    ),

    "đức_năng_thắng_số": ConceptDef(
        key="đức_năng_thắng_số",
        ten_han_viet="Đức Năng Thắng Số",
        chu_han="德能胜数",
        nghia_co_ban=(
            "Đức + hành động của con người CÓ THỂ thắng được số mệnh. "
            "Paradigm cốt — số chỉ là XÁC SUẤT, không phải định mệnh."
        ),
        trich_sach=[
            {
                "sach": "Hoàng Tuấn (Lý Thuyết Tượng Số) p37",
                "noi_dung": (
                    "Số là xác suất, không phải định mệnh. Đức năng thắng số — "
                    "hành động đạo đức của con người có thể đổi được số."
                ),
            },
        ],
        iron_rule_link="Iron Rule #4 + #6 (cận đại confirm)",
        related_concepts=["đồng_dạng_học"],
    ),
}


def glossary_explain(key: str, depth: str = "full") -> dict | None:
    """Lookup thuật ngữ. depth: 'tooltip' (1 câu) / 'full' (toàn bộ)."""
    cd = GLOSSARY.get(key.lower().replace(" ", "_"))
    if not cd:
        return None
    if depth == "tooltip":
        return {
            "ten": cd.ten_han_viet,
            "chu_han": cd.chu_han,
            "nghia": cd.nghia_co_ban,
        }
    return cd.to_dict()


def render_concept_markdown(key: str) -> str:
    """Render 1 thuật ngữ thành chùm ánh sáng markdown."""
    cd = GLOSSARY.get(key.lower().replace(" ", "_"))
    if not cd:
        return f"_(Chưa có định nghĩa cho '{key}')_"

    lines = [f"### 💡 **{cd.ten_han_viet}** ({cd.chu_han})\n"]
    lines.append(f"**Nghĩa:** {cd.nghia_co_ban}\n")
    if cd.han_viet_explained:
        lines.append(f"**Chữ Hán:** {cd.han_viet_explained}\n")
    if cd.trich_sach:
        lines.append("**📖 Trích sách:**")
        for ts in cd.trich_sach:
            dong_str = f" (dòng {ts['dong']})" if ts.get("dong") else ""
            lines.append(f"> _{ts['noi_dung']}_  ")
            lines.append(f"> — **{ts['sach']}**{dong_str}\n")
    if cd.related_concepts:
        lines.append(f"**Liên quan:** {', '.join(cd.related_concepts)}\n")
    if cd.iron_rule_link:
        lines.append(f"🪷 _{cd.iron_rule_link}_\n")
    return "\n".join(lines)


def auto_highlight_text(text: str, depth: str = "tooltip") -> list[dict]:
    """Auto-detect keyword trong text → trả list highlights {keyword, definition}.

    Để frontend render tooltip hover. Match Hán-Việt + variants.
    """
    found = []
    seen = set()
    for key, cd in GLOSSARY.items():
        ten = cd.ten_han_viet
        if ten in text and ten not in seen:
            found.append({
                "keyword": ten,
                "key": key,
                "definition": cd.nghia_co_ban,
                "chu_han": cd.chu_han,
            })
            seen.add(ten)
    return found


def list_all_keys() -> list[str]:
    """List tất cả keys trong glossary."""
    return list(GLOSSARY.keys())
