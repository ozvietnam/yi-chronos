"""Nguyên Lưu Trace — dòng chảy ngũ hành trong 4 trụ (TTT chương 19).

Paradigm CỐT (Nhậm Thiết Tiều, TTT chương 19 dòng 2560):
> "Nguyên lưu, tức vượng thần trong Tứ Trụ vậy. Tổn quát cân lưu thông sinh hóa,
>  đắc cục đắc mỹ thì cát. Hoặc khởi tại Tỷ Kiếp, kết thúc tại Tài Quan là hỉ;
>  hoặc khởi tại Tài Quan, kết thúc tại Tỷ Kiếp là kỳ."

Logic:
1. Tìm VƯỢNG THẦN nhất trong Tứ Trụ (theo Nhậm Thiết Tiều, không cần đương lệnh)
2. Trace sinh xuất từ vượng thần → đến đâu (theo chuỗi sinh Ngũ Hành)
3. Đối chiếu Hỉ thần Day Master xem dòng chảy có đến đích cát không

Vd founder Mậu Thìn / Đinh Tỵ / Giáp Tuất / Giáp Tý:
- Vượng nhất: Thổ (Mậu Thìn + Tuất + có Đinh Hỏa sinh Thổ)
- Khởi: Thổ → sinh Kim → Kim sinh Thủy → Thủy sinh Mộc (Day Master Giáp)
- Đích: Mộc = Day Master + Tỷ Kiếp = HỈ THẦN của DM nhược
→ Dòng chảy ĐẾN ĐÚNG hỉ thần = CÁT (Trời bù cho founder)

Pattern khởi-đích (4 ý nghĩa):
- a. Năm-tháng = Thực Ấn + ngày-giờ = Tài Quan → tổ phụ che, con cháu hưởng
- b. Năm-tháng = Quan + ngày-giờ = Thương Kiếp → tổ phụ khó, hình thê khắc tử
- c. Ngày-giờ = Tài Quan + năm-tháng = Thực Ấn → tổ phụ vẻ vang, sự nghiệp tự tạo
- d. Ngày-giờ = Tài Quan + năm-tháng = Thương Kiếp → tự khởi nghiệp
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── Element flow (Ngũ Hành Sinh) ────────────────────────────────────────────

ELEMENT_SHENG: dict[str, str] = {
    "mộc": "hỏa",   # Mộc sinh Hỏa
    "hỏa": "thổ",   # Hỏa sinh Thổ
    "thổ": "kim",   # Thổ sinh Kim
    "kim": "thủy",  # Kim sinh Thủy
    "thủy": "mộc",  # Thủy sinh Mộc
}

ELEMENT_KE: dict[str, str] = {
    "mộc": "thổ",   # Mộc khắc Thổ
    "thổ": "thủy",
    "thủy": "hỏa",
    "hỏa": "kim",
    "kim": "mộc",
}


@dataclass
class NguyenLuuResult:
    """Kết quả Nguyên Lưu trace."""

    nguyen_element: str             # Vượng thần khởi nguồn (vd "thổ")
    nguyen_position: list[str]      # Trụ nào chứa nguồn (vd ["year", "day", "hour"])
    luu_chain: list[str]            # Chuỗi chảy: ["thổ", "kim", "thủy", "mộc"]
    diem_dich: str                  # Element kết thúc dòng chảy
    diem_dich_la_dm: bool           # Có phải Day Master không?
    diem_dich_la_hi_than: bool      # Có phải Hỉ Thần không?
    chan_tro_position: str          # Trụ nào cản trở dòng (nếu có)
    chan_tro_element: str           # Element cản trở (khắc thần kế tiếp)
    pattern: str                    # "khởi_tỷ_kiếp_kết_tài_quan" / "khởi_tài_quan_kết_tỷ_kiếp" / ...
    y_nghia: str                    # Diễn giải (a/b/c/d theo TTT)
    cat_hung_score: float           # 0-10
    narrative: str
    trich_dan: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _count_elements_in_pillars(pillars: dict) -> dict[str, list[str]]:
    """Đếm mỗi element xuất hiện ở trụ nào (stem + branch)."""
    from .constants import BRANCH_ELEMENT
    from .phu_uc_route import STEM_ELEMENT

    el_positions: dict[str, list[str]] = {"mộc": [], "hỏa": [], "thổ": [], "kim": [], "thủy": []}
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        stem = p.get("stem")
        if stem:
            el = STEM_ELEMENT.get(stem)
            if el and el in el_positions:
                el_positions[el].append(f"{pos}_stem")
        branch = p.get("branch")
        if branch:
            el = BRANCH_ELEMENT.get(branch, "").lower()
            if el in el_positions:
                el_positions[el].append(f"{pos}_branch")
    return el_positions


def _find_nguyen(el_counts: dict[str, list[str]]) -> tuple[str, list[str]]:
    """Tìm element VƯỢNG NHẤT — đó là Nguyên (gốc dòng chảy)."""
    sorted_els = sorted(el_counts.items(), key=lambda x: len(x[1]), reverse=True)
    if sorted_els and sorted_els[0][1]:
        return sorted_els[0][0], sorted_els[0][1]
    return "", []


def _trace_chain(nguyen: str, el_counts: dict[str, list[str]],
                 max_depth: int = 5) -> tuple[list[str], str, str]:
    """Trace chuỗi sinh xuất từ nguyên đến hết.

    Returns: (chain, blocked_element, blocked_position)
    """
    chain = [nguyen]
    visited = {nguyen}
    current = nguyen
    blocked_el = ""
    blocked_pos = ""

    for _ in range(max_depth):
        nxt = ELEMENT_SHENG.get(current)
        if not nxt or nxt in visited:
            break
        # Có element kế tiếp trong tứ trụ không?
        if el_counts.get(nxt):
            chain.append(nxt)
            visited.add(nxt)
            current = nxt
        else:
            # Bị tắt mạch — chuỗi dừng tại current
            blocked_el = nxt
            blocked_pos = "không có trong Tứ Trụ"
            break

    return chain, blocked_el, blocked_pos


def trace_nguyen_luu(tu_tru: dict, hi_than_elements: list[str] | None = None) -> NguyenLuuResult:
    """Engine chính Nguyên Lưu.

    Args:
        tu_tru: pillars
        hi_than_elements: list element là Hỉ Thần của Day Master.
                          Nếu không cung cấp, infer từ Phù-Ức/Tòng.

    Returns: NguyenLuuResult
    """
    from .phu_uc_route import STEM_ELEMENT, route_phu_uc
    from .tong_cach_route import route_tong_cach

    pillars = tu_tru["pillars"]
    day_master_stem = pillars["day"]["stem"]
    day_master_element = STEM_ELEMENT.get(day_master_stem, "")

    # 1. Đếm elements
    el_counts = _count_elements_in_pillars(pillars)

    # 2. Tìm nguyên (vượng nhất)
    nguyen, nguyen_pos = _find_nguyen(el_counts)

    # 3. Trace chuỗi
    chain, blocked_el, blocked_pos = _trace_chain(nguyen, el_counts)
    diem_dich = chain[-1] if chain else ""

    # 4. Infer Hỉ Thần nếu chưa có
    if hi_than_elements is None:
        tong = route_tong_cach(tu_tru)
        if tong.is_tong:
            hi_than_elements = tong.dung_than_elements
        else:
            phu_uc = route_phu_uc(tu_tru)
            hi_than_elements = phu_uc.dung_than_elements

    # 5. Đối chiếu
    diem_dich_la_dm = (diem_dich == day_master_element)
    diem_dich_la_hi_than = (diem_dich in (hi_than_elements or []))

    # 6. Pattern (gốc-đích)
    pattern = _classify_pattern(chain, day_master_element)
    y_nghia = _interpret_pattern(pattern, diem_dich_la_hi_than)

    # 7. Score
    if diem_dich_la_hi_than:
        score = 8.5
    elif diem_dich_la_dm:
        score = 7.0
    elif blocked_el:
        score = 4.0
    else:
        score = 5.0

    # 8. Narrative
    chain_str = " → ".join([e.title() for e in chain])
    parts = [
        f"**Nguyên (vượng nhất):** {nguyen.title()} (ở {len(nguyen_pos)} vị trí: {', '.join(nguyen_pos)})",
        f"**Dòng chảy:** {chain_str}",
        f"**Điểm đích:** {diem_dich.title()}"
        + (" = Day Master" if diem_dich_la_dm else "")
        + (" = HỈ THẦN ✅" if diem_dich_la_hi_than else " = KHÔNG phải hỉ thần ⚠️"),
    ]
    if blocked_el:
        parts.append(f"**Bị cản trở:** Mạch đáng lẽ sang {blocked_el.title()} nhưng {blocked_pos}")
    parts.append(f"**Score cát-hung:** {score}/10")
    narrative = "\n\n".join(parts)

    return NguyenLuuResult(
        nguyen_element=nguyen,
        nguyen_position=nguyen_pos,
        luu_chain=chain,
        diem_dich=diem_dich,
        diem_dich_la_dm=diem_dich_la_dm,
        diem_dich_la_hi_than=diem_dich_la_hi_than,
        chan_tro_position=blocked_pos,
        chan_tro_element=blocked_el,
        pattern=pattern,
        y_nghia=y_nghia,
        cat_hung_score=round(score, 1),
        narrative=narrative,
        trich_dan=[
            {
                "sach": "Trích Thiên Tủy chương 19 (Nguyên Lưu)",
                "dong": 2560,
                "noi_dung": (
                    "Nguyên lưu, tức vượng thần trong Tứ Trụ vậy. Tổn quát cân lưu thông "
                    "sinh hóa, đắc cục đắc mỹ thì cát. Hoặc khởi tại Tỷ Kiếp, kết thúc "
                    "tại Tài Quan là hỉ; hoặc khởi tại Tài Quan, kết thúc tại Tỷ Kiếp là kỳ."
                ),
            },
        ],
    )


def _classify_pattern(chain: list[str], dm_element: str) -> str:
    """Phân loại pattern khởi-đích."""
    if not chain or not dm_element:
        return "unknown"
    nguyen = chain[0]
    dich = chain[-1]

    # Khởi tại Tỷ Kiếp (cùng hành DM) → ?
    if nguyen == dm_element:
        # Đích là gì so với DM?
        if dich == ELEMENT_KE.get(dm_element):  # Tài
            return "khởi_tỷ_kiếp_kết_tài"
        elif ELEMENT_KE.get(dich) == dm_element:  # Quan Sát
            return "khởi_tỷ_kiếp_kết_quan_sát"
        else:
            return "khởi_tỷ_kiếp_kết_khác"
    # Khởi tại Tài (DM khắc) → ?
    elif nguyen == ELEMENT_KE.get(dm_element):
        if dich == dm_element:
            return "khởi_tài_kết_tỷ_kiếp"
    # Khởi tại Ấn (sinh DM) → ?
    elif ELEMENT_SHENG.get(nguyen) == dm_element:
        if dich == dm_element:
            return "khởi_ấn_kết_dm"
    return f"khởi_{nguyen}_kết_{dich}"


def _interpret_pattern(pattern: str, hi_than_match: bool) -> str:
    """Diễn giải pattern theo TTT chương 19."""
    if hi_than_match:
        if "khởi_ấn" in pattern:
            return (
                "Dòng chảy khởi từ Ấn (sinh khí) đến Day Master = **tổ phụ che chở, "
                "con cháu được hưởng phúc đức**. Mạch sinh thuận, khí dưỡng thân."
            )
        elif "khởi_tỷ_kiếp_kết_tài" in pattern:
            return (
                "Khởi Tỷ Kiếp kết Tài = **hỉ pattern TTT** (anh em cùng tạo nên tài lực). "
                "Sự nghiệp tự lập, phát từ đồng đạo."
            )
        elif "khởi_tài_kết_tỷ_kiếp" in pattern:
            return (
                "Khởi Tài kết Tỷ Kiếp = **kỳ pattern TTT** (tài lực quy tụ về đồng đạo). "
                "Quý nhân giúp đỡ, tự tạo dựng được sản nghiệp."
            )
        else:
            return "Dòng chảy lưu thông đến Hỉ Thần — paradigm 'đắc cục đắc mỹ' của TTT."
    else:
        if "khởi_tỷ_kiếp_kết_khác" in pattern:
            return (
                "Dòng chảy không đến đích hỉ thần — khí lưu nhưng chệch hướng. "
                "Cần thêm thần thuốc trung gian để dẫn dòng."
            )
        return "Dòng chảy chưa thuận theo Hỉ Thần — vận có thể bù để dẫn dòng cát."


def render_nguyen_luu_markdown(result: NguyenLuuResult) -> str:
    """Render markdown."""
    lines = [
        f"## 🌊 Nguyên Lưu Trace (TTT chương 19)\n",
        result.narrative,
        f"\n### 🎯 Ý nghĩa\n",
        result.y_nghia,
        f"\n### 📖 Trích Trích Thiên Tủy",
    ]
    for td in result.trich_dan:
        dong_str = f" (dòng {td['dong']})" if td.get("dong") else ""
        lines.append(f"\n> _{td['noi_dung']}_  ")
        lines.append(f"> — **{td['sach']}**{dong_str}")
    lines.append("\n🪷 _Iron Rule #4+6: Nguyên Lưu phản chiếu dòng chảy khí — KHÔNG predict 'tiền vận - hậu vận'._")
    return "\n".join(lines)
