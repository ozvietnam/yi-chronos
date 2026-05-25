"""TOC detector — Stage 2.1 of Smart Book Onboarding.

3 strategies (priority order):
    1. PDF bookmarks (fitz.get_toc()) — fastest + most reliable
    2. Visual scan for TOC pages (vision OCR of "目录"/"Mục lục" page)
       NOT YET IMPLEMENTED — defer to v2
    3. Keyword scan first N pages for chapter markers
       (第X章 / 卷N / Phần N / Chương N / Chapter N)

If all 3 fail → fallback "single chapter covering whole book".

Output: dict with `strategy`, `chapters[]` where each chapter has
`title`, `page_start`, `page_end`. Saved as `_TOC.md` markdown.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Chapter marker patterns (priority order, most specific first)
_CHAPTER_PATTERNS = [
    # Chinese: 第一章, 第1章, 第一回, 第一节, 卷一, 卷1, 部一
    (re.compile(r"第[一二三四五六七八九十百零〇\d]+(章|回|节|篇)"), "zh-chapter"),
    (re.compile(r"卷[一二三四五六七八九十百\d]+"), "zh-volume"),
    (re.compile(r"部[一二三四五六七八九十\d]+"), "zh-part"),
    # Vietnamese
    (re.compile(r"Chương\s+\d+", re.IGNORECASE), "vi-chapter"),
    (re.compile(r"Phần\s+\d+", re.IGNORECASE), "vi-part"),
    (re.compile(r"Quyển\s+\d+", re.IGNORECASE), "vi-volume"),
    # English
    (re.compile(r"Chapter\s+\d+", re.IGNORECASE), "en-chapter"),
    (re.compile(r"Part\s+\d+", re.IGNORECASE), "en-part"),
]


# ─── Strategy 1: PDF bookmarks ────────────────────────────────────────────────


def detect_toc_via_bookmarks(pdf_path: Path) -> Optional[dict]:
    """Extract TOC from PDF bookmarks (fitz.get_toc()).

    Returns dict {strategy, chapters[]} or None if no bookmarks found.
    """
    import fitz

    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    try:
        toc = doc.get_toc()
        total_pages = doc.page_count
    finally:
        doc.close()

    if not toc:
        return None

    chapters = []
    for entry in toc:
        # fitz toc entry: [level, title, page] (page is 1-indexed)
        level, title, page = entry[0], entry[1].strip(), entry[2]
        # Only collect top-level (level=1) chapters for chunking
        if level != 1:
            continue
        chapters.append({
            "title": title,
            "page_start": page,
            "page_end": None,  # filled below
            "level": level,
        })

    if not chapters:
        return None

    # Compute page_end for each chapter (next chapter's start - 1, last → total_pages)
    for i in range(len(chapters)):
        if i + 1 < len(chapters):
            chapters[i]["page_end"] = chapters[i + 1]["page_start"] - 1
        else:
            chapters[i]["page_end"] = total_pages

    return {
        "strategy": "bookmarks",
        "total_pages": total_pages,
        "chapters": chapters,
    }


# ─── Strategy 3: Keyword scan ────────────────────────────────────────────────


def detect_toc_via_keywords(
    pdf_path: Path, *, scan_first_n: int = 30
) -> Optional[dict]:
    """Scan first N pages of PDF for chapter markers in text layer.

    Limitation: only works if PDF has text layer (not pure scan).
    For scan PDFs, this won't find anything — return None → fallback.
    """
    import fitz

    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    try:
        n_scan = min(scan_first_n, doc.page_count)
        total_pages = doc.page_count

        found_chapters: list[dict] = []
        seen_titles: set = set()

        for page_idx in range(n_scan):
            page = doc.load_page(page_idx)
            text = page.get_text("text") or ""
            for line in text.splitlines():
                line = line.strip()
                if not line or len(line) > 80:
                    continue
                for pattern, _kind in _CHAPTER_PATTERNS:
                    m = pattern.search(line)
                    if m:
                        # Use marker prefix + nearby text as title (max 60 chars)
                        title = line[:60]
                        if title in seen_titles:
                            continue
                        seen_titles.add(title)
                        found_chapters.append({
                            "title": title,
                            "page_start": page_idx + 1,
                            "page_end": None,
                            "level": 1,
                        })
                        break
    finally:
        doc.close()

    if not found_chapters:
        return None

    # Compute page_end
    for i in range(len(found_chapters)):
        if i + 1 < len(found_chapters):
            found_chapters[i]["page_end"] = found_chapters[i + 1]["page_start"] - 1
        else:
            found_chapters[i]["page_end"] = total_pages

    return {
        "strategy": "keywords",
        "total_pages": total_pages,
        "chapters": found_chapters,
    }


# ─── Strategy 2: Visual TOC scan (placeholder) ───────────────────────────────


def detect_toc_via_visual(pdf_path: Path) -> Optional[dict]:
    """Vision-based TOC detection — finds "目录" / "Mục lục" pages, OCRs them.

    NOT YET IMPLEMENTED. Requires hooking into MinerU or PaddleOCR.
    Defer to v2 when more books need it. For now always returns None.
    """
    return None


# ─── Top-level detect_toc ────────────────────────────────────────────────────


def detect_toc(pdf_path: Path) -> dict:
    """Try all strategies in priority order. Always returns a result
    (falls back to single-chapter "whole book" if nothing found)."""
    import fitz

    pdf_path = Path(pdf_path)

    # Strategy 1
    result = detect_toc_via_bookmarks(pdf_path)
    if result:
        logger.info(f"📖 TOC via bookmarks: {len(result['chapters'])} chapters")
        return result

    # Strategy 2 (placeholder)
    result = detect_toc_via_visual(pdf_path)
    if result:
        return result

    # Strategy 3
    result = detect_toc_via_keywords(pdf_path)
    if result:
        logger.info(f"📖 TOC via keywords: {len(result['chapters'])} chapters")
        return result

    # Fallback: single chapter
    doc = fitz.open(pdf_path)
    total = doc.page_count
    doc.close()
    logger.info(f"📖 TOC fallback: single-chapter (no TOC found, {total} pages)")
    return {
        "strategy": "fallback",
        "total_pages": total,
        "chapters": [{
            "title": "Toàn bộ sách (no TOC)",
            "page_start": 1,
            "page_end": total,
            "level": 1,
        }],
    }


# ─── Persistence ─────────────────────────────────────────────────────────────


def save_toc(toc_result: dict, output_path: Path) -> Path:
    """Save TOC as human-readable markdown."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# Mục lục — Detected")
    lines.append("")
    lines.append(f"**Strategy**: `{toc_result['strategy']}`")
    lines.append(f"**Total pages**: {toc_result['total_pages']}")
    lines.append(f"**Chapters**: {len(toc_result['chapters'])}")
    lines.append("")
    lines.append("## Chapters")
    lines.append("")
    lines.append("| # | Title | Page range |")
    lines.append("|---|---|---|")
    for i, ch in enumerate(toc_result["chapters"], 1):
        page_range = f"{ch['page_start']}–{ch['page_end']}"
        lines.append(f"| {i} | {ch['title']} | {page_range} |")

    lines.append("")
    if toc_result["strategy"] == "fallback":
        lines.append(
            "_⚠ Không detect được TOC tự động. Anh có thể edit file này thủ công._"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
