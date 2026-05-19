from engine.luc_hao import calculate_timing


def test_void_release_can_be_today_when_branch_matches():
    result = calculate_timing(
        dung_than_chi="Dần",
        current_date_chi="Dần",
        is_moving=False,
        is_tuan_khong=True,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="fast",
        mai_hoa_total=8,
    )
    assert result["primary_rule_id"] == "void_release"
    assert result["best_match"]["offset_days"] == 0


def test_void_clash_activation_is_secondary_candidate():
    result = calculate_timing(
        dung_than_chi="Tý",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=True,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="medium",
        mai_hoa_total=10,
    )
    trigger_types = [item["trigger_type"] for item in result["candidates"]]
    assert "void_release" in trigger_types
    assert "void_clash_activation" in trigger_types
    assert result["best_match"]["trigger_type"] == "void_release"
