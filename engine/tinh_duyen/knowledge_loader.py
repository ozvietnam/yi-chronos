"""Knowledge loader cho module tinh_duyen.

Load 6 file JSON tri thức trong engine/tinh_duyen/knowledge/ với cache
(functools.lru_cache) — chỉ đọc đĩa 1 lần / process.

Helper name->key (tiếng Việt có dấu -> snake key) để tra cứu các dict
dùng snake_case làm khoá (vd 'Tử Vi' -> 'tu_vi', 'Phá Quân' -> 'pha_quan').
"""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"

# Tên file -> khoá logic dùng trong code.
_FILES = {
    "tuvi_phuthe": "tuvi_phuthe.json",
    "batu_hon_nhan": "batu_hon_nhan.json",
    "reconcile": "tuvi_batu_reconcile.json",
    "personality": "personality_comm_style.json",
    "cach_cuc": "cach_cuc_tinh_duyen.json",
    "life_stages": "life_stages.json",
    "cham_cap_do": "cham_cap_do.json",
}


@lru_cache(maxsize=None)
def _load_one(filename: str) -> dict:
    path = _KNOWLEDGE_DIR / filename
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def load_knowledge() -> dict:
    """Trả dict {logical_key: parsed_json} cho cả 6 file tri thức (cached)."""
    return {key: _load_one(fname) for key, fname in _FILES.items()}


def get(logical_key: str) -> dict:
    """Lấy 1 khối tri thức theo khoá logic (tuvi_phuthe, batu_hon_nhan, ...)."""
    return load_knowledge()[logical_key]


def name_to_key(name: str) -> str:
    """Chuẩn hoá tên tiếng Việt có dấu -> snake key không dấu.

    'Tử Vi'      -> 'tu_vi'
    'Phá Quân'   -> 'pha_quan'
    'Thiên Tướng'-> 'thien_tuong'
    """
    if not name:
        return ""
    # Bỏ dấu thanh + dấu mũ/móc (NFD rồi strip combining marks).
    decomposed = unicodedata.normalize("NFD", name)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    # đ/Đ không tách được bằng NFD -> xử riêng.
    stripped = stripped.replace("Đ", "D").replace("đ", "d")
    stripped = stripped.lower().strip()
    return "_".join(part for part in stripped.split() if part)


__all__ = ["load_knowledge", "get", "name_to_key"]
