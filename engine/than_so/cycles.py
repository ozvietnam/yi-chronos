"""Lớp BIẾN — chu kỳ thời gian (Pinnacle / Challenge / Period / Personal Year).

Tương ứng Đại Vận / Lưu Niên của Tử Vi (Iron Rule #6 CƠ+BIẾN).
Công thức: worldnumerology.com (Decoz) + affinitynumerology.
"""
from __future__ import annotations

from .core_numbers import reduce_number


def _abs_challenge(a: int, b: int) -> int:
    # Thử thách dùng trị tuyệt đối hiệu, KHÔNG giữ master (0-8).
    return reduce_number(abs(a - b), keep_master=False)


def pinnacles_and_challenges(day: int, month: int, year: int) -> dict:
    m = reduce_number(month)
    d = reduce_number(day)
    y = reduce_number(year)
    life_path = reduce_number(reduce_number(day) + reduce_number(month) + reduce_number(year))

    p1 = reduce_number(m + d)
    p2 = reduce_number(d + y)
    p3 = reduce_number(p1 + p2)
    p4 = reduce_number(m + y)

    c1 = _abs_challenge(m, d)
    c2 = _abs_challenge(d, y)
    c3 = _abs_challenge(c1, c2)
    c4 = _abs_challenge(m, y)

    first_end_age = 36 - life_path
    return {
        "pinnacles": [
            {"index": 1, "value": p1, "age_range": f"0–{first_end_age}"},
            {"index": 2, "value": p2, "age_range": f"{first_end_age + 1}–{first_end_age + 9}"},
            {"index": 3, "value": p3, "age_range": f"{first_end_age + 10}–{first_end_age + 18}"},
            {"index": 4, "value": p4, "age_range": f"{first_end_age + 19}+"},
        ],
        "challenges": [
            {"index": 1, "value": c1},
            {"index": 2, "value": c2},
            {"index": 3, "value": c3, "main": True},
            {"index": 4, "value": c4},
        ],
    }


def period_cycles(day: int, month: int, year: int) -> list[dict]:
    return [
        {"index": 1, "name_vi": "Chu kỳ đầu (thanh xuân)", "value": reduce_number(month)},
        {"index": 2, "name_vi": "Chu kỳ giữa (trung niên)", "value": reduce_number(day)},
        {"index": 3, "name_vi": "Chu kỳ cuối (viên mãn)", "value": reduce_number(year)},
    ]


def personal_year(day: int, month: int, target_year: int) -> dict:
    raw = reduce_number(month) + reduce_number(day) + reduce_number(target_year)
    return {"target_year": target_year, "value": reduce_number(raw, keep_master=False)}
