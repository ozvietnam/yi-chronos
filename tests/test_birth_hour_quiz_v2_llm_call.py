"""Tests for LLM caller with retry + fallback (mocked provider)."""
from unittest.mock import patch, MagicMock
from engine.yi_wiki.birth_hour_quiz_v2.llm_call import call_trait_llm

CAND = [{"chi": "Mão", "pillars": {"year": {"stem": "A", "branch": "B"},
                                    "month": {"stem": "A", "branch": "B"},
                                    "day": {"stem": "A", "branch": "B"},
                                    "hour": {"stem": "A", "branch": "B"}}}]


def test_call_trait_llm_success():
    fake = '''```json
{"Mão": {"decision_style": "analytical", "leadership_orientation": "supportive",
         "emotional_pattern": "cool", "communication_style": "nuanced",
         "career_direction": "creative", "marriage_timing_rough": "25_30",
         "health_pattern_general": "on"}}
```'''
    with patch("engine.yi_wiki.birth_hour_quiz_v2.llm_call._provider_complete",
               return_value=fake):
        result = call_trait_llm(CAND)
    assert result["Mão"]["decision_style"] == "analytical"


def test_call_trait_llm_retries_on_invalid_json():
    bad = "not json at all"
    good = '{"Mão": {"decision_style": "analytical", "leadership_orientation": "dominant", "emotional_pattern": "cool", "communication_style": "direct", "career_direction": "corporate", "marriage_timing_rough": "som_25", "health_pattern_general": "strong"}}'
    mock = MagicMock(side_effect=[bad, good])
    with patch("engine.yi_wiki.birth_hour_quiz_v2.llm_call._provider_complete", mock):
        result = call_trait_llm(CAND)
    assert mock.call_count == 2
    assert result["Mão"]["leadership_orientation"] == "dominant"


def test_call_trait_llm_raises_on_total_failure():
    # Every provider in the chain (deepseek → lmstudio → anthropic) returns
    # unparseable text → all parse-fail → RuntimeError.
    mock = MagicMock(side_effect=lambda *a, **k: "not json")
    with patch("engine.yi_wiki.birth_hour_quiz_v2.llm_call._provider_complete", mock):
        try:
            call_trait_llm(CAND)
        except RuntimeError:
            return  # expected
        raise AssertionError("should have raised RuntimeError")
