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


from engine.yi_wiki.birth_hour_quiz_v2.rules.branches import (
    BRANCH_ELEMENTS, HOUR_RANGES, TCM_ORGAN, hour_to_chi
)


def test_branch_elements():
    assert len(BRANCH_ELEMENTS) == 12
    assert BRANCH_ELEMENTS["Tý"] == "Thuỷ"
    assert BRANCH_ELEMENTS["Hợi"] == "Thuỷ"
    assert BRANCH_ELEMENTS["Ngọ"] == "Hoả"


def test_hour_ranges_cover_24h():
    total = 0
    for chi, (start, end) in HOUR_RANGES.items():
        span = (end - start) % 24 or 24
        # Tý wraps midnight → span = 2 (23→1)
        if start > end:
            span = (24 - start) + end
        assert span == 2, f"{chi} span should be 2h, got {span}"
        total += span
    assert total == 24


def test_tcm_organ_clock():
    assert TCM_ORGAN["Tý"] == "thận"
    assert TCM_ORGAN["Ngọ"] == "tâm"


def test_hour_to_chi():
    assert hour_to_chi(23) == "Tý"
    assert hour_to_chi(0) == "Tý"
    assert hour_to_chi(8) == "Thìn"
    assert hour_to_chi(12) == "Ngọ"
