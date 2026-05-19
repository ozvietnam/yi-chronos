"""Top-level Bát Tự Hà Lạc orchestrator.

Public function:
    cast_ha_lac(birth_datetime_local, timezone='Asia/Ho_Chi_Minh', gender='nam')

Returns a JSON-serializable dict with:
- tien_thien_quai (先天卦, fate hexagram)
- hau_thien_quai (後天卦, operating hexagram)
- nguyen_duong (moving line) for each
- decade trajectory (12 stages from ~age 1 to ~age 84-90)
- intermediate Thiên/Địa numbers (for explainability)
- notes (any flagged caveats)
"""

from __future__ import annotations

from engine.bat_tu import extract_tu_tru

from .decade_trajectory import build_trajectory
from .hau_thien import derive_hau_thien
from .nguyen_duong import nguyen_duong_line
from .number_pools import compute_number_pools
from .quai_assembly import assemble_tien_thien


METHOD_ID = "bat_tu_ha_lac_v1"
SOURCE_REF = (
    "Học Năng, Bát Tự Hà Lạc Lược Khảo, Saigon 1974. "
    "Cross-verified with Chen Tuan (陈抟) lineage."
)


def cast_ha_lac(
    *,
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
) -> dict:
    """Compute Bát Tự Hà Lạc from a birth datetime."""
    if gender not in ("nam", "nữ"):
        raise ValueError("gender must be 'nam' or 'nữ'")

    # Step 1: Tứ trụ via existing Bát Tự engine.
    tu_tru = extract_tu_tru(birth_datetime_local, timezone)

    # Step 2: number pools.
    pools = compute_number_pools(tu_tru["pillars"])

    # Step 3: Tiên thiên quái.
    year_stem = tu_tru["pillars"]["year"]["stem"]
    tien_thien = assemble_tien_thien(
        pools_tien_reduced=pools.tien_reduced,
        pools_dia_reduced=pools.dia_reduced,
        year_stem=year_stem,
        gender=gender,
    )

    # Step 4: nguyên đường for Tiên thiên.
    hour_branch = tu_tru["pillars"]["hour"]["branch"]
    nd_tien, nd_tien_notes = nguyen_duong_line(tien_thien.binary_top_down, hour_branch)

    # Step 5: Hậu thiên + its nguyên đường.
    hau_thien, nd_hau, hau_notes = derive_hau_thien(tien_thien, nd_tien, hour_branch)

    # Step 6: decade trajectory.
    trajectory = build_trajectory(
        tien_binary=tien_thien.binary_top_down,
        hau_binary=hau_thien.binary_top_down,
        nguyen_duong_tien=nd_tien,
        nguyen_duong_hau=nd_hau,
    )

    all_notes = list(tien_thien.notes) + nd_tien_notes + hau_notes

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "birth_datetime_local": birth_datetime_local,
        "timezone": timezone,
        "gender": gender,
        "year_stem_polarity": (
            "dương" if year_stem in ("Giáp", "Bính", "Mậu", "Canh", "Nhâm") else "âm"
        ),
        "hour_branch": hour_branch,
        "number_pools": pools.to_dict(),
        "tien_thien_quai": {
            **tien_thien.to_dict(),
            "nguyen_duong_line": nd_tien,
        },
        "hau_thien_quai": {
            **hau_thien.to_dict(),
            "nguyen_duong_line": nd_hau,
        },
        "decade_trajectory": trajectory,
        "lifespan_span": {
            "start_age": trajectory[0]["age_start"] if trajectory else 1,
            "end_age": trajectory[-1]["age_end"] if trajectory else 0,
            "total_years": sum(t["years_span"] for t in trajectory),
        },
        "notes": all_notes,
        "interpretation_hint": (
            "Tiên thiên quái = cốt tử mệnh (vận tổng đời người). "
            "Hậu thiên quái = vận động dụng (cách thức vận hành thực tế). "
            "Mỗi hào = một giai đoạn ~6-9 năm. Hào nguyên đường = giai đoạn chủ chốt. "
            "Sách Học Năng (1974) chia 12 hào thành 84 năm chuẩn."
        ),
    }
