"""Tách Họ / Đệm / Tên theo name_order (vn | western) — Decoz first/middle/last."""
from __future__ import annotations

from .name_calculator import normalize_vietnamese


def split_name_parts(name: str, name_order: str = "vn") -> dict:
    """Trả {parts, first_name, middle_name, last_name, initials, name_order}.

    - vn (mặc định): tokens = [Họ, …Đệm, Tên]
      Decoz first_name = Tên (token cuối); last_name = Họ (token đầu).
    - western: First … Middle Last theo tiếng Anh.
    """
    normalized = normalize_vietnamese(name)
    parts = [p for p in normalized.split() if p]
    if not parts:
        return {
            "parts": [],
            "first_name": "",
            "middle_name": "",
            "last_name": "",
            "initials": [],
            "name_order": name_order,
            "normalized": normalized,
        }

    order = (name_order or "vn").lower().strip()
    if order not in ("vn", "western"):
        order = "vn"

    if order == "western":
        first_name = parts[0]
        last_name = parts[-1] if len(parts) > 1 else ""
        middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
    else:
        # VN: Họ … Đệm Tên
        last_name = parts[0]  # Họ → Decoz last / Spiritual
        first_name = parts[-1]  # Tên → Decoz first / Physical
        middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) == 2 else "")
        if len(parts) == 1:
            first_name = parts[0]
            last_name = ""
            middle_name = ""
        elif len(parts) == 2:
            # Họ Tên — không đệm
            last_name = parts[0]
            first_name = parts[1]
            middle_name = ""

    initials = [p[0] for p in parts if p]
    return {
        "parts": parts,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "initials": initials,
        "name_order": order,
        "normalized": normalized,
    }
