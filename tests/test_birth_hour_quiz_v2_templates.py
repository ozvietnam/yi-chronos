"""Tests for question templates library (19 traits)."""
from engine.yi_wiki.birth_hour_quiz_v2.templates import TRAIT_TEMPLATES


EXPECTED_TRAITS = {
    "body_height", "body_build", "face_shape", "skin_tone",
    "hair_quality", "eye_features", "physiognomy_marks",
    "decision_style", "leadership_orientation", "introvert_extrovert",
    "emotional_pattern", "communication_style",
    "wake_natural_time", "energy_peak_period", "sleep_pattern",
    "career_direction", "sibling_position_likely",
    "marriage_timing_rough", "health_pattern_general",
}


def test_all_19_templates_present():
    assert set(TRAIT_TEMPLATES.keys()) == EXPECTED_TRAITS


def test_each_template_has_required_fields():
    for trait, tpl in TRAIT_TEMPLATES.items():
        assert "question_vi" in tpl, f"{trait} missing question_vi"
        assert "domain" in tpl,      f"{trait} missing domain"
        assert "value_labels" in tpl, f"{trait} missing value_labels"
        assert isinstance(tpl["value_labels"], dict)
        assert len(tpl["value_labels"]) >= 2, f"{trait} needs ≥2 value labels"


def test_face_shape_template_values():
    tpl = TRAIT_TEMPLATES["face_shape"]
    assert "dai" in tpl["value_labels"]
    assert "vuong" in tpl["value_labels"]
    assert "tron" in tpl["value_labels"]


def test_energy_peak_template_values():
    tpl = TRAIT_TEMPLATES["energy_peak_period"]
    for v in ["sang", "trua", "chieu", "toi", "dem"]:
        assert v in tpl["value_labels"], f"missing value: {v}"


def test_value_labels_are_vietnamese():
    """Sanity: at least one common Vietnamese marker."""
    sample = TRAIT_TEMPLATES["body_height"]["value_labels"]
    text = " ".join(sample.values())
    assert any(ch in text for ch in "àáâãèéêíòóôõùúýăđ")
