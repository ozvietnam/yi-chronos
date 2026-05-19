"""Loader for the 14 chính tinh schema (data/tu_vi/chinh_tinh.json).

Each star has the canonical Tử Vi metadata + interpretation template
(keywords / tich_cuc / tieu_cuc) inspired by kabalavn convention.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data/tu_vi/chinh_tinh.json"


@dataclass(frozen=True)
class ChinhTinh:
    """One Tử Vi chính tinh (principal star)."""

    id: str
    ten_vi: str                    # Vietnamese name
    ten_zh: str                    # Chinese name (1-2 chars)
    ngu_hanh: str                  # Ngũ hành (may include alternatives like "mộc / thủy")
    am_duong: str                  # 'âm' or 'dương'
    hoa_khi: str                   # Tính chất chính (đế / phú / quý / quyền / ...)
    chu_ve: list[str]              # Domains the star governs
    dac_dia: list[str]             # Đắc địa positions (Địa Chi)
    lac_dia: list[str]             # Lạc địa positions (may be empty)
    keywords: list[str]            # 3-5 short keywords
    tich_cuc: str                  # Positive interpretation
    tieu_cuc: str                  # Negative interpretation

    def to_dict(self) -> dict:
        return asdict(self)


def _build_from_raw(raw: dict) -> ChinhTinh:
    """Coerce a JSON entry into a ChinhTinh dataclass with defaults."""
    return ChinhTinh(
        id=raw["id"],
        ten_vi=raw["ten_vi"],
        ten_zh=raw["ten_zh"],
        ngu_hanh=raw["ngu_hanh"],
        am_duong=raw["am_duong"],
        hoa_khi=raw["hoa_khi"],
        chu_ve=list(raw.get("chu_ve", [])),
        dac_dia=list(raw.get("dac_dia", [])),
        lac_dia=list(raw.get("lac_dia", [])),
        keywords=list(raw.get("keywords", [])),
        tich_cuc=raw.get("tich_cuc", ""),
        tieu_cuc=raw.get("tieu_cuc", ""),
    )


@lru_cache(maxsize=1)
def _load_data() -> dict:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Tử Vi chính tinh data not found: {DATA_PATH}")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _load_stars() -> tuple[ChinhTinh, ...]:
    raw = _load_data()
    stars = raw.get("stars", [])
    if len(stars) != 14:
        raise ValueError(f"Expected 14 chính tinh, got {len(stars)} in {DATA_PATH}")
    return tuple(_build_from_raw(s) for s in stars)


ALL_CHINH_TINH: tuple[ChinhTinh, ...] = _load_stars()


def list_chinh_tinh() -> list[ChinhTinh]:
    """Return the 14 chính tinh in canonical order."""
    return list(ALL_CHINH_TINH)


def get_chinh_tinh(star_id: str) -> ChinhTinh:
    """Look up a star by its `id` (slug — e.g. 'tu_vi', 'thai_duong')."""
    for s in ALL_CHINH_TINH:
        if s.id == star_id:
            return s
    raise ValueError(f"Unknown chính tinh id: {star_id!r}")


def get_chinh_tinh_by_name(name_vi: str) -> ChinhTinh:
    """Look up by Vietnamese name (case-sensitive)."""
    for s in ALL_CHINH_TINH:
        if s.ten_vi == name_vi:
            return s
    raise ValueError(f"Unknown chính tinh name_vi: {name_vi!r}")
