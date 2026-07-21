"""Tính số cốt lõi Pythagoras — chuẩn Decoz (Method A + per-name-part).

Công thức: data/than_so/master/pythagorean_spec.json
"""
from __future__ import annotations

from .constants import KARMIC_DEBT_NUMBERS, MASTER_NUMBERS
from .name_calculator import is_vowel, letter_value, letters_only, name_breakdown
from .name_parts import split_name_parts


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def reduce_number(n: int, keep_master: bool = True) -> int:
    """Rút gọn về 1 chữ số, GIỮ master 11/22/33 nếu keep_master."""
    while n > 9 and not (keep_master and n in MASTER_NUMBERS):
        n = digit_sum(n)
    return n


def reduce_with_trace(n: int, keep_master: bool = True) -> dict:
    """Trả {raw, reduced, steps, karmic_debt} — raw/steps để audit + nợ nghiệp."""
    karmic = n if n in KARMIC_DEBT_NUMBERS else None
    steps = [n]
    cur = n
    while cur > 9 and not (keep_master and cur in MASTER_NUMBERS):
        cur = digit_sum(cur)
        steps.append(cur)
        if cur in KARMIC_DEBT_NUMBERS and karmic is None:
            karmic = cur
    return {"raw": n, "reduced": cur, "steps": steps, "karmic_debt": karmic}


def _sum_letters_flat(text: str, system: str, which: str) -> int:
    """Cộng chữ trong MỘT chuỗi (một phần tên). which = all|vowels|consonants."""
    letters = letters_only(text)
    total = 0
    for i, ch in enumerate(letters):
        v = is_vowel(letters, i)
        if which == "all" or (which == "vowels" and v) or (which == "consonants" and not v):
            total += letter_value(ch, system)
    return total


def _name_number_per_parts(
    name: str,
    system: str,
    which: str,
    name_vi: str,
    name_order: str = "vn",
) -> dict:
    """Decoz: rút từng phần tên rồi cộng — không cộng tràn cả chuỗi."""
    split = split_name_parts(name, name_order)
    part_traces: list[dict] = []
    part_values: list[int] = []
    for part in split["parts"]:
        raw = _sum_letters_flat(part, system, which)
        if which != "all" and raw == 0 and not letters_only(part):
            continue
        # Phần không có nguyên âm/phụ âm tương ứng → bỏ qua (không cộng 0 giả)
        letters = letters_only(part)
        if which == "vowels" and not any(is_vowel(letters, i) for i in range(len(letters))):
            continue
        if which == "consonants" and all(is_vowel(letters, i) for i in range(len(letters))):
            continue
        tr = reduce_with_trace(raw)
        part_traces.append({"part": part, **tr})
        part_values.append(tr["reduced"])

    if not part_values:
        # Fallback: cả tên phẳng (tên rỗng phụ âm hiếm)
        raw = _sum_letters_flat(name, system, which)
        tr = reduce_with_trace(raw)
        return {
            "name_vi": name_vi,
            "value": tr["reduced"],
            "raw": raw,
            "steps": tr["steps"],
            "karmic_debt": tr["karmic_debt"],
            "parts": [],
        }

    total_raw = sum(part_values)
    final = reduce_with_trace(total_raw)
    # Karmic: ưu tiên từ tổng cuối, rồi từ từng phần
    karmic = final["karmic_debt"]
    if karmic is None:
        for pt in part_traces:
            if pt.get("karmic_debt"):
                karmic = pt["karmic_debt"]
                break

    return {
        "name_vi": name_vi,
        "value": final["reduced"],
        "raw": total_raw,
        "steps": final["steps"],
        "karmic_debt": karmic,
        "parts": part_traces,
    }


def life_path(day: int, month: int, year: int) -> dict:
    """Số Đường Đời — Decoz Method A."""
    d = reduce_number(day)
    m = reduce_number(month)
    y = reduce_number(year)
    total = d + m + y
    trace = reduce_with_trace(total)
    return {
        "name_vi": "Số Đường Đời",
        "value": trace["reduced"],
        "components": {"day": d, "month": m, "year": y},
        "raw": total,
        "steps": trace["steps"],
        "karmic_debt": trace["karmic_debt"],
    }


def life_path_single_digit(lp_value: int) -> int:
    """Dùng cho tuổi đỉnh/period: Decoz yêu cầu rút Master về đơn."""
    return reduce_number(lp_value, keep_master=False)


def compute_core(
    name: str,
    day: int,
    month: int,
    year: int,
    system: str = "pythagorean",
    name_order: str = "vn",
) -> dict:
    lp = life_path(day, month, year)
    expression = _name_number_per_parts(name, system, "all", "Số Sứ Mệnh", name_order)
    soul = _name_number_per_parts(name, system, "vowels", "Số Linh Hồn", name_order)
    personality = _name_number_per_parts(name, system, "consonants", "Số Nhân Cách", name_order)

    bday_trace = reduce_with_trace(day)
    birthday = {
        "name_vi": "Số Ngày Sinh",
        "value": bday_trace["reduced"],
        "raw_day": day,
        "compound": day if day > 9 else None,
        "steps": bday_trace["steps"],
        "karmic_debt": bday_trace["karmic_debt"],
    }

    maturity_raw = lp["value"] + expression["value"]
    maturity_tr = reduce_with_trace(maturity_raw)
    maturity = {
        "name_vi": "Số Trưởng Thành",
        "value": maturity_tr["reduced"],
        "raw": maturity_raw,
        "steps": maturity_tr["steps"],
        "karmic_debt": maturity_tr["karmic_debt"],
    }

    return {
        "system": system,
        "name_order": name_order,
        "life_path": lp,
        "expression": expression,
        "soul_urge": soul,
        "personality": personality,
        "birthday": birthday,
        "maturity": maturity,
        "breakdown": name_breakdown(name, system),
        "name_parts": split_name_parts(name, name_order),
    }
