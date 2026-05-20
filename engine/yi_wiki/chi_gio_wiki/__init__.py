"""Chi Giờ Wiki — knowledge base for 12 Earthly Branches (2-hour periods).

Each chi has its own JSON file at `data/<chi_id>.json`. Loader API lazily
reads files on demand and caches in-memory.

Public API:
    list_chi()                     → list of available chi names
    get_chi(name)                  → full entry
    get_bordering(name)            → {previous, next}
    get_thirds(name)               → early/middle/late subdivisions
    get_questions(name, neighbor)  → discrimination question bank
    get_all_chi()                  → dict {name: entry} for all loaded
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"

# Mapping from chi name to data filename (slugified, accent-stripped).
_CHI_FILES = {
    "Tý":   "ty.json",
    "Sửu":  "suu.json",
    "Dần":  "dan.json",
    "Mão":  "mao.json",
    "Thìn": "thin.json",
    "Tỵ":   "ty_serpent.json",   # distinct from Tý (Chuột) — slug ambiguous in Vietnamese
    "Ngọ":  "ngo.json",
    "Mùi":  "mui.json",
    "Thân": "than.json",
    "Dậu":  "dau.json",
    "Tuất": "tuat.json",
    "Hợi":  "hoi.json",
}


@lru_cache(maxsize=12)
def _load(chi_name: str) -> dict:
    """Lazy-load and cache one chi data file."""
    if chi_name not in _CHI_FILES:
        raise KeyError(f"Unknown chi: {chi_name!r}")
    path = _DATA_DIR / _CHI_FILES[chi_name]
    if not path.exists():
        raise FileNotFoundError(f"Data file missing for {chi_name}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_chi() -> list[str]:
    """Return list of chi names whose data file is present (sorted by hour)."""
    return [chi for chi in _CHI_FILES if (_DATA_DIR / _CHI_FILES[chi]).exists()]


def get_chi(name: str) -> dict:
    """Return full wiki entry for chi `name`."""
    return _load(name)


def get_bordering(name: str) -> dict:
    """Return {previous: {chi, leak_traits}, next: {chi, leak_traits}}."""
    return _load(name).get("bordering", {})


def get_thirds(name: str) -> dict:
    """Return {early, middle, late} subdivisions, or empty dict if not defined."""
    return _load(name).get("thirds", {})


def get_questions(name: str, neighbor_key: str) -> list[dict]:
    """Return discrimination questions for `name` vs given neighbor key.

    Args:
        name: chi name (vd "Tý")
        neighbor_key: e.g. "vs_Hoi_early" or "vs_Suu_late"
    """
    return _load(name).get("discrimination_questions", {}).get(neighbor_key, [])


def get_all_chi() -> dict[str, dict]:
    """Return dict of all loaded chi entries (used for UI listing)."""
    return {chi: _load(chi) for chi in list_chi()}
