"""Số KÉP Chaldean (Cheiro's Book of Numbers 1926, public domain).

Nạp từ `data/than_so/master/chaldean_compound_numbers.json` — nối 2026-07-16
(audit "hút mà chưa nối": bảng đã curate 2026-06-05 nhưng engine không đọc).

Paradigm Cheiro: số đơn 1-9 = mặt VẬT CHẤT; số kép (raw ≥ 10) = mặt
HUYỀN/TINH THẦN. `cross_reference` Chaldean trong cast trước đây chỉ trả số
trần — mất toàn bộ tầng nghĩa số kép.
"""

from __future__ import annotations

from functools import lru_cache

from .constants import _load_json


@lru_cache(maxsize=1)
def _data() -> dict:
    try:
        return _load_json("chaldean_compound_numbers.json")
    except Exception:
        return {}


def compound_info(raw: int) -> dict | None:
    """Ý nghĩa số kép cho tổng chưa rút gọn `raw`. None nếu ngoài bảng (không bịa).

    Kèm hành tinh của số đơn tương ứng (single_numbers_planet) nếu raw 1-9.
    """
    d = _data()
    if not d:
        return None
    rec = d.get("compound_numbers", {}).get(str(raw))
    if rec is not None:
        return {"compound": raw, **rec, "source": d.get("source")}
    single = d.get("single_numbers_planet", {}).get(str(raw))
    if single is not None:
        return {"compound": raw, **single, "source": d.get("source")}
    return None
