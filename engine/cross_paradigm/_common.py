"""Primitive dùng chung cho mọi orchestrator liên-phái (cross-paradigm).

Đồng-tham/dị-tham (Iron #3 kept_all) + paradigm guard (Iron #4/#6/#8). Dùng bởi
hon_nhan_song_phai (#55), couple_sync (#56), và các module liên-phái sau.
"""
from __future__ import annotations

import unicodedata
from typing import Optional

from engine.hermes_guard import paradigm_violations

CONCORD_DONG = "đồng_tham"   # 2 phái cùng hướng → tin cao
CONCORD_DI = "dị_tham"       # lệch hướng → giữ CẢ HAI, thận trọng (KHÔNG chọn phái)
CONCORD_MOT = "một_phía"     # chỉ 1 phái có tín hiệu


def norm(s: str) -> str:
    """Bỏ dấu + lower (match bền)."""
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower().replace("đ", "d")


def concord(lead_dir: Optional[str], cross_dir: Optional[str]) -> str:
    """Đồng-tham nếu cùng hướng; dị-tham nếu lệch; một-phía nếu thiếu 1 phía."""
    if lead_dir is None or cross_dir is None:
        return CONCORD_MOT
    return CONCORD_DONG if lead_dir == cross_dir else CONCORD_DI


def reframe_check(text: str) -> tuple[bool, list[str]]:
    """(paradigm_ok, flags). ok=False nếu dính giọng tiên tri (predict)."""
    flags = paradigm_violations(text or "")
    return (not flags), flags
