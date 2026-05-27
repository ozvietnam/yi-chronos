"""Bát Tự Hà Lạc Lý Số — cross-module engine bridging Bát Tự → 2 personal hexagrams.

This is the YI-CHRONOS differentiator (Mục 5.1) — kabala.vn references this technique
in their I Ching primer but does not ship it. We do.

Public API:
    cast_ha_lac(*, birth_datetime_local, timezone='Asia/Ho_Chi_Minh', gender='nam')
"""

from .cast import METHOD_ID, SOURCE_REF, cast_ha_lac
from .luan_giai import compose_ha_lac_luan_giai


__all__ = [
    "METHOD_ID",
    "SOURCE_REF",
    "cast_ha_lac",
    "compose_ha_lac_luan_giai",
]
