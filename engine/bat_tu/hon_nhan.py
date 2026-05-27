"""Hôn Nhân (婚姻) — marriage / partnership analysis from Bát Tự chart.

Paradigm (Iron Rule #4+6): Phân tích Hôn nhân KHÔNG dự đoán "anh sẽ lấy người
giàu / chia tay năm X". Phân tích đọc **cấu trúc khí của Cung Phối + Tài/Quan
star + Đào hoa** trong lá số → mô tả XU HƯỚNG + Khí mà partner mang đến.

Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (rải rác trong Q. 4-6
về Lục Thân + Hôn nhân + Đào hoa).

Algorithm:
1. **Cung Phối** = Trụ Ngày địa chi (đại biểu cho vợ/chồng).
2. **Star của vợ/chồng**:
   - Nam: Chính Tài (vợ chính) + Thiên Tài (vợ lẽ/đào hoa)
   - Nữ: Chính Quan (chồng) + Thất Sát (đối tượng mạnh / kẻ cường)
3. **Vượng-Nhược** của star → mức độ rõ nét.
4. **Cảnh báo** cấu hình:
   - Nam: Kiếp Tài đoạt Chính Tài → vợ bị tổn / khó giữ tài
   - Nữ: Thương Quan kiến Quan → khắc chồng / hôn nhân biến động
   - Trụ Ngày chi tự hình / lục xung với Trụ Năm/Tháng/Giờ → tổ ấm khó ổn
5. **Đào hoa / Hồng Diễm / Cô Thần / Quả Tú** → tô thêm.
6. **Thời điểm khả thi** (suggestion, không predict):
   - Đại Vận có Tài/Quan tinh vượng
   - Lưu Niên có chi hợp / hợp cục với Trụ Ngày chi
"""

from __future__ import annotations

from .constants import BRANCH_ELEMENT, BRANCH_HIDDEN_STEMS, STEM_ELEMENT
from .luu_nien import LUC_HAI, LUC_HOP, LUC_XUNG, TAM_HOP, TAM_HINH_GROUPS
from .thap_than import thap_than_of


# ─── Reference tables ────────────────────────────────────────────────────────

# Cung Phối narrative — Trụ Ngày chi → biểu tượng vợ/chồng
CUNG_PHOI_BRANCH_TRAIT: dict[str, str] = {
    "Tý": "Cung Phối thuộc Tý (thủy) — vợ/chồng có tâm tư sâu, ưa ẩn, nhạy cảm.",
    "Sửu": "Cung Phối thuộc Sửu (thổ ẩm) — vợ/chồng chăm chỉ, kiên nhẫn, thiên về truyền thống.",
    "Dần": "Cung Phối thuộc Dần (mộc dương) — vợ/chồng có chí tiến thủ, năng động, cương trực.",
    "Mão": "Cung Phối thuộc Mão (mộc âm) — vợ/chồng nhẹ nhàng, mềm mại, ưa thẩm mỹ.",
    "Thìn": "Cung Phối thuộc Thìn (thổ dương) — vợ/chồng có khả năng tổ chức, quyền uy ngầm.",
    "Tỵ": "Cung Phối thuộc Tỵ (hỏa âm) — vợ/chồng thông minh, kín đáo, có chiều sâu.",
    "Ngọ": "Cung Phối thuộc Ngọ (hỏa dương) — vợ/chồng nhiệt tình, sáng tỏ, dễ bộc lộ.",
    "Mùi": "Cung Phối thuộc Mùi (thổ khô) — vợ/chồng có tâm tính ngoan, biết chiều chuộng.",
    "Thân": "Cung Phối thuộc Thân (kim dương) — vợ/chồng quyết đoán, có tài, hơi cứng đầu.",
    "Dậu": "Cung Phối thuộc Dậu (kim âm) — vợ/chồng tinh tế, có nhãn quan thẩm mỹ + tài năng.",
    "Tuất": "Cung Phối thuộc Tuất (thổ dương) — vợ/chồng trung thành, bảo vệ, có nguyên tắc.",
    "Hợi": "Cung Phối thuộc Hợi (thủy âm) — vợ/chồng giàu cảm xúc, sâu sắc, đôi khi trầm.",
}

