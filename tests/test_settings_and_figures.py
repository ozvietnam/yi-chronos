"""Tests cho 2 việc anh yêu cầu:
1. Settings: provider notes (plan_type + free-form text) persist + API endpoints
2. Figure detection: OCR/cleanup nhận diện [[FIGURE:type|desc]] → BookFigure entry
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# ─── Việc 1: Provider notes ─────────────────────────────────────────────────


def test_provider_notes_set_and_get(tmp_path, monkeypatch):
    from engine.ai import registry as reg_mod
    # Redirect notes path to tmp
    monkeypatch.setattr(reg_mod, "_NOTES_PATH", tmp_path / "notes.json")
    r = reg_mod.ProviderRegistry()

    # Set notes
    out = r.set_notes("deepseek", plan_type="api_pay_per_token", notes="$10 deposit")
    assert out["plan_type"] == "api_pay_per_token"
    assert out["notes"] == "$10 deposit"

    # Reload — notes persist
    r2 = reg_mod.ProviderRegistry()
    n = r2.get_notes("deepseek")
    assert n["plan_type"] == "api_pay_per_token"
    assert n["notes"] == "$10 deposit"


def test_provider_notes_partial_update(tmp_path, monkeypatch):
    from engine.ai import registry as reg_mod
    monkeypatch.setattr(reg_mod, "_NOTES_PATH", tmp_path / "notes.json")
    r = reg_mod.ProviderRegistry()
    r.set_notes("ollama", plan_type="local", notes="Mac M4 36GB")
    # Update only notes
    r.set_notes("ollama", notes="updated note only")
    n = r.get_notes("ollama")
    assert n["plan_type"] == "local"      # unchanged
    assert n["notes"] == "updated note only"


def test_provider_notes_invalid_provider_raises(tmp_path, monkeypatch):
    from engine.ai import registry as reg_mod
    monkeypatch.setattr(reg_mod, "_NOTES_PATH", tmp_path / "notes.json")
    r = reg_mod.ProviderRegistry()
    with pytest.raises(KeyError):
        r.set_notes("nonexistent", plan_type="local")


def test_list_providers_includes_notes_and_plan(tmp_path, monkeypatch):
    from engine.ai import registry as reg_mod
    monkeypatch.setattr(reg_mod, "_NOTES_PATH", tmp_path / "notes.json")
    r = reg_mod.ProviderRegistry()
    r.set_notes("deepseek", plan_type="api_pay_per_token", notes="test")
    listing = r.list_providers()
    ds = next(p for p in listing if p["name"] == "deepseek")
    assert ds["plan_type"] == "api_pay_per_token"
    assert ds["notes"] == "test"
    assert "is_unhealthy" in ds


def test_notes_default_empty(tmp_path, monkeypatch):
    from engine.ai import registry as reg_mod
    monkeypatch.setattr(reg_mod, "_NOTES_PATH", tmp_path / "notes.json")
    r = reg_mod.ProviderRegistry()
    n = r.get_notes("ollama")
    assert n["plan_type"] is None
    assert n["notes"] is None


# ─── Việc 2: Figure detection ───────────────────────────────────────────────


def test_parse_figures_extracts_all():
    from engine.yi_lexicon.restoration.cleanup import parse_figures
    text = (
        "Đoạn văn trước. [[FIGURE:ha_do|Hà Đồ 10 chấm chia 5 cặp]]\n"
        "Đoạn giữa. [[FIGURE:bat_quai_tien_thien|Vòng 8 quẻ Phục Hy]]\n"
        "Đoạn cuối."
    )
    figs = parse_figures(text)
    assert len(figs) == 2
    assert figs[0].figure_type == "ha_do"
    assert "10 chấm" in figs[0].description
    assert figs[1].figure_type == "bat_quai_tien_thien"


def test_parse_figures_empty_text():
    from engine.yi_lexicon.restoration.cleanup import parse_figures
    assert parse_figures("") == []
    assert parse_figures("không có hình") == []


def test_parse_figures_handles_special_chars():
    from engine.yi_lexicon.restoration.cleanup import parse_figures
    text = "[[FIGURE:so_do_ngu_hanh|Kim → Mộc → Hoả → Thổ tương sinh]]"
    figs = parse_figures(text)
    assert len(figs) == 1
    assert "Kim → Mộc" in figs[0].description


def test_html_renderer_creates_figure_placeholder():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "Đoạn trước.\n\n[[FIGURE:ha_do|Hà Đồ ở giữa trang]]\n\nĐoạn sau."
    html = render_page_html(md)
    assert "figure-placeholder" in html
    assert 'data-figure-type="ha_do"' in html
    assert "Hà Đồ ở giữa trang" in html
    # WikiLink not confused with figure
    assert 'class="wikilink"' not in html  # no plain wikilinks in this snippet


def test_html_renderer_handles_wikilink_and_figure_together():
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "[[Càn]] mạnh. [[FIGURE:bat_quai_tien_thien|Vòng 8 quẻ]] [[Khôn]] thuận."
    html = render_page_html(md)
    assert 'data-concept="Càn"' in html
    assert 'data-concept="Khôn"' in html
    assert "figure-placeholder" in html
    assert 'data-figure-type="bat_quai_tien_thien"' in html


def test_html_figure_escapes_xss():
    """Figure description containing HTML must be escaped."""
    from engine.yi_lexicon.restoration.exporters.html_wiki import render_page_html
    md = "[[FIGURE:khac|Bad <script>alert(1)</script> desc]]"
    html = render_page_html(md)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_cleanup_result_has_detected_figures_field():
    """CleanupResult dataclass exposes detected_figures."""
    from engine.yi_lexicon.restoration.cleanup import CleanupResult, DetectedFigure
    r = CleanupResult()
    assert r.detected_figures == []
    r.detected_figures.append(DetectedFigure(
        figure_type="ha_do", description="test", placeholder="[[FIGURE:ha_do|test]]"
    ))
    assert len(r.detected_figures) == 1


def test_cleanup_reinserts_figures_when_llm_strips_them(monkeypatch):
    """If LLM removes [[FIGURE:...]] from output, cleanup re-appends from raw OCR."""
    from engine.yi_lexicon.restoration.cleanup import cleanup_page

    # Mock LLM provider that strips figure placeholders
    fake_provider = MagicMock()
    fake_resp = MagicMock()
    fake_resp.content = json.dumps({
        "cleaned_markdown": "Text only — LLM stripped figure marker.",
        "section_hint": None,
        "wikilinks": [],
        "confidence": 0.9,
        "warnings": []
    })
    fake_provider.chat.return_value = fake_resp

    raw = "Original page text.\n\n[[FIGURE:ha_do|Hà Đồ 10 chấm]]\n\nMore text."
    result = cleanup_page(raw, glossary_terms=[], llm_provider=fake_provider)
    assert len(result.detected_figures) == 1
    assert result.detected_figures[0].figure_type == "ha_do"
    # Cleanup auto re-inserted the marker
    assert "[[FIGURE:ha_do" in result.cleaned_markdown
    assert any("strip" in w.lower() for w in result.warnings)


def test_bookfigure_new_fields():
    from engine.yi_lexicon.restoration.manifest import BookFigure
    f = BookFigure(
        figure_id="fig-0010-detected-1", page=10,
        image_path=None,
        description="Hà Đồ ở giữa trang 10 chấm",
        figure_type="ha_do",
        source="detected_in_scan",
        redraw_status="needs_redraw",
        placeholder="[[FIGURE:ha_do|Hà Đồ ở giữa trang 10 chấm]]",
    )
    assert f.image_path is None
    assert f.source == "detected_in_scan"
    assert f.redraw_status == "needs_redraw"
    assert f.placeholder is not None


def test_manifest_serializes_new_figure_fields(tmp_path):
    from engine.yi_lexicon.restoration.manifest import (
        BookManifest, BookFigure, save_manifest, load_manifest
    )
    m = BookManifest(book_slug="test", book_name="Test",
                     figures=[
                         BookFigure(
                             figure_id="fig-0001-detected-1", page=1,
                             image_path=None, description="Hà Đồ",
                             figure_type="ha_do", source="detected_in_scan",
                             redraw_status="needs_redraw",
                             placeholder="[[FIGURE:ha_do|Hà Đồ]]",
                         )
                     ])
    path = tmp_path / "manifest.json"
    save_manifest(m, path)
    loaded = load_manifest(path)
    f = loaded.figures[0]
    assert f.source == "detected_in_scan"
    assert f.redraw_status == "needs_redraw"
    assert f.description == "Hà Đồ"
    assert f.placeholder == "[[FIGURE:ha_do|Hà Đồ]]"
