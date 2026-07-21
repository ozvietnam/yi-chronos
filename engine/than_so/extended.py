"""Số mở rộng Pythagoras (Decoz extended chart) — Attitude, Bridges, Planes, …"""
from __future__ import annotations

from collections import Counter

from .core_numbers import reduce_number, reduce_with_trace
from .name_calculator import letter_value, letters_only
from .name_parts import split_name_parts

# Decoz Planes of Expression letter sets
PLANE_PHYSICAL = frozenset("DEMW")
PLANE_MENTAL = frozenset("AGHJLNP")
PLANE_EMOTIONAL = frozenset("BIORSTXZ")
PLANE_INTUITIVE = frozenset("CFKQUVY")
GROUP_GROUNDED = frozenset("CDGLMV")
GROUP_VACILLATING = frozenset("BFHJNPQSTUWXY")
GROUP_CREATIVE = frozenset("AEIKORZ")


def attitude(day: int, month: int) -> dict:
    """Số Thái Độ = tháng + ngày (rút, giữ master)."""
    raw = reduce_number(month) + reduce_number(day)
    tr = reduce_with_trace(raw)
    return {
        "name_vi": "Số Thái Độ",
        "value": tr["reduced"],
        "raw": raw,
        "steps": tr["steps"],
        "karmic_debt": tr["karmic_debt"],
    }


def balance(name: str, name_order: str = "vn", system: str = "pythagorean") -> dict:
    """Số Cân Bằng = tổng chữ cái đầu mỗi phần tên. Master không áp dụng."""
    split = split_name_parts(name, name_order)
    vals = [letter_value(ch, system) for ch in split["initials"]]
    raw = sum(vals)
    value = reduce_number(raw, keep_master=False)
    return {
        "name_vi": "Số Cân Bằng",
        "value": value,
        "raw": raw,
        "initials": split["initials"],
        "letter_values": vals,
    }


def rational_thought(
    name: str,
    day: int,
    name_order: str = "vn",
    system: str = "pythagorean",
) -> dict:
    """Ngày sinh (rút) + toàn bộ chữ TÊN RIÊNG (first name). Master không áp dụng."""
    split = split_name_parts(name, name_order)
    first = split["first_name"]
    name_sum = sum(letter_value(ch, system) for ch in letters_only(first))
    d = reduce_number(day, keep_master=False)
    raw = d + name_sum
    value = reduce_number(raw, keep_master=False)
    return {
        "name_vi": "Số Tư Duy Lý Trí",
        "value": value,
        "raw": raw,
        "first_name": first,
        "day_reduced": d,
        "name_sum": name_sum,
    }


def karmic_lessons(name: str, system: str = "pythagorean") -> dict:
    """Số 1–9 thiếu trong tên khai sinh."""
    letters = letters_only(name)
    present = {letter_value(ch, system) for ch in letters if letter_value(ch, system)}
    missing = [n for n in range(1, 10) if n not in present]
    return {
        "name_vi": "Bài Học Nghiệp (số thiếu)",
        "values": missing,
        "count": len(missing),
        "present": sorted(present),
    }


def hidden_passion(name: str, system: str = "pythagorean") -> dict:
    """Số xuất hiện nhiều nhất trong tên (có thể nhiều)."""
    letters = letters_only(name)
    counts: Counter[int] = Counter()
    for ch in letters:
        v = letter_value(ch, system)
        if v:
            counts[v] += 1
    if not counts:
        return {"name_vi": "Số Đam Mê Tiềm Ẩn", "values": [], "counts": {}, "max_count": 0}
    max_c = max(counts.values())
    values = sorted(n for n, c in counts.items() if c == max_c)
    return {
        "name_vi": "Số Đam Mê Tiềm Ẩn",
        "values": values,
        "counts": {str(k): v for k, v in sorted(counts.items())},
        "max_count": max_c,
    }


def subconscious_self(lessons_count: int) -> dict:
    """9 − số lượng Karmic Lessons."""
    value = 9 - lessons_count
    return {
        "name_vi": "Số Tự Ngã Tiềm Thức",
        "value": max(0, value),
        "lessons_count": lessons_count,
    }


def cornerstone_capstone(name: str, name_order: str = "vn", system: str = "pythagorean") -> dict:
    from .name_calculator import is_vowel

    split = split_name_parts(name, name_order)
    first = letters_only(split["first_name"])
    corner = first[0] if first else ""
    cap = first[-1] if first else ""
    first_vowel = ""
    for i, ch in enumerate(first):
        if is_vowel(first, i):
            first_vowel = ch
            break
    return {
        "cornerstone": {
            "name_vi": "Cornerstone",
            "letter": corner,
            "value": letter_value(corner, system) if corner else None,
        },
        "capstone": {
            "name_vi": "Capstone",
            "letter": cap,
            "value": letter_value(cap, system) if cap else None,
        },
        "first_vowel": {
            "name_vi": "Nguyên âm đầu (First Vowel)",
            "letter": first_vowel,
            "value": letter_value(first_vowel, system) if first_vowel else None,
        },
        "first_name": split["first_name"],
    }