# Đào Hoa rule (4-stage classical):
# Năm/Ngày chi Tý/Thìn/Thân → Đào Hoa = Dậu (Tử Bình tài liệu phổ thông)
# Năm/Ngày chi Sửu/Tỵ/Dậu → Đào Hoa = Ngọ
# Năm/Ngày chi Dần/Ngọ/Tuất → Đào Hoa = Mão
# Năm/Ngày chi Mão/Mùi/Hợi → Đào Hoa = Tý
DAO_HOA_BY_BRANCH: dict[str, str] = {}
for trio, dh in [
    (("Tý", "Thìn", "Thân"), "Dậu"),
    (("Sửu", "Tỵ", "Dậu"), "Ngọ"),
    (("Dần", "Ngọ", "Tuất"), "Mão"),
    (("Mão", "Mùi", "Hợi"), "Tý"),
]:
    for b in trio:
        DAO_HOA_BY_BRANCH[b] = dh


# ─── Helpers ────────────────────────────────────────────────────────────────


def _branch_interactions_with(target: str, others: list[str]) -> list[dict]:
    """All interactions between `target` chi and a list of other chi."""
    out = []
    for o in others:
        if o == target:
            continue
        pair = frozenset([target, o])
        if pair in LUC_HOP:
            out.append({"with": o, "type": "lục hợp", "polarity": "lành",
                       "narrative": f"Lục hợp với {o} ({LUC_HOP[pair]}) — quan hệ ấm áp."})
        if pair in LUC_XUNG:
            out.append({"with": o, "type": "lục xung", "polarity": "hung",
                       "narrative": f"Lục xung với {o} — biến động trong quan hệ."})
        if pair in LUC_HAI:
            out.append({"with": o, "type": "lục hại", "polarity": "hung",
                       "narrative": f"Lục hại với {o} — bất hòa ngầm."})
        for group in TAM_HINH_GROUPS:
            if target in group and o in group:
                out.append({"with": o, "type": "tương hình", "polarity": "hung",
                           "narrative": f"Tương hình {target}-{o} — cẳng khẩu, va chạm."})
                break
    return out


def _count_partner_star(pillars: dict, day_master: str, gender: str) -> dict:
    """Đếm Tài (nam) / Quan (nữ) stars trong lá số."""
    if gender == "nam":
        # Vợ chính + vợ lẽ
        target_thap_than = {"Chính Tài", "Thiên Tài"}
        main = "Chính Tài"
        secondary = "Thiên Tài"
    else:
        target_thap_than = {"Chính Quan", "Thất Sát"}
        main = "Chính Quan"
        secondary = "Thất Sát"

    visible_positions: list[str] = []
    hidden_positions: list[str] = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        if pos != "day":
            stem_tt = thap_than_of(day_master, p["stem"])
            if stem_tt in target_thap_than:
                visible_positions.append(f"{p.get('position_vi', pos)} (can {p['stem']} = {stem_tt})")
        for hs in p["hidden_stems"]:
            if hs == day_master and pos == "day":
                continue
            hs_tt = thap_than_of(day_master, hs)
            if hs_tt in target_thap_than:
                hidden_positions.append(f"{p.get('position_vi', pos)} (tàng {hs} = {hs_tt})")
    return {
        "gender": gender,
        "main_star": main,
        "secondary_star": secondary,
        "visible_positions": visible_positions,
        "hidden_positions": hidden_positions,
        "total_count": len(visible_positions) + len(hidden_positions),
    }


def _check_warning_patterns(pillars: dict, day_master: str, gender: str,
                             thap_than_dist: dict) -> list[dict]:
    """Phát hiện cấu hình hôn nhân cảnh báo."""
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    out = []
    if gender == "nam":
        if has("Kiếp Tài") and (has("Chính Tài") or has("Thiên Tài")):
            out.append({
                "name": "Kiếp Tài đoạt Tài",
                "polarity": "cẩn trọng",
                "narrative": (
                    "Lá số có Tài tinh + Kiếp Tài. Đối với nam — cần đề phòng tổn hại "
                    "trong quan hệ vợ chồng từ phía bạn bè/cộng sự cùng giới, "
                    "hoặc cạnh tranh tài lộc ảnh hưởng đến gia đình."
                ),
            })
        # Nhật chủ nhược + Tài vượng
        tai_count = visible.get("Chính Tài", 0) + visible.get("Thiên Tài", 0) + \
                    hidden.get("Chính Tài", 0) + hidden.get("Thiên Tài", 0)
        if tai_count >= 3:
            out.append({
                "name": "Tài tinh quá vượng",
                "polarity": "cẩn trọng",
                "narrative": (
                    "Tài tinh quá nhiều (≥3) — nam có thể có nhiều quan hệ, "
                    "tình duyên đa dạng. Cần Day Master vượng để 'gánh' được Tài. "
                    "Nếu Day Master nhược → quan hệ mệt mỏi, khó duy trì."
                ),
            })
    else:  # nữ
        if has("Thương Quan") and (has("Chính Quan") or has("Thất Sát")):
            out.append({
                "name": "Thương Quan kiến Quan",
                "polarity": "cẩn trọng",
                "narrative": (
                    "Lá số nữ có cả Thương Quan + Quan tinh — cấu hình khắc chồng cổ điển. "
                    "Cần Chính Ấn để 'Thương Quan phối Ấn' hóa giải. "
                    "Hôn nhân cần đối tác có Ấn (học vấn/từ thiện)."
                ),
            })
        if has("Chính Quan") and has("Thất Sát"):
            out.append({
                "name": "Quan Sát hỗn tạp",
                "polarity": "cẩn trọng",
                "narrative": (
                    "Cả Chính Quan + Thất Sát đồng lộ — nữ có thể vướng nhiều mối quan hệ "
                    "đan xen. Cần lựa chọn 1 + chế hoặc hóa cái kia."
                ),
            })
    return out


