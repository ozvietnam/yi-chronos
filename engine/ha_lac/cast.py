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
from .ho_quai import derive_ho_quai
from .hoa_cong import analyze_hoa_cong_nguyen_khi, determine_season_from_month
from .menh_hop_cach import evaluate_menh_hop_cach
from .nguyen_duong import nguyen_duong_line
from .nien_menh_dac_the import (
    evaluate_dac_the,
    evaluate_nien_menh_vs_que_tien_thien,
)
from .thoi_que import describe_thoi_cau_truc
from .number_pools import compute_number_pools
from .quai_assembly import assemble_tien_thien


METHOD_ID = "bat_tu_ha_lac_v1"
SOURCE_REF = (
    "Học Năng, Bát Tự Hà Lạc Lược Khảo, Saigon 1974. "
    "Cross-verified with Chen Tuan (陈抟) lineage."
)


def _safe_call(fn, **kwargs):
    """Safe wrapper — catch error so cast doesn't fail if 1 sub-engine has issue."""
    try:
        return fn(**kwargs)
    except Exception as e:
        return {"_error": str(e)[:200]}


def _compute_menh_hop_cach(birth_dt_str, tu_tru, tien_thien, nd_tien, pools, year_stem) -> dict | None:
    """Helper — evaluate Mệnh Hợp Cách 10 tiêu chuẩn."""
    try:
        import re
        m = re.search(r"\d{4}-(\d{2})", birth_dt_str)
        month = int(m.group(1)) if m else 6
        season = determine_season_from_month(month)
        # Nạp âm: extract from year pillar if available
        year_pillar = tu_tru["pillars"]["year"]
        nap_am_raw = year_pillar.get("nap_am") or year_pillar.get("element") or ""
        # Map to one of Kim/Mộc/Thủy/Hỏa/Thổ
        mang = None
        for k in ("Kim", "Mộc", "Thủy", "Hỏa", "Thổ"):
            if k.lower() in str(nap_am_raw).lower():
                mang = k
                break
        year_polarity = "dương" if year_stem in ("Giáp", "Bính", "Mậu", "Canh", "Nhâm") else "âm"
        result = evaluate_menh_hop_cach(
            source_quai_name=tien_thien.name_vi,
            upper_trigram=tien_thien.upper_trigram,
            lower_trigram=tien_thien.lower_trigram,
            binary_top_down=tien_thien.binary_top_down,
            nguyen_duong_line=nd_tien,
            year_polarity=year_polarity,
            so_duong=pools.tien_raw,
            so_am=pools.dia_raw,
            season_key=season,
            birth_month_amlich=None,  # TODO: convert dương→âm lịch
            mang_nap_am=mang,
        )
        return result.to_dict()
    except Exception as e:
        return {"_error": str(e)[:200]}


def _compute_hoa_cong_nguyen_khi(birth_dt_str, tu_tru, tien_thien, hau_thien, ho_tien, ho_hau) -> dict | None:
    """Helper — gather structural trigrams + run hoa_cong analysis."""
    try:
        # Parse month from birth dt
        import re
        m = re.search(r"\d{4}-(\d{2})", birth_dt_str)
        if not m:
            return None
        month = int(m.group(1))
        # Gather trigrams from structure
        trigrams = []
        for q in (tien_thien, hau_thien):
            if hasattr(q, "upper_trigram"):
                trigrams.append(q.upper_trigram)
            if hasattr(q, "lower_trigram"):
                trigrams.append(q.lower_trigram)
        for h in (ho_tien, ho_hau):
            if h:
                trigrams.append(h.get("ngoai_ho_trigram"))
                trigrams.append(h.get("noi_ho_trigram"))
        trigrams = [t for t in trigrams if t]
        year = tu_tru["pillars"]["year"]
        return analyze_hoa_cong_nguyen_khi(
            birth_month=month,
            year_stem=year["stem"],
            year_branch=year["branch"],
            structural_trigrams=trigrams,
        )
    except Exception as e:
        return {"_error": str(e)[:200]}


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

    # Step 5b: Hỗ quái cho cả Tiên Thiên + Hậu Thiên (Xuân Cang p.4)
    try:
        ho_tien = derive_ho_quai(tien_thien.binary_top_down, source_name=tien_thien.name_vi).to_dict()
    except Exception:
        ho_tien = None
    try:
        ho_hau = derive_ho_quai(hau_thien.binary_top_down, source_name=hau_thien.name_vi).to_dict()
    except Exception:
        ho_hau = None

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
        "ho_quai_tien": ho_tien,
        "ho_quai_hau": ho_hau,
        "hoa_cong_nguyen_khi": _compute_hoa_cong_nguyen_khi(
            birth_datetime_local, tu_tru, tien_thien, hau_thien, ho_tien, ho_hau
        ),
        "menh_hop_cach": _compute_menh_hop_cach(
            birth_datetime_local, tu_tru, tien_thien, nd_tien, pools, year_stem
        ),
        "thoi_que": describe_thoi_cau_truc(tien_thien.name_vi, hau_thien.name_vi),
        "nien_menh_vs_que_TT": _safe_call(
            evaluate_nien_menh_vs_que_tien_thien,
            can_chi_nam=f"{tu_tru['pillars']['year']['stem']} {tu_tru['pillars']['year']['branch']}",
            que_tien_thien_upper=tien_thien.upper_trigram,
        ),
        "dac_the": _safe_call(
            evaluate_dac_the,
            can_nam=tu_tru["pillars"]["year"]["stem"],
            can_chi_nam=f"{tu_tru['pillars']['year']['stem']} {tu_tru['pillars']['year']['branch']}",
        ),
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
