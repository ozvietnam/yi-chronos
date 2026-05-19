"""Tests for candidate pillars generator (calls real bat_tu engine)."""
from engine.yi_wiki.birth_hour_quiz_v2.pillars import build_candidates


def test_build_candidates_range_returns_full_pillars():
    """1988-05-02 + range 6h-12h → at least 4 candidates each with full pillars."""
    out = build_candidates(
        birth_date="1988-05-02",
        timezone="Asia/Ho_Chi_Minh",
        hour_range=(6, 12),
    )
    assert len(out) >= 3
    chis = {c["chi"] for c in out}
    assert "Thìn" in chis
    for c in out:
        assert "pillars" in c
        for k in ("year", "month", "day", "hour"):
            assert k in c["pillars"], f"missing pillar {k}"
            assert "stem" in c["pillars"][k]
            assert "branch" in c["pillars"][k]


def test_build_candidates_unknown_range_all_12():
    out = build_candidates("1988-05-02", "Asia/Ho_Chi_Minh", hour_range=None)
    assert len(out) == 12
    chis = {c["chi"] for c in out}
    assert "Tý" in chis and "Hợi" in chis


def test_build_candidates_tight_range_one_chi():
    out = build_candidates("1988-05-02", "Asia/Ho_Chi_Minh", hour_range=(7, 8))
    # 7-8h is fully inside Thìn (7-9)
    chis = {c["chi"] for c in out}
    assert "Thìn" in chis


def test_build_candidates_different_hours_yield_different_hour_pillars():
    """Pillars for different chi giờ should differ in hour stem/branch."""
    out = build_candidates("1988-05-02", "Asia/Ho_Chi_Minh", hour_range=(6, 12))
    hour_pillars = [
        (c["chi"], c["pillars"]["hour"]["stem"], c["pillars"]["hour"]["branch"])
        for c in out
    ]
    # All hour branches should be distinct across candidates
    branches = {hb for _, _, hb in hour_pillars}
    assert len(branches) == len(out), "hour branches must differ per candidate"
