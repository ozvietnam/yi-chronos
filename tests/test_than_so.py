"""Tests for engine.than_so — Pythagoras (Decoz P0)."""
from __future__ import annotations

import pytest

from engine.than_so import (
    cast_than_so,
    compute_core,
    compute_extended,
    cross_bind_dong_phuong,
    life_path,
    normalize_vietnamese,
    personal_day,
    personal_month,
    personal_year,
    pinnacles_and_challenges,
    reduce_number,
)
from engine.than_so.core_numbers import reduce_with_trace
from engine.than_so.cycles import period_cycles
from engine.than_so.name_parts import split_name_parts


# ─── Reduce + master ──────────────────────────────────────────────────────────


def test_reduce_basic():
    assert reduce_number(28) == 1
    assert reduce_number(17) == 8


def test_reduce_keeps_master():
    assert reduce_number(11) == 11
    assert reduce_number(29) == 11
    assert reduce_number(33) == 33


def test_reduce_no_master_when_disabled():
    assert reduce_number(11, keep_master=False) == 2


# ─── Vietnamese normalize ─────────────────────────────────────────────────────


def test_normalize_strips_diacritics_and_d():
    assert normalize_vietnamese("Nguyễn Văn An") == "NGUYEN VAN AN"
    assert normalize_vietnamese("Đỗ Thị Hương") == "DO THI HUONG"


def test_normalize_no_consonant_cluster_split():
    assert normalize_vietnamese("Nguyễn").replace(" ", "") == "NGUYEN"


# ─── Decoz golden Life Path fixtures ─────────────────────────────────────────


def test_life_path_journal_example():
    lp = life_path(23, 11, 1990)
    assert lp["value"] == 8
    assert lp["components"]["month"] == 11


def test_life_path_decoz_aug_12_1990():
    # Decoz: 8 + 3 + 1 = 12 → 3
    lp = life_path(12, 8, 1990)
    assert lp["value"] == 3


def test_life_path_decoz_nov_22_1983():
    # 11 + 22 + 3 = 36 → 9
    lp = life_path(22, 11, 1983)
    assert lp["value"] == 9
    assert lp["components"]["month"] == 11
    assert lp["components"]["day"] == 22


def test_life_path_karmic_16_oct_15_1998():
    # Method A: 1 + 6 + 9 = 16 → 7 (shortcut 34 would hide 16)
    lp = life_path(15, 10, 1998)
    assert lp["value"] == 7
    assert lp["karmic_debt"] == 16


# ─── Name numbers ─────────────────────────────────────────────────────────────


def test_expression_john_pythagorean():
    core = compute_core("John", 1, 1, 2000, system="pythagorean", name_order="western")
    assert core["expression"]["value"] == 2


def test_soul_and_personality_split():
    core = compute_core("John", 1, 1, 2000, system="pythagorean", name_order="western")
    assert core["soul_urge"]["value"] == 6
    assert core["personality"]["value"] == 5


def test_expression_per_name_part_has_parts():
    core = compute_core("Nguyễn Văn An", 1, 1, 2000, name_order="vn")
    assert len(core["expression"]["parts"]) == 3
    assert core["name_parts"]["first_name"] == "AN"
    assert core["name_parts"]["last_name"] == "NGUYEN"


def test_name_order_vn_vs_western():
    vn = split_name_parts("Nguyễn Văn An", "vn")
    western = split_name_parts("An Van Nguyen", "western")
    assert vn["first_name"] == "AN"
    assert western["first_name"] == "AN"
    assert vn["last_name"] == "NGUYEN"


def test_chaldean_system_still_works():
    ch = compute_core("John", 1, 1, 2000, system="chaldean", name_order="western")
    assert 1 <= ch["expression"]["value"] <= 33


# ─── Karmic + Challenges ──────────────────────────────────────────────────────


def test_karmic_debt_trace():
    t = reduce_with_trace(13)
    assert t["reduced"] == 4
    assert t["karmic_debt"] == 13


