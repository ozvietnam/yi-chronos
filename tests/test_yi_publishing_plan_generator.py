"""Tests for engine.yi_publishing.plan_generator.

Generates 4 plan artifacts from profile + TOC:
  - _OCR-CONFIG.json
  - _READING-PLAN.md
  - _TRANSLATION-PLAN.md
  - _LLM-ROUTING.md
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_profile() -> dict:
    return {
        "columns": 3,
        "density": "normal",
        "script": "chinese",
        "ocr_config": {
            "backend": "pipeline",
            "language": "ch",
            "formula_enable": False,
            "method": "auto",
            "rationale": "3-col Hán cổ, spike test detected 26% equation false-positive with default; disable formula parsing.",
        },
    }


@pytest.fixture
def sample_toc_with_chapters() -> dict:
    return {
        "strategy": "bookmarks",
        "total_pages": 588,
        "chapters": [
            {"title": "Chương 1: Mở đầu", "page_start": 1, "page_end": 50, "level": 1},
            {"title": "Chương 2: Nguyên lý", "page_start": 51, "page_end": 200, "level": 1},
            {"title": "Chương 3: Ứng dụng", "page_start": 201, "page_end": 450, "level": 1},
            {"title": "Chương 4: Phụ lục", "page_start": 451, "page_end": 588, "level": 1},
        ],
    }


@pytest.fixture
def sample_toc_fallback() -> dict:
    return {
        "strategy": "fallback",
        "total_pages": 100,
        "chapters": [
            {"title": "Toàn bộ sách (no TOC)", "page_start": 1, "page_end": 100, "level": 1},
        ],
    }


# ─── OCR config ──────────────────────────────────────────────────────────────


def test_generate_ocr_config_from_profile(sample_profile, sample_toc_with_chapters, tmp_path):
    from engine.yi_publishing.plan_generator import generate_ocr_config

    cfg = generate_ocr_config(sample_profile, sample_toc_with_chapters, tmp_path)
    assert cfg["backend"] == "pipeline"
    assert cfg["language"] == "ch"
    assert cfg["formula_enable"] is False
    # workers recommendation = sensible default (≤4)
    assert 1 <= cfg["workers"] <= 4
    # File written
    assert (tmp_path / "_OCR-CONFIG.json").exists()


def test_ocr_config_workers_scale_with_pages(sample_profile, sample_toc_fallback, tmp_path):
    """For very small books (< 50 pages), workers should default to 1 (no parallel benefit)."""
    from engine.yi_publishing.plan_generator import generate_ocr_config

    # 50-page book
    small_toc = {**sample_toc_fallback, "total_pages": 30}
    small_toc["chapters"][0]["page_end"] = 30
    cfg = generate_ocr_config(sample_profile, small_toc, tmp_path)
    assert cfg["workers"] == 1

    # 600+ pages → 3 or 4 workers
    big_toc = {**sample_toc_fallback, "total_pages": 600}
    big_toc["chapters"][0]["page_end"] = 600
    cfg = generate_ocr_config(sample_profile, big_toc, tmp_path / "big")
    assert cfg["workers"] >= 3


# ─── Reading plan ────────────────────────────────────────────────────────────


def test_generate_reading_plan_per_chapter(sample_profile, sample_toc_with_chapters, tmp_path):
    from engine.yi_publishing.plan_generator import generate_reading_plan

    generate_reading_plan(sample_profile, sample_toc_with_chapters, tmp_path)
    md = (tmp_path / "_READING-PLAN.md").read_text(encoding="utf-8")
    # Each chapter listed
    for ch in sample_toc_with_chapters["chapters"]:
        assert ch["title"] in md
    # Has tier column
    assert "Tier" in md or "tier" in md


def test_reading_plan_default_tier_a():
    """All chapters default to A tier; anh edits manually."""
    from engine.yi_publishing.plan_generator import _default_chapter_tier

    assert _default_chapter_tier({"title": "Chương 1"}) == "A"


def test_reading_plan_handles_phụ_lục_as_c_tier():
    """Common: appendix/phụ lục is C tier."""
    from engine.yi_publishing.plan_generator import _default_chapter_tier

    assert _default_chapter_tier({"title": "Phụ lục A: Bảng tra"}) == "C"
    assert _default_chapter_tier({"title": "Appendix B"}) == "C"
    assert _default_chapter_tier({"title": "附录"}) == "C"


# ─── Translation plan ────────────────────────────────────────────────────────


def test_translation_plan_chunks_by_chapter_when_toc_available(
    sample_profile, sample_toc_with_chapters, tmp_path
):
    from engine.yi_publishing.plan_generator import generate_translation_plan

    plan = generate_translation_plan(sample_profile, sample_toc_with_chapters, tmp_path)
    # 4 chapters → 4 chunks (or more if a chapter is split for large size)
    assert len(plan["chunks"]) >= 4
    # First chunk covers chapter 1
    assert plan["chunks"][0]["page_start"] == 1
    assert plan["chunks"][0]["page_end"] <= 50


def test_translation_plan_splits_large_chapter():
    """Chapters >150 pages get split into smaller chunks."""
    from engine.yi_publishing.plan_generator import _split_chapter_into_chunks

    big_chapter = {"title": "Chương 1: Đại", "page_start": 1, "page_end": 300}
    chunks = _split_chapter_into_chunks(big_chapter, max_chunk_pages=100)
    assert len(chunks) >= 3
    # All pages covered
    assert chunks[0]["page_start"] == 1
    assert chunks[-1]["page_end"] == 300


def test_translation_plan_chunks_equal_when_no_toc(
    sample_profile, sample_toc_fallback, tmp_path
):
    """Without TOC, equal split into ~50-page chunks."""
    from engine.yi_publishing.plan_generator import generate_translation_plan

    plan = generate_translation_plan(sample_profile, sample_toc_fallback, tmp_path)
    # 100 pages / 50 per chunk = ~2 chunks
    assert len(plan["chunks"]) >= 1
    total = sum(c["page_end"] - c["page_start"] + 1 for c in plan["chunks"])
    assert total == 100


def test_translation_plan_routes_llm_by_script(sample_profile, sample_toc_with_chapters, tmp_path):
    from engine.yi_publishing.plan_generator import generate_translation_plan

    plan = generate_translation_plan(sample_profile, sample_toc_with_chapters, tmp_path)
    # Chinese classical → reasoner-class LLM (deepseek-reasoner or similar)
    assert "llm_route" in plan
    primary = plan["llm_route"]["primary"]
    assert primary in ("deepseek-reasoner", "deepseek-chat", "claude-sonnet")


# ─── LLM routing markdown ────────────────────────────────────────────────────


def test_generate_llm_routing_md(sample_profile, sample_toc_with_chapters, tmp_path):
    from engine.yi_publishing.plan_generator import generate_llm_routing

    generate_llm_routing(sample_profile, sample_toc_with_chapters, tmp_path)
    md = (tmp_path / "_LLM-ROUTING.md").read_text(encoding="utf-8")
    assert "deepseek" in md.lower() or "claude" in md.lower()


# ─── End-to-end generate_all_plans ───────────────────────────────────────────


def test_generate_all_plans_creates_4_artifacts(sample_profile, sample_toc_with_chapters, tmp_path):
    from engine.yi_publishing.plan_generator import generate_all_plans

    result = generate_all_plans(sample_profile, sample_toc_with_chapters, tmp_path)
    assert (tmp_path / "_OCR-CONFIG.json").exists()
    assert (tmp_path / "_READING-PLAN.md").exists()
    assert (tmp_path / "_TRANSLATION-PLAN.md").exists()
    assert (tmp_path / "_LLM-ROUTING.md").exists()
    # Returns a summary dict
    assert "ocr_config" in result
    assert "chunks_count" in result
    assert "estimated_ocr_hours" in result
