"""Tử Vi — Cung Reading Builder.

Cho 1 lá số (chart_summary), surface các passages từ:
- Q1 Phú Thái Vi (phu_matches cached) — luận giải các cách cục
- Q3 Diễn Giải 12 Cung × 14 Chính Tinh (raw text lines p0142-p0198)
- 14 chính tinh schema (data/tu_vi/chinh_tinh.json) — keywords + tích cực + tiêu cực

→ Group thành dict {palace_name → {branch, stars, chinh_tinh, star_schemas, passages}}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
Q3_TRANSL_ROOT = ROOT / "data/yi_publishing/translations/tuvidauso-zh"
CHINH_TINH_SCHEMA = ROOT / "data/tu_vi/chinh_tinh.json"

CHINH_TINH_NAMES = [
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn", "Thiên Tướng", "Thiên Lương",
    "Thất Sát", "Phá Quân",
]

ALL_PALACES = [
    "Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc",
    "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ",
]

# Q3 pages range
Q3_PAGE_START = 142
Q3_PAGE_END = 198


def _load_chinh_tinh_schema() -> dict[str, dict]:
    if not CHINH_TINH_SCHEMA.exists():
        return {}
    raw = json.loads(CHINH_TINH_SCHEMA.read_text())
    stars = raw.get("stars", raw) if isinstance(raw, dict) else raw
    return {s["ten_vi"]: s for s in stars}


def _load_q3_lines() -> list[tuple[int, str, str, str]]:
    """Load all Q3 lines → list of (page, line_id, text_vi, text_vi_luangiai)."""
    out: list[tuple[int, str, str, str]] = []
    for pn in range(Q3_PAGE_START, Q3_PAGE_END + 1):
        pdir = Q3_TRANSL_ROOT / f"p{pn:04d}"
        if not pdir.exists():
            continue
        for jf in sorted(pdir.glob("r*.json")):
            try:
                d = json.loads(jf.read_text())
            except Exception:
                continue
            for lid, v in sorted(d.get("lines", {}).items()):
                vi = v.get("text_vi", "") or ""
                lg = v.get("text_vi_luangiai", "") or ""
                if vi or lg:
                    out.append((pn, f"{jf.stem}-{lid}", vi, lg))
    return out


# Cache Q3 lines at module load (1418 lines, fast)
_Q3_LINES_CACHE: list[tuple[int, str, str, str]] | None = None


def _q3_lines() -> list[tuple[int, str, str, str]]:
    global _Q3_LINES_CACHE
    if _Q3_LINES_CACHE is None:
        _Q3_LINES_CACHE = _load_q3_lines()
    return _Q3_LINES_CACHE


def _scan_q3_for_palace(
    palace: str, branch: str, stars_in_palace: list[str],
) -> list[dict[str, Any]]:
    """Find Q3 lines mentioning any star_in_palace + (palace name OR branch name).

    Returns list of {source, page, line_id, hanviet, luangiai, matched_stars}.
    """
    if not stars_in_palace:
        return []
    chinh_in_pal = [s for s in stars_in_palace if s in CHINH_TINH_NAMES]
    if not chinh_in_pal:
        return []
    out: list[dict[str, Any]] = []
    for page, lid, vi, lg in _q3_lines():
        text = vi + " " + lg
        # Match: palace name OR branch in text
        has_palace_ref = palace in text or branch in text
        if not has_palace_ref:
            continue
        matched_stars = [s for s in chinh_in_pal if s in text]
        if not matched_stars:
            continue
        out.append({
            "source": "Q3",
            "page": page,
            "line_id": lid,
            "hanviet": vi,
            "luangiai": lg,
            "matched_stars": matched_stars,
        })
    return out


def _q1_passages_for_palace(
    phu_matches: list[dict], palace: str, stars_in_palace: list[str],
) -> list[dict[str, Any]]:
    """Filter Q1 Phú passages relevant to this palace.

    Heuristic: passage matches palace if reasons mention palace name, OR
    if any star in palace appears in reasons.
    """
    out: list[dict[str, Any]] = []
    for m in phu_matches:
        reasons = m.get("reasons", [])
        reasons_text = " | ".join(reasons)
        mentions_palace = palace in reasons_text
        matched_stars = [s for s in stars_in_palace if s in reasons_text]
        if not (mentions_palace or matched_stars):
            continue
        p = m.get("passage", {})
        out.append({
            "source": "Q1 Phú Thái Vi",
            "page": p.get("page"),
            "line_id": p.get("line_id"),
            "hanviet": p.get("hanviet", ""),
            "luangiai": p.get("luangiai", ""),
            "giaithichdande": p.get("giaithichdande", ""),
            "score": m.get("score", 0),
            "reasons": reasons,
            "matched_stars": matched_stars or None,
        })
    # Sort by score desc
    out.sort(key=lambda x: -(x.get("score") or 0))
    return out


def build_cung_readings(
    chart_summary: dict[str, Any],
    phu_matches: list[dict] | None = None,
) -> dict[str, Any]:
    """Build per-palace reading bundle for a Tử Vi chart.

    Args:
        chart_summary: dict with keys: palace_to_branch, star_to_branch, menh_chu, etc.
        phu_matches: optional list of Q1 phu match dicts (from phu_matches.json).

    Returns:
        dict {
          "palaces": {palace_name: {branch, stars, chinh_tinh, star_schemas, passages}},
          "stats": {total_q3, total_q1, palaces_with_data},
        }
    """
    palace_to_branch = chart_summary.get("palace_to_branch", {})
    star_to_branch = chart_summary.get("star_to_branch", {})

    # Invert: branch → stars
    branch_to_stars: dict[str, list[str]] = {}
    for star, br in star_to_branch.items():
        branch_to_stars.setdefault(br, []).append(star)

    star_schemas = _load_chinh_tinh_schema()
    phu_matches = phu_matches or []

    palaces_data: dict[str, Any] = {}
    total_q3 = 0
    total_q1 = 0
    palaces_with_data = 0

    for palace in ALL_PALACES:
        branch = palace_to_branch.get(palace)
        if not branch:
            continue
        stars = branch_to_stars.get(branch, [])
        chinh_in_pal = [s for s in stars if s in CHINH_TINH_NAMES]

        # Star schemas for chính tinh in this palace
        schemas = {s: star_schemas.get(s, {}) for s in chinh_in_pal if s in star_schemas}

        # Mine Q3 lines
        q3_passages = _scan_q3_for_palace(palace, branch, stars)
        total_q3 += len(q3_passages)

        # Filter Q1 Phú passages
        q1_passages = _q1_passages_for_palace(phu_matches, palace, stars)
        total_q1 += len(q1_passages)

        if q3_passages or q1_passages or chinh_in_pal:
            palaces_with_data += 1

        palaces_data[palace] = {
            "branch": branch,
            "stars": stars,
            "chinh_tinh": chinh_in_pal,
            "phu_tinh": [s for s in stars if s not in CHINH_TINH_NAMES],
            "star_schemas": schemas,
            "q1_passages": q1_passages[:5],  # top 5 from Phú
            "q3_passages": q3_passages[:10],  # top 10 from Q3 (raw)
        }

    return {
        "palaces": palaces_data,
        "stats": {
            "total_q3_passages": total_q3,
            "total_q1_passages": total_q1,
            "palaces_with_data": palaces_with_data,
            "palaces_covered": len(palaces_data),
        },
    }


# CLI entry: generate cung_readings for a cached founder/person
if __name__ == "__main__":
    import sys

    person = sys.argv[1] if len(sys.argv) > 1 else "_founder"
    cache_dir = ROOT / f"data/yi_publishing/analysis_cache/{person}"
    phu_file = cache_dir / "phu_matches.json"

    if not phu_file.exists():
        print(f"❌ {phu_file} not found")
        sys.exit(1)

    phu_data = json.loads(phu_file.read_text())
    chart = phu_data["chart_summary"]
    phu_matches = phu_data.get("matched_passages", [])

    result = build_cung_readings(chart, phu_matches)
    out = cache_dir / "cung_readings.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(f"✅ {out}")
    print(f"   Stats: {result['stats']}")
