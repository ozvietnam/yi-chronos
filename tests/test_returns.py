from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.returns import compute_solar_returns


@pytest.fixture(scope="module")
def returns():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_solar_returns(birth, lat=21.0285, lon=105.8542, span_years=30)


def test_returns_one_per_year(returns):
    assert len(returns) == 31
    ages = [r.age for r in returns]
    assert ages == list(range(0, 31))


def test_first_return_close_to_birth():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    rs = compute_solar_returns(birth, span_years=0)
    assert len(rs) == 1
    delta = abs((datetime.fromisoformat(rs[0].date_utc.replace("Z", "+00:00")) - birth).total_seconds())
    assert delta < 60  # within a minute


def test_sun_sign_constant_across_returns(returns):
    """Solar returns by definition put Sun at natal longitude → same sign each year."""
    sun_signs = {r.chart.sun_sign for r in returns}
    assert len(sun_signs) == 1


def test_returns_are_one_year_apart(returns):
    for i in range(1, len(returns)):
        prev = datetime.fromisoformat(returns[i - 1].date_utc.replace("Z", "+00:00"))
        cur = datetime.fromisoformat(returns[i].date_utc.replace("Z", "+00:00"))
        delta_days = (cur - prev).total_seconds() / 86400.0
        assert 364.5 < delta_days < 366.5


def test_chart_includes_ascendant_when_location_provided(returns):
    for r in returns:
        assert r.chart.ascendant is not None


def test_chart_excludes_ascendant_without_location():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    rs = compute_solar_returns(birth, span_years=2)
    for r in rs:
        assert r.chart.ascendant is None


def test_serializable_to_dict(returns):
    import json
    sample = returns[0].to_dict()
    serialized = json.dumps(sample)
    restored = json.loads(serialized)
    assert restored["age"] == 0
    assert "chart" in restored
    assert "bodies" in restored["chart"]


def test_determinism():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = [r.to_dict() for r in compute_solar_returns(birth, span_years=10)]
    b = [r.to_dict() for r in compute_solar_returns(birth, span_years=10)]
    assert a == b
