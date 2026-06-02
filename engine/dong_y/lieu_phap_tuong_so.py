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

    lines.append(f"\n---\n\n{result.iron_rule_warning}")
    return "\n".join(lines)
