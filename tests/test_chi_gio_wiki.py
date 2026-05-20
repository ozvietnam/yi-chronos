"""Tests for chi giờ wiki loader API."""
import pytest

from engine.yi_wiki.chi_gio_wiki import (
    list_chi, get_chi, get_bordering, get_thirds, get_questions, get_all_chi,
)


def test_get_chi_ty_full_data():
    ty = get_chi("Tý")
    assert ty["id"] == "Tý"
    assert ty["ngu_hanh"] == "Thuỷ"
    assert ty["tcm_organ"] == "thận"
    assert ty["wraps_midnight"] is True
    assert ty["range_hours"] == [23, 1]


def test_get_chi_core_traits():
    ty = get_chi("Tý")
    for domain in ("personality", "physical", "daily_habit"):
        assert domain in ty["core_traits"]
        assert len(ty["core_traits"][domain]) >= 3


def test_get_bordering():
    bd = get_bordering("Tý")
    assert bd["previous"]["chi"] == "Hợi"
    assert bd["next"]["chi"] == "Sửu"
    assert "Phúc hậu, hiền hoà" in bd["previous"]["leak_traits"]


def test_get_thirds_three_subdivisions():
    th = get_thirds("Tý")
    assert set(th.keys()) == {"early", "middle", "late"}
    assert th["early"]["range"] == "23:00-23:30"
    assert "Hợi" in th["early"]["label"]
    assert "Sửu" in th["late"]["label"]


def test_get_questions_by_neighbor():
    qs_early = get_questions("Tý", "vs_Hoi_early")
    assert len(qs_early) >= 5
    for q in qs_early:
        assert "id" in q
        assert "situation" in q
        assert "options" in q
        assert set(q["options"].keys()) == {"A", "B"}


def test_get_chi_unknown_raises():
    with pytest.raises((KeyError, FileNotFoundError)):
        get_chi("NonExistent")


def test_list_chi_returns_loaded_only():
    """Should return list of all chi that have data files (Wiki-1 = only Tý)."""
    chis = list_chi()
    assert "Tý" in chis
