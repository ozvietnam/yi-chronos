"""Lưu Niên (流年) — annual analysis: how the current year flows through the chart.

Lưu Niên là tầng phân tích zoom-in từ Đại Vận (10 năm) xuống 1 năm cụ thể —
sau đó xuống 12 tháng (Lưu Nguyệt) nếu user muốn.

Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (Chương 3+ và rải rác Q. 4-5
về Lưu Niên Sát).

Paradigm (Iron Rule #4+6): Tử Bình KHÔNG dự đoán "năm nay sẽ giàu". Lưu Niên
phản chiếu **cấu hình khí của năm hiện tại** đi qua lá số + Đại Vận. Mục đích:
biết năm nay đang ở đâu trong tổng thể → cân bằng (Bổ) phù hợp.

Algorithm:
1. Lưu Niên Trụ (Can-Chi năm hiện tại) — qua chronos (Lập Xuân boundary)
2. Thập Thần của Lưu Niên Can vs Day Master → "năm nay là năm Thần gì"
3. Tương tác Chi Lưu Niên với 4 trụ gốc (lục hợp/lục xung/tam hợp/hình/hại)
4. Tương tác Lưu Niên với Đại Vận hiện tại (cùng cấu hình hay đối lập)
5. Đánh giá Lưu Niên vs Dụng/Hỷ/Kỵ Thần (thuận/nghịch/trung tính)
6. (Optional) Lưu Nguyệt — 12 tháng dùng "Ngũ Hổ Độn" công thức
7. Bổ Hướng cho năm: nhấn mạnh Dụng Thần, dùng tháng thuận làm việc lớn
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .constants import (
    BRANCH_ELEMENT,
    EARTHLY_BRANCHES,
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    HEAVENLY_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
)
from .thap_than import thap_than_of


# ─── Reference tables ────────────────────────────────────────────────────────

# Lục Hợp (六合) — 6 cặp địa chi hợp lành
LUC_HOP: dict[frozenset, str] = {
    frozenset(["Tý", "Sửu"]): "thổ",
    frozenset(["Dần", "Hợi"]): "mộc",
    frozenset(["Mão", "Tuất"]): "hỏa",
    frozenset(["Thìn", "Dậu"]): "kim",
    frozenset(["Tỵ", "Thân"]): "thủy",
    frozenset(["Ngọ", "Mùi"]): "hỏa",
}

# Lục Xung (六沖) — 6 cặp địa chi đối xung
LUC_XUNG: set[frozenset] = {
    frozenset(["Tý", "Ngọ"]),
    frozenset(["Sửu", "Mùi"]),
    frozenset(["Dần", "Thân"]),
    frozenset(["Mão", "Dậu"]),
    frozenset(["Thìn", "Tuất"]),
    frozenset(["Tỵ", "Hợi"]),
}

# Tam Hợp (三合) — 3 chi tạo thành cục (mạnh nhất)
TAM_HOP: dict[str, frozenset] = {
    "thủy": frozenset(["Thân", "Tý", "Thìn"]),
    "mộc": frozenset(["Hợi", "Mão", "Mùi"]),
    "hỏa": frozenset(["Dần", "Ngọ", "Tuất"]),
    "kim": frozenset(["Tỵ", "Dậu", "Sửu"]),
}

# Lục Hại (六害) — 6 cặp hại nhau
LUC_HAI: set[frozenset] = {
    frozenset(["Tý", "Mùi"]),
    frozenset(["Sửu", "Ngọ"]),
    frozenset(["Dần", "Tỵ"]),
    frozenset(["Mão", "Thìn"]),
    frozenset(["Thân", "Hợi"]),
    frozenset(["Dậu", "Tuất"]),
}

# Tam Hình (三刑) — Dần-Tỵ-Thân (vô lễ), Sửu-Tuất-Mùi (thị thế), Tý-Mão (vô lễ)
TAM_HINH_GROUPS: list[frozenset] = [
    frozenset(["Dần", "Tỵ", "Thân"]),    # Vô lễ
    frozenset(["Sửu", "Tuất", "Mùi"]),   # Thị thế (cậy quyền)
]
TUONG_HINH: set[frozenset] = {
    frozenset(["Tý", "Mão"]),  # Vô lễ
}
TU_HINH: set[str] = {"Thìn", "Ngọ", "Dậu", "Hợi"}  # tự hình (chi tự hình)

# Ngũ Hổ Độn (五虎遁) — Năm Can → Can tháng Dần đầu năm
NGU_HO_DON: dict[str, str] = {
    "Giáp": "Bính", "Kỷ": "Bính",
    "Ất": "Mậu", "Canh": "Mậu",
    "Bính": "Canh", "Tân": "Canh",
    "Đinh": "Nhâm", "Nhâm": "Nhâm",
    "Mậu": "Giáp", "Quý": "Giáp",
}

# 12 tháng theo Tiết khí (mỗi tháng bắt đầu tại 1 tiết)
MONTH_BRANCHES: tuple[str, ...] = (
    "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
    "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu",
)
MONTH_TIET_KHI: tuple[str, ...] = (
    "Lập Xuân", "Kinh Trập", "Thanh Minh", "Lập Hạ", "Mang Chủng", "Tiểu Thử",
    "Lập Thu", "Bạch Lộ", "Hàn Lộ", "Lập Đông", "Đại Tuyết", "Tiểu Hàn",
)


# ─── Core computation ───────────────────────────────────────────────────────


def compute_luu_nien_pillar_by_year(year: int) -> dict:
    """Compute Lưu Niên Trụ (year pillar) for a given solar year using formula.

    Reference: 1984 = Giáp Tý (60-year cycle anchor).
    Note: this is calendar-year approximation — for accurate Tử Bình year
    boundary (Lập Xuân), use `compute_luu_nien_pillar_now()`.
    """
    n = (year - 1984) % 60
    stem = HEAVENLY_STEMS[n % 10]
    branch = EARTHLY_BRANCHES[n % 12]
    return {
        "year_solar": year,
        "stem": stem,
        "branch": branch,
        "stem_element": STEM_ELEMENT[stem],
        "branch_element": BRANCH_ELEMENT[branch],
        "stem_polarity": STEM_POLARITY[stem],
    }


def compute_luu_nien_pillar_now(timezone: str = "Asia/Ho_Chi_Minh",
                                 reference_dt: str | None = None) -> dict:
    """Compute Lưu Niên via chronos (respects Lập Xuân boundary)."""
    from core.chronos import calculate_chronos_state
    chronos = calculate_chronos_state(reference_dt, timezone)
    gz_year = chronos.ganzhi.year  # e.g. "Bính Ngọ"
    parts = gz_year.split()
    if len(parts) != 2:
        # Fallback to formula
        if reference_dt:
            year = int(reference_dt[:4])
        else:
            year = datetime.now(ZoneInfo(timezone)).year
        return compute_luu_nien_pillar_by_year(year)
    stem, branch = parts
    # Determine solar year context
    if reference_dt:
        try:
            year = int(reference_dt[:4])
        except (ValueError, IndexError):
            year = datetime.now(ZoneInfo(timezone)).year
    else:
        year = datetime.now(ZoneInfo(timezone)).year
    return {
        "year_solar": year,
        "stem": stem,
        "branch": branch,
        "stem_element": STEM_ELEMENT[stem],
        "branch_element": BRANCH_ELEMENT[branch],
        "stem_polarity": STEM_POLARITY[stem],
    }


def _branch_interaction(b1: str, b2: str) -> list[dict]:
    """Detect all interactions between 2 địa chi."""
    out = []
    pair = frozenset([b1, b2])
    if b1 == b2:
        if b1 in TU_HINH:
            out.append({"type": "tự hình", "polarity": "hung",
                       "narrative": f"{b1} tự hình — cùng chi gặp lại có thể tăng cường tiêu cực."})
        else:
            out.append({"type": "đồng chi", "polarity": "trung",
                       "narrative": f"{b1} trùng — gốc cũ thêm gốc mới, tăng cường tính chất chi."})
    elif pair in LUC_HOP:
        el = LUC_HOP[pair]
        out.append({"type": "lục hợp", "polarity": "lành", "transforms_to": el,
                   "narrative": f"{b1} + {b2} = lục hợp → khí hợp thành {el.title()}, năm thuận tình duyên / quan hệ."})
    elif pair in LUC_XUNG:
        out.append({"type": "lục xung", "polarity": "hung",
                   "narrative": f"{b1} ⚔ {b2} = lục xung → đối lập 180°, năm có biến động (di chuyển / chia tay / khởi nghiệp)."})
    elif pair in LUC_HAI:
        out.append({"type": "lục hại", "polarity": "hung",
                   "narrative": f"{b1} ✗ {b2} = lục hại → bất hòa ngấm ngầm, cẩn trọng quan hệ."})
    # Tam Hình
    for group in TAM_HINH_GROUPS:
        if b1 in group and b2 in group and b1 != b2:
            out.append({"type": "tương hình", "polarity": "hung",
                       "narrative": f"{b1} ⚖ {b2} = tương hình (thuộc nhóm {'-'.join(sorted(group))}), kiện tụng / khắc khẩu."})
            break
    if pair in TUONG_HINH:
        out.append({"type": "tương hình (vô lễ)", "polarity": "hung",
                   "narrative": f"{b1} ⚖ {b2} = tương hình vô lễ, gia đình bất ổn."})
    return out


def _luu_nien_vs_chart(luu_nien: dict, pillars: dict, day_master: str) -> dict:
    """Phân tích tương tác Lưu Niên với 4 trụ gốc."""
    ln_branch = luu_nien["branch"]
    ln_stem = luu_nien["stem"]
    interactions = {}
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        chi_inter = _branch_interaction(ln_branch, p["branch"])
        # Stem-stem interaction: same → trợ; ngũ hành sinh khắc
        stem_inter = _stem_interaction(ln_stem, p["stem"])
        interactions[pos] = {
            "pillar_position_vi": p.get("position_vi", pos),
            "natal_stem": p["stem"],
            "natal_branch": p["branch"],
            "chi_interactions": chi_inter,
            "stem_interaction": stem_inter,
        }
    # Tam Hợp / Tam Hội detection across 4 pillars + Lưu Niên
    natal_branches = {p["branch"] for p in pillars.values()}
    all_branches = natal_branches | {ln_branch}
    tam_hop = []
    for el, group in TAM_HOP.items():
        if group.issubset(all_branches) and ln_branch in group:
            tam_hop.append({
                "element": el,
                "branches": sorted(group),
                "narrative": f"Năm nay + lá số tạo TAM HỢP cục {el.title()} ({'+'.join(sorted(group))}) → khí {el.title()} cực vượng.",
            })
        elif ln_branch in group:
            present = group & all_branches
            if len(present) == 2:
                missing = next(iter(group - present))
                tam_hop.append({
                    "element": el,
                    "branches": sorted(present),
                    "type": "bán hợp",
                    "narrative": f"Năm nay tạo BÁN HỢP cục {el.title()} ({'+'.join(sorted(present))}), khí {el.title()} tăng. Chi {missing} sẽ kích hoạt cục đầy đủ nếu xuất hiện ở Lưu Nguyệt.",
                })
    return {
        "vs_pillars": interactions,
        "tam_hop_detected": tam_hop,
    }


def _stem_interaction(s1: str, s2: str) -> dict:
    """Quan hệ giữa 2 thiên can: same / sinh / khắc."""
    if s1 == s2:
        return {"type": "đồng can", "polarity": "trung",
                "narrative": f"{s1} trùng — tăng cường khí can."}
    e1, e2 = STEM_ELEMENT[s1], STEM_ELEMENT[s2]
    if e1 == e2:
        return {"type": "tỷ hòa", "polarity": "trung",
                "narrative": f"{s1} ↔ {s2} cùng hành {e1.title()} → tỷ hòa, trợ giúp."}
    if ELEMENT_GENERATES[e1] == e2:
        return {"type": "ta sinh", "polarity": "lành",
                "narrative": f"{s1} ({e1.title()}) → sinh {s2} ({e2.title()})."}
    if ELEMENT_GENERATES[e2] == e1:
        return {"type": "sinh ta", "polarity": "lành",
                "narrative": f"{s2} ({e2.title()}) → sinh {s1} ({e1.title()})."}
    if ELEMENT_CONTROLS[e1] == e2:
        return {"type": "ta khắc", "polarity": "trung",
                "narrative": f"{s1} ({e1.title()}) → khắc {s2} ({e2.title()})."}
    if ELEMENT_CONTROLS[e2] == e1:
        return {"type": "khắc ta", "polarity": "hung",
                "narrative": f"{s2} ({e2.title()}) → khắc {s1} ({e1.title()})."}
    return {"type": "không tương quan", "polarity": "trung", "narrative": ""}


def _evaluate_vs_dung_than(luu_nien: dict, dung_than: dict) -> dict:
    """Đánh giá Lưu Niên vs Dụng/Hỷ/Kỵ Thần — verdict tổng cho năm."""
    dung_el = dung_than.get("dung_than_element", "")
    hy_el = dung_than.get("hy_than_element", "")
    ky_el = dung_than.get("ky_than_element", "")
    ln_stem_el = luu_nien["stem_element"]
    ln_branch_el = luu_nien["branch_element"]
    elements = {ln_stem_el, ln_branch_el}

    matches_dung = dung_el in elements
    matches_hy = hy_el in elements
    matches_ky = ky_el in elements

    if matches_dung and not matches_ky:
        verdict = "thuận"
        narrative = (
            f"✦ Lưu Niên có khí {dung_el.title()} = **Dụng Thần** → năm THUẬN. "
            f"Đây là thời cơ tốt để khởi sự, đẩy mạnh, cân bằng cấu trúc khí."
        )
    elif matches_ky and not matches_dung:
        verdict = "thử thách"
        narrative = (
            f"⚠ Lưu Niên có khí {ky_el.title()} = **Kỵ Thần** → năm THỬ THÁCH. "
            f"Tăng cường Bổ Dụng Thần ({dung_el.title()}) qua nghề/môi trường/ẩm thực để hóa giải."
        )
    elif matches_dung and matches_ky:
        verdict = "hỗn tạp"
        narrative = (
            f"⚖ Lưu Niên vừa có Dụng Thần ({dung_el.title()}) vừa có Kỵ Thần ({ky_el.title()}) → "
            f"năm HỖN TẠP. Cơ hội + thử thách song hành — cần chọn lọc."
        )
    elif matches_hy:
        verdict = "thuận nhẹ"
        narrative = (
            f"✧ Lưu Niên có khí {hy_el.title()} = Hỷ Thần (sinh Dụng Thần) → năm thuận nhẹ, "
            f"phù hợp tích lũy + chuẩn bị."
        )
    else:
        verdict = "trung tính"
        narrative = (
            f"Lưu Niên khí {ln_stem_el.title()}/{ln_branch_el.title()} trung tính so với Dụng Thần — "
            f"không hỗ trợ mạnh nhưng cũng không cản. Năm bình ổn để duy trì."
        )
    return {
        "verdict": verdict,
        "matches_dung_than": matches_dung,
        "matches_hy_than": matches_hy,
        "matches_ky_than": matches_ky,
        "narrative": narrative,
    }


def _evaluate_vs_dai_van(luu_nien: dict, current_cycle: dict | None) -> dict:
    """Đánh giá Lưu Niên vs Đại Vận hiện tại."""
    if not current_cycle:
        return {
            "current_dai_van": None,
            "narrative": "Chưa xác định Đại Vận hiện tại (cần cung cấp current_age).",
        }
    dv_stem = current_cycle.get("stem", "")
    dv_branch = current_cycle.get("branch", "")
    dv_stem_el = STEM_ELEMENT.get(dv_stem, "")
    dv_branch_el = BRANCH_ELEMENT.get(dv_branch, "")
    ln_stem = luu_nien["stem"]
    ln_branch = luu_nien["branch"]

    # Stem-stem
    stem_inter = _stem_interaction(ln_stem, dv_stem)
    # Branch-branch
    chi_inter = _branch_interaction(ln_branch, dv_branch)

    return {
        "current_dai_van": {
            "stem": dv_stem,
            "branch": dv_branch,
            "stem_element": dv_stem_el,
            "branch_element": dv_branch_el,
            "start_age": current_cycle.get("start_age"),
            "end_age": current_cycle.get("end_age"),
        },
        "stem_interaction": stem_inter,
        "chi_interactions": chi_inter,
        "narrative": (
            f"Lưu Niên **{ln_stem} {ln_branch}** vs Đại Vận **{dv_stem} {dv_branch}** "
            f"({current_cycle.get('start_age')}-{current_cycle.get('end_age')} tuổi). "
            f"Can: {stem_inter['narrative']}"
            + (f" Chi: {chi_inter[0]['narrative']}" if chi_inter else "")
        ),
    }


def _compute_luu_nguyet(year_stem: str, year: int) -> list[dict]:
    """12 tháng — Lưu Nguyệt — qua Ngũ Hổ Độn.

    Returns list of {month_index, branch, stem, tiet_khi, narrative}.
    """
    start_stem = NGU_HO_DON.get(year_stem)
    if not start_stem:
        return []
    start_idx = HEAVENLY_STEMS.index(start_stem)
    months = []
    for m_idx, (branch, tiet) in enumerate(zip(MONTH_BRANCHES, MONTH_TIET_KHI)):
        stem = HEAVENLY_STEMS[(start_idx + m_idx) % 10]
        months.append({
            "month_solar": m_idx + 2 if m_idx + 2 <= 12 else (m_idx + 2 - 12),  # rough: Dần ≈ tháng 2 DL
            "month_index": m_idx + 1,  # 1=Dần ... 12=Sửu
            "stem": stem,
            "branch": branch,
            "stem_element": STEM_ELEMENT[stem],
            "branch_element": BRANCH_ELEMENT[branch],
            "tiet_khi": tiet,
        })
    return months


def _evaluate_luu_nguyet(months: list[dict], dung_than: dict, day_master: str) -> list[dict]:
    """Score each month vs Dụng/Kỵ thần + Thập Thần."""
    dung_el = dung_than.get("dung_than_element", "")
    ky_el = dung_than.get("ky_than_element", "")
    out = []
    for m in months:
        stem_el = m["stem_element"]
        branch_el = m["branch_element"]
        elements = {stem_el, branch_el}
        tt = thap_than_of(day_master, m["stem"])
        if dung_el in elements and ky_el not in elements:
            verdict = "thuận"
            short = "✦"
        elif ky_el in elements and dung_el not in elements:
            verdict = "thử thách"
            short = "⚠"
        elif dung_el in elements and ky_el in elements:
            verdict = "hỗn tạp"
            short = "⚖"
        else:
            verdict = "trung"
            short = "·"
        out.append({**m, "verdict": verdict, "short_marker": short, "thap_than": tt})
    return out


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_luu_nien_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ. Lưu Niên + Lưu Nguyệt "
    "theo công thức Ngũ Hổ Độn + Tiết khí (Q. 4-5)."
)


def analyze_luu_nien(
    bat_tu_state: dict,
    *,
    current_age: int | None = None,
    target_year: int | None = None,
    timezone: str = "Asia/Ho_Chi_Minh",
    include_luu_nguyet: bool = True,
) -> dict:
    """Phân tích Lưu Niên — năm hiện tại đi qua lá số.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.
        current_age: Optional. Used to detect current Đại Vận cycle.
        target_year: Optional solar year (default = current year ICT).
        timezone: For "now" computation.
        include_luu_nguyet: Compute 12 tháng breakdown.

    Returns:
        Structured analysis dict ready for API/UI.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    # 1. Lưu Niên Pillar
    if target_year is None:
        target_year = datetime.now(ZoneInfo(timezone)).year
    # Use chronos for accurate Lập Xuân boundary if target_year == current year
    now = datetime.now(ZoneInfo(timezone))
    if target_year == now.year:
        luu_nien = compute_luu_nien_pillar_now(timezone=timezone)
    else:
        # Default to mid-year date for past/future computation via chronos
        ref_dt = f"{target_year}-06-15T12:00"
        luu_nien = compute_luu_nien_pillar_now(timezone=timezone, reference_dt=ref_dt)

    # 2. Thập Thần của Lưu Niên
    day_master = bat_tu_state["tu_tru"]["day_master"]["stem"]
    luu_nien_thap_than = thap_than_of(day_master, luu_nien["stem"])
    luu_nien["thap_than_vs_dm"] = luu_nien_thap_than

    # 3. Tương tác Lưu Niên vs 4 trụ gốc
    pillars = bat_tu_state["tu_tru"]["pillars"]
    vs_chart = _luu_nien_vs_chart(luu_nien, pillars, day_master)

    # 4. Tương tác Lưu Niên vs Đại Vận hiện tại
    current_cycle = None
    if current_age is not None:
        for c in bat_tu_state.get("dai_van", {}).get("cycles", []):
            if c.get("start_age", 0) <= current_age <= c.get("end_age", 999):
                current_cycle = c
                break
    vs_dai_van = _evaluate_vs_dai_van(luu_nien, current_cycle)

    # 5. Đánh giá tổng vs Dụng Thần
    dung_than = bat_tu_state.get("dung_than", {})
    overall = _evaluate_vs_dung_than(luu_nien, dung_than)

    # 6. Lưu Nguyệt
    months = []
    if include_luu_nguyet:
        raw_months = _compute_luu_nguyet(luu_nien["stem"], target_year)
        months = _evaluate_luu_nguyet(raw_months, dung_than, day_master)

    # 7. Bổ Hướng cho năm
    bo_narrative = (
        f"Cả năm {target_year} ({luu_nien['stem']} {luu_nien['branch']}): "
        f"Bổ Dụng Thần **{dung_than.get('dung_than_element', '').title()}** "
        f"+ Hỷ Thần **{dung_than.get('hy_than_element', '').title()}**. "
    )
    # Recommend best months
    if months:
        good_months = [m for m in months if m["verdict"] == "thuận"]
        bad_months = [m for m in months if m["verdict"] == "thử thách"]
        if good_months:
            bo_narrative += (
                f"Tháng thuận lợi: "
                + ", ".join(f"tháng {m['month_index']} ({m['branch']})" for m in good_months[:4])
                + ". "
            )
        if bad_months:
            bo_narrative += (
                f"Tháng cần đề phòng: "
                + ", ".join(f"tháng {m['month_index']} ({m['branch']})" for m in bad_months[:4])
                + "."
            )

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Lưu Niên KHÔNG dự đoán năm nay anh thành/bại. "
            "Lưu Niên phản chiếu cấu hình khí năm hiện tại đi qua lá số. "
            "Mục đích: biết năm nay ở đâu trong tổng thể → cân bằng (Bổ) phù hợp."
        ),
        "target_year": target_year,
        "luu_nien": luu_nien,
        "vs_chart": vs_chart,
        "vs_dai_van": vs_dai_van,
        "overall_verdict": overall,
        "luu_nguyet": months,
        "bo_huong_nam": {
            "narrative": bo_narrative,
            "dung_than_element": dung_than.get("dung_than_element"),
            "hy_than_element": dung_than.get("hy_than_element"),
            "ky_than_element": dung_than.get("ky_than_element"),
        },
        "closing": (
            f"Năm {target_year} là 1 chu kỳ trong tổng thể Đại Vận. "
            f"Khí của năm phản chiếu cơ hội + thử thách. "
            f"Tri mệnh → chọn cách đi qua, không cưỡng theo."
        ),
    }
