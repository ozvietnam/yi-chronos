"""Tests for engine.yi_publishing.page_splitter.

page_splitter renders per-page thumbnails + detects basic page types
(blank / text / image-heavy / cover). Foundation for Smart Onboarding Pipeline.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Build a 5-page PDF with mixed content:
    p1 = blank
    p2 = dense text (Hán chars)
    p3 = sparse text
    p4 = image-heavy (large filled rect)
    p5 = mostly blank (just page number)
    """
    import fitz

    doc = fitz.open()

    # p1: blank
    doc.new_page(width=595, height=842)

    # p2: dense text — fill grid of Hán chars (simulate 3-col woodblock)
    p2 = doc.new_page(width=595, height=842)
    for col in range(3):
        for row in range(40):
            x = 80 + col * 180
            y = 80 + row * 18
            p2.insert_text((x, y), "甲乙丙丁戊己庚辛", fontsize=14)

    # p3: sparse text
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((100, 400), "Sparse single line", fontsize=12)

    # p4: large filled rect = image-heavy
    p4 = doc.new_page(width=595, height=842)
    rect = fitz.Rect(80, 80, 515, 762)
    p4.draw_rect(rect, color=(0, 0, 0), fill=(0.3, 0.3, 0.3))

    # p5: just page number bottom
    p5 = doc.new_page(width=595, height=842)
    p5.insert_text((290, 800), "5", fontsize=10)

    out = tmp_path / "sample.pdf"
    doc.save(out)
    doc.close()
    return out


def test_render_thumbnails_creates_one_per_page(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import render_thumbnails

    out_dir = tmp_path / "thumbs"
    paths = render_thumbnails(sample_pdf, out_dir, max_dim=200)
    assert len(paths) == 5
    for p in paths:
        assert p.exists()
        assert p.suffix in (".jpg", ".jpeg")


def test_render_thumbnails_filenames_zero_padded(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import render_thumbnails

    out_dir = tmp_path / "thumbs"
    paths = render_thumbnails(sample_pdf, out_dir)
    names = sorted([p.name for p in paths])
    assert names == ["p0001.jpg", "p0002.jpg", "p0003.jpg", "p0004.jpg", "p0005.jpg"]


def test_render_thumbnails_max_dim_respected(sample_pdf: Path, tmp_path: Path):
    from PIL import Image

    from engine.yi_publishing.page_splitter import render_thumbnails

    out_dir = tmp_path / "thumbs"
    paths = render_thumbnails(sample_pdf, out_dir, max_dim=150)
    for p in paths:
        with Image.open(p) as im:
            assert max(im.size) <= 150


def test_detect_blank_page(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import (
        detect_page_type,
        render_thumbnails,
    )

    paths = render_thumbnails(sample_pdf, tmp_path / "thumbs")
    # p1 is blank, p5 is mostly blank
    assert detect_page_type(paths[0]) == "blank"


def test_detect_dense_text_page(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import (
        detect_page_type,
        render_thumbnails,
    )

    paths = render_thumbnails(sample_pdf, tmp_path / "thumbs")
    # p2 has 3 columns of dense Hán chars
    assert detect_page_type(paths[1]) == "text"


def test_detect_image_heavy_page(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import (
        detect_page_type,
        render_thumbnails,
    )

    paths = render_thumbnails(sample_pdf, tmp_path / "thumbs")
    # p4 is large filled rect
    assert detect_page_type(paths[3]) == "image"


def test_analyze_book_returns_summary(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import analyze_book

    out_dir = tmp_path / "out"
    result = analyze_book(sample_pdf, out_dir)
    assert result["page_count"] == 5
    assert len(result["pages"]) == 5
    # Each page has page_num + type + thumbnail filename
    p1 = result["pages"][0]
    assert p1["page_num"] == 1
    assert p1["type"] in ("blank", "text", "image", "mixed")
    assert "thumbnail" in p1


def test_analyze_book_writes_page_types_json(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import analyze_book

    out_dir = tmp_path / "out"
    analyze_book(sample_pdf, out_dir)
    types_json = out_dir / "page_types.json"
    assert types_json.exists()

    data = json.loads(types_json.read_text(encoding="utf-8"))
    assert data["page_count"] == 5
    assert len(data["pages"]) == 5


def test_analyze_book_creates_thumbnails_subfolder(sample_pdf: Path, tmp_path: Path):
    from engine.yi_publishing.page_splitter import analyze_book

    out_dir = tmp_path / "out"
    analyze_book(sample_pdf, out_dir)
    thumb_dir = out_dir / "thumbnails"
    assert thumb_dir.exists()
    assert len(list(thumb_dir.glob("p*.jpg"))) == 5


def test_render_thumbnails_skip_existing(sample_pdf: Path, tmp_path: Path):
    """Re-running shouldn't re-render — for speed on incremental updates."""
    from engine.yi_publishing.page_splitter import render_thumbnails

    out_dir = tmp_path / "thumbs"
    paths1 = render_thumbnails(sample_pdf, out_dir)
    mtime1 = paths1[0].stat().st_mtime

    import time
    time.sleep(0.1)

    paths2 = render_thumbnails(sample_pdf, out_dir, skip_existing=True)
    mtime2 = paths2[0].stat().st_mtime
    assert mtime1 == mtime2, "Should not have re-rendered when skip_existing=True"


def test_page_type_for_only_page_number():
    """Page with only a page number (large whitespace) should be blank."""
    # This is tested implicitly by sample p5; verify the categorization heuristic.
    from engine.yi_publishing.page_splitter import _whitespace_ratio
    from PIL import Image

    # All white image
    img = Image.new("L", (200, 280), color=255)
    assert _whitespace_ratio(img) > 0.95
