"""Tử Vi — Miếu Vượng Hãm (sức mạnh sao tại cung).

Theo Q2 p0102 "Thập nhị cung Miếu Vượng Lạc Hãm đồ" + Q2 p0103-p0125 diễn giải.

Mỗi sao tại mỗi cung có 1 trong 6 mức:
  - Miếu (4 điểm): mạnh nhất
  - Vượng (3 điểm): mạnh
  - Đắc (2 điểm): khá
  - Bình (1 điểm): trung tính
  - Lạc (-1 điểm): yếu
  - Hãm (-2 điểm): yếu nhất

Reference: `data/tu_vi/mieu_vuong_ham.json` schema_version=tu_vi_mieu_vuong_ham_v1
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/tu_vi/mieu_vuong_ham.json"


@lru_cache(maxsize=1)
def _load_table() -> dict:
    return json.loads(DATA_PATH.read_text())


def level_at(star: str, branch: str) -> str | None:
    """Get level (miếu/vượng/đắc/bình/lạc/hãm) for star at branch."""
    table = _load_table().get("table", {})
    return table.get(star, {}).get(branch)


def level_score(level: str) -> int:
    """Score for a level."""
    levels = _load_table().get("levels", {})
    return levels.get(level, {}).get("score", 0)


def level_label(level: str) -> str:
    """Human-readable label."""
    levels = _load_table().get("levels", {})
    return levels.get(level, {}).get("label", level)


def level_color(level: str) -> str:
    """Color hex for UI."""
    levels = _load_table().get("levels", {})
    return levels.get(level, {}).get("color", "#94a3b8")


def chart_strength(la_so: dict) -> dict:
    """Compute toàn bộ sức mạnh của 14 chính tinh trong lá số.

    Returns:
        {
          "stars": [{star, branch, level, score, label}],
          "total_score": int,
          "verdict": str,
          "strongest": [...],  # top 3 strongest
          "weakest": [...]     # top 3 weakest
        }
    """
    BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    chinh = la_so.get("chinh_tinh", {})
    stars_data = []
    total = 0
    for star, branch_idx in chinh.items():
        branch = BRANCHES[branch_idx]
        level = level_at(star, branch)
        if level is None:
            continue
        score = level_score(level)
        total += score
        stars_data.append({
            "star": star,
            "branch": branch,
            "level": level,
            "score": score,
            "label": level_label(level),
            "color": level_color(level),
        })

    # Sort by score
    sorted_stars = sorted(stars_data, key=lambda s: -s["score"])
    strongest = sorted_stars[:3]
    weakest = sorted_stars[-3:]

    # Verdict based on total
    if total >= 30:
        verdict = "rất vượng — 14 chính tinh hầu hết đắc địa, lá số có khí thế mạnh"
    elif total >= 15:
        verdict = "vượng — đa số chính tinh đắc địa, lá số khá tốt"
    elif total >= 0:
        verdict = "bình — cát hung lẫn, không đặc biệt thiên về bên nào"
    elif total >= -15:
        verdict = "yếu — nhiều chính tinh hãm, cần cẩn trọng"
    else:
        verdict = "rất yếu — đa số chính tinh hãm, lá số gặp nhiều thử thách"

    return {
        "stars": stars_data,
        "total_score": total,
        "verdict": verdict,
        "strongest": strongest,
        "weakest": weakest,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    from engine.tu_vi.an_sao import cast_la_so
    from core.chronos import calculate_chronos_state

    chronos = calculate_chronos_state("1988-06-05T23:30:00", "Asia/Ho_Chi_Minh")
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    la_so = cast_la_so(
        lunar_month=int(m_str), lunar_day=int(d_str), hour_branch="Tý",
        year_stem=year_parts[0], year_branch=year_parts[1], gender="nam",
    )
    result = chart_strength(la_so)
    print(f"=== Founder chart strength ===")
    print(f"Total: {result['total_score']} → {result['verdict']}\n")
    for s in result['stars']:
        print(f"  {s['star']:12s} tại {s['branch']:5s} = {s['level']:8s} ({s['score']:+d})")
    print(f"\nStrongest: {[(s['star'], s['level']) for s in result['strongest']]}")
    print(f"Weakest:   {[(s['star'], s['level']) for s in result['weakest']]}")
