"""Tests for tiered conflict-aware mapping per anh's tuyên ngôn (2026-05-12).

Verifies:
- Same school + same dim_type + different dim_value → conflict group created
- Different schools → NOT a conflict (each school independent)
- Resolve conflict → primary set + others demoted
- Tier ordering helper works
- Tier manifest loader reads YAML correctly
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_db(monkeypatch, tmp_path):
    tmp_db = tmp_path / "lexicon.sqlite3"
    monkeypatch.setattr("engine.yi_lexicon.store._DB_PATH", tmp_db)
    yield


# ─── Schema migration ───────────────────────────────────────────────────────


def test_v2_columns_added_to_mappings():
    from engine.yi_lexicon import add_concept, add_mapping
    from engine.yi_lexicon.store import _conn, bootstrap_db

    bootstrap_db()
    c = add_concept(canonical_vi="test", concept_type="concept")
    m = add_mapping(
        c.concept_id, "ngu_hanh", "mộc",
        source_tier="A", source_book="Test Book",
        source_page=42, source_quote="lá thuộc Mộc theo Hoàng Đế Nội Kinh",
    )
    assert m.source_tier == "A"
    assert m.source_book == "Test Book"
    assert m.source_page == 42
    assert "Hoàng Đế" in m.source_quote


# ─── Conflict detection ─────────────────────────────────────────────────────


def test_same_school_different_value_creates_conflict():
    """vàng → Thổ (sách A) vs vàng → Kim (sách B) → conflict group."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts

    c = add_concept(canonical_vi="vàng", concept_type="color")
    m1 = add_mapping(
        c.concept_id, "ngu_hanh", "thổ",
        school="common", source_tier="A",
        source_book="Học Thuyết Âm Dương Ngũ Hành",
    )
    m2 = add_mapping(
        c.concept_id, "ngu_hanh", "kim",
        school="common", source_tier="B",
        source_book="Hà Đồ trong văn minh Đại Việt",
    )
    assert m1.conflict_flag == 0  # first mapping not flagged yet
    # After m2 inserted, both should be flagged
    conflicts = list_conflicts(status="open")
    assert len(conflicts) == 1
    assert conflicts[0]["concept_vi"] == "vàng"
    assert conflicts[0]["dim_type"] == "ngu_hanh"
    assert len(conflicts[0]["mappings"]) == 2


def test_different_school_NOT_a_conflict():
    """Per tuyên ngôn nguyên tắc 2: mỗi trường phái độc lập.

    Bát Tự nói X, Tử Vi nói Y → KHÔNG conflict (each valid trong school).
    """
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts

    c = add_concept(canonical_vi="số 5", concept_type="number")
    add_mapping(c.concept_id, "bat_quai", "Tốn",
                school="mai_hoa", source_tier="A")
    add_mapping(c.concept_id, "ngu_hanh", "thổ",   # different dim_type → no conflict
                school="mai_hoa", source_tier="A")
    add_mapping(c.concept_id, "bat_quai", "Càn",  # different SCHOOL — no conflict
                school="luc_hao", source_tier="A")

    conflicts = list_conflicts(status="open")
    assert conflicts == [], "Same dim_type but different school must not conflict"


def test_exact_duplicate_returns_existing_no_conflict():
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts

    c = add_concept(canonical_vi="đỏ", concept_type="color")
    m1 = add_mapping(c.concept_id, "ngu_hanh", "hỏa", school="common")
    m2 = add_mapping(c.concept_id, "ngu_hanh", "hỏa", school="common")
    assert m1.mapping_id == m2.mapping_id
    assert list_conflicts(status="open") == []


# ─── Resolution ─────────────────────────────────────────────────────────────


def test_resolve_conflict_picks_primary():
    """Anh chọn primary → primary verified=1, others demoted (conflict_flag=0 but alternative)."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts, resolve_conflict, mappings_for

    c = add_concept(canonical_vi="trắng", concept_type="color")
    m_thoa = add_mapping(c.concept_id, "ngu_hanh", "thổ", school="common", source_tier="C")
    m_kim = add_mapping(c.concept_id, "ngu_hanh", "kim", school="common", source_tier="A",
                       source_book="Hoàng Đế Nội Kinh")
    cgs = list_conflicts(status="open")
    assert len(cgs) == 1
    cg = cgs[0]

    ok = resolve_conflict(
        cg["conflict_group_id"],
        primary_mapping_id=m_kim.mapping_id,
        status="resolved",
        anh_note="Kim correct per HĐNK Tier A",
    )
    assert ok

    # No more open conflicts
    assert list_conflicts(status="open") == []
    # Primary verified
    mps = mappings_for(c.concept_id)
    primary = next(m for m in mps if m.mapping_id == m_kim.mapping_id)
    assert primary.verified_by_anh == 1


def test_resolve_kept_all():
    """status='kept_all' → all mappings valid (multi-school disagree but each valid)."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts, mappings_for, resolve_conflict

    c = add_concept(canonical_vi="số 1", concept_type="number")
    add_mapping(c.concept_id, "bat_quai", "Càn", school="common", source_tier="A")
    add_mapping(c.concept_id, "bat_quai", "Khảm", school="common", source_tier="A")

    cg = list_conflicts(status="open")[0]
    resolve_conflict(cg["conflict_group_id"], status="kept_all",
                     anh_note="Tiên thiên: Càn. Hậu thiên: Khảm. Both correct in context.")

    # All mappings should have conflict_flag=0 after kept_all
    mps = mappings_for(c.concept_id)
    assert all(m.conflict_flag == 0 for m in mps)
    # No open conflicts
    assert list_conflicts(status="open") == []


