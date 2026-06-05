"""Tính 6 số cốt lõi + số mở rộng (Pythagoras / Chaldean).

Công thức theo chuẩn Decoz (rút gọn riêng từng thành phần để tránh sai số).
"""
from __future__ import annotations

from .constants import KARMIC_DEBT_NUMBERS, MASTER_NUMBERS
from .name_calculator import is_vowel, letter_value, letters_only, name_breakdown


def digit_sum(n: int) -> int:
    return sum(int(d) for d in str(abs(n)))


def reduce_number(n: int, keep_master: bool = True) -> int:
    """Rút gọn về 1 chữ số, GIỮ master 11/22/33 nếu keep_master."""
    while n > 9 and not (keep_master and n in MASTER_NUMBERS):
        n = digit_sum(n)
    return n


def reduce_with_trace(n: int, keep_master: bool = True) -> dict:
    """Trả {raw, reduced, karmic_debt} — raw để phát hiện nợ nghiệp."""
    karmic = n if n in KARMIC_DEBT_NUMBERS else None
    steps = [n]
    cur = n
    while cur > 9 and not (keep_master and cur in MASTER_NUMBERS):
        cur = digit_sum(cur)
        steps.append(cur)
        if cur in KARMIC_DEBT_NUMBERS:
            karmic = cur
    return {"raw": n, "reduced": cur, "steps": steps, "karmic_debt": karmic}


def _sum_letters(name: str, system: str, which: str) -> int:
    """which = 'all' | 'vowels' | 'consonants'."""
    letters = letters_only(name)
    total = 0
    for i, ch in enumerate(letters):
        v = is_vowel(letters, i)
        if which == "all" or (which == "vowels" and v) or (which == "consonants" and not v):
            total += letter_value(ch, system)
    return total


def life_path(day: int, month: int, year: int) -> dict:
    """Số Đường Đời — rút gọn riêng ngày/tháng/năm rồi cộng (chuẩn Decoz)."""
    d = reduce_number(day)
    m = reduce_number(month)
    y = reduce_number(year)
    total = d + m + y
    trace = reduce_with_trace(total)
    return {
        "name_vi": "Số Đường Đời",
        "value": trace["reduced"],
        "components": {"day": d, "month": m, "year": y},
        "karmic_debt": trace["karmic_debt"],
    }


def _name_number(name: str, system: str, which: str, name_vi: str) -> dict:
    raw = _sum_letters(name, system, which)
    trace = reduce_with_trace(raw)
    return {
        "name_vi": name_vi,
        "value": trace["reduced"],
        "raw": raw,
        "karmic_debt": trace["karmic_debt"],
    }


def compute_core(name: str, day: int, month: int, year: int, system: str = "pythagorean") -> dict:
    lp = life_path(day, month, year)
    expression = _name_number(name, system, "all", "Số Sứ Mệnh")
    soul = _name_number(name, system, "vowels", "Số Linh Hồn")
    personality = _name_number(name, system, "consonants", "Số Nhân Cách")
    birthday = {"name_vi": "Số Ngày Sinh", "value": reduce_number(day), "raw_day": day}
    maturity_raw = lp["value"] + expression["value"]
    maturity = {"name_vi": "Số Trưởng Thành", "value": reduce_number(maturity_raw), "raw": maturity_raw}

    return {
        "system": system,
        "life_path": lp,
        "expression": expression,
        "soul_urge": soul,
        "personality": personality,
        "birthday": birthday,
        "maturity": maturity,
        "breakdown": name_breakdown(name, system),
    }
