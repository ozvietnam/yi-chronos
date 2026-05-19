"""Tests for Liên Hoa luận sự deeper layers."""

from __future__ import annotations

import pytest

from engine.lien_hoa import cast_lien_hoa
from engine.lien_hoa.luan_su_deeper import (
    composed_synthesis,
    interpret_career,
    interpret_children,
    interpret_lawsuit,
    interpret_study,
    luan_su_deeper,
    per_kts_narrative,
)


@pytest.fixture
def spread_test() -> dict:
    return cast_lien_hoa(
        number_right_hand=1, number_left_hand=8,
        question_text="test deeper", gender="nam",
    )


# ─── Per-KTS narrative ────────────────────────────────────────────────────────


def test_per_kts_narrative_returns_one_per_kts(spread_test):
    narratives = per_kts_narrative(spread_test)
    assert len(narratives) == spread_test["khong_thoi_count"]
    for n in narratives:
        assert "role_in_sequence" in n
        assert "phase_meaning" in n
        assert "transition_to_next" in n


def test_per_kts_narrative_tien_de_role(spread_test):
    """First KTS must be labeled Tiên đề."""
    narratives = per_kts_narrative(spread_test)
    assert "Tiên đề" in narratives[0]["role_in_sequence"]


def test_per_kts_narrative_last_kts_ends(spread_test):
    """Last KTS narrative must indicate end of sequence."""
    narratives = per_kts_narrative(spread_test)
    assert "Kết thúc" in narratives[-1]["transition_to_next"]


# ─── Extra domains ────────────────────────────────────────────────────────────


def test_interpret_children_returns_DomainReading(spread_test):
    r = interpret_children(spread_test)
    assert r.domain == "children"
    assert r.verdict
    assert r.explanation


def test_interpret_study_returns_DomainReading(spread_test):
    r = interpret_study(spread_test)
    assert r.domain == "study"


def test_interpret_lawsuit_returns_DomainReading(spread_test):
    r = interpret_lawsuit(spread_test)
    assert r.domain == "lawsuit"


def test_interpret_career_returns_DomainReading(spread_test):
    r = interpret_career(spread_test)
    assert r.domain == "career"


# ─── Synthesis ────────────────────────────────────────────────────────────────


def test_composed_synthesis_has_3_paragraphs(spread_test):
    domains = spread_test["luan_su"]["domain_readings"]
    syn = composed_synthesis(spread_test, domains)
    paragraphs = syn.split("\n\n")
    assert len(paragraphs) == 3


def test_composed_synthesis_mentions_gender_and_quai(spread_test):
    domains = spread_test["luan_su"]["domain_readings"]
    syn = composed_synthesis(spread_test, domains)
    assert "TA Nam" in syn
    # Tiên đề quẻ name (Bĩ for P=1, T=8 → 1+8=9 mod 6 = 3 hào động)
    assert "Bĩ" in syn or "đợt" in syn


# ─── Top-level deeper ─────────────────────────────────────────────────────────


def test_luan_su_deeper_complete(spread_test):
    deeper = luan_su_deeper(spread_test)
    assert "extra_domain_readings" in deeper
    assert "per_kts_narratives" in deeper
    assert "composed_synthesis_full" in deeper
    assert len(deeper["extra_domain_readings"]) == 4   # children + study + lawsuit + career
    assert len(deeper["per_kts_narratives"]) == spread_test["khong_thoi_count"]


def test_cast_lien_hoa_includes_luan_su_deeper(spread_test):
    """cast_lien_hoa should wire luan_su_deeper into output."""
    assert "luan_su_deeper" in spread_test
    deeper = spread_test["luan_su_deeper"]
    assert len(deeper["extra_domain_readings"]) == 4


def test_luan_su_deeper_is_json_serializable(spread_test):
    import json
    deeper = spread_test["luan_su_deeper"]
    s = json.dumps(deeper, ensure_ascii=False)
    decoded = json.loads(s)
    assert "composed_synthesis_full" in decoded