def bridges(core: dict) -> dict:
    """|LP−Expression|, |Soul−Personality|, |LP−Birthday| — trị tuyệt đối đơn."""

    def _bridge(a: int, b: int, name_vi: str) -> dict:
        # Dùng đơn (rút master) để hiệu 0–8 kiểu Decoz phổ biến
        aa = reduce_number(a, keep_master=False)
        bb = reduce_number(b, keep_master=False)
        return {"name_vi": name_vi, "value": abs(aa - bb), "from": a, "to": b}

    return {
        "life_path_expression": _bridge(
            core["life_path"]["value"],
            core["expression"]["value"],
            "Cầu Đường Đời ↔ Sứ Mệnh",
        ),
        "soul_personality": _bridge(
            core["soul_urge"]["value"],
            core["personality"]["value"],
            "Cầu Linh Hồn ↔ Nhân Cách",
        ),
        "life_path_birthday": _bridge(
            core["life_path"]["value"],
            core["birthday"]["value"],
            "Cầu Đường Đời ↔ Ngày Sinh",
        ),
    }


def planes_of_expression(name: str, system: str = "pythagorean") -> dict:
    """Bốn mặt phẳng + ba nhóm chữ (Decoz)."""
    letters = letters_only(name)
    plane_sums = {"physical": 0, "mental": 0, "emotional": 0, "intuitive": 0}
    group_sums = {"grounded": 0, "vacillating": 0, "creative": 0}
    for ch in letters:
        v = letter_value(ch, system)
        if ch in PLANE_PHYSICAL:
            plane_sums["physical"] += v
        if ch in PLANE_MENTAL:
            plane_sums["mental"] += v
        if ch in PLANE_EMOTIONAL:
            plane_sums["emotional"] += v
        if ch in PLANE_INTUITIVE:
            plane_sums["intuitive"] += v
        if ch in GROUP_GROUNDED:
            group_sums["grounded"] += v
        if ch in GROUP_VACILLATING:
            group_sums["vacillating"] += v
        if ch in GROUP_CREATIVE:
            group_sums["creative"] += v

    planes = {
        k: {
            "name_vi": {
                "physical": "Thể chất",
                "mental": "Trí tuệ",
                "emotional": "Cảm xúc",
                "intuitive": "Trực giác",
            }[k],
            "raw": raw,
            "value": reduce_number(raw),
        }
        for k, raw in plane_sums.items()
    }
    groups = {
        k: {
            "name_vi": {
                "grounded": "Grounded",
                "vacillating": "Vacillating",
                "creative": "Creative",
            }[k],
            "raw": raw,
            "value": reduce_number(raw),
        }
        for k, raw in group_sums.items()
    }
    return {"name_vi": "Mặt Phẳng Biểu Đạt", "planes": planes, "groups": groups}


def compute_extended(
    name: str,
    day: int,
    month: int,
    core: dict,
    system: str = "pythagorean",
    name_order: str = "vn",
    current_name: str | None = None,
) -> dict:
    from .core_numbers import _name_number_per_parts

    lessons = karmic_lessons(name, system)
    letters_meta = cornerstone_capstone(name, name_order, system)
    out: dict = {
        "attitude": attitude(day, month),
        "balance": balance(name, name_order, system),
        "rational_thought": rational_thought(name, day, name_order, system),
        "karmic_lessons": lessons,
        "hidden_passion": hidden_passion(name, system),
        "subconscious_self": subconscious_self(lessons["count"]),
        "cornerstone": letters_meta["cornerstone"],
        "capstone": letters_meta["capstone"],
        "first_vowel": letters_meta["first_vowel"],
        "bridges": bridges(core),
        "planes_of_expression": planes_of_expression(name, system),
    }

    if current_name and current_name.strip():
        out["minor"] = {
            "name_raw": current_name,
            "expression": _name_number_per_parts(
                current_name, system, "all", "Minor Expression", name_order
            ),
            "soul_urge": _name_number_per_parts(
                current_name, system, "vowels", "Minor Soul Urge", name_order
            ),
            "personality": _name_number_per_parts(
                current_name, system, "consonants", "Minor Personality", name_order
            ),
        }
    else:
        out["minor"] = None

    return out
