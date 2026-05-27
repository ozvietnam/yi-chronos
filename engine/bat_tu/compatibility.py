"""Compatibility — so 2 lá số Bát Tự (vợ-chồng / cha-con / partner / sibling).

Paradigm (Iron Rule #4+6): KHÔNG dự đoán "2 anh chị sẽ ly hôn / sống hạnh phúc".
Đọc cấu trúc khí giữa 2 lá số → mô tả CHIỀU TƯƠNG TÁC, điểm hợp, điểm xung,
hành nào bổ cho bên nào.

Source: Thiệu Vĩ Hoa Q. 5-6 (Lục Thân + Nạp Âm comparison) + tradition.

Algorithm:
1. **Nạp Âm** comparison (30 cặp Giáp Tý → 6 nạp âm elements):
   - Sinh / Khắc / Tỷ hòa Nạp Âm hành
2. **Day Master compatibility**:
   - 5 hợp Can: Giáp-Kỷ → Thổ, Ất-Canh → Kim, Bính-Tân → Thủy, Đinh-Nhâm → Mộc, Mậu-Quý → Hỏa
   - Sinh / Khắc / Tỷ hòa ngũ hành
3. **Cung Phối** (Trụ Ngày chi) check:
   - Lục hợp (6 cặp lành) / Lục xung (6 cặp đối) / Lục hại / Tam hợp
4. **Ngũ hành dynamics**:
   - A có khí thiếu mà B có thừa? (bổ cho A)
   - Chia sẻ Dụng Thần?
5. **Spouse-specific** (gender pair):
   - Tài tinh Nam vs DM Nữ (vợ trong lá số chồng)
   - Quan tinh Nữ vs DM Nam (chồng trong lá số vợ)
6. **Overall verdict**: thuận / trung / thử thách
"""

from __future__ import annotations

from .constants import (
    BRANCH_ELEMENT,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    STEM_ELEMENT,
    STEM_POLARITY,
)
from .luu_nien import LUC_HAI, LUC_HOP, LUC_XUNG, TAM_HOP, TAM_HINH_GROUPS


# ─── Reference tables ───────────────────────────────────────────────────────

# 5 hợp Can — same as Hóa Khí pairs
HOP_CAN: dict[frozenset, str] = {
    frozenset(["Giáp", "Kỷ"]): "thổ",
    frozenset(["Ất", "Canh"]): "kim",
    frozenset(["Bính", "Tân"]): "thủy",
    frozenset(["Đinh", "Nhâm"]): "mộc",
    frozenset(["Mậu", "Quý"]): "hỏa",
}

