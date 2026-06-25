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


# Biến thể glyph giản thể (trong từ điển) ↔ phồn thể (canon concept_index gốc).
# Chỉ liệt kê các glyph thật sự xuất hiện ở thập thần Bát Tự / cụm gộp — neo từ
# canonical_zh của concept_index:tu_binh_ba_tu (8391-8400). Mỗi biến thể trỏ về
# CHÍNH entry Bát Tự, không liên quan sao Tử Vi → không phá bẫy đồng-âm.
_HAN_VARIANTS: dict[str, list[str]] = {
    "七杀": ["七殺"],   # Thất Sát (thập thần) — canon 8397 dùng 七殺 phồn thể
    "伤官": ["傷官"],   # Thương Quan — canon 8394
    "正财": ["正財"],   # Chính Tài — canon 8396
    "偏财": ["偏財"],   # Thiên Tài — canon 8395
    "劫财": ["劫財"],   # Kiếp Tài — canon 8392
    "偏官": ["偏官"],   # Thiên Quan (= biệt danh Thất Sát) giữ nguyên
}


def _han_variants(han: str) -> list[str]:
    """Trả các biến thể glyph (giản↔phồn) của 1 chữ Hán, nếu có."""
    return _HAN_VARIANTS.get(han, [])


@lru_cache(maxsize=1)
def _index() -> dict[str, dict]:
    """Index tra cứu chuẩn-hoá khoá (lower + strip) → entry.

    Index theo CẢ han_viet (tên Việt) LẪN chữ Hán. Với thập thần Bát Tự, glyph
    trong từ điển là bản giản thể (七杀, 伤官, 正财, 偏财, 劫财) trong khi canon gốc
    (concept_index:tu_binh_ba_tu, canonical_zh) là bản phồn thể (七殺, 傷官, 正財,
    偏財, 劫財). Để mọi caller tra bằng glyph nào (giản thể từ data nội bộ HOẶC
    phồn thể đúng canon từ wiki) đều khớp đúng entry thập thần — KHÔNG vớ nhầm sao
    Tử Vi cùng tên — ta index thêm biến thể glyph. Mapping chỉ trỏ về CHÍNH entry
    Bát Tự của nó, nên không phá bẫy đồng-âm.
    """
    tu_dien = load_tu_dien()["tu_dien"]
    idx: dict[str, dict] = {}
    for name, entry in tu_dien.items():
        idx[_norm(name)] = entry
        han = entry.get("han")
        if han:
            idx.setdefault(_norm(han), entry)
            for variant in _han_variants(han):
                idx.setdefault(_norm(variant), entry)
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
