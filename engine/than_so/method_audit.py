"""So sánh Method A (Decoz) vs shortcut phổ biến — dựng tin cậy / audit."""
from __future__ import annotations

from .core_numbers import (
    _name_number_per_parts,
    _sum_letters_flat,
    life_path,
    reduce_with_trace,
)
from .name_calculator import normalize_vietnamese


def life_path_shortcut_digit_string(day: int, month: int, year: int) -> dict:
    """Cộng mọi chữ số ngày-tháng-năm rồi rút — Decoz gọi là SAI."""
    digits = f"{month}{day}{year}"
    raw = sum(int(ch) for ch in digits)
    tr = reduce_with_trace(raw)
    return {"method": "digit_string_shortcut", "raw": raw, "value": tr["reduced"], "steps": tr["steps"], "karmic_debt": tr["karmic_debt"]}


def life_path_shortcut_unit_sum(day: int, month: int, year: int) -> dict:
    """Cộng tháng+ngày+năm (chưa rút từng đơn vị) rồi rút — cũng SAI theo Decoz."""
    raw = month + day + year
    tr = reduce_with_trace(raw)
    return {"method": "unit_sum_shortcut", "raw": raw, "value": tr["reduced"], "steps": tr["steps"], "karmic_debt": tr["karmic_debt"]}


def expression_name_audit(name: str, name_order: str = "vn", system: str = "pythagorean") -> dict:
    """Decoz rút từng phần tên vs shortcut cộng tràn cả chuỗi.

    Fixture lệch: Mary Ann Smith → Decoz Expression 2, flat shortcut 11.
    """
    normalized = normalize_vietnamese(name)
    decoz = _name_number_per_parts(
        normalized, system, "all", "Số Sứ Mệnh", name_order=name_order
    )
    flat_raw = _sum_letters_flat(normalized, system, "all")
    flat = reduce_with_trace(flat_raw)
    master_in_parts = [
        {"part": p["part"], "value": p["reduced"]}
        for p in (decoz.get("parts") or [])
        if p.get("reduced") in (11, 22, 33)
    ]
    diverged = decoz["value"] != flat["reduced"]
    master_hidden = bool(master_in_parts) and flat["reduced"] not in (11, 22, 33)
    karmic_in_parts = [p.get("karmic_debt") for p in (decoz.get("parts") or []) if p.get("karmic_debt")]
    karmic_hidden = bool(karmic_in_parts) and not flat.get("karmic_debt")
    return {
        "name_vi": "Kiểm chứng Expression (rút từng phần tên)",
        "decoz_per_part": {
            "value": decoz["value"],
            "raw": decoz["raw"],
            "steps": decoz["steps"],
            "karmic_debt": decoz.get("karmic_debt"),
            "parts": decoz.get("parts") or [],
        },
        "flat_full_name_shortcut": {
            "method": "flat_full_name_sum",
            "raw": flat_raw,
            "value": flat["reduced"],
            "steps": flat["steps"],
            "karmic_debt": flat.get("karmic_debt"),
        },
        "diverged": diverged,
        "master_in_parts": master_in_parts,
        "master_hidden_by_flat": master_hidden,
        "karmic_hidden_by_flat": karmic_hidden,
        "note": (
            "Chuẩn YI = Decoz: rút từng phần Họ/Đệm/Tên rồi cộng. "
            "Cộng tràn cả chuỗi có thể lệch số cuối hoặc che Master/Karmic từng phần."
        ),
    }


def method_audit(
    day: int,
    month: int,
    year: int,
    name: str | None = None,
    name_order: str = "vn",
    system: str = "pythagorean",
) -> dict:
    """Trả Decoz Method A + 2 shortcut Life Path (+ Expression name audit nếu có tên)."""
    correct = life_path(day, month, year)
    s1 = life_path_shortcut_digit_string(day, month, year)
    s2 = life_path_shortcut_unit_sum(day, month, year)
    diverged = correct["value"] != s1["value"] or correct["value"] != s2["value"]
    karmic_hidden = bool(
        correct.get("karmic_debt")
        and correct["karmic_debt"] not in (s1.get("karmic_debt"), s2.get("karmic_debt"))
    )
    out = {
        "name_vi": "Kiểm chứng công thức Life Path",
        "decoz_method_a": {
            "value": correct["value"],
            "components": correct["components"],
            "raw": correct["raw"],
            "steps": correct["steps"],
            "karmic_debt": correct.get("karmic_debt"),
        },
        "shortcut_digit_string": s1,
        "shortcut_unit_sum": s2,
        "diverged": diverged,
        "karmic_hidden_by_shortcut": karmic_hidden,
        "note": (
            "Chuẩn YI = Decoz Method A (rút riêng tháng/ngày/năm). "
            "Shortcut có thể trùng số cuối nhưng mất Master/Karmic trung gian."
        ),
    }
    if name and name.strip():
        out["expression"] = expression_name_audit(name, name_order=name_order, system=system)
    return out
