"""Lớp BIẾN — Pinnacle / Challenge / Period / Personal YMD / Transit / Essence.

Chuẩn Decoz: data/than_so/master/pythagorean_spec.json
"""
from __future__ import annotations

from datetime import date

from .core_numbers import life_path_single_digit, reduce_number
from .name_calculator import letter_value, letters_only
from .name_parts import split_name_parts


def _abs_challenge(a: int, b: int) -> int:
    return reduce_number(abs(a - b), keep_master=False)


def pinnacles_and_challenges(day: int, month: int, year: int) -> dict:
    # Pinnacles: giữ Master khi rút M/D/Y
    m = reduce_number(month)
    d = reduce_number(day)
    y = reduce_number(year)
    lp = reduce_number(m + d + y)
    lp_single = life_path_single_digit(lp)

    p1 = reduce_number(m + d)
    p2 = reduce_number(d + y)
    p3 = reduce_number(p1 + p2)
    p4 = reduce_number(m + y)

    # Challenges: Decoz — bỏ Master (rút về đơn) trước khi trừ
    cm = reduce_number(month, keep_master=False)
    cd = reduce_number(day, keep_master=False)
    cy = reduce_number(year, keep_master=False)
    c1 = _abs_challenge(cm, cd)
    c2 = _abs_challenge(cd, cy)
    c3 = _abs_challenge(c1, c2)
    c4 = _abs_challenge(cm, cy)

    first_end_age = 36 - lp_single
    return {
        "pinnacles": [
            {"index": 1, "value": p1, "age_range": f"0–{first_end_age}", "age_end": first_end_age},
            {
                "index": 2,
                "value": p2,
                "age_range": f"{first_end_age + 1}–{first_end_age + 9}",
                "age_start": first_end_age + 1,
                "age_end": first_end_age + 9,
            },
            {
                "index": 3,
                "value": p3,
                "age_range": f"{first_end_age + 10}–{first_end_age + 18}",
                "age_start": first_end_age + 10,
                "age_end": first_end_age + 18,
            },
            {
                "index": 4,
                "value": p4,
                "age_range": f"{first_end_age + 19}+",
                "age_start": first_end_age + 19,
            },
        ],
        "challenges": [
            {"index": 1, "value": c1},
            {"index": 2, "value": c2},
            {"index": 3, "value": c3, "main": True},
            {"index": 4, "value": c4},
        ],
    }


def period_cycles(day: int, month: int, year: int) -> list[dict]:
    """3 chu kỳ đời + tuổi kết thúc theo Decoz (P2 = đúng 27 năm)."""
    m = reduce_number(month)
    d = reduce_number(day)
    y = reduce_number(year)
    lp = reduce_number(m + d + y)
    lp_single = life_path_single_digit(lp)
    p1_end = 36 - lp_single
    p2_end = p1_end + 27
    return [
        {
            "index": 1,
            "name_vi": "Chu kỳ đầu (thanh xuân)",
            "value": m,
            "age_range": f"0–{p1_end}",
            "age_end": p1_end,
        },
        {
            "index": 2,
            "name_vi": "Chu kỳ giữa (trung niên)",
            "value": d,
            "age_range": f"{p1_end + 1}–{p2_end}",
            "age_start": p1_end + 1,
            "age_end": p2_end,
            "duration_years": 27,
        },
        {
            "index": 3,
            "name_vi": "Chu kỳ cuối (viên mãn)",
            "value": y,
            "age_range": f"{p2_end + 1}+",
            "age_start": p2_end + 1,
        },
    ]


def personal_year(day: int, month: int, target_year: int) -> dict:
    raw = reduce_number(month) + reduce_number(day) + reduce_number(target_year)
    return {
        "target_year": target_year,
        "value": reduce_number(raw, keep_master=False),
        "raw": raw,
    }


def personal_month(day: int, month: int, target_year: int, target_month: int) -> dict:
    py = personal_year(day, month, target_year)
    raw = py["value"] + reduce_number(target_month, keep_master=False)
    return {
        "target_year": target_year,
        "target_month": target_month,
        "personal_year": py["value"],
        "value": reduce_number(raw, keep_master=False),
        "raw": raw,
    }


def personal_day(
    day: int,
    month: int,
    target_year: int,
    target_month: int,
    target_day: int,
) -> dict:
    pm = personal_month(day, month, target_year, target_month)
    raw = pm["value"] + reduce_number(target_day, keep_master=False)
    return {
        "target_year": target_year,
        "target_month": target_month,
        "target_day": target_day,
        "personal_month": pm["value"],
        "value": reduce_number(raw, keep_master=False),
        "raw": raw,
    }


