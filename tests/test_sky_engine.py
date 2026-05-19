from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.sky import (
    ASPECTS,
    DEFAULT_BODIES,
    SIGN_ELEMENTS,
    ZODIAC_SIGNS,
    _angular_separation,
    _longitude_to_sign,
    calculate_sky_chart,
)


def test_zodiac_sign_mapping_exhaustive():
    assert len(ZODIAC_SIGNS) == 12
    assert all(s in SIGN_ELEMENTS for s in ZODIAC_SIGNS)
    elements = {SIGN_ELEMENTS[s] for s in ZODIAC_SIGNS}
    assert elements == {"fire", "earth", "air", "water"}


def test_longitude_to_sign_boundaries():
    assert _longitude_to_sign(0.0) == ("aries", 0.0)
    assert _longitude_to_sign(29.999)[0] == "aries"
    assert _longitude_to_sign(30.0) == ("taurus", 0.0)
    assert _longitude_to_sign(359.9)[0] == "pisces"
    assert _longitude_to_sign(360.0) == ("aries", 0.0)


def test_angular_separation_shortest_path():
    assert _angular_separation(10.0, 20.0) == pytest.approx(10.0)
    assert _angular_separation(350.0, 10.0) == pytest.approx(20.0)
    assert _angular_separation(0.0, 180.0) == pytest.approx(180.0)
    assert _angular_separation(0.0, 270.0) == pytest.approx(90.0)


def test_calculate_sky_chart_returns_all_default_bodies():
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    names = [b.name for b in chart.bodies]
    assert names == list(DEFAULT_BODIES)
    assert len(chart.bodies) == 10


def test_sun_in_aries_at_vernal_equinox_2026():
    # Vernal equinox 2026 ~ Mar 20 14:46 UTC. Sun should be near 0 degrees Aries.
    chart = calculate_sky_chart(datetime(2026, 3, 20, 14, 46, tzinfo=timezone.utc))
    sun = next(b for b in chart.bodies if b.name == "sun")
    assert sun.sign == "aries"
    assert sun.sign_degree < 0.5  # within half a degree


def test_determinism_same_input_same_output():
    dt = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    chart1 = calculate_sky_chart(dt)
    chart2 = calculate_sky_chart(dt)
    assert chart1.to_dict() == chart2.to_dict()


def test_dignities_correct_for_known_placements():
    """Mars in Aries = rulership; Jupiter in Cancer = exaltation; Saturn in Aries = fall."""
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    by_name = {b.name: b for b in chart.bodies}
    assert by_name["mars"].sign == "aries"
    assert by_name["mars"].dignity == "rulership"
    assert by_name["jupiter"].sign == "cancer"
    assert by_name["jupiter"].dignity == "exaltation"
    assert by_name["saturn"].sign == "aries"
    assert by_name["saturn"].dignity == "fall"


def test_pluto_retrograde_in_may_2026():
    # Pluto is retrograde from early May to mid-October 2026.
    chart = calculate_sky_chart(datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc))
    pluto = next(b for b in chart.bodies if b.name == "pluto")
    assert pluto.is_retrograde is True


def test_sun_never_marked_retrograde():
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    sun = next(b for b in chart.bodies if b.name == "sun")
    assert sun.is_retrograde is False


def test_aspects_have_valid_orb():
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    valid_types = {name for name, _, _ in ASPECTS}
    max_orbs = {name: orb for name, _, orb in ASPECTS}
    for aspect in chart.aspects:
        assert aspect.aspect_type in valid_types
        assert aspect.orb_deg <= max_orbs[aspect.aspect_type]
        assert 0 <= aspect.angle_deg <= 180


def test_aspects_no_self_pairing():
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    for aspect in chart.aspects:
        assert aspect.body_a != aspect.body_b


def test_dominant_element_is_one_of_four():
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    assert chart.dominant_element in {"fire", "earth", "air", "water"}


def test_ascendant_midheaven_only_when_location_provided():
    dt = datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc)
    chart_no_loc = calculate_sky_chart(dt)
    assert chart_no_loc.ascendant is None
    assert chart_no_loc.midheaven is None

    chart_with_loc = calculate_sky_chart(dt, lat=21.0285, lon=105.8542)  # Hanoi
    assert chart_with_loc.ascendant is not None
    assert chart_with_loc.midheaven is not None
    assert chart_with_loc.ascendant.sign in ZODIAC_SIGNS
    assert chart_with_loc.midheaven.sign in ZODIAC_SIGNS


def test_naive_datetime_treated_as_utc():
    # Naive datetime should be treated as UTC.
    dt_naive = datetime(2026, 5, 10, 15, 0)
    dt_aware = datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc)
    chart_naive = calculate_sky_chart(dt_naive)
    chart_aware = calculate_sky_chart(dt_aware)
    assert chart_naive.to_dict() == chart_aware.to_dict()


def test_to_dict_serializable():
    import json
    chart = calculate_sky_chart(datetime(2026, 5, 10, 15, 0, tzinfo=timezone.utc))
    payload = chart.to_dict()
    # Must round-trip through JSON.
    serialized = json.dumps(payload)
    restored = json.loads(serialized)
    assert restored["sun_sign"] == chart.sun_sign
    assert len(restored["bodies"]) == 10
