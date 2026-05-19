"""Tam Thiên ruler-profile derivation — large composition layer."""

from __future__ import annotations

from typing import Any

from .constants import (
    PAIR_DYNAMICS_MAP,
    TRIGRAM_ROLE_MAP,
    VIRTUE_ANCHOR_HEXAGRAMS,
)


def _build_ruler_profile(
    *,
    question_text: str,
    moving_lines: list[int],
    moving_line_analysis: list[dict[str, Any]],
    mai_hoa_environment: dict[str, Any],
    timing_prediction: dict[str, Any],
    verdict_tag: str,
    primary_hex_name: str,
    transformed_hex_name: str,
) -> dict[str, Any]:
    relation_tag = mai_hoa_environment.get("relation_tag", "neutral")
    upper_trigram = mai_hoa_environment.get("upper_trigram", "")
    lower_trigram = mai_hoa_environment.get("lower_trigram", "")
    if relation_tag == "supportive":
        context_text = "Thoán-layer: Môi trường Dụng sinh Thể, bối cảnh trợ lực."
    elif relation_tag == "controlling":
        context_text = "Thoán-layer: Thể khắc Dụng, chủ động kiểm soát được nhịp việc."
    elif relation_tag == "pressure":
        context_text = "Thoán-layer: Dụng khắc Thể, ngoại cảnh tạo áp lực rõ."
    elif relation_tag == "draining":
        context_text = "Thoán-layer: Thể sinh Dụng, có dấu hiệu hao lực."
    else:
        context_text = "Thoán-layer: Quan hệ ngũ hành trung tính, cần thêm xác thực."

    if not moving_lines:
        process_text = "Tượng-layer: Hào tĩnh nhiều, thiên về quan sát và chỉnh nền."
    else:
        process_text = (
            "Tượng-layer: Có hào động tại "
            + ", ".join(str(v) for v in moving_lines)
            + ", ưu tiên bám diễn biến vi mô theo từng hào."
        )

    best = timing_prediction.get("best_match", {})
    best_offset = int(best.get("offset_days", 0))
    pace_bucket = timing_prediction.get("pace_bucket", "medium")
    timing_text = (
        f"Timing-layer: ưu tiên D+{best_offset}"
        + (f" (ngày {best.get('branch')})" if best.get("branch") else "")
        + f" - {best.get('reason', 'mốc ứng kỳ theo phễu lọc')}."
    )

    if verdict_tag == "favorable":
        action_text = "Action-layer: Có thể tiến bước chủ động, vẫn giữ biên an toàn."
    elif verdict_tag == "caution":
        action_text = "Action-layer: Ưu tiên phòng thủ, hoãn quyết định all-in."
    else:
        action_text = "Action-layer: Trạng thái cân bằng, nên thăm dò thêm trước khi chốt."

    degraded_hits = sum("suy" in row.get("impact", "") for row in moving_line_analysis)
    if verdict_tag == "favorable" and degraded_hits == 0:
        decision_quality = "favorable"
    elif verdict_tag == "neutral" or degraded_hits == 1:
        decision_quality = "mixed"
    else:
        decision_quality = "regret-risk"

    if decision_quality == "favorable" and relation_tag in {"supportive", "controlling"}:
        strategy_mode = "execute"
    elif decision_quality == "regret-risk":
        strategy_mode = "reframe"
    else:
        strategy_mode = "stabilize"

    if decision_quality == "regret-risk":
        posture_mode = "hide_and_wait"
    elif pace_bucket == "slow" or relation_tag in {"pressure", "draining"}:
        posture_mode = "stabilize"
    else:
        posture_mode = "advance"

    if posture_mode in {"hide_and_wait", "stabilize"}:
        leverage_mode = "light"
    elif decision_quality == "favorable" and pace_bucket == "fast":
        leverage_mode = "high"
    else:
        leverage_mode = "normal"

    trigger_offset = best_offset if best_offset > 0 else 1
    staged_plan = {
        "prepare": "Ổn định nội lực, chốt phạm vi việc nhỏ và dữ liệu cốt lõi.",
        "trigger": f"Kích hoạt tại mốc D+{trigger_offset} theo ứng kỳ tốt nhất.",
        "push": "Sau khi kích hoạt, mở rộng từng nhịp và tránh all-in trong một bước.",
    }

    has_clear_question = len(question_text.strip()) >= 12
    social_ready = relation_tag in {"supportive", "controlling"}
    if social_ready and has_clear_question and len(moving_lines) >= 2:
        coalition_strength = "high"
    elif social_ready or has_clear_question:
        coalition_strength = "medium"
    else:
        coalition_strength = "low"

    conflict_mode = (
        "negotiate_first"
        if decision_quality != "favorable" or relation_tag in {"pressure", "draining"}
        else "legal_last"
    )

    evidence_gate = {
        "status": "ready"
        if has_clear_question and (len(moving_lines) > 0 or decision_quality == "favorable")
        else "insufficient",
        "note": (
            "Đủ dữ kiện để chốt bước quyết định kế tiếp."
            if has_clear_question and (len(moving_lines) > 0 or decision_quality == "favorable")
            else "Thiếu dữ kiện xác thực; nên bổ sung bằng chứng trước khi quyết định lớn."
        ),
    }

    counterparty_risk = (
        "screen_required"
        if relation_tag in {"supportive", "controlling"} and decision_quality in {"mixed", "regret-risk"}
        else "normal_watch"
    )

    if relation_tag in {"pressure", "draining"} and best_offset > 10:
        scope_gate = "small_ok_big_wait"
    elif decision_quality == "favorable" and relation_tag in {"supportive", "controlling"}:
        scope_gate = "small_big_ok"
    else:
        scope_gate = "all_wait"

    if leverage_mode == "light":
        tradeoff_hint = "Cắt việc phụ, giữ nguồn lực cho hạng mục cốt lõi trong 1-2 nhịp tới."
    elif leverage_mode == "high":
        tradeoff_hint = "Tập trung nguồn lực vào mốc chính, tránh phân tán sang mục tiêu phụ."
    else:
        tradeoff_hint = "Phân bổ đều, nhưng ưu tiên hạng mục tạo chứng cứ tiến triển sớm."

    timing_ready = best_offset <= 10
    resource_ready = leverage_mode != "light"
    social_ready = coalition_strength in {"medium", "high"}
    readiness_score = int(timing_ready) + int(resource_ready) + int(social_ready)
    triple_condition_check = {
        "timing_ready": timing_ready,
        "resource_ready": resource_ready,
        "social_ready": social_ready,
        "score": f"{readiness_score}/3",
        "allow_execute": readiness_score >= 2 and evidence_gate["status"] == "ready",
    }

    if not triple_condition_check["allow_execute"] and strategy_mode == "execute":
        strategy_mode = "stabilize"

    if scope_gate == "small_ok_big_wait":
        one_line_verdict = f"Ưu tiên việc nhỏ trước, canh mốc D+{trigger_offset} mới tăng nhịp."
    elif strategy_mode == "execute":
        one_line_verdict = f"Có thể triển khai có kiểm soát quanh mốc D+{trigger_offset}."
    else:
        one_line_verdict = "Giữ thế ổn định, bổ sung dữ kiện rồi mới quyết định lớn."

    reverse_probe = {
        "best_offset_days": best_offset,
        "check_offsets": sorted({max(0, best_offset - 1), best_offset, best_offset + 1}),
        "note": "Dùng cụm mốc nghịch để kiểm tra đảo pha trước khi chốt quyết định lớn.",
    }

    recovery_focus_set = {"Phục", "Khôn"}
    is_recovery_case = (
        primary_hex_name in recovery_focus_set or transformed_hex_name in recovery_focus_set
    )
    recovery_cycle = {
        "is_recovery_case": is_recovery_case,
        "reentry_window": reverse_probe["check_offsets"] if is_recovery_case else [],
        "note": (
            "Case phục hồi: ưu tiên dựng lại nền rồi mới mở rộng."
            if is_recovery_case
            else "Case không nghiêng phục hồi chu kỳ."
        ),
    }
    pair_dynamics = PAIR_DYNAMICS_MAP.get((upper_trigram, lower_trigram), "other_pair")
    timing_dual_view = {
        "forward_offsets": [
            int(item.get("offset_days", 0))
            for item in timing_prediction.get("candidates", [])[:3]
        ],
        "reverse_check_offsets": reverse_probe["check_offsets"],
    }

    virtue_anchor = (
        VIRTUE_ANCHOR_HEXAGRAMS.get(primary_hex_name)
        or VIRTUE_ANCHOR_HEXAGRAMS.get(transformed_hex_name)
        or ""
    )

    has_line_signal = bool(moving_line_analysis)
    confidence = (
        "high" if has_clear_question and has_line_signal
        else "medium" if has_clear_question
        else "low"
    )
    notes = "Ruler giữ chế độ conservative nếu dữ liệu câu hỏi mơ hồ hoặc tín hiệu hào yếu."

    return {
        "id": "tam_thien_v1",
        "layers": {
            "context": context_text,
            "process": process_text,
            "timing": timing_text,
            "action": action_text,
        },
        "context_trigram_roles": {
            "upper_trigram": {
                "name": upper_trigram,
                "role": TRIGRAM_ROLE_MAP.get(upper_trigram, "vai trò chưa định danh"),
            },
            "lower_trigram": {
                "name": lower_trigram,
                "role": TRIGRAM_ROLE_MAP.get(lower_trigram, "vai trò chưa định danh"),
            },
        },
        "pair_dynamics": pair_dynamics,
        "timing_dual_view": timing_dual_view,
        "decision_quality": decision_quality,
        "strategy_mode": strategy_mode,
        "posture_mode": posture_mode,
        "leverage_mode": leverage_mode,
        "scope_gate": scope_gate,
        "tradeoff_hint": tradeoff_hint,
        "triple_condition_check": triple_condition_check,
        "one_line_verdict": one_line_verdict,
        "coalition_strength": coalition_strength,
        "conflict_mode": conflict_mode,
        "counterparty_risk": counterparty_risk,
        "evidence_gate": evidence_gate,
        "staged_plan": staged_plan,
        "recovery_cycle": recovery_cycle,
        "reverse_probe": reverse_probe,
        "virtue_anchor": virtue_anchor,
        "confidence": confidence,
        "notes": notes,
    }