def _detect_special_stars(than_sat: list[dict]) -> dict:
    """Tìm sao Đào hoa / Hồng Diễm / Cô Thần / Quả Tú / Thiên Hỉ trong lá số."""
    relevant_names = {"Đào Hoa", "Hồng Diễm", "Cô Thần", "Quả Tú", "Thiên Hỷ", "Long Đức"}
    found = {}
    for s in than_sat:
        name = s.get("name", "")
        if name in relevant_names:
            found[name] = {
                "polarity": s.get("polarity"),
                "pillar": s.get("found_at_pillar"),
                "description": s.get("description", "")[:200],
            }
    return found


def _suggest_timing(dai_van_cycles: list[dict], day_branch: str, day_master_el: str,
                     dung_than_el: str, gender: str) -> dict:
    """Suggest likely-favorable Đại Vận cycles cho hôn nhân.

    Heuristic: cycle có chi hợp với day_branch OR chứa Tài/Quan element.
    """
    if not dai_van_cycles:
        return {"favorable_cycles": [], "narrative": "Chưa có dữ liệu Đại Vận."}
    # Partner element: nam → Tài (khắc bởi day master), nữ → Quan (khắc day master)
    from .constants import ELEMENT_CONTROLS
    if gender == "nam":
        partner_el = ELEMENT_CONTROLS.get(day_master_el)
    else:
        # Nữ: Quan = element khắc day master. Find which element controls day_master_el.
        partner_el = None
        for el, target in ELEMENT_CONTROLS.items():
            if target == day_master_el:
                partner_el = el
                break
    favorable = []
    for c in dai_van_cycles:
        score = 0
        reasons = []
        c_stem_el = STEM_ELEMENT.get(c.get("stem", ""))
        c_branch_el = BRANCH_ELEMENT.get(c.get("branch", ""))
        pair = frozenset([day_branch, c.get("branch", "")])
        if pair in LUC_HOP:
            score += 2
            reasons.append(f"lục hợp với Cung Phối {day_branch}")
        # Tam hợp containing day_branch
        for el, group in TAM_HOP.items():
            if day_branch in group and c.get("branch") in group and day_branch != c.get("branch"):
                score += 2
                reasons.append(f"bán hợp {el} với Cung Phối")
                break
        if partner_el and (c_stem_el == partner_el or c_branch_el == partner_el):
            score += 1
            reasons.append(f"có khí {partner_el} ({'Tài' if gender == 'nam' else 'Quan'} tinh)")
        if c_stem_el == dung_than_el or c_branch_el == dung_than_el:
            score += 1
            reasons.append(f"hợp Dụng Thần {dung_than_el}")
        if score >= 2:
            favorable.append({
                **c,
                "score": score,
                "reasons": reasons,
            })
    # Sort by score desc, take top 3
    favorable.sort(key=lambda x: -x["score"])
    favorable = favorable[:3]
    return {
        "partner_element": partner_el,
        "favorable_cycles": favorable,
        "narrative": (
            f"Các chu kỳ Đại Vận thuận lợi cho hôn nhân/quan hệ "
            f"(theo {'Tài' if gender == 'nam' else 'Quan'} tinh + hợp Cung Phối): "
            + (", ".join(f"V{c['cycle_index']} ({c['stem']} {c['branch']}, "
                         f"{c['start_age']}-{c['end_age']}t)"
                         for c in favorable) if favorable
               else "không phát hiện chu kỳ đặc biệt thuận lợi từ rule cơ bản.")
            + "."
        ),
    }


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_hon_nhan_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ. Cung Phối + Tài/Quan Tinh + "
    "Đào Hoa pattern (Q. 4-6 rải rác)."
)


