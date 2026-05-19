"""Tests for engine.bat_tu.cach_cuc — Bát Tự pattern classifier."""

from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu
from engine.bat_tu.cach_cuc import (
    CACH_DETAILS,
    THAP_THAN_TO_CACH,
    classify_cach_cuc,
)


def test_thap_than_to_cach_covers_8_canonical():
    """8 standard Thập Thần map to 8 cách cục."""
    expected_keys = {
        "Chính Quan", "Thất Sát", "Chính Tài", "Thiên Tài",
        "Thực Thần", "Thương Quan", "Chính Ấn", "Thiên Ấn",
    }
    assert expected_keys.issubset(set(THAP_THAN_TO_CACH.keys()))


def test_cach_details_complete():
    """Every entry in THAP_THAN_TO_CACH should have details."""
    for cach in THAP_THAN_TO_CACH.values():
        assert cach in CACH_DETAILS
        d = CACH_DETAILS[cach]
        assert d["essence"]
        assert d["favorable"]


def test_classify_cach_cuc_with_known_chart():
    """1985-08-15 chart: Day Master Kỷ, Month Mùi.
    Mùi tàng can: (Kỷ, Đinh, Ất). Bản khí = Kỷ.
    Kỷ vs Kỷ = same stem → Kiến Lộc cách (special).
    """
    pillars = {
        "year":  {"stem": "Ất",  "branch": "Sửu"},
        "month": {"stem": "Quý", "branch": "Mùi"},
        "day":   {"stem": "Kỷ",  "branch": "Tỵ"},
        "hour":  {"stem": "Kỷ",  "branch": "Tỵ"},
    }
    r = classify_cach_cuc(pillars, "Kỷ")
    assert "Kiến Lộc" in r["cach_name"]


def test_classify_cach_cuc_chinh_quan_example():
    """Chart with month branch giving Chính Quan."""
    # Day Master Giáp (mộc dương). For Chính Quan = Tân (kim âm khắc Giáp).
    # Need month branch with Tân as primary hidden stem → Dậu (tàng Tân only).
    pillars = {
        "year":  {"stem": "Mậu", "branch": "Dần"},
        "month": {"stem": "Tân", "branch": "Dậu"},
        "day":   {"stem": "Giáp", "branch": "Tý"},
        "hour":  {"stem": "Giáp", "branch": "Tý"},
    }
    r = classify_cach_cuc(pillars, "Giáp")
    assert "Chính Quan" in r["cach_name"]
    assert r["based_on_thap_than"] == "Chính Quan"


def test_classify_cach_cuc_returns_dict():
    pillars = {
        "year":  {"stem": "Ất",  "branch": "Sửu"},
        "month": {"stem": "Quý", "branch": "Mùi"},
        "day":   {"stem": "Kỷ",  "branch": "Tỵ"},
        "hour":  {"stem": "Kỷ",  "branch": "Tỵ"},
    }
    r = classify_cach_cuc(pillars, "Kỷ")
    assert isinstance(r, dict)
    assert "cach_name" in r
    assert "polarity" in r
    assert "essence" in r
    assert "favorable" in r
    assert "ky" in r


def test_cast_bat_tu_includes_cach_cuc():
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="nam")
    assert "cach_cuc" in r
    cc = r["cach_cuc"]
    assert "Kiến Lộc" in cc["cach_name"] or cc["cach_name"] != "Không xác định"
