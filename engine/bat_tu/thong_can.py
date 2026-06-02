"""Thông Căn (通根) — Thiên Can có gốc trong Địa Chi.

Paradigm Trích Thiên Tủy bình chú (Nhậm Thiết Tiều), Chương 3 Nhân Đạo:
> "Thiên can suy nhược mà còn bị địa chi ức chế, địa chi khí nhược
>  mà còn bị thiên can khắc, tức là không hưởng hung nguy vậy."
>
> "Thiên can Mộc rất sợ hành Kim khắc... Nếu địa chi có Dần Mão Mộc,
>  tức thiên can THÔNG GỐC (THÔNG CĂN)."

Khái niệm:
- **Lộc** (祿) = chính căn, đất Lâm Quan của Can — gốc MẠNH nhất
- **Trường Sinh** (長生) = đất sinh đầu — gốc TRUNG
- **Kho Mộ** (墓庫) = đất chứa khí cũ — gốc YẾU (đang lưu kho)

⚠️ Iron Rule #4+6: Output là CƠ CẤU KHÍ, không phải "tốt/xấu" tĩnh.
Engine ĐÃ ghi nhận trong dung_than.py::v2_note rằng cần build module này ở v3.
Đây chính là v3.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


# Mapping Thiên Can → (Lộc, Trường Sinh, Kho Mộ) cho 10 can
# Reference: Trích Thiên Tủy + 子平真詮 canonical tables
THONG_CAN_TABLE: dict[str, dict] = {
    "Giáp": {"loc": "Dần", "truong_sinh": "Hợi", "kho_mo": "Mùi", "element": "mộc"},
    "Ất":   {"loc": "Mão", "truong_sinh": "Ngọ", "kho_mo": "Mùi", "element": "mộc"},
    "Bính": {"loc": "Tỵ",  "truong_sinh": "Dần", "kho_mo": "Tuất", "element": "hỏa"},
    "Đinh": {"loc": "Ngọ", "truong_sinh": "Dậu", "kho_mo": "Tuất", "element": "hỏa"},
    "Mậu":  {"loc": "Tỵ",  "truong_sinh": "Dần", "kho_mo": "Tuất", "element": "thổ"},
    "Kỷ":   {"loc": "Ngọ", "truong_sinh": "Dậu", "kho_mo": "Tuất", "element": "thổ"},
    "Canh": {"loc": "Thân", "truong_sinh": "Tỵ", "kho_mo": "Sửu", "element": "kim"},
    "Tân":  {"loc": "Dậu", "truong_sinh": "Tý",  "kho_mo": "Sửu", "element": "kim"},
    "Nhâm": {"loc": "Hợi", "truong_sinh": "Thân", "kho_mo": "Thìn", "element": "thủy"},
    "Quý":  {"loc": "Tý",  "truong_sinh": "Mão", "kho_mo": "Thìn", "element": "thủy"},
}


@dataclass(frozen=True)
class ThongCanResult:
    """Kết quả phân tích thông căn cho 1 Thiên Can."""

    stem: str
    stem_position: str  # year / month / day / hour
    element: str
    has_loc: list[str]            # branches where Lộc found (positions)
    has_truong_sinh: list[str]    # branches where Trường Sinh found
    has_kho_mo: list[str]         # branches where Kho Mộ found
    # Bonus: cùng-loại chi (same element as stem) — engine count tính qua đây
    same_element_branches: list[str]
    strength_tag: str             # "loc_vuong" / "thong_can" / "hu_phu"
    score: float                  # 0.0 (hư phù) → 10.0 (lộc vượng)
    narrative: str

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_thong_can(stem: str, position: str, all_branches: dict[str, str]) -> ThongCanResult:
    """Phân tích thông căn cho 1 Thiên Can.

    Args:
        stem: Vietnamese stem (e.g. "Giáp")
        position: pillar position (year/month/day/hour) — where this stem sits
        all_branches: {pos: branch} for all 4 pillars

    Returns: ThongCanResult
    """
    table = THONG_CAN_TABLE.get(stem)
    if not table:
        return ThongCanResult(
            stem=stem, stem_position=position, element="?",
            has_loc=[], has_truong_sinh=[], has_kho_mo=[],
            same_element_branches=[], strength_tag="unknown",
            score=0.0, narrative="Can chưa khớp bảng tra",
        )

    loc, ts, kho = table["loc"], table["truong_sinh"], table["kho_mo"]
    el = table["element"]
    from .constants import BRANCH_ELEMENT

    has_loc = []
    has_ts = []
    has_kho = []
    same_el = []
    for pos, branch in all_branches.items():
        if branch == loc:
            has_loc.append(pos)
        if branch == ts:
            has_ts.append(pos)
        if branch == kho:
            has_kho.append(pos)
        # Cùng-loại chi: chi có ngũ hành = ngũ hành của can (không tính trùng)
        if (BRANCH_ELEMENT.get(branch, "").lower() == el and
                branch != loc and branch != ts and branch != kho):
            same_el.append(pos)

    # Score: Lộc = 4, Trường Sinh = 2.5, Kho Mộ = 1.5, Same element = 1.5
    score = (
        len(has_loc) * 4.0
        + len(has_ts) * 2.5
        + len(has_kho) * 1.5
        + len(same_el) * 1.5
    )

    # Classify
    if score >= 4.0:
        tag = "loc_vuong"
        label = "LỘC VƯỢNG"
        desc = "có Lộc làm chính căn, khí cương vượng đầy đủ"
    elif score >= 2.0:
        tag = "thong_can"
        label = "THÔNG CĂN"
        desc = "có gốc trong Địa Chi, khí thực không hư"
    elif score > 0:
        tag = "thong_can_yeu"
        label = "THÔNG CĂN YẾU"
        desc = "có gốc nhưng yếu, dễ bị tổn"
    else:
        tag = "hu_phu"
        label = "HƯ PHÙ"
        desc = "không có gốc — khí giả tạo, gặp khắc dễ tan"

    parts = []
    if has_loc:
        parts.append(f"Lộc ở Trụ {' + '.join(has_loc)} ({loc})")
    if has_ts:
        parts.append(f"Trường Sinh ở Trụ {' + '.join(has_ts)} ({ts})")
    if has_kho:
        parts.append(f"Kho Mộ ở Trụ {' + '.join(has_kho)} ({kho})")
    if same_el:
        parts.append(f"chi cùng hành ở Trụ {' + '.join(same_el)}")
    detail = "; ".join(parts) if parts else "không có chi nào sinh phù"

    narrative = (
        f"**{stem} ({el.title()}) ở Trụ {position}: {label}** — {desc}. "
        f"Chi tiết: {detail}. Score={score:.1f}/10."
    )

    return ThongCanResult(
        stem=stem, stem_position=position, element=el,
        has_loc=has_loc, has_truong_sinh=has_ts, has_kho_mo=has_kho,
        same_element_branches=same_el,
        strength_tag=tag, score=round(score, 1),
        narrative=narrative,
    )


def analyze_all_thong_can(pillars: dict) -> list[dict]:
    """Phân tích thông căn cho cả 4 Thiên Can trong Tứ Trụ.

    Returns: list of 4 ThongCanResult dicts, ordered year/month/day/hour.
    """
    all_branches = {}
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        b = p.get("branch")
        if b:
            all_branches[pos] = b

    out = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        stem = p.get("stem")
        if not stem:
            continue
        r = analyze_thong_can(stem, pos, all_branches)
        out.append(r.to_dict())
    return out


def summarize_day_master_thong_can(pillars: dict) -> dict:
    """Tóm tắt Nhật Chủ thông căn — CỐT cho cường/nhược refinement.

    Theo Trích Thiên Tủy: Nhật Chủ thông căn = bồi thân thật.
    Hư phù = thân "có vẻ" mạnh trên giấy nhưng thực ra rỗng.
    """
    pillars_dict = {pos: p.get("branch") for pos, p in pillars.items() if p.get("branch")}
    day_stem = pillars.get("day", {}).get("stem")
    if not day_stem:
        return {"error": "no day stem"}
    r = analyze_thong_can(day_stem, "day", pillars_dict)
    return {
        "day_stem": day_stem,
        "element": r.element,
        "strength_tag": r.strength_tag,
        "score": r.score,
        "narrative": r.narrative,
        "paradigm_note": (
            "Theo Trích Thiên Tủy bình chú: Nhật Chủ thông căn = bồi thân THẬT. "
            "Hư phù = thân 'có vẻ' mạnh trên giấy (đếm tỉ kiếp lộ) nhưng thực ra rỗng "
            "— gặp khắc dễ vỡ. Cần đối chiếu với cường/nhược thông qua count_elements."
        ),
    }
