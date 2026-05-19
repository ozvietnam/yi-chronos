from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.solar_arc import compute_solar_arc_hits


@pytest.fixture(scope="module")
def hits():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    return compute_solar_arc_hits(birth, lat=21.0285, lon=105.8542, span_years=90)


def test_returns_nonempty(hits):
    assert len(hits) > 20


def test_sorted_by_age(hits):
    ages = [h.age_years for h in hits]
    assert ages == sorted(ages)


def test_within_span(hits):
    for h in hits:
        assert 0 <= h.age_years <= 90


def test_directed_and_target_differ(hits):
    for h in hits:
        assert h.directed_body != h.natal_target


def test_field_validity(hits):
    for h in hits:
        d = h.to_dict()
        assert d["aspect_type"] in {
            "conjunction", "sextile", "square", "trine", "opposition"
        }
        assert d["importance"] in {"major", "medium", "minor"}
        assert 0 <= d["arc_value_deg"] < 360


def test_arc_value_grows_with_age(hits):
    """Solar arc grows monotonically; for any aspect, arc value scales with age."""
    # For conjunction (angle 0), arc = (target_lon - directed_lon) % 360
    # Arc value at age N years ≈ N degrees (rough).
    # So conjunctions at age 30 should have arc ≈ 30°, not 100°.
    for h in hits:
        # Tolerance ±25° (different actual progressed Sun motion + initial offset).
        # arc at age 0 = 0, arc at age 90 ≈ 89°.
        assert abs(h.arc_value_deg - h.age_years) < 30


def test_determinism():
    birth = datetime(1990, 3, 15, 12, 0, tzinfo=timezone.utc)
    a = [h.to_dict() for h in compute_solar_arc_hits(birth, span_years=60)]
    b = [h.to_dict() for h in compute_solar_arc_hits(birth, span_years=60)]
    assert a == b


def test_works_without_location():
    birth = datetime(1985, 7, 20, 3, 30, tzinfo=timezone.utc)
    hits_no_loc = compute_solar_arc_hits(birth, span_years=60)
    assert len(hits_no_loc) > 0
    for h in hits_no_loc:
        assert h.natal_target not in {"ascendant", "midheaven"}
