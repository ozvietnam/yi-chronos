"""Tests cho MarkItDown text-layer backend."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


def test_has_text_layer_returns_false_for_missing_file(tmp_path):
    from engine.yi_lexicon.restoration.text_backends import has_text_layer
    assert has_text_layer(tmp_path / "nonexistent.pdf") is False


def test_has_text_layer_returns_false_for_empty(tmp_path):
    """No subprocess output → no text layer."""
    from engine.yi_lexicon.restoration.text_backends import has_text_layer
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="")
        assert has_text_layer(fake_pdf) is False


def test_has_text_layer_returns_true_when_text_present(tmp_path):
    from engine.yi_lexicon.restoration.text_backends import has_text_layer
    fake_pdf = tmp_path / "doc.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="x" * 500)
        assert has_text_layer(fake_pdf) is True


def test_clean_pdf_artifacts_strips_watermarks():
    from engine.yi_lexicon.restoration.text_backends import _clean_pdf_artifacts
    raw = "Text bình thường.\nhttps://thuviensach.vn\nMore text."
    cleaned = _clean_pdf_artifacts(raw)
    assert "thuviensach.vn" not in cleaned
    assert "Text bình thường" in cleaned
    assert "More text" in cleaned


def test_clean_pdf_artifacts_strips_sachvui():
    from engine.yi_lexicon.restoration.text_backends import _clean_pdf_artifacts
    raw = "Ebook miễn phí tại : www.Sachvui.Com\nContent here"
    cleaned = _clean_pdf_artifacts(raw)
    assert "Sachvui" not in cleaned
    assert "Content here" in cleaned


def test_clean_pdf_artifacts_collapses_blank_lines():
    from engine.yi_lexicon.restoration.text_backends import _clean_pdf_artifacts
    raw = "A\n\n\n\n\nB"
    cleaned = _clean_pdf_artifacts(raw)
    # Max 2 newlines in a row
    assert "\n\n\n" not in cleaned
    assert "A" in cleaned
    assert "B" in cleaned


def test_markitdown_backend_returns_error_when_no_pdf():
    from engine.yi_lexicon.restoration.text_backends import MarkItDownBackend
    b = MarkItDownBackend(pdf_path=None)
    r = b.ocr_page_by_number(1)
    assert r.text == ""
    assert r.backend == "markitdown"
    assert any("not found" in e.lower() or "extract failed" in e.lower() for e in r.errors)


def test_markitdown_backend_ocr_page_png_unsupported():
    """Pipeline calling ocr_page(png_path) on MarkItDown should error gracefully."""
    from engine.yi_lexicon.restoration.text_backends import MarkItDownBackend
    b = MarkItDownBackend(pdf_path="/tmp/fake.pdf")
    r = b.ocr_page(Path("/tmp/fake.png"))
    assert r.text == ""
    assert any("not supported" in e.lower() for e in r.errors)


def test_markitdown_backend_serves_cached_pages(tmp_path, monkeypatch):
    """Mock MarkItDown extraction → verify per-page serve."""
    from engine.yi_lexicon.restoration import text_backends
    fake_pdf = tmp_path / "book.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n")

    # Mock markitdown to return 3 pages
    class FakeResult:
        text_content = "Page A text\fPage B text\fPage C text"

    class FakeMD:
        def convert(self, p):
            return FakeResult()

    import sys
    fake_module = MagicMock()
    fake_module.MarkItDown = FakeMD
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    b = text_backends.MarkItDownBackend(pdf_path=fake_pdf)
    r1 = b.ocr_page_by_number(1)
    r2 = b.ocr_page_by_number(2)
    r3 = b.ocr_page_by_number(3)
    assert "Page A text" in r1.text
    assert "Page B text" in r2.text
    assert "Page C text" in r3.text
    assert r1.confidence == 0.95
    # Out of range
    r4 = b.ocr_page_by_number(5)
    assert r4.text == ""
    assert any("out of range" in e for e in r4.errors)


def test_markitdown_total_pages(tmp_path, monkeypatch):
    from engine.yi_lexicon.restoration import text_backends
    fake_pdf = tmp_path / "book.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4\n")

    class FakeResult:
        text_content = "Page1\fPage2\fPage3\f"  # trailing \f → 1 empty page stripped

    class FakeMD:
        def convert(self, p): return FakeResult()

    import sys
    fake_module = MagicMock()
    fake_module.MarkItDown = FakeMD
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    b = text_backends.MarkItDownBackend(pdf_path=fake_pdf)
    assert b.total_pages == 3


def test_markitdown_bind_pdf_resets_cache(tmp_path):
    from engine.yi_lexicon.restoration.text_backends import MarkItDownBackend
    fake1 = tmp_path / "a.pdf"
    fake2 = tmp_path / "b.pdf"
    fake1.write_bytes(b"%PDF-1.4\n")
    fake2.write_bytes(b"%PDF-1.4\n")
    b = MarkItDownBackend(pdf_path=fake1)
    b._extracted = True  # simulate cached
    b._pages_cache = ["foo"]
    b.bind_pdf(fake2)
    assert b._extracted is False
    assert b._pages_cache is None
    assert b._pdf_path == fake2


def test_restoration_config_has_force_ocr():
    from engine.yi_lexicon.restoration import RestorationConfig
    cfg = RestorationConfig()
    assert cfg.force_ocr is False
    assert cfg.ocr_backend in ("auto", "tesseract", "qwen-vl", "markitdown")


def test_restoration_config_default_is_auto():
    from engine.yi_lexicon.restoration import RestorationConfig
    cfg = RestorationConfig()
    assert cfg.ocr_backend == "auto"
