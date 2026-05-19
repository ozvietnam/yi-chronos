"""Entropy + answer scoring + round convergence."""
from __future__ import annotations

import math
from collections import Counter


def entropy(predictions: dict[str, str]) -> float:
    """Shannon entropy in bits over predicted values."""
    counts = Counter(predictions.values())
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def score_answer(
    candidates: list[str],
    question: dict,
    chosen_option_id: str,
) -> dict[str, float]:
    """Compute per-candidate score delta from user's answer.

    Match → +weight. Mismatch → -weight × 0.5. Unsure → 0. Unknown option → 0.
    """
    weight = question["weight"]
    chosen = next(
        (o for o in question["options"] if o["id"] == chosen_option_id),
        None,
    )
    if chosen is None or chosen_option_id == "unsure":
        return {c: 0.0 for c in candidates}

    matched = set(chosen["candidates"])
    return {
        c: (weight if c in matched else -weight * 0.5)
        for c in candidates
    }


def after_round(
    scores: dict[str, float],
    candidates_remaining: list[str],
    round_num: int,
    max_rounds: int,
) -> tuple[str, object]:
    """Decide whether to FINAL, FINAL_UNCERTAIN, or CONTINUE after a round.

    Returns:
        ("FINAL", "<chi>")              — clear winner
        ("FINAL_UNCERTAIN", [chi1, chi2]) — top 2 if budget exhausted or empty
        ("CONTINUE", [surviving_chis])  — keep going, drop weak (< 0.5×top)
    """
    if not scores:
        return ("FINAL_UNCERTAIN", [])

    sorted_chis = sorted(scores, key=scores.get, reverse=True)
    top_chi = sorted_chis[0]
    top_score = scores[top_chi]
    second_score = scores[sorted_chis[1]] if len(sorted_chis) > 1 else 0

    # Clear winner: margin > 50% of top
    if top_score > 0 and (top_score - second_score) / top_score > 0.5:
        return ("FINAL", top_chi)

    # Budget exhausted: return top 2
    if round_num >= max_rounds:
        return ("FINAL_UNCERTAIN", sorted_chis[:2])

    # Continue: drop candidates below threshold, cap at 6
    threshold = top_score * 0.5 if top_score > 0 else float("-inf")
    survivors = [c for c in candidates_remaining if scores[c] >= threshold][:6]
    return ("CONTINUE", survivors)
