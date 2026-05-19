"""Top-level Lục Hào casting orchestrator."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from core.chronos import calculate_chronos_state
from core.hexagram import apply_moving_lines, get_hexagram_by_binary

from .casting import (
    InteractionSignal,
    _coin_face,
    _extract_stem_branch,
    _line_branch,
    _line_from_coin_sum,
)
from .constants import (
    BRANCH_ELEMENT,
    CLASH_BRANCH,
    TIMING_FUNNEL_MATRIX_V2,
    VOID_BRANCHES_BY_DAY_STEM,
)
from .jingfang import build_jingfang_scaffold
from .mai_hoa_env import _mai_hoa_environment
from .relations import (
    _detect_hidden_line_candidates,
    _impact_label,
    _relation,
    _select_dung_than_line,
)
from .ruler_profile import _build_ruler_profile
from .timing import (
    _estimate_by_maihoa_formula,
    _pace_bucket,
    calculate_timing,
)


def cast_luc_hao(
    *,
    datetime_local: str | None,
    timezone: str,
    question_text: str,
    interaction: InteractionSignal,
) -> dict[str, Any]:
    chronos = calculate_chronos_state(datetime_local, timezone)
    mai_hoa_env = _mai_hoa_environment(chronos)
    day_stem, day_branch = _extract_stem_branch(chronos.ganzhi.day)
    month_stem, month_branch = _extract_stem_branch(chronos.ganzhi.month)
    if not day_stem:
        day_stem = "Giáp"
    if not day_branch:
        day_branch = "Tý"
    if not month_branch:
        month_branch = "Tý"
    day_element = BRANCH_ELEMENT.get(day_branch, "thủy")
    seed_material = (
        f"{chronos.timestamp_utc}|{question_text}|{interaction.hold_duration_ms}|"
        f"{interaction.move_event_count}|{interaction.path_length_px:.2f}|{interaction.release_timestamp_ms}"
    )
    seed = int.from_bytes(sha256(seed_material.encode("utf-8")).digest()[:4], "big")

    lines = []
    line_bits_bottom_up = []
    moving_lines = []
    current_seed = seed
    for line_pos in range(1, 7):
        total = 0
        coin_values = []
        for _ in range(3):
            coin_value, current_seed = _coin_face(current_seed)
            total += coin_value
            coin_values.append(coin_value)
        decoded = _line_from_coin_sum(total)
        line_bits_bottom_up.append("1" if decoded["polarity"] == "yang" else "0")
        if decoded["moving"]:
            moving_lines.append(line_pos)
        branch = _line_branch(line_pos, day_branch)
        element = BRANCH_ELEMENT[branch]
        lines.append(
            {
                "line_position": line_pos,
                "coin_values": coin_values,
                "coin_sum": total,
                "symbol": decoded["symbol"],
                "polarity": decoded["polarity"],
                "moving": decoded["moving"],
                "branch": branch,
                "element": element,
                "luc_than": _relation(day_element, element),
            }
        )

    binary = "".join(line_bits_bottom_up[::-1])
    transformed_binary = apply_moving_lines(binary, moving_lines)
    primary_hex = get_hexagram_by_binary(binary)
    transformed_hex = get_hexagram_by_binary(transformed_binary)

    # 京房 scaffolding: 8 cung classifier + Najia + Lục thân theo cung + 伏神.
    # NOTE: this is the canonical 京房 layer (cung-element-based) — distinct from
    # the day-stem-based lục thân in `lines[]` above which serves the 文王 timing layer.
    primary_jingfang = build_jingfang_scaffold(binary, king_wen_index=primary_hex.king_wen_index)
    transformed_jingfang = build_jingfang_scaffold(transformed_binary, king_wen_index=transformed_hex.king_wen_index)

    # Deterministic baseline: line 3 is The, line 6 is Ung for v1.
    the_line = 3
    ung_line = 6
    the_info = next(line for line in lines if line["line_position"] == the_line)
    ung_info = next(line for line in lines if line["line_position"] == ung_line)

    tuan_khong_set = VOID_BRANCHES_BY_DAY_STEM.get(day_stem, ())
    for line in lines:
        line["is_tuan_khong"] = line["branch"] in tuan_khong_set
        line["is_month_break"] = CLASH_BRANCH.get(line["branch"]) == month_branch
        line["is_day_break"] = CLASH_BRANCH.get(line["branch"]) == day_branch

    moving_impact = []
    for line in lines:
        if not line["moving"]:
            continue
        impact = _impact_label(the_info["element"], line["element"])
        if line["is_tuan_khong"] or line["is_month_break"] or line["is_day_break"]:
            impact = f"{impact} nhưng lực suy (không/phá)"
        moving_impact.append(
            {
                "line_position": line["line_position"],
                "impact": impact,
                "luc_than": line["luc_than"],
            }
        )

    caution_count = sum(
        "cảnh giác" in item["impact"] or "suy" in item["impact"] for item in moving_impact
    )
    support_count = sum(
        "thuận" in item["impact"] or "chủ động" in item["impact"] for item in moving_impact
    )
    if support_count > caution_count:
        verdict = "Có cửa thuận, nên hành động có kế hoạch."
        verdict_tag = "favorable"
    elif caution_count > support_count:
        verdict = "Thế yếu hoặc bị cản, nên giảm rủi ro trước khi tiến."
        verdict_tag = "caution"
    else:
        verdict = "Trạng thái cân bằng, nên theo dõi thêm tín hiệu mới."
        verdict_tag = "neutral"

    # Mix with Mai Hoa environmental flow for multi-layer energy judgement.
    relation_tag = mai_hoa_env["relation_tag"]
    if relation_tag in {"supportive", "controlling"} and verdict_tag == "caution":
        energy_flow = "Nội lực yếu nhưng môi trường đang trợ, nên tiến chậm mà chắc."
    elif relation_tag in {"pressure", "draining"} and verdict_tag == "favorable":
        energy_flow = "Nghiệm ngắn hạn thuận nhưng môi trường hao lực, cần giữ biên an toàn."
    elif relation_tag in {"pressure", "draining"} and verdict_tag == "caution":
        energy_flow = "Cả môi trường và chi tiết đều nghịch, ưu tiên phòng thủ."
    elif relation_tag in {"supportive", "controlling"} and verdict_tag == "favorable":
        energy_flow = "Dòng năng lượng đồng pha, khả năng thành sự cao."
    else:
        energy_flow = "Dòng năng lượng trung tính, nên chờ thêm tín hiệu xác nhận."

    dung_than_line = _select_dung_than_line(lines, question_text)
    pace_bucket = _pace_bucket(mai_hoa_env)
    mai_hoa_total = _estimate_by_maihoa_formula(mai_hoa_env)
    timing_prediction = calculate_timing(
        dung_than_chi=dung_than_line["branch"],
        current_date_chi=day_branch,
        is_moving=bool(dung_than_line["moving"]),
        is_tuan_khong=bool(dung_than_line["is_tuan_khong"]),
        is_month_break=bool(dung_than_line["is_month_break"]),
        is_day_break=bool(dung_than_line["is_day_break"]),
        pace_bucket=pace_bucket,
        mai_hoa_total=mai_hoa_total,
        current_local_datetime=chronos.local_datetime,
    )
    hidden_line_candidates = _detect_hidden_line_candidates(lines, dung_than_line)
    ruler_profile = _build_ruler_profile(
        question_text=question_text,
        moving_lines=moving_lines,
        moving_line_analysis=moving_impact,
        mai_hoa_environment=mai_hoa_env,
        timing_prediction=timing_prediction,
        verdict_tag=verdict_tag,
        primary_hex_name=primary_hex.name_vi,
        transformed_hex_name=transformed_hex.name_vi,
    )

    return {
        "question_text": question_text,
        "seed": seed,
        "primary_hexagram": {
            "name_vi": primary_hex.name_vi,
            "binary": binary,
            "king_wen_index": primary_hex.king_wen_index,
        },
        "transformed_hexagram": {
            "name_vi": transformed_hex.name_vi,
            "binary": transformed_binary,
            "king_wen_index": transformed_hex.king_wen_index,
        },
        "moving_lines": moving_lines,
        "the_line": the_line,
        "ung_line": ung_line,
        "the_info": {"line_position": the_line, "branch": the_info["branch"], "element": the_info["element"]},
        "ung_info": {"line_position": ung_line, "branch": ung_info["branch"], "element": ung_info["element"]},
        "calendar_checks": {
            "day_ganzhi": chronos.ganzhi.day,
            "month_ganzhi": chronos.ganzhi.month,
            "day_stem": day_stem,
            "day_branch": day_branch,
            "month_branch": month_branch,
            "tuan_khong_branches": list(tuan_khong_set),
        },
        "lines": lines,
        "moving_line_analysis": moving_impact,
        "dung_than": {
            "line_position": dung_than_line["line_position"],
            "branch": dung_than_line["branch"],
            "element": dung_than_line["element"],
            "luc_than": dung_than_line["luc_than"],
            "moving": dung_than_line["moving"],
            "is_tuan_khong": dung_than_line["is_tuan_khong"],
            "is_month_break": dung_than_line["is_month_break"],
            "is_day_break": dung_than_line["is_day_break"],
        },
        "timing_prediction": timing_prediction,
        "hidden_line_candidates": hidden_line_candidates,
        "jingfang_scaffold": primary_jingfang.to_dict(),
        "transformed_jingfang_scaffold": transformed_jingfang.to_dict(),
        "timing_funnel_matrix": list(TIMING_FUNNEL_MATRIX_V2),
        "verdict": {"tag": verdict_tag, "text": verdict},
        "mai_hoa_environment": mai_hoa_env,
        "energy_flow_summary": energy_flow,
        "ruler_profile": ruler_profile,
    }
