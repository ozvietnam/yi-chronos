"""Tử Vi engine package — currently provides 14 chính tinh schema + loader.

Mục 2.1: foundation for the rich Tử Vi panel.
Future scope: an-sao algorithm (cung Mệnh + 14 stars + phụ tinh + sát tinh)
to be built on top of this schema.
"""

from .an_sao import METHOD_ID, SOURCE_REF, cast_la_so
from .chinh_tinh import (
    ALL_CHINH_TINH,
    ChinhTinh,
    get_chinh_tinh,
    list_chinh_tinh,
)
from .interpretation import interpret_la_so, interpret_palace
from .luu_tru import dai_han_intra_cung_per_year, luu_tru_for_year, year_to_ganzhi


__all__ = [
    "ALL_CHINH_TINH",
    "METHOD_ID",
    "SOURCE_REF",
    "ChinhTinh",
    "cast_la_so",
    "dai_han_intra_cung_per_year",
    "get_chinh_tinh",
    "interpret_la_so",
    "interpret_palace",
    "list_chinh_tinh",
    "luu_tru_for_year",
    "year_to_ganzhi",
]
