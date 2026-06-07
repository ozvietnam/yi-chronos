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
# Volume mount /opt/yi-chronos/data shadows data/ in Docker — embedded first
_CANDIDATES = [
    ROOT / "embedded_data/tu_vi/mieu_vuong_ham.json",
    ROOT / "data/tu_vi/mieu_vuong_ham.json",
]
DATA_PATH = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[-1])


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

    Q4 enhancement (2026-05-20): Apply palace weights theo Q4 p0276 r003-r005.
    Sao tốt ở cung cao cường (Mệnh/Phúc/Quan/Điền/Thê) nặng phúc hơn sao tốt ở
    cung ác nhược (Tướng Mạo/Nô Bộc).

    Returns:
        {
          "stars": [{star, branch, level, score, label, palace, palace_tier, weighted_score}],
          "total_score": int (raw sum without weight),
          "weighted_total_score": float (Q4 palace-weighted),
          "verdict": str,
          "strongest": [...],
          "weakest": [...]
        }
    """
    import json as _json
    BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

    # Load palace weights from Q4 p0276
    palace_weights_path = ROOT / "data/tu_vi/palace_weights.json"
    palace_tier_map = {}  # palace_name → (tier_name, weight)
    if palace_weights_path.exists():
        pw = _json.loads(palace_weights_path.read_text())
        for tier_name, tier_data in pw.get("tiers", {}).items():
            weight = tier_data.get("weight", 1.0)
            for pal in tier_data.get("palaces", []):
                palace_tier_map[pal] = (tier_name, weight)

    # Build branch_index → palace_name lookup
    branch_to_palace = {}
    for p in la_so.get("palaces", []):
        branch_to_palace[p["branch_index"]] = p["name"]

    chinh = la_so.get("chinh_tinh", {})
    stars_data = []
    total = 0
    weighted_total = 0.0
    for star, branch_idx in chinh.items():
        branch = BRANCHES[branch_idx]
        level = level_at(star, branch)
        if level is None:
            continue
        score = level_score(level)
        total += score

        # Apply palace weight (Q4)
        palace_name = branch_to_palace.get(branch_idx, "?")
        tier_name, weight = palace_tier_map.get(palace_name, ("cận_cường", 1.0))
        # Special rule: Tật Ách/Thiên Di + sao Miếu → đảo ngược ác sát thành quý (×1.3)
        if palace_name in ("Tật Ách", "Thiên Di") and level == "miếu":
            weight *= 1.3
        weighted_score = round(score * weight, 2)
        weighted_total += weighted_score

        stars_data.append({
            "star": star,
            "branch": branch,
            "level": level,
            "score": score,
            "label": level_label(level),
            "color": level_color(level),
            "palace": palace_name,
            "palace_tier": tier_name,
            "palace_weight": weight,
            "weighted_score": weighted_score,
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
        "weighted_total_score": round(weighted_total, 2),
        "verdict": verdict,
        "strongest": strongest,
        "weakest": weakest,
        "palace_weights_source": "Q4 p0276 (Phase A Batch 4)",
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
