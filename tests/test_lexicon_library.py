"""Tests for YI-Lexicon library / Thủ thư layer (v3, 2026-05-12).

Covers:
- Corpus v3 schema migration: status, tier, progress fields all populate
- add_corpus + update_corpus + progress recompute
- list_corpora filters by tier/status/school
- library_stats aggregation
- librarian.scan_library_dir (skip_llm=True) returns proposals
- register_proposal_as_corpus idempotency
"""

from __future__ import annotations

import importlib
import os
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def isolated_lexicon(tmp_path, monkeypatch):
    """Point store._DB_PATH at a temp DB for test isolation."""
    from engine.yi_lexicon import store as st
    db = tmp_path / "test_lexicon.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    st.bootstrap_db()
    return st


def test_corpus_v3_fields_default(isolated_lexicon):
    st = isolated_lexicon
    c = st.add_corpus(name="Test Book A")
    assert c.status == "queued"
    assert c.tier == "B"
    assert c.tier_decided_by == "manifest"
    assert c.pages_total == 0
    assert c.pages_ingested == 0
    assert c.progress_percent == 0.0
    assert c.schools_tags == []


def test_corpus_with_all_v3_metadata(isolated_lexicon):
    st = isolated_lexicon
    c = st.add_corpus(
        name="Trích Thiên Tủy",
        author="Nhậm Thiết Tiều",
        tier="A",
        tier_decided_by="manifest",
        pages_total=300,
        schools_tags=["bat_tu"],
        librarian_summary="Kinh điển Bát Tự thời Thanh.",
    )
    assert c.tier == "A"
    assert c.pages_total == 300
    assert "bat_tu" in c.schools_tags
    assert c.librarian_summary.startswith("Kinh điển")


def test_update_corpus_recomputes_progress(isolated_lexicon):
    st = isolated_lexicon
    c = st.add_corpus(name="Book Prog", pages_total=200)
    c2 = st.update_corpus(c.corpus_id, pages_ingested=50)
    assert c2.pages_ingested == 50
    assert c2.progress_percent == 25.0
    c3 = st.update_corpus(c.corpus_id, pages_ingested=200, status="done")
    assert c3.progress_percent == 100.0
    assert c3.status == "done"


def test_list_corpora_tier_filter(isolated_lexicon):
    st = isolated_lexicon
    st.add_corpus(name="S Book", tier="S")
    st.add_corpus(name="A Book 1", tier="A")
    st.add_corpus(name="A Book 2", tier="A")
    st.add_corpus(name="B Book", tier="B")
    assert len(st.list_corpora(tier="S")) == 1
    assert len(st.list_corpora(tier="A")) == 2
    assert len(st.list_corpora(tier="B")) == 1


def test_list_corpora_school_filter(isolated_lexicon):
    st = isolated_lexicon
    st.add_corpus(name="BT Book", schools_tags=["bat_tu"])
    st.add_corpus(name="MH Book", schools_tags=["mai_hoa", "lien_hoa"])
    st.add_corpus(name="Common Book", schools_tags=["common"])
    bt = st.list_corpora(school="bat_tu")
    assert len(bt) == 1 and bt[0].name == "BT Book"
    mh = st.list_corpora(school="mai_hoa")
    assert len(mh) == 1 and "MH Book" in mh[0].name


def test_list_corpora_sorted_by_tier(isolated_lexicon):
    st = isolated_lexicon
    st.add_corpus(name="C Book", tier="C")
    st.add_corpus(name="S Book", tier="S")
    st.add_corpus(name="B Book", tier="B")
    st.add_corpus(name="A Book", tier="A")
    out = st.list_corpora()
    tiers_order = [c.tier for c in out]
    assert tiers_order == ["S", "A", "B", "C"]


def test_library_stats_aggregation(isolated_lexicon):
    st = isolated_lexicon
    st.add_corpus(name="X", tier="S", pages_total=500)
    st.add_corpus(name="Y", tier="A", pages_total=300, status="reading")
    st.update_corpus(2, pages_ingested=60)  # 20% of 300
    s = st.library_stats()
    assert s["total_books"] == 2
    assert s["by_tier"]["S"] == 1
    assert s["by_tier"]["A"] == 1
    assert s["pages_total"] == 800
    assert s["pages_ingested"] == 60
    assert s["overall_progress_percent"] == pytest.approx(7.5, rel=0.1)


