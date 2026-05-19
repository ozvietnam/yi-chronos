from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.transit_timeline import compute_transit_hits


@pytest.fixture(scope="module")
def hits():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_transit_hits(birth, lat=21.0285, lon=105.8542, span_years=60)


def test_returns_nonempty_list(hits):
    assert len(hits) > 50


def test_sorted_by_age(hits):
    ages = [h.age_years for h in hits]
    assert ages == sorted(ages)


def test_all_within_span(hits):
    for h in hits:
        assert 0 <= h.age_years <= 60


def test_field_validity(hits):
    for h in hits:
        d = h.to_dict()
        assert d["transit_body"] in {"jupiter", "saturn", "uranus", "neptune", "pluto"}
        assert d["natal_point"] in {
            "sun", "moon", "mercury", "venus", "mars", "ascendant", "midheaven"
        }
        assert d["aspect_type"] in {
            "conjunction", "sextile", "square", "trine", "opposition"
        }
        assert d["importance"] in {"major", "medium", "minor"}
        assert d["transit_sign"] in {
            "aries", "taurus", "gemini", "cancer", "leo", "virgo",
            "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
        }


def test_includes_asc_when_location_provided(hits):
    asc_hits = [h for h in hits if h.natal_point == "ascendant"]
    assert len(asc_hits) > 0


def test_excludes_asc_when_no_location():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    hits_no_loc = compute_transit_hits(birth, span_years=40)
    asc_hits = [h for h in hits_no_loc if h.natal_point == "ascendant"]
    assert len(asc_hits) == 0


def test_major_hits_are_strong_combinations(hits):
    """Major = (Sun/Moon/Asc/MC) ∩ (Saturn/Uranus/Pluto) ∩ hard aspect."""
    luminaries = {"sun", "moon", "ascendant", "midheaven"}
    heavies = {"saturn", "uranus", "pluto"}
    hard = {"conjunction", "square", "opposition"}
    for h in hits:
        if h.importance == "major":
            assert h.natal_point in luminaries
            assert h.transit_body in heavies
            assert h.aspect_type in hard


def test_determinism():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = compute_transit_hits(birth, span_years=30)
    b = compute_transit_hits(birth, span_years=30)
    assert [h.to_dict() for h in a] == [h.to_dict() for h in b]


def test_saturn_conjunct_natal_sun_appears_at_some_point(hits):
    """In a 60-year span, Saturn must conjunct natal Sun at least once (29.5y cycle)."""
    matches = [h for h in hits if h.transit_body == "saturn"
               and h.natal_point == "sun" and h.aspect_type == "conjunction"]
    assert len(matches) >= 1