def test_pinnacles_formula():
    pc = pinnacles_and_challenges(23, 11, 1990)
    m, d, y = 11, 5, 1
    p = [x["value"] for x in pc["pinnacles"]]
    assert p[0] == reduce_number(m + d)
    assert p[1] == reduce_number(d + y)
    assert p[3] == reduce_number(m + y)
    assert pc["challenges"][2]["main"] is True


def test_challenges_reduce_master_before_subtract():
    # Month 11 → challenge unit 2 (not 11)
    pc = pinnacles_and_challenges(23, 11, 1990)
    # c1 = |2 - 5| = 3
    assert pc["challenges"][0]["value"] == 3


def test_period_cycle_second_is_27_years():
    periods = period_cycles(23, 11, 1990)
    assert periods[1]["duration_years"] == 27
    # LP 8 → p1_end = 36-8 = 28; p2_end = 28+27 = 55
    assert periods[0]["age_end"] == 28
    assert periods[1]["age_end"] == 55


# ─── Extended ─────────────────────────────────────────────────────────────────


def test_extended_attitude_and_lessons():
    core = compute_core("Nguyễn Văn An", 23, 11, 1990)
    ext = compute_extended("Nguyễn Văn An", 23, 11, core, name_order="vn")
    # Attitude: month 11 + day 5 = 16 → 7
    assert ext["attitude"]["value"] == 7
    assert "values" in ext["karmic_lessons"]
    assert "life_path_expression" in ext["bridges"]
    assert "physical" in ext["planes_of_expression"]["planes"]


def test_extended_minor_from_current_name():
    core = compute_core("Nguyễn Văn An", 23, 11, 1990)
    ext = compute_extended(
        "Nguyễn Văn An", 23, 11, core, current_name="An", name_order="vn"
    )
    assert ext["minor"] is not None
    assert ext["minor"]["expression"]["value"] >= 1


def test_personal_month_day():
    py = personal_year(15, 5, 2026)
    assert py["value"] == 3  # Decoz: 5+6+1? 5+15→6 + 2026→10→1 = 5+6+1=12→3
    pm = personal_month(15, 5, 2026, 2)
    assert 1 <= pm["value"] <= 9
    pd = personal_day(15, 5, 2026, 2, 3)
    assert 1 <= pd["value"] <= 9


# ─── Cast E2E ─────────────────────────────────────────────────────────────────


def test_cast_full_chart_p0():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", target_year=2026, current_name="An")
    assert res["schema_version"] == "v2"
    assert res["core"]["life_path"]["value"] == 8
    assert "extended" in res
    assert res["extended"]["attitude"]["value"] == 7
    assert "personal_month" in res["cycles"]
    assert "personal_day" in res["cycles"]
    assert "essence" in res["cycles"]
    assert "transits" in res["cycles"]
    assert res["cross_reference"]["system"] == "chaldean"
    assert "dong_phuong_doi_chieu" not in res  # default off
    assert "predict" not in res["reading"]["paradigm_note"].lower()


def test_cast_dong_phuong_opt_in():
    res = cast_than_so("Nguyễn Văn An", "1990-11-23", include_dong_phuong=True)
    assert "dong_phuong_doi_chieu" in res


def test_cast_rejects_bad_date():
    with pytest.raises(ValueError):
        cast_than_so("Test", "23-11-1990")


def test_cast_rejects_empty_name():
    with pytest.raises(ValueError):
        cast_than_so("  ", "1990-11-23")


# ─── Cross-bind (opt-in, kept for regression) ─────────────────────────────────


def test_cross_bind_number_3_strong_consensus():
    cb = cross_bind_dong_phuong(3)
    assert "Mộc" in cb["consensus_ngu_hanh"]


def test_cross_bind_number_9_divergence_not_forced():
    cb = cross_bind_dong_phuong(9)
    assert cb["divergence"] is True
