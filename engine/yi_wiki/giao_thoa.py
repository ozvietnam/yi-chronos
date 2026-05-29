"""Giao thoa 2 quẻ — Ngũ hành relation theo paradigm Mai Hoa.

⚠️ Iron Rule #4: KHÔNG output "cát/hung". Chỉ output **CẤU TRÚC** (sinh/khắc/tỉ hoà).

Quan hệ Ngũ hành 5 trạng thái:
- Tỉ hoà (cùng hành): không xung không sinh — bình
- A sinh B: A nuôi B → B được lợi
- A khắc B: A áp B → B bị áp lực
- B sinh A: B nuôi A → A được lợi
- B khắc A: B áp A → A bị áp lực

→ Mỗi trạng thái chỉ là TƯỢNG, KHÔNG phải verdict.
"""
from __future__ import annotations

from engine.yi_wiki.cast import Hexagram


# 8 bát quái → Ngũ hành
BAT_QUAI_NGU_HANH = {
    "Càn": "Kim",
    "Đoài": "Kim",
    "Ly": "Hỏa",
    "Chấn": "Mộc",
    "Tốn": "Mộc",
    "Khảm": "Thủy",
    "Cấn": "Thổ",
    "Khôn": "Thổ",
}

# Sinh: A sinh B nghĩa là A nuôi B (đứng trước)
# Mộc sinh Hỏa → Hỏa sinh Thổ → Thổ sinh Kim → Kim sinh Thủy → Thủy sinh Mộc
SINH_CYCLE = {
    "Mộc": "Hỏa",
    "Hỏa": "Thổ",
    "Thổ": "Kim",
    "Kim": "Thủy",
    "Thủy": "Mộc",
}

# Khắc: A khắc B nghĩa là A áp B
# Mộc khắc Thổ → Thổ khắc Thủy → Thủy khắc Hỏa → Hỏa khắc Kim → Kim khắc Mộc
KHAC_CYCLE = {
    "Mộc": "Thổ",
    "Thổ": "Thủy",
    "Thủy": "Hỏa",
    "Hỏa": "Kim",
    "Kim": "Mộc",
}


