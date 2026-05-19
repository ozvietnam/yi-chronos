from __future__ import annotations

import pytest

from core.chronos import calculate_chronos_state
from engine.personal_quai import (
    BRANCH_CLASH,
    CONTROLS,
    GENERATES,
    THREE_HARMONY_GROUPS,
    TIET_KHI_ELEMENT,
    TRIGRAM_ELEMENT,
    _branch_interaction_score,
    _element_relation_score,
    compute_natal_hexagram,
    score_compatibility,
)


@pytest.fixture(scope="module")
def natal():
    return compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")


def test_natal_has_all_required_fields(natal):
    assert natal.method_id == "mai_hoa_nntt_v1"
    assert natal.primary_binary
    assert natal.primary_name
    assert 1 <= natal.primary_king_wen <= 64
    assert natal.upper_trigram in TRIGRAM_ELEMENT
    assert natal.lower_trigram in TRIGRAM_ELEMENT
    assert 1 <= natal.moving_line <= 6
    assert set(natal.derived_hexagrams.keys()) == {"chanh", "ho", "bien", "giao", "phuc", "bao"}


def test_natal_determinism():
    a = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    b = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    assert a.primary_binary == b.primary_binary
    assert a.derivation == b.derivation


def test_compatibility_in_range(natal):
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    breakdown = score_compatibility(natal, state)
    assert 0 <= breakdown.final_score <= 100


def test_self_match_yields_high_score():
    """Compatibility of natal moment vs natal moment should hit self-match bonus."""
    natal = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    state = calculate_chronos_state("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    breakdown = score_compatibility(natal, state)
    assert breakdown.self_match_bonus == 25
    assert breakdown.final_score >= 70


def test_element_relation_score_symmetric_for_same():
    score, label = _element_relation_score("mộc", "mộc")
    assert score == 10
    assert label == "tỷ hòa"


def test_element_relation_sinh_positive():
    # Mộc sinh hỏa.
    score, _ = _element_relation_score("mộc", "hỏa")
    assert score > 0


def test_element_relation_khac_negative():
    # Mộc khắc thổ.
    score, _ = _element_relation_score("mộc", "thổ")
    assert score < 0


def test_branch_clash_negative():
    # Tý xung Ngọ.
    score, label = _branch_interaction_score("Tý", "Ngọ")
    assert score == -25
    assert "xung" in label


def test_branch_six_harmony_positive():
    # Tý hợp Sửu.
    score, label = _branch_interaction_score("Tý", "Sửu")
    assert score == 18
    assert "lục hợp" in label


def test_branch_three_harmony():
    # Thân Tý Thìn.
    score, label = _branch_interaction_score("Thân", "Tý")
    assert score > 0
    assert "tam hợp" in label


def test_branch_clash_table_complete():
    """Every branch should have a clash partner; clash is symmetric."""
    branches = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")
    for b in branches:
        assert b in BRANCH_CLASH
        partner = BRANCH_CLASH[b]
        assert BRANCH_CLASH[partner] == b


def test_three_harmony_groups_complete():
    """4 groups × 3 branches = 12 branches total."""
    flat = set()
    for group in THREE_HARMONY_GROUPS:
        assert len(group) == 3
        flat |= group
    assert len(flat) == 12


def test_tiet_khi_table_covers_24():
    assert len(TIET_KHI_ELEMENT) == 24
    elements_used = set(TIET_KHI_ELEMENT.values())
    assert elements_used <= {"mộc", "hỏa", "thổ", "kim", "thủy"}


def test_breakdown_serializable(natal):
    import json
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    breakdown = score_compatibility(natal, state)
    payload = json.dumps(breakdown.to_dict())
    restored = json.loads(payload)
    assert "final_score" in restored
    assert "notes" in restored
    assert isinstance(restored["notes"], list)


def test_natal_serializable(natal):
    import json
    payload = json.dumps(natal.to_dict())
    restored = json.loads(payload)
    assert restored["primary_binary"] == natal.primary_binary
    assert "derived_hexagrams" in restored
