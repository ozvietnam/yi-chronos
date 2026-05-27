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
        }
    if SINH_CYCLE.get(hanh_A) == hanh_B:
        return {
            "relation": "A_sinh_B",
            "label_vi": f"{hanh_A} sinh {hanh_B}",
            "paradigm_note": f"{hanh_A} (A) nuôi {hanh_B} (B) — B được lợi từ A.",
        }
    if SINH_CYCLE.get(hanh_B) == hanh_A:
        return {
            "relation": "B_sinh_A",
            "label_vi": f"{hanh_B} sinh {hanh_A}",
            "paradigm_note": f"{hanh_B} (B) nuôi {hanh_A} (A) — A được lợi từ B.",
        }
    if KHAC_CYCLE.get(hanh_A) == hanh_B:
        return {
            "relation": "A_khac_B",
            "label_vi": f"{hanh_A} khắc {hanh_B}",
            "paradigm_note": f"{hanh_A} (A) áp {hanh_B} (B) — B bị áp lực từ A.",
        }
    if KHAC_CYCLE.get(hanh_B) == hanh_A:
        return {
            "relation": "B_khac_A",
            "label_vi": f"{hanh_B} khắc {hanh_A}",
            "paradigm_note": f"{hanh_B} (B) áp {hanh_A} (A) — A bị áp lực từ B.",
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