def _transit_letter_at_age(name_letters: str, age: int, system: str = "pythagorean") -> dict | None:
    """Letter covering `age` (from 0), each letter lasts its Pythagorean value years."""
    if not name_letters:
        return None
    letters = letters_only(name_letters)
    if not letters:
        return None
    # Build repeating timeline
    timeline: list[tuple[str, int]] = []
    # Safety: cover ages 0..120
    pos = 0
    idx = 0
    while pos <= max(age, 120):
        ch = letters[idx % len(letters)]
        dur = letter_value(ch, system) or 1
        for _ in range(dur):
            timeline.append((ch, dur))
            pos += 1
            if pos > 120:
                break
        idx += 1
    if age >= len(timeline):
        # extend more
        while len(timeline) <= age:
            ch = letters[idx % len(letters)]
            dur = letter_value(ch, system) or 1
            for _ in range(dur):
                timeline.append((ch, dur))
            idx += 1
    ch, dur = timeline[age]
    return {"letter": ch, "value": letter_value(ch, system), "duration": dur}


def transits_and_essence(
    name: str,
    age: int,
    name_order: str = "vn",
    system: str = "pythagorean",
) -> dict:
    """Transit Physical/Mental/Spiritual + Essence tại tuổi `age` (từ 0)."""
    split = split_name_parts(name, name_order)
    first = split["first_name"]
    middle = split["middle_name"]
    last = split["last_name"]

    physical = _transit_letter_at_age(first, age, system)
    if middle:
        mental = _transit_letter_at_age(middle, age, system)
        spiritual = _transit_letter_at_age(last, age, system) if last else mental
    else:
        # Decoz: no middle → Mental & Spiritual merge from last name
        merged = _transit_letter_at_age(last or first, age, system)
        mental = merged
        spiritual = merged

    vals = [t["value"] for t in (physical, mental, spiritual) if t]
    essence_raw = sum(vals)
    essence_value = reduce_number(essence_raw)
    return {
        "age": age,
        "physical": physical,
        "mental": mental,
        "spiritual": spiritual,
        "essence": {
            "name_vi": "Essence",
            "raw": essence_raw,
            "value": essence_value,
        },
    }


def age_digit(birth: date, on_date: date) -> dict:
    """Age Digit = tuổi trước sinh nhật + tuổi sau sinh nhật trong năm lịch on_date."""
    year_age_before_bday = max(0, on_date.year - birth.year - 1)
    year_age_after_bday = year_age_before_bday + 1
    raw = year_age_before_bday + year_age_after_bday
    return {
        "name_vi": "Age Digit",
        "value": reduce_number(raw, keep_master=False),
        "raw": raw,
        "age_before_birthday": year_age_before_bday,
        "age_after_birthday": year_age_after_bday,
        "calendar_year": on_date.year,
    }


def personal_calendar(
    day: int,
    month: int,
    start_year: int,
    start_month: int,
    months: int = 24,
) -> list[dict]:
    """Lịch Personal Month 12–24 tháng tới (Decoz) — checklist hành động theo khí."""
    out: list[dict] = []
    y, m = start_year, start_month
    for _ in range(max(1, months)):
        pm = personal_month(day, month, y, m)
        out.append({
            "year": y,
            "month": m,
            "label": f"{y:04d}-{m:02d}",
            "personal_year": pm["personal_year"],
            "personal_month": pm["value"],
        })
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def build_cycles(
    day: int,
    month: int,
    year: int,
    name: str,
    name_order: str = "vn",
    target_year: int | None = None,
    target_month: int | None = None,
    target_day: int | None = None,
    as_of: date | None = None,
    calendar_months: int = 24,
) -> dict:
    """Gói đầy đủ chu kỳ cho cast."""
    as_of = as_of or date.today()
    ty = target_year if target_year is not None else as_of.year
    tm = target_month if target_month is not None else as_of.month
    td = target_day if target_day is not None else as_of.day

    birth = date(year, month, day)
    # Age for transit: completed years as of as_of
    age = as_of.year - birth.year
    if (as_of.month, as_of.day) < (birth.month, birth.day):
        age -= 1
    age = max(0, age)

    pc = pinnacles_and_challenges(day, month, year)
    py = personal_year(day, month, ty)
    pm = personal_month(day, month, ty, tm)
    pd = personal_day(day, month, ty, tm, td)
    te = transits_and_essence(name, age, name_order)
    duality = {
        "name_vi": "Duality (Essence × Personal Year)",
        "essence": te["essence"]["value"],
        "personal_year": py["value"],
        "pair": [te["essence"]["value"], py["value"]],
    }

    return {
        **pc,
        "period_cycles": period_cycles(day, month, year),
        "personal_year": py,
        "personal_month": pm,
        "personal_day": pd,
        "personal_calendar": personal_calendar(day, month, ty, tm, calendar_months),
        "transits": te,
        "essence": te["essence"],
        "duality": duality,
        "age_digit": age_digit(birth, as_of),
        "as_of": as_of.isoformat(),
        "age": age,
    }
