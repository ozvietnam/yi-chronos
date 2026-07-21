"""Orchestrator — cast_than_so → lá số Pythagoras đầy đủ (Decoz P0).

Chaldean chỉ còn đối chiếu chéo tên (không trộn vào pipeline chính).
"""
from __future__ import annotations

from datetime import date

from .constants import METHOD_ID, SOURCE_REF
from .core_numbers import compute_core
from .cycles import build_cycles
from .deep_reading import compose_deep_reading
from .extended import compute_extended
from .interpretation import compose_reading
from .method_audit import method_audit
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
    include_dong_phuong: bool = False,
    target_year: int | None = None,
    target_month: int | None = None,
    target_day: int | None = None,
    current_name: str | None = None,
    name_order: str = "vn",
    as_of: str | None = None,
) -> dict:
    """Lập lá số Pythagoras (Decoz).

    name: họ tên khai sinh đầy đủ.
    current_name: tên đang dùng (Minor numbers) — optional.
    name_order: 'vn' (Họ…Tên) | 'western' (First…Last).
    include_dong_phuong: mặc định TẮT — module tập trung Pythagoras.
    """
    if not name or not name.strip():
        raise ValueError("name không được rỗng")
    d = _parse_date(birth_date)
    normalized = normalize_vietnamese(name)
    as_of_date = _parse_date(as_of) if as_of else date.today()

    # Pipeline chính luôn Pythagorean cho inventory đầy đủ; `system` chỉ đổi bảng chữ
    # khi user chọn chaldean làm hệ chính (tên). Life path vẫn Pythagoras/Decoz.
    core_system = system if system in ("pythagorean", "chaldean") else "pythagorean"
    core = compute_core(name, d.day, d.month, d.year, system=core_system, name_order=name_order)
    extended = compute_extended(
        name,
        d.day,
        d.month,
        core,
        system=core_system,
        name_order=name_order,
        current_name=current_name,
    )
    cycles = build_cycles(
        d.day,
        d.month,
        d.year,
        name,
        name_order=name_order,
        target_year=target_year,
        target_month=target_month,
        target_day=target_day,
        as_of=as_of_date,
    )

    result: dict = {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "schema_version": "v2",
        "spec": "data/than_so/master/pythagorean_spec.json",
        "input": {
            "name_raw": name,
            "name_normalized": normalized,
            "current_name": current_name,
            "birth_date": d.isoformat(),
            "system": core_system,
            "name_order": name_order,
            "as_of": as_of_date.isoformat(),
        },
        "core": core,
        "extended": extended,
        "cycles": cycles,
        "reading": compose_reading(core, cycles, extended),
        "deep_reading": compose_deep_reading(core, extended, cycles),
        "method_audit": method_audit(
            d.day,
            d.month,
            d.year,
            name=normalized,
            name_order=name_order,
            system=core_system,
        ),
    }

    if include_chaldean and core_system != "chaldean":
        from .library import balliett_provenance_note, chaldean_flat_name_compound, resolve_compound

        chaldean_core = compute_core(
            name, d.day, d.month, d.year, system="chaldean", name_order=name_order
        )
        flat = chaldean_flat_name_compound(name)
        day_compound = resolve_compound(d.day) if d.day >= 10 else None
        result["cross_reference"] = {
            "system": "chaldean",
            "note": "Đối chiếu Chaldean (Cheiro, thư viện PD) — chỉ số TÊN + số kép; không trộn vào lá số Pythagoras chính.",
            "expression": chaldean_core["expression"]["value"],
            "soul_urge": chaldean_core["soul_urge"]["value"],
            "personality": chaldean_core["personality"]["value"],
            "name_compound_flat": flat,
            "birthday_compound": day_compound,
            "balliett": balliett_provenance_note(),
        }
    elif core_system == "chaldean":
        from .library import chaldean_flat_name_compound

        result["chaldean_detail"] = chaldean_flat_name_compound(name)

    if include_dong_phuong:
        from .cross_bind import cross_bind_dong_phuong

        result["dong_phuong_doi_chieu"] = {
            "life_path": cross_bind_dong_phuong(core["life_path"]["value"]),
            "expression": cross_bind_dong_phuong(core["expression"]["value"]),
        }
    return result
