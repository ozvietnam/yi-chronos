"""Chấn Đoài + Khảm Ly — Trích Thiên Tủy Chương 33-34.

Paradigm Nhậm Thiết Tiều:

CHẤN ĐOÀI (Mộc-Kim đối lập, Day Master Mộc):
> "Cơ lý Chấn Đoài có năm: Công - Thành - Nhuận - Tòng - Noãn."

5 trường hợp Mộc-Kim theo mùa:
1. **Sơ xuân** (đầu tháng Dần) — Mộc non, Kim cứng → Hỏa **CÔNG** (đánh Kim)
2. **Trọng xuân** (tháng Mão) — Mộc vượng, Kim suy → Thổ **THÀNH** (sinh Kim)
3. **Hạ lệnh** (Tỵ Ngọ Mùi) — Mộc thiệt, Kim táo → Thủy **NHUẬN** (làm ướt cả 2)
4. **Thu lệnh** (Thân Dậu Tuất) — Mộc tàn, Kim sắc → Thổ **TÒNG** (theo Kim)
5. **Đông lệnh** (Hợi Tý Sửu) — Mộc suy, Kim hàn → Hỏa **NOÃN** (làm ấm cả 2)

KHẢM LY (Thủy-Hỏa giao tế, Day Master Thủy hoặc Hỏa):
> "Lý giăng co gồm có năm: thăng, hàng, hòa, giải, chế."

Paradigm:
- **Ký tế** (Thủy trên Hỏa dưới) — đẹp
- **Vị tế** (Hỏa trên Thủy dưới) — chưa thành
- **Giao châu** (Thiên Can Thủy / Địa Chi Hỏa) — thân cường thì quý
- **Giao chiến** (Thiên Can Hỏa / Địa Chi Thủy) — thân nhược thì hung

⚠️ Iron Rule #4+6: Output = paradigm theo mùa-cấu hình, không predict tĩnh.
"""

from __future__ import annotations


# Phân loại tháng → mùa
MONTH_SEASON: dict[str, str] = {
    "Dần": "so_xuan", "Mão": "trong_xuan", "Thìn": "cuoi_xuan",
    "Tỵ": "ha", "Ngọ": "ha", "Mùi": "ha",
    "Thân": "thu", "Dậu": "thu", "Tuất": "thu",
    "Hợi": "dong", "Tý": "dong", "Sửu": "dong",
}


# 5 lý lẽ Chấn Đoài (Day Master Mộc)
CHAN_DOAI_PARADIGMS: dict[str, dict] = {
    "so_xuan": {
        "name": "Công (攻) — Sơ xuân",
        "essence": "Mộc non yếu, Kim cứng đè",
        "yong_than": "hỏa",
        "yong_role": "công đánh Kim cứu Mộc",
        "paradigm": "Sơ xuân Mộc còn non, dễ bị Kim chặt. Phải dùng Hỏa Công khắc Kim.",
    },
    "trong_xuan": {
        "name": "Thành (成) — Trọng xuân",
        "essence": "Mộc vượng, Kim suy không khắc nổi",
        "yong_than": "thổ",
        "yong_role": "thành — sinh Kim trợ vực",
        "paradigm": "Trọng xuân Mộc đương lệnh, Kim suy. Phải dùng Thổ Thành sinh Kim làm cho có lực chế Mộc.",
    },
    "ha": {
        "name": "Nhuận (潤) — Hạ lệnh",
        "essence": "Mộc khô vì Hỏa cháy, Kim cũng táo",
        "yong_than": "thủy",
        "yong_role": "nhuận — làm ướt cả 2",
        "paradigm": "Hạ lệnh Hỏa cháy, Mộc khô + Kim táo. Phải dùng Thủy Nhuận làm ướt cả 2.",
    },
    "thu": {
        "name": "Tòng (從) — Thu lệnh",
        "essence": "Mộc tàn héo, Kim sắc bén áp đảo",
        "yong_than": "thổ",
        "yong_role": "tòng — theo Kim (đầu hàng)",
        "paradigm": "Thu lệnh Kim vượng cực, Mộc tàn héo không chống nổi. Phải dùng Thổ Tòng theo về Kim — paradigm 'cường giảm nhược tòng'.",
    },
    "dong": {
        "name": "Noãn (暖) — Đông lệnh",
        "essence": "Mộc suy lạnh, Kim hàn không sắc",
        "yong_than": "hỏa",
        "yong_role": "noãn — làm ấm cả 2",
        "paradigm": "Đông lệnh Thủy đông, Mộc suy + Kim hàn không có lực. Phải dùng Hỏa Noãn làm ấm cả 2.",
    },
}