# Nạp Âm — 30 cặp Giáp Tý → 6 nạp âm elements (24 names)
# Format: (stem, branch) → nạp âm element
NAP_AM_MAP: dict[tuple[str, str], str] = {
    # 1-2: Hải Trung Kim (Kim đáy biển)
    ("Giáp", "Tý"): "kim", ("Ất", "Sửu"): "kim",
    # 3-4: Lư Trung Hỏa (Lửa trong lò)
    ("Bính", "Dần"): "hỏa", ("Đinh", "Mão"): "hỏa",
    # 5-6: Đại Lâm Mộc (Mộc rừng lớn)
    ("Mậu", "Thìn"): "mộc", ("Kỷ", "Tỵ"): "mộc",
    # 7-8: Lộ Bàng Thổ (Đất bên đường)
    ("Canh", "Ngọ"): "thổ", ("Tân", "Mùi"): "thổ",
    # 9-10: Kiếm Phong Kim (Kim mũi kiếm)
    ("Nhâm", "Thân"): "kim", ("Quý", "Dậu"): "kim",
    # 11-12: Sơn Đầu Hỏa (Hỏa đầu núi)
    ("Giáp", "Tuất"): "hỏa", ("Ất", "Hợi"): "hỏa",
    # 13-14: Giản Hạ Thủy (Thủy dưới khe)
    ("Bính", "Tý"): "thủy", ("Đinh", "Sửu"): "thủy",
    # 15-16: Thành Đầu Thổ (Thổ đầu thành)
    ("Mậu", "Dần"): "thổ", ("Kỷ", "Mão"): "thổ",
    # 17-18: Bạch Lạp Kim (Kim mạ trắng)
    ("Canh", "Thìn"): "kim", ("Tân", "Tỵ"): "kim",
    # 19-20: Dương Liễu Mộc (Mộc dương liễu)
    ("Nhâm", "Ngọ"): "mộc", ("Quý", "Mùi"): "mộc",
    # 21-22: Tuyền Trung Thủy (Thủy giữa suối)
    ("Giáp", "Thân"): "thủy", ("Ất", "Dậu"): "thủy",
    # 23-24: Ốc Thượng Thổ (Thổ trên mái)
    ("Bính", "Tuất"): "thổ", ("Đinh", "Hợi"): "thổ",
    # 25-26: Tích Lịch Hỏa (Hỏa sét lửa)
    ("Mậu", "Tý"): "hỏa", ("Kỷ", "Sửu"): "hỏa",
    # 27-28: Tùng Bá Mộc (Mộc cây thông bá)
    ("Canh", "Dần"): "mộc", ("Tân", "Mão"): "mộc",
    # 29-30: Trường Lưu Thủy (Thủy dòng dài)
    ("Nhâm", "Thìn"): "thủy", ("Quý", "Tỵ"): "thủy",
    # 31-32: Sa Trung Kim (Kim trong cát)
    ("Giáp", "Ngọ"): "kim", ("Ất", "Mùi"): "kim",
    # 33-34: Sơn Hạ Hỏa (Hỏa dưới núi)
    ("Bính", "Thân"): "hỏa", ("Đinh", "Dậu"): "hỏa",
    # 35-36: Bình Địa Mộc (Mộc đất bằng)
    ("Mậu", "Tuất"): "mộc", ("Kỷ", "Hợi"): "mộc",
    # 37-38: Bích Thượng Thổ (Thổ trên vách)
    ("Canh", "Tý"): "thổ", ("Tân", "Sửu"): "thổ",
    # 39-40: Kim Bạch Kim (Kim trắng bạch)
    ("Nhâm", "Dần"): "kim", ("Quý", "Mão"): "kim",
    # 41-42: Phú Đăng Hỏa (Hỏa đèn dầu)
    ("Giáp", "Thìn"): "hỏa", ("Ất", "Tỵ"): "hỏa",
    # 43-44: Thiên Hà Thủy (Thủy sông trời)
    ("Bính", "Ngọ"): "thủy", ("Đinh", "Mùi"): "thủy",
    # 45-46: Đại Trạch Thổ (Thổ đầm lớn)
    ("Mậu", "Thân"): "thổ", ("Kỷ", "Dậu"): "thổ",
    # 47-48: Thoa Xuyến Kim (Kim đồ trang sức)
    ("Canh", "Tuất"): "kim", ("Tân", "Hợi"): "kim",
    # 49-50: Tang Đố Mộc (Mộc cây dâu)
    ("Nhâm", "Tý"): "mộc", ("Quý", "Sửu"): "mộc",
    # 51-52: Đại Khê Thủy (Thủy khe lớn)
    ("Giáp", "Dần"): "thủy", ("Ất", "Mão"): "thủy",
    # 53-54: Sa Trung Thổ (Thổ trong cát)
    ("Bính", "Thìn"): "thổ", ("Đinh", "Tỵ"): "thổ",
    # 55-56: Thiên Thượng Hỏa (Hỏa trên trời)
    ("Mậu", "Ngọ"): "hỏa", ("Kỷ", "Mùi"): "hỏa",
    # 57-58: Thạch Lựu Mộc (Mộc cây thạch lựu)
    ("Canh", "Thân"): "mộc", ("Tân", "Dậu"): "mộc",
    # 59-60: Đại Hải Thủy (Thủy biển lớn)
    ("Nhâm", "Tuất"): "thủy", ("Quý", "Hợi"): "thủy",
}

