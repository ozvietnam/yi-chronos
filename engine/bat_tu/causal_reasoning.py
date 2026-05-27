"""Causal Reasoning Layer — "Vì sao + Liên kết" cho Bát Tự.

Paradigm shift: current `luan_giai.py` LIỆT KÊ trạng thái (Day Master nhược, 4 Tài tinh,
Đại Vận Kỵ Thần). Layer này TRẢ LỜI:
- **Điều gì ảnh hưởng?** (upstream factors)
- **Nguyên nhân vì sao?** (root cause analysis)
- **Liên kết với sự việc nào khác?** (cross-pattern + compound effects)

Method:
1. Cho mỗi finding lớn (DM strength, Tài count, Đại Vận polarity, ...) → trace ngược nguyên nhân
2. Build cross-pattern graph: pattern A reinforces/contradicts pattern B
3. Compound warnings: 2+ patterns cộng dồn → emergent meaning (lớn hơn tổng từng phần)
4. Time-aware: Đại Vận + Lưu Niên kích hoạt latent patterns

Output: dict `causal_reasoning` với 4 sections cho UI render.
"""

from __future__ import annotations

from .constants import (
    BRANCH_ELEMENT,
    BRANCH_HIDDEN_STEMS,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    STEM_ELEMENT,
)


# ─── Helpers ────────────────────────────────────────────────────────────────


def _element_relation_label(a: str, b: str) -> str:
    """Quan hệ ngắn gọn: A sinh B / A khắc B / A bị B khắc / cùng / không."""
    if a == b:
        return "cùng hành"
    if ELEMENT_GENERATES.get(a) == b:
        return f"{a} sinh {b}"
    if ELEMENT_GENERATES.get(b) == a:
        return f"{b} sinh {a}"
    if ELEMENT_CONTROLS.get(a) == b:
        return f"{a} khắc {b}"
    if ELEMENT_CONTROLS.get(b) == a:
        return f"{b} khắc {a}"
    return "không trực tiếp"


