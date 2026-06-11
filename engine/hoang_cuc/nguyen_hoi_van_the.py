"""Nguyên-Hội-Vận-Thế — định vị một năm trong chu kỳ 129.600 năm.

locate_year(2026) → vị trí đầy đủ (hội/vận/thế + số thứ tự cục bộ & toàn nguyên,
can chi, khoảng năm của từng tầng) — thuần số học từ mốc trong sách.
"""
from __future__ import annotations

from .constants import (
    ANCHOR_CITATION, HOI_CHI, HOI_MOI_NGUYEN, HOI_NOTES, HOI_QUE,
    HOI_QUE_CITATION, NAM_MOI_HOI, NAM_MOI_NGUYEN, NAM_MOI_THE, NAM_MOI_VAN,
    NGUYEN_START_ASTRO, THE_MOI_VAN, VAN_MOI_HOI, can_chi_year,
)


def _display_year(astro: int) -> str:
    """Astronomical year → nhãn hiển thị (0 = 1 TCN, -1 = 2 TCN...)."""
    return f"{astro} CN" if astro > 0 else f"{1 - astro} TCN"


def locate_year(year: int) -> dict:
    """Định vị năm dương lịch (astronomical) trong nguyên hiện tại.

    Returns dict JSON-serializable; raise ValueError nếu năm ngoài nguyên.
    """
    offset = year - NGUYEN_START_ASTRO  # năm thứ offset+1 của nguyên (0-based)
    if not (0 <= offset < NAM_MOI_NGUYEN):
        raise ValueError(
            f"Năm {year} ngoài nguyên hiện tại "
            f"({_display_year(NGUYEN_START_ASTRO)} → {_display_year(NGUYEN_START_ASTRO + NAM_MOI_NGUYEN - 1)})")

    the_global = offset // NAM_MOI_THE + 1            # 1..4320
    nam_trong_the = offset % NAM_MOI_THE + 1          # 1..30
    van_global = (the_global - 1) // THE_MOI_VAN + 1  # 1..360
    the_trong_van = (the_global - 1) % THE_MOI_VAN + 1
    hoi_idx = (van_global - 1) // VAN_MOI_HOI         # 0..11
    van_trong_hoi = (van_global - 1) % VAN_MOI_HOI + 1
    hoi_chi = HOI_CHI[hoi_idx]

    hoi_start = NGUYEN_START_ASTRO + hoi_idx * NAM_MOI_HOI
    van_start = NGUYEN_START_ASTRO + (van_global - 1) * NAM_MOI_VAN
    the_start = NGUYEN_START_ASTRO + (the_global - 1) * NAM_MOI_THE

    return {
        "year": year,
        "can_chi": can_chi_year(year),
        "nguyen": {
            "so": 1,
            "label": "Giáp nhất (nguyên hiện tại)",
            "start": _display_year(NGUYEN_START_ASTRO),
            "end": _display_year(NGUYEN_START_ASTRO + NAM_MOI_NGUYEN - 1),
            "nam_trong_nguyen": offset + 1,
        },
        "hoi": {
            "so": hoi_idx + 1,
            "chi": hoi_chi,
            "label": f"Hội {hoi_chi} (hội thứ {hoi_idx + 1}/12)",
            "start": _display_year(hoi_start),
            "end": _display_year(hoi_start + NAM_MOI_HOI - 1),
            "note": HOI_NOTES.get(hoi_chi),
            "que": {**HOI_QUE[hoi_chi], "citation": HOI_QUE_CITATION},
        },
        "van": {
            "so_toan_nguyen": van_global,
            "so_trong_hoi": van_trong_hoi,
            "label": f"Vận {van_global} (vận {van_trong_hoi}/30 của hội {hoi_chi})",
            "start": _display_year(van_start),
            "end": _display_year(van_start + NAM_MOI_VAN - 1),
        },
        "the": {
            "so_toan_nguyen": the_global,
            "so_trong_van": the_trong_van,
            "label": f"Thế {the_global} (thế {the_trong_van}/12 của vận {van_global})",
            "start": _display_year(the_start),
            "end": _display_year(the_start + NAM_MOI_THE - 1),
            "nam_trong_the": nam_trong_the,
        },
        "que_van": None,  # quẻ tầng VẬN/THẾ: chờ bảng tập Trung/Hạ (tầng HỘI đã có trong hoi.que)
        "citation": ANCHOR_CITATION,
    }


def timeline(start: int, end: int) -> list[dict]:
    """Dải mốc THẾ trong [start..end] — cho UI vẽ trục thời gian (gọn)."""
    out = []
    y = start
    while y <= end:
        loc = locate_year(y)
        the = loc["the"]
        out.append({
            "the_start": the["start"], "the_end": the["end"],
            "the_so": the["so_toan_nguyen"],
            "van_so": loc["van"]["so_toan_nguyen"],
            "hoi_chi": loc["hoi"]["chi"],
        })
        # nhảy tới đầu thế kế tiếp
        the_start_astro = NGUYEN_START_ASTRO + (the["so_toan_nguyen"] - 1) * NAM_MOI_THE
        y = the_start_astro + NAM_MOI_THE
    return out
