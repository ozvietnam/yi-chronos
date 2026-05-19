"""Tests for Domain 3 energy traits derivation (TCM clock)."""
from engine.yi_wiki.birth_hour_quiz_v2.rules.energy import derive_energy_traits


def test_derive_energy_returns_3_traits():
    out = derive_energy_traits({"hour": {"branch": "Mão"}})
    assert set(out.keys()) == {"wake_natural_time", "energy_peak_period", "sleep_pattern"}


def test_mao_morning_person():
    """Mão hour (5-7h) → wake early, peak morning."""
    out = derive_energy_traits({"hour": {"branch": "Mão"}})
    assert out["wake_natural_time"] == "5_7h"
    assert out["energy_peak_period"] == "sang"


def test_ty_night_owl():
    """Tý hour (23-1h) → late sleep, peak late."""
    out = derive_energy_traits({"hour": {"branch": "Tý"}})
    assert out["sleep_pattern"] == "sau_1h"
    assert out["energy_peak_period"] == "dem"


def test_ngo_noon_peak():
    """Ngọ hour (11-13h) → peak noon."""
    out = derive_energy_traits({"hour": {"branch": "Ngọ"}})
    assert out["energy_peak_period"] == "trua"
