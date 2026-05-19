import math

from core.chronos import calculate_chronos_state
from core.temporal_encoder import encode_temporal_features


def test_temporal_encoder_returns_fixed_finite_vector():
    state = calculate_chronos_state("2026-05-08T09:30:00", "Asia/Ho_Chi_Minh")
    features = encode_temporal_features(state)

    assert len(features.vector) == 12
    assert all(math.isfinite(value) for value in features.vector)
    assert features.algorithm_version == "mvp-0.1.0"


def test_same_input_produces_same_chronos_state():
    first = calculate_chronos_state("2026-05-08T09:30:00", "Asia/Ho_Chi_Minh")
    second = calculate_chronos_state("2026-05-08T09:30:00", "Asia/Ho_Chi_Minh")

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.timestamp_utc == "2026-05-08T02:30:00Z"
