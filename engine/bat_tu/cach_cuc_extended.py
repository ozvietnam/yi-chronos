"""Cách Cục Extended — Tòng cách + Hóa Khí cách + Five Special patterns.

Engine v1 (`cach_cuc.py`) chỉ detect 10 cách phổ thông + 2 cách đặc biệt (Kiến Lộc, Dương Nhận)
qua bản khí Trụ Tháng. Đây là edge case: khi Day Master TOO EXTREME (nhược hẳn hoặc vượng hẳn),
classical Tử Bình áp dụng **paradigm đảo ngược** — không support Day Master mà "theo" khí mạnh nhất.

3 nhóm cách đặc biệt:

1. **Tòng cách (從格)** — 4 loại — khi Day Master extreme NHƯỢC + không có khí gốc:
   - Tòng Tài (從財): all Tài → theo Tài → Dụng Thần = Tài
   - Tòng Sát (從殺): all Sát → theo Sát → Dụng Thần = Sát
   - Tòng Nhi (從兒): all Thực/Thương → theo Output → Dụng Thần = Thực/Thương
   - Tòng Cường (從強): KHI extreme VƯỢNG + all Ấn/Tỷ → theo Cường → Dụng Thần = Tỷ/Kiếp

2. **Hóa Khí cách (化氣格)** — 5 loại — Day Master HỢP với can khác → biến thành element mới:
   - Giáp+Kỷ → hóa Thổ (sinh tháng Thìn/Tuất/Sửu/Mùi)
   - Ất+Canh → hóa Kim (sinh tháng Thân/Dậu/Tuất)
   - Bính+Tân → hóa Thủy (sinh tháng Hợi/Tý/Sửu)
   - Đinh+Nhâm → hóa Mộc (sinh tháng Dần/Mão/Thìn)
   - Mậu+Quý → hóa Hỏa (sinh tháng Tỵ/Ngọ/Mùi)

3. **Five Special (Ngũ Khí Triều Nguyên)** — 5 loại — lá số THUẦN 1 hành:
   - Khúc Trực (曲直): DM Mộc + ≥3 chi Mộc + không có Kim khắc
   - Viêm Thượng (炎上): DM Hỏa + ≥3 chi Hỏa + không có Thủy khắc
   - Giá Sắc (稼穡): DM Thổ + ≥3 chi Thổ + không có Mộc khắc
   - Tòng Cách (從革): DM Kim + ≥3 chi Kim + không có Hỏa khắc
   - Nhuận Hạ (潤下): DM Thủy + ≥3 chi Thủy + không có Thổ khắc

Khi detect 1 trong các pattern này → cập nhật Dụng Thần + Cách Cục label, KHÔNG dùng heuristic
vượng/nhược thường (sẽ chỉ ra sai hướng).

Reference: Tử Bình Chân Thuyên ch.7-9 + Trích Thiên Tủy ch.4 + Thiệu Vĩ Hoa Q. 4-5.

Public API:
- detect_extreme_pattern(pillars, day_master_stem, element_counts, dm_strength_diff) → dict | None
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .constants import (
    BRANCH_ELEMENT,
    BRANCH_HIDDEN_STEMS,
    EARTHLY_BRANCHES,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    STEM_ELEMENT,
)


# ─── Reference tables ────────────────────────────────────────────────────────

# 5 hợp Can — Hóa Khí
HOP_CAN: dict[frozenset, str] = {
    frozenset(["Giáp", "Kỷ"]): "thổ",
    frozenset(["Ất", "Canh"]): "kim",
    frozenset(["Bính", "Tân"]): "thủy",
    frozenset(["Đinh", "Nhâm"]): "mộc",
    frozenset(["Mậu", "Quý"]): "hỏa",
}

# Element → months (chi) it is vượng during
ELEMENT_VUONG_MONTHS: dict[str, set[str]] = {
    "mộc": {"Dần", "Mão", "Thìn"},
    "hỏa": {"Tỵ", "Ngọ", "Mùi"},
    "thổ": {"Thìn", "Tuất", "Sửu", "Mùi"},   # 4 tháng cuối mỗi mùa
    "kim": {"Thân", "Dậu", "Tuất"},
    "thủy": {"Hợi", "Tý", "Sửu"},
}

# Five Special pattern names (theo Day Master element)
FIVE_SPECIAL: dict[str, dict[str, str]] = {
    "mộc": {
        "name": "Khúc Trực cách (曲直格)",
        "essence": "Lá số toàn Mộc + Day Master Giáp/Ất + chi Mộc (Dần/Mão/Thìn/Hợi/Mùi đủ Tam Hợp Mộc cục) → mệnh thuần Mộc. "
                   "Thuộc 'Ngũ Khí Triều Nguyên'. Hợp khởi nghiệp ngành Mộc + giáo dục + y học cổ truyền.",
        "khac_by": "kim",
        "dung_than_element": "mộc",
        "hy_than_element": "thủy",
        "ky_than_element": "kim",
    },
    "hỏa": {
        "name": "Viêm Thượng cách (炎上格)",
        "essence": "Lá số toàn Hỏa + DM Bính/Đinh + chi Hỏa (Tỵ/Ngọ/Mùi/Dần/Tuất tam hợp Hỏa cục) → mệnh thuần Hỏa. "
                   "Hợp ngành Hỏa: ẩm thực, năng lượng, văn nghệ, truyền thông sáng tạo.",
        "khac_by": "thủy",
        "dung_than_element": "hỏa",
        "hy_than_element": "mộc",
        "ky_than_element": "thủy",
    },
    "thổ": {
        "name": "Giá Sắc cách (稼穡格)",
        "essence": "Lá số toàn Thổ + DM Mậu/Kỷ + 4 chi Thổ (Thìn/Tuất/Sửu/Mùi) → mệnh thuần Thổ. "
                   "Hợp bất động sản, nông nghiệp, kiến trúc.",
        "khac_by": "mộc",
        "dung_than_element": "thổ",
        "hy_than_element": "hỏa",
        "ky_than_element": "mộc",
    },
    "kim": {
        "name": "Tòng Cách cách (從革格)",
        "essence": "Lá số toàn Kim + DM Canh/Tân + chi Kim (Thân/Dậu/Tuất/Tỵ/Sửu tam hợp Kim cục) → mệnh thuần Kim. "
                   "Hợp quân đội, cơ khí, kim hoàn, leadership cứng.",
        "khac_by": "hỏa",
        "dung_than_element": "kim",
        "hy_than_element": "thổ",
        "ky_than_element": "hỏa",
    },
    "thủy": {
        "name": "Nhuận Hạ cách (潤下格)",
        "essence": "Lá số toàn Thủy + DM Nhâm/Quý + chi Thủy (Hợi/Tý/Sửu/Thân/Thìn tam hợp Thủy cục) → mệnh thuần Thủy. "
                   "Hợp hàng hải, y học, chiêm bốc, du lịch, công nghệ.",
        "khac_by": "thổ",
        "dung_than_element": "thủy",
        "hy_than_element": "kim",
        "ky_than_element": "thổ",
    },
}

# Tòng cách labels
TONG_CACH_LABELS: dict[str, dict[str, str]] = {
    "Tòng Tài": {
        "name": "Tòng Tài cách (從財格)",
        "essence": "Day Master cực nhược + không gốc + Tài tinh quá vượng → buộc 'theo Tài'. "
                   "Dụng Thần = Tài (đảo ngược heuristic thường). Hợp kinh doanh + tài chính + tài lộc theo môi trường.",
    },
    "Tòng Sát": {
        "name": "Tòng Sát cách (從殺格)",
        "essence": "Day Master cực nhược + Quan/Sát quá mạnh → 'theo Sát'. "
                   "Dụng Thần = Sát. Hợp môi trường cạnh tranh + áp lực cao + leadership ép buộc.",
    },
    "Tòng Nhi": {
        "name": "Tòng Nhi cách (從兒格)",
        "essence": "Day Master cực nhược + Thực/Thương quá vượng → 'theo Output'. "
                   "Dụng Thần = Thực/Thương + Tài. Hợp sáng tạo + nghệ thuật + biểu diễn.",
    },
    "Tòng Cường": {
        "name": "Tòng Cường cách (從強格)",
        "essence": "Day Master cực vượng + Ấn/Tỷ chiếm hầu hết → 'theo Cường'. "
                   "Dụng Thần = Tỷ/Kiếp + Ấn. Hợp leadership độc lập + tự lập + khởi nghiệp cá nhân.",
    },
}


# ─── Result type ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ExtremePatternResult:
    """Phát hiện 1 extreme pattern."""
    pattern_type: Literal["tong", "hoa", "special"]
    name: str
    essence: str
    dung_than_element: str
    hy_than_element: str
    ky_than_element: str
    confidence: Literal["high", "medium", "low"]
    notes: str

    def to_dict(self) -> dict:
        return {
            "pattern_type": self.pattern_type,
            "name": self.name,
            "essence": self.essence,
            "dung_than_element": self.dung_than_element,
            "hy_than_element": self.hy_than_element,
            "ky_than_element": self.ky_than_element,
            "confidence": self.confidence,
            "notes": self.notes,
        }


# ─── Detection logic ────────────────────────────────────────────────────────


def _count_element_total(element_counts: dict[str, float]) -> float:
    return sum(element_counts.values())


def _is_extreme_weak(dm_strength_diff: float, threshold: float = -6.0) -> bool:
    """Day Master nhược đến mức Tòng cách."""
    return dm_strength_diff <= threshold


def _is_extreme_strong(dm_strength_diff: float, threshold: float = 6.0) -> bool:
    """Day Master vượng đến mức Tòng Cường."""
    return dm_strength_diff >= threshold


def _check_five_special(pillars: dict, day_master_stem: str,
                         element_counts: dict[str, float]) -> ExtremePatternResult | None:
    """Five Special: Day Master + ≥3 chi cùng element + không khắc bởi element opposite."""
    dm_el = STEM_ELEMENT[day_master_stem]
    special = FIVE_SPECIAL.get(dm_el)
    if not special:
        return None
    # Count chi of dm_el
    chi_count = 0
    for pos in ("year", "month", "day", "hour"):
        if BRANCH_ELEMENT.get(pillars[pos]["branch"]) == dm_el:
            chi_count += 1
    if chi_count < 3:
        return None
    # Check no significant khắc element
    khac_el = special["khac_by"]
    khac_count = element_counts.get(khac_el, 0)
    total = _count_element_total(element_counts)
    if khac_count > total * 0.15:  # >15% = significant Kim if dm Mộc
        return None
    # Check ratio of dm_el is dominant
    dm_el_count = element_counts.get(dm_el, 0)
    if dm_el_count < total * 0.5:
        return None
    return ExtremePatternResult(
        pattern_type="special",
        name=special["name"],
        essence=special["essence"],
        dung_than_element=special["dung_than_element"],
        hy_than_element=special["hy_than_element"],
        ky_than_element=special["ky_than_element"],
        confidence="high" if chi_count >= 4 else "medium",
        notes=f"Day Master {day_master_stem} ({dm_el}), {chi_count}/4 chi {dm_el}, "
              f"khắc element {khac_el}: {khac_count:.1f}/{total:.1f}.",
    )


def _check_hoa_khi(pillars: dict, day_master_stem: str,
                    element_counts: dict[str, float]) -> ExtremePatternResult | None:
    """Hóa Khí: Day Master hợp Can ở Trụ Tháng/Giờ + tháng đúng element + không có khí khắc."""
    # Find candidate stem to hợp with day_master
    month_branch = pillars["month"]["branch"]
    candidates = []
    for pos in ("month", "hour", "year"):  # day_master is "day"
        stem = pillars[pos]["stem"]
        pair = frozenset([day_master_stem, stem])
        if pair in HOP_CAN:
            hoa_el = HOP_CAN[pair]
            if month_branch in ELEMENT_VUONG_MONTHS.get(hoa_el, set()):
                # Check no significant khắc element in chart
                khac_el = None
                for el, target in ELEMENT_CONTROLS.items():
                    if target == hoa_el:
                        khac_el = el
                        break
                khac_count = element_counts.get(khac_el, 0) if khac_el else 0
                total = _count_element_total(element_counts)
                if khac_count > total * 0.2:
                    continue  # has too much khắc, hóa fails
                candidates.append({
                    "hoa_el": hoa_el,
                    "pair": (day_master_stem, stem, pos),
                    "score": element_counts.get(hoa_el, 0) / max(total, 1),
                })
    if not candidates:
        return None
    # Take strongest hóa
    best = max(candidates, key=lambda c: c["score"])
    hoa_el = best["hoa_el"]
    # Hỷ Thần = element generating hoa_el
    hy_el = None
    for el, target in ELEMENT_GENERATES.items():
        if target == hoa_el:
            hy_el = el
            break
    # Kỵ Thần = element controlling hoa_el
    ky_el = None
    for el, target in ELEMENT_CONTROLS.items():
        if target == hoa_el:
            ky_el = el
            break
    return ExtremePatternResult(
        pattern_type="hoa",
        name=f"Hóa Khí cách — hóa {hoa_el.title()}",
        essence=(
            f"Day Master {day_master_stem} hợp với {best['pair'][1]} (trụ {best['pair'][2]}) → "
            f"biến thành khí {hoa_el.title()}. Tháng sinh thuộc {hoa_el} → 'chân hóa'. "
            f"Dụng Thần = khí hóa {hoa_el.title()} (đảo paradigm thường)."
        ),
        dung_than_element=hoa_el,
        hy_than_element=hy_el or hoa_el,
        ky_than_element=ky_el or "",
        confidence="medium" if best["score"] < 0.4 else "high",
        notes=f"Tỷ lệ {hoa_el} trong tổng khí: {best['score']*100:.0f}%.",
    )


def _check_tong_cach(pillars: dict, day_master_stem: str,
                      element_counts: dict[str, float],
                      thap_than_dist: dict, dm_strength_diff: float) -> ExtremePatternResult | None:
    """Tòng cách: Day Master cực nhược + 1 nhóm Thập Thần chiếm gần hết."""
    if not _is_extreme_weak(dm_strength_diff):
        # Also check Tòng Cường (extreme strong + all support)
        if _is_extreme_strong(dm_strength_diff):
            return _check_tong_cuong(day_master_stem, element_counts, thap_than_dist, dm_strength_diff)
        return None

    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0
    total = sum(combined.values()) or 1

    dm_el = STEM_ELEMENT[day_master_stem]
    # Tòng Tài: Tài chiếm ≥50% + DM nhược
    tai_score = combined.get("Chính Tài", 0) + combined.get("Thiên Tài", 0)
    sat_score = combined.get("Chính Quan", 0) + combined.get("Thất Sát", 0)
    thuc_score = combined.get("Thực Thần", 0) + combined.get("Thương Quan", 0)

    # Find the most dominant group
    groups = [
        ("Tòng Tài", tai_score, ELEMENT_CONTROLS[dm_el]),
        ("Tòng Sát", sat_score, _find_controller(dm_el)),
        ("Tòng Nhi", thuc_score, ELEMENT_GENERATES[dm_el]),
    ]
    groups.sort(key=lambda g: -g[1])
    name, score, target_el = groups[0]
    if score < total * 0.45:
        return None
    if not target_el:
        return None

    info = TONG_CACH_LABELS[name]
    # Hỷ Thần for Tòng = sinh ra Dụng (Tòng Tài → Hỷ = Thực Thương)
    hy_el = None
    for el, target in ELEMENT_GENERATES.items():
        if target == target_el:
            hy_el = el
            break
    # Kỵ Thần = khắc Dụng (Tòng Tài Dụng=Tài → Kỵ = Tỷ/Kiếp = dm_el)
    ky_el = dm_el  # Day Master element becomes Kỵ in Tòng cases
    return ExtremePatternResult(
        pattern_type="tong",
        name=info["name"],
        essence=info["essence"],
        dung_than_element=target_el,
        hy_than_element=hy_el or target_el,
        ky_than_element=ky_el,
        confidence="medium" if score < total * 0.6 else "high",
        notes=f"Day Master nhược (diff={dm_strength_diff:.1f}), nhóm dominant '{name}' chiếm {score/total*100:.0f}%.",
    )


def _check_tong_cuong(day_master_stem: str, element_counts: dict[str, float],
                       thap_than_dist: dict, dm_strength_diff: float) -> ExtremePatternResult | None:
    """Tòng Cường: DM cực vượng + Ấn + Tỷ/Kiếp chiếm ≥70%."""
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0
    total = sum(combined.values()) or 1
    cuong_score = (combined.get("Chính Ấn", 0) + combined.get("Thiên Ấn", 0)
                    + combined.get("Tỷ Kiên", 0) + combined.get("Kiếp Tài", 0))
    if cuong_score < total * 0.7:
        return None
    dm_el = STEM_ELEMENT[day_master_stem]
    info = TONG_CACH_LABELS["Tòng Cường"]
    return ExtremePatternResult(
        pattern_type="tong",
        name=info["name"],
        essence=info["essence"],
        dung_than_element=dm_el,
        hy_than_element=_find_generator(dm_el) or dm_el,
        ky_than_element=ELEMENT_CONTROLS[dm_el],
        confidence="high",
        notes=f"DM cực vượng (diff={dm_strength_diff:.1f}), Ấn+Tỷ chiếm {cuong_score/total*100:.0f}%.",
    )


def _find_controller(element: str) -> str | None:
    """Element nào khắc target."""
    for el, target in ELEMENT_CONTROLS.items():
        if target == element:
            return el
    return None


def _find_generator(element: str) -> str | None:
    """Element nào sinh target."""
    for el, target in ELEMENT_GENERATES.items():
        if target == element:
            return el
    return None


# ─── Public API ─────────────────────────────────────────────────────────────


def detect_extreme_pattern(
    pillars: dict,
    day_master_stem: str,
    element_counts: dict[str, float],
    thap_than_dist: dict,
    dm_strength_diff: float,
) -> dict | None:
    """Detect 1 extreme cách cục pattern (Five Special > Hóa Khí > Tòng).

    Args:
        pillars: 4 trụ dict
        day_master_stem: Vietnamese can name
        element_counts: from `count_elements()`
        thap_than_dist: from cast_bat_tu output (visible + hidden)
        dm_strength_diff: support - drain (from day_master_assessment)

    Returns:
        Dict with extreme pattern info, or None if no extreme pattern detected.

    Priority: Five Special > Hóa Khí > Tòng (since they overlap).
    """
    # 1. Five Special (purest form)
    result = _check_five_special(pillars, day_master_stem, element_counts)
    if result:
        return result.to_dict()

    # 2. Hóa Khí (transform)
    result = _check_hoa_khi(pillars, day_master_stem, element_counts)
    if result:
        return result.to_dict()

    # 3. Tòng cách (follow)
    result = _check_tong_cach(pillars, day_master_stem, element_counts,
                                thap_than_dist, dm_strength_diff)
    if result:
        return result.to_dict()

    return None
