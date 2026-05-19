"""Tests for rule-derived personality traits (yin-yang ratio + sibling hint)."""
from engine.yi_wiki.birth_hour_quiz_v2.rules.personality import (
    derive_yin_yang_ratio, derive_sibling_position_hint,
)


def test_all_yang_stems_extrovert():
    pillars = {
        "year":  {"stem": "Giáp", "branch": "Tý"},
        "month": {"stem": "Bính", "branch": "Tý"},
        "day":   {"stem": "Mậu",  "branch": "Tý"},
        "hour":  {"stem": "Canh", "branch": "Tý"},
    }
    assert derive_yin_yang_ratio(pillars) == "mostly_extro"


def test_all_yin_stems_introvert():
    pillars = {
        "year":  {"stem": "Ất",   "branch": "Sửu"},
        "month": {"stem": "Đinh", "branch": "Sửu"},
        "day":   {"stem": "Kỷ",   "branch": "Sửu"},
        "hour":  {"stem": "Tân",  "branch": "Sửu"},
    }
    assert derive_yin_yang_ratio(pillars) == "mostly_intro"


def test_mixed_yin_yang_mid():
    pillars = {
        "year":  {"stem": "Giáp", "branch": "Tý"},
        "month": {"stem": "Ất",   "branch": "Sửu"},
        "day":   {"stem": "Bính", "branch": "Tý"},
        "hour":  {"stem": "Đinh", "branch": "Sửu"},
    }
    assert derive_yin_yang_ratio(pillars) == "mid"


def test_sibling_position_ca_year_chi():
    """Year chi = Tý/Ngọ/Mão/Dậu (đào hoa) → ca."""
    assert derive_sibling_position_hint({"year": {"branch": "Mão"}}) == "ca"
    assert derive_sibling_position_hint({"year": {"branch": "Tý"}}) == "ca"


def test_sibling_position_giua_year_chi():
    """Year chi = Dần/Thân/Tỵ/Hợi → giua."""
    assert derive_sibling_position_hint({"year": {"branch": "Dần"}}) == "giua"


def test_sibling_position_ut_year_chi():
    """Year chi = Thìn/Tuất/Sửu/Mùi → ut."""
    assert derive_sibling_position_hint({"year": {"branch": "Thìn"}}) == "ut"
