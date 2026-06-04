"""Tam Nguyên Cửu Vận — paradigm thời đại 180 năm (Thiệu Vĩ Hoa).

Paradigm:
- 180 năm chia thành 3 nguyên (Thượng / Trung / Hạ) × 9 cung × 20 năm
- Hiện tại 2024-2043 = Cung LY (Hạ Nguyên) — sáng tỏ, biểu hiện, AI tỏa sáng

Iron rule: KHÔNG predict cát/hung. Đây là paradigm THỜI ĐẠI để hiểu xu thế.

Reference: Thiệu Vĩ Hoa — Chu Dịch Dự Đoán Học, Lời tựa.
Seed: data/seeds/thieu_vi_hoa_paradigm.json
"""

from __future__ import annotations

import json
from pathlib import Path

_SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "thieu_vi_hoa_paradigm.json"
_CACHE: dict | None = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_SEED_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def get_cung_van_for_year(year: int) -> dict | None:
    """Lấy cung vận cho 1 năm cụ thể (vd: 2026 → Cung Ly)."""
    data = _load()["tam_nguyen_cuu_van"]
    all_cycles = data["thuong_nguyen"] + data["trung_nguyen"] + data["ha_nguyen"]
    for cycle in all_cycles:
        if cycle["tu_nam"] <= year <= cycle["den_nam"]:
            return cycle
    return None


def get_current_cung_van() -> dict:
    """Cung vận hiện tại + lời cho user."""
    data = _load()["tam_nguyen_cuu_van"]
    return data["hien_tai_2026"]


def get_full_cycle() -> list[dict]:
    """Toàn bộ 9 cung × 20 năm của vòng Thượng/Trung/Hạ Nguyên hiện tại."""
    data = _load()["tam_nguyen_cuu_van"]
    return data["thuong_nguyen"] + data["trung_nguyen"] + data["ha_nguyen"]


def build_context(year: int = 2026) -> str:
    """Build context cho LLM phê mệnh sâu — cite cung vận hiện tại."""
    cycle = get_cung_van_for_year(year)
    if not cycle:
        return ""

    parts = []
    parts.append("=== TAM NGUYÊN CỬU VẬN (Thiệu Vĩ Hoa) ===")
    parts.append(f"\nNăm {year} = Cung **{cycle['cung']}** ({cycle['tu_nam']}-{cycle['den_nam']}) — Nguyên {cycle['nguyen']}")
    parts.append(f"Tính chất: {cycle['tinh_chat']}")

    current = get_current_cung_van()
    if year >= 2024:
        parts.append(f"\nGhi chú thời đại: {current['ghi_chu']}")

    parts.append("\n⚠ Paradigm thời đại, KHÔNG predict cát/hung cá nhân.")
    return "\n".join(parts)


__all__ = ["get_cung_van_for_year", "get_current_cung_van", "get_full_cycle", "build_context"]
