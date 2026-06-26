# -*- coding: utf-8 -*-
"""Loader cho ontology nền — xương sống toạ-độ Đông phương học.

Đọc data/yi_lexicon/ontology_nen.json (canonical, deterministic) và cung cấp
API tra cứu + sinh-khắc ngũ hành + resolve alias (vi/zh) → khái niệm chuẩn.

Tái dùng ở mọi môn: Tử Vi, Bát Tự, Kinh Dịch, Mai Hoa, Hà Lạc, Hoàng Cực…
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "data", "yi_lexicon", "ontology_nen.json")
)


@lru_cache(maxsize=4)
def load_ontology(path: str = _DEFAULT_PATH) -> dict:
    """Nạp toàn bộ ontology (cache)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Ngũ hành ──────────────────────────────────────────────
def ngu_hanh_sinh(hanh: str) -> Optional[str]:
    """hanh sinh ra hành nào (Mộc→Hỏa…)."""
    o = load_ontology()
    d = o["ngu_hanh"].get(hanh)
    return d["sinh"] if d else None


def ngu_hanh_khac(hanh: str) -> Optional[str]:
    """hanh khắc hành nào (Mộc→Thổ…)."""
    o = load_ontology()
    d = o["ngu_hanh"].get(hanh)
    return d["khac"] if d else None


def quan_he_ngu_hanh(a: str, b: str) -> str:
    """Quan hệ của a ĐỐI VỚI b: 'sinh' | 'khắc' | 'bị sinh' | 'bị khắc' | 'đồng' | 'không rõ'."""
    o = load_ontology()
    da = o["ngu_hanh"].get(a)
    if not da or b not in o["ngu_hanh"]:
        return "không rõ"
    if a == b:
        return "đồng"
    if da["sinh"] == b:
        return "sinh"
    if da["khac"] == b:
        return "khắc"
    if da["duoc_sinh_boi"] == b:
        return "bị sinh"
    if da["bi_khac_boi"] == b:
        return "bị khắc"
    return "không rõ"


# ── Tra cứu thực thể ──────────────────────────────────────
def thien_can(ten: str) -> Optional[dict]:
    return load_ontology()["thien_can"].get(resolve("thien_can", ten) or ten)


def dia_chi(ten: str) -> Optional[dict]:
    return load_ontology()["dia_chi"].get(resolve("dia_chi", ten) or ten)


def bat_quai(ten: str) -> Optional[dict]:
    return load_ontology()["bat_quai"].get(resolve("bat_quai", ten) or ten)


def que(ten: str) -> Optional[dict]:
    return load_ontology()["que_64"].get(resolve("que_64", ten) or ten)


def que_from_quai(thuong: str, ha: str) -> Optional[dict]:
    """Tra quẻ theo thượng quái + hạ quái (đã resolve alias)."""
    o = load_ontology()
    tq = resolve("bat_quai", thuong) or thuong
    hq = resolve("bat_quai", ha) or ha
    for ten, d in o["que_64"].items():
        if d["thuong_quai"] == tq and d["ha_quai"] == hq:
            return {"ten_vi": ten, **d}
    return None


# ── Alias resolution ──────────────────────────────────────
def resolve(loai: str, ten: str) -> Optional[str]:
    """Chuẩn hoá tên (vi/zh) → canonical_vi trong nhóm `loai`.

    loai ∈ {thien_can, dia_chi, bat_quai, que_64}.
    """
    o = load_ontology()
    table = o.get("alias", {}).get(loai, {})
    return table.get(ten)


def resolve_any(ten: str) -> Optional[tuple]:
    """Dò ten qua MỌI nhóm. Trả (loai, canonical_vi) đầu tiên khớp."""
    o = load_ontology()
    for loai, table in o.get("alias", {}).items():
        if ten in table:
            return (loai, table[ten])
    return None


# ── Nạp giáp (Kinh Dịch ↔ Bát Tự) ─────────────────────────
def nap_giap(quai: str) -> list:
    """Can(s) nạp vào quái."""
    d = bat_quai(quai)
    return d["nap_giap"] if d else []


def quai_tu_can(can: str) -> list:
    """Quái(s) nhận can này (ngược nạp giáp)."""
    o = load_ontology()
    can_c = resolve("thien_can", can) or can
    return [vi for vi, d in o["bat_quai"].items() if can_c in d["nap_giap"]]


if __name__ == "__main__":  # smoke
    o = load_ontology()
    print("loaded:", len(o["thien_can"]), len(o["dia_chi"]),
          len(o["bat_quai"]), len(o["que_64"]))
    print("Mộc sinh", ngu_hanh_sinh("Mộc"), "| Mộc khắc", ngu_hanh_khac("Mộc"))
    print("Giáp đối Mậu:", quan_he_ngu_hanh(thien_can("Giáp")["ngu_hanh"],
                                            thien_can("Mậu")["ngu_hanh"]))
    print("alias 甲 ->", resolve("thien_can", "甲"))
    print("nạp giáp Càn:", nap_giap("乾"))
    print("quẻ Khôn/Càn:", que_from_quai("坤", "乾")["ten_vi"])