def _trace_dm_strength_causes(state: dict) -> dict:
    """Tại sao DM vượng/nhược? Trace chi tháng + drain/support breakdown."""
    pillars = state["tu_tru"]["pillars"]
    dm_stem = state["tu_tru"]["day_master"]["stem"]
    dm_el = state["tu_tru"]["day_master"]["element"]
    dm_assess = state["ngu_hanh"]["day_master_assessment"]
    tag = dm_assess["strength_tag"]
    diff = dm_assess.get("support_score", 0) - dm_assess.get("drain_score", 0)
    month_branch = pillars["month"]["branch"]
    month_el = pillars["month"]["branch_element"]

    causes = []

    # 1. Chi tháng (lệnh tháng) — quan trọng nhất
    rel = _element_relation_label(month_el, dm_el)
    if month_el == dm_el:
        loi_effect = "ĐẮC LỆNH (chi tháng cùng hành DM) → support strongly"
    elif ELEMENT_GENERATES.get(month_el) == dm_el:
        loi_effect = "ĐẮC LỆNH (chi tháng sinh DM) → support"
    elif ELEMENT_GENERATES.get(dm_el) == month_el:
        loi_effect = f"TIẾT KHÍ (DM sinh chi tháng → mất khí cho {month_el})"
    elif ELEMENT_CONTROLS.get(month_el) == dm_el:
        loi_effect = f"BỊ KHẮC (chi tháng {month_el} khắc DM {dm_el})"
    elif ELEMENT_CONTROLS.get(dm_el) == month_el:
        loi_effect = f"HAO KHẮC (DM khắc chi tháng → hao sức)"
    else:
        loi_effect = "không trực tiếp"

    causes.append({
        "factor": "Chi tháng (lệnh tháng)",
        "detail": f"{month_branch} ({month_el})",
        "effect": loi_effect,
        "weight": "CAO" if "ĐẮC" in loi_effect or "TIẾT" in loi_effect or "BỊ KHẮC" in loi_effect else "TRUNG",
    })

    # 2. 4 trụ chi tàng can — tổng hợp Thập Thần
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    count = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0)
    an_count = count("Chính Ấn") + count("Thiên Ấn")
    ty_count = count("Tỷ Kiên") + count("Kiếp Tài")
    tai_count = count("Chính Tài") + count("Thiên Tài")
    quan_count = count("Chính Quan") + count("Thất Sát")
    thuc_count = count("Thực Thần") + count("Thương Quan")

    if an_count + ty_count >= 3:
        causes.append({
            "factor": "Nguồn SUPPORT",
            "detail": f"Ấn = {an_count} (sinh DM) + Tỷ/Kiếp = {ty_count} (trợ DM)",
            "effect": "support tổng cộng kha khá",
            "weight": "TRUNG",
        })
    elif an_count + ty_count <= 1:
        causes.append({
            "factor": "Nguồn SUPPORT YẾU",
            "detail": f"Ấn = {an_count} + Tỷ/Kiếp = {ty_count} → tổng ≤ 1",
            "effect": "thiếu sinh trợ → DM dễ nhược",
            "weight": "CAO",
        })

    if tai_count + quan_count + thuc_count >= 5:
        causes.append({
            "factor": "Nguồn DRAIN MẠNH",
            "detail": f"Tài = {tai_count} (DM khắc) + Quan/Sát = {quan_count} (khắc DM) + "
                      f"Thực/Thương = {thuc_count} (DM sinh)",
            "effect": "hao tiết tổng cộng mạnh → DM khó vượng",
            "weight": "CAO",
        })

    # 3. Verdict tổng
    if tag == "weak":
        conclusion = (
            f"→ DM **{dm_stem} ({dm_el})** NHƯỢC vì hội tụ "
            f"{sum(1 for c in causes if c['weight']=='CAO')} yếu tố trọng. "
            f"Δ = {diff:+.1f}. Cần 'thuốc' = Ấn (sinh thân) + Tỷ/Kiếp (trợ thân)."
        )
    elif tag == "strong":
        conclusion = (
            f"→ DM **{dm_stem} ({dm_el})** VƯỢNG vì lệnh tháng hợp + support đủ. "
            f"Δ = {diff:+.1f}. Cần 'thuốc' = Tài/Quan/Thực (hao tiết bớt)."
        )
    else:
        conclusion = (
            f"→ DM **{dm_stem} ({dm_el})** TRUNG HÒA. Δ = {diff:+.1f}. "
            f"Dụng Thần theo Điều Hậu (khí hậu)."
        )

    return {
        "question": "Vì sao Day Master nhược/vượng/trung?",
        "causes": causes,
        "diff": diff,
        "conclusion": conclusion,
    }