def analyze_hon_nhan(bat_tu_state: dict) -> dict:
    """Phân tích Hôn nhân từ lá số Bát Tự.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.

    Returns:
        Structured dict với 6 sections.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    gender = bat_tu_state.get("gender", "nam")
    pillars = bat_tu_state["tu_tru"]["pillars"]
    day_master = bat_tu_state["tu_tru"]["day_master"]["stem"]
    day_master_el = bat_tu_state["tu_tru"]["day_master"]["element"]
    day_branch = pillars["day"]["branch"]
    thap_than_dist = bat_tu_state.get("thap_than_distribution", {})
    than_sat = bat_tu_state.get("than_sat", [])
    dai_van = bat_tu_state.get("dai_van", {})
    dung_than = bat_tu_state.get("dung_than", {})

    # 1. Cung Phối
    cung_phoi_narrative = CUNG_PHOI_BRANCH_TRAIT.get(
        day_branch,
        f"Cung Phối thuộc {day_branch} — đặc tính chưa có entry.",
    )
    # Phối + tương tác với 3 trụ khác
    other_branches = [pillars[p]["branch"] for p in ("year", "month", "hour")]
    cung_phoi_interactions = _branch_interactions_with(day_branch, other_branches)
    # Tàng can của Cung Phối → Thập Thần
    cung_phoi_tang = []
    for hs in BRANCH_HIDDEN_STEMS.get(day_branch, ()):
        if hs == day_master:
            continue
        tt = thap_than_of(day_master, hs)
        cung_phoi_tang.append({"stem": hs, "thap_than": tt})

    # 2. Partner Star analysis
    partner_star = _count_partner_star(pillars, day_master, gender)

    # 3. Warnings
    warnings = _check_warning_patterns(pillars, day_master, gender, thap_than_dist)

    # 4. Special stars
    special = _detect_special_stars(than_sat)
    # Cung Phối có Đào Hoa không?
    dao_hoa_chi = DAO_HOA_BY_BRANCH.get(day_branch)
    if dao_hoa_chi:
        dao_hoa_present = dao_hoa_chi in [pillars[p]["branch"] for p in ("year", "month", "day", "hour")]
    else:
        dao_hoa_present = False

    # 5. Timing suggestions
    timing = _suggest_timing(
        dai_van.get("cycles", []),
        day_branch,
        day_master_el,
        dung_than.get("dung_than_element", ""),
        gender,
    )

    # 6. Overall verdict
    score = 0
    if partner_star["total_count"] >= 1:
        score += 1
    if partner_star["visible_positions"]:
        score += 1
    if warnings:
        score -= len(warnings)
    favorable_cp = [i for i in cung_phoi_interactions if i.get("polarity") == "lành"]
    hung_cp = [i for i in cung_phoi_interactions if i.get("polarity") == "hung"]
    score += len(favorable_cp) - len(hung_cp)
    if score >= 2:
        overall_label = "thuận"
        overall_narrative = "Cấu trúc hôn nhân thuận — Cung Phối + star + tương tác hài hòa."
    elif score >= 0:
        overall_label = "trung bình"
        overall_narrative = "Cấu trúc hôn nhân trung bình — có cả thuận + thử thách, cần lựa chọn."
    else:
        overall_label = "thử thách"
        overall_narrative = "Cấu trúc hôn nhân nhiều thử thách — Cung Phối nhiều xung/hại, cần ý thức hóa giải."

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Phân tích Hôn nhân KHÔNG dự đoán anh sẽ lấy ai / năm nào. "
            "Đọc cấu trúc khí của Cung Phối + Tài/Quan tinh → mô tả XU HƯỚNG + "
            "khí mà partner mang đến + thời điểm khả thi (suggestion, không cứng)."
        ),
        "gender": gender,
        "cung_phoi": {
            "branch": day_branch,
            "branch_element": BRANCH_ELEMENT.get(day_branch),
            "trait_narrative": cung_phoi_narrative,
            "tang_can": cung_phoi_tang,
            "interactions_with_other_pillars": cung_phoi_interactions,
            "has_dao_hoa_in_chart": dao_hoa_present,
            "dao_hoa_chi": dao_hoa_chi,
        },
        "partner_star": partner_star,
        "warnings": warnings,
        "special_stars": special,
        "timing_suggestions": timing,
        "overall": {
            "label": overall_label,
            "score": score,
            "narrative": overall_narrative,
        },
        "closing": (
            "Hôn nhân là dòng khí giữa 2 người. Tử Bình chỉ cho thấy CẤU HÌNH khí "
            "phía mình + xu hướng partner. Chất lượng quan hệ là sự gặp gỡ + chăm sóc "
            "có ý thức — không định sẵn."
        ),
    }
