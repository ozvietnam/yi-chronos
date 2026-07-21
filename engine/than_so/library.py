"""Thư viện Thần Số — load dữ liệu từ sách đã restore (Balliett / Campbell / Cheiro)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from .core_numbers import _sum_letters_flat, reduce_with_trace
from .name_calculator import normalize_vietnamese

MASTER = Path(__file__).resolve().parents[2] / "data" / "than_so" / "master"


@lru_cache(maxsize=1)
def chaldean_compounds() -> dict:
    return json.loads((MASTER / "chaldean_compound_numbers.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def library_provenance() -> dict:
    return json.loads((MASTER / "library_provenance.json").read_text(encoding="utf-8"))


def resolve_compound(n: int | None) -> dict | None:
    """Tra số kép Cheiro 10–52; theo alias_of nếu có; gắn paradigm đồng dạng."""
    if n is None:
        return None
    try:
        n = int(n)
    except (TypeError, ValueError):
        return None
    if n < 10:
        return None
    data = chaldean_compounds()
    compounds = data.get("compound_numbers") or {}
    visited: set[int] = set()
    cur = n
    chain: list[int] = []
    while cur not in visited:
        visited.add(cur)
        chain.append(cur)
        node = compounds.get(str(cur))
        if not node:
            if cur > 52:
                # Cheiro: trên 52 ít dùng; rút về digit sum rồi tra lại nếu còn kép
                s = sum(int(d) for d in str(cur))
                if s == cur:
                    return None
                cur = s
                continue
            return None
        alias = node.get("alias_of")
        if alias is None:
            return {
                "value": n,
                "resolved": cur,
                "alias_chain": chain,
                "symbol": node.get("symbol", ""),
                "meaning_vi": node.get("meaning_vi", ""),
                "dong_dang": (
                    "Sắc thái cấu trúc cần quan-sát — KHÔNG phán may/xui cố định "
                    "(Cheiro PD → paradigm YI đồng dạng)."
                ),
                "source": "cheiro-book-of-numbers Ch.XIII (OCR thư viện)",
            }
        cur = int(alias)
    return None


def chaldean_flat_name_compound(name: str) -> dict:
    """Cheiro: cộng tràn tên (Chaldean) → số kép trước rút — khác Decoz per-part."""
    normalized = normalize_vietnamese(name)
    raw = _sum_letters_flat(normalized, "chaldean", "all")
    tr = reduce_with_trace(raw, keep_master=False)  # Chaldean thường không giữ 11/22 như Decoz
    compound = raw if raw >= 10 else None
    # Nếu raw > 52, vẫn giữ raw + resolve qua alias chain / digit
    lookup = resolve_compound(raw) if raw >= 10 else None
    return {
        "name_normalized": normalized,
        "raw": raw,
        "reduced": tr["reduced"],
        "compound": compound,
        "compound_reading": lookup,
        "method": "chaldean_flat_sum",
        "provenance": "cheiro-book-of-numbers",
    }


def campbell_inclusion_meta() -> dict:
    return {
        "name_vi": "Bảng Bao Hàm (Inclusion Table)",
        "provenance": "campbell-your-days-are-numbered",
        "note": (
            "Florence Campbell: đếm tần suất chữ-số 1–9 trong tên. "
            "Số trội → Hidden Passion; số thiếu → Karmic Lessons. "
            "Method facts — không publish nguyên văn Campbell trước 2027."
        ),
    }


def balliett_provenance_note() -> dict:
    return {
        "name_vi": "Balliett — provenance Pythagoras hiện đại",
        "provenance": "balliett-philosophy-of-numbers",
        "note": (
            "Bảng A=1…I=9, nguyên âm = linh hồn, master 11/22: gốc Balliett (~1908, PD). "
            "Jordan/Decoz hệ thống hóa sau — thư viện chưa có Jordan/Goodwin."
        ),
    }
