"""Liên Hoa Độn Pháp engine package.

Source: 'Liên Hoa Độn Pháp' (thư viện sách/LIENHOADON.pdf), uploaded by user
as the canonical reference for this school.

This is a SEPARATE school from Mai Hoa Dịch Số. They share Tiên thiên Bát quái
fundamentals but differ in:
- Liên Hoa requires user to provide 2 numbers (rút thăm hương / lá).
- Liên Hoa generates 5, 9, or 13 KHÔNG THỜI SỰ via [+4, +6, +4] gia số chain
  for 1, 2, or 3 đợt độn — Mai Hoa NNTT does not have this chain.
- Liên Hoa tags lục thân for ALL 6 đơn quái in each không thời, with TA reference
  fixed at Tiên đề.

Public API:
    cast_lien_hoa(*, number_right_hand, number_left_hand, question_text="", gender="nam")
"""

from .cast import LienHoaSpread, cast_lien_hoa
from .luan_su import LuanSu, luan_su


__all__ = [
    "LienHoaSpread",
    "LuanSu",
    "cast_lien_hoa",
    "luan_su",
]
