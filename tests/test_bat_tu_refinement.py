"""Tests for Bát Tự refinement: Dụng Thần heuristic + accurate starting age."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from engine.bat_tu import cast_bat_tu
from engine.bat_tu.dung_than import (
    DungThan,
    classify_elements_role,
    determine_dung_than,
)
from engine.bat_tu.starting_age import (
    compute_starting_age,
    next_tiet_khi_date,
    prev_tiet_khi_date,
)


# ─── Dụng Thần heuristic ──────────────────────────────────────────────────────


def test_classify_elements_role_for_thuy_day_master():
    """Day Master thủy: roles relative to it."""
    roles = classify_elements_role("thủy")
    # Self: thủy
    assert roles["thủy"] == "self"
    # Seal: element that generates thủy = kim
    assert roles["kim"] == "seal"
    # Output: element thủy generates = mộc
    assert roles["mộc"] == "output"
    # Wealth: element thủy controls = hỏa
    assert roles["hỏa"] == "wealth"
    # Pressure: element that controls thủy = thổ
    assert roles["thổ"] == "pressure"


def test_classify_elements_role_for_tho_day_master():
    """Day Master thổ: roles."""
    roles = classify_elements_role("thổ")
    assert roles["thổ"] == "self"
    assert roles["hỏa"] == "seal"        # hỏa sinh thổ
    assert roles["kim"] == "output"      # thổ sinh kim
    assert roles["thủy"] == "wealth"     # thổ khắc thủy
    assert roles["mộc"] == "pressure"    # mộc khắc thổ


def test_determine_dung_than_strong_picks_drain_element():
    """Strong DM should pick wealth/output/pressure as Dụng Thần."""
    counts = {"kim": 0.5, "mộc": 2.0, "thủy": 0.3, "hỏa": 3.0, "thổ": 5.0}
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=counts,
        strength_tag="strong",
    )
    # For strong thổ, drain options: mộc (pressure), thủy (wealth), kim (output).
    # Mộc has count 2.0 — highest → wins.
    assert dt.dung_than_element == "mộc"
    assert dt.dung_than_role == "pressure"


def test_determine_dung_than_weak_picks_support_element():
    """Weak DM should pick seal/self as Dụng Thần."""
    counts = {"kim": 0.2, "mộc": 0.3, "thủy": 0.5, "hỏa": 1.5, "thổ": 0.8}
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=counts,
        strength_tag="weak",
    )
    # Weak thổ: seal=hỏa (count 1.5), self=thổ (count 0.8). hỏa wins.
    assert dt.dung_than_element == "hỏa"
    assert dt.dung_than_role == "seal"


def test_determine_dung_than_balanced_uses_month_branch():
    """Balanced DM with month branch hint should prefer that element."""
    counts = {"kim": 1, "mộc": 1, "thủy": 1, "hỏa": 1, "thổ": 2}
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=counts,
        strength_tag="balanced",
        month_branch_element="hỏa",
    )
    assert dt.dung_than_element == "hỏa"


def test_dung_than_returns_dataclass_with_dict_serialization():
    counts = {"kim": 1, "mộc": 1, "thủy": 1, "hỏa": 1, "thổ": 1}
    dt = determine_dung_than(
        day_element="thủy", element_counts=counts, strength_tag="strong",
    )
    assert isinstance(dt, DungThan)
    d = dt.to_dict()
    assert "dung_than_element" in d
    assert "hy_than_element" in d
    assert "ky_than_element" in d
    assert "all_roles" in d
    assert len(d["all_roles"]) == 5


# ─── Starting age (accurate via tiết khí) ─────────────────────────────────────


def test_next_tiet_khi_after_birth():
    """For a birth on a known date, next tiết khí must be within ~30 days."""
    birth = datetime(1985, 8, 15, 10, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    nxt = next_tiet_khi_date(birth)
    delta_days = (nxt - birth).total_seconds() / 86400
    assert 0 < delta_days < 32   # within ~1 month


def test_prev_tiet_khi_before_birth():
    birth = datetime(1985, 8, 15, 10, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    prv = prev_tiet_khi_date(birth)
    delta_days = (birth - prv).total_seconds() / 86400
    assert 0 < delta_days < 32


def test_compute_starting_age_forward():
    """For thuận direction: age based on distance to NEXT tiết khí."""
    birth = datetime(1985, 8, 15, 10, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    sa = compute_starting_age(birth, direction=+1)
    assert 1 <= sa["starting_age"] <= 10
    assert sa["estimation_method"] == "tiet_khi_3day_rule"
    assert sa["distance_days"] > 0


def test_compute_starting_age_backward():
    """For nghịch direction: age based on distance to PREVIOUS tiết khí."""
    birth = datetime(1985, 8, 15, 10, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    sa = compute_starting_age(birth, direction=-1)
    assert 1 <= sa["starting_age"] <= 10
    # 1985-08-15 → previous tiết khí ~ Lập Thu (Aug 7-8) → ~10 days → age 3.
    assert sa["starting_age"] == 3


def test_compute_starting_age_clamps_to_1_10():
    """Result must always be in [1, 10]."""
    # Birth right on a tiết khí — distance ≈ 0 days.
    birth = datetime(1985, 8, 7, 12, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    sa = compute_starting_age(birth, direction=+1)
    assert 1 <= sa["starting_age"] <= 10


# ─── Integration via cast_bat_tu ──────────────────────────────────────────────


def test_cast_bat_tu_includes_dung_than():
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    assert "dung_than" in r
    dt = r["dung_than"]
    assert dt["dung_than_element"] in ("kim", "mộc", "thủy", "hỏa", "thổ")
    assert dt["hy_than_element"] in ("kim", "mộc", "thủy", "hỏa", "thổ")
    assert dt["ky_than_element"] in ("kim", "mộc", "thủy", "hỏa", "thổ")


def test_cast_bat_tu_uses_accurate_starting_age():
    """When birth_datetime_local is passed, Đại Vận should use tiết khí computation."""
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    dv = r["dai_van"]
    assert dv["starting_age_estimation"] == "tiet_khi_3day_rule"
    assert dv["distance_days_to_reference_tiet_khi"] is not None
    assert dv["reference_tiet_khi_date"] is not None
    # For 1985-08-15 nam, year stem Ất (yin) + nam → nghịch → use previous tiết khí.
    # Previous tiết khí is Lập Thu (Aug 7-8) — distance ~10 days → starting age 3.
    assert dv["direction_label"] == "nghịch"
    assert dv["starting_age"] == 3


def test_cast_bat_tu_dung_than_strong_for_known_chart():
    """1985-08-15 Kỷ thổ Day Master — chart has lots of thổ (Sửu, Mùi, Tỵ, Tỵ) → strong."""
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    assert r["dung_than"]["strength_tag"] == "strong"
    # Pressure element (controls thổ) = mộc.
    # Wealth element (thổ controls) = thủy.
    # Output element (thổ generates) = kim.
    # Drain candidates by priority: pressure → wealth → output.
    # In this chart mộc count = 1.3, thủy = 1.3, kim = 0.9 → pressure (mộc) wins by tie-breaking priority.
    assert r["dung_than"]["dung_than_element"] == "mộc"
