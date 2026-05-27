"""Tests for engine.bat_tu.luc_than — 6 family relations analysis."""
from __future__ import annotations

import pytest

from engine.bat_tu import analyze_luc_than, cast_bat_tu


@pytest.fixture
def founder_state():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


@pytest.fixture
def founder_lt(founder_state):
    return analyze_luc_than(founder_state)


def test_method_id(founder_lt):
    assert founder_lt["method_id"] == "bat_tu_luc_than_v1"


def test_paradigm(founder_lt):
    assert "KHÔNG dự đoán" in founder_lt["paradigm_guard"]


def test_all_sections(founder_lt):
    required = ["method_id", "paradigm_guard", "gender",
                "pillar_overview", "relations", "closing"]
    for k in required:
        assert k in founder_lt


def test_founder_nam_has_7_relations(founder_lt):
    """Nam có 7 quan hệ Lục Thân (Cha+Mẹ+Anh chị em+Vợ chính+Vợ lẽ+Con trai+Con gái)."""
    assert len(founder_lt["relations"]) == 7
    names = [r["name"] for r in founder_lt["relations"]]
    assert "Cha" in names
    assert "Mẹ" in names
    assert "Vợ chính" in names


def test_founder_father_strong(founder_lt):
    """Founder có 4 Thiên Tài (Mậu thổ) → Cha strong."""
    cha = next(r for r in founder_lt["relations"] if r["name"] == "Cha")
    assert cha["strength"] == "strong"
    assert len(cha["positions"]) >= 3


def test_founder_vo_chinh_absent(founder_lt):
    """Founder không có Chính Tài → Vợ chính absent."""
    vo = next(r for r in founder_lt["relations"] if r["name"] == "Vợ chính")
    assert vo["strength"] == "absent"


def test_female_chart_relations():
    """Nữ chart có Chồng/Tình cảm phụ thay vì Vợ."""
    state = cast_bat_tu(
        birth_datetime_local="1990-03-15T10:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nữ",
    )
    lt = analyze_luc_than(state)
    names = {r["name"] for r in lt["relations"]}
    assert "Chồng" in names
    assert "Vợ chính" not in names


def test_pillar_overview_4_pillars(founder_lt):
    assert len(founder_lt["pillar_overview"]) == 4
    labels = {p["label"] for p in founder_lt["pillar_overview"]}
    assert labels == {"Trụ Năm", "Trụ Tháng", "Trụ Ngày", "Trụ Giờ"}


def test_invalid_state_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        analyze_luc_than({})


def test_each_relation_has_narrative(founder_lt):
    for r in founder_lt["relations"]:
        assert r.get("narrative")
        assert len(r["narrative"]) > 50
