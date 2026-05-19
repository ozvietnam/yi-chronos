"""Tests cho metadata extraction layer (v2, 2026-05-12).

Anh đề xuất: hashtag + summary_short + persons + que_mentions để hỗ trợ search +
wiki-building, KHÔNG phải wikilink (Phase 3).
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest


def test_normalize_hashtag_adds_hash():
    from engine.yi_lexicon.restoration.cleanup import _normalize_hashtag
    assert _normalize_hashtag("ngũ-hành") == "#ngũ-hành"
    assert _normalize_hashtag("#ngũ-hành") == "#ngũ-hành"
    assert _normalize_hashtag("Ngũ Hành") == "#ngũ-hành"


def test_normalize_hashtag_strips_special_chars():
    from engine.yi_lexicon.restoration.cleanup import _normalize_hashtag
    assert _normalize_hashtag("#Càn @ Khôn") == "#càn--khôn"  # spaces → -, @ stripped
    assert "@" not in _normalize_hashtag("@special")


def test_cleanup_result_has_v2_fields():
    from engine.yi_lexicon.restoration.cleanup import CleanupResult
    r = CleanupResult()
    assert r.summary_short == ""
    assert r.hashtags == []
    assert r.persons == []
    assert r.que_mentions == []


def test_cleanup_extracts_metadata_from_llm_json():
    from engine.yi_lexicon.restoration.cleanup import cleanup_page
    fake_llm = MagicMock()
    fake_resp = MagicMock()
    fake_resp.content = json.dumps({
        "cleaned_markdown": "## Ngũ Hành\n\nKim Mộc Thuỷ Hoả Thổ.",
        "section_hint": {"level": 2, "title": "Ngũ Hành"},
        "wikilinks": ["Ngũ Hành", "Kim", "Mộc"],
        "summary_short": "Giới thiệu 5 hành cơ bản theo Chu Hy.",
        "hashtags": ["#ngũ-hành", "Kim", "#chu-hy"],
        "persons": ["Chu Hy", "Trình Di"],
        "que_mentions": ["Đại Quá"],
        "confidence": 0.9,
        "warnings": []
    })
    fake_llm.chat.return_value = fake_resp

    result = cleanup_page("raw OCR text", glossary_terms=[], llm_provider=fake_llm)
    assert result.summary_short == "Giới thiệu 5 hành cơ bản theo Chu Hy."
    assert "#ngũ-hành" in result.hashtags
    assert "#kim" in result.hashtags  # normalized (no #-prefix → added)
    assert "#chu-hy" in result.hashtags
    assert "Chu Hy" in result.persons
    assert "Trình Di" in result.persons
    assert "Đại Quá" in result.que_mentions


def test_cleanup_ignores_invalid_metadata_types():
    from engine.yi_lexicon.restoration.cleanup import cleanup_page
    fake_llm = MagicMock()
    fake_resp = MagicMock()
    fake_resp.content = json.dumps({
        "cleaned_markdown": "Text.",
        "hashtags": ["#ok", 123, None, "  "],  # mixed garbage
        "persons": "Chu Hy",                    # wrong type — should ignore
        "que_mentions": ["Đại Quá", ""],
        "confidence": 0.7
    })
    fake_llm.chat.return_value = fake_resp
    result = cleanup_page("raw", glossary_terms=[], llm_provider=fake_llm)
    assert result.hashtags == ["#ok"]
    assert result.persons == []  # string-typed → ignored (only list accepted)
    assert result.que_mentions == ["Đại Quá"]


def test_book_page_has_v2_metadata_fields():
    from engine.yi_lexicon.restoration.manifest import BookPage
    p = BookPage(page=1)
    assert p.summary_short == ""
    assert p.hashtags == []
    assert p.persons == []
    assert p.que_mentions == []


def test_book_manifest_has_reverse_indexes():
    from engine.yi_lexicon.restoration.manifest import BookManifest
    m = BookManifest(book_slug="test", book_name="Test")
    assert m.hashtag_index == []
    assert m.person_index == []


def test_upsert_hashtag_dedupes():
    from engine.yi_lexicon.restoration.manifest import BookManifest, upsert_hashtag
    m = BookManifest(book_slug="test", book_name="Test")
    upsert_hashtag(m, "#ngũ-hành", 5)
    upsert_hashtag(m, "#ngũ-hành", 5)   # dup
    upsert_hashtag(m, "#ngũ-hành", 10)  # new page
    upsert_hashtag(m, "#âm-dương", 5)   # new tag
    assert len(m.hashtag_index) == 2
    nh = next(h for h in m.hashtag_index if h.tag == "#ngũ-hành")
    assert nh.pages == [5, 10]
    assert nh.count == 2


def test_upsert_person_dedupes():
    from engine.yi_lexicon.restoration.manifest import BookManifest, upsert_person
    m = BookManifest(book_slug="t", book_name="T")
    upsert_person(m, "Chu Hy", 1)
    upsert_person(m, "Chu Hy", 1)
    upsert_person(m, "Chu Hy", 7)
    upsert_person(m, "Trình Di", 1)
    chu = next(p for p in m.person_index if p.name == "Chu Hy")
    assert chu.pages == [1, 7]
    assert chu.count == 2


def test_manifest_roundtrip_includes_v2_fields(tmp_path):
    from engine.yi_lexicon.restoration.manifest import (
        BookManifest, BookPage, HashtagIndex, PersonIndex,
        save_manifest, load_manifest,
    )
    m = BookManifest(
        book_slug="test", book_name="Test",
        pages=[BookPage(
            page=1, summary_short="TLDR test",
            hashtags=["#ngũ-hành"], persons=["Chu Hy"],
            que_mentions=["Càn"],
        )],
        hashtag_index=[HashtagIndex(tag="#ngũ-hành", pages=[1], count=1)],
        person_index=[PersonIndex(name="Chu Hy", pages=[1], count=1)],
    )
    path = tmp_path / "manifest.json"
    save_manifest(m, path)
    loaded = load_manifest(path)
    p = loaded.pages[0]
    assert p.summary_short == "TLDR test"
    assert "#ngũ-hành" in p.hashtags
    assert "Chu Hy" in p.persons
    assert "Càn" in p.que_mentions
    assert loaded.hashtag_index[0].tag == "#ngũ-hành"
    assert loaded.person_index[0].name == "Chu Hy"


def test_summary_short_truncated_at_300_chars():
    from engine.yi_lexicon.restoration.cleanup import cleanup_page
    fake_llm = MagicMock()
    fake_resp = MagicMock()
    long_summary = "x" * 500
    fake_resp.content = json.dumps({
        "cleaned_markdown": "Text.",
        "summary_short": long_summary,
        "confidence": 0.8
    })
    fake_llm.chat.return_value = fake_resp
    result = cleanup_page("raw", glossary_terms=[], llm_provider=fake_llm)
    assert len(result.summary_short) <= 300