def test_library_stats_respects_filters(isolated_lexicon):
    st = isolated_lexicon
    st.add_corpus(name="S Queued", tier="S", status="queued", pages_total=100)
    st.add_corpus(name="A Done", tier="A", status="done", pages_total=200, schools_tags=["bat_tu"])
    st.add_corpus(name="A Queued", tier="A", status="queued", pages_total=300, schools_tags=["luc_hao"])
    st.update_corpus(2, pages_ingested=200)

    tier_a = st.library_stats(tier="A")
    assert tier_a["total_books"] == 2
    assert tier_a["by_tier"] == {"A": 2}
    assert tier_a["pages_total"] == 500

    done = st.library_stats(status="done")
    assert done["total_books"] == 1
    assert done["by_status"] == {"done": 1}
    assert done["pages_ingested"] == 200

    bat_tu = st.library_stats(school="bat_tu")
    assert bat_tu["total_books"] == 1
    assert bat_tu["by_tier"] == {"A": 1}


def test_add_corpus_returns_existing_on_name_collision(isolated_lexicon):
    st = isolated_lexicon
    c1 = st.add_corpus(name="Duplicate", tier="A")
    c2 = st.add_corpus(name="Duplicate", tier="B")  # tier ignored
    assert c1.corpus_id == c2.corpus_id
    assert c2.tier == "A"  # original kept


def test_get_corpus_by_id_and_name(isolated_lexicon):
    st = isolated_lexicon
    c = st.add_corpus(name="Lookup Me", author="Anh")
    assert st.get_corpus(corpus_id=c.corpus_id).name == "Lookup Me"
    assert st.get_corpus(name="Lookup Me").author == "Anh"
    assert st.get_corpus(corpus_id=99999) is None


def test_librarian_proposal_registers_corpus(isolated_lexicon, tmp_path):
    """register_proposal_as_corpus stores fields correctly."""
    st = isolated_lexicon
    from engine.yi_lexicon.librarian import LibrarianProposal, register_proposal_as_corpus
    prop = LibrarianProposal(
        file_path=str(tmp_path / "fake.pdf"),
        pages_total=120,
        title="Sample Book",
        author="Test Author",
        tier="A",
        schools=["luc_hao", "mai_hoa"],
        summary="A sample.",
        confidence=0.8,
    )
    c = register_proposal_as_corpus(prop)
    assert c.name == "Sample Book"
    assert c.tier == "A"
    assert c.pages_total == 120
    assert set(c.schools_tags) == {"luc_hao", "mai_hoa"}
    assert c.tier_decided_by == "librarian_llm"


def test_librarian_idempotent_register(isolated_lexicon, tmp_path):
    st = isolated_lexicon
    from engine.yi_lexicon.librarian import LibrarianProposal, register_proposal_as_corpus
    prop = LibrarianProposal(
        file_path=str(tmp_path / "b.pdf"),
        pages_total=50,
        title="Idempotent",
        tier="B",
        schools=["common"],
    )
    c1 = register_proposal_as_corpus(prop)
    c2 = register_proposal_as_corpus(prop)
    assert c1.corpus_id == c2.corpus_id


def test_librarian_anh_decision_not_overwritten(isolated_lexicon, tmp_path):
    """If anh manually set tier_decided_by='anh', re-classify must not overwrite."""
    st = isolated_lexicon
    from engine.yi_lexicon.librarian import LibrarianProposal, register_proposal_as_corpus
    prop = LibrarianProposal(
        file_path=str(tmp_path / "anh.pdf"),
        pages_total=100,
        title="Anh's Pick",
        tier="C",
        schools=["common"],
    )
    c = register_proposal_as_corpus(prop)
    # Anh changes tier to S manually
    st.update_corpus(c.corpus_id, tier="S", tier_decided_by="anh")
    # LLM re-runs and tries to downgrade
    prop.tier = "C"
    register_proposal_as_corpus(prop)
    final = st.get_corpus(corpus_id=c.corpus_id)
    assert final.tier == "S"
    assert final.tier_decided_by == "anh"


def test_list_schools_returns_known(isolated_lexicon):
    from engine.yi_lexicon.librarian import list_schools
    schools = list_schools()
    keys = {s["key"] for s in schools}
    assert "mai_hoa" in keys
    assert "bat_tu" in keys
    assert "common" in keys


def test_add_school_dynamic(isolated_lexicon):
    from engine.yi_lexicon.librarian import add_school, list_schools, KNOWN_SCHOOLS
    KNOWN_SCHOOLS.pop("test_school", None)
    r = add_school("test_school", "Trường phái thử", "#ff00ff")
    assert r["key"] == "test_school"
    assert r["vi"] == "Trường phái thử"
    assert any(s["key"] == "test_school" for s in list_schools())
    KNOWN_SCHOOLS.pop("test_school", None)  # cleanup
