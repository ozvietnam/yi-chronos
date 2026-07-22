"""Tương hợp Pythagoras (Decoz-style multi-aspect) — đọc đồng dạng, KHÔNG predict.

So sánh Life Path / Expression / Soul Urge / Personality + Năm cá nhân hiện tại.
Ma trận: data/than_so/master/compatibility_matrix.json
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .cast import cast_than_so
from .core_numbers import reduce_number
from .interpretation import describe_number

DATA = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master" / "compatibility_matrix.json"

ASPECT_KEYS = (
    ("life_path", "Số Đường Đời"),
    ("expression", "Số Sứ Mệnh"),
    ("soul_urge", "Số Linh Hồn"),
    ("personality", "Số Nhân Cách"),
)

SCORE_POINTS = {"high": 3, "medium": 2, "low": 1}
SCORE_LABEL_VI = {"high": "Thuận khí", "medium": "Cần quan-sát", "low": "Ma sát hữu ích"}

PARADIGM = (
    "Tương hợp thần số = tấm gương cấu trúc đôi — "
    "KHÔNG phải phán ‘hợp thì cưới / khắc thì chia’. "
    "Câu hỏi đúng: hai cấu trúc này mời quan-sát / điều chỉnh điều gì?"
)

DISCLAIMER = (
    "Báo cáo này MƯỢN khung số Pythagoras để soi tương tác — "
    "không thay tư vấn tâm lý / y tế / pháp lý."
)


@lru_cache(maxsize=1)
def _matrix() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def root_digit(value: int) -> int:
    """Master → gốc để tra bảng (11→2, 22→4, 33→6)."""
    roots = {int(k): v for k, v in (_matrix().get("master_roots") or {}).items()}
    if value in roots:
        return int(roots[value])
    if value in (11, 22, 33):
        return reduce_number(value, keep_master=False)
    return int(value) if 1 <= int(value) <= 9 else reduce_number(int(value), keep_master=False)


def pair_key(a: int, b: int) -> str:
    ra, rb = root_digit(a), root_digit(b)
    lo, hi = sorted((ra, rb))
    return f"{lo}-{hi}"


def lookup_pair(a: int, b: int) -> dict:
    mtx = _matrix()
    key = pair_key(a, b)
    row = (mtx.get("pairs") or {}).get(key)
    if not row:
        return {
            "pair": key,
            "score": "medium",
            "points": 2,
            "label_vi": SCORE_LABEL_VI["medium"],
            "dynamic_vi": f"Cặp {a}–{b}: chưa có mô tả chi tiết — quan-sát khác biệt nhịp sống.",
            "gap_vi": "Hai người đang giả định mình cùng một nhịp?",
            "improve_vi": "Nói rõ nhu cầu nhịp / không gian trước khi giải quyết việc.",
            "values": [a, b],
            "roots": [root_digit(a), root_digit(b)],
        }
    score = row["score"]
    out = {
        "pair": key,
        "score": score,
        "points": SCORE_POINTS.get(score, 2),
        "label_vi": SCORE_LABEL_VI.get(score, score),
        "dynamic_vi": row.get("dynamic_vi", ""),
        "gap_vi": row.get("gap_vi", ""),
        "improve_vi": row.get("improve_vi", ""),
        "values": [a, b],
        "roots": [root_digit(a), root_digit(b)],
    }
    if row.get("cheiro_vi"):
        out["cheiro_vi"] = row["cheiro_vi"]
    return out


def _person_slice(chart: dict, label: str) -> dict:
    core = chart["core"]
    cy = chart.get("cycles") or {}
    return {
        "label": label,
        "name": chart["input"]["name_raw"],
        "birth_date": chart["input"]["birth_date"],
        "core": {k: {"value": core[k]["value"], "name_vi": core[k]["name_vi"]} for k, _ in ASPECT_KEYS},
        "personal_year": (cy.get("personal_year") or {}).get("value"),
        "personal_year_target": (cy.get("personal_year") or {}).get("target_year"),
        "archetypes": {k: describe_number(core[k]["value"]) for k, _ in ASPECT_KEYS},
    }


def analyze_compatibility(
    name_a: str,
    birth_date_a: str,
    name_b: str,
    birth_date_b: str,
    *,
    name_order_a: str = "vn",
    name_order_b: str = "vn",
    relationship_type: str = "partner",
    target_year: int | None = None,
) -> dict:
    """So sánh hai lá số Pythagoras — multi-aspect + năm cá nhân."""
    chart_a = cast_than_so(
        name_a,
        birth_date_a,
        name_order=name_order_a,
        include_chaldean=False,
        include_dong_phuong=False,
        target_year=target_year,
    )
    chart_b = cast_than_so(
        name_b,
        birth_date_b,
        name_order=name_order_b,
        include_chaldean=False,
        include_dong_phuong=False,
        target_year=target_year,
    )

    weights = (_matrix().get("aspect_weights") or {})
    aspects: list[dict] = []
    weighted = 0.0
    weight_sum = 0.0

    for key, name_vi in ASPECT_KEYS:
        va = chart_a["core"][key]["value"]
        vb = chart_b["core"][key]["value"]
        pair = lookup_pair(va, vb)
        w = float(weights.get(key, 0.25))
        weighted += pair["points"] * w
        weight_sum += w
        read = pair["dynamic_vi"]
        if pair.get("cheiro_vi"):
            read = f"{read} Cheiro: {pair['cheiro_vi']}"
        aspect_row = {
            "key": key,
            "name_vi": name_vi,
            "a": va,
            "b": vb,
            "weight": w,
            "read": read,
            "gap": pair["gap_vi"],
            "improve": pair["improve_vi"],
            **{k: pair[k] for k in ("pair", "score", "points", "label_vi", "roots")},
        }
        if pair.get("cheiro_vi"):
            aspect_row["cheiro_vi"] = pair["cheiro_vi"]
        aspects.append(aspect_row)

    max_points = 3.0
    overall_01 = (weighted / weight_sum / max_points) if weight_sum else 0.5
    overall_pct = round(overall_01 * 100)
    if overall_pct >= 75:
        band = "high"
    elif overall_pct >= 55:
        band = "medium"
    else:
        band = "low"

    lp_a = chart_a["core"]["life_path"]["value"]
    lp_b = chart_b["core"]["life_path"]["value"]
    composite_raw = root_digit(lp_a) + root_digit(lp_b)
    composite = reduce_number(composite_raw, keep_master=True)

    py_a = (chart_a.get("cycles") or {}).get("personal_year") or {}
    py_b = (chart_b.get("cycles") or {}).get("personal_year") or {}
    year_pair = None
    if py_a.get("value") is not None and py_b.get("value") is not None:
        year_pair = lookup_pair(py_a["value"], py_b["value"])

    rel_hint = {
        "spouse": "Trong quan hệ đôi lâu dài: ưu tiên cải thiện Life Path + Soul Urge trước.",
        "partner": "Trong quan hệ đối tác: ưu tiên Expression (cách làm việc/biểu đạt) + Life Path.",
        "family": "Trong gia đình: ưu tiên Personality (cách hiện diện) + Soul Urge (nhu cầu sâu).",
        "colleague": "Trong công việc: ưu tiên Expression + Personality; Life Path là nền dài hạn.",
        "friend": "Trong bạn bè: ưu tiên Personality + Soul Urge; giữ khoảng tự do.",
    }.get(relationship_type, "Quan-sát cả bốn lớp số; đừng chỉ nhìn một con số.")

    return {
        "schema_version": "v2-compat",
        "method_id": "pythagorean_compatibility_decoz_style",
        "paradigm_note": PARADIGM,
        "disclaimer": DISCLAIMER,
        "relationship_type": relationship_type,
        "relationship_hint": rel_hint,
        "person_a": _person_slice(chart_a, "A"),
        "person_b": _person_slice(chart_b, "B"),
        "aspects": aspects,
        "overall": {
            "percent": overall_pct,
            "band": band,
            "label_vi": SCORE_LABEL_VI[band],
            "weighted_points": round(weighted, 3),
            "read": (
                f"Tổng hợp {overall_pct}/100 ({SCORE_LABEL_VI[band]}): "
                "điểm phản ánh mức thuận khí cấu trúc — không phải lời tiên tri về tương lai quan hệ."
            ),
            "gap": "Anh/chị đang dùng điểm số để phán quan hệ thay vì quan-sát ma sát cụ thể?",
            "improve": rel_hint,
        },
        "composite_life_path": {
            "value": composite,
            "raw": composite_raw,
            "from": [lp_a, lp_b],
            "archetype": describe_number(composite),
            "read": (
                f"Số ghép Đường Đời (gốc {root_digit(lp_a)}+{root_digit(lp_b)}→{composite}): "
                "khí của ‘đôi như một thực thể’ — để quan-sát, không để đoán vận."
            ),
        },
        "personal_year": {
            "a": py_a.get("value"),
            "b": py_b.get("value"),
            "target_year": py_a.get("target_year") or py_b.get("target_year"),
            "pair": year_pair,
            "read": (
                None
                if not year_pair
                else (
                    f"Năm cá nhân hiện tại {py_a.get('value')} × {py_b.get('value')}: "
                    f"{year_pair['dynamic_vi']}"
                )
            ),
            "improve": None if not year_pair else year_pair.get("improve_vi"),
        },
    }
