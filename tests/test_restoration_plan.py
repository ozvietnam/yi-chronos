"""Tests for restoration plan workflow (Phase 1 → 2 → 3).

Validates:
- create_plan generates batches + sample analysis
- load_plan reads back JSON sidecar
- mark_batch updates batch status + log
- advance_phase moves through phases correctly
- append_log preserves history
- Phase 1 stays text-only (no wikilink wiring tests in this file)
- Markdown rendering includes copyright + phase tracker
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest


@pytest.fixture
def isolated_with_book(tmp_path, monkeypatch):
    """Set up an isolated DB + restored root + 1 corpus row pointing at a fake PDF."""
    from engine.yi_lexicon import store as st
    from engine.yi_lexicon.restoration import plan as plan_mod
    db = tmp_path / "lex.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    # Re-route RESTORED_ROOT to tmp
    monkeypatch.setattr(plan_mod, "RESTORED_ROOT", tmp_path / "restored")
    # Create fake PDF (empty file — pdfinfo will fail, plan uses fallback 0)
    fake_pdf = tmp_path / "fake-book.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n%fake\n")
    st.bootstrap_db()
    c = st.add_corpus(
        name="Sách Thử Phục Chế",
        author="Test Author",
        tier="A",
        pages_total=200,
        schools_tags=["common"],
        file_path=str(fake_pdf),
    )
    return st, plan_mod, c, tmp_path


def test_create_plan_generates_batches(isolated_with_book, monkeypatch):
    st, plan_mod, corpus, tmp = isolated_with_book

    # Skip OCR sampling (real pdftoppm needs valid PDF)
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})

    plan = plan_mod.create_plan(corpus.corpus_id)
    assert plan.corpus_id == corpus.corpus_id
    assert plan.book_name == "Sách Thử Phục Chế"
    assert plan.tier == "A"
    assert plan.pages_total == 200
    assert len(plan.phase1_batches) == 4  # 200 pages / 50 per batch
    assert plan.phase1_batches[0].page_start == 1
    assert plan.phase1_batches[0].page_end == 50
    assert plan.phase1_batches[-1].page_end == 200
    assert plan.current_phase == 1
    assert plan.phase1_status == "not_started"


def test_plan_eta_calculation(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    # 200 pages × 70s = 14000s = 3.89h
    assert plan.phase1_eta_hours == pytest.approx(3.89, abs=0.1)


def test_plan_load_returns_existing(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan1 = plan_mod.create_plan(corpus.corpus_id)
    plan2 = plan_mod.load_plan(corpus.corpus_id)
    assert plan2 is not None
    assert plan2.corpus_id == plan1.corpus_id
    assert plan2.pages_total == plan1.pages_total
    assert len(plan2.phase1_batches) == len(plan1.phase1_batches)


def test_plan_load_returns_none_when_missing(isolated_with_book):
    _, plan_mod, corpus, _ = isolated_with_book
    # No create_plan called
    p = plan_mod.load_plan(corpus.corpus_id)
    assert p is None


def test_create_plan_overwrite_false_keeps_existing(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    p1 = plan_mod.create_plan(corpus.corpus_id)
    # Add a custom note
    p1.notes = "đã edit tay"
    plan_mod.save_plan(p1)
    p2 = plan_mod.create_plan(corpus.corpus_id, overwrite=False)
    assert p2.notes == "đã edit tay"


def test_mark_batch_updates_status(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    first = plan.phase1_batches[0]
    b = plan_mod.mark_batch(plan, first.batch_id,
                             status="in_progress", pages_done=10)
    assert b.status == "in_progress"
    assert b.pages_done == 10
    assert b.started_at is not None
    b2 = plan_mod.mark_batch(plan, first.batch_id, status="done", pages_done=50)
    assert b2.status == "done"
    assert b2.finished_at is not None


def test_advance_phase_workflow(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    assert plan.current_phase == 1
    # Start phase 1
    plan_mod.advance_phase(plan, to_phase=1)
    assert plan.phase1_status == "in_progress"
    # → phase 2
    plan_mod.advance_phase(plan, to_phase=2)
    assert plan.current_phase == 2
    assert plan.phase1_status == "done"
    assert plan.phase2_status == "in_progress"
    # → phase 3
    plan_mod.advance_phase(plan, to_phase=3)
    assert plan.current_phase == 3
    assert plan.phase2_status == "done"
    assert plan.phase3_status == "in_progress"


def test_advance_phase_rejects_invalid(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    assert plan_mod.advance_phase(plan, to_phase=5) is False
    assert plan_mod.advance_phase(plan, to_phase=0) is False


def test_log_appends(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    initial = len(plan.log)
    plan_mod.append_log(plan, "test event 1")
    plan_mod.append_log(plan, "test event 2")
    assert len(plan.log) == initial + 2
    assert plan.log[-1]["event"] == "test event 2"
    assert plan.log[-1]["ts"] > 0


def test_plan_md_contains_phases_and_disclaimer(isolated_with_book, monkeypatch, tmp_path):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    md_path = plan_mod._plan_path(plan.book_slug)
    assert md_path.exists()
    md = md_path.read_text(encoding="utf-8")
    assert "Phase 1 — Phục dựng nguyên văn" in md
    assert "Phase 2 — Đọc kỹ đọc sâu" in md
    assert "Phase 3 — Wiki + Mapping" in md
    assert "KHÔNG vội" in md  # tuyên ngôn
    assert "qwen-vl" in md or "qwen2.5" in md  # pipeline config visible
    # Frontmatter
    assert "corpus_id:" in md
    assert "current_phase: 1" in md


def test_phase1_disabled_wikilink_documented(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    md = plan_mod._plan_path(plan.book_slug).read_text(encoding="utf-8")
    # Phase 1 must explicitly say wikilinks are off
    assert "Wikilinks" in md and "disabled" in md


def test_risks_flag_long_book(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    # Bump corpus pages to 800
    plan_mod_store = __import__("engine.yi_lexicon.store",
                                 fromlist=["update_corpus"])
    plan_mod_store.update_corpus(corpus.corpus_id, pages_total=800)
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "mờ",
                                          "has_chinese": True, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    assert any("Sách dài" in r for r in plan.risks)
    assert any("Hán" in r for r in plan.risks)
    assert any("mờ" in r.lower() for r in plan.risks)


def test_batch_split_for_50_pages(isolated_with_book, monkeypatch):
    _, plan_mod, corpus, _ = isolated_with_book
    plan_mod_store = __import__("engine.yi_lexicon.store",
                                 fromlist=["update_corpus"])
    plan_mod_store.update_corpus(corpus.corpus_id, pages_total=125)
    monkeypatch.setattr(plan_mod, "_sample_quick_ocr",
                        lambda *a, **kw: {"pages": [], "overall_quality": "good",
                                          "has_chinese": False, "has_footnotes": False})
    plan = plan_mod.create_plan(corpus.corpus_id)
    assert len(plan.phase1_batches) == 3
    assert plan.phase1_batches[0].page_start == 1
    assert plan.phase1_batches[0].page_end == 50
    assert plan.phase1_batches[1].page_end == 100
    assert plan.phase1_batches[2].page_end == 125  # last partial


def test_default_sample_distributed():
    from engine.yi_lexicon.restoration.plan import _default_sample
    s = _default_sample(1000)
    assert len(s) == 5
    assert s[0] < s[-1]
    assert s[0] >= 1
    assert s[-1] <= 1000
    # spread across the book
    assert s[2] in range(400, 600)
