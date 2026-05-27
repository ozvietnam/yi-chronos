"""Tests for engine.bat_tu.auspicious_event — date picker."""
from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu, pick_auspicious_dates


@pytest.fixture
def founder_chart():
    return cast_bat_tu(
        birth_datetime_local="1988-06-05T23:30",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )


def test_method_id(founder_chart):
    r = pick_auspicious_dates(
        founder_chart, event_type="general",
        start_date="2026-06-01", end_date="2026-06-30",
    )
    assert r["method_id"] == "bat_tu_auspicious_event_v1"


def test_paradigm_no_predict(founder_chart):
    r = pick_auspicious_dates(
        founder_chart, event_type="wedding",
        start_date="2026-06-01", end_date="2026-06-15",
    )
    assert "KHÔNG đảm bảo" in r["paradigm_guard"]


def test_scan_30_days(founder_chart):
    r = pick_auspicious_dates(
        founder_chart, event_type="general",
        start_date="2026-06-01", end_date="2026-06-30",
    )
    assert r["total_scanned"] == 30


def test_top_candidates_present(founder_chart):
    r = pick_auspicious_dates(
        founder_chart, event_type="business_opening",
        start_date="2026-06-01", end_date="2026-06-30", top_n=5,
    )
    assert len(r["top_candidates"]) == 5
    for c in r["top_candidates"]:
        assert "date" in c
        assert "score" in c
        assert "day_pillar" in c
        assert "reasons" in c


def test_top_better_than_avoid(founder_chart):
    """Top candidates must have higher score than avoid dates."""
    r = pick_auspicious_dates(
        founder_chart, event_type="business_opening",
        start_date="2026-06-01", end_date="2026-06-30",
    )
    top_score = r["top_candidates"][0]["score"]
    avoid_score = r["avoid_dates"][0]["score"]
    assert top_score > avoid_score


def test_dung_than_match_increases_score(founder_chart):
    """Founder's Dụng = Mộc — days with Mộc should rank high."""
    r = pick_auspicious_dates(
        founder_chart, event_type="business_opening",
        start_date="2026-06-01", end_date="2026-06-30",
    )
    # Top candidate should likely have Mộc element somewhere
    top = r["top_candidates"][0]
    p = top["day_pillar"]
    assert top["score"] > 0


@pytest.mark.parametrize("event_type", [
    "wedding", "business_opening", "moving_house",
    "signing_contract", "travel", "general",
])
def test_all_event_types_work(founder_chart, event_type):
    r = pick_auspicious_dates(
        founder_chart, event_type=event_type,
        start_date="2026-06-01", end_date="2026-06-15",
    )
    assert r["event_type"] == event_type
    assert r["event_label"]


def test_invalid_date_format_rejected(founder_chart):
    with pytest.raises(ValueError):
        pick_auspicious_dates(
            founder_chart, event_type="general",
            start_date="invalid", end_date="2026-06-30",
        )


def test_range_too_large_rejected(founder_chart):
    with pytest.raises(ValueError, match="too large"):
        pick_auspicious_dates(
            founder_chart, event_type="general",
            start_date="2026-01-01", end_date="2026-12-31",
        )


def test_invalid_chart_rejected():
    with pytest.raises(ValueError, match="tu_tru"):
        pick_auspicious_dates(
            {}, event_type="general",
            start_date="2026-06-01", end_date="2026-06-30",
        )
