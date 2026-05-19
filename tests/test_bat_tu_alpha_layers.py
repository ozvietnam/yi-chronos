"""Tests for Bát Tự α layers: Trường Sinh + Thần Sát + Đại Vận."""

from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu
from engine.bat_tu.dai_van import (
    JIAZI_CYCLE,
    compute_dai_van,
    compute_tieu_van,
    determine_direction,
)
from engine.bat_tu.than_sat import detect_than_sat
from engine.bat_tu.truong_sinh import (
    PHASE_STRENGTH,
    TRUONG_SINH_PHASES,
    compute_truong_sinh_chart,
    phase_of_branch,
)


# ─── Vòng Trường Sinh ─────────────────────────────────────────────────────────


def test_truong_sinh_phases_count_is_12():
    assert len(TRUONG_SINH_PHASES) == 12


def test_truong_sinh_giap_yang_walks_forward():
    """Giáp (yang mộc) starts at Hợi, walks forward."""
    assert phase_of_branch("Giáp", "Hợi") == "Trường Sinh"
    assert phase_of_branch("Giáp", "Tý") == "Mộc Dục"
    assert phase_of_branch("Giáp", "Sửu") == "Quan Đới"
    assert phase_of_branch("Giáp", "Mão") == "Đế Vượng"


def test_truong_sinh_at_yin_walks_backward():
    """Ất (yin mộc) starts at Ngọ, walks backward."""
    assert phase_of_branch("Ất", "Ngọ") == "Trường Sinh"
    assert phase_of_branch("Ất", "Tỵ") == "Mộc Dục"
    assert phase_of_branch("Ất", "Thìn") == "Quan Đới"


def test_truong_sinh_canh_yang_starts_at_ty():
    """Canh (yang kim) starts at Tỵ."""
    assert phase_of_branch("Canh", "Tỵ") == "Trường Sinh"
    assert phase_of_branch("Canh", "Dậu") == "Đế Vượng"


def test_truong_sinh_ky_yin_starts_at_dau():
    """Kỷ (yin thổ) starts at Dậu, walks backward."""
    assert phase_of_branch("Kỷ", "Dậu") == "Trường Sinh"
    assert phase_of_branch("Kỷ", "Tỵ") == "Đế Vượng"


def test_phase_strength_covers_all_phases():
    for phase in TRUONG_SINH_PHASES:
        assert phase in PHASE_STRENGTH


def test_compute_truong_sinh_chart_returns_4_pillars():
    pillars = {
        "year":  {"stem": "Ất", "branch": "Sửu", "position_vi": "Trụ Năm"},
        "month": {"stem": "Quý", "branch": "Mùi", "position_vi": "Trụ Tháng"},
        "day":   {"stem": "Kỷ", "branch": "Tỵ", "position_vi": "Trụ Ngày"},
        "hour":  {"stem": "Kỷ", "branch": "Tỵ", "position_vi": "Trụ Giờ"},
    }
    chart = compute_truong_sinh_chart(pillars, day_master_stem="Kỷ")
    assert chart["day_master_stem"] == "Kỷ"
    assert chart["truong_sinh_start_branch"] == "Dậu"
    assert set(chart["pillars"].keys()) == {"year", "month", "day", "hour"}
    # Day & hour both Tỵ → Đế Vượng for Kỷ (yin walking backward from Dậu).
    assert chart["pillars"]["day"]["phase"] == "Đế Vượng"
    assert chart["pillars"]["hour"]["phase"] == "Đế Vượng"


# ─── Thần Sát ─────────────────────────────────────────────────────────────────


def test_than_sat_returns_list():
    pillars = {
        "year":  {"stem": "Ất", "branch": "Sửu"},
        "month": {"stem": "Quý", "branch": "Mùi"},
        "day":   {"stem": "Kỷ", "branch": "Tỵ"},
        "hour":  {"stem": "Kỷ", "branch": "Tỵ"},
    }
    stars = detect_than_sat(pillars, "Kỷ")
    assert isinstance(stars, list)
    # Should detect Dương Nhận twice (Tỵ in day + hour) for Kỷ stem.
    duong_nhan = [s for s in stars if s["name"] == "Dương Nhận"]
    assert len(duong_nhan) == 2


