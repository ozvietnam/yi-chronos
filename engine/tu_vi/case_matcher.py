"""Tử Vi — Historical Case Studies Matcher.

Match lá số user với các "lá số mẫu" rút từ Q3+Q4 Tử Vi Đẩu Số Toàn Thư.

Paradigm (theo thâm nhuần Q4 + Iron Rule #6):
- KHÔNG predict "anh sẽ giống X"
- Surface NÉT GIỐNG về cấu trúc sao+cung như dẫn chứng phê mệnh
- Luôn present 2 paradigm khi có tension (vd Tử Phá Thìn Tuất: Trần Đoàn cát vs Khang Tiết hung)
- Dùng "mỗ" pattern — gợi mở, không phán cứng

Reference: `data/tu_vi/case_studies.json` schema_version=tu_vi_case_studies_v1
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CASE_STUDIES_PATH = ROOT / "data/tu_vi/case_studies.json"
BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

_cases_cache: dict | None = None


def _load_cases() -> dict:
    global _cases_cache
    if _cases_cache is None:
        _cases_cache = json.loads(CASE_STUDIES_PATH.read_text())
    return _cases_cache


def _stars_at_palace(la_so: dict, palace_name: str) -> list[str]:
    """Get all chính tinh + phụ tinh + sát tinh at the given palace."""
    palaces = la_so.get("palaces", [])
    palace = next((p for p in palaces if p["name"] == palace_name), None)
    if not palace:
        return []
    bi = palace["branch_index"]
    chinh = la_so.get("chinh_tinh", {})
    phu = la_so.get("phu_tinh", {})
    sat = la_so.get("sat_tinh", {})
    out = []
    for name, idx in {**chinh, **phu, **sat}.items():
        if idx == bi:
            out.append(name)
    return out


def _menh_info(la_so: dict) -> tuple[str | None, list[str]]:
    """Return (menh_branch_name, stars_at_menh)."""
    palaces = la_so.get("palaces", [])
    menh = next((p for p in palaces if p["name"] == "Mệnh"), None)
    if not menh:
        return None, []
    branch_name = BRANCHES[menh["branch_index"]]
    return branch_name, _stars_at_palace(la_so, "Mệnh")


def _tam_hop_branches(branch_name: str) -> list[str]:
    """Tam hợp: Dần-Ngọ-Tuất, Thân-Tý-Thìn, Tỵ-Dậu-Sửu, Hợi-Mão-Mùi."""
    groups = [
        {"Dần", "Ngọ", "Tuất"},
        {"Thân", "Tý", "Thìn"},
        {"Tỵ", "Dậu", "Sửu"},
        {"Hợi", "Mão", "Mùi"},
    ]
    for g in groups:
        if branch_name in g:
            return sorted(g)
    return []


def _check_pattern(la_so: dict, pattern: dict) -> dict:
    """Check 1 pattern against la_so. Returns:
      {matched: bool, score: int, reasons: list[str], gaps: list[str]}
    """
    menh_branch, menh_stars = _menh_info(la_so)
    if not menh_branch:
        return {"matched": False, "score": 0, "reasons": [], "gaps": ["no_menh"]}

    score = 0
    reasons: list[str] = []
    gaps: list[str] = []

    # Required menh branch
    required_branch = pattern.get("menh_branch")
    branch_any = pattern.get("menh_branch_any", [])
    if required_branch:
        if menh_branch == required_branch:
            score += 5
            reasons.append(f"Mệnh tại {menh_branch} ✓")
        else:
            gaps.append(f"Mệnh phải tại {required_branch} (anh tại {menh_branch})")
            return {"matched": False, "score": 0, "reasons": reasons, "gaps": gaps}
    elif branch_any:
        if menh_branch in branch_any:
            score += 5
            reasons.append(f"Mệnh tại {menh_branch} ∈ {branch_any} ✓")
        else:
            gaps.append(f"Mệnh phải ∈ {branch_any} (anh tại {menh_branch})")
            return {"matched": False, "score": 0, "reasons": reasons, "gaps": gaps}

    # Required chính tinh
    required = set(pattern.get("menh_chinh_tinh_required", []))
    menh_star_set = set(menh_stars)
    missing = required - menh_star_set
    if missing:
        gaps.append(f"Thiếu chính tinh required: {sorted(missing)}")
        return {"matched": False, "score": 0, "reasons": reasons, "gaps": gaps}
    if required:
        score += 5 * len(required)
        reasons.append(f"Mệnh có {sorted(required)} ✓")

    # Supporting stars (any)
    supporting = set(pattern.get("supporting_stars_any", []))
    if supporting:
        # Check anywhere on the chart (any palace) — these are sao chiếu
        all_stars = set(la_so.get("chinh_tinh", {}).keys()) | set(la_so.get("phu_tinh", {}).keys())
        matched_support = supporting & all_stars
        if matched_support:
            score += 2 * len(matched_support)
            reasons.append(f"Có sao trợ {sorted(matched_support)} ✓")

    # Tam hợp
    tam_hop_req = pattern.get("tam_hop_required")
    if tam_hop_req:
        tam_hop = _tam_hop_branches(menh_branch)
        if "-".join(tam_hop) == tam_hop_req or tam_hop_req in "-".join(tam_hop):
            score += 3
            reasons.append(f"Tam hợp {tam_hop_req} ✓")
        else:
            gaps.append(f"Tam hợp khác: {'-'.join(tam_hop)} vs yêu cầu {tam_hop_req}")

    return {
        "matched": True,
        "score": score,
        "reasons": reasons,
        "gaps": gaps,
    }


def match_cases(la_so: dict, top_n: int = 3) -> dict:
    """Match la_so against all case patterns.

    Returns:
        {
            "matches": [{"pattern_id", "pattern_name", "polarity", "score",
                         "reasons", "gaps", "figures", "lesson_short", "warning",
                         "source_ref", "key_phrase_hv"}],
            "paradigm_note": str
        }
    """
    cases = _load_cases()
    patterns = cases.get("patterns", [])
    results: list[dict] = []

    for p in patterns:
        check = _check_pattern(la_so, p.get("chart_pattern", {}))
        if not check["matched"]:
            continue
        results.append({
            "pattern_id": p["id"],
            "pattern_name": p["name_vi"],
            "pattern_name_zh": p.get("name_zh", ""),
            "polarity": p["polarity"],
            "score": check["score"],
            "reasons": check["reasons"],
            "gaps": check["gaps"],
            "figures": p.get("historical_figures", []),
            "lesson_short": p.get("lesson_short", ""),
            "lesson_long": p.get("lesson_long", ""),
            "warning": p.get("warning", ""),
            "source_ref": p.get("source_ref", {}),
            "key_phrase_hv": p.get("key_phrase_hv", ""),
            "key_phrase_zh": p.get("key_phrase_zh", ""),
            "key_phrase_hv_tran": p.get("key_phrase_hv_tran", ""),
            "key_phrase_hv_khang_tiet": p.get("key_phrase_hv_khang_tiet", ""),
        })

    # Sort by score desc
    results.sort(key=lambda r: -r["score"])

    return {
        "matches": results[:top_n],
        "paradigm_note": cases.get("paradigm_note", ""),
        "anti_predict_guards": cases.get("engine_notes", {}).get("anti_predict_guards", []),
    }


if __name__ == "__main__":
    # CLI test with founder chart
    import sys
    sys.path.insert(0, str(ROOT))
    from engine.tu_vi.an_sao import cast_la_so
    from core.chronos import calculate_chronos_state

    chronos = calculate_chronos_state("1988-06-05T23:30:00", "Asia/Ho_Chi_Minh")
    d_str, m_str, _ = chronos.almanac.lunar_date.split("/")
    year_parts = chronos.ganzhi.year.split()
    la_so = cast_la_so(
        lunar_month=int(m_str),
        lunar_day=int(d_str),
        hour_branch="Tý",
        year_stem=year_parts[0],
        year_branch=year_parts[1],
        gender="nam",
    )
    result = match_cases(la_so)
    print(json.dumps(result, ensure_ascii=False, indent=2))
