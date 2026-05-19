from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.life_timeline import compute_life_timeline


@pytest.fixture(scope="module")
def sample_milestones():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_life_timeline(birth, span_years=90)


def test_returns_nonempty_list(sample_milestones):
    assert len(sample_milestones) > 10


def test_milestones_sorted_by_age(sample_milestones):
    ages = [m.age_years for m in sample_milestones]
    assert ages == sorted(ages)


def test_first_saturn_return_falls_around_age_29(sample_milestones):
    saturn_returns = [m for m in sample_milestones if m.transit_body == "saturn" and m.aspect_type == "return"]
    assert len(saturn_returns) >= 1
    first_sr_age = saturn_returns[0].age_years
    assert 28.0 < first_sr_age < 30.5, f"Saturn return should be ~29, got {first_sr_age}"


def test_second_saturn_return_around_age_58(sample_milestones):
    saturn_returns = [m for m in sample_milestones if m.transit_body == "saturn" and m.aspect_type == "return"]
    second = [m for m in saturn_returns if m.age_years > 50]
    assert len(second) >= 1
    assert 57.0 < second[0].age_years < 60.5


def test_uranus_opposition_around_age_42_to_44(sample_milestones):
    """Classic 'midlife' Uranus opposition Uranus event."""
    events = [m for m in sample_milestones if m.transit_body == "uranus" and m.aspect_type == "opposition"]
    assert len(events) >= 1
    age = events[0].age_years
    assert 41.0 < age < 45.0


def test_jupiter_returns_appear_roughly_every_12_years(sample_milestones):
    jr = [m.age_years for m in sample_milestones if m.transit_body == "jupiter" and m.aspect_type == "return"]
    assert len(jr) >= 5
    # Group close-spaced retrograde triples by taking earliest of each cluster.
    clusters: list[float] = []
    for age in jr:
        if not clusters or age - clusters[-1] > 5:
            clusters.append(age)
    gaps = [clusters[i + 1] - clusters[i] for i in range(len(clusters) - 1)]
    for g in gaps:
        assert 11.0 < g < 13.0, f"Jupiter return gap should be ~12, got {g}"


def test_milestone_fields_complete(sample_milestones):
    for m in sample_milestones:
        d = m.to_dict()
        assert d["date_utc"].endswith("Z")
        assert d["age_years"] >= 0
        assert d["transit_body"] in {"saturn", "jupiter", "uranus", "neptune", "pluto"}
        assert d["aspect_type"] in {"return", "square", "opposition"}
        assert d["importance"] in {"major", "medium", "minor"}
        assert d["transit_sign"] in {
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
        }
        assert 0 <= d["transit_degree"] < 30


def test_determinism_same_birth_same_output():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = compute_life_timeline(birth, span_years=60)
    b = compute_life_timeline(birth, span_years=60)
    assert [m.to_dict() for m in a] == [m.to_dict() for m in b]


def test_naive_birth_treated_as_utc():
    naive = datetime(1990, 3, 15, 12, 0)
    aware = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = compute_life_timeline(naive, span_years=40)
    b = compute_life_timeline(aware, span_years=40)
    assert [m.to_dict() for m in a] == [m.to_dict() for m in b]


def test_span_limits_age_range():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    short = compute_life_timeline(birth, span_years=20)
    long_ = compute_life_timeline(birth, span_years=60)
    assert all(m.age_years <= 20.5 for m in short)
    assert max(m.age_years for m in long_) > 20