def _trace_tai_concentration_causes(state: dict) -> dict | None:
    """Tại sao có nhiều Tài tinh? Trace branch tàng can structure."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    tai_count = (visible.get("Chính Tài", 0) + visible.get("Thiên Tài", 0)
                 + hidden.get("Chính Tài", 0) + hidden.get("Thiên Tài", 0))
    if tai_count < 3:
        return None

    pillars = state["tu_tru"]["pillars"]
    day_master = state["tu_tru"]["day_master"]["stem"]
    dm_el = state["tu_tru"]["day_master"]["element"]
    tai_el = ELEMENT_CONTROLS.get(dm_el)

    sources = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        for h in p.get("hidden_stems_with_thap_than", []):
            tt = h.get("thap_than", "")
            if tt in ("Chính Tài", "Thiên Tài"):
                sources.append({
                    "pillar": p.get("position_vi", pos),
                    "branch": p["branch"],
                    "hidden_stem": h["stem"],
                    "thap_than": tt,
                    "reason": (
                        f"Chi {p['branch']} tàng can {h['stem']} (hành {tai_el}) — "
                        f"= {tt} của DM {day_master}"
                    ),
                })

    return {
        "question": f"Vì sao có nhiều Tài tinh ({tai_count} vị trí)?",
        "tai_count": tai_count,
        "tai_element": tai_el,
        "sources": sources,
        "explanation": (
            f"Tài tinh = element {tai_el} (do DM {dm_el} khắc). "
            f"Lá số có {len(sources)} chi tàng can {tai_el} (qua tàng can structure). "
            f"Đây là LÝ DO Thổ thừa + cấu hình 'Tài đa thân nhược' xuất hiện."
        ),
    }


def _trace_dai_van_polarity_cause(state: dict, current_age: int | None) -> dict | None:
    """Tại sao Đại Vận hiện tại lành/dữ? Trace element + interactions."""
    if current_age is None:
        return None
    dv_cycles = state.get("dai_van", {}).get("cycles", [])
    current = None
    for c in dv_cycles:
        if c.get("start_age", 0) <= current_age <= c.get("end_age", 999):
            current = c
            break
    if not current:
        return None

    dt = state.get("dung_than", {})
    dung_el = dt.get("dung_than_element", "")
    ky_el = dt.get("ky_than_element", "")
    stem_el = STEM_ELEMENT.get(current.get("stem", ""), "")
    branch_el = BRANCH_ELEMENT.get(current.get("branch", ""), "")
    dm_el = state["tu_tru"]["day_master"]["element"]

    causes = []

    # 1. Element of Đại Vận
    if stem_el == ky_el or branch_el == ky_el:
        causes.append({
            "factor": "Khí Đại Vận = Kỵ Thần",
            "detail": f"DV {current.get('stem')} {current.get('branch')} có khí {stem_el}/{branch_el}, "
                      f"Kỵ Thần = {ky_el}",
            "effect": f"{ky_el} khắc Dụng Thần ({dung_el}) → 10 năm thử thách",
        })
    elif stem_el == dung_el or branch_el == dung_el:
        causes.append({
            "factor": "Khí Đại Vận = Dụng Thần",
            "detail": f"DV {current.get('stem')} {current.get('branch')} có khí {dung_el}",
            "effect": "→ 10 năm thuận, phát huy được",
        })

    # 2. Element vs DM
    rel_dm = _element_relation_label(stem_el, dm_el)
    causes.append({
        "factor": "Quan hệ với Day Master",
        "detail": f"DV can {current.get('stem')} ({stem_el}) ↔ DM ({dm_el})",
        "effect": rel_dm,
    })

    # 3. Interactions với 4 trụ
    from .luu_nien import LUC_HOP, LUC_XUNG, LUC_HAI, TAM_HINH_GROUPS
    pillars = state["tu_tru"]["pillars"]
    dv_branch = current.get("branch")
    interactions = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        pair = frozenset([dv_branch, p["branch"]])
        if pair in LUC_HOP:
            interactions.append({
                "type": "lục hợp",
                "with": f"{p.get('position_vi', pos)} ({p['branch']})",
                "effect": f"kích hoạt khí {LUC_HOP[pair]} → "
                          + ("tăng Kỵ" if LUC_HOP[pair] == ky_el else "tăng Dụng" if LUC_HOP[pair] == dung_el else "trung tính"),
            })
        if pair in LUC_XUNG:
            interactions.append({
                "type": "lục xung",
                "with": f"{p.get('position_vi', pos)} ({p['branch']})",
                "effect": f"biến động lĩnh vực {p.get('domain_vi', pos)}",
            })
        if pair in LUC_HAI:
            interactions.append({
                "type": "lục hại",
                "with": f"{p.get('position_vi', pos)} ({p['branch']})",
                "effect": "bất hòa ngầm",
            })
        for group in TAM_HINH_GROUPS:
            if dv_branch in group and p["branch"] in group and dv_branch != p["branch"]:
                interactions.append({
                    "type": "tương hình",
                    "with": f"{p.get('position_vi', pos)} ({p['branch']})",
                    "effect": "kiện tụng / va chạm",
                })
                break

    return {
        "question": f"Vì sao Đại Vận hiện tại "
                    f"({current.get('stem')} {current.get('branch')}) lành/dữ?",
        "cycle": {
            "stem": current.get("stem"),
            "branch": current.get("branch"),
            "age_range": f"{current.get('start_age')}-{current.get('end_age')}",
        },
        "causes": causes,
        "interactions_with_4_pillars": interactions,
        "conclusion": (
            f"Đại Vận {current.get('stem')} {current.get('branch')} "
            f"({current.get('start_age')}-{current.get('end_age')} tuổi): "
            + ("THỬ THÁCH" if stem_el == ky_el or branch_el == ky_el
               else "THUẬN" if stem_el == dung_el or branch_el == dung_el
               else "TRUNG TÍNH")
            + f". {len(interactions)} interactions với trụ gốc."
        ),
    }


def _detect_compound_warnings(state: dict, current_age: int | None) -> list[dict]:
    """Cảnh báo compound — khi 2+ patterns cộng dồn → emergent risk lớn hơn."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    count = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0)
    dm_tag = state["ngu_hanh"]["day_master_assessment"]["strength_tag"]

    out = []

    # Compound 1: DM nhược + Thương Quan kiến Quan + Đại Vận hiện tại Kim/Quan
    if dm_tag == "weak" and has("Thương Quan") and has("Chính Quan") and current_age:
        dv_cycles = state.get("dai_van", {}).get("cycles", [])
        for c in dv_cycles:
            if c.get("start_age", 0) <= current_age <= c.get("end_age", 999):
                stem_el = STEM_ELEMENT.get(c.get("stem", ""), "")
                dm_el = state["tu_tru"]["day_master"]["element"]
                # Quan/Sát element = element khắc DM
                quan_el = None
                for el, target in ELEMENT_CONTROLS.items():
                    if target == dm_el:
                        quan_el = el
                        break
                if stem_el == quan_el or BRANCH_ELEMENT.get(c.get("branch", "")) == quan_el:
                    out.append({
                        "name": "Compound: Thương Quan kiến Quan + Đại Vận Quan",
                        "severity": "cao",
                        "layers": [
                            f"Layer 1: DM nhược (Δ {state['ngu_hanh']['day_master_assessment'].get('support_score', 0) - state['ngu_hanh']['day_master_assessment'].get('drain_score', 0):+.1f})",
                            f"Layer 2: Thương Quan + Chính Quan đồng lộ trong lá số",
                            f"Layer 3: Đại Vận hiện tại ({c.get('stem')} {c.get('branch')}) "
                            f"có khí Quan ({quan_el}) → kích hoạt Layer 2",
                        ],
                        "narrative": (
                            f"3 yếu tố cộng dồn trong giai đoạn {c.get('start_age')}-{c.get('end_age')} tuổi: "
                            f"DM nhược không chống được Quan + Thương Quan có sẵn (phá Quan) + "
                            f"Đại Vận khí Quan kích hoạt = đại hung cho danh tiếng / quan lộ / pháp luật. "
                            f"💊 **Hóa giải compound**: Hạ chí + Ấn (học vấn) + tránh kích thích trực diện."
                        ),
                    })
                break

    # Compound 2: Tài đa thân nhược + Đại Vận Tài/Quan (sinh từ Tài)
    tai_count = count("Chính Tài") + count("Thiên Tài")
    if dm_tag == "weak" and tai_count >= 3 and current_age:
        dv_cycles = state.get("dai_van", {}).get("cycles", [])
        for c in dv_cycles:
            if c.get("start_age", 0) <= current_age <= c.get("end_age", 999):
                stem_el = STEM_ELEMENT.get(c.get("stem", ""), "")
                dm_el = state["tu_tru"]["day_master"]["element"]
                tai_el = ELEMENT_CONTROLS.get(dm_el)
                quan_el = None
                for el, target in ELEMENT_CONTROLS.items():
                    if target == dm_el:
                        quan_el = el
                        break
                # Tài sinh Quan → khi cả 2 hành active
                if stem_el == quan_el:
                    out.append({
                        "name": "Compound: Tài đa thân nhược + Đại Vận Quan",
                        "severity": "cao",
                        "layers": [
                            f"Layer 1: DM nhược không gánh nổi {tai_count} Tài tinh",
                            f"Layer 2: Đại Vận khí {stem_el} = Quan",
                            f"Layer 3: Tài sinh Quan → Quan khắc DM mạnh thêm",
                        ],
                        "narrative": (
                            f"Tài đa (sẵn) → Tài sinh Quan (Đại Vận) → Quan khắc DM nhược = chuỗi suy hao 3 tầng. "
                            f"Trong {c.get('start_age')}-{c.get('end_age')} tuổi: tránh áp lực tài chính + chức vụ "
                            f"cùng lúc. Ưu tiên Bồi Thân (Ấn / Tỷ Kiếp / nghỉ ngơi)."
                        ),
                    })
                break

    # Compound 3: Thực Thần chế Sát + Ấn hóa Sát + Thương Quan phối Ấn (3 lành layer)
    if has("Thất Sát") and has("Thực Thần") and (has("Chính Ấn") or has("Thiên Ấn")):
        out.append({
            "name": "Compound: Quý hiển 3 tầng (Thực chế + Ấn hóa + có Thương phối)",
            "severity": "lành cao",
            "layers": [
                "Layer 1: Thực Thần chế Sát → Sát thành QUYỀN",
                "Layer 2: Ấn hóa Sát → áp lực thành học vấn/quý nhân",
                "Layer 3: Có cả Thực + Ấn → cấu hình kinh điển QUÝ",
            ],
            "narrative": (
                "3 cấu hình thuận đồng thời có mặt → đây là 1 trong các pattern QUÝ hiển nhất của Tử Bình. "
                "Anh có khả năng chuyển áp lực + tài năng + học vấn thành leadership chính danh. "
                "Tận dụng bằng cách: chọn môi trường áp lực cao nhưng có sáng tạo + giữ học hỏi liên tục."
            ),
        })

    return out


