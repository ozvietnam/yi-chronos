"""Dụng Thần (用神) — favorable element / god heuristic.

Classical 子平 method:
- Day Master "vượng" (strong): need to drain or restrain → Dụng Thần ∈ {Thực/Thương, Tài, Quan/Sát}
- Day Master "nhược" (weak): need support → Dụng Thần ∈ {Ấn, Tỷ/Kiếp}
- Balanced: prefer the month-branch element OR the lacking element

Hỷ Thần (喜神) = secondary favorable, supports Dụng Thần.
Kỵ Thần (忌神) = unfavorable, opposite of Dụng Thần.

**v2 ADDS Điều Hậu (調候 — climate balance)** per critique #1 from bat_tu sage:
> "Kỷ Thổ sinh tháng Mùi (nóng khô) cần Thủy điều hậu hơn là Mộc khắc chế.
>  Nếu chỉ dùng cường độ thuần, Dụng Thần = Mộc sai hướng cải vận."

The climate matrix below is distilled from 窮通寶鑑 (the canonical climate text).
When strength-based and climate-based Dụng Thần agree → high confidence.
When they disagree → strength wins as primary, climate becomes Hỷ Thần (secondary).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import BRANCH_ELEMENT, ELEMENT_CONTROLS, ELEMENT_GENERATES, FIVE_ELEMENTS


# ─── Climate balance (Điều Hậu) ──────────────────────────────────────────────
#
# `CLIMATE_PREFERENCE[day_stem][month_branch]` → ordered list of preferred
# elements (most preferred first). Encodes the 寒/暖/燥/濕 (cold/warm/dry/wet)
# logic from 窮通寶鑑.
#
# Heuristic principles:
#  - Summer (Tỵ Ngọ Mùi)  — hot+dry  → all Day Masters benefit from Thủy
#  - Winter (Hợi Tý Sửu)  — cold+wet → all Day Masters benefit from Hỏa
#  - Spring (Dần Mão Thìn) — wet, growing → balance Hỏa + Thủy
#  - Autumn (Thân Dậu Tuất) — dry, cooling → Thủy still useful, sometimes Hỏa
#
# Per-stem refinements follow 窮通寶鑑 standard exits:
#  - Giáp/Ất Mộc: cần Thủy nuôi rễ + Hỏa khai hoa (tùy mùa)
#  - Bính/Đinh Hỏa: cần Thủy điều nhiệt (mùa hè), Mộc dẫn (mùa đông)
#  - Mậu/Kỷ Thổ: cần Thủy nhuận táo (mùa hè), Hỏa ấm (mùa đông)
#  - Canh/Tân Kim: cần Thủy tẩy (mùa hè), Hỏa luyện (mùa đông)
#  - Nhâm/Quý Thủy: cần Hỏa ấm (mùa đông), Mộc tiết (mùa hè)
#
# Returns up to 2 climate-preferred elements per (stem, branch).

_SUMMER = ("Tỵ", "Ngọ", "Mùi")
_WINTER = ("Hợi", "Tý", "Sửu")
_SPRING = ("Dần", "Mão", "Thìn")
_AUTUMN = ("Thân", "Dậu", "Tuất")


def _climate_preferences(day_stem: str, month_branch: str) -> tuple[list[str], str]:
    """Return (preferred_elements_list, vi_note).

    First element is the strongest climate need; second is secondary.
    """
    is_summer = month_branch in _SUMMER
    is_winter = month_branch in _WINTER
    is_spring = month_branch in _SPRING
    is_autumn = month_branch in _AUTUMN

    # Day stems grouped by element
    if day_stem in ("Giáp", "Ất"):           # 木 Mộc
        if is_summer: return ["thủy"], f"Mộc sinh hè ({month_branch}) — Thủy nhuận rễ, tránh khô héo"
        if is_winter: return ["hỏa", "thủy"], f"Mộc sinh đông ({month_branch}) — Hỏa ấm, Thủy không nên dư"
        if is_spring: return ["hỏa", "thủy"], f"Mộc sinh xuân ({month_branch}) — Hỏa khai hoa + Thủy duy trì"
        return ["thủy", "hỏa"], f"Mộc sinh thu ({month_branch}) — Thủy giữ sống + Hỏa luyện thân"

    if day_stem in ("Bính", "Đinh"):         # 火 Hỏa
        if is_summer: return ["thủy"], f"Hỏa sinh hè ({month_branch}) — nóng quá, BẮT BUỘC Thủy điều hậu"
        if is_winter: return ["mộc", "hỏa"], f"Hỏa sinh đông ({month_branch}) — Mộc dẫn lửa, lạnh quá"
        if is_spring: return ["mộc"], f"Hỏa sinh xuân ({month_branch}) — Mộc nuôi Hỏa"
        return ["mộc", "thủy"], f"Hỏa sinh thu ({month_branch}) — Mộc tiếp tế + Thủy cân bằng"

    if day_stem in ("Mậu", "Kỷ"):            # 土 Thổ
        if is_summer:
            # Critical case from sage critique: Kỷ Thổ sinh tháng Mùi
            return ["thủy"], (
                f"Thổ sinh hè ({month_branch}) — nóng khô, **Thủy điều hậu là Dụng Thần Điều Hậu**. "
                "Nếu thiếu Thủy, Thổ khô cằn không sinh vạn vật."
            )
        if is_winter: return ["hỏa"], f"Thổ sinh đông ({month_branch}) — lạnh ướt, Hỏa làm ấm + khô"
        if is_spring: return ["hỏa", "thủy"], f"Thổ sinh xuân ({month_branch}) — Hỏa khô đất, Thủy nuôi"
        return ["thủy"], f"Thổ sinh thu ({month_branch}) — khô, Thủy nhuận"

    if day_stem in ("Canh", "Tân"):          # 金 Kim
        if is_summer: return ["thủy"], f"Kim sinh hè ({month_branch}) — nóng, Thủy nguội kim"
        if is_winter: return ["hỏa"], f"Kim sinh đông ({month_branch}) — lạnh, Hỏa luyện kim"
        if is_spring: return ["thổ", "hỏa"], f"Kim sinh xuân ({month_branch}) — Thổ sinh + Hỏa luyện"
        return ["thủy"], f"Kim sinh thu ({month_branch}) — Kim vượng tự khắc, Thủy tiết"

    # Nhâm/Quý Thủy
    if is_summer: return ["kim", "thủy"], f"Thủy sinh hè ({month_branch}) — Kim nguồn + tự sinh"
    if is_winter: return ["hỏa"], f"Thủy sinh đông ({month_branch}) — Thủy vượng quá, BẮT BUỘC Hỏa ấm"
    if is_spring: return ["hỏa", "mộc"], f"Thủy sinh xuân ({month_branch}) — Hỏa ấm + Mộc tiết"
    return ["mộc"], f"Thủy sinh thu ({month_branch}) — Mộc dẫn nước"


def _element_generating(target: str) -> str:
    """Element that generates `target` (parent in Sinh cycle)."""
    for el, child in ELEMENT_GENERATES.items():
        if child == target:
            return el
    raise ValueError(f"Unknown element: {target}")


def _element_controlling(target: str) -> str:
    """Element that controls `target` (parent in Khắc cycle)."""
    for el, victim in ELEMENT_CONTROLS.items():
        if victim == target:
            return el
    raise ValueError(f"Unknown element: {target}")


def _pick_secondary_favorable(
    favorable_roles: list[str],
    dung_role: str,
    role_to_el: dict[str, str],
    element_counts: dict[str, float],
) -> str:
    """Pick the Hỷ Thần role: a favorable role (≠ dung) with the highest count.

    Tie-break by the order in `favorable_roles` (priority list). Guarantees the
    returned role is in the favorable group relative to the Day Master.
    """
    others = [r for r in favorable_roles if r != dung_role]
    if not others:
        return dung_role
    # Highest count first; stable order preserves priority on ties.
    return max(others, key=lambda r: element_counts.get(role_to_el[r], 0.0))


def classify_elements_role(day_element: str) -> dict[str, str]:
    """Map each of the 5 elements to its role relative to the Day Master.

    Returns: {element: role_tag} where role_tag ∈
        {'self', 'seal', 'output', 'wealth', 'pressure'}
    """
    dm = day_element
    return {
        dm: "self",                                # 比/劫 (same)
        _element_generating(dm): "seal",           # 印 (generates DM)
        ELEMENT_GENERATES[dm]: "output",           # 食/傷 (DM generates)
        ELEMENT_CONTROLS[dm]: "wealth",            # 財 (DM controls)
        _element_controlling(dm): "pressure",      # 官/殺 (controls DM)
    }


ROLE_VI: dict[str, str] = {
    "self":     "Tỷ Kiếp (đồng loại)",
    "seal":     "Ấn (sinh nhật chủ)",
    "output":   "Thực Thương (nhật chủ sinh)",
    "wealth":   "Tài (nhật chủ khắc)",
    "pressure": "Quan Sát (khắc nhật chủ)",
}

ROLE_GLYPH: dict[str, str] = {
    "self": "比/劫", "seal": "印", "output": "食/傷",
    "wealth": "財", "pressure": "官/殺",
}


@dataclass(frozen=True)
class DungThan:
    """Dụng Thần / Hỷ Thần / Kỵ Thần assessment (v2 — strength + climate)."""

    strength_tag: str               # 'strong' | 'weak' | 'balanced' | 'neutral'
    dung_than_element: str          # primary favorable element (strength-driven)
    dung_than_role: str             # role label
    dung_than_role_vi: str
    dung_than_reason: str
    hy_than_element: str            # secondary favorable
    hy_than_role: str
    ky_than_element: str            # unfavorable
    ky_than_role: str
    all_roles: dict[str, str]       # element → role for all 5 elements
    note: str
    # ─── v2 climate fields ──────────────────────────────────────────────────
    climate_dung_than: str | None = None        # element preferred by climate (Điều Hậu)
    climate_secondary: str | None = None        # secondary climate preference
    climate_reason: str | None = None           # vi explanation
    strength_climate_agree: bool | None = None  # do strength & climate agree?
    confidence: str = "medium"                  # 'high' (agree) | 'medium' | 'low' (disagree)

    def to_dict(self) -> dict:
        return asdict(self)


def determine_dung_than(
    *,
    day_element: str,
    element_counts: dict[str, float],
    strength_tag: str,
    month_branch_element: str | None = None,
    day_stem: str | None = None,
    month_branch: str | None = None,
) -> DungThan:
    """Compute Dụng Thần using strength heuristic + climate balance (v2).

    New params (optional, enable climate layer):
      - day_stem: Vietnamese stem of Day Master (e.g. "Kỷ") — needed for Điều Hậu
      - month_branch: Vietnamese month branch (e.g. "Mùi") — needed for Điều Hậu

    If either is missing, falls back to v1 strength-only logic (climate_* fields None).
    """
    roles = classify_elements_role(day_element)
    # Inverse: role → element
    role_to_el = {role: el for el, role in roles.items()}

    if strength_tag == "strong":
        # Strong DM: prefer to drain or restrain.
        # Favorable group (relative to NHẬT CHỦ): {食傷 output, 財 wealth, 官殺 pressure}.
        # Unfavorable group: {印 seal, 比劫 self} — these only add fuel to an already
        # strong DM. Priority for Dụng Thần: pressure → wealth → output (by count).
        favorable_roles = ["pressure", "wealth", "output"]
        # Among non-zero candidates, choose one with highest count.
        best_role = None
        best_count = -1.0
        for role in favorable_roles:
            el = role_to_el[role]
            if element_counts.get(el, 0) > best_count:
                best_count = element_counts[el]
                best_role = role
        if best_role is None:
            best_role = "pressure"
        dung_el = role_to_el[best_role]
        # Hỷ Thần = another FAVORABLE role (relative to DM), not derived from dung's
        # generating chain. Pick the favorable role ≠ dung with the highest count.
        hy_role = _pick_secondary_favorable(
            favorable_roles, best_role, role_to_el, element_counts
        )
        hy_el = role_to_el[hy_role]
        # Kỵ Thần = the element that fuels a strong DM most directly: 印 (seal).
        ky_role = "seal"
        ky_el = role_to_el[ky_role]
        reason = (
            f"Nhật chủ {day_element} vượng — cần tiết / khắc bớt sinh khí. "
            f"Chọn {ROLE_VI[best_role]} làm Dụng Thần (vai trò tiêu hao mạnh nhất hiện hữu). "
            f"Kỵ Ấn ({ky_el}) vì sinh thân càng vượng."
        )

    elif strength_tag == "weak":
        # Weak DM: prefer support.
        # Favorable group (relative to NHẬT CHỦ): {印 seal, 比劫 self}.
        # Unfavorable group: {官殺 pressure, 財 wealth, 食傷 output}.
        # Priority for Dụng Thần: seal (印) → self (比劫) by count.
        favorable_roles = ["seal", "self"]
        best_role = None
        best_count = -1.0
        for role in favorable_roles:
            el = role_to_el[role]
            if element_counts.get(el, 0) > best_count:
                best_count = element_counts[el]
                best_role = role
        if best_role is None:
            best_role = "seal"
        dung_el = role_to_el[best_role]
        # Hỷ Thần = the OTHER supporting role (印↔比劫), NOT _generating(dung) —
        # which for a weak DM would resolve to 官殺 (the element that controls DM).
        hy_role = "self" if best_role == "seal" else "seal"
        hy_el = role_to_el[hy_role]
        # Kỵ Thần = 官殺 (pressure) — the element that directly controls/harms the
        # already-weak Day Master.
        ky_role = "pressure"
        ky_el = role_to_el[ky_role]
        reason = (
            f"Nhật chủ {day_element} nhược — cần nguồn lực bồi dưỡng. "
            f"Chọn {ROLE_VI[best_role]} làm Dụng Thần (vai trò bổ trợ chính). "
            f"Kỵ Quan Sát ({ky_el}) vì khắc thân đang yếu."
        )

    else:
        # Balanced or neutral: use month branch element as Dụng Thần,
        # or pick the lowest-count element.
        if month_branch_element and element_counts.get(month_branch_element, 0) >= 1:
            dung_el = month_branch_element
            best_role = roles.get(dung_el, "self")
        else:
            # Find the element with lowest count to bring balance.
            sorted_els = sorted(element_counts.items(), key=lambda kv: kv[1])
            dung_el = sorted_els[0][0]
            best_role = roles.get(dung_el, "self")
        hy_el = _element_generating(dung_el)
        hy_role = roles.get(hy_el, "self")
        ky_el = _element_controlling(dung_el)
        ky_role = roles.get(ky_el, "self")
        reason = (
            f"Nhật chủ {day_element} cân bằng — Dụng Thần lấy theo nguyệt lệnh / "
            "hành thiếu hụt nhất để giữ thế hài hòa."
        )

    # ─── v2: Climate balance (Điều Hậu) ─────────────────────────────────────
    climate_primary: str | None = None
    climate_secondary: str | None = None
    climate_reason_text: str | None = None
    strength_climate_agree: bool | None = None
    confidence = "medium"

    if day_stem and month_branch:
        prefs, climate_reason_text = _climate_preferences(day_stem, month_branch)
        climate_primary = prefs[0] if prefs else None
        climate_secondary = prefs[1] if len(prefs) > 1 else None
        strength_climate_agree = (climate_primary == dung_el)

        if strength_climate_agree:
            confidence = "high"
            reason += f" Điều Hậu xác nhận: {climate_reason_text}"
        else:
            confidence = "low"
            # When strength and climate disagree, promote climate to Hỷ Thần
            # (replaces the auto-generated hy_el from "generates dung_el").
            old_hy = hy_el
            hy_el = climate_primary
            hy_role = roles.get(hy_el, "balanced")
            reason += (
                f" ⚠️ Cường độ chọn {dung_el} ({ROLE_VI[best_role]}) nhưng "
                f"Điều Hậu cần {climate_primary} ({climate_reason_text}). "
                f"Hỷ Thần được nâng từ {old_hy} → {climate_primary} để bù khí hậu. "
                "Cân nhắc đảo Dụng Thần ↔ Hỷ Thần nếu lá số nóng/lạnh nghiêm trọng."
            )

    v1_note = (
        "Heuristic v1 — chỉ dùng cường độ + nguyệt lệnh. "
        "子平 cổ điển còn xét điều hậu (寒/暖/燥/濕), thông căn (通根), "
        "và cách cục (格局). Phiên bản tinh chỉnh sang phase sau."
    )
    v2_note = (
        "Heuristic v2 — cường độ + Điều Hậu (窮通寶鑑). "
        "Còn cần thông căn (通根 xuyên thấu can-chi) + cách cục (格局) ở v3."
    )

    return DungThan(
        strength_tag=strength_tag,
        dung_than_element=dung_el,
        dung_than_role=best_role,
        dung_than_role_vi=ROLE_VI[best_role],
        dung_than_reason=reason,
        hy_than_element=hy_el,
        hy_than_role=hy_role,
        ky_than_element=ky_el,
        ky_than_role=ky_role,
        all_roles={el: roles[el] for el in FIVE_ELEMENTS},
        note=v2_note if (day_stem and month_branch) else v1_note,
        climate_dung_than=climate_primary,
        climate_secondary=climate_secondary,
        climate_reason=climate_reason_text,
        strength_climate_agree=strength_climate_agree,
        confidence=confidence,
    )


# ─── Cascade Dụng Thần (Thiệu Vĩ Hoa tr. 101-109) ───────────────────────────
# Mỗi tình huống → 2-3 dụng thần xếp hạng #1/#2/#3
# Paradigm: "Bệnh-Thuốc" — nguồn bệnh quyết định thứ tự thuốc.

def _dominant_role_against_dm(
    *, day_element: str, element_counts: dict[str, float]
) -> str:
    """Tìm role có count cao nhất (= nguồn 'bệnh' chính của mệnh cục).
    Returns one of: pressure, wealth, output, self, seal.
    """
    roles = classify_elements_role(day_element)
    role_counts: dict[str, float] = {}
    for el, role in roles.items():
        role_counts[role] = role_counts.get(role, 0) + element_counts.get(el, 0)
    # Day Master's own element ("self") = bản thân, không tính là bệnh
    role_counts.pop("self", None)
    if not role_counts:
        return "pressure"
    return max(role_counts.items(), key=lambda kv: kv[1])[0]


def determine_dung_than_cascade(
    *, day_element: str, element_counts: dict[str, float], strength_tag: str
) -> list[dict]:
    """Cascade Dụng Thần #1/#2/#3 theo Thiệu Vĩ Hoa tr. 101-109.

    Returns list of {rank, role, role_vi, element, reason}.

    5 trường hợp (Bệnh-Thuốc paradigm):
    - Weak + Quan Sát nhiều  → Ấn → Tỉ Kiếp
    - Weak + Tài nhiều        → Tỉ Kiếp → Ấn
    - Weak + Thực Thương nhiều → Ấn → Tỉ Kiếp
    - Strong + Ấn nhiều       → Tài → Quan Sát → Thực Thương
    - Strong + Tỉ Kiếp nhiều  → Quan Sát → Thực Thương → Tài
    """
    roles = classify_elements_role(day_element)
    role_to_el = {role: el for el, role in roles.items()}
    dominant = _dominant_role_against_dm(
        day_element=day_element, element_counts=element_counts
    )

    # Define cascade per situation
    if strength_tag == "weak":
        if dominant == "pressure":
            cascade_roles = ["seal", "self"]
            paradigm = "Nhược + Quan Sát nhiều → Ấn hóa Sát sinh thân + Tỉ Kiếp giúp đỡ"
        elif dominant == "wealth":
            cascade_roles = ["self", "seal"]
            paradigm = (
                "Nhược + Tài nhiều → Tỉ Kiếp giúp thân thắng tài + Ấn sinh thân. "
                "Của cải = mầm tai họa nếu thân không gánh nổi."
            )
        elif dominant == "output":
            cascade_roles = ["seal", "self"]
            paradigm = "Nhược + Thực Thương nhiều → Ấn vừa sinh thân vừa chế Thực Thương"
        else:
            cascade_roles = ["seal", "self"]
            paradigm = "Nhược chung — Ấn + Tỉ Kiếp giúp đỡ"
    elif strength_tag == "strong":
        if dominant == "seal":
            cascade_roles = ["wealth", "pressure", "output"]
            paradigm = (
                "Vượng + Ấn nhiều → Tài chế áp Ấn + hao thân. Quan Sát + Thực Thương "
                "là thuốc thứ hai/ba khi không có Tài."
            )
        elif dominant == "self":
            cascade_roles = ["pressure", "output", "wealth"]
            paradigm = (
                "Vượng + Tỉ Kiếp nhiều → Quan Sát chế áp Kiếp + Thực Thương xì hơi vượng. "
                "Tài là thuốc cuối khi không có 2 cái trên."
            )
        else:
            cascade_roles = ["pressure", "wealth", "output"]
            paradigm = "Vượng chung — Quan Sát + Tài + Thực Thương tiêu hao"
    else:
        # Trung hòa — không cần cascade dramatic
        return []

    cascade = []
    for rank, role in enumerate(cascade_roles, start=1):
        if role not in role_to_el:
            continue
        el = role_to_el[role]
        cascade.append({
            "rank": rank,
            "role": role,
            "role_vi": ROLE_VI[role],
            "element": el,
            "element_count_in_chart": element_counts.get(el, 0),
            "paradigm": paradigm if rank == 1 else "",
        })
    return cascade
