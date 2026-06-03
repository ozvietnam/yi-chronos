"""Liệu Pháp Tượng Số — sinh dãy số chữa bệnh (paradigm độc đáo từ sách).

Source: "Chữa bệnh theo Chu Dịch" (Lý Ngọc Sơn + Lý Kiện Dân), CHƯƠNG I + II.
Paradigm: đọc nhẩm dãy số tượng quẻ → cộng hưởng vibration với tạng phủ.

⚠️ Paradigm này KHÁC LẠ — nhưng có gốc từ sách thật (đã verified):
- Số tiên thiên Bát Quái: Càn=1, Đoài=2, Ly=3, Chấn=4, Tốn=5, Khảm=6, Cấn=7, Khôn=8
- Mỗi tạng phủ tương ứng 1 quẻ → 1 số
- Số 0 thêm vào (đuôi) = âm khí (tăng hoặc giảm tùy ngữ cảnh)
- Dãy số được đọc nhẩm theo trật tự sinh-khắc

VÍ DỤ trong sách (verified):
- "640" hoặc "40" = Bổ máu Can, dưỡng gân cốt (cho gân cốt yếu)
- "640" = Tư âm tiềm dương (Can-Thận đồng nguồn: 6=Khảm/Thận, 4=Chấn/Can)
- "20.650" = Phấn chấn thận dương (cho lạnh, đau lưng)
- "650.3820" = Bổ thận dương + kiện tỳ hóa thấp
- "260.50" = Bổ thận nạp khí
- "430.20" = Thông can khí an thần
- "003" = Trị Can hỏa làm mắt đỏ
- "3820" = Hỏa sinh Thổ, Thổ sinh Kim — kiện tỳ ích khí

⚠️ Iron Rule: Đây là CÔNG CỤ THIỀN ĐỊNH (đọc nhẩm để tập trung tâm),
KHÔNG phải thuốc thay thế y học hiện đại. Cần đi khám bác sĩ song song.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# Số tiên thiên của 8 quẻ
QUE_SO: dict[str, int] = {
    "Càn": 1, "Đoài": 2, "Ly": 3, "Chấn": 4,
    "Tốn": 5, "Khảm": 6, "Cấn": 7, "Khôn": 8,
}

# Mỗi quẻ chủ tạng nào
QUE_TANG: dict[str, str] = {
    "Càn": "Đại trường (đầu)",
    "Đoài": "Phế",
    "Ly": "Tâm",
    "Chấn": "Can (gân)",
    "Tốn": "Đởm (đùi)",
    "Khảm": "Thận (xương)",
    "Cấn": "Vị",
    "Khôn": "Tỳ (bụng)",
}


# 5 PHƯƠNG PHÁP LẬP SỐ (yếu lĩnh dòng 3309-3312):
# "Bát quái vi thể, ngũ hành vi dụng; Tỷ loại thủ tướng, dĩ tượng định số;
#  biện chứng thi trị, bình hoành âm dương."
PHUONG_PHAP_LAP_SO: list[dict] = [
    {
        "phuong_phap": "1. Theo tượng bát quái (bộ phận cơ thể)",
        "vi_du": "Bệnh ở chân → 4 (Chấn) + 0 trước/sau",
        "case": "Học sinh Lý Viện trẹo gót → 0004000 → 20 phút khỏi",
        "trich_dong": "3181-3198",
    },
    {
        "phuong_phap": "2. Theo lý luận tàng tượng (tạng chủ)",
        "vi_du": "Bệnh về da → 2 (Đoài/Phế) chủ 'bì mao' + 000 → 0002",
        "case": "Nữ giáo sư người Mông mẩn ngứa → 0002 → mấy phút hết ngứa",
        "trich_dong": "3200-3213",
    },
    {
        "phuong_phap": "3. Theo 'quân cự tả sứ' (như đơn thuốc Đông y)",
        "vi_du": "Can dương tăng (đau đầu, mất ngủ) → 640.30.80",
        "case": "6=quân (Khảm, mát thận âm) + 4=cự (Chấn, bổ Can âm) + 30=tả (Ly, an thần) + 80=sứ (Khôn, kiện tỳ)",
        "trich_dong": "3215-3246",
    },
    {
        "phuong_phap": "4. Theo kinh lạc tuần hành",
        "vi_du": "Bệnh mũi → 07 (Cấn → Vị kinh → mũi)",
        "case": "Bệnh nhân Lăng viêm mũi → 07 → 1 ngày khỏi",
        "trich_dong": "3248-3255",
    },
    {
        "phuong_phap": "5. Theo quy luật ngũ hành sinh khắc",
        "vi_du": "650.30.820 = ôn thông thận dương + kiện tỳ ích khí",
        "case": "6 (Thủy) → 5 (Mộc) → 3 (Hỏa) → 8 (Thổ) → 2 (Kim) → vòng tròn sinh khắc",
        "trich_dong": "3259-3287",
    },
]

# QUY TẮC SỐ 0 (dòng 3144-3158, 3279-3287):
QUY_TAC_SO_0: dict = {
    "y_nghia": "Số 0 = khí hỗn nguyên thái cực, làm tăng năng lượng sóng tin tức để thông kinh khí âm dương.",
    "quy_tac": [
        "0 chẵn (00, 0000) = thiên ÂM (lạnh, làm dịu)",
        "0 lẻ (0, 000) = thiên ÔN DƯƠNG (ấm, kích hoạt)",
        "0 đặt TRƯỚC tượng số = hơi thiên về ÂM (phòng tổn âm)",
        "0 đặt SAU tượng số = hơi thiên về DƯƠNG (đẩy khí ra)",
    ],
    "vi_du": [
        "0002 (000 trước 2): trị mẩn ngứa - thiên âm để giữ âm khi sơ phong",
        "20.0000 (0000 sau): sơ giải dương",
        "003 = trị Can hỏa làm mắt đỏ (00 thủy khắc hỏa)",
    ],
}

# 6 LƯU Ý KHI NIỆM (dòng 3316-3377):
LUU_Y_KHI_NIEM: list[str] = [
    "Niệm KHÔNG cảm thấy gì → vẫn tiếp tục (tác dụng vẫn có). Cảm ứng dễ chịu (mát đầu, nhẹ thân) = đúng số. Khó chịu ở đầu/dạ dày/tim = lập số sai → đổi số.",
    "Không câu nệ thời gian / địa điểm / tư thế: đi/ngồi/nằm đều niệm được. Tốt nhất: trước khi ngủ + sau thức giấc + lúc thả lỏng nhập tĩnh.",
    "Đã khỏi vẫn tiếp tục niệm để củng cố + tăng cường sức khỏe.",
    "Trong khi niệm, năng lượng tin tức xung kích vào ô bệnh → chứng trạng có thể tạm thời nặng lên. Chỉ cần đầu/dạ dày/tim không khó chịu là OK, cứ niệm tiếp.",
    "Có thể phối hợp châm cứu, hoặc dùng riêng rẽ.",
    "Tuỳ bệnh tình điều chỉnh số: nếu thấy dễ chịu thì giữ, khó chịu thì đổi.",
]

# CHỐNG CHỈ ĐỊNH (dòng 3373-3377):
CHONG_CHI_DINH: str = (
    "⛔ CẤM dùng cho: người tinh thần không bình thường (rối loạn tâm thần) + người trí nhớ kém."
)


# Công thức tượng số chuẩn (verified từ sách)
CONG_THUC_TUONG_SO: list[dict] = [
    {
        "tuong_so": "640",
        "y_nghia": "Bổ máu Can, dưỡng gân cốt",
        "phan_tich": "6=Khảm/Thận, 4=Chấn/Can, 0=âm khí. Can-Thận đồng nguồn → tư âm dưỡng huyết Can.",
        "chi_dinh": [
            "Gân yếu, chuột rút",
            "Đứt gân, đầu gối yếu",
            "Móng giòn dễ gãy",
            "Chân tay run rẩy",
            "Đau lưng + gối yếu (kèm thận hư)",
        ],
        "trich_sach": "Dòng 2426: 'Những chứng bệnh do Can không đủ máu, nói chung lấy tượng là 640 hoặc 40'",
    },
    {
        "tuong_so": "720.650.380",
        "y_nghia": "ĐAU KHỚP GỐI mạn tính — ôn bổ dương Tỳ-Thận, hàn thấp tự mất",
        "phan_tich": (
            "3 nguyên: 720 (tác động khớp gối) + 650 (chấn thận dương) + 380 (ôn tỳ táo thấp). "
            "7=Cấn(núi/khớp), 2=Đoài sơ giải cục bộ, 6=Khảm thận, 5=Tốn mộc, 3=Ly hỏa, 8=Khôn thổ."
        ),
        "chi_dinh": [
            "Đau khớp gối mạn tính",
            "Đau khớp lan tỏa, hàn thấp",
            "Thoái hóa khớp tuổi trung niên",
            "Đau khớp sau chấn thương (như đứt gân đã mổ)",
        ],
        "trich_sach": (
            "Case 71 (dòng 6325): Bà Trương 53t đau 2 khớp gối từ 1992, đã chữa nhiều không khỏi. "
            "Niệm 720.650.380 + nhĩ áp 3 tháng → khỏi + tóc bạc đen lại + sinh khí tăng."
        ),
    },
    {
        "tuong_so": "0004000",
        "y_nghia": "Trẹo gót / khớp bàn chân — tản ứ hoạt huyết, tiêu sưng",
        "phan_tich": (
            "4=Chấn (chân) ở giữa, 000 trước + 000 sau để tăng lợi tiểu + tiêu sưng + "
            "tản ứ hoạt huyết. Số 0 chẵn = thiên âm."
        ),
        "chi_dinh": [
            "Trẹo khớp gót / khớp cổ chân",
            "Sưng tấy chân sau chấn thương",
            "Đau bộ phận chân do tổn thương",
            "Bong gân chân cấp tính",
        ],
        "trich_sach": (
            "Case học sinh Lý Viện (dòng 3192): trẹo gót sưng tấy không đi nổi. "
            "Niệm 0004000 → 20 phút thấy lạnh→nóng→dễ chịu, 4 ngày hết sưng."
        ),
    },
    {
        "tuong_so": "640.30.80",
        "y_nghia": "Đau đầu, mất ngủ, buồn bực — Can dương hơi tăng",
        "phan_tich": (
            "4 nguyên 'quân cự tả sứ': 640 (tư âm tiềm dương) + 30 (Ly an thần) + 80 (Khôn kiện tỳ). "
            "6=quân, 4=cự, 3=tả, 8=sứ."
        ),
        "chi_dinh": [
            "Đau đầu kéo dài (do Can dương lên)",
            "Mất ngủ buồn bực",
            "Cao huyết áp nhẹ",
            "Hay cáu gắt vô cớ",
        ],
        "trich_sach": "Dòng 3241",
    },
    {
        "tuong_so": "650.3820",
        "y_nghia": "Bổ thận dương + kiện tỳ hóa thấp",
        "phan_tich": "650=Tốn-Khảm (gió-nước, dương mộc sinh thận thủy), 3820=Ly-Khôn-Đoài (hỏa-thổ-kim sinh khí).",
        "chi_dinh": [
            "Thận dương hư: lạnh tay chân, mệt mỏi, di tiểu nhiều lần",
            "Liệt dương, sinh khí kém",
            "Đau lưng + tứ chi lạnh",
            "Phù toàn thân",
        ],
        "trich_sach": "Dòng 2546: '650.3820 có thể kiện tỳ ích khí'",
    },
    {
        "tuong_so": "260.50",
        "y_nghia": "Bổ thận nạp khí (hô hấp ngắn)",
        "phan_tich": "260=Đoài-Khảm-âm (phế kim sinh thận thủy), 50=Tốn-âm (dương mộc tả).",
        "chi_dinh": [
            "Hô hấp ngắn, hen suyễn",
            "Khí hít vào không đủ",
            "Thận không nạp khí",
        ],
        "trich_sach": "Dòng 2569: '260.50 là đoài kim sinh thận thủy, thêm 00 để tả thận khí'",
    },
    {
        "tuong_so": "430.20",
        "y_nghia": "Thông Can khí an thần",
        "phan_tich": "430=Chấn-Ly-âm (mộc sinh hỏa, an tâm thần), 20=Đoài-âm (kim tả Can).",
        "chi_dinh": [
            "Can khí uất, buồn bực không tả",
            "Stress, dễ giận",
            "Kinh nguyệt không đều (nữ)",
            "Mất ngủ do Can uất",
        ],
        "trich_sach": "Dòng 2404: 'Lập tượng số là 430.20 để thông Can khí an thần'",
    },
    {
        "tuong_so": "20.650",
        "y_nghia": "Phấn chấn thận dương (đau lưng + lạnh)",
        "phan_tich": "20=Đoài-âm (kim sinh thủy), 650=Khảm-Tốn-âm (thận-mộc tương sinh).",
        "chi_dinh": [
            "Thận dương hư",
            "Đau lưng kéo dài",
            "Tay chân lạnh",
            "Tinh thần mệt mỏi",
        ],
        "trich_sach": "Dòng 2521: 'Lập tượng số là 20.650'",
    },
    {
        "tuong_so": "3820",
        "y_nghia": "Kiện tỳ ích khí (Hỏa→Thổ→Kim)",
        "phan_tich": "3=Ly/hỏa, 8=Khôn/thổ, 2=Đoài/kim, 0=âm. Chuỗi sinh: hỏa→thổ→kim.",
        "chi_dinh": [
            "Tỳ hư, ăn không ngon",
            "Đầy bụng, phân lỏng",
            "Mệt mỏi không lý do",
            "Cơ nhão",
        ],
        "trich_sach": "Dòng 2547: '3820 là hỏa sinh thổ, thổ sinh kim'",
    },
    {
        "tuong_so": "003",
        "y_nghia": "Trị Can hỏa làm mắt đỏ",
        "phan_tich": "00=âm (thủy), 3=Ly/hỏa. Thủy khắc hỏa.",
        "chi_dinh": [
            "Mắt đỏ sưng",
            "Can hỏa vượng",
            "Đỏ mặt giận dữ",
        ],
        "trich_sach": "Dòng 2450: 'Can hỏa làm mắt đỏ lên hay sưng đỏ là 003'",
    },
]


@dataclass
class TuongSoResult:
    """Kết quả tra tượng số phù hợp."""

    chan_thuong_input: str
    matched_formulas: list[dict]   # Các công thức khớp
    primary_formula: dict          # Công thức ưu tiên nhất
    huong_dan_doc: str             # Hướng dẫn đọc nhẩm
    iron_rule_warning: str         # Cảnh báo Iron Rule

    def to_dict(self) -> dict:
        return asdict(self)


def tim_tuong_so(chan_thuong: str) -> TuongSoResult:
    """Tìm công thức tượng số phù hợp với triệu chứng."""
    ct = chan_thuong.lower()
    matched = []
    for formula in CONG_THUC_TUONG_SO:
        for chi in formula["chi_dinh"]:
            # Loose match — bất cứ keyword chính nào
            chi_lower = chi.lower()
            keywords = [w for w in chi_lower.split() if len(w) >= 3]
            if any(k in ct for k in keywords) or any(c in ct for c in chi_lower.split(",")[0].split()):
                matched.append(formula)
                break

    if not matched:
        # Fallback: nếu có gân/đầu gối → 640
        if any(k in ct for k in ["gân", "đầu gối", "móng", "khớp"]):
            matched.append(CONG_THUC_TUONG_SO[0])  # 640

    # Re-priority: KHỚP + (mạn / kéo dài / thoái hóa / nhiều năm) → ưu tiên 720.650.380
    chronic_keywords = ["mạn", "kéo dài", "thoái hóa", "nhiều năm", "lâu", "đã mổ", "sau mổ"]
    if "khớp" in ct and any(k in ct for k in chronic_keywords):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "720.650.380":
                # Move to front
                matched.insert(0, matched.pop(i))
                break

    # Trẹo / bong gân cấp tính → ưu tiên 0004000
    acute_keywords = ["trẹo", "bong gân", "sưng tấy", "vừa bị", "mới bị"]
    if any(k in ct for k in acute_keywords):
        for i, f in enumerate(matched):
            if f["tuong_so"] == "0004000":
                matched.insert(0, matched.pop(i))
                break

    primary = matched[0] if matched else CONG_THUC_TUONG_SO[0]

    huong_dan = (
        "**Cách đọc nhẩm:**\n"
        f"1. Tâm tịnh, ngồi thẳng, mắt khép nhẹ hoặc nhìn xuôi\n"
        f"2. Đọc nhẩm dãy số **{primary['tuong_so']}** trong đầu (không cần nói ra)\n"
        f"3. Mỗi lần đọc cho hơi thở 1 nhịp. Đếm 36-108 lần/buổi\n"
        f"4. 2-3 buổi/ngày, vào giờ tạng tương ứng vượng nhất\n"
        f"5. Không cần ép — đọc với tâm thoải mái, không phải 'để khỏi bệnh' mà 'để tĩnh tâm'"
    )

    return TuongSoResult(
        chan_thuong_input=chan_thuong,
        matched_formulas=matched,
        primary_formula=primary,
        huong_dan_doc=huong_dan,
        iron_rule_warning=(
            "⚠️ **Paradigm CỔ — KHÔNG thay thế y học hiện đại.** "
            "Liệu pháp tượng số là CÔNG CỤ THIỀN ĐỊNH — đọc nhẩm để tập trung tâm + "
            "cộng hưởng paradigm Bát Quái. Vẫn cần đi khám bác sĩ, theo phác đồ. "
            "Em không khuyến nghị bỏ thuốc Tây hoặc Đông y chính thống."
        ),
    )


def render_tuong_so_markdown(result: TuongSoResult) -> str:
    if not result.matched_formulas:
        return "_(Chưa tìm thấy công thức phù hợp)_"

    lines = [
        f"## 🔢 Liệu pháp Tượng Số (paradigm cổ độc đáo)\n",
        f"_Triệu chứng:_ **{result.chan_thuong_input}**\n",
        f"### 🎯 Tượng số ưu tiên: **{result.primary_formula['tuong_so']}**\n",
        f"**Ý nghĩa:** {result.primary_formula['y_nghia']}\n",
        f"**Phân tích quẻ:** {result.primary_formula['phan_tich']}\n",
        f"**Chỉ định:**",
    ]
    for c in result.primary_formula['chi_dinh']:
        lines.append(f"- {c}")
    lines.append(f"\n**Trích sách:** _{result.primary_formula['trich_sach']}_\n")
    lines.append(result.huong_dan_doc)

    if len(result.matched_formulas) > 1:
        lines.append("\n### Công thức khác liên quan")
        for f in result.matched_formulas[1:]:
            lines.append(f"- **{f['tuong_so']}**: {f['y_nghia']}")

    # 5 phương pháp lập số
    lines.append("\n### 📐 5 Phương pháp lập số (yếu lĩnh chương I)")
    for pp in PHUONG_PHAP_LAP_SO:
        lines.append(f"\n**{pp['phuong_phap']}**")
        lines.append(f"- Ví dụ: {pp['vi_du']}")
        lines.append(f"- Case: _{pp['case']}_")

    # Quy tắc số 0
    lines.append("\n### 🔢 Quy tắc số 0")
    lines.append(f"_{QUY_TAC_SO_0['y_nghia']}_\n")
    for rule in QUY_TAC_SO_0['quy_tac']:
        lines.append(f"- {rule}")

    # 6 lưu ý
    lines.append("\n### 📋 6 Lưu ý khi niệm (cốt từ sách)")
    for i, ly in enumerate(LUU_Y_KHI_NIEM, 1):
        lines.append(f"{i}. {ly}")

    lines.append(f"\n{CHONG_CHI_DINH}\n")
    lines.append(f"\n---\n\n{result.iron_rule_warning}")
    return "\n".join(lines)


def get_paradigm_overview() -> dict:
    """Trả về paradigm tổng quan để frontend display."""
    return {
        "yeu_linh": (
            "Bát quái vi thể, ngũ hành vi dụng; "
            "Tỷ loại thủ tướng, dĩ tượng định số; "
            "Biện chứng thi trị, bình hoành âm dương."
        ),
        "yeu_linh_giai": (
            "Bát quái là thể (gốc), ngũ hành là dụng (cách dùng). "
            "Lấy tượng theo phân loại, dùng tượng để định số. "
            "Biện chứng để chữa trị, cân bằng âm dương."
        ),
        "phuong_phap_lap_so": PHUONG_PHAP_LAP_SO,
        "quy_tac_so_0": QUY_TAC_SO_0,
        "luu_y_khi_niem": LUU_Y_KHI_NIEM,
        "chong_chi_dinh": CHONG_CHI_DINH,
        "source": "Chữa bệnh theo Chu Dịch — Lý Ngọc Sơn + Lý Kiện Dân, chương I (dòng 3100-3380)",
    }
