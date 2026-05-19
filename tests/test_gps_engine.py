"""Tests for GPS engine — trigger generation + action recommendations."""

from __future__ import annotations

from datetime import date

import pytest

from engine.gps_engine import (
    ACTION_TEMPLATES,
    DOMAINS,
    DOMAIN_ELEMENT_AFFINITY,
    DOMAIN_VI,
    GPSDay,
    Trigger,
    _profile_hash,
    _score_band,
    compute_gps_day,
    hash_gps_day,
    hash_trigger,
)
from engine.personal_quai import compute_natal_hexagram


@pytest.fixture(scope="module")
def natal():
    return compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")


@pytest.fixture(scope="module")
def gps_day(natal):
    return compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")


def test_returns_gps_day_with_required_fields(gps_day):
    assert gps_day.date_local == "2026-05-18"
    assert gps_day.day_pillar
    assert gps_day.day_quai
    assert 1 <= gps_day.day_quai_king_wen <= 64
    assert gps_day.solar_term
    assert gps_day.profile_hash
    assert "mode" in gps_day.runtime_mode


def test_score_bands_complete():
    assert _score_band(85) == "high"
    assert _score_band(70) == "medium_plus"
    assert _score_band(55) == "medium"
    assert _score_band(40) == "medium_minus"
    assert _score_band(20) == "low"


def test_action_templates_cover_all_domains_and_bands():
    expected_bands = {"high", "medium_plus", "medium", "medium_minus", "low"}
    for domain in DOMAINS:
        assert domain in ACTION_TEMPLATES
        assert set(ACTION_TEMPLATES[domain].keys()) == expected_bands
        for band, templates in ACTION_TEMPLATES[domain].items():
            assert len(templates) >= 2  # At least 2 alternatives per cell.


def test_domain_vi_translations_complete():
    for domain in DOMAINS:
        assert domain in DOMAIN_VI


def test_domain_element_affinity_uses_valid_elements():
    valid = {"kim", "mộc", "thủy", "hỏa", "thổ"}
    for el in DOMAIN_ELEMENT_AFFINITY.values():
        assert el in valid


def test_triggers_sorted_by_score_descending(gps_day):
    scores = [t.score for t in gps_day.triggers]
    assert scores == sorted(scores, reverse=True)


def test_triggers_have_valid_fields(gps_day):
    valid_bands = {"high", "medium_plus", "medium", "medium_minus", "low"}
    for t in gps_day.triggers:
        assert t.domain in DOMAINS
        assert 0 <= t.score <= 100
        assert t.score_band in valid_bands
        assert t.hour_branch in (
            "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
            "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"
        )
        assert 0 <= t.hour_midpoint < 24
        assert t.action_text  # Non-empty.
        assert t.rule_id.startswith("gps:")
        assert "compatibility_breakdown" in t.score_components


def test_min_score_threshold_filters_low_triggers(natal):
    """If min_score is high, fewer triggers."""
    g_high = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh", min_score_for_trigger=80)
    g_low = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh", min_score_for_trigger=30)
    assert len(g_high.triggers) <= len(g_low.triggers)
    for t in g_high.triggers:
        assert t.score >= 80


def test_determinism(natal):
    a = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")
    b = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")
    assert a.to_dict() == b.to_dict()


def test_hash_stable_across_calls(natal):
    a = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")
    b = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")
    assert hash_gps_day(a) == hash_gps_day(b)


def test_hash_changes_with_different_dates(natal):
    a = compute_gps_day(natal, date(2026, 5, 18), "Asia/Ho_Chi_Minh")
    b = compute_gps_day(natal, date(2026, 5, 19), "Asia/Ho_Chi_Minh")
    assert hash_gps_day(a) != hash_gps_day(b)


def test_trigger_hash_unique_per_trigger(gps_day):
    hashes = {hash_trigger(t, gps_day.profile_hash, gps_day.date_local) for t in gps_day.triggers}
    assert len(hashes) == len(gps_day.triggers)


def test_profile_hash_consistent():
    a = _profile_hash("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    b = _profile_hash("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    assert a == b
    c = _profile_hash("1985-07-20T03:31:00", "Asia/Ho_Chi_Minh")
    assert c != a


def test_runtime_mode_present_in_output(gps_day):
    assert gps_day.runtime_mode["mode"] in {"EXPERIMENTAL", "PRODUCTION"}
    assert "message" in gps_day.runtime_mode


def test_serializable(gps_day):
    import json
    payload = json.dumps(gps_day.to_dict(), ensure_ascii=False)
    restored = json.loads(payload)
    assert restored["date_local"] == gps_day.date_local
    assert len(restored["triggers"]) == len(gps_day.triggers)
