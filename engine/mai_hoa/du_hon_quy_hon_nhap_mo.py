"""Du Hồn + Quy Hồn + Nhập Mộ — paradigm Mai Hoa nâng cao (Thiệu Vĩ Hoa).

Paradigm:
- Du Hồn: 8 quẻ — hồn đang DI CHUYỂN, đương sự bôn ba sắp trở về
- Quy Hồn: 8 quẻ — hồn ĐÃ TRỞ VỀ, hoàn thành chu kỳ
- Nhập Mộ: Hào dụng thần nhập quẻ Mộ — sự việc bị ẨN/KẸT/CHẬM

Iron rule: KHÔNG predict cát/hung. Đây là paradigm TRẠNG THÁI tâm thái + sự việc.

Reference: Thiệu Vĩ Hoa — Chu Dịch Dự Đoán Học (Giảng Nghĩa 1993, bổ sung từ bản 1990).
Seed: data/seeds/thieu_vi_hoa_paradigm.json
"""

from __future__ import annotations

import json
from pathlib import Path

_SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seeds" / "thieu_vi_hoa_paradigm.json"
_CACHE: dict | None = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_SEED_PATH, encoding="utf-8") as f:
            _CACHE = json.load(f)
    return _CACHE


def is_du_hon(que_name: str) -> bool:
    """Check quẻ có thuộc 8 quẻ Du Hồn không."""
    return que_name in _load()["du_hon_quy_hon"]["du_hon"]["8_que_du_hon"]


def is_quy_hon(que_name: str) -> bool:
    """Check quẻ có thuộc 8 quẻ Quy Hồn không."""
    return que_name in _load()["du_hon_quy_hon"]["quy_hon"]["8_que_quy_hon"]


def get_du_hon_meaning() -> dict:
    """Ý nghĩa Du Hồn + 5 nguyên tắc đọc."""
    return _load()["du_hon_quy_hon"]["du_hon"]


def get_quy_hon_meaning() -> dict:
    """Ý nghĩa Quy Hồn + 3 nguyên tắc đọc."""
    return _load()["du_hon_quy_hon"]["quy_hon"]


def get_mo_for_ngu_hanh(ngu_hanh: str) -> str | None:
    """Tra tháng Mộ cho ngũ hành (Thủy/Thổ → Thìn, Mộc → Mùi, Hỏa → Tuất, Kim → Sửu)."""
    mapping = _load()["nhap_mo"]["bang_mo"]
    nh = ngu_hanh.lower()
    if nh in ("thủy", "thuy"):
        return mapping["thuy_tho"]
    if nh in ("thổ", "tho"):
        return mapping["thuy_tho"]
    if nh in ("mộc", "moc"):
        return mapping["moc"]
    if nh in ("hỏa", "hoa"):
        return mapping["hoa"]
    if nh in ("kim",):
        return mapping["kim"]
    return None


def build_context_for_que(que_name: str) -> str:
    """Build context cho LLM khi cast Mai Hoa được quẻ que_name."""
    parts = []
    if is_du_hon(que_name):
        info = get_du_hon_meaning()
        parts.append(f"⭐ Quẻ {que_name} thuộc DU HỒN — {info['y_nghia']}")
        parts.append("Nguyên tắc đọc:")
        for r in info["y_nghia_doc"]:
            parts.append(f"  • {r}")
    elif is_quy_hon(que_name):
        info = get_quy_hon_meaning()
        parts.append(f"⭐ Quẻ {que_name} thuộc QUY HỒN — {info['y_nghia']}")
        parts.append("Nguyên tắc đọc:")
        for r in info["y_nghia_doc"]:
            parts.append(f"  • {r}")

    if parts:
        parts.append("\n⚠ Paradigm trạng thái, KHÔNG predict cát/hung.")
        return "\n".join(parts)
    return ""


__all__ = [
    "is_du_hon",
    "is_quy_hon",
    "get_du_hon_meaning",
    "get_quy_hon_meaning",
    "get_mo_for_ngu_hanh",
    "build_context_for_que",
]
