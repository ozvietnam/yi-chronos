from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from engine.personal_quai import compute_natal_hexagram
from engine.van_trong_van import (
    HOUR_BRANCH_ORDER,
    VN_HOUR_MIDPOINTS,
    compute_van_trong_van,
)


@pytest.fixture(scope="module")
def result():
    natal = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    return compute_van_trong_van(natal, start_date=start, span_days=30)


def test_returns_correct_number_of_days(result):
    assert len(result.days) == 30


def test_days_are_consecutive(result):
    from datetime import date
    dates = [date.fromisoformat(d.date_local) for d in result.days]
    for i in range(1, len(dates)):
        assert (dates[i] - dates[i - 1]).days == 1


def test_each_day_has_12_hour_slots(result):
    for d in result.days:
        assert len(d.all_hour_scores) == 12
        branches = [s.branch for s in d.all_hour_scores]
        assert branches == list(HOUR_BRANCH_ORDER)


def test_best_hour_score_is_max(result):
    for d in result.days:
        max_slot = max(d.all_hour_scores, key=lambda s: s.score)
        assert d.best_hour_score == max_slot.score
        assert d.best_hour_branch == max_slot.branch


def test_worst_hour_score_is_min(result):
    for d in result.days:
        min_slot = min(d.all_hour_scores, key=lambda s: s.score)
        assert d.worst_hour_score == min_slot.score
        assert d.worst_hour_branch == min_slot.branch


def test_score_in_valid_range(result):
    for d in result.days:
        assert 0 <= d.day_compatibility.final_score <= 100
        for slot in d.all_hour_scores:
            assert 0 <= slot.score <= 100


def test_hour_midpoint_table():
    assert VN_HOUR_MIDPOINTS["Tý"] == 0
    assert VN_HOUR_MIDPOINTS["Ngọ"] == 12
    assert len(VN_HOUR_MIDPOINTS) == 12


def test_each_day_has_primary_quai(result):
    for d in result.days:
        assert d.primary_name
        assert 1 <= d.primary_king_wen <= 64
        assert len(d.primary_binary) == 6


def test_determinism():
    natal = compute_natal_hexagram("1990-03-15T12:00:00", "Asia/Ho_Chi_Minh")
    start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
    a = compute_van_trong_van(natal, start_date=start, span_days=10)
    b = compute_van_trong_van(natal, start_date=start, span_days=10)
    assert a.to_dict() == b.to_dict()


def test_serializable(result):
    import json
    payload = json.dumps(result.to_dict())
    restored = json.loads(payload)
    assert restored["span_days"] == 30
    assert len(restored["days"]) == 30