# Diễn giải paradigm rich cho từng cặp Ngũ hành (CỐT cho UI)
# A nuôi B / A áp B → ý nghĩa CỤ THỂ cho user, không trừu tượng
NGU_HANH_PARADIGM_RICH = {
    # Tỉ hoà
    ("Mộc","Mộc"): "🌿 2 hành Mộc cùng nhau — đều LỚN LÊN, lan rộng. Hài hoà sinh trưởng.",
    ("Hỏa","Hỏa"): "🔥 2 hành Hỏa cùng nhau — đều BÙNG LÊN, sáng tỏ. Cẩn thận cháy lớn.",
    ("Thổ","Thổ"): "⛰ 2 hành Thổ cùng nhau — đều NÂNG ĐỠ, ổn định. Bình thuận, dày gốc.",
    ("Kim","Kim"): "⚔ 2 hành Kim cùng nhau — đều CƯƠNG TRỰC, cắt gọt. Cẩn thận cứng quá.",
    ("Thủy","Thủy"): "💧 2 hành Thủy cùng nhau — đều CHẢY XUỐNG, thông suốt. Mềm mà vào sâu.",
    # Sinh — A nuôi B (đạo của)
    ("Mộc","Hỏa"): "🌿→🔥 Mộc nuôi Hỏa — sự phát triển dẫn đến bùng sáng. Anh tạo điều kiện cho cái sáng.",
    ("Hỏa","Thổ"): "🔥→⛰ Hỏa nuôi Thổ — sự sáng cháy tạo ra đất (tro). Anh đem nhiệt huyết đắp gốc.",
    ("Thổ","Kim"): "⛰→⚔ Thổ nuôi Kim — đất sinh kim loại. Anh tích đức để nuôi cương trực.",
    ("Kim","Thủy"): "⚔→💧 Kim nuôi Thủy — kim loại sinh nước (luyện). Anh dùng kỷ luật để mở dòng chảy.",
    ("Thủy","Mộc"): "💧→🌿 Thủy nuôi Mộc — nước tưới cây. Anh đem mềm để nuôi sự lớn lên.",
    # Bị sinh — A được B nuôi
    ("Hỏa","Mộc"): "🌿→🔥 Mộc nuôi Hỏa — Anh được nuôi bằng sự phát triển. Có người/việc tạo điều kiện cho Anh bùng lên.",
    ("Thổ","Hỏa"): "🔥→⛰ Hỏa nuôi Thổ — Anh được sự sáng cháy đắp gốc. Nhận năng lượng từ ngoài.",
    ("Kim","Thổ"): "⛰→⚔ Thổ nuôi Kim — Anh được đất nuôi cương trực. Có nền tảng tích lũy.",
    ("Thủy","Kim"): "⚔→💧 Kim nuôi Thủy — Anh được kỷ luật mở dòng. Có khung để chảy.",
    ("Mộc","Thủy"): "💧→🌿 Thủy nuôi Mộc — Anh được mềm tưới. Có nguồn để lớn lên.",
    # Khắc — A áp B
    ("Mộc","Thổ"): "🌿⚡⛰ Mộc khắc Thổ — cây rút chất đất. Anh khai thác/làm hao gốc.",
    ("Thổ","Thủy"): "⛰⚡💧 Thổ khắc Thủy — đất ngăn nước. Anh chặn dòng chảy / kiềm dòng.",
    ("Thủy","Hỏa"): "💧⚡🔥 Thủy khắc Hỏa — nước dập lửa. Anh dập nhiệt / hạ năng lượng.",
    ("Hỏa","Kim"): "🔥⚡⚔ Hỏa khắc Kim — lửa nung chảy kim. Anh dùng nhiệt phá cương.",
    ("Kim","Mộc"): "⚔⚡🌿 Kim khắc Mộc — sắt chặt cây. Anh dùng cương cắt sinh trưởng.",
    # Bị khắc — A bị B áp
    ("Thổ","Mộc"): "🌿⚡⛰ Mộc khắc Thổ — Anh bị rút chất / bị hao. Có người/việc khai thác Anh.",
    ("Thủy","Thổ"): "⛰⚡💧 Thổ khắc Thủy — Anh bị ngăn dòng. Có chỗ chặn không cho chảy.",
    ("Hỏa","Thủy"): "💧⚡🔥 Thủy khắc Hỏa — Anh bị dập nhiệt. Có nước hạ năng lượng Anh.",
    ("Kim","Hỏa"): "🔥⚡⚔ Hỏa khắc Kim — Anh bị nung chảy. Có nhiệt phá cương của Anh.",
    ("Mộc","Kim"): "⚔⚡🌿 Kim khắc Mộc — Anh bị chặt. Có cương cắt sinh trưởng Anh.",
}


def explain_ngu_hanh_rich(hanh_A: str, hanh_B: str) -> str:
    """Diễn giải paradigm cho cặp A-B (A = subject, B = đối tượng).

    Returns rich paradigm-aware string cho UI hiển thị.
    """
    return NGU_HANH_PARADIGM_RICH.get(
        (hanh_A, hanh_B),
        f"{hanh_A} ↔ {hanh_B} — quan hệ chưa định nghĩa rõ.",
    )