def test_than_sat_thien_at_quy_nhan_detection():
    """Day stem Giáp → Thiên Ất Quý Nhân branches are Sửu and Mùi."""
    pillars = {
        "year":  {"stem": "Bính", "branch": "Sửu"},
        "month": {"stem": "Đinh", "branch": "Mùi"},
        "day":   {"stem": "Giáp", "branch": "Tý"},
        "hour":  {"stem": "Mậu", "branch": "Thìn"},
    }
    stars = detect_than_sat(pillars, "Giáp")
    quy_nhan = [s for s in stars if s["name"] == "Thiên Ất Quý Nhân"]
    assert len(quy_nhan) >= 2   # Sửu in year + Mùi in month


def test_than_sat_returns_dicts():
    pillars = {
        "year":  {"stem": "Giáp", "branch": "Tý"},
        "month": {"stem": "Bính", "branch": "Dần"},
        "day":   {"stem": "Mậu", "branch": "Thân"},
        "hour":  {"stem": "Canh", "branch": "Thân"},
    }
    stars = detect_than_sat(pillars, "Mậu")
    for s in stars:
        assert isinstance(s, dict)
        assert "name" in s and "polarity" in s
        assert s["polarity"] in ("lành", "dữ", "trung tính")


# ─── Đại Vận ──────────────────────────────────────────────────────────────────


def test_jiazi_cycle_has_60_entries():
    assert len(JIAZI_CYCLE) == 60
    # First entry must be Giáp Tý.
    assert JIAZI_CYCLE[0] == ("Giáp", "Tý")
    # Last entry must be Quý Hợi.
    assert JIAZI_CYCLE[59] == ("Quý", "Hợi")


def test_determine_direction_yang_male_forward():
    """Dương Nam → thuận (+1). Year stem Giáp = yang."""
    assert determine_direction("Giáp", "nam") == +1


def test_determine_direction_yin_male_backward():
    """Âm Nam → nghịch (-1). Year stem Ất = yin."""
    assert determine_direction("Ất", "nam") == -1


def test_determine_direction_yin_female_forward():
    """Âm Nữ → thuận."""
    assert determine_direction("Ất", "nữ") == +1


def test_determine_direction_yang_female_backward():
    """Dương Nữ → nghịch."""
    assert determine_direction("Giáp", "nữ") == -1


def test_compute_dai_van_returns_8_cycles_by_default():
    cycles = compute_dai_van(
        month_pillar_stem="Quý",
        month_pillar_branch="Mùi",
        year_stem="Ất",
        gender="nam",
        starting_age=7,
    )
    assert len(cycles) == 8
    # First cycle: backward from Quý Mùi → Nhâm Ngọ
    assert cycles[0]["stem"] == "Nhâm"
    assert cycles[0]["branch"] == "Ngọ"
    assert cycles[0]["start_age"] == 7
    assert cycles[0]["end_age"] == 16


def test_compute_dai_van_forward_direction():
    """Dương Nam (Giáp + nam) → forward."""
    cycles = compute_dai_van(
        month_pillar_stem="Bính",
        month_pillar_branch="Dần",
        year_stem="Giáp",
        gender="nam",
        starting_age=3,
    )
    # First cycle forward from Bính Dần → Đinh Mão
    assert cycles[0]["stem"] == "Đinh"
    assert cycles[0]["branch"] == "Mão"


def test_compute_tieu_van_starts_at_ty_for_male():
    """Tiểu Vận for nam starts at Tỵ."""
    tv = compute_tieu_van("Sửu", "nam")
    assert tv[0]["branch"] == "Tỵ"
    assert tv[0]["age"] == 1


def test_compute_tieu_van_starts_at_than_for_female():
    tv = compute_tieu_van("Sửu", "nữ")
    assert tv[0]["branch"] == "Thân"


# ─── Top-level cast integration ───────────────────────────────────────────────


def test_cast_bat_tu_includes_alpha_layers():
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    assert "truong_sinh" in r
    assert "than_sat" in r
    assert "dai_van" in r
    assert len(r["truong_sinh"]["pillars"]) == 4
    assert isinstance(r["than_sat"], list)
    assert len(r["dai_van"]["cycles"]) == 8


def test_cast_bat_tu_dai_van_direction_for_known_chart():
    """1985 birth — year stem Ất is yin → nam should walk backward (nghịch)."""
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    assert r["dai_van"]["direction"] == -1
    assert r["dai_van"]["direction_label"] == "nghịch"


def test_cast_bat_tu_no_longer_lists_deferred_alpha_layers():
    """After refinement, α layers AND Dụng Thần / starting-age are all live."""
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    # Live layers
    assert "truong_sinh" in r
    assert "than_sat" in r
    assert "dai_van" in r
    assert "dung_than" in r
    # Starting age now uses real tiết khí
    assert r["dai_van"]["starting_age_estimation"] == "tiet_khi_3day_rule"
