"""Top-level Bát Tự orchestrator.

Public function: cast_bat_tu(birth_datetime_local, timezone='Asia/Ho_Chi_Minh', gender='nam')
"""

from __future__ import annotations

from .cach_cuc import classify_cach_cuc
from .constants import BRANCH_ELEMENT, THAP_THAN_MEANING, THAP_THAN_SHORT
from .dai_van import build_dai_van_chart
from .dung_than import determine_dung_than
from .ngu_hanh import count_elements, day_master_strength
from .than_sat import detect_than_sat
from .thap_than import THAP_THAN_FAMILY, thap_than_of
from .truong_sinh import compute_truong_sinh_chart
from .tu_tru import extract_tu_tru


METHOD_ID = "bat_tu_tu_tru_v1"
SOURCE_REF = "子平真詮 + 滴天髓 + 三命通會 (canonical Tử Bình tradition)"


def _annotate_pillars_with_thap_than(pillars: dict, day_master: str) -> dict:
    """Add thap_than (relative to Day Master) to each pillar's stem + branch hidden stems."""
    annotated = {}
    for pos in ("year", "month", "day", "hour"):
        p = dict(pillars[pos])
        if pos == "day":
            # Day pillar IS the Day Master — stem self-reference labeled "Bản thân"
            p["stem_thap_than"] = "Bản thân"
            p["stem_thap_than_short"] = "TA"
        else:
            tt = thap_than_of(day_master, p["stem"])
            p["stem_thap_than"] = tt
            p["stem_thap_than_short"] = THAP_THAN_SHORT.get(tt, tt)
        # Hidden stems in the branch
        hidden_with_tt = []
        for hs in p["hidden_stems"]:
            if hs == day_master and pos == "day":
                hidden_with_tt.append({"stem": hs, "thap_than": "Bản thân (gốc)"})
            else:
                hidden_with_tt.append({
                    "stem": hs,
                    "thap_than": thap_than_of(day_master, hs),
                })
        p["hidden_stems_with_thap_than"] = hidden_with_tt
        annotated[pos] = p
    return annotated


def cast_bat_tu(
    *,
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
) -> dict:
    """Cast a Bát Tự chart from a birth datetime.

    Returns a JSON-serializable dict with:
      - tu_tru: 4 pillars + Day Master
      - thap_than_chart: per-pillar Thập Thần labels
      - ngu_hanh: element distribution
      - day_master_assessment: strength tag
    """
    if gender not in ("nam", "nữ"):
        raise ValueError("gender must be 'nam' or 'nữ'")

    base = extract_tu_tru(birth_datetime_local, timezone)
    day_master = base["day_master"]["stem"]

    pillars_annotated = _annotate_pillars_with_thap_than(base["pillars"], day_master)
    element_counts = count_elements(base["pillars"])
    dm_assessment = day_master_strength(base["day_master"]["element"], element_counts)

    # Build a compact summary of the chart's 10-god distribution.
    thap_than_distribution: dict[str, int] = {}
    for pos in ("year", "month", "hour"):     # skip 'day' (= Bản thân)
        tt = pillars_annotated[pos]["stem_thap_than"]
        thap_than_distribution[tt] = thap_than_distribution.get(tt, 0) + 1
    # Also count hidden stems' Thập Thần.
    hidden_thap_than_distribution: dict[str, int] = {}
    for pos in ("year", "month", "day", "hour"):
        for h in pillars_annotated[pos]["hidden_stems_with_thap_than"]:
            tt = h["thap_than"]
            if tt.startswith("Bản thân"):
                continue
            hidden_thap_than_distribution[tt] = hidden_thap_than_distribution.get(tt, 0) + 1

    # ─── α layers: Vòng Trường Sinh + Thần Sát + Đại Vận ────────────────────
    truong_sinh = compute_truong_sinh_chart(base["pillars"], day_master)
    than_sat = detect_than_sat(base["pillars"], day_master)
    year_stem = base["pillars"]["year"]["stem"]

    # Parse birth_datetime for accurate starting-age computation.
    parsed_birth_dt = None
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        local_dt_naive = datetime.fromisoformat(birth_datetime_local)
        if local_dt_naive.tzinfo is None:
            local_dt_naive = local_dt_naive.replace(tzinfo=ZoneInfo(timezone))
        parsed_birth_dt = local_dt_naive
    except (ValueError, ImportError):
        parsed_birth_dt = None

    dai_van = build_dai_van_chart(
        pillars=base["pillars"],
        year_stem=year_stem,
        gender=gender,
        birth_datetime=parsed_birth_dt,
    )

    # ─── Refinement layer: Dụng Thần / Hỷ Thần (v2 — + Điều Hậu) ──────────
    month_branch = base["pillars"]["month"]["branch"]
    month_branch_el = BRANCH_ELEMENT.get(month_branch)
    dung_than = determine_dung_than(
        day_element=base["day_master"]["element"],
        element_counts=element_counts,
        strength_tag=dm_assessment["strength_tag"],
        month_branch_element=month_branch_el,
        # v2: enable Điều Hậu climate balance
        day_stem=base["day_master"]["stem"],
        month_branch=month_branch,
    )

    # Cách cục classifier
    cach_cuc = classify_cach_cuc(base["pillars"], day_master)

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "birth_datetime_local": birth_datetime_local,
        "timezone": timezone,
        "gender": gender,
        "tu_tru": {
            "ganzhi_raw": base["ganzhi_raw"],
            "pillars": pillars_annotated,
            "day_master": base["day_master"],
            "solar_term": base["solar_term"],
        },
        "thap_than_meanings": THAP_THAN_MEANING,
        "thap_than_family_map": THAP_THAN_FAMILY,
        "thap_than_distribution": {
            "visible": thap_than_distribution,
            "hidden": hidden_thap_than_distribution,
        },
        "ngu_hanh": {
            "counts": element_counts,
            "day_master_assessment": dm_assessment,
        },
        "truong_sinh": truong_sinh,
        "than_sat": than_sat,
        "dai_van": dai_van,
        "dung_than": dung_than.to_dict(),
        # cach_cuc is already a dict (classify_cach_cuc returns CachCucResult.to_dict())
        # The dict contains both `cach_name` AND the alias `cach_cuc_label` (added 2026-05-12)
        "cach_cuc": cach_cuc,
        "deferred_layers": [
            "Thần Sát mở rộng (hiện ship 15 sao cốt lõi) — full set ~80 sao",
            "Tòng cách + Hóa khí cách (extreme patterns) — cần Day Master strength ≥ 8 hoặc ≤ -8",
            # NOTE: Điều hậu added in dung_than v2 (2026-05-12) — removed from deferred.
        ],
    }
