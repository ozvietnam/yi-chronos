"""Tests for engine.bat_tu — Bát Tự MVP."""

from __future__ import annotations

import pytest

from engine.bat_tu import cast_bat_tu, extract_tu_tru, thap_than_of
from engine.bat_tu.ngu_hanh import (
    count_elements,
    day_master_strength,
)
from engine.bat_tu.thap_than import thap_than_short


# ─── Thập Thần classifier ──────────────────────────────────────────────────────


def test_thap_than_same_element_same_polarity_is_ti_kien():
    # Giáp (mộc dương) vs Giáp (mộc dương)
    assert thap_than_of("Giáp", "Giáp") == "Tỷ Kiên"


def test_thap_than_same_element_opposite_polarity_is_kiep_tai():
    assert thap_than_of("Giáp", "Ất") == "Kiếp Tài"  # both mộc, dương vs âm


def test_thap_than_day_generates_target_same_polarity_is_thuc_than():
    # Giáp (mộc dương) generates Bính (hỏa dương) → Thực Thần
    assert thap_than_of("Giáp", "Bính") == "Thực Thần"


def test_thap_than_day_generates_target_opposite_polarity_is_thuong_quan():
    # Giáp dương → Đinh hỏa âm → Thương Quan
    assert thap_than_of("Giáp", "Đinh") == "Thương Quan"


def test_thap_than_day_controls_target_same_polarity_is_thien_tai():
    # Giáp (mộc dương) controls Mậu (thổ dương) → Thiên Tài
    assert thap_than_of("Giáp", "Mậu") == "Thiên Tài"


def test_thap_than_day_controls_target_opposite_polarity_is_chinh_tai():
    # Giáp dương controls Kỷ thổ âm → Chính Tài
    assert thap_than_of("Giáp", "Kỷ") == "Chính Tài"


def test_thap_than_target_controls_day_same_polarity_is_that_sat():
    # Canh (kim dương) controls Giáp (mộc dương) → Thất Sát
    assert thap_than_of("Giáp", "Canh") == "Thất Sát"


def test_thap_than_target_controls_day_opposite_polarity_is_chinh_quan():
    # Tân (kim âm) controls Giáp dương → Chính Quan
    assert thap_than_of("Giáp", "Tân") == "Chính Quan"


def test_thap_than_target_generates_day_same_polarity_is_thien_an():
    # Nhâm (thủy dương) generates Giáp (mộc dương) → Thiên Ấn
    assert thap_than_of("Giáp", "Nhâm") == "Thiên Ấn"


def test_thap_than_target_generates_day_opposite_polarity_is_chinh_an():
    # Quý (thủy âm) generates Giáp dương → Chính Ấn
    assert thap_than_of("Giáp", "Quý") == "Chính Ấn"


def test_thap_than_short_label():
    assert thap_than_short("Tỷ Kiên") == "Tỷ"
    assert thap_than_short("Chính Quan") == "Quan"


def test_thap_than_all_10_distinct_pairs():
    """For Day Master Giáp, the 10 stems must produce 10 distinct Thập Thần."""
    stems = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    relations = {thap_than_of("Giáp", s) for s in stems}
    assert len(relations) == 10


def test_thap_than_rejects_unknown_stem():
    with pytest.raises(ValueError):
        thap_than_of("Foo", "Giáp")


# ─── Tứ Trụ extraction ─────────────────────────────────────────────────────────


def test_extract_tu_tru_basic_shape():
    r = extract_tu_tru("1985-08-15T10:30:00", "Asia/Ho_Chi_Minh")
    assert "pillars" in r
    assert set(r["pillars"].keys()) == {"year", "month", "day", "hour"}
    for pos, p in r["pillars"].items():
        assert "stem" in p
        assert "branch" in p
        assert "stem_element" in p
        assert "branch_element" in p
        assert isinstance(p["hidden_stems"], list)


