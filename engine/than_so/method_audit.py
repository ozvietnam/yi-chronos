"""So sánh Method A (Decoz) vs shortcut phổ biến — dựng tin cậy / audit."""
from __future__ import annotations

from .core_numbers import life_path, reduce_with_trace


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


def method_audit(day: int, month: int, year: int) -> dict:
    """Trả Decoz Method A + 2 shortcut + cờ diverged / karmic_hidden."""
    correct = life_path(day, month, year)
    s1 = life_path_shortcut_digit_string(day, month, year)
    s2 = life_path_shortcut_unit_sum(day, month, year)
    diverged = correct["value"] != s1["value"] or correct["value"] != s2["value"]
    karmic_hidden = bool(
        correct.get("karmic_debt")
        and correct["karmic_debt"] not in (s1.get("karmic_debt"), s2.get("karmic_debt"))
    )
    return {
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
