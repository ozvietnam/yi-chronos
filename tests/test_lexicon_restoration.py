"""Tests for YI-Lexicon restoration pipeline (Phase A).

Covers:
- BookManifest serialization roundtrip
- make_book_slug normalizes Vietnamese
- upsert_wikilink dedupes occurrences
- HTML wiki exporter wraps [[Concept]] in <a class="wikilink">
- Markdown exporter assembles frontmatter + page concat
- store v4 fields persist via update_corpus
- Pipeline status transitions (none → pending → done) via update_corpus

Does NOT call actual OCR/LLM (those are integration tests, run manually).
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    from engine.yi_lexicon import store as st
    db = tmp_path / "lex.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    st.bootstrap_db()
    return st


def test_book_manifest_roundtrip(tmp_path):
    from engine.yi_lexicon.restoration.manifest import (
        BookManifest, BookSection, BookPage, BookFigure,
        WikiLinkIndex, save_manifest, load_manifest,
    )
    m = BookManifest(
        book_slug="kinh-dich-test",
        book_name="Kinh Dịch Test",
        author="Anh",
        tier="S",
        pages_total=10,
        pages_restored=3,
        schools=["common"],
        sections=[BookSection(section_id="sec-1", title="Chương 1", level=1, start_page=1, end_page=3)],
        pages=[BookPage(page=1, section_id="sec-1", md_path="pages/page-0001.md",
                        word_count=120, wikilinks=["Càn"])],
        figures=[BookFigure(figure_id="fig-1-1", page=1, image_path="figures/fig-1-1.png")],
        wikilink_index=[WikiLinkIndex(concept_vi="Càn", occurrences=[{"page": 1, "section_id": "sec-1"}])],
    )
    path = tmp_path / "manifest.json"
    save_manifest(m, path)
    loaded = load_manifest(path)
    assert loaded.book_name == "Kinh Dịch Test"
    assert loaded.tier == "S"
    assert len(loaded.sections) == 1
    assert loaded.sections[0].title == "Chương 1"
    assert loaded.pages[0].wikilinks == ["Càn"]
    assert loaded.wikilink_index[0].concept_vi == "Càn"


def test_make_book_slug_vietnamese():
    from engine.yi_lexicon.restoration.manifest import make_book_slug
    assert make_book_slug("Kinh Dịch Trọn Bộ") == "kinh-dich-tron-bo"
    assert make_book_slug("Học Thuyết Âm Dương") == "hoc-thuyet-am-duong"
    assert make_book_slug("   ") == "untitled"
    assert make_book_slug("Bốc Phệ Chính Tông") == "boc-phe-chinh-tong"


def test_upsert_wikilink_dedupes():
    from engine.yi_lexicon.restoration.manifest import BookManifest, upsert_wikilink
    m = BookManifest(book_slug="test", book_name="Test")
    upsert_wikilink(m, "Càn", 1, "sec-1")
    upsert_wikilink(m, "Càn", 1, "sec-1")  # dup
    upsert_wikilink(m, "Càn", 2, "sec-1")  # new occurrence
    upsert_wikilink(m, "Khôn", 1, "sec-1")  # new concept
    assert len(m.wikilink_index) == 2
    can = next(w for w in m.wikilink_index if w.concept_vi == "Càn")
    assert len(can.occurrences) == 2
    pages = sorted(o["page"] for o in can.occurrences)
    assert pages == [1, 2]


def test_html_wiki_renders_wikilinks():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "## Tiết 1\n\n[[Càn]] và [[Khôn]] là 2 quẻ chính.\n\n- [[Mộc]]\n- [[Hoả]]"
    html = render_page_html(md)
    assert "<h2>Tiết 1</h2>" in html
    assert 'class="wikilink"' in html
    assert 'data-concept="Càn"' in html
    assert 'data-concept="Khôn"' in html
    assert "<ul>" in html and "</ul>" in html


def test_html_wiki_escapes_unsafe():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "Bad <script>alert(1)</script> here"
    html = render_page_html(md)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_html_wiki_blockquote():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    html = render_page_html("> Hệ Từ Truyện nói [[Thái Cực]] sinh Lưỡng Nghi")
    assert "<blockquote>" in html
    assert 'data-concept="Thái Cực"' in html


def test_corpus_restored_fields_default(isolated):
    st = isolated
    c = st.add_corpus(name="Test Resto")
    assert c.restored_status == "none"
    assert c.restored_pages == 0
    assert c.copyright_status == "internal_only"
    assert c.allow_download == 0


def test_corpus_restored_status_transition(isolated):
    st = isolated
    c = st.add_corpus(name="Test Transition", pages_total=100)
    # none → pending
    c1 = st.update_corpus(c.corpus_id, restored_status="pending",
                           restored_path="/tmp/test")
    assert c1.restored_status == "pending"
    # pending → partial (some pages done)
    c2 = st.update_corpus(c.corpus_id, restored_status="partial", restored_pages=10)
    assert c2.restored_status == "partial"
    assert c2.restored_pages == 10
    # → done
    c3 = st.update_corpus(c.corpus_id, restored_status="done", restored_pages=100,
                           bump_restored_at=True)
    assert c3.restored_status == "done"
    assert c3.restored_at is not None


def test_sync_restoration_metadata_from_manifest_updates_stale_corpus(isolated, tmp_path):
    st = isolated
    from engine.yi_lexicon.restoration.manifest import BookManifest, BookPage, save_manifest

    root = tmp_path / "restored-book"
    root.mkdir()
    manifest_path = root / "manifest.json"
    manifest = BookManifest(
        book_slug="restored-book",
        book_name="Restored Book",
        pages_total=3,
        pages_restored=3,
        pages=[
            BookPage(page=1, md_path="pages/page-0001.md"),
            BookPage(page=2, md_path="pages/page-0002.md"),
            BookPage(page=3, md_path="pages/page-0003.md"),
        ],
    )
    save_manifest(manifest, manifest_path)
    c = st.add_corpus(name="Restored Book", pages_total=3)
    c = st.update_corpus(
        c.corpus_id,
        restored_status="partial",
        restored_pages=1,
        restored_path=str(root),
        restored_manifest=str(manifest_path),
    )

    synced = st.sync_restoration_metadata_from_manifest(c)

    assert synced.restored_pages == 3
    assert synced.restored_status == "done"


def test_corpus_allow_download_default_off(isolated):
    """Per anh's policy: download disabled by default for ALL books."""
    st = isolated
    for tier in ("S", "A", "B", "C"):
        c = st.add_corpus(name=f"Book {tier}", tier=tier)
        assert c.allow_download == 0, f"tier {tier} must default to no-download"


