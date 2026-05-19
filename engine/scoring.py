from __future__ import annotations

from core.chronos import ChronosState


def calculate_scores(state: ChronosState, kp_index: float) -> dict[str, float]:
    moon = state.moon_phase.illumination
    solar = state.solar_term.solar_longitude / 360
    kp_norm = min(max(kp_index / 9, 0), 1)
    heaven = round((kp_norm * 0.55) + (moon * 0.25) + (solar * 0.20), 3)
    earth = round((0.35 + abs(0.5 - solar) * 0.3 + moon * 0.2), 3)
    instability = round(min(1.0, kp_norm * 0.65 + abs(0.5 - moon) * 0.35), 3)
    return {"heaven": heaven, "earth": earth, "instability": instability}

