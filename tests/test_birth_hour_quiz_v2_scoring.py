"""Tests for entropy + answer scoring + round convergence."""
import math
from engine.yi_wiki.birth_hour_quiz_v2.scoring import (
    entropy, score_answer, after_round,
)


def test_entropy_uniform_4():
    """4 candidates each unique → log2(4) = 2.0"""
    preds = {"Mão": "a", "Thìn": "b", "Tỵ": "c", "Ngọ": "d"}
    assert math.isclose(entropy(preds), 2.0, rel_tol=1e-6)


def test_entropy_split_2_2():
    """2/2 split → 1.0"""
    preds = {"Mão": "a", "Thìn": "b", "Tỵ": "a", "Ngọ": "b"}
    assert math.isclose(entropy(preds), 1.0, rel_tol=1e-6)


def test_entropy_all_same():
    preds = {"Mão": "x", "Thìn": "x", "Tỵ": "x"}
    assert entropy(preds) == 0


def test_entropy_empty():
    assert entropy({}) == 0.0


def test_score_answer_match_reward():
    candidates = ["Mão", "Thìn", "Tỵ"]
    question = {
        "id": "face_shape",
        "weight": 2.0,
        "options": [
            {"id": "dai", "candidates": ["Mão"]},
            {"id": "vuong", "candidates": ["Thìn"]},
            {"id": "nhon", "candidates": ["Tỵ"]},
            {"id": "unsure", "candidates": []},
        ],
    }
    delta = score_answer(candidates, question, "vuong")
    assert delta["Thìn"] == 2.0
    assert delta["Mão"] == -1.0   # mismatch: -0.5 × 2.0
    assert delta["Tỵ"] == -1.0


def test_score_answer_unsure_zero():
    candidates = ["Mão", "Thìn"]
    question = {"weight": 2.0, "options": [{"id": "unsure", "candidates": []}]}
    delta = score_answer(candidates, question, "unsure")
    assert all(v == 0 for v in delta.values())


def test_score_answer_unknown_option():
    """If chosen option ID not in question.options, return zeros."""
    candidates = ["Mão"]
    question = {"weight": 2.0, "options": [{"id": "dai", "candidates": ["Mão"]}]}
    delta = score_answer(candidates, question, "nonexistent")
    assert delta["Mão"] == 0


def test_after_round_clear_winner():
    scores = {"Mão": 10.0, "Thìn": 2.0, "Tỵ": 1.0}
    status, result = after_round(scores, ["Mão", "Thìn", "Tỵ"], round_num=1, max_rounds=3)
    assert status == "FINAL"
    assert result == "Mão"


def test_after_round_continue_drops_weak():
    scores = {"Mão": 10.0, "Thìn": 9.0, "Tỵ": 4.0, "Ngọ": 1.0}
    status, survivors = after_round(scores, ["Mão", "Thìn", "Tỵ", "Ngọ"], round_num=1, max_rounds=3)
    assert status == "CONTINUE"
    assert "Mão" in survivors and "Thìn" in survivors
    assert "Ngọ" not in survivors  # 1 < 0.5 × 10


def test_after_round_budget_exhausted():
    scores = {"Mão": 5.0, "Thìn": 4.0}
    status, result = after_round(scores, ["Mão", "Thìn"], round_num=3, max_rounds=3)
    assert status == "FINAL_UNCERTAIN"
    assert isinstance(result, list)
    assert "Mão" in result and "Thìn" in result


def test_after_round_empty_scores():
    status, result = after_round({}, [], round_num=1, max_rounds=3)
    assert status == "FINAL_UNCERTAIN"