def analyze_chan_doai(day_element: str, month_branch: str, has_kim: bool) -> dict | None:
    """Phân tích Chấn Đoài — Day Master Mộc + có Kim trong lá số.

    Args:
        day_element: ngũ hành Day Master (phải = "mộc")
        month_branch: chi tháng
        has_kim: có Kim trong Tứ Trụ không

    Returns: dict result or None.
    """
    if day_element.lower() != "mộc":
        return None
    if not has_kim:
        return None

    season = MONTH_SEASON.get(month_branch)
    if not season:
        return None

    # Sơ xuân là 7 ngày đầu Dần — em đơn giản dùng Dần làm sơ xuân
    if season == "cuoi_xuan":
        # Tháng Thìn — gần với hạ
        season = "ha"

    paradigm = CHAN_DOAI_PARADIGMS.get(season)
    if not paradigm:
        return None

    return {
        "applies": True,
        "season": season,
        "month_branch": month_branch,
        "pattern_name": paradigm["name"],
        "essence": paradigm["essence"],
        "yong_than": paradigm["yong_than"],
        "yong_role": paradigm["yong_role"],
        "narrative": (
            f"**Chấn Đoài — Mộc-Kim đối lập (Trích Thiên Tủy Ch.33)**\n\n"
            f"Day Master Mộc + có Kim, sinh tháng **{month_branch}** ({season.replace('_',' ')}).\n\n"
            f"→ Pattern: **{paradigm['name']}**\n\n"
            f"Bản chất: {paradigm['essence']}.\n\n"
            f"**Dụng Thần đề xuất**: **{paradigm['yong_than'].title()}** "
            f"({paradigm['yong_role']}).\n\n"
            f"Quote Nhậm Thị: _{paradigm['paradigm']}_"
        ),
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 33 Chấn Đoài",
    }


# Khảm Ly patterns (Day Master Thủy hoặc Hỏa)
KHAM_LY_PATTERNS: dict[str, dict] = {
    "ky_te": {
        "name": "Ký tế (既濟) — Thủy trên Hỏa dưới",
        "essence": "Thủy chế Hỏa, cân bằng — hoàn thành",
        "verdict": "tốt",
        "narrative": "Thiên Can Thủy + Địa Chi Hỏa → Thủy giáng, Hỏa thăng giao nhau = Ký tế. Cấu hình hoàn thành.",
    },
    "vi_te": {
        "name": "Vị tế (未濟) — Hỏa trên Thủy dưới",
        "essence": "Hỏa trên, Thủy dưới — chưa giao tế",
        "verdict": "chưa thành",
        "narrative": "Thiên Can Hỏa + Địa Chi Thủy → 2 khí không giao nhau = Vị tế. Cần thêm yếu tố đẩy giao.",
    },
    "giao_chau": {
        "name": "Giao châu (交州) — Thân cường",
        "essence": "Toàn Thiên Can Thủy, toàn Địa Chi Hỏa",
        "verdict": "phú quý nếu thân cường",
        "narrative": "Giao châu — 2 khí đối lập cực điểm. Chỉ thân cường mới phú quý; thân nhược thì hung.",
    },
    "giao_chien": {
        "name": "Giao chiến (交戰) — Thân nhược",
        "essence": "Toàn Thiên Can Hỏa, toàn Địa Chi Thủy",
        "verdict": "hung nếu thân nhược",
        "narrative": "Giao chiến — 2 khí xung đột. Thân nhược không thể chịu nổi → hung.",
    },
}


def analyze_kham_ly(day_element: str, pillars: dict) -> dict | None:
    """Phân tích Khảm Ly — Day Master Thủy hoặc Hỏa, có cả 2 hành.

    Args:
        day_element: ngũ hành Day Master
        pillars: 4 trụ

    Returns: dict result or None.
    """
    if day_element.lower() not in ("thủy", "hỏa"):
        return None

    # Đếm Thủy/Hỏa trong stems vs branches
    from .constants import STEM_ELEMENT, BRANCH_ELEMENT
    stems_thuy = 0
    stems_hoa = 0
    branches_thuy = 0
    branches_hoa = 0
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        st = p.get("stem")
        br = p.get("branch")
        if st:
            el = STEM_ELEMENT.get(st, "").lower()
            if el == "thủy": stems_thuy += 1
            elif el == "hỏa": stems_hoa += 1
        if br:
            el = BRANCH_ELEMENT.get(br, "").lower()
            if el == "thủy": branches_thuy += 1
            elif el == "hỏa": branches_hoa += 1

    # Detect pattern
    pattern_key = None
    if stems_thuy >= 2 and branches_hoa >= 2:
        pattern_key = "giao_chau"
    elif stems_hoa >= 2 and branches_thuy >= 2:
        pattern_key = "giao_chien"
    elif stems_thuy >= 1 and branches_hoa >= 1 and stems_thuy >= stems_hoa:
        pattern_key = "ky_te"
    elif stems_hoa >= 1 and branches_thuy >= 1 and stems_hoa >= stems_thuy:
        pattern_key = "vi_te"

    if not pattern_key:
        return None

    p = KHAM_LY_PATTERNS[pattern_key]
    return {
        "applies": True,
        "pattern_key": pattern_key,
        "pattern_name": p["name"],
        "essence": p["essence"],
        "verdict": p["verdict"],
        "counts": {
            "stems_thuy": stems_thuy, "stems_hoa": stems_hoa,
            "branches_thuy": branches_thuy, "branches_hoa": branches_hoa,
        },
        "narrative": (
            f"**Khảm Ly — Thủy-Hỏa giao tế (Trích Thiên Tủy Ch.34)**\n\n"
            f"Day Master {day_element.title()}, pattern **{p['name']}**.\n\n"
            f"{p['narrative']}\n\n"
            f"Verdict: {p['verdict']}."
        ),
        "source": "Trích Thiên Tủy bình chú — Nhậm Thiết Tiều, Chương 34 Khảm Ly",
    }
