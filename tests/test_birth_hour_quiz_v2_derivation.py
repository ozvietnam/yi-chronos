"""Tests for trait derivation orchestrator (rules + LLM = 19 traits)."""
from unittest.mock import patch
from engine.yi_wiki.birth_hour_quiz_v2.derivation import derive_all_traits


SAMPLE_CANDIDATES = [
    {"chi": "Mão",  "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                 "month": {"stem": "Bính", "branch": "Thìn"},
                                 "day":   {"stem": "Quý", "branch": "Sửu"},
                                 "hour":  {"stem": "Ất",  "branch": "Mão"}}},
]
FAKE_LLM = {
    "Mão": {"decision_style": "analytical", "leadership_orientation": "supportive",
            "emotional_pattern": "cool", "communication_style": "nuanced",
            "career_direction": "creative", "marriage_timing_rough": "25_30",
            "health_pattern_general": "on"},
}


def test_derive_all_traits_returns_22_per_candidate():
    with patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm",
               return_value=FAKE_LLM):
        out = derive_all_traits(SAMPLE_CANDIDATES)
    expected = {
        # Domain 1 (7)
        "body_height", "body_build", "face_shape", "skin_tone",
        "hair_quality", "eye_features", "physiognomy_marks",
        # Domain 2 (5)
        "decision_style", "leadership_orientation", "introvert_extrovert",
        "emotional_pattern", "communication_style",
        # Domain 3 (3)
        "wake_natural_time", "energy_peak_period", "sleep_pattern",
        # Domain 4 (4)
        "career_direction", "sibling_position_likely",
        "marriage_timing_rough", "health_pattern_general",
        # Domain 5 (3) — tật ách/bệnh sử (Tử Vi Bôn Ba video 091)
        "health_hoa_linh", "health_khong_kiep", "health_sat_tinh_than",
    }
    got = set(out["Mão"].keys())
    assert got == expected, f"missing: {expected - got}, extra: {got - expected}"
    # SAMPLE thiếu lunar/gender → domain 5 degrade êm về unknown, không raise
    assert out["Mão"]["health_hoa_linh"] == "unknown"


def test_llm_values_pass_through():
    with patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm",
               return_value=FAKE_LLM):
        out = derive_all_traits(SAMPLE_CANDIDATES)
    assert out["Mão"]["decision_style"] == "analytical"
    assert out["Mão"]["career_direction"] == "creative"


def test_rule_values_take_precedence_over_llm():
    """Rule traits (e.g. introvert_extrovert) should NOT be from LLM."""
    llm_trying_to_override = {
        "Mão": {**FAKE_LLM["Mão"], "introvert_extrovert": "INVALID"},  # would be invalid anyway
    }
    with patch("engine.yi_wiki.birth_hour_quiz_v2.derivation.call_trait_llm",
               return_value=llm_trying_to_override):
        out = derive_all_traits(SAMPLE_CANDIDATES)
    # introvert_extrovert is rule-derived (yin/yang ratio)
    assert out["Mão"]["introvert_extrovert"] in {"mostly_intro", "mid", "mostly_extro"}
