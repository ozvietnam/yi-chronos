"""Một fact nhiều tên gọi — resolver biệt danh sao qua wiki (Anh chốt 2026-06-11).

> "đế tinh với tử vi thì dùng wiki mà lọc, một fact nhiều tên gọi thôi.
>  khi tìm thì tìm song song cho ra hết kết quả." — Anh

Nguồn sự thật: wiki concept_index.aliases (đã seed từ data/tu_vi/star_aliases.json).
Dùng ở 2 chỗ:
1. Tagging (tag_fix / atomize): detect sao qua MỌI tên gọi
2. Search FTS: expand query — tìm "Đế tinh" cũng ra kết quả "Tử Vi" và ngược lại
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "yi_wiki" / "wiki.sqlite3"
# Volume mount shadows data/ trong container → fallback embedded_data/
_SEED_CANDIDATES = [
    PROJECT_ROOT / "data" / "tu_vi" / "star_aliases.json",
    PROJECT_ROOT / "embedded_data" / "tu_vi" / "star_aliases.json",
]
SEED_PATH = next((p for p in _SEED_CANDIDATES if p.exists()), _SEED_CANDIDATES[0])

# Tên chuẩn tiếng Việt → canonical (để map alias wiki → canonical)
_VI_TO_CANON = {
    "Tử Vi": "tu_vi", "Thiên Cơ": "thien_co", "Thái Dương": "thai_duong",
    "Vũ Khúc": "vu_khuc", "Thiên Đồng": "thien_dong", "Liêm Trinh": "liem_trinh",
    "Thiên Phủ": "thien_phu", "Thái Âm": "thai_am", "Tham Lang": "tham_lang",
    "Cự Môn": "cu_mon", "Thiên Tướng": "thien_tuong", "Thiên Lương": "thien_luong",
    "Thất Sát": "that_sat", "Phá Quân": "pha_quan",
    "Văn Xương": "van_xuong", "Văn Khúc": "van_khuc",
    "Tả Phụ": "ta_phu", "Hữu Bật": "huu_bat",
    "Thiên Khôi": "thien_khoi", "Thiên Việt": "thien_viet",
    "Kình Dương": "kinh_duong", "Đà La": "da_la",
    "Hỏa Tinh": "hoa_tinh", "Linh Tinh": "linh_tinh",
    "Địa Không": "dia_khong", "Địa Kiếp": "dia_kiep",
    "Lộc Tồn": "loc_ton", "Thiên Mã": "thien_ma",
}

_CACHE: dict[str, list[str]] | None = None


def alias_to_stars() -> dict[str, list[str]]:
    """Bảng alias → list sao canonical. Wiki trước, seed JSON bù.

    Trả dict {tên gọi: [canonical...]} — gồm CẢ tên chuẩn lẫn biệt danh.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    table: dict[str, list[str]] = {}
    # Tên chuẩn
    for vi, canon in _VI_TO_CANON.items():
        table[vi] = [canon]

    # Seed JSON (evidence-based từ atoms)
    try:
        seed = json.loads(SEED_PATH.read_text())
        for alias, stars in seed.get("aliases", {}).items():
            table[alias] = stars
    except Exception:
        pass

    # Wiki concept_index.aliases — nguồn sự thật, ghi đè/bổ sung
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT canonical_vi, aliases FROM concept_index "
            "WHERE aliases IS NOT NULL AND aliases != '' AND aliases != '[]'"
        ).fetchall()
        conn.close()
        for canonical_vi, aliases_json in rows:
            canon = _VI_TO_CANON.get(canonical_vi)
            if not canon:
                continue
            try:
                for alias in json.loads(aliases_json):
                    table.setdefault(alias, [])
                    if canon not in table[alias]:
                        table[alias].append(canon)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    _CACHE = table
    return table


_PALACE_CACHE: dict[str, list[str]] | None = None


def palace_alias_patterns() -> dict[str, list[str]]:
    """Bảng cung canonical → list pattern cụm viết tắt (case-sensitive)."""
    global _PALACE_CACHE
    if _PALACE_CACHE is not None:
        return _PALACE_CACHE
    table: dict[str, list[str]] = {}
    try:
        seed = json.loads(SEED_PATH.read_text())
        for canon, pats in seed.get("palace_aliases", {}).items():
            if canon.startswith("_"):
                continue
            table[canon] = pats
    except Exception:
        pass
    _PALACE_CACHE = table
    return table


def detect_palaces(text: str) -> list[str]:
    """Detect cung qua cụm viết tắt ('ở Tài', 'cung Phúc'...) — case-sensitive."""
    found: list[str] = []
    for canon, pats in palace_alias_patterns().items():
        if any(p in text for p in pats) and canon not in found:
            found.append(canon)
    return found


def detect_stars(text: str) -> list[str]:
    """Detect MỌI sao trong text qua mọi tên gọi (tìm song song)."""
    found: list[str] = []
    for alias, stars in alias_to_stars().items():
        if alias in text:
            for s in stars:
                if s not in found:
                    found.append(s)
    return found


def expand_search_terms(query: str) -> list[str]:
    """Expand query search: 'Đế tinh' → ['Đế tinh', 'Tử Vi', 'Đế tọa', ...].

    Trả list term để search song song (OR) — ra hết kết quả mọi tên gọi.
    """
    table = alias_to_stars()
    terms = [query]
    # Query khớp alias nào → thêm mọi tên gọi khác của cùng (bộ) sao đó
    q_stars: set[str] = set()
    for alias, stars in table.items():
        if alias.lower() in query.lower():
            q_stars.update(stars)
    if q_stars:
        for alias, stars in table.items():
            if set(stars) & q_stars and alias not in terms:
                terms.append(alias)
    return terms
