"""Tests for engine.ha_lac.luan_giai — Bát Tự Hà Lạc synthesizer."""
from __future__ import annotations

import pytest

from engine.ha_lac import cast_ha_lac, compose_ha_lac_luan_giai


@pytest.fixture
def founder_state():
    return cast_ha_lac(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_luan(founder_state):
    return compose_ha_lac_luan_giai(founder_state, current_age=38)


def test_method_id(founder_luan):
    assert founder_luan["method_id"] == "bat_tu_ha_lac_luan_giai_v1"


def test_source_ref_cites_hoc_nang(founder_luan):
    assert "Học Năng" in founder_luan["source_ref"]


def test_all_sections_present(founder_luan):
    required = [
        "method_id", "source_ref", "paradigm_guard", "overview",
        "tien_thien_luan", "hau_thien_luan", "comparison",
        "trajectory_luan", "bo_huong_stage", "lifespan", "closing",
    ]
    for key in required:
        assert key in founder_luan


def test_paradigm_no_predict(founder_luan):
    assert "KHÔNG dự đoán" in founder_luan["paradigm_guard"]


def test_founder_tien_thien_quai_60(founder_luan):
    t = founder_luan["tien_thien_luan"]
    assert t["king_wen"] == 60
    assert t["name_vi"] == "Tiết"


def test_founder_hau_thien_quai_29(founder_luan):
    h = founder_luan["hau_thien_luan"]
    assert h["king_wen"] == 29


def test_founder_comparison_thuy(founder_luan):
    c = founder_luan["comparison"]
    assert c["tien_upper_el"] == "thủy"
    assert c["hau_upper_el"] == "thủy"
    assert c["pattern"] == "tỷ hòa"


def test_founder_age_38_stage(founder_luan):
    tj = founder_luan["trajectory_luan"]
    current = tj["current"]
    assert current is not None
    assert current["stage_index"] == 5
    assert current["age_start"] <= 38 <= current["age_end"]


def test_founder_lifespan_84_to_90_years(founder_luan):
    span = founder_luan["lifespan"]
    assert 84 <= span["total_years"] <= 90


def test_founder_12_stages(founder_luan):
    tj = founder_luan["trajectory_luan"]
    assert len(tj["stages"]) == 12
    assert tj["stages"][0]["hexagram"] == "tien"
    assert tj["stages"][0]["line_position"] == 1
    assert tj["stages"][11]["hexagram"] == "hau"
    assert tj["stages"][11]["line_position"] == 6


def test_founder_2_nguyen_duong_stages(founder_luan):
    tj = founder_luan["trajectory_luan"]
    nd_stages = [s for s in tj["stages"] if s["is_nguyen_duong"]]
    assert len(nd_stages) == 2
    tiens = [s for s in nd_stages if s["hexagram"] == "tien"]
    haus = [s for s in nd_stages if s["hexagram"] == "hau"]
    assert len(tiens) == 1
    assert len(haus) == 1


def test_founder_is_current_marked(founder_luan):
    tj = founder_luan["trajectory_luan"]
    current_stages = [s for s in tj["stages"] if s["is_current"]]
    assert len(current_stages) == 1


def test_no_current_age_works():
    state = cast_ha_lac(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    luan = compose_ha_lac_luan_giai(state, current_age=None)
    tj = luan["trajectory_luan"]
    assert tj["current"] is None
    current_stages = [s for s in tj["stages"] if s["is_current"]]
    assert len(current_stages) == 0


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tien_thien_quai"):
        compose_ha_lac_luan_giai({}, current_age=30)


def test_female_chart_works():
    state = cast_ha_lac(
        birth_datetime_local="1995-08-15T14:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    luan = compose_ha_lac_luan_giai(state, current_age=30)
    assert luan["method_id"]
    assert luan["tien_thien_luan"]["king_wen"]


def test_nguyen_duong_phase_label(founder_luan):
    assert founder_luan["tien_thien_luan"]["nguyen_duong_phase"]
    assert founder_luan["hau_thien_luan"]["nguyen_duong_phase"]


def test_each_stage_has_phase_label(founder_luan):
    tj = founder_luan["trajectory_luan"]
    for s in tj["stages"]:
        assert s["phase_label"]


def test_yang_yao_9_years(founder_luan):
    for s in founder_luan["trajectory_luan"]["stages"]:
        if s["polarity"] == "yang":
            assert s["years_span"] == 9
        else:
            assert s["years_span"] == 6


def test_bo_huong_present(founder_luan):
    assert founder_luan["bo_huong_stage"]
    assert len(founder_luan["bo_huong_stage"]) > 50


def test_closing_paradigm(founder_luan):
    closing = founder_luan["closing"]
    assert "Học Năng" in closing
    assert "MỆNH" in closing.upper() or "Mệnh" in closing
