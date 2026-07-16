"""Orchestrator — cast_than_so(name, birth_date) → lá số Thần Số Học đầy đủ.

Đa phái (Iron Rule #3): mặc định Pythagoras, kèm Chaldean để đối chiếu.
"""
from __future__ import annotations

from datetime import date

from .constants import METHOD_ID, SOURCE_REF
from .core_numbers import compute_core
from .cross_bind import cross_bind_dong_phuong
from .cycles import period_cycles, personal_year, pinnacles_and_challenges
from .interpretation import compose_reading
from .name_calculator import normalize_vietnamese


def _parse_date(birth_date: str) -> date:
    try:
        return date.fromisoformat(birth_date.strip())
    except ValueError as exc:
        raise ValueError(f"birth_date phải dạng YYYY-MM-DD, nhận '{birth_date}'") from exc


def cast_than_so(
    name: str,
    birth_date: str,
    system: str = "pythagorean",
    include_chaldean: bool = True,
    include_dong_phuong: bool = True,
    target_year: int | None = None,
) -> dict:
    """name: họ tên đầy đủ (có dấu được — sẽ tự chuẩn hóa).
    birth_date: 'YYYY-MM-DD'. system: phái chính. include_chaldean: kèm đối chiếu.
    """
    if not name or not name.strip():
        raise ValueError("name không được rỗng")
    d = _parse_date(birth_date)
    normalized = normalize_vietnamese(name)

    core = compute_core(name, d.day, d.month, d.year, system=system)
    cycles = {
        **pinnacles_and_challenges(d.day, d.month, d.year),
        "period_cycles": period_cycles(d.day, d.month, d.year),
    }
    if target_year is not None:
        cycles["personal_year"] = personal_year(d.day, d.month, target_year)

    result: dict = {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "schema_version": "v1",
        "input": {
            "name_raw": name,
            "name_normalized": normalized,
            "birth_date": d.isoformat(),
            "system": system,
        },
        "core": core,
        "cycles": cycles,
        "reading": compose_reading(core, cycles),
    }

    if include_chaldean and system != "chaldean":
        # Đối chiếu chéo — chỉ các số TÊN khác nhau giữa 2 phái (số ngày sinh giống nhau).
        chaldean_core = compute_core(name, d.day, d.month, d.year, system="chaldean")
        # Số KÉP Cheiro (mặt huyền/tinh thần) theo tổng CHƯA rút gọn — nối
        # master chaldean_compound_numbers.json (2026-07-16). Ngoài bảng → bỏ key.
        from .chaldean_compound import compound_info
        _compounds = {
            k: compound_info(chaldean_core[k]["raw"])
            for k in ("expression", "soul_urge", "personality")
        }
        result["cross_reference"] = {
            "system": "chaldean",
            "note": "Đối chiếu Chaldean (Iron Rule #3 — đa phái). Số từ ngày sinh giống nhau; chỉ số TÊN khác.",
            "expression": chaldean_core["expression"]["value"],
            "soul_urge": chaldean_core["soul_urge"]["value"],
            "personality": chaldean_core["personality"]["value"],
            "compound_numbers": {k: v for k, v in _compounds.items() if v},
        }

    if include_dong_phuong:
        # Đối chiếu Đông phương (Iron Rule #3) cho Số Đường Đời + Số Sứ Mệnh.
        result["dong_phuong_doi_chieu"] = {
            "life_path": cross_bind_dong_phuong(core["life_path"]["value"]),
            "expression": cross_bind_dong_phuong(core["expression"]["value"]),
        }
    return result
