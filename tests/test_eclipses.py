from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.eclipses import compute_eclipses


@pytest.fixture(scope="module")
def eclipses():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_eclipses(birth, lat=21.0285, lon=105.8542, span_years=60, only_activated=True)


def test_returns_nonempty(eclipses):
    assert len(eclipses) > 5


def test_sorted_by_age(eclipses):
    ages = [e.age_years for e in eclipses]
    assert ages == sorted(ages)


def test_only_activated_have_activations(eclipses):
    for e in eclipses:
        assert len(e.activations) > 0


def test_eclipse_types_valid(eclipses):
    for e in eclipses:
        assert e.eclipse_type in {"solar", "lunar"}
        if e.eclipse_type == "solar":
            assert e.eclipse_subtype in {"total_or_annular", "partial"}
        else:
            assert e.eclipse_subtype in {"total", "partial", "penumbral"}


def test_lat_within_threshold(eclipses):
    for e in eclipses:
        if e.eclipse_type == "solar":
            assert abs(e.moon_latitude) <= 1.5
        else:
            assert abs(e.moon_latitude) <= 1.0


def test_activation_orbs_within_limits(eclipses):
    for e in eclipses:
        for a in e.activations:
            assert a.orb_deg <= 6.0
            assert a.importance in {"major", "medium", "minor"}


def test_known_2024_eclipse_falls_in_aries_or_pisces():
    """The Apr 8, 2024 total solar eclipse was in Aries 19°.
    For someone born 1985-07-20, age would be ~38.7 years."""
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    all_eclipses = compute_eclipses(birth, lat=21.0285, lon=105.8542, span_years=40, only_activated=False)
    near_2024_apr = [e for e in all_eclipses if "2024-04" in e.date_utc and e.eclipse_type == "solar"]
    assert len(near_2024_apr) >= 1
    assert near_2024_apr[0].eclipse_sign == "aries"


def test_determinism():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = [e.to_dict() for e in compute_eclipses(birth, span_years=30, only_activated=False)]
    b = [e.to_dict() for e in compute_eclipses(birth, span_years=30, only_activated=False)]
    assert a == b
