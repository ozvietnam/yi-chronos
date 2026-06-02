"""Cha Mẹ (父母) — luận về cha mẹ từ Tứ Trụ.

Paradigm Thiệu Vĩ Hoa Tập 2 Chương 12-13:
- Cha = Tỉ Kiếp cướp Tài → Cha (vì Tài là Mẹ → cướp Tài = phạm Cha)
- Mẹ = Ấn Tinh (sinh thân)
- Trụ Năm + Trụ Tháng = cung cha mẹ
- Tỉ Kiếp trùng trùng → khắc Cha
- Tài nhiều quá → khắc Mẹ (vì Tài đoạt Ấn)
- Tháng khắc Năm → tổn thương cha mẹ
- Phụ mẫu gặp Mộ Địa → mất cha mẹ sớm

⚠️ Iron Rule #4+6: KHÔNG predict tĩnh "cha anh sẽ chết năm X". Chỉ output
TÍN HIỆU cấu trúc → khuyên cách chăm sóc + sống có hiếu.
"""

from __future__ import annotations

from .constants import BRANCH_ELEMENT


def luan_cha_me(state: dict) -> dict:
    """Phân tích cấu trúc cha mẹ từ Tứ Trụ.

    Returns:
      {
        "patterns": list of detected patterns,
        "narrative": tổng hợp,
        "paradigm_guard": notice không predict tĩnh
      }
    """
    pillars = state.get("tu_tru", {}).get("pillars", {})
    if not pillars:
        return {"patterns": [], "narrative": "", "paradigm_guard": ""}

    counts = state.get("ngu_hanh", {}).get("counts", {})
    assessment = state.get("ngu_hanh", {}).get("day_master_assessment", {})
    day_element = (assessment.get("day_master_element") or "").lower()

    patterns = []

    # 1. Tỉ Kiếp trùng trùng → khắc Cha
    ti_kiep_count = 0
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        for h in [p.get("stem")] + [h.get("stem") if isinstance(h, dict) else h
                                     for h in (p.get("hidden_stems_thap_than", []) or [])]:
            tt = ""
            stem_tt = p.get("stem_thap_than", "") if h == p.get("stem") else ""
            # Use thap_than annotation if available
            if "Tỉ" in stem_tt or "Kiếp" in stem_tt:
                ti_kiep_count += 1
        # Hidden stems
        for h in p.get("hidden_stems_thap_than", []) or []:
            if isinstance(h, dict):
                tt = h.get("thap_than", "")
                if "Tỉ" in tt or "Kiếp" in tt:
                    ti_kiep_count += 0.5  # less weight for hidden
    if ti_kiep_count >= 3:
        patterns.append({
            "type": "ti_kiep_khac_cha",
            "severity": "high" if ti_kiep_count >= 4 else "medium",
            "narrative": (
                f"**Tỉ Kiếp trùng trùng** ({ti_kiep_count:.1f} units) — "
                f"Thiệu Vĩ Hoa Tập 2 Ch.12: 'Tỉ Kiếp nhiều = cướp Tài = phạm Cha'. "
                "Tín hiệu cấu trúc cảnh báo quan hệ với Cha có thể căng. "
                "KHÔNG predict — anh nên chủ động chăm sóc + dành thời gian cho Cha."
            ),
        })

    # 2. Tài nhiều → khắc Mẹ
    # Find Tài (wealth) role
    tai_total = 0.0
    if day_element:
        from .ngu_hanh import _element_controlling
        # Wealth = element Day Master controls
        wealth_el = _element_controlling(day_element)
        tai_total = counts.get(wealth_el, 0)
    if tai_total >= 4:
        patterns.append({
            "type": "tai_nhieu_khac_me",
            "severity": "high" if tai_total >= 5 else "medium",
            "narrative": (
                f"**Tài nhiều** ({tai_total:.1f}) — Thiệu Vĩ Hoa Tập 2 Ch.12: "
                "'Tài nhiều thì khắc Ấn = phạm Mẹ'. Tín hiệu quan hệ với Mẹ "
                "có thể có khoảng cách. Bổ cứu qua Ấn (đọc sách / học vấn / tâm linh) "
                "để cân bằng + dành thời gian cho Mẹ."
            ),
        })

    # 3. Tháng khắc Năm → tổn thương cha mẹ
    year_el_stem = pillars.get("year", {}).get("stem_element", "").lower()
    month_el_stem = pillars.get("month", {}).get("stem_element", "").lower()
    if year_el_stem and month_el_stem:
        from .ngu_hanh import _element_controlling
        if _element_controlling(month_el_stem) == year_el_stem:
            patterns.append({
                "type": "thang_khac_nam",
                "severity": "medium",
                "narrative": (
                    f"**Tháng khắc Năm** ({month_el_stem.title()} khắc {year_el_stem.title()}) — "
                    "Trụ Tháng (con) áp Trụ Năm (cha mẹ tổ tiên). "
                    "Tín hiệu xa cách / xung đột thế hệ. Bổ cứu qua thái độ tôn kính, "
                    "không phải án định mệnh."
                ),
            })

    paradigm_guard = (
        "⚠️ Paradigm Thiệu Vĩ Hoa: Tử Bình KHÔNG predict 'cha anh sẽ X năm Y'. "
        "Đây chỉ là TÍN HIỆU CẤU TRÚC → khuyên cách chăm sóc + sống có hiếu. "
        "Cha mẹ mạnh khỏe hay không phụ thuộc nhiều yếu tố khác (Tứ Trụ cha mẹ + môi trường + y tế)."
    )

    if not patterns:
        narrative = "Cấu trúc cha mẹ trong Tứ Trụ ổn — không phát hiện pattern khắc / hại rõ rệt."
    else:
        narrative = f"Phát hiện {len(patterns)} tín hiệu liên quan đến cha mẹ trong Tứ Trụ:\n" + \
                    "\n".join(f"- {p['narrative']}" for p in patterns)

    return {
        "patterns": patterns,
        "narrative": narrative,
        "paradigm_guard": paradigm_guard,
    }