def test_extract_tu_tru_day_master_consistency():
    r = extract_tu_tru("1985-08-15T10:30:00", "Asia/Ho_Chi_Minh")
    day_pillar = r["pillars"]["day"]
    assert r["day_master"]["stem"] == day_pillar["stem"]
    assert r["day_master"]["element"] == day_pillar["stem_element"]


# ─── Ngũ hành balance ──────────────────────────────────────────────────────────


def test_count_elements_returns_all_5_elements():
    r = extract_tu_tru("1985-08-15T10:30:00", "Asia/Ho_Chi_Minh")
    counts = count_elements(r["pillars"])
    assert set(counts.keys()) == {"kim", "mộc", "thủy", "hỏa", "thổ"}
    # All counts must be numeric and non-negative.
    for v in counts.values():
        assert v >= 0


def test_day_master_strength_categorizes():
    r = extract_tu_tru("1985-08-15T10:30:00", "Asia/Ho_Chi_Minh")
    counts = count_elements(r["pillars"])
    dm = day_master_strength(r["day_master"]["element"], counts)
    assert dm["strength_tag"] in ("strong", "weak", "balanced", "neutral")
    assert dm["support_score"] >= 0
    assert dm["drain_score"] >= 0


# ─── Top-level cast ────────────────────────────────────────────────────────────


def test_cast_bat_tu_complete_shape():
    r = cast_bat_tu(
        birth_datetime_local="1985-08-15T10:30:00",
        timezone="Asia/Ho_Chi_Minh",
        gender="nam",
    )
    assert r["method_id"] == "bat_tu_tu_tru_v1"
    assert "tu_tru" in r
    assert "ngu_hanh" in r
    assert "thap_than_distribution" in r
    assert "thap_than_meanings" in r

    # Each pillar must have Thập Thần annotations.
    for pos in ("year", "month", "hour"):
        assert r["tu_tru"]["pillars"][pos]["stem_thap_than"] in {
            "Tỷ Kiên", "Kiếp Tài", "Thực Thần", "Thương Quan",
            "Thiên Tài", "Chính Tài", "Thất Sát", "Chính Quan",
            "Thiên Ấn", "Chính Ấn",
        }
    # Day pillar's stem is the Day Master itself.
    assert r["tu_tru"]["pillars"]["day"]["stem_thap_than"] == "Bản thân"


def test_cast_bat_tu_rejects_invalid_gender():
    with pytest.raises(ValueError):
        cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00", gender="other")


def test_cast_bat_tu_is_json_serializable():
    import json

    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00")
    s = json.dumps(r, ensure_ascii=False)
    # Round-trip
    decoded = json.loads(s)
    assert decoded["method_id"] == "bat_tu_tu_tru_v1"


def test_cast_bat_tu_alpha_layers_no_longer_deferred():
    """After α-rollout + refinement, all 7 layers are live; only advanced
    layers (Thần Sát mở rộng, cách cục, điều hậu) remain deferred."""
    r = cast_bat_tu(birth_datetime_local="1985-08-15T10:30:00")
    # All 7 layers must now appear at top-level
    assert "truong_sinh" in r
    assert "than_sat" in r
    assert "dai_van" in r
    assert "dung_than" in r
    deferred = r.get("deferred_layers", [])
    # Only advanced layers remain deferred
    deferred_text = " ".join(deferred)
    assert "Cách cục" in deferred_text or "Điều hậu" in deferred_text or "Thần Sát mở rộng" in deferred_text


def test_api_bat_tu_endpoint():
    """Smoke: /api/bat-tu/cast returns a valid structure."""
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/bat-tu/cast",
        json={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "gender": "nam",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "bat_tu_state" in payload
    state = payload["bat_tu_state"]
    assert state["method_id"] == "bat_tu_tu_tru_v1"
    assert state["tu_tru"]["pillars"]["day"]["stem_thap_than"] == "Bản thân"
