"""Thần Số Học (Numerology) engine — tính mệnh từ TÊN + NGÀY SINH.

Phái: Pythagoras (mặc định) + Chaldean (đối chiếu, Iron Rule #3).
Paradigm: đọc đồng dạng, KHÔNG predict (Iron Rule #4/#6).
Journal: docs/design/than-sohoc-pythagoras-tham-nhuan.md
"""
from __future__ import annotations

from .constants import KARMIC_DEBT_NUMBERS, MASTER_NUMBERS, METHOD_ID, SOURCE_REF, SYSTEMS
from .cast import cast_than_so
from .core_numbers import compute_core, life_path, reduce_number
from .cross_bind import cross_bind_dong_phuong
from .cycles import period_cycles, personal_year, pinnacles_and_challenges
from .interpretation import compose_reading, describe_number
from .name_calculator import name_breakdown, normalize_vietnamese

__all__ = [
    "KARMIC_DEBT_NUMBERS",
    "MASTER_NUMBERS",
    "METHOD_ID",
    "SOURCE_REF",
    "SYSTEMS",
    "cast_than_so",
    "compose_reading",
    "compute_core",
    "cross_bind_dong_phuong",
    "describe_number",
    "life_path",
    "name_breakdown",
    "normalize_vietnamese",
    "period_cycles",
    "personal_year",
    "pinnacles_and_challenges",
    "reduce_number",
]
