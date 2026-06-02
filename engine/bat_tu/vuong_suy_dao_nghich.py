"""Vượng Suy Điên Đảo (旺衰顛倒) — Nghịch lý vượng-suy của Nhậm Thiết Tiều.

Paradigm Trích Thiên Tủy bình chú Chương 17 Suy Vượng:

> "Đắc lệnh thì luận là vượng, thất lệnh dễ cho là suy, tuy là chí lý,
>  nhưng cũng dễ chết vì sai lầm."

Nhậm Thị bác bỏ thông lệ "đắc lệnh = vượng". Khi 1 hành đạt cực điểm
(thái vượng hoặc cực vượng), nó BIẾN TÍNH:
- Thái vượng → tựa hành KHẮC mình (ngược cực)
- Cực vượng → tựa hành mình SINH (sinh tận)

Tương tự cho suy:
- Thái suy → tựa hành mình SINH (do bị bòn rút)
- Cực suy → tựa hành KHẮC mình (do bị khắc tận)

20 lý lẽ điên đảo này CỰC CỐT — dụng thần phải đảo ngược lý thông thường.

Threshold tạm tính:
- Thái vượng: ≥40% Tứ Trụ
- Cực vượng: ≥50% Tứ Trụ
- Thái suy: ≤10% Tứ Trụ
- Cực suy: ≤5% Tứ Trụ (gần 0)
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


# Map: element → (element it generates, element that controls it)
# Mộc → Hỏa (sinh) → Thổ (khắc bởi Mộc) / Mộc khắc bởi Kim
ELEMENT_GEN: dict[str, str] = {
    "mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc",
}
ELEMENT_CTRL_BY: dict[str, str] = {  # hành nào khắc element này
    "mộc": "kim", "hỏa": "thủy", "thổ": "mộc", "kim": "hỏa", "thủy": "thổ",
}


# 20 lý lẽ Vượng-Suy theo Nhậm Thiết Tiều (Trích Thiên Tủy Chương 17 tr.67)
# Format: (element, state) → (similar_to, suggested_use, paradigm_text)

VUONG_SUY_PARADOX: dict[tuple[str, str], dict] = {
    # --- Thái Vượng (tựa hành khắc mình) ---
    ("mộc", "thai_vuong"): {
        "similar_to": "kim",
        "suggested_use": "hỏa",
        "use_role": "rèn luyện",
        "paradigm": "Mộc thái vượng tựa Kim cứng — mừng được Hỏa rèn luyện",
    },
    ("hỏa", "thai_vuong"): {
        "similar_to": "thủy",
        "suggested_use": "thổ",
        "use_role": "ngăn",
        "paradigm": "Hỏa thái vượng tựa Thủy chảy — mừng Thổ ngăn lại",
    },
    ("thổ", "thai_vuong"): {
        "similar_to": "mộc",
        "suggested_use": "kim",
        "use_role": "khắc",
        "paradigm": "Thổ thái vượng tựa Mộc cứng — mừng gặp Kim khắc",
    },
    ("kim", "thai_vuong"): {
        "similar_to": "hỏa",
        "suggested_use": "thủy",
        "use_role": "cứu",
        "paradigm": "Kim thái vượng tựa Hỏa cháy — mừng gặp Thủy cứu",
    },
    ("thủy", "thai_vuong"): {
        "similar_to": "thổ",
        "suggested_use": "mộc",
        "use_role": "khắc chế",
        "paradigm": "Thủy thái vượng tựa Thổ ngăn — mừng gặp Mộc khắc chế",
    },
    # --- Cực Vượng (tựa hành mình sinh) ---
    ("mộc", "cuc_vuong"): {
        "similar_to": "hỏa",
        "suggested_use": "thủy",
        "use_role": "khắc",
        "paradigm": "Mộc cực vượng tựa Hỏa cháy — mừng gặp Thủy khắc",
    },
    ("hỏa", "cuc_vuong"): {
        "similar_to": "thổ",
        "suggested_use": "mộc",
        "use_role": "khắc",
        "paradigm": "Hỏa cực vượng tựa Thổ — mừng gặp Mộc khắc (Mộc khắc Thổ)",
    },
    ("thổ", "cuc_vuong"): {
        "similar_to": "thủy",
        "suggested_use": "hỏa",
        "use_role": "luyện",
        "paradigm": "Thổ cực vượng tựa Thủy — mừng có Hỏa luyện",
    },
    ("kim", "cuc_vuong"): {
        "similar_to": "thủy",
        "suggested_use": "thổ",
        "use_role": "ngăn",
        "paradigm": "Kim cực vượng tựa Thủy chảy — mừng Thổ ngăn lại",
    },
    ("thủy", "cuc_vuong"): {
        "similar_to": "mộc",
        "suggested_use": "kim",
        "use_role": "khắc",
        "paradigm": "Thủy cực vượng tựa Mộc — mừng gặp Kim khắc",
    },
    # --- Thái Suy (tựa hành mình sinh — bị bòn rút) ---
    ("mộc", "thai_suy"): {
        "similar_to": "thủy",
        "suggested_use": "kim",
        "use_role": "sinh",
        "paradigm": "Mộc thái suy tựa Thủy yếu — cần Kim sinh (Kim sinh Thủy, Thủy sinh Mộc)",
    },
    ("hỏa", "thai_suy"): {
        "similar_to": "mộc",
        "suggested_use": "thủy",
        "use_role": "sinh",
        "paradigm": "Hỏa thái suy tựa Mộc khô — cần Thủy sinh (Thủy sinh Mộc, Mộc sinh Hỏa)",
    },
    ("thổ", "thai_suy"): {
        "similar_to": "hỏa",
        "suggested_use": "mộc",
        "use_role": "sinh",
        "paradigm": "Thổ thái suy tựa Hỏa tắt — cần Mộc sinh (Mộc sinh Hỏa, Hỏa sinh Thổ)",
    },
    ("kim", "thai_suy"): {
        "similar_to": "thổ",
        "suggested_use": "hỏa",
        "use_role": "sinh",
        "paradigm": "Kim thái suy tựa Thổ rời — cần Hỏa sinh (Hỏa sinh Thổ, Thổ sinh Kim)",
    },
    ("thủy", "thai_suy"): {
        "similar_to": "kim",
        "suggested_use": "thổ",
        "use_role": "sinh",
        "paradigm": "Thủy thái suy tựa Kim cứng — cần Thổ sinh (Thổ sinh Kim, Kim sinh Thủy)",
    },
    # --- Cực Suy (tựa hành khắc mình — bị khắc tận) ---
    ("mộc", "cuc_suy"): {
        "similar_to": "thổ",
        "suggested_use": "hỏa",
        "use_role": "sinh thân qua tiết Thổ",
        "paradigm": "Mộc cực suy tựa Thổ — cần Hỏa sinh (sinh khí + tiết Thổ)",
    },
    ("hỏa", "cuc_suy"): {
        "similar_to": "kim",
        "suggested_use": "thổ",
        "use_role": "sinh thân",
        "paradigm": "Hỏa cực suy tựa Kim — cần Thổ sinh (xì hơi Kim + sinh Hỏa)",
    },
    ("thổ", "cuc_suy"): {
        "similar_to": "thủy",
        "suggested_use": "kim",
        "use_role": "sinh thân",
        "paradigm": "Thổ cực suy tựa Thủy — cần Kim sinh (tiết Thủy + sinh Thổ)",
    },
    ("kim", "cuc_suy"): {
        "similar_to": "mộc",
        "suggested_use": "thủy",
        "use_role": "sinh thân",
        "paradigm": "Kim cực suy tựa Mộc — cần Thủy sinh (xì Mộc + sinh Kim)",
    },
    ("thủy", "cuc_suy"): {
        "similar_to": "hỏa",
        "suggested_use": "mộc",
        "use_role": "sinh thân qua Mộc",
        "paradigm": "Thủy cực suy tựa Hỏa — cần Mộc sinh (Mộc tiết Hỏa + sinh Thủy)",
    },
}


def classify_extreme_state(day_element: str, element_counts: dict[str, float]) -> str | None:
    """Xếp loại trạng thái cực của Day Master.

    Returns:
        "thai_vuong" | "cuc_vuong" | "thai_suy" | "cuc_suy" | None (bình thường)
    """
    total = sum(element_counts.values()) or 1
    dm_count = element_counts.get(day_element, 0)
    dm_share = dm_count / total

    # Cũng phải xét hành sinh DM (Ấn Thụ)
    seal_el = None
    for el, gen in ELEMENT_GEN.items():
        if gen == day_element:
            seal_el = el
            break
    seal_share = element_counts.get(seal_el, 0) / total if seal_el else 0

    # Total "supporting" (DM + Ấn)
    support_share = dm_share + seal_share

    if support_share >= 0.65 and dm_share >= 0.35:
        if support_share >= 0.80:
            return "cuc_vuong"
        return "thai_vuong"
    if support_share <= 0.18:
        if support_share <= 0.10:
            return "cuc_suy"
        return "thai_suy"
    return None


def detect_vuong_suy_paradox(day_element: str, element_counts: dict[str, float]) -> dict | None:
    """Detect nếu lá số trigger 1 trong 20 lý lẽ điên đảo.

    Returns dict result or None.
    """
    day_element = (day_element or "").lower()
    if not day_element:
        return None

    state = classify_extreme_state(day_element, element_counts)
    if not state:
        return None

    paradox = VUONG_SUY_PARADOX.get((day_element, state))
    if not paradox:
        return None

    total = sum(element_counts.values()) or 1
    dm_share = element_counts.get(day_element, 0) / total

    state_vi = {
        "thai_vuong": "THÁI VƯỢNG (≥50% Tứ Trụ)",
        "cuc_vuong": "CỰC VƯỢNG (≥75% Tứ Trụ)",
        "thai_suy": "THÁI SUY (≤18%)",
        "cuc_suy": "CỰC SUY (≤10%)",
    }.get(state, state)

    return {
        "day_element": day_element,
        "state": state,
        "state_vi": state_vi,
        "dm_share": round(dm_share, 3),
        "similar_to": paradox["similar_to"],
        "suggested_use": paradox["suggested_use"],
        "use_role": paradox["use_role"],
        "paradigm_text": paradox["paradigm"],
        "narrative": (
            f"**Vượng-Suy Điên Đảo (Trích Thiên Tủy Ch.17)** ⚡⚡⚡\n\n"
            f"Day Master {day_element.title()} đang ở trạng thái **{state_vi}** "
            f"({dm_share*100:.0f}% Tứ Trụ).\n\n"
            f"→ Theo Nhậm Thiết Tiều: {paradox['paradigm']}.\n\n"
            f"**Dụng Thần đề xuất (nghịch logic thông thường)**: **{paradox['suggested_use'].title()}** "
            f"({paradox['use_role']}).\n\n"
            f"⚠️ Đây là 1 trong 20 lý lẽ điên đảo của Trích Thiên Tủy — KHÁC với heuristic vượng-suy "
            f"thông thường. Khi 1 hành đến cực điểm, dụng thần phải đảo ngược."
        ),
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 17 Suy Vượng, tr.66-67",
    }
