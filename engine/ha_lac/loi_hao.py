"""Lookup lời hào Hà Lạc từ seed `data/seeds/hexagram_lines_ha_lac.json`.

Nguồn seed: Xuân Cang — Bát Tự Hà Lạc và Quỹ Đạo Đời Người (p.76+),
64 quẻ × 6 hào = 384 entries khi ĐỦ. Seed hiện phủ MỘT PHẦN (Càn + Khôn);
bơm thêm = phiên đọc sách `data/restored_books/bat-tu-ha-lac-va-quy-dao-doi-nguoi`.

Kỷ luật quote-or-silence: quẻ/hào chưa có trong seed → trả None — engine
tự ghi "chưa có nguồn", KHÔNG bịa lời hào.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SEED_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data" / "seeds" / "hexagram_lines_ha_lac.json"
)


@lru_cache(maxsize=1)
def _load() -> dict:
    """Load + index seed theo (tên quẻ, số hào). Fail → index rỗng."""
    try:
        raw = json.loads(_SEED_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"index": {}, "source": None}
    index: dict[tuple[str, int], dict] = {}
    for rec in raw.get("records", []):
        try:
            index[(rec["quai"], int(rec["hao"]))] = rec
        except (KeyError, TypeError, ValueError):
            continue
    return {"index": index, "source": raw.get("source")}


def get_loi_hao(quai_name: str, hao: int) -> dict | None:
    """Record đầy đủ của 1 hào (loi_kinh, nhl_giang, toan_ha_lac_giai,
    mhc/mkhc, vận-năm theo giới...) kèm `source` đích danh sách gốc,
    hoặc None nếu seed chưa có."""
    data = _load()
    rec = data["index"].get((quai_name, int(hao)))
    if rec is None:
        return None
    return {**rec, "source": rec.get("source") or data["source"]}


def loi_hao_for_stage(quai_name: str, hao: int) -> dict | None:
    """Bản gọn để nhét vào decade-trajectory stage. None nếu chưa có nguồn.

    Giữ đủ 3 giới vận-năm (Quan/Sĩ/Thường + Nữ nếu có) — cast không biết
    giới của user, UI/caller tự chọn hiển thị.
    """
    rec = get_loi_hao(quai_name, hao)
    if rec is None:
        return None
    return {
        "quai": rec["quai"],
        "hao": rec["hao"],
        "loi_kinh": rec.get("loi_kinh"),
        "nhl_giang": rec.get("nhl_giang"),
        "toan_ha_lac_giai": rec.get("toan_ha_lac_giai"),
        "van_nam": {
            "quan": rec.get("van_nam_quan"),
            "si": rec.get("van_nam_si"),
            "thuong": rec.get("van_nam_thuong"),
            "nu": rec.get("van_nam_nu"),
        },
        "source": _load()["source"],
    }


def coverage() -> dict:
    """Stats phủ seed — minh bạch phần còn thiếu (không giả vờ đủ 384)."""
    index = _load()["index"]
    quai_set = {q for q, _ in index}
    return {
        "n_hao": len(index),
        "n_quai": len(quai_set),
        "quai_covered": sorted(quai_set),
        "target": 384,
    }
