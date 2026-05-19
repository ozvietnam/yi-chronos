from __future__ import annotations


def calculate_sync_score(personal_vector: dict[str, object], universe_scores: dict[str, float]) -> float:
    bias = personal_vector["five_element_bias"]
    assert isinstance(bias, dict)
    water = float(bias.get("thủy", 0))
    fire = float(bias.get("hỏa", 0))
    heaven = universe_scores["heaven"]
    instability = universe_scores["instability"]
    score = 0.45 + heaven * 0.25 + (1 - instability) * 0.2 + (water + fire) * 0.1
    return round(min(max(score, 0), 1), 3)