def _detect_cross_pattern_links(state: dict, luan_giai: dict | None = None) -> list[dict]:
    """Cross-links giữa patterns: A reinforces B, A contradicts B, A explains B."""
    links = []
    if not luan_giai:
        return links

    fav_names = {f["name"] for f in luan_giai.get("favorable_combinations", [])}
    warn_names = {w["name"] for w in luan_giai.get("warnings", [])}

    # Link 1: Thực Thương sinh Tài + Tài đa thân nhược → trade-off
    if "Thực Thương sinh Tài" in fav_names and "Thân nhược không gánh nổi Tài" in warn_names:
        links.append({
            "type": "trade-off",
            "between": ["Thực Thương sinh Tài", "Thân nhược không gánh Tài"],
            "narrative": (
                "Mâu thuẫn nội tại: Cấu hình thuận 'Thực Thương sinh Tài' (kinh điển PHÚ) "
                "ĐỒNG THỜI với cảnh báo 'Thân nhược không gánh Tài'. "
                "→ Anh CÓ KHẢ NĂNG tạo Tài (qua sáng tạo + thương mại) "
                "nhưng KHÓ GIỮ Tài (thân yếu không chịu áp lực tài chính lớn). "
                "**Giải pháp**: Bồi thân TRƯỚC (Đời 1 = học vấn + đối tác), Tài lộc đến SAU (Đời 2)."
            ),
        })

    # Link 2: Thực Thần chế Sát + Thương Quan kiến Quan → split context
    if "Thực Thần chế Sát" in fav_names and "Thương Quan kiến Quan" in warn_names:
        links.append({
            "type": "split context",
            "between": ["Thực Thần chế Sát (lành)", "Thương Quan kiến Quan (hung)"],
            "narrative": (
                "Cùng lá số có cả 2 cấu hình đối nghịch — Quan Sát hỗn tạp + Thực Thương hỗn tạp. "
                "→ Phân biệt RÕ context: "
                "**Khi đối với Thất Sát** (áp lực sáng tạo, mạo hiểm có chiến lược) → kích hoạt Thực Thần chế Sát = thuận. "
                "**Khi đối với Chính Quan** (cấp trên, pháp luật, danh tiếng) → tránh Thương Quan phá = giữ kỷ luật + lễ phép. "
                "Không thể tận dụng cả 2 cùng lúc."
            ),
        })

    # Link 3: Đại Vận Kỵ + Compound warnings
    dv_current = luan_giai.get("dai_van_current", {})
    if dv_current.get("matches_ky_than") and "Tài bị Kiếp đoạt" in warn_names:
        links.append({
            "type": "time-trigger",
            "between": ["Đại Vận Kỵ Thần", "Tài bị Kiếp đoạt"],
            "narrative": (
                "Đại Vận hiện tại đi vào Kỵ Thần — đây là thời gian latent pattern "
                "'Tài bị Kiếp đoạt' DỄ KÍCH HOẠT nhất. "
                "→ 10 năm này cảnh giác đầu tư chung, partnership tài chính, lãi suất cao."
            ),
        })

    # Link 4: Cách Cục Thực Thần + Kỵ Kiêu Thần → liên kết với Thiên Ấn
    cc = luan_giai.get("cach_cuc_luan", {})
    if cc.get("name") and "Thực Thần" in cc["name"]:
        dist = state.get("thap_than_distribution", {})
        visible = dist.get("visible", {})
        hidden = dist.get("hidden", {})
        if visible.get("Thiên Ấn", 0) + hidden.get("Thiên Ấn", 0) > 0:
            links.append({
                "type": "structural threat",
                "between": ["Thực Thần cách (cách cục chính)", "Thiên Ấn (Kiêu Thần)"],
                "narrative": (
                    "Cách cục là 'Thực Thần cách' — phúc lộc đến từ Thực Thần. "
                    "Nhưng lá số CÓ Thiên Ấn (Kiêu) — đây là kẻ ĐOẠT Thực Thần kinh điển. "
                    "→ Phải bảo vệ Thực Thần bằng cách: thêm Chính Tài (khắc Kiêu) "
                    "hoặc chọn nghề ổn định có deadline + output rõ ràng (Kiêu khó đoạt khi Thực có công việc cụ thể)."
                ),
            })

    return links


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_causal_reasoning_v1"
SOURCE_REF = (
    "Causal reasoning layer trên Thiệu Vĩ Hoa Q1 + Tử Bình Chân Thuyên — "
    "trả lời 'điều gì ảnh hưởng / nguyên nhân / liên kết'."
)


