"""Lục thân computation — tag each đơn quái relative to a TA reference.

Lục thân = 6 thân relationships between an đơn quái's element and TA's element:
    H (Huynh Đệ)  — đồng hành (same element)
    P (Phụ Mẫu)   — sanh TA  (element generates TA's element)
    C (Tử Tôn)    — TA sanh  (TA's element generates this element)
    Q (Quan Quỷ)  — khắc TA  (element controls TA's element)
    T (Thê Tài)   — TA khắc  (TA's element controls this element)
"""

from __future__ import annotations

from .constants import (
    ELEMENT_CONTROLS,
    ELEMENT_GENERATES,
    LUC_THAN_NAMES,
    TRIGRAM_ELEMENT,
)


def luc_than_of_element(ta_element: str, target_element: str) -> str:
    """Return single-letter lục thân key (H/P/C/Q/T)."""
    if ta_element == target_element:
        return "H"
    if ELEMENT_GENERATES.get(target_element) == ta_element:
        return "P"   # target sanh TA → target là Phụ Mẫu
    if ELEMENT_GENERATES.get(ta_element) == target_element:
        return "C"   # TA sanh target → target là Tử Tôn
    if ELEMENT_CONTROLS.get(target_element) == ta_element:
        return "Q"   # target khắc TA → target là Quan Quỷ
    if ELEMENT_CONTROLS.get(ta_element) == target_element:
        return "T"   # TA khắc target → target là Thê Tài
    raise ValueError(f"no relation between {ta_element} and {target_element}")


def luc_than_of_trigram(ta_element: str, trigram: str) -> str:
    return luc_than_of_element(ta_element, TRIGRAM_ELEMENT[trigram])


def luc_than_name(key: str) -> str:
    return LUC_THAN_NAMES[key]