def ngu_hanh_relation(hanh_A: str, hanh_B: str) -> dict:
    """Quan hệ Ngũ hành A → B.

    Returns:
        {
            "relation": "ti_hoa" | "A_sinh_B" | "A_khac_B" | "B_sinh_A" | "B_khac_A",
            "label_vi": str,
            "paradigm_note": str,
        }
    """
    if hanh_A == hanh_B:
        return {
            "relation": "ti_hoa",
            "label_vi": f"{hanh_A}-{hanh_B} tỉ hoà",
            "paradigm_note": "2 hành cùng nhau — không xung không sinh, bình thuận.",
            "paradigm_rich": explain_ngu_hanh_rich(hanh_A, hanh_B),
        }
    if SINH_CYCLE.get(hanh_A) == hanh_B:
        return {
            "relation": "A_sinh_B",
            "label_vi": f"{hanh_A} sinh {hanh_B}",
            "paradigm_note": f"{hanh_A} (A) nuôi {hanh_B} (B) — B được lợi từ A.",
            "paradigm_rich": explain_ngu_hanh_rich(hanh_A, hanh_B),
        }
    if SINH_CYCLE.get(hanh_B) == hanh_A:
        return {
            "relation": "B_sinh_A",
            "label_vi": f"{hanh_B} sinh {hanh_A}",
            "paradigm_note": f"{hanh_B} (B) nuôi {hanh_A} (A) — A được lợi từ B.",
            "paradigm_rich": explain_ngu_hanh_rich(hanh_A, hanh_B),
        }
    if KHAC_CYCLE.get(hanh_A) == hanh_B:
        return {
            "relation": "A_khac_B",
            "label_vi": f"{hanh_A} khắc {hanh_B}",
            "paradigm_note": f"{hanh_A} (A) áp {hanh_B} (B) — B bị áp lực từ A.",
            "paradigm_rich": explain_ngu_hanh_rich(hanh_A, hanh_B),
        }
    if KHAC_CYCLE.get(hanh_B) == hanh_A:
        return {
            "relation": "B_khac_A",
            "label_vi": f"{hanh_B} khắc {hanh_A}",
            "paradigm_note": f"{hanh_B} (B) áp {hanh_A} (A) — A bị áp lực từ B.",
            "paradigm_rich": explain_ngu_hanh_rich(hanh_A, hanh_B),
        }
    return {
        "relation": "unknown",
        "label_vi": f"{hanh_A} ↔ {hanh_B}",
        "paradigm_note": "Quan hệ không rõ — cần đọc thủ công.",
    }


def giao_thoa_2_quẻ(quẻ_A: Hexagram, quẻ_B: Hexagram) -> dict:
    """Phân tích giao thoa 2 quẻ ở 3 cấp:
    1. Thể-Thể: thượng quẻ A vs thượng quẻ B
    2. Dụng-Dụng: hạ quẻ A vs hạ quẻ B
    3. Toàn bộ: kết hợp 4 chiều

    Args:
        quẻ_A: thường là quẻ Khởi Sinh / Lưu Niên (cấu trúc gốc Anh)
        quẻ_B: thường là quẻ thời điểm (Lưu Nguyệt / Nhật / Vũ trụ)

    Returns:
        dict với relations + paradigm explanation
    """
    # Hành của 2 quẻ đơn của mỗi quẻ kép
    A_upper = BAT_QUAI_NGU_HANH[quẻ_A.upper_que]
    A_lower = BAT_QUAI_NGU_HANH[quẻ_A.lower_que]
    B_upper = BAT_QUAI_NGU_HANH[quẻ_B.upper_que]
    B_lower = BAT_QUAI_NGU_HANH[quẻ_B.lower_que]

    return {
        "que_A": quẻ_A.name,
        "que_B": quẻ_B.name,
        "the_vs_the": {
            "A_upper": f"{quẻ_A.upper_que}({A_upper})",
            "B_upper": f"{quẻ_B.upper_que}({B_upper})",
            **ngu_hanh_relation(A_upper, B_upper),
        },
        "dung_vs_dung": {
            "A_lower": f"{quẻ_A.lower_que}({A_lower})",
            "B_lower": f"{quẻ_B.lower_que}({B_lower})",
            **ngu_hanh_relation(A_lower, B_lower),
        },
        "the_A_vs_dung_B": {
            "A_upper": f"{quẻ_A.upper_que}({A_upper})",
            "B_lower": f"{quẻ_B.lower_que}({B_lower})",
            **ngu_hanh_relation(A_upper, B_lower),
        },
        "the_B_vs_dung_A": {
            "A_lower": f"{quẻ_A.lower_que}({A_lower})",
            "B_upper": f"{quẻ_B.upper_que}({B_upper})",
            **ngu_hanh_relation(A_lower, B_upper),
        },
        "paradigm_note": (
            "⚠️ Đây là CẤU TRÚC Ngũ hành — KHÔNG phải verdict cát/hung. "
            "Anh đọc paradigm, không phải nhận lệnh."
        ),
    }
