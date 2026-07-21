"""Thần Số Học (Numerology) engine — Pythagoras (Decoz) là pipeline chính.

Spec: data/than_so/master/pythagorean_spec.json
Journal: docs/design/than-sohoc-pythagoras-tham-nhuan.md
"""
from __future__ import annotations

from .constants import KARMIC_DEBT_NUMBERS, MASTER_NUMBERS, METHOD_ID, SOURCE_REF, SYSTEMS
from .cast import cast_than_so
from .core_numbers import compute_core, life_path, reduce_number
from .cross_bind import cross_bind_dong_phuong
from .cycles import (
    build_cycles,
    period_cycles,
    personal_day,
    personal_month,
    personal_year,
    pinnacles_and_challenges,
)
from .extended import compute_extended
from .interpretation import compose_reading, describe_number
from .name_calculator import name_breakdown, normalize_vietnamese

__all__ = [
    "KARMIC_DEBT_NUMBERS",
    "MASTER_NUMBERS",
    "METHOD_ID",
    "SOURCE_REF",
    "SYSTEMS",
    "build_cycles",
    "cast_than_so",
    "compose_reading",
    "compute_core",
    "compute_extended",
    "cross_bind_dong_phuong",
    "describe_number",
    "life_path",
    "name_breakdown",
    "normalize_vietnamese",
    "period_cycles",
    "personal_day",
    "personal_month",
    "personal_year",
    "pinnacles_and_challenges",
    "reduce_number",
]
