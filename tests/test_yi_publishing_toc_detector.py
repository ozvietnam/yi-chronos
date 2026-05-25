"""Tests for engine.yi_publishing.toc_detector.

TOC detection has 3 strategies (priority order):
1. PDF bookmarks (fitz.get_toc())
2. Visual scan for "目录"/"Mục lục" pages → OCR title list
3. Keyword scan first 30 pages for chapter markers (第X章, 卷N, PHẦN N...)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def pdf_with_bookmarks(tmp_path: Path) -> Path:
    """PDF with embedded bookmark TOC (Strategy 1 happy path)."""
    import fitz

    doc = fitz.open()
    for _ in range(10):
        doc.new_page(width=595, height=842)

    toc = [
        [1, "Chương 1: Giới thiệu", 1],
        [1, "Chương 2: Nguyên lý", 3],
        [1, "Chương 3: Ứng dụng", 6],
        [1, "Chương 4: Kết luận", 9],
    ]
    doc.set_toc(toc)
    out = tmp_path / "with_bookmarks.pdf"
    doc.save(out)
    doc.close()
    return out


@pytest.fixture
def pdf_no_bookmarks_with_markers(tmp_path: Path) -> Path:
    """PDF without bookmarks but with chapter markers in first 10 pages.

    Use English/ASCII chapter markers (Chapter N) because PyMuPDF default
    font doesn't render CJK chars. Pattern matcher tests other regexes too.
    """
    import fitz

    doc = fitz.open()
    chapter_pages = [
        (1, "Chapter 1: Introduction"),
        (5, "Chapter 2: Principles"),
        (8, "Chapter 3: Applications"),
    ]
    for i in range(10):
        page = doc.new_page(width=595, height=842)
        for cp, title in chapter_pages:
            if (i + 1) == cp:
                page.insert_text((100, 100), title, fontsize=18)

    out = tmp_path / "with_markers.pdf"
    doc.save(out)
    doc.close()
    return out


@pytest.fixture
def pdf_no_toc_at_all(tmp_path: Path) -> Path:
    """Plain PDF with no bookmarks, no chapter markers."""
    import fitz

    doc = fitz.open()
    for _ in range(5):
        page = doc.new_page(width=595, height=842)
        page.insert_text((100, 400), "Just regular text", fontsize=12)
    out = tmp_path / "no_toc.pdf"
    doc.save(out)
    doc.close()
    return out


# ─── Strategy 1: bookmarks ────────────────────────────────────────────────────


def test_detect_via_bookmarks(pdf_with_bookmarks: Path):
    from engine.yi_publishing.toc_detector import detect_toc_via_bookmarks

    result = detect_toc_via_bookmarks(pdf_with_bookmarks)
    assert result is not None
    assert len(result["chapters"]) == 4
    assert result["chapters"][0]["title"] == "Chương 1: Giới thiệu"
    assert result["chapters"][0]["page_start"] == 1


def test_bookmarks_returns_none_for_pdf_without(pdf_no_toc_at_all: Path):
    from engine.yi_publishing.toc_detector import detect_toc_via_bookmarks

    assert detect_toc_via_bookmarks(pdf_no_toc_at_all) is None


def test_bookmarks_computes_page_end_for_each_chapter(pdf_with_bookmarks: Path):
    from engine.yi_publishing.toc_detector import detect_toc_via_bookmarks

    result = detect_toc_via_bookmarks(pdf_with_bookmarks)
    chapters = result["chapters"]
    # 10 total pages, chapters at 1,3,6,9 → ends: 2, 5, 8, 10
    assert chapters[0]["page_end"] == 2
    assert chapters[1]["page_end"] == 5
    assert chapters[2]["page_end"] == 8
    assert chapters[3]["page_end"] == 10


# ─── Strategy 3: keyword scan ────────────────────────────────────────────────


def test_detect_via_keyword_scan(pdf_no_bookmarks_with_markers: Path):
    from engine.yi_publishing.toc_detector import detect_toc_via_keywords

    result = detect_toc_via_keywords(pdf_no_bookmarks_with_markers, scan_first_n=10)
    assert result is not None
    chapters = result["chapters"]
    assert len(chapters) >= 2
    titles = [c["title"] for c in chapters]
    assert any("Chapter" in t for t in titles)


def test_chapter_patterns_match_chinese_keywords():
    """Regex patterns should match Chinese chapter markers (no PDF render needed)."""
    from engine.yi_publishing.toc_detector import _CHAPTER_PATTERNS

    samples = ["第一章 太极生两仪", "第3章 八卦", "卷一", "卷5", "第三回 论道"]
    for s in samples:
        matched = any(p.search(s) for p, _ in _CHAPTER_PATTERNS)
        assert matched, f"Failed to match: {s}"


def test_chapter_patterns_match_vietnamese():
    from engine.yi_publishing.toc_detector import _CHAPTER_PATTERNS

    samples = ["Chương 1: Mở đầu", "Phần 2", "Quyển 3 — Tử Vi"]
    for s in samples:
        matched = any(p.search(s) for p, _ in _CHAPTER_PATTERNS)
        assert matched, f"Failed to match: {s}"


def test_keyword_scan_returns_none_when_no_markers(pdf_no_toc_at_all: Path):
    from engine.yi_publishing.toc_detector import detect_toc_via_keywords

    result = detect_toc_via_keywords(pdf_no_toc_at_all, scan_first_n=5)
    assert result is None


# ─── Top-level detect_toc (combines strategies) ──────────────────────────────


def test_detect_toc_prefers_bookmarks(pdf_with_bookmarks: Path):
    from engine.yi_publishing.toc_detector import detect_toc

    result = detect_toc(pdf_with_bookmarks)
    assert result["strategy"] == "bookmarks"
    assert len(result["chapters"]) == 4


def test_detect_toc_falls_back_to_keywords(pdf_no_bookmarks_with_markers: Path):
    from engine.yi_publishing.toc_detector import detect_toc

    result = detect_toc(pdf_no_bookmarks_with_markers)
    assert result["strategy"] == "keywords"
    assert len(result["chapters"]) >= 2


def test_detect_toc_returns_single_chapter_when_no_toc(pdf_no_toc_at_all: Path):
    """When no TOC detectable, return a single "Toàn bộ sách" chapter."""
    from engine.yi_publishing.toc_detector import detect_toc

    result = detect_toc(pdf_no_toc_at_all)
    assert result["strategy"] == "fallback"
    assert len(result["chapters"]) == 1
    assert result["chapters"][0]["page_start"] == 1
    assert result["chapters"][0]["page_end"] == 5


def test_detect_toc_writes_markdown(pdf_with_bookmarks: Path, tmp_path: Path):
    from engine.yi_publishing.toc_detector import detect_toc, save_toc

    result = detect_toc(pdf_with_bookmarks)
    toc_md = tmp_path / "_TOC.md"
    save_toc(result, toc_md)
    assert toc_md.exists()
    content = toc_md.read_text(encoding="utf-8")
    assert "Chương 1" in content
    assert "Strategy" in content
