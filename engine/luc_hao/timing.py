"""Ứng-kỳ timing engine — funnel-based candidate ranking."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from .constants import CLASH_BRANCH, HARMONY_BRANCH
from .relations import _days_until_branch


def _pace_bucket(mai_hoa_env: dict[str, Any]) -> str:
    fast_trigrams = {"Chấn", "Tốn"}
    slow_trigrams = {"Cấn", "Khôn"}
    upper = mai_hoa_env["upper_trigram"]
    lower = mai_hoa_env["lower_trigram"]
    relation_tag = mai_hoa_env["relation_tag"]
    if upper in fast_trigrams or lower in fast_trigrams or relation_tag == "pressure":
        return "fast"
    if upper in slow_trigrams or lower in slow_trigrams or relation_tag == "draining":
        return "slow"
    return "medium"


def _unit_from_pace(pace: str) -> str:
    if pace == "fast":
        return "day_or_hour"
    if pace == "slow":
        return "month_or_year"
    return "day_or_week"


def _estimate_by_maihoa_formula(mai_hoa_env: dict[str, Any]) -> int:
    return (
        int(mai_hoa_env["upper_trigram_num"])
        + int(mai_hoa_env["lower_trigram_num"])
        + int(mai_hoa_env["moving_line_num"])
    )


def _to_local_iso_plus_days(local_datetime_text: str, offset_days: int) -> str:
    try:
        dt = datetime.fromisoformat(local_datetime_text)
    except ValueError:
        return ""
    projected = dt + timedelta(days=offset_days)
    return projected.date().isoformat()


def calculate_timing(
    *,
    dung_than_chi: str,
    current_date_chi: str,
    is_moving: bool,
    is_tuan_khong: bool,
    is_month_break: bool,
    is_day_break: bool,
    pace_bucket: str,
    mai_hoa_total: int,
    current_local_datetime: str | None = None,
) -> dict[str, Any]:
    clash_branch = CLASH_BRANCH.get(dung_than_chi, dung_than_chi)
    harmony_branch = HARMONY_BRANCH.get(dung_than_chi, dung_than_chi)
    release_branch = dung_than_chi

    days_to_hop = _days_until_branch(current_date_chi, harmony_branch)
    days_to_xung = _days_until_branch(current_date_chi, clash_branch)
    days_to_release = _days_until_branch(current_date_chi, release_branch)

    candidates: list[dict[str, Any]] = []

    priority_shift = 1 if (is_month_break and is_day_break and not is_tuan_khong) else 0

    if is_tuan_khong:
        candidates.append(
            {
                "trigger_type": "void_release",
                "branch": release_branch,
                "offset_days": days_to_release,
                "reason": "Ra khỏi Tuần Không (điền thực theo địa chi hào)",
                "priority": 1,
            }
        )
        candidates.append(
            {
                "trigger_type": "void_clash_activation",
                "branch": clash_branch,
                "offset_days": days_to_xung,
                "reason": "Xung thực để kích hoạt hào đang Không",
                "priority": 2,
            }
        )
    elif is_moving:
        candidates.append(
            {
                "trigger_type": "moving_to_harmony",
                "branch": harmony_branch,
                "offset_days": days_to_hop,
                "reason": "Hào Dụng Thần động -> ưu tiên ngày Hợp",
                "priority": 1 + priority_shift,
            }
        )
    else:
        candidates.append(
            {
                "trigger_type": "static_to_clash",
                "branch": clash_branch,
                "offset_days": days_to_xung,
                "reason": "Hào Dụng Thần tĩnh -> ưu tiên ngày Xung",
                "priority": 1 + priority_shift,
            }
        )

    if is_month_break or is_day_break:
        candidates.append(
            {
                "trigger_type": "break_recovery_by_harmony",
                "branch": harmony_branch,
                "offset_days": days_to_hop,
                "reason": "Hào bị phá -> chờ Hợp để gỡ thế phá",
                "priority": 1 if (is_month_break and is_day_break and not is_tuan_khong) else 2,
            }
        )

    candidates.append(
        {
            "trigger_type": "mai_hoa_formula",
            "branch": "",
            "offset_days": mai_hoa_total,
            "reason": "Mai Hoa số thành quẻ (thượng + hạ + hào động)",
            "priority": 3 + priority_shift,
        }
    )
    if current_local_datetime:
        for item in candidates:
            item["projected_local_date"] = _to_local_iso_plus_days(
                current_local_datetime, int(item["offset_days"])
            )
    candidates.sort(key=lambda item: (item["priority"], item["offset_days"]))
    best = candidates[0]

    return {
        "pace_bucket": pace_bucket,
        "timing_unit_hint": _unit_from_pace(pace_bucket),
        "dung_than_chi": dung_than_chi,
        "current_date_chi": current_date_chi,
        "candidates": candidates,
        "best_match": best,
        "primary_rule_id": best["trigger_type"],
        "funnel_matrix_version": "v2",
        "funnel_applied": [item["trigger_type"] for item in candidates],
    }
