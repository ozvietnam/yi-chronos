from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.progressions import (
    compute_progressed_chart,
    compute_progressed_moon_timeline,
)


@pytest.fixture(scope="module")
def phases():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_progressed_moon_timeline(birth, span_years=90)


def test_phases_cover_full_span(phases):
    assert phases[0].age_start == 0.0
    assert phases[-1].age_end is None
    for p in phases[:-1]:
        assert p.age_end is not None


def test_phases_are_continuous(phases):
    for i in range(1, len(phases)):
        assert phases[i].age_start == phases[i - 1].age_end


def test_progressed_moon_signs_change_roughly_every_2_to_3_years(phases):
    """First phase may be partial (depends on natal Moon's position in its sign)."""
    completed = [p for p in phases if p.age_end is not None]
    # Skip the first phase which is partial.
    durations = [p.age_end - p.age_start for p in completed[1:]]
    assert all(1.5 < d < 3.5 for d in durations)


def test_phase_signs_are_valid(phases):
    valid = {
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    }
    for p in phases:
        assert p.sign in valid


def test_progressed_chart_returns_full_chart():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    chart = compute_progressed_chart(birth, at_age_years=30, lat=21.0285, lon=105.8542)
    assert len(chart.bodies) == 10
    assert chart.ascendant is not None


def test_progressed_chart_at_age_zero_close_to_natal():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    chart_zero = compute_progressed_chart(birth, at_age_years=0)
    sun = next(b for b in chart_zero.bodies if b.name == "sun")
    assert sun.sign == "cancer"  # Sun in Cancer for July 20 birth


def test_determinism():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = [p.to_dict() for p in compute_progressed_moon_timeline(birth, span_years=30)]
    b = [p.to_dict() for p in compute_progressed_moon_timeline(birth, span_years=30)]
    assert a == b
