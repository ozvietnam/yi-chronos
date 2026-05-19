"""Tests for quiz engine (strategy + candidate generation + question gen)."""
from engine.yi_wiki.birth_hour_quiz_v2.engine import (
    detect_strategy, generate_candidates_for_range, generate_questions,
    K_PER_ROUND, MAX_ROUNDS,
)


def test_detect_strategy_by_count():
    assert detect_strategy(["Mão", "Thìn"]) == "single_round"
    assert detect_strategy(["a"] * 6) == "single_round"
    assert detect_strategy(["a"] * 7) == "two_round"
    assert detect_strategy(["a"] * 9) == "two_round"
    assert detect_strategy(["a"] * 10) == "three_round"
    assert detect_strategy(["a"] * 12) == "three_round"


def test_k_per_round_total_matches_strategy():
    """Total questions must match strategy table in spec §2."""
    assert K_PER_ROUND["single_round"] * MAX_ROUNDS["single_round"] == 12
    assert K_PER_ROUND["two_round"]    * MAX_ROUNDS["two_round"]    == 12
    assert K_PER_ROUND["three_round"]  * MAX_ROUNDS["three_round"]  == 15


def test_generate_candidates_tight_range():
    chis = generate_candidates_for_range(7, 9)
    # Range 7-9 (inclusive) covers Thìn (7-9) only (Tỵ starts at 9)
    assert "Thìn" in chis
    assert len(chis) <= 2


def test_generate_candidates_medium_range():
    chis = generate_candidates_for_range(6, 12)
    # Hours 6-12 covers Mão (5-7), Thìn (7-9), Tỵ (9-11), Ngọ (11-13)
    assert set(chis).issuperset({"Mão", "Thìn", "Tỵ", "Ngọ"})


def test_generate_candidates_full_day():
    chis = generate_candidates_for_range(0, 23)
    assert len(chis) == 12


def test_generate_questions_picks_high_entropy_first():
    predictions = {
        "Mão":  {"face_shape": "dai", "body_height": "cao", "skin_tone": "trang"},
        "Thìn": {"face_shape": "vuong", "body_height": "cao", "skin_tone": "trang"},
        "Tỵ":   {"face_shape": "nhon", "body_height": "trung_binh", "skin_tone": "trang"},
        "Ngọ":  {"face_shape": "tron", "body_height": "trung_binh", "skin_tone": "trang"},
    }
    questions = generate_questions(
        strategy="single_round",
        candidates=list(predictions),
        predictions=predictions,
        used_dimensions=set(),
    )
    q_ids = [q["id"] for q in questions]
    # face_shape (entropy 2.0) should appear; skin_tone (entropy 0) should NOT
    assert "face_shape" in q_ids
    assert "skin_tone" not in q_ids
    # First question = highest weight
    assert questions[0]["weight"] >= questions[-1]["weight"]


def test_generate_questions_skips_used_dimensions():
    predictions = {
        "Mão": {"face_shape": "dai", "body_height": "cao"},
        "Thìn": {"face_shape": "vuong", "body_height": "trung_binh"},
    }
    questions = generate_questions(
        strategy="single_round",
        candidates=list(predictions),
        predictions=predictions,
        used_dimensions={"face_shape"},
    )
    q_ids = [q["id"] for q in questions]
    assert "face_shape" not in q_ids
    assert "body_height" in q_ids


def test_generate_questions_options_have_unsure():
    predictions = {
        "Mão": {"face_shape": "dai"},
        "Thìn": {"face_shape": "vuong"},
    }
    questions = generate_questions(
        strategy="single_round",
        candidates=list(predictions),
        predictions=predictions,
        used_dimensions=set(),
    )
    assert questions
    opts = questions[0]["options"]
    assert any(o["id"] == "unsure" for o in opts)
