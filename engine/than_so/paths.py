"""Resolve data/than_so/master — prefer mounted data/, fallback embedded_data/.

VPS mounts /opt/yi-chronos/data → shadow data/. Master dicts are COPY'd into
image as embedded_data/than_so/master/ (Dockerfile). If the volume has a stale
partial tree, fall back to embedded so new JSON (balliett_tone_color, …) load.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_REQUIRED = (
    "pythagorean_spec.json",
    "number_meanings.json",
    "balliett_tone_color.json",
    "cheiro_birth_numbers.json",
    "interpretation_principles.json",
)


@lru_cache(maxsize=1)
def than_so_master_dir() -> Path:
    primary = _ROOT / "data" / "than_so" / "master"
    embedded = _ROOT / "embedded_data" / "than_so" / "master"
    if all((primary / name).is_file() for name in _REQUIRED):
        return primary
    if embedded.is_dir() and all((embedded / name).is_file() for name in _REQUIRED):
        return embedded
    if primary.is_dir():
        return primary
    return embedded
