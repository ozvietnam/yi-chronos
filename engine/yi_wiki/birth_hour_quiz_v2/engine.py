"""Quiz strategy detection + candidate generation + question generation."""
from __future__ import annotations

from collections import defaultdict

from .rules.branches import BRANCHES, HOUR_RANGES
from .scoring import entropy
from .templates import TRAIT_TEMPLATES


K_PER_ROUND = {
    "single_round": 12,
    "two_round":     6,
    "three_round":   5,
}

MAX_ROUNDS = {
    "single_round": 1,
    "two_round":    2,
    "three_round":  3,
}


def detect_strategy(candidates: list[str]) -> str:
    n = len(candidates)
    if n <= 6:
        return "single_round"
    if n <= 9:
        return "two_round"
    return "three_round"


def generate_candidates_for_range(start_hour: int, end_hour: int) -> list[str]:
    """Generate list of chi giờ falling within [start, end] hour range (inclusive).

    Edge cases:
    - start > end: wraps midnight (e.g., 22 → 2 covers Hợi, Tý, Sửu)
    - 0-23: all 12 chi
    """
    # Build set of hours covered by the range (inclusive of both endpoints)
    if start_hour > end_hour:
        range_hours = set(range(start_hour, 24)) | set(range(0, end_hour + 1))
    else:
        range_hours = set(range(start_hour, end_hour + 1))

    out = []
    for chi in BRANCHES:
        chi_start, chi_end = HOUR_RANGES[chi]
        if chi_start > chi_end:  # Tý wraps midnight
            chi_hours = set(range(chi_start, 24)) | set(range(0, chi_end))
        else:
            chi_hours = set(range(chi_start, chi_end))
        if chi_hours & range_hours:
            out.append(chi)
    return out


def generate_questions(
    strategy: str,
    candidates: list[str],
    predictions: dict[str, dict[str, str]],
    used_dimensions: set[str],
) -> list[dict]:
    """Generate K=K_PER_ROUND[strategy] highest-entropy questions for this round.

    Each question has:
      - id: trait_id
      - question: Vietnamese text
      - domain: category
      - options: list of {id, label, candidates} + final unsure option
      - weight: entropy value
    """
    K = K_PER_ROUND[strategy]

    entropies = {}
    for trait in TRAIT_TEMPLATES:
        if trait in used_dimensions:
            continue
        trait_preds = {
            c: predictions[c].get(trait, "unknown")
            for c in candidates
            if c in predictions
        }
        if not trait_preds:
            continue
        h = entropy(trait_preds)
        if h > 0:
            entropies[trait] = h

    top = sorted(entropies.items(), key=lambda x: -x[1])[:K]
    return [_build_question(trait, h, predictions, candidates) for trait, h in top]


def _build_question(
    trait: str,
    weight: float,
    predictions: dict[str, dict[str, str]],
    candidates: list[str],
) -> dict:
    """Build one question with candidates grouped by predicted value."""
    template = TRAIT_TEMPLATES[trait]
    groups: dict[str, list[str]] = defaultdict(list)
    for chi in candidates:
        value = predictions[chi].get(trait, "unknown")
        groups[value].append(chi)

    options = []
    for value, chis in groups.items():
        if value not in template["value_labels"]:
            continue
        options.append({
            "id": value,
            "label": template["value_labels"][value],
            "candidates": chis,
        })
    options.append({
        "id": "unsure",
        "label": "Tôi không rõ / khó nói",
        "candidates": [],
    })

    return {
        "id": trait,
        "question": template["question_vi"],
        "domain": template["domain"],
        "options": options,
        "weight": weight,
    }
