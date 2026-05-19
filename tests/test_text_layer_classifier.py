"""Tests cho text-layer classifier (Librarian v5)."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """Isolated DB."""
    from engine.yi_lexicon import store as st
    db = tmp_path / "lex.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    st.bootstrap_db()
    return st


def test_classify_text_layer_missing_file(tmp_path):
    from engine.yi_lexicon.librarian import classify_text_layer
    r = classify_text_layer(tmp_path / "nope.pdf")
    assert r["method"] == "unknown"
    assert "not found" in r["errors"][0].lower()


def test_classify_text_layer_pure_scan(tmp_path):
    """Mock pdftotext returning empty → pure_scan."""
    from engine.yi_lexicon.librarian import classify_text_layer
    pdf = tmp_path / "scan.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=100), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="")  # empty text
        r = classify_text_layer(pdf)
    assert r["method"] == "pure_scan"
    assert r["chars_per_page"] == 0.0
    assert r["pages_total"] == 100


def test_classify_text_layer_text_layer(tmp_path):
    """Mock pdftotext returning 500 chars/page → text_layer."""
    from engine.yi_lexicon.librarian import classify_text_layer
    pdf = tmp_path / "good.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=200), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="X" * 500)  # 500 chars
        r = classify_text_layer(pdf)
    assert r["method"] == "text_layer"
    assert r["chars_per_page"] == 500.0
    # Fast restore time
    assert r["estimated_time_min"] < 15


def test_classify_text_layer_hybrid(tmp_path):
    """Mock pdftotext returning ~100 chars/page → hybrid."""
    from engine.yi_lexicon.librarian import classify_text_layer
    pdf = tmp_path / "mix.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=100), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="X" * 100)
        r = classify_text_layer(pdf)
    assert r["method"] == "hybrid"
    assert r["chars_per_page"] == 100.0


def test_classify_handles_subprocess_exceptions(tmp_path):
    from engine.yi_lexicon.librarian import classify_text_layer
    pdf = tmp_path / "bad.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=10), \
         patch("subprocess.run", side_effect=Exception("subprocess failed")):
        r = classify_text_layer(pdf)
    # All probes failed → falls back to pure_scan
    assert r["method"] == "pure_scan"
    assert len(r["errors"]) > 0


def test_classify_picks_spread_sample_pages(tmp_path):
    from engine.yi_lexicon.librarian import classify_text_layer
    pdf = tmp_path / "long.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    calls = []
    def fake_run(cmd, **kw):
        # Capture page args
        f_idx = cmd.index("-f") if "-f" in cmd else -1
        l_idx = cmd.index("-l") if "-l" in cmd else -1
        if f_idx > -1 and l_idx > -1:
            calls.append((int(cmd[f_idx+1]), int(cmd[l_idx+1])))
        return MagicMock(stdout="X" * 300)
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=1000), \
         patch("subprocess.run", side_effect=fake_run):
        r = classify_text_layer(pdf)
    # 10 spread pages, last should be near end
    assert r["pages_probed"] == 10
    pages = [c[0] for c in calls]
    assert min(pages) >= 1
    assert max(pages) > 500  # at least one page near second half


def test_corpus_has_text_layer_fields(isolated):
    st = isolated
    c = st.add_corpus(name="Test Book TX")
    assert c.restore_method == "unknown"
    assert c.text_layer_chars_per_page == 0.0
    assert c.text_layer_probed_at is None


def test_update_corpus_sets_text_layer_fields(isolated):
    st = isolated
    c = st.add_corpus(name="Update TX")
    c2 = st.update_corpus(
        c.corpus_id,
        restore_method="text_layer",
        text_layer_chars_per_page=523.4,
        bump_text_layer_probed_at=True,
    )
    assert c2.restore_method == "text_layer"
    assert c2.text_layer_chars_per_page == 523.4
    assert c2.text_layer_probed_at is not None


def test_scan_library_text_layers_only_unprobed(isolated, tmp_path):
    """only_unprobed=True skips books with text_layer_probed_at set."""
    st = isolated
    fake = tmp_path / "x.pdf"
    fake.write_bytes(b"%PDF-1.4\n")
    c1 = st.add_corpus(name="Book A", file_path=str(fake))
    c2 = st.add_corpus(name="Book B", file_path=str(fake))
    # Mark Book A as probed
    st.update_corpus(c1.corpus_id, bump_text_layer_probed_at=True,
                     restore_method="text_layer")

    from engine.yi_lexicon.librarian import scan_library_text_layers
    with patch("engine.yi_lexicon.librarian.classify_text_layer") as mock_classify:
        mock_classify.return_value = {
            "method": "pure_scan", "chars_per_page": 0.0,
            "pages_probed": 10, "pages_total": 100,
            "estimated_time_min": 50, "errors": []
        }
        r = scan_library_text_layers(only_unprobed=True)
    # Only Book B (unprobed) should be scanned
    assert r["scanned"] == 1
    names = [b["name"] for b in r["books"]]
    assert "Book B" in names
    assert "Book A" not in names


def test_librarian_proposal_has_text_layer_fields():
    from engine.yi_lexicon.librarian import LibrarianProposal
    p = LibrarianProposal(file_path="/tmp/x.pdf", pages_total=100)
    assert p.text_layer_method == "unknown"
    assert p.text_layer_chars_per_page == 0.0


def test_analyze_book_probes_text_layer(isolated, tmp_path):
    """analyze_book auto-probes text layer."""
    from engine.yi_lexicon.librarian import analyze_book
    pdf = tmp_path / "auto.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("engine.yi_lexicon.librarian._pdf_page_count", return_value=100), \
         patch("engine.yi_lexicon.librarian._make_cover", return_value=None), \
         patch("engine.yi_lexicon.librarian.classify_text_layer") as mock_classify, \
         patch("engine.yi_lexicon.librarian.get_book_meta_for_file", return_value=None), \
         patch("engine.yi_lexicon.librarian._ocr_intro_pages", return_value=""):
        mock_classify.return_value = {
            "method": "text_layer", "chars_per_page": 800.0,
            "pages_probed": 10, "pages_total": 100,
            "estimated_time_min": 4.2, "errors": []
        }
        prop = analyze_book(pdf, skip_llm=True)
    assert prop.text_layer_method == "text_layer"
    assert prop.text_layer_chars_per_page == 800.0
    assert prop.text_layer_estimated_min == 4.2
