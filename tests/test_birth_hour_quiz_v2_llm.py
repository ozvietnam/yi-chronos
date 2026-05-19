"""Tests for LLM prompt builder + response parser (quiz v2 Domain 2+4)."""
import pytest
from engine.yi_wiki.birth_hour_quiz_v2.llm_prompts import (
    build_trait_prompt, parse_llm_response, LLM_OUTPUT_SCHEMA,
)

SAMPLE_CANDIDATES = [
    {"chi": "Mão",  "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                 "month": {"stem": "Bính", "branch": "Thìn"},
                                 "day":   {"stem": "Quý", "branch": "Sửu"},
                                 "hour":  {"stem": "Ất",  "branch": "Mão"}}},
    {"chi": "Thìn", "pillars": {"year": {"stem": "Mậu", "branch": "Thìn"},
                                 "month": {"stem": "Bính", "branch": "Thìn"},
                                 "day":   {"stem": "Quý", "branch": "Sửu"},
                                 "hour":  {"stem": "Bính", "branch": "Thìn"}}},
]


def test_build_prompt_includes_all_candidates():
    prompt = build_trait_prompt(SAMPLE_CANDIDATES)
    assert "Mão" in prompt
    assert "Thìn" in prompt
    assert "JSON" in prompt


def test_parse_valid_response_with_fence():
    raw = '''Some preamble.
```json
{
  "Mão":  {"decision_style": "analytical", "leadership_orientation": "supportive",
           "emotional_pattern": "cool", "communication_style": "nuanced",
           "career_direction": "creative", "marriage_timing_rough": "25_30",
           "health_pattern_general": "on"},
  "Thìn": {"decision_style": "impulsive", "leadership_orientation": "dominant",
           "emotional_pattern": "passionate", "communication_style": "direct",
           "career_direction": "entrepreneurial", "marriage_timing_rough": "som_25",
           "health_pattern_general": "strong"}
}
```'''
    result = parse_llm_response(raw, expected_candidates=["Mão", "Thìn"])
    assert result["Mão"]["decision_style"] == "analytical"
    assert result["Thìn"]["leadership_orientation"] == "dominant"


def test_parse_valid_response_no_fence():
    raw = '{"Mão": {"decision_style": "patient", "leadership_orientation": "independent", "emotional_pattern": "steady", "communication_style": "quiet", "career_direction": "professional", "marriage_timing_rough": "30_35", "health_pattern_general": "strong"}}'
    result = parse_llm_response(raw, expected_candidates=["Mão"])
    assert result["Mão"]["decision_style"] == "patient"


def test_parse_rejects_invalid_enum():
    bad = '{"Mão": {"decision_style": "INVALID_VALUE"}}'
    with pytest.raises(ValueError, match="INVALID_VALUE"):
        parse_llm_response(bad, expected_candidates=["Mão"])


def test_parse_rejects_non_json():
    with pytest.raises(ValueError, match="non-JSON"):
        parse_llm_response("just some text", expected_candidates=["Mão"])