# Names for nice display
NAP_AM_NAMES: dict[tuple[str, str], str] = {
    ("Giáp", "Tý"): "Hải Trung Kim",   ("Ất", "Sửu"): "Hải Trung Kim",
    ("Bính", "Dần"): "Lư Trung Hỏa",   ("Đinh", "Mão"): "Lư Trung Hỏa",
    ("Mậu", "Thìn"): "Đại Lâm Mộc",     ("Kỷ", "Tỵ"): "Đại Lâm Mộc",
    ("Canh", "Ngọ"): "Lộ Bàng Thổ",     ("Tân", "Mùi"): "Lộ Bàng Thổ",
    ("Nhâm", "Thân"): "Kiếm Phong Kim", ("Quý", "Dậu"): "Kiếm Phong Kim",
    ("Giáp", "Tuất"): "Sơn Đầu Hỏa",     ("Ất", "Hợi"): "Sơn Đầu Hỏa",
    ("Bính", "Tý"): "Giản Hạ Thủy",     ("Đinh", "Sửu"): "Giản Hạ Thủy",
    ("Mậu", "Dần"): "Thành Đầu Thổ",    ("Kỷ", "Mão"): "Thành Đầu Thổ",
    ("Canh", "Thìn"): "Bạch Lạp Kim",   ("Tân", "Tỵ"): "Bạch Lạp Kim",
    ("Nhâm", "Ngọ"): "Dương Liễu Mộc",  ("Quý", "Mùi"): "Dương Liễu Mộc",
    ("Giáp", "Thân"): "Tuyền Trung Thủy", ("Ất", "Dậu"): "Tuyền Trung Thủy",
    ("Bính", "Tuất"): "Ốc Thượng Thổ",   ("Đinh", "Hợi"): "Ốc Thượng Thổ",
    ("Mậu", "Tý"): "Tích Lịch Hỏa",     ("Kỷ", "Sửu"): "Tích Lịch Hỏa",
    ("Canh", "Dần"): "Tùng Bá Mộc",     ("Tân", "Mão"): "Tùng Bá Mộc",
    ("Nhâm", "Thìn"): "Trường Lưu Thủy", ("Quý", "Tỵ"): "Trường Lưu Thủy",
    ("Giáp", "Ngọ"): "Sa Trung Kim",     ("Ất", "Mùi"): "Sa Trung Kim",
    ("Bính", "Thân"): "Sơn Hạ Hỏa",     ("Đinh", "Dậu"): "Sơn Hạ Hỏa",
    ("Mậu", "Tuất"): "Bình Địa Mộc",    ("Kỷ", "Hợi"): "Bình Địa Mộc",
    ("Canh", "Tý"): "Bích Thượng Thổ",   ("Tân", "Sửu"): "Bích Thượng Thổ",
    ("Nhâm", "Dần"): "Kim Bạch Kim",    ("Quý", "Mão"): "Kim Bạch Kim",
    ("Giáp", "Thìn"): "Phú Đăng Hỏa",   ("Ất", "Tỵ"): "Phú Đăng Hỏa",
    ("Bính", "Ngọ"): "Thiên Hà Thủy",   ("Đinh", "Mùi"): "Thiên Hà Thủy",
    ("Mậu", "Thân"): "Đại Trạch Thổ",   ("Kỷ", "Dậu"): "Đại Trạch Thổ",
    ("Canh", "Tuất"): "Thoa Xuyến Kim", ("Tân", "Hợi"): "Thoa Xuyến Kim",
    ("Nhâm", "Tý"): "Tang Đố Mộc",     ("Quý", "Sửu"): "Tang Đố Mộc",
    ("Giáp", "Dần"): "Đại Khê Thủy",   ("Ất", "Mão"): "Đại Khê Thủy",
    ("Bính", "Thìn"): "Sa Trung Thổ",   ("Đinh", "Tỵ"): "Sa Trung Thổ",
    ("Mậu", "Ngọ"): "Thiên Thượng Hỏa", ("Kỷ", "Mùi"): "Thiên Thượng Hỏa",
    ("Canh", "Thân"): "Thạch Lựu Mộc",  ("Tân", "Dậu"): "Thạch Lựu Mộc",
    ("Nhâm", "Tuất"): "Đại Hải Thủy",   ("Quý", "Hợi"): "Đại Hải Thủy",
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _nap_am(stem: str, branch: str) -> tuple[str, str]:
    """Return (element, name) cho Nạp Âm của trụ Năm."""
    element = NAP_AM_MAP.get((stem, branch), "unknown")
    name = NAP_AM_NAMES.get((stem, branch), "Unknown")
    return element, name


def _element_relation(a: str, b: str) -> dict:
    """Quan hệ ngũ hành giữa 2 element."""
    if a == b:
        return {"type": "tỷ hòa", "polarity": "trung-lành",
                "narrative": f"Cùng hành {a.title()} — tỷ hòa, hợp ý nhau."}
    if ELEMENT_GENERATES.get(a) == b:
        return {"type": "A sinh B", "polarity": "lành",
                "narrative": f"{a.title()} sinh {b.title()} — A nuôi dưỡng B."}
    if ELEMENT_GENERATES.get(b) == a:
        return {"type": "B sinh A", "polarity": "lành",
                "narrative": f"{b.title()} sinh {a.title()} — B nuôi dưỡng A."}
    if ELEMENT_CONTROLS.get(a) == b:
        return {"type": "A khắc B", "polarity": "căng",
                "narrative": f"{a.title()} khắc {b.title()} — A áp chế B."}
    if ELEMENT_CONTROLS.get(b) == a:
        return {"type": "B khắc A", "polarity": "căng",
                "narrative": f"{b.title()} khắc {a.title()} — B áp chế A."}
    return {"type": "không tương quan", "polarity": "trung",
            "narrative": f"{a.title()} và {b.title()} không tương tác trực tiếp."}


def _branch_relation(b1: str, b2: str) -> list[dict]:
    """Quan hệ giữa 2 địa chi."""
    pair = frozenset([b1, b2])
    out = []
    if b1 == b2:
        out.append({"type": "đồng chi", "polarity": "trung",
                   "narrative": f"Cùng chi {b1} — đồng điệu."})
    if pair in LUC_HOP:
        el = LUC_HOP[pair]
        out.append({"type": "lục hợp", "polarity": "lành",
                   "narrative": f"{b1} + {b2} = lục hợp ({el.title()}) — ấm áp, hợp."})
    if pair in LUC_XUNG:
        out.append({"type": "lục xung", "polarity": "căng",
                   "narrative": f"{b1} ⚔ {b2} = lục xung — đối lập, biến động."})
    if pair in LUC_HAI:
        out.append({"type": "lục hại", "polarity": "căng",
                   "narrative": f"{b1} ✗ {b2} = lục hại — bất hòa ngầm."})
    for group in TAM_HINH_GROUPS:
        if b1 in group and b2 in group and b1 != b2:
            out.append({"type": "tương hình", "polarity": "căng",
                       "narrative": f"{b1} ⚖ {b2} = tương hình — va chạm."})
            break
    # Tam hợp
    for el, group in TAM_HOP.items():
        if b1 in group and b2 in group and b1 != b2:
            out.append({"type": "bán hợp cục", "polarity": "lành",
                       "narrative": f"{b1} + {b2} bán hợp {el.title()} cục."})
            break
    return out


def _ngu_hanh_dynamics(counts_a: dict, counts_b: dict, dung_a: str, dung_b: str) -> dict:
    """Phân tích A có thiếu hành nào mà B có thừa? Common Dụng Thần?"""
    total_a = sum(counts_a.values()) or 1
    total_b = sum(counts_b.values()) or 1
    a_thieu = [el for el, c in counts_a.items() if c <= 0.5]
    b_thieu = [el for el, c in counts_b.items() if c <= 0.5]
    a_thua = [el for el, c in counts_a.items() if c >= 3]
    b_thua = [el for el, c in counts_b.items() if c >= 3]

    # B bổ cho A?
    b_helps_a = []
    for el in a_thieu:
        if counts_b.get(el, 0) >= 1.5:
            b_helps_a.append(el)
    # A bổ cho B?
    a_helps_b = []
    for el in b_thieu:
        if counts_a.get(el, 0) >= 1.5:
            a_helps_b.append(el)
    common_dung = dung_a == dung_b

    narratives = []
    if b_helps_a:
        narratives.append(
            f"B BỔ cho A khí: {', '.join(el.title() for el in b_helps_a)}."
        )
    if a_helps_b:
        narratives.append(
            f"A BỔ cho B khí: {', '.join(el.title() for el in a_helps_b)}."
        )
    if common_dung:
        narratives.append(
            f"Cả 2 cùng Dụng Thần {dung_a.title()} → cùng hướng hợp khí."
        )
    if not narratives:
        narratives.append("Khí ngũ hành 2 bên độc lập — không bổ cho nhau, cũng không xung.")
    return {
        "a_thieu": a_thieu,
        "b_thieu": b_thieu,
        "a_thua": a_thua,
        "b_thua": b_thua,
        "b_helps_a": b_helps_a,
        "a_helps_b": a_helps_b,
        "common_dung_than": common_dung,
        "dung_a": dung_a,
        "dung_b": dung_b,
        "narrative": " ".join(narratives),
    }


def _spouse_check(chart_a: dict, chart_b: dict) -> dict | None:
    """Spouse-specific check (only when gender pair = nam + nữ)."""
    a_gender = chart_a.get("gender", "")
    b_gender = chart_b.get("gender", "")
    if {a_gender, b_gender} != {"nam", "nữ"}:
        return None
    nam = chart_a if a_gender == "nam" else chart_b
    nu = chart_b if a_gender == "nam" else chart_a
    nam_dm_el = nam["tu_tru"]["day_master"]["element"]
    nu_dm_el = nu["tu_tru"]["day_master"]["element"]

    # In Nam's chart, vợ = Tài tinh = element nam khắc
    vo_in_nam_el = ELEMENT_CONTROLS.get(nam_dm_el)
    # In Nữ's chart, chồng = Quan tinh = element khắc nữ
    chong_in_nu_el = None
    for el, target in ELEMENT_CONTROLS.items():
        if target == nu_dm_el:
            chong_in_nu_el = el
            break

    vo_match = vo_in_nam_el == nu_dm_el
    chong_match = chong_in_nu_el == nam_dm_el

    narrative = []
    if vo_match:
        narrative.append(
            f"Nữ DM {nu_dm_el.title()} TRÙNG element Tài tinh trong lá số Nam "
            f"({vo_in_nam_el.title()}) → vợ trong lá số chồng đúng."
        )
    if chong_match:
        narrative.append(
            f"Nam DM {nam_dm_el.title()} TRÙNG element Quan tinh trong lá số Nữ "
            f"({chong_in_nu_el.title()}) → chồng trong lá số vợ đúng."
        )
    if not narrative:
        narrative.append(
            "Day Master 2 bên không trùng với Tài/Quan tinh tương ứng — "
            "không có gắn kết Tài-Quan trực tiếp."
        )
    return {
        "nam_dm_el": nam_dm_el,
        "nu_dm_el": nu_dm_el,
        "vo_should_be_el": vo_in_nam_el,
        "chong_should_be_el": chong_in_nu_el,
        "vo_match": vo_match,
        "chong_match": chong_match,
        "narrative": " ".join(narrative),
    }


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_compatibility_v1"
SOURCE_REF = (
    "Nạp Âm + 5 hợp Can + Lục/Tam hợp chi (Thiệu Vĩ Hoa Q. 5-6 + tradition)."
)


def analyze_compatibility(chart_a: dict, chart_b: dict,
                           relationship_type: str = "spouse") -> dict:
    """So 2 lá số Bát Tự.

    Args:
        chart_a: Output of `cast_bat_tu(...)` for person A
        chart_b: Same for person B
        relationship_type: 'spouse' / 'parent_child' / 'partner' / 'sibling'

    Returns:
        Dict with comparison sections.
    """
    if "tu_tru" not in chart_a or "tu_tru" not in chart_b:
        raise ValueError("Both charts must contain 'tu_tru' key")

    a_year_stem = chart_a["tu_tru"]["pillars"]["year"]["stem"]
    a_year_branch = chart_a["tu_tru"]["pillars"]["year"]["branch"]
    b_year_stem = chart_b["tu_tru"]["pillars"]["year"]["stem"]
    b_year_branch = chart_b["tu_tru"]["pillars"]["year"]["branch"]

    a_dm = chart_a["tu_tru"]["day_master"]["stem"]
    b_dm = chart_b["tu_tru"]["day_master"]["stem"]
    a_dm_el = STEM_ELEMENT[a_dm]
    b_dm_el = STEM_ELEMENT[b_dm]
    a_day_branch = chart_a["tu_tru"]["pillars"]["day"]["branch"]
    b_day_branch = chart_b["tu_tru"]["pillars"]["day"]["branch"]

    # 1. Nạp Âm
    a_napam_el, a_napam_name = _nap_am(a_year_stem, a_year_branch)
    b_napam_el, b_napam_name = _nap_am(b_year_stem, b_year_branch)
    napam_relation = _element_relation(a_napam_el, b_napam_el)
    napam_section = {
        "a": {"name": a_napam_name, "element": a_napam_el,
              "ganzhi": f"{a_year_stem} {a_year_branch}"},
        "b": {"name": b_napam_name, "element": b_napam_el,
              "ganzhi": f"{b_year_stem} {b_year_branch}"},
        "relation": napam_relation,
    }

    # 2. Day Master compatibility
    dm_pair = frozenset([a_dm, b_dm])
    if dm_pair in HOP_CAN:
        hoa_el = HOP_CAN[dm_pair]
        dm_compat = {
            "type": "hợp can",
            "hoa_element": hoa_el,
            "polarity": "lành — rất hợp",
            "narrative": (
                f"Day Master 2 bên = {a_dm} + {b_dm} → 5 HỢP CAN, "
                f"hợp thành khí {hoa_el.title()}. Cấu hình tâm hợp ý."
            ),
        }
    else:
        dm_element_rel = _element_relation(a_dm_el, b_dm_el)
        dm_compat = {
            "type": "ngũ hành",
            "a_dm": a_dm, "a_el": a_dm_el,
            "b_dm": b_dm, "b_el": b_dm_el,
            **dm_element_rel,
        }

    # 3. Cung Phối
    cung_phoi = {
        "a_chi": a_day_branch,
        "b_chi": b_day_branch,
        "interactions": _branch_relation(a_day_branch, b_day_branch),
    }

    # 4. Ngũ hành dynamics
    dynamics = _ngu_hanh_dynamics(
        chart_a["ngu_hanh"]["counts"],
        chart_b["ngu_hanh"]["counts"],
        chart_a.get("dung_than", {}).get("dung_than_element", ""),
        chart_b.get("dung_than", {}).get("dung_than_element", ""),
    )

    # 5. Spouse-specific
    spouse = _spouse_check(chart_a, chart_b)

    # 6. Overall verdict — score from all sections
    score = 0
    if napam_relation["polarity"] == "lành":
        score += 2
    elif napam_relation["polarity"] == "căng":
        score -= 1
    if dm_compat.get("type") == "hợp can":
        score += 3
    elif dm_compat.get("polarity") == "lành":
        score += 1
    elif dm_compat.get("polarity") == "căng":
        score -= 1
    cp_lành = sum(1 for i in cung_phoi["interactions"] if i["polarity"] == "lành")
    cp_căng = sum(1 for i in cung_phoi["interactions"] if i["polarity"] == "căng")
    score += cp_lành * 2 - cp_căng * 2
    if dynamics["b_helps_a"] or dynamics["a_helps_b"]:
        score += 1
    if dynamics["common_dung_than"]:
        score += 1
    if spouse:
        if spouse["vo_match"]:
            score += 1
        if spouse["chong_match"]:
            score += 1

    if score >= 4:
        verdict_label = "rất thuận"
        verdict_narr = "Cấu hình tương tác RẤT thuận — nhiều điểm hợp, ít xung."
    elif score >= 2:
        verdict_label = "thuận"
        verdict_narr = "Cấu hình thuận — điểm hợp nhiều hơn điểm xung."
    elif score >= -1:
        verdict_label = "trung bình"
        verdict_narr = "Cấu hình trung bình — có cả thuận + xung, cần ý thức điều chỉnh."
    else:
        verdict_label = "thử thách"
        verdict_narr = "Cấu hình thử thách — nhiều xung khắc, cần kiên nhẫn + hóa giải có ý thức."

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "So 2 lá số KHÔNG dự đoán 2 anh chị sẽ ly hôn / hạnh phúc mãi. "
            "Đọc cấu trúc khí giữa 2 lá số → mô tả CHIỀU TƯƠNG TÁC, "
            "điểm hợp, điểm xung, hành nào bổ. Quan hệ là gặp gỡ có ý thức."
        ),
        "relationship_type": relationship_type,
        "nap_am": napam_section,
        "day_master_compat": dm_compat,
        "cung_phoi": cung_phoi,
        "ngu_hanh_dynamics": dynamics,
        "spouse_check": spouse,
        "overall": {
            "score": score,
            "label": verdict_label,
            "narrative": verdict_narr,
        },
        "closing": (
            "2 lá số là 2 cấu trúc khí gặp nhau. Tương tác là dòng chảy động, "
            "không phải kết quả định sẵn. Tử Bình cho thấy XU HƯỚNG — chất lượng "
            "quan hệ phụ thuộc kiến thức + ý thức chăm sóc của cả 2."
        ),
    }
