"""Tests for engine.yi_publishing.onboarding orchestrator.

Uses mocked MinerU runner to avoid real OCR subprocess (~3 min real time).
End-to-end runs the full Stage 1.2 → 2.2 pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def real_minilike_pdf(tmp_path: Path) -> Path:
    """Build a 20-page PDF with mixed content for full-pipeline testing."""
    import fitz

    doc = fitz.open()
    toc = []

    # Cover
    cover = doc.new_page(width=595, height=842)
    cover.insert_text((100, 200), "BOOK COVER", fontsize=36)

    # Chapter 1 (pages 2-7)
    for i in range(2, 8):
        page = doc.new_page(width=595, height=842)
        if i == 2:
            page.insert_text((100, 80), "Chapter 1: Introduction", fontsize=18)
        for row in range(20):
            page.insert_text((60, 120 + row * 25),
                             "Lorem ipsum dolor sit amet consectetur",
                             fontsize=10)

    # Chapter 2 (pages 8-14)
    for i in range(8, 15):
        page = doc.new_page(width=595, height=842)
        if i == 8:
            page.insert_text((100, 80), "Chapter 2: Principles", fontsize=18)
        for row in range(20):
            page.insert_text((60, 120 + row * 25),
                             "Principle content goes here",
                             fontsize=10)

    # Chapter 3 — Appendix (pages 15-20)
    for i in range(15, 21):
        page = doc.new_page(width=595, height=842)
        if i == 15:
            page.insert_text((100, 80), "Appendix A: Reference", fontsize=18)

    # Embed bookmarks for TOC
    doc.set_toc([
        [1, "Chapter 1: Introduction", 2],
        [1, "Chapter 2: Principles", 8],
        [1, "Appendix A: Reference", 15],
    ])

    out = tmp_path / "minilike.pdf"
    doc.save(out)
    doc.close()
    return out


@pytest.fixture
def mock_mineru_runner():
    """Always returns clean output with no equations (winner = default)."""
    def runner(*, pdf_path, output_root, start, end, backend, language, formula_enable, **kwargs):
        book_id = pdf_path.stem
        out = output_root / book_id / "auto"
        out.mkdir(parents=True, exist_ok=True)
        pages = []
        for _ in range(start, end + 1):
            pages.append([{
                "type": "paragraph",
                "content": {
                    "paragraph_content": [
                        {"type": "text", "content": "hello world"},
                    ],
                },
                "bbox": [0, 0, 100, 100],
            }])
        (out / f"{book_id}_content_list_v2.json").write_text(
            json.dumps(pages, ensure_ascii=False), encoding="utf-8"
        )
    return runner


# ─── End-to-end orchestrator ─────────────────────────────────────────────────


def test_onboard_book_creates_all_artifacts(
    real_minilike_pdf: Path, mock_mineru_runner, tmp_path: Path
):
    from engine.yi_publishing.onboarding import onboard_book

    out = tmp_path / "onboarding"
    summary = onboard_book(
        book_id="minilike",
        pdf_path=real_minilike_pdf,
        output_dir=out,
        n_sample_pages=2,
        mineru_runner=mock_mineru_runner,
    )

    # Summary fields
    assert summary["book_id"] == "minilike"
    assert summary["page_count"] == 20
    assert "profile" in summary
    assert "ocr_config" in summary
    assert "toc" in summary
    assert "plan" in summary

    # Artifacts exist
    assert (out / "page_types.json").exists()
    assert (out / "thumbnails").exists()
    assert len(list((out / "thumbnails").glob("p*.jpg"))) == 20
    assert (out / "book_profile.json").exists()
    assert (out / "_TOC.md").exists()
    assert (out / "_OCR-CONFIG.json").exists()
    assert (out / "_READING-PLAN.md").exists()
    assert (out / "_TRANSLATION-PLAN.md").exists()
    assert (out / "_LLM-ROUTING.md").exists()
    assert (out / "_PLAN-SUMMARY.json").exists()
    assert (out / "onboarding_log.json").exists()


def test_onboard_book_detects_bookmarks_toc(
    real_minilike_pdf: Path, mock_mineru_runner, tmp_path: Path
):
    from engine.yi_publishing.onboarding import onboard_book

    out = tmp_path / "onboarding"
    summary = onboard_book(
        book_id="minilike",
        pdf_path=real_minilike_pdf,
        output_dir=out,
        n_sample_pages=2,
        mineru_runner=mock_mineru_runner,
    )
    assert summary["toc"]["strategy"] == "bookmarks"
    assert summary["toc"]["chapter_count"] == 3


def test_onboard_book_skip_thumbnails_on_rerun(
    real_minilike_pdf: Path, mock_mineru_runner, tmp_path: Path
):
    from engine.yi_publishing.onboarding import onboard_book

    out = tmp_path / "onboarding"
    onboard_book(
        book_id="minilike",
        pdf_path=real_minilike_pdf,
        output_dir=out,
        n_sample_pages=2,
        mineru_runner=mock_mineru_runner,
    )
    # Second run with skip_thumbnails=True should reuse cached page_types.json
    summary2 = onboard_book(
        book_id="minilike",
        pdf_path=real_minilike_pdf,
        output_dir=out,
        n_sample_pages=2,
        mineru_runner=mock_mineru_runner,
        skip_thumbnails=True,
    )
    assert summary2["page_count"] == 20


def test_onboard_book_missing_pdf_raises(tmp_path: Path):
    from engine.yi_publishing.onboarding import onboard_book

    with pytest.raises(FileNotFoundError):
        onboard_book(
            book_id="ghost",
            pdf_path=tmp_path / "nope.pdf",
            output_dir=tmp_path / "out",
        )


def test_onboard_book_picks_no_formula_when_spike_shows_false_positives(
    real_minilike_pdf: Path, tmp_path: Path
):
    """If MinerU spike with formula=True returns 50% equation_ratio,
    onboarding should pick no-formula config."""
    from engine.yi_publishing.onboarding import onboard_book

    def runner_with_false_positives(*, pdf_path, output_root, start, end,
                                     backend, language, formula_enable, **kw):
        book_id = pdf_path.stem
        out = output_root / book_id / "auto"
        out.mkdir(parents=True, exist_ok=True)
        ratio = 0.5 if formula_enable else 0.0
        pages = []
        for _ in range(start, end + 1):
            n_items = 10
            n_eq = int(n_items * ratio)
            content = []
            for i in range(n_items):
                if i < n_eq:
                    content.append({"type": "equation_inline", "content": "x"})
                else:
                    content.append({"type": "text", "content": "hello"})
            pages.append([{
                "type": "paragraph",
                "content": {"paragraph_content": content},
                "bbox": [0, 0, 100, 100],
            }])
        (out / f"{book_id}_content_list_v2.json").write_text(
            json.dumps(pages, ensure_ascii=False), encoding="utf-8"
        )

    out = tmp_path / "onboarding"
    summary = onboard_book(
        book_id="minilike",
        pdf_path=real_minilike_pdf,
        output_dir=out,
        n_sample_pages=2,
        mineru_runner=runner_with_false_positives,
    )
    # Intelligence: pick no-formula because formula version showed equations
    assert summary["ocr_config"]["formula_enable"] is False
