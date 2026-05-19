from engine.luc_hao import _detect_hidden_line_candidates, calculate_timing


def test_double_break_promotes_break_recovery_priority():
    result = calculate_timing(
        dung_than_chi="Tý",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=False,
        is_month_break=True,
        is_day_break=True,
        pace_bucket="medium",
        mai_hoa_total=9,
        current_local_datetime="2026-05-08T09:00:00",
    )
    assert result["primary_rule_id"] == "break_recovery_by_harmony"
    assert result["best_match"]["trigger_type"] == "break_recovery_by_harmony"


def test_timing_candidates_include_projected_local_date():
    result = calculate_timing(
        dung_than_chi="Mão",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=False,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="fast",
        mai_hoa_total=6,
        current_local_datetime="2026-05-08T09:00:00",
    )
    assert all("projected_local_date" in item for item in result["candidates"])


def test_hidden_line_candidates_detect_same_relation_static_lines():
    lines = [
        {"line_position": 1, "luc_than": "Thê Tài", "moving": True, "branch": "Tý", "element": "thủy"},
        {"line_position": 2, "luc_than": "Quan Quỷ", "moving": False, "branch": "Sửu", "element": "thổ"},
        {"line_position": 3, "luc_than": "Thê Tài", "moving": False, "branch": "Dần", "element": "mộc"},
        {"line_position": 4, "luc_than": "Phụ Mẫu", "moving": False, "branch": "Mão", "element": "mộc"},
    ]
    hidden = _detect_hidden_line_candidates(lines, lines[0])
    assert len(hidden) == 1
    assert hidden[0]["line_position"] == 3
