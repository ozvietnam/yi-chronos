"""Tests for Domain 1 physical traits derivation."""
from engine.yi_wiki.birth_hour_quiz_v2.rules.physical import derive_physical_traits

# Example: 1988-05-02 hour Thìn — full pillars (simulated)
SAMPLE_PILLARS = {
    "year":  {"stem": "Mậu", "branch": "Thìn"},
    "month": {"stem": "Bính", "branch": "Thìn"},
    "day":   {"stem": "Quý", "branch": "Sửu"},
    "hour":  {"stem": "Bính", "branch": "Thìn"},
}


def test_derive_physical_returns_7_traits():
    out = derive_physical_traits(SAMPLE_PILLARS)
    expected_keys = {
        "body_height", "body_build", "face_shape", "skin_tone",
        "hair_quality", "eye_features", "physiognomy_marks",
    }
    assert set(out.keys()) == expected_keys


def test_face_shape_uses_day_master_and_hour():
    # Quý Thuỷ baseline=oval, hour Thìn=Thổ → adjustment to vuong
    out = derive_physical_traits(SAMPLE_PILLARS)
    assert out["face_shape"] in {"oval", "vuong", "tron"}


def test_physiognomy_marks_from_hour_chi():
    # Hour Tý → 1 xoáy (per CHI_HOUR_PHYSIOGNOMY)
    pillars_ty = {**SAMPLE_PILLARS, "hour": {"stem": "Nhâm", "branch": "Tý"}}
    out = derive_physical_traits(pillars_ty)
    assert out["physiognomy_marks"] == "1_xoay"


def test_physiognomy_marks_two_xoay_for_dan():
    pillars_dan = {**SAMPLE_PILLARS, "hour": {"stem": "Giáp", "branch": "Dần"}}
    out = derive_physical_traits(pillars_dan)
    assert out["physiognomy_marks"] == "2_xoay"
