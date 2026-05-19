from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_sky_now_returns_full_chart():
    response = client.get("/api/sky-now?at=2026-05-10T15:00:00Z")
    assert response.status_code == 200
    payload = response.json()

    assert payload["timestamp_utc"].startswith("2026-05-10T15:00")
    assert payload["ephemeris_source"] == "JPL DE440s"
    assert len(payload["bodies"]) == 10
    assert payload["sun_sign"] in {
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    }
    assert payload["dominant_element"] in {"fire", "earth", "air", "water"}


def test_sky_now_without_location_has_no_ascendant():
    response = client.get("/api/sky-now?at=2026-05-10T15:00:00Z")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ascendant"] is None
    assert payload["midheaven"] is None


def test_sky_now_with_location_has_ascendant_and_midheaven():
    # Hanoi coordinates.
    response = client.get("/api/sky-now?at=2026-05-10T15:00:00Z&lat=21.0285&lon=105.8542")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ascendant"] is not None
    assert payload["midheaven"] is not None
    assert "sign" in payload["ascendant"]
    assert "sign_degree" in payload["midheaven"]


def test_sky_now_default_timestamp_uses_current_time():
    response = client.get("/api/sky-now")
    assert response.status_code == 200
    payload = response.json()
    assert "timestamp_utc" in payload
    assert len(payload["bodies"]) == 10


def test_universe_now_now_includes_sky_block():
    response = client.get("/api/universe-now")
    assert response.status_code == 200
    payload = response.json()
    # Backward compat: existing fields still present.
    assert "yi_state" in payload
    assert "scores" in payload
    assert "algorithm_version" in payload
    # New sky block.
    assert "sky" in payload
    assert len(payload["sky"]["bodies"]) == 10
    assert payload["sky"]["ephemeris_source"] == "JPL DE440s"


def test_sky_now_body_fields_complete():
    response = client.get("/api/sky-now?at=2026-05-10T15:00:00Z")
    payload = response.json()
    sample = payload["bodies"][0]
    expected_keys = {
        "name", "ecliptic_longitude", "ecliptic_latitude",
        "sign", "sign_degree", "is_retrograde",
        "speed_deg_per_day", "dignity",
    }
    assert expected_keys.issubset(sample.keys())


def test_sky_now_aspects_have_required_fields():
    response = client.get("/api/sky-now?at=2026-05-10T15:00:00Z")
    payload = response.json()
    if payload["aspects"]:
        sample = payload["aspects"][0]
        expected = {"body_a", "body_b", "aspect_type", "angle_deg", "orb_deg", "applying"}
        assert expected.issubset(sample.keys())
