# -*- coding: utf-8 -*-
"""Loader TỪ ĐIỂN thuần-Việt CÓ NEO (PHA B).

Hạ tầng TÁI DÙNG: mọi sản phẩm (gieo duyên, hôn nhân nam/nữ, chân dung...) tra
bản thuần-Việt đã NEO từ canon qua đây — không tự dịch lại (chống drift).

    from engine.yi_lexicon.tu_dien_loader import tra_thuan_viet, load_tu_dien

    e = tra_thuan_viet("Thiên Tướng")
    print(e["thuan_viet"])   # câu đời thường giữ đủ nét canon
    print(e["net_canon"])    # các nét để QA
    print(e["nguon"])        # truy ngược sách

Tra không phân biệt hoa/thường, bỏ khoảng trắng thừa. Trả None nếu không có term.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

_JSON_PATH = Path(__file__).resolve().parent / "tu_dien_thuan_viet.json"


@lru_cache(maxsize=1)
def load_tu_dien() -> dict[str, Any]:
    """Đọc toàn bộ từ điển thuần-Việt (cache 1 lần). Trả full dict {_meta, thong_ke, tu_dien}."""
    if not _JSON_PATH.exists():
        raise FileNotFoundError(
            f"Chưa build {_JSON_PATH.name}. Chạy: python -m engine.yi_lexicon.build_tu_dien_thuan_viet"
        )
    return json.loads(_JSON_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _index() -> dict[str, dict]:
    """Index tra cứu chuẩn-hoá khoá (lower + strip) → entry."""
    tu_dien = load_tu_dien()["tu_dien"]
    idx: dict[str, dict] = {}
    for name, entry in tu_dien.items():
        idx[_norm(name)] = entry
        han = entry.get("han")
        if han:
            idx.setdefault(_norm(han), entry)
    return idx


def _norm(s: str) -> str:
    return " ".join(s.strip().split()).lower()


def tra_thuan_viet(term: str) -> Optional[dict]:
    """Tra 1 term → entry đầy đủ (han, han_viet, loai, dinh_nghia_canon, net_canon,
    thuan_viet, nguon, can_review). Trả None nếu không tìm thấy.

    Khớp theo han_viet HOẶC chữ Hán, không phân biệt hoa/thường.
    """
    if not term:
        return None
    return _index().get(_norm(term))


def thuan_viet_str(term: str, fallback: str | None = None) -> Optional[str]:
    """Tiện ích: lấy thẳng câu thuần_viet (chuỗi) của term, hoặc fallback nếu thiếu."""
    e = tra_thuan_viet(term)
    if e and e.get("thuan_viet"):
        return e["thuan_viet"]
    return fallback


def all_terms() -> list[str]:
    """Danh sách han_viet của mọi term trong từ điển."""
    return list(load_tu_dien()["tu_dien"].keys())