def analyze_causal_reasoning(
    bat_tu_state: dict,
    luan_giai: dict | None = None,
    current_age: int | None = None,
) -> dict:
    """Causal + relational reasoning trên lá số.

    Args:
        bat_tu_state: Output of cast_bat_tu()
        luan_giai: Optional output of compose_luan_giai() — needed for cross-links
        current_age: Optional — needed for Đại Vận causal trace

    Returns:
        Dict with 4 reasoning sections.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    dm_causes = _trace_dm_strength_causes(bat_tu_state)
    tai_causes = _trace_tai_concentration_causes(bat_tu_state)
    dv_causes = _trace_dai_van_polarity_cause(bat_tu_state, current_age)
    compound = _detect_compound_warnings(bat_tu_state, current_age)
    cross_links = _detect_cross_pattern_links(bat_tu_state, luan_giai)

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Causal reasoning layer KHÔNG dự đoán — phân tích NGUYÊN NHÂN cấu hình "
            "+ LIÊN KẾT giữa các patterns + COMPOUND effects. "
            "Giúp người đọc HIỂU vì sao, không chỉ biết cái gì."
        ),
        "dm_strength_causes": dm_causes,
        "tai_concentration_causes": tai_causes,
        "dai_van_polarity_causes": dv_causes,
        "compound_effects": compound,
        "cross_pattern_links": cross_links,
        "closing": (
            "Liên kết = sự sống của lá số. Một mình mỗi cấu hình chỉ là TRỮ năng. "
            "Khi 2-3 cấu hình GẶP NHAU (compound) trong cùng giai đoạn — "
            "đó là lúc lá số PHÁT HUY hoặc PHÁT BỆNH. "
            "Hiểu liên kết → biết khi nào 'đẩy', khi nào 'thủ'."
        ),
    }
