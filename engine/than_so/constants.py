"""Hằng số + bảng tra cho Thần Số Học (Numerology).

Single source of truth: nạp bảng chữ cái + ý nghĩa số TỪ data JSON
(`data/than_so/master/*.json`) để engine và tài liệu không lệch nhau.

Paradigm (Iron Rule #4/#6): số = gương cấu trúc tâm-thiên-thân, KHÔNG predict.
Đa phái (Iron Rule #3): Pythagoras (mặc định) + Chaldean (đối chiếu).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

METHOD_ID = "than_so_pythagoras_chaldean_v1"
SOURCE_REF = (
    "Pythagorean numerology (Decoz/Juno Jordan standard) + Chaldean (Cheiro). "
    "Đối chiếu chéo nhiều nguồn — xem docs/design/than-sohoc-pythagoras-tham-nhuan.md"
)

MASTER_NUMBERS = (11, 22, 33)
KARMIC_DEBT_NUMBERS = (13, 14, 16, 19)
PURE_VOWELS = frozenset("AEIOU")

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master"


@lru_cache(maxsize=None)
def _load_json(name: str) -> dict:
    with (_DATA_DIR / name).open(encoding="utf-8") as fh:
        return json.load(fh)


def _build_letter_map(rows: dict[str, list[str]]) -> dict[str, int]:
    """rows = {"1": ["A","J","S"], ...} → {"A": 1, "J": 1, ...}."""
    out: dict[str, int] = {}
    for value_str, letters in rows.items():
        value = int(value_str)
        for letter in letters:
            out[letter.upper()] = value
    return out


@lru_cache(maxsize=None)
def letter_maps() -> dict[str, dict[str, int]]:
    data = _load_json("letter_maps.json")
    return {
        "pythagorean": _build_letter_map(data["pythagorean"]["rows"]),
        "chaldean": _build_letter_map(data["chaldean"]["rows"]),
    }


@lru_cache(maxsize=None)
def number_meanings() -> dict[str, dict]:
    return _load_json("number_meanings.json")["numbers"]


@lru_cache(maxsize=None)
def karmic_meanings() -> dict[str, dict]:
    return _load_json("karmic_debt.json")["karmic_debts"]


SYSTEMS = ("pythagorean", "chaldean")
