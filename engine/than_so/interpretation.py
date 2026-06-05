"""Soạn luận giải — paradigm ĐỌC ĐỒNG DẠNG, KHÔNG predict.

Lấy ý nghĩa từ number_meanings.json + karmic_debt.json. Tone: quan-số-trace-tính.
"""
from __future__ import annotations

from .constants import karmic_meanings, number_meanings


def _meaning(value: int) -> dict | None:
    return number_meanings().get(str(value))


def describe_number(value: int) -> dict:
    m = _meaning(value)
    if not m:
        return {"value": value, "archetype_vi": f"Số {value}", "note": "Chưa có dữ liệu."}
    return {
        "value": value,
        "archetype_vi": m.get("archetype_vi", ""),
        "keywords": m.get("keywords", []),
        "strengths": m.get("strengths", ""),
        "shadow": m.get("shadow", ""),
        "dong_dang": m.get("dong_dang", ""),
        "is_master": m.get("is_master", False),
    }


def interpret_core(core: dict) -> dict:
    """Diễn giải 6 số cốt lõi theo tone đồng dạng."""
    out: dict[str, dict] = {}
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        node = core[key]
        out[key] = {
            "name_vi": node["name_vi"],
            **describe_number(node["value"]),
        }
    return out


def collect_karmic(core: dict) -> list[dict]:
    debts: list[dict] = []
    seen: set[int] = set()
    km = karmic_meanings()
    for key in ("life_path", "expression", "soul_urge", "personality"):
        kd = core[key].get("karmic_debt")
        if kd and kd not in seen:
            seen.add(kd)
            info = km.get(str(kd), {})
            debts.append(
                {
                    "number": kd,
                    "source": core[key]["name_vi"],
                    "theme_vi": info.get("theme_vi", ""),
                    "this_life": info.get("this_life", ""),
                    "dong_dang": info.get("dong_dang", ""),
                }
            )
    return debts


PARADIGM_NOTE = (
    "Thần Số Học ở đây là MÔN ĐỌC ĐỒNG DẠNG (Pythagoras: 'Vạn vật là số'), "
    "KHÔNG phải bói tốt/xấu. Số phản chiếu cấu trúc tâm-thiên-thân của Anh — "
    "câu hỏi đúng là 'cấu trúc này mời Anh quan-sát điều gì', không phải 'tương lai sẽ ra sao'."
)


def compose_reading(core: dict, cycles: dict | None = None) -> dict:
    reading = {
        "paradigm_note": PARADIGM_NOTE,
        "core": interpret_core(core),
        "karmic_debts": collect_karmic(core),
    }
    if cycles:
        reading["cycles_hint"] = (
            "Các chu kỳ (Đỉnh Vận / Thử Thách / Năm Cá Nhân) là lớp BIẾN — "
            "đọc 'khí của giai đoạn', tương ứng Đại Vận/Lưu Niên, không predict được-mất."
        )
    return reading