def test_corpus_can_enable_download_manually(isolated):
    st = isolated
    c = st.add_corpus(name="Open Book")
    assert c.allow_download == 0
    c2 = st.update_corpus(c.corpus_id, allow_download=1,
                           copyright_status="public_domain")
    assert c2.allow_download == 1
    assert c2.copyright_status == "public_domain"


def test_markdown_exporter_frontmatter(tmp_path):
    """Markdown exporter writes proper frontmatter + concat pages."""
    from engine.yi_lexicon.restoration.manifest import (
        BookManifest, BookPage, save_manifest
    )
    from engine.yi_lexicon.restoration.exporters.markdown import export_full_markdown

    root = tmp_path / "test-book"
    pages_dir = root / "pages"
    pages_dir.mkdir(parents=True)
    (pages_dir / "page-0001.md").write_text("## Tiết 1\n\nNội dung trang 1.", encoding="utf-8")
    (pages_dir / "page-0002.md").write_text("## Tiết 2\n\nNội dung trang 2.", encoding="utf-8")

    m = BookManifest(
        book_slug="test-book",
        book_name="Sách Thử",
        author="Tác giả X",
        tier="A",
        corpus_id=42,
        pages_total=2,
        pages_restored=2,
        copyright_status="public_domain",
        pages=[
            BookPage(page=1, md_path="pages/page-0001.md"),
            BookPage(page=2, md_path="pages/page-0002.md"),
        ],
    )
    out = export_full_markdown(m, root)
    text = out.read_text(encoding="utf-8")
    assert "title: \"Sách Thử\"" in text
    assert "tier: \"A\"" in text
    assert "corpus_id: 42" in text
    assert "Nội dung trang 1" in text
    assert "Nội dung trang 2" in text
    assert "<a id=\"page-1\"></a>" in text
    assert "Bản phục chế nội bộ" in text  # copyright disclaimer present


def test_ocr_backend_factory():
    from engine.yi_lexicon.restoration.ocr_backends import get_backend, TesseractBackend
    b = get_backend("tesseract")
    assert isinstance(b, TesseractBackend)
    assert b.name == "tesseract"
    with pytest.raises(ValueError):
        get_backend("olmocr")  # not yet implemented


def test_glossary_terms_fetch(isolated):
    """fetch_glossary_terms_for_book returns lexicon concepts + Hermes terms."""
    st = isolated
    st.add_concept(canonical_vi="Càn", concept_type="symbol")
    st.add_concept(canonical_vi="Khôn", concept_type="symbol")
    st.add_concept(canonical_vi="Ngũ Hành", concept_type="concept")

    from engine.yi_lexicon.restoration.cleanup import fetch_glossary_terms_for_book
    terms = fetch_glossary_terms_for_book()
    assert "Càn" in terms
    assert "Khôn" in terms
    assert "Ngũ Hành" in terms


def test_html_wiki_image_rendering():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "![Hà Đồ](placeholder-fig-20-1.png)"
    html = render_page_html(md)
    assert "<figure>" in html
    assert 'src="placeholder-fig-20-1.png"' in html
    assert 'alt="Hà Đồ"' in html


def test_sections_for_reader_are_sorted_by_page():
    from engine.yi_lexicon.restoration.manifest import BookSection, sections_for_reader

    sections = [
        BookSection(section_id="sec-late", title="Late", level=2, start_page=181, end_page=200),
        BookSection(section_id="sec-early", title="Early", level=2, start_page=34, end_page=40),
        BookSection(section_id="sec-mid", title="Mid", level=3, start_page=103, end_page=104),
    ]

    out = sections_for_reader(sections)

    assert [s.section_id for s in out] == ["sec-early", "sec-mid", "sec-late"]
