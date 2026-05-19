from __future__ import annotations

from core.chronos import calculate_chronos_state
from core.yi64.narrative import (
    HEXAGRAM_STATE_PHRASES,
    ROLE_DESCRIPTION,
    ROLE_LABEL,
    build_narrative,
)


def test_narrative_returns_six_segments():
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    n = build_narrative(state)
    assert len(n.segments) == 6
    role_keys = [s.role_key for s in n.segments]
    assert role_keys == ["chanh", "ho", "bien", "giao", "phuc", "bao"]


def test_each_segment_has_known_role_label_and_description():
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    n = build_narrative(state)
    for s in n.segments:
        assert s.role_label == ROLE_LABEL[s.role_key]
        assert s.role_description == ROLE_DESCRIPTION[s.role_key]


def test_each_segment_has_state_phrase():
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    n = build_narrative(state)
    for s in n.segments:
        assert len(s.state_phrase) > 0


def test_all_64_hexagrams_have_state_phrases():
    """Every King Wen hexagram name should map to a state phrase."""
    from core.hexagram import list_hexagrams
    for hx in list_hexagrams():
        assert hx.name_vi in HEXAGRAM_STATE_PHRASES, \
            f"Missing state phrase for {hx.name_vi} ({hx.king_wen_index})"


def test_composed_text_is_state_only_no_advice_words():
    """Sanity check: composed text must not contain prescriptive advice verbs."""
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    n = build_narrative(state)
    forbidden = ["nên", "phải", "đừng", "hãy", "khuyên", "chắc chắn", "sẽ là"]
    text_lower = n.composed_text.lower()
    for word in forbidden:
        assert word not in text_lower, \
            f"Forbidden prescriptive word '{word}' in composed_text: {n.composed_text}"


def test_determinism_same_input_same_narrative():
    a = build_narrative(calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh"))
    b = build_narrative(calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh"))
    assert a.to_dict() == b.to_dict()


def test_narrative_exposes_method_id_and_source():
    state = calculate_chronos_state("2026-05-11T10:00:00", "Asia/Ho_Chi_Minh")
    n = build_narrative(state)
    assert n.method_id == "mai_hoa_nntt_v1"
    assert "Thiệu Khang Tiết" in n.source_ref
    assert "year_branch_idx" in n.derivation
