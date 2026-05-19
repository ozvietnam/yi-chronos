from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from engine.lunar_returns import compute_lunar_returns


@pytest.fixture(scope="module")
def returns():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    from_dt = datetime(2026, 5, 10, tzinfo=timezone.utc)
    return compute_lunar_returns(birth, from_dt=from_dt, count=12, lat=21.0285, lon=105.8542)


def test_returns_count(returns):
    assert len(returns) == 12


def test_indices_strictly_increasing(returns):
    indices = [r.index for r in returns]
    assert indices == sorted(indices)
    for i in range(1, len(indices)):
        assert indices[i] - indices[i - 1] == 1


def test_returns_about_27_days_apart(returns):
    for i in range(1, len(returns)):
        prev = datetime.fromisoformat(returns[i - 1].date_utc.replace("Z", "+00:00"))
        cur = datetime.fromisoformat(returns[i].date_utc.replace("Z", "+00:00"))
        delta = (cur - prev).total_seconds() / 86400.0
        assert 26.5 < delta < 28.5


def test_moon_sign_constant_in_returns(returns):
    """By definition, lunar return = Moon at natal Moon longitude → same sign."""
    moon_signs = {r.chart.moon_sign for r in returns}
    assert len(moon_signs) == 1


def test_returns_only_after_from_dt(returns):
    from_dt = datetime(2026, 5, 10, tzinfo=timezone.utc)
    for r in returns:
        rd = datetime.fromisoformat(r.date_utc.replace("Z", "+00:00"))
        assert rd >= from_dt


def test_chart_has_ascendant_when_location_provided(returns):
    for r in returns:
        assert r.chart.ascendant is not None


def test_serializable(returns):
    import json
    payload = json.dumps(returns[0].to_dict())
    restored = json.loads(payload)
    assert "chart" in restored
    assert "bodies" in restored["chart"]
