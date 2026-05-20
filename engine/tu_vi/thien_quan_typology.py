"""Tử Vi — Thiên Quán Phân Cung 36 Archetypes Typology.

Theo Q4 p0268-p0271 (Phase A Batch 3-4 thâm nhuần 2026-05-20):
12 giờ × 3 khắc (thượng/trung/hạ tứ khắc) = 36 archetypes.

Input: birth_hour + khac_level → output: archetype profile.
KHÔNG cần lá số đầy đủ — chỉ cần giờ sinh.

Iron Rule #6: "Bất khả chấp nhất" (Q4 p0299 r018) — KHÔNG predict cứng.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data/tu_vi/thien_quan_36_archetypes.json"

KHAC_LEVELS = ["thượng", "trung", "hạ"]
HOUR_BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


@lru_cache(maxsize=1)
def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text())


def get_archetype(hour: str, khac: str) -> dict | None:
    """Get archetype for (hour, khac) pair.

    Args:
        hour: chi giờ sinh ("Tý", "Sửu", ...)
        khac: "thượng" | "trung" | "hạ"

    Returns: archetype dict with cung_name, khac_phu_mau, luc_than, etc.
    """
    if hour not in HOUR_BRANCHES:
        return None
    if khac not in KHAC_LEVELS:
        return None
    data = _load_data()
    for a in data.get("archetypes", []):
        if a.get("hour") == hour and a.get("khac") == khac:
            return {
                **a,
                "iron_rule_note": "Đây là archetype CHUNG theo giờ-khắc, KHÔNG thay thế lá số Tử Vi đầy đủ. Anh có thể không match 100%.",
                "paradigm_note": "Iron Rule #6 (Q4 p0299 r018): 'Bất khả chấp nhất' — 18 sao vận chuyển tùy người biến thông.",
            }
    return None


def list_all_archetypes() -> list[dict]:
    """List all 36 archetypes."""
    return _load_data().get("archetypes", [])


def get_archetypes_by_hour(hour: str) -> list[dict]:
    """Get all 3 archetypes (thượng/trung/hạ) for a specific hour."""
    if hour not in HOUR_BRANCHES:
        return []
    return [a for a in _load_data().get("archetypes", []) if a.get("hour") == hour]


if __name__ == "__main__":
    # Test với anh — giờ Tý (anh sinh 23:30 giờ Tý)
    # 23:00-23:14 = thượng; 23:15-23:44 = trung; 23:45-00:59 = hạ? (heuristic)
    # 23:30 → trung tứ khắc
    print("=== Test founder: giờ Tý trung ===")
    a = get_archetype("Tý", "trung")
    if a:
        print(f"Cung: {a.get('cung_name')}")
        print(f"Khắc phụ mẫu: {a.get('khac_phu_mau')}")
        print(f"Lục thân: {a.get('luc_than')}")
        print(f"Sự nghiệp: {a.get('su_nghiep')}")
        print(f"Summary: {a.get('summary_vi')}")
        print(f"\nIron Rule note: {a.get('iron_rule_note')}")

    print(f"\n=== Total archetypes: {len(list_all_archetypes())} ===")
