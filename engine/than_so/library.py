"""Thư viện Thần Số — load dữ liệu từ sách đã restore (Balliett / Campbell / Cheiro)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .core_numbers import _sum_letters_flat, reduce_with_trace
from .name_calculator import normalize_vietnamese

MASTER = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master"


@lru_cache(maxsize=1)
def chaldean_compounds() -> dict:
    return json.loads((MASTER / "chaldean_compound_numbers.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def cheiro_birth_numbers() -> dict:
    return json.loads((MASTER / "cheiro_birth_numbers.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def library_provenance() -> dict:
    return json.loads((MASTER / "library_provenance.json").read_text(encoding="utf-8"))


def resolve_cheiro_birth(digit: int | None) -> dict | None:
    """Tra Birth Day Cheiro 1–9 (Ch.III–XI). Không ghi đè Decoz number_meanings."""
    if digit is None:
        return None
    try:
        d = int(digit)
    except (TypeError, ValueError):
        return None
    while d > 9:
        d = sum(int(x) for x in str(d))
    if d < 1:
        return None
    node = (cheiro_birth_numbers().get("numbers") or {}).get(str(d))
    if not node:
        return None
    conflicts = cheiro_birth_numbers().get("conflict_digits") or []
    return {
        "value": d,
        "planet": node.get("planet"),
        "planet_vi": node.get("planet_vi"),
        "archetype_en": node.get("archetype_en", ""),
        "archetype_vi": node.get("archetype_vi", ""),
        "keywords": node.get("keywords") or [],
        "favorable_days": node.get("favorable_days") or [],
        "colors": node.get("colors") or [],
        "jewels": node.get("jewels") or [],
        "cheiro_vs_decoz": node.get("cheiro_vs_decoz", ""),
        "conflict_with_decoz": d in conflicts,
        "linked_with": node.get("linked_with"),
        "source": "cheiro-book-of-numbers Ch.III–XI",
        "dong_dang": (
            "Cheiro Birth Day = Key vật chất thân thiết — quan-sát khí hành tinh/series; "
            "KHÔNG may/xui. Khi lệch Decoz: present BOTH (Iron Rule #3)."
        ),
    }


def resolve_compound(n: int | None) -> dict | None:
    """Tra số kép Cheiro 10–52; theo alias_of nếu có; gắn paradigm đồng dạng."""
    if n is None:
        return None
    try:
        n = int(n)
    except (TypeError, ValueError):
        return None
    if n < 10:
        return None
    data = chaldean_compounds()
    compounds = data.get("compound_numbers") or {}
    visited: set[int] = set()
    cur = n
    chain: list[int] = []
    while cur not in visited:
        visited.add(cur)
        chain.append(cur)
        node = compounds.get(str(cur))
        if not node:
            if cur > 52:
                # Cheiro: trên 52 ít dùng; rút về digit sum rồi tra lại nếu còn kép
                s = sum(int(d) for d in str(cur))
                if s == cur:
                    return None
                cur = s
                continue
            return None
        alias = node.get("alias_of")
        if alias is None:
            return {
                "value": n,
                "resolved": cur,
                "alias_chain": chain,
                "symbol": node.get("symbol", ""),
                "meaning_vi": node.get("meaning_vi", ""),
                "dong_dang": (
                    "Sắc thái cấu trúc cần quan-sát — KHÔNG phán may/xui cố định "
                    "(Cheiro PD → paradigm YI đồng dạng)."
                ),
                "source": "cheiro-book-of-numbers Ch.XIII (OCR thư viện)",
            }
        cur = int(alias)
    return None


def chaldean_flat_name_compound(name: str) -> dict:
    """Cheiro: cộng tràn tên (Chaldean) → số kép trước rút — khác Decoz per-part."""
    normalized = normalize_vietnamese(name)
    raw = _sum_letters_flat(normalized, "chaldean", "all")
    tr = reduce_with_trace(raw, keep_master=False)  # Chaldean thường không giữ 11/22 như Decoz
    compound = raw if raw >= 10 else None
    # Nếu raw > 52, vẫn giữ raw + resolve qua alias chain / digit
    lookup = resolve_compound(raw) if raw >= 10 else None
    return {
        "name_normalized": normalized,
        "raw": raw,
        "reduced": tr["reduced"],
        "compound": compound,
        "compound_reading": lookup,
        "method": "chaldean_flat_sum",
        "provenance": "cheiro-book-of-numbers",
    }


def campbell_inclusion_meta() -> dict:
    return {
        "name_vi": "Bảng Bao Hàm (Inclusion Table)",
        "provenance": "campbell-your-days-are-numbered",
        "note": (
            "Florence Campbell: đếm tần suất chữ-số 1–9 trong tên. "
            "Số trội → Hidden Passion; số thiếu → Karmic Lessons. "
            "Method facts — không publish nguyên văn Campbell trước 2027."
        ),
    }


def balliett_provenance_note() -> dict:
    return {
        "name_vi": "Balliett — provenance Pythagoras hiện đại",
        "provenance": "balliett-philosophy-of-numbers",
        "deep_read_status": "B1+B2+B3",
        "data_file": "balliett_tone_color.json",
        "journal": "docs/design/than-so-balliett-tham-nhuan-vong-B1.md",
        "note": (
            "Bảng A=1…I=9, nguyên âm = linh hồn, master 11/22: gốc Balliett (~1908, PD). "
            "Tone/color + Life Song keynote + Spiritual Birthday days (B1–B3). "
            "Jordan/Decoz hệ thống hóa sau — thư viện chưa có Jordan/Goodwin."
        ),
    }


@lru_cache(maxsize=1)
def balliett_tone_color() -> dict:
    return json.loads((MASTER / "balliett_tone_color.json").read_text(encoding="utf-8"))


def resolve_balliett_tone(digit: int | None) -> dict | None:
    """Tra màu/âm Balliett cho 1–9, 11, 22. Không rút master. 33 → None."""
    if digit is None:
        return None
    try:
        d = int(digit)
    except (TypeError, ValueError):
        return None
    data = balliett_tone_color()
    numbers = data.get("numbers") or {}
    key = str(d)
    node = numbers.get(key)
    if not node and d not in (11, 22, 33) and d > 9:
        while d > 9:
            d = sum(int(x) for x in str(d))
        key = str(d)
        node = numbers.get(key)
    if not node:
        return None
    out = {
        "value": int(key),
        "colors": node.get("colors") or [],
        "colors_vi": node.get("colors_vi") or [],
        "tones": node.get("tones") or [],
        "archetype_vi": node.get("archetype_vi", ""),
        "keywords_vi": node.get("keywords_vi") or [],
        "ocr_confidence": node.get("ocr_confidence", "medium"),
        "source": "balliett-philosophy-of-numbers",
        "dong_dang": (
            "Balliett: số·màu·âm = ba mặt một rung động để quan-sát khí — "
            "KHÔNG kê đơn màu may / đá quý / bệnh."
        ),
        "forbid": data.get("forbid") or [],
    }
    if node.get("cheiro_color_conflict"):
        out["cheiro_color_conflict"] = node["cheiro_color_conflict"]
        out["present_both"] = True
    if node.get("colors_expresses"):
        out["colors_expresses"] = node["colors_expresses"]
    if node.get("is_master"):
        out["is_master"] = True
        out["reduces_to"] = node.get("reduces_to")
    return out


def balliett_birth_digit(month: int, day: int, year: int) -> dict:
    """Balliett birth vibration: month + day_digit + year_digit (Ch.II Henry Elder).

    Khác Decoz Life Path (cộng mọi chữ số). Khác Cheiro Birth Day (chỉ ngày).
    Ngày 11/22: giữ master ở lớp ngày; Wanamaker OCR liệt kê birth numbers
    [month+year, day] song song với tổng gộp.
    """
    from .core_numbers import reduce_number

    month_d = int(month)
    day_raw = int(day)
    year_d = reduce_number(sum(int(c) for c in str(int(year))), keep_master=False)
    if day_raw in (11, 22):
        day_d = day_raw
        month_year = reduce_number(month_d + year_d, keep_master=True)
        birth_numbers = [month_year, day_d]
    else:
        day_d = reduce_number(day_raw, keep_master=False)
        birth_numbers = None
    raw = month_d + day_d + year_d
    birth = reduce_number(raw, keep_master=True)
    out = {
        "birth_digit": birth,
        "raw": raw,
        "components": {"month": month_d, "day_digit": day_d, "year_digit": year_d},
        "method": "balliett_month_plus_day_digit_plus_year_digit",
        "differs_from": ["decoz_life_path", "cheiro_birth_day_only"],
        "note_vi": (
            "Balliett birth digit = khí bài học hiện tại (màu/âm đi kèm); "
            "không thay Life Path Decoz hay Birth Day Cheiro."
        ),
        "tone": resolve_balliett_tone(birth),
    }
    if birth_numbers:
        out["birth_numbers"] = birth_numbers
        out["wanamaker_mode"] = True
        out["note_vi"] += (
            f" Ngày master {day_d}: OCR cũng liệt kê birth numbers {birth_numbers} "
            "(tháng+năm · ngày) — present BOTH."
        )
    return out


def balliett_spiritual_birthday_days(day: int) -> dict:
    """Spiritual Birthday days (Ch.XVI OCR): ngày trong tháng cùng day-digit với ngày sinh.

    Ví dụ sinh ngày 1 → 1, 10, 19, 28 mỗi tháng. Balliett: ngày luyện / quan-sát
    lực birth — YI KHÔNG gọi là ngày may.
    """
    from .core_numbers import reduce_number

    day_raw = int(day)
    if day_raw in (11, 22):
        day_digit = day_raw
        days = [day_raw]
    else:
        day_digit = reduce_number(day_raw, keep_master=False)
        days = [d for d in range(1, 32) if reduce_number(d, keep_master=False) == day_digit]
    return {
        "day_digit": day_digit,
        "days_in_month": days,
        "method": "same_day_digit_each_month",
        "source": "balliett-philosophy-of-numbers Ch.XVI (Spiritual Birthday)",
        "yi_reframe": (
            "Ngày luyện / quan-sát khí birth — ghi nhật ký cảm-hành; "
            "KHÔNG phải ngày may để quyết định lớn."
        ),
        "example_ocr": "Sinh 1/3/1883 → day digit 1 → Spiritual Birthday 1, 10, 19, 28",
    }


def balliett_life_song(month: int, day: int, year: int, expression_value: int | None = None) -> dict:
    """Life Song / key-note (Ch.XIX) — nguyên lý; chart in-book OCR mất (~L3326).

    Key-note = tone của Balliett birth digit. Name = motif quá khứ (Expression).
    """
    bb = balliett_birth_digit(month, day, year)
    birth = bb["birth_digit"]
    tone = bb.get("tone") or resolve_balliett_tone(birth)
    notes = (tone or {}).get("tones") or []
    colors = (tone or {}).get("colors") or (tone or {}).get("colors_expresses") or []
    ex_tone = resolve_balliett_tone(expression_value) if expression_value is not None else None
    return {
        "birth_digit": birth,
        "keynote": notes[0] if notes else None,
        "keynotes": notes,
        "colors": colors,
        "archetype_vi": (tone or {}).get("archetype_vi", ""),
        "name_motif": {
            "expression": expression_value,
            "tones": (ex_tone or {}).get("tones"),
            "colors": (ex_tone or {}).get("colors"),
        }
        if ex_tone
        else None,
        "chart_status": "missing_ocr",
        "chart_note_vi": (
            "Bảng Life Song đầy đủ trong sách (p.102) mất trong OCR Abbyy — "
            "chỉ giữ nguyên lý key-note; không bịa chart."
        ),
        "practice_vi": (
            "Strike/sing key-note birth (hoặc nghe âm cùng độ) như bài tập mở kênh — "
            "không playlist may mắn."
        ),
        "source": "balliett-philosophy-of-numbers Ch.V + Ch.XIX",
        "spiritual_birthday": balliett_spiritual_birthday_days(day),
        "birth": bb,
    }
