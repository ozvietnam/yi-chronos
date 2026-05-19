"""Tests for Heavenly Stems + Earthly Branches tables (quiz v2 rules)."""
from engine.yi_wiki.birth_hour_quiz_v2.rules.stems import (
    STEM_ELEMENTS, STEM_YIN_YANG, DAY_MASTER_BASELINE
)


def test_stem_elements_complete():
    assert len(STEM_ELEMENTS) == 10
    assert STEM_ELEMENTS["Giáp"] == "Mộc"
    assert STEM_ELEMENTS["Quý"] == "Thuỷ"


def test_stem_yin_yang():
    assert STEM_YIN_YANG["Giáp"] == "Dương"
    assert STEM_YIN_YANG["Ất"] == "Âm"


def test_day_master_baseline_giap():
    bl = DAY_MASTER_BASELINE["Giáp"]
    assert bl["body_height"] == "cao"
    assert bl["body_build"] == "gay_thon"
    assert bl["skin_tone"] == "trang"
