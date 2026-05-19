from engine.luc_hao import calculate_timing


def test_timing_moving_prefers_harmony():
    result = calculate_timing(
        dung_than_chi="Tý",
        current_date_chi="Tý",
        is_moving=True,
        is_tuan_khong=False,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="fast",
        mai_hoa_total=15,
    )
    assert result["primary_rule_id"] == "moving_to_harmony"
    assert result["best_match"]["branch"] == "Sửu"


def test_timing_static_prefers_clash():
    result = calculate_timing(
        dung_than_chi="Tý",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=False,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="medium",
        mai_hoa_total=12,
    )
    assert result["primary_rule_id"] == "static_to_clash"
    assert result["best_match"]["branch"] == "Ngọ"


def test_timing_void_release_has_highest_priority():
    result = calculate_timing(
        dung_than_chi="Dần",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=True,
        is_month_break=False,
        is_day_break=False,
        pace_bucket="slow",
        mai_hoa_total=9,
    )
    assert result["primary_rule_id"] == "void_release"
    assert result["best_match"]["branch"] == "Dần"


def test_timing_always_contains_mai_hoa_formula_candidate():
    result = calculate_timing(
        dung_than_chi="Mão",
        current_date_chi="Tý",
        is_moving=False,
        is_tuan_khong=False,
        is_month_break=True,
        is_day_break=False,
        pace_bucket="medium",
        mai_hoa_total=11,
    )
    assert any(item["trigger_type"] == "mai_hoa_formula" for item in result["candidates"])