# ─── Tier helpers ───────────────────────────────────────────────────────────


def test_tier_compare():
    from engine.yi_lexicon.store import _tier_compare

    assert _tier_compare("S", "A") < 0
    assert _tier_compare("A", "S") > 0
    assert _tier_compare("B", "B") == 0
    assert _tier_compare("S", "C") < 0


# ─── Manifest loader ────────────────────────────────────────────────────────


def test_manifest_loads_books():
    from engine.yi_lexicon.tiers import get_book_meta, list_books_by_tier, reload_manifest

    reload_manifest()
    # Known TIER S book
    book = get_book_meta("kinh_dich_ngo_tat_to")
    assert book is not None
    assert book.tier == "S"
    assert "Ngô Tất Tố" in book.author or "Ngô Tất Tố" in book.title

    # Tier S list non-empty
    tier_s = list_books_by_tier("S")
    assert len(tier_s) >= 1


def test_manifest_lookup_by_filename():
    from engine.yi_lexicon.tiers import get_book_meta_for_file, get_tier_for_file

    tier = get_tier_for_file("Kinh Dich Tron Bo - Ngo Tat To.pdf")
    assert tier == "S"

    book = get_book_meta_for_file("Trích Thiên tuỷ bình chú (Full)- Nhậm Thiết Tiều.pdf")
    assert book is not None
    assert book.tier == "A"
    assert "bat_tu" in book.schools


def test_reading_plan_has_weeks():
    from engine.yi_lexicon.tiers import current_reading_week, reading_plan

    plan = reading_plan()
    assert len(plan) >= 6, "Expected at least 6 weeks of reading plan"
    # Current pending week should be week 1 (Foundation)
    cur = current_reading_week()
    assert cur is not None
    assert cur["week"] == 1


# ─── Mappings query with conflict flag ──────────────────────────────────────


def test_mappings_for_includes_conflict_status():
    from engine.yi_lexicon import add_concept, add_mapping, mappings_for

    c = add_concept(canonical_vi="nâu", concept_type="color")
    add_mapping(c.concept_id, "ngu_hanh", "thổ", school="common", source_tier="A")
    add_mapping(c.concept_id, "ngu_hanh", "mộc", school="common", source_tier="C")

    mps = mappings_for(c.concept_id)
    # Both should be in conflict
    assert sum(1 for m in mps if m.conflict_flag == 1) == 2
    # Both have conflict_group_id set
    assert all(m.conflict_group_id is not None for m in mps)


def test_case_insensitive_duplicate_no_conflict():
    """'thủy' và 'Thủy' là same fact — không tạo conflict."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts

    c = add_concept(canonical_vi="Thủy element", concept_type="concept")
    m1 = add_mapping(c.concept_id, "ngu_hanh", "thủy", school="common")
    m2 = add_mapping(c.concept_id, "ngu_hanh", "Thủy", school="common")
    # Should dedupe via case-insensitive match
    assert m1.mapping_id == m2.mapping_id
    assert list_conflicts(status="open") == []


def test_multi_value_dim_types_allow_multiple():
    """Concept có thể map nhiều giá trị trên `khac`, `huong`, etc. — không conflict."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts, mappings_for

    c = add_concept(canonical_vi="Thủy", concept_type="concept")
    # Cả 2 đều valid — 1 là Sinh số, 6 là Thành số
    add_mapping(c.concept_id, "khac", "số 1", school="common")
    add_mapping(c.concept_id, "khac", "số 6", school="common")
    # Concept Lạc Thư có 9 số ở 9 hướng — multiple `huong` mappings OK
    add_mapping(c.concept_id, "huong", "Bắc", school="common")
    add_mapping(c.concept_id, "huong", "Đông", school="common")

    assert list_conflicts(status="open") == []
    mps = mappings_for(c.concept_id)
    assert len(mps) == 4
    assert all(m.conflict_flag == 0 for m in mps)


def test_canonical_dim_type_single_value_still_conflicts():
    """Canonical dim_types (ngu_hanh, bat_quai, am_duong) vẫn phải single-value."""
    from engine.yi_lexicon import add_concept, add_mapping, list_conflicts

    c = add_concept(canonical_vi="vàng", concept_type="color")
    add_mapping(c.concept_id, "ngu_hanh", "thổ", school="common", source_tier="A")
    add_mapping(c.concept_id, "ngu_hanh", "kim", school="common", source_tier="B")
    # Real conflict — same dim_type, different value, NOT in MULTI_VALUE list
    conflicts = list_conflicts(status="open")
    assert len(conflicts) == 1
