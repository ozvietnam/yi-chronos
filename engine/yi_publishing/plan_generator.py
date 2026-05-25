"""Plan generator — Stage 2.2 of Smart Book Onboarding.

Combines book_profile.json + _TOC.md to generate 4 artifacts:
  - _OCR-CONFIG.json     : machine-readable config for Stage 4 OCR
  - _READING-PLAN.md     : S/A/B/C tier per chapter (human-editable)
  - _TRANSLATION-PLAN.md : chunked plan + LLM routing
  - _LLM-ROUTING.md      : content-type → provider/model table

All outputs Anh-editable. Template-based, no LLM call needed here.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ─── OCR config ──────────────────────────────────────────────────────────────


def _recommend_workers(total_pages: int) -> int:
    """Decide swarm worker count based on book size.

    <50 pages: 1 worker (no parallel benefit, overhead > saving)
    50–200: 2 workers
    200–500: 3 workers
    >500: 4 workers (max RAM cho M4 36GB)
    """
    if total_pages < 50:
        return 1
    if total_pages < 200:
        return 2
    if total_pages < 500:
        return 3
    return 4


def generate_ocr_config(profile: dict, toc: dict, output_dir: Path) -> dict:
    """Generate _OCR-CONFIG.json from profile + TOC.

    Returns the config dict (and writes to file).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base = profile["ocr_config"]
    cfg = {
        "backend": base.get("backend", "pipeline"),
        "language": base.get("language", "ch"),
        "method": base.get("method", "auto"),
        "formula_enable": base.get("formula_enable", True),
        "workers": _recommend_workers(toc["total_pages"]),
        "rationale": base.get("rationale", ""),
        "approved_at": None,  # Anh will set after review
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    (output_dir / "_OCR-CONFIG.json").write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return cfg


# ─── Reading plan ────────────────────────────────────────────────────────────

_APPENDIX_PATTERNS = re.compile(
    r"(phụ\s*lục|appendix|附录|附錄|index|bảng\s*tra)", re.IGNORECASE
)
_INTRO_PATTERNS = re.compile(r"(lời\s*nói\s*đầu|preface|前言|序)", re.IGNORECASE)


def _default_chapter_tier(chapter: dict) -> str:
    """Suggest S/A/B/C tier from chapter title.

    Heuristic:
      - Appendix/index/bảng tra → C (reference only)
      - Lời nói đầu/preface → B (skim)
      - Others → A (default — most chapters)
      - S is reserved cho anh manual mark (cốt lõi đặc biệt)
    """
    title = chapter.get("title", "")
    if _APPENDIX_PATTERNS.search(title):
        return "C"
    if _INTRO_PATTERNS.search(title):
        return "B"
    return "A"


def generate_reading_plan(profile: dict, toc: dict, output_dir: Path) -> Path:
    """Generate _READING-PLAN.md table with S/A/B/C tier per chapter."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Reading Plan",
        "",
        "Tier system (S/A/B/C) cho mức độ ưu tiên đọc + dịch:",
        "- **S-tier**: chương cốt lõi (đọc kỹ + journal thâm nhuần)",
        "- **A-tier**: chương quan trọng (đọc trung bình + dịch đầy đủ)",
        "- **B-tier**: chương tham khảo (skim + dịch chính)",
        "- **C-tier**: phụ lục / index (chỉ extract wiki, có thể bỏ qua bản dịch chi tiết)",
        "",
        f"_Auto-generated 2026 — Anh edit free-form._",
        "",
        "| # | Chapter | Page range | Tier | Effort estimate | Notes |",
        "|---|---|---|---|---|---|",
    ]

    for i, ch in enumerate(toc["chapters"], 1):
        tier = _default_chapter_tier(ch)
        pages = ch["page_end"] - ch["page_start"] + 1
        # Effort: rough estimate cho dịch (1 trang = 5-10 phút Anh time tier A)
        effort_hr = {"S": pages * 0.4, "A": pages * 0.15, "B": pages * 0.05, "C": 0}.get(tier, 0.1)
        lines.append(
            f"| {i} | {ch['title']} | {ch['page_start']}–{ch['page_end']} "
            f"| {tier} | ~{effort_hr:.1f}h | |"
        )

    lines.append("")
    lines.append(f"**Total pages**: {toc['total_pages']}")
    lines.append(f"**TOC strategy**: `{toc['strategy']}`")

    out = output_dir / "_READING-PLAN.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ─── Translation plan ────────────────────────────────────────────────────────

MAX_CHUNK_PAGES = 100  # split large chapters
TARGET_CHUNK_PAGES = 50  # ideal chunk size


def _split_chapter_into_chunks(
    chapter: dict, *, max_chunk_pages: int = MAX_CHUNK_PAGES
) -> list[dict]:
    """Split a chapter into multiple chunks if too large.

    Each chunk inherits chapter title with " (Part X)" suffix.
    """
    start = chapter["page_start"]
    end = chapter["page_end"]
    pages = end - start + 1
    if pages <= max_chunk_pages:
        return [{"title": chapter["title"], "page_start": start, "page_end": end}]

    chunks = []
    n_parts = (pages + max_chunk_pages - 1) // max_chunk_pages
    chunk_size = (pages + n_parts - 1) // n_parts
    cs = start
    part = 1
    while cs <= end:
        ce = min(cs + chunk_size - 1, end)
        chunks.append({
            "title": f"{chapter['title']} (Part {part}/{n_parts})",
            "page_start": cs,
            "page_end": ce,
        })
        cs = ce + 1
        part += 1
    return chunks


def _pick_llm_route(profile: dict) -> dict:
    """Pick LLM routing based on script + density."""
    script = profile.get("script", "unknown")
    density = profile.get("density", "normal")
    columns = profile.get("columns", 1)

    # Classical Chinese dense → reasoner (cổ văn cần suy luận)
    # Modern Chinese → chat (faster, sufficient)
    # Vietnamese → chat
    # Latin → chat
    if script == "chinese" and (density in ("dense", "saturated") or columns >= 2):
        primary = "deepseek-reasoner"
        fallback = "deepseek-chat"
        notes = "Classical Chinese + dense/multi-col → reasoner cho suy luận cổ văn"
    elif script == "chinese":
        primary = "deepseek-chat"
        fallback = "claude-sonnet"
        notes = "Modern Chinese → chat (faster, good quality)"
    elif script in ("vietnamese", "latin"):
        primary = "deepseek-chat"
        fallback = "claude-sonnet"
        notes = "Vietnamese/Latin → chat model"
    else:
        primary = "deepseek-chat"
        fallback = "claude-sonnet"
        notes = "Unknown script — default chat"

    return {
        "primary": primary,
        "fallback": fallback,
        "rationale": notes,
    }


def generate_translation_plan(
    profile: dict, toc: dict, output_dir: Path
) -> dict:
    """Generate _TRANSLATION-PLAN.md + return plan dict.

    Strategy:
      - If TOC has real chapters (strategy != fallback): chunk by chapter,
        split chapters >100 pages.
      - If TOC fallback: equal split into ~50-page chunks.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chunks: list[dict] = []
    if toc["strategy"] == "fallback":
        # Equal split
        total = toc["total_pages"]
        n_chunks = max(1, (total + TARGET_CHUNK_PAGES - 1) // TARGET_CHUNK_PAGES)
        chunk_size = (total + n_chunks - 1) // n_chunks
        cs = 1
        for i in range(n_chunks):
            ce = min(cs + chunk_size - 1, total)
            chunks.append({
                "title": f"Phần {i + 1}/{n_chunks} (no TOC)",
                "page_start": cs,
                "page_end": ce,
            })
            cs = ce + 1
    else:
        for ch in toc["chapters"]:
            chunks.extend(_split_chapter_into_chunks(ch))

    llm_route = _pick_llm_route(profile)

    plan = {
        "chunks": chunks,
        "llm_route": llm_route,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    # Markdown rendering
    lines = [
        "# Translation Plan",
        "",
        f"**Total chunks**: {len(chunks)}",
        f"**Total pages**: {toc['total_pages']}",
        f"**Primary LLM**: `{llm_route['primary']}`",
        f"**Fallback LLM**: `{llm_route['fallback']}`",
        f"**Rationale**: {llm_route['rationale']}",
        "",
        "## Chunks",
        "",
        "| # | Title | Page range | Pages |",
        "|---|---|---|---|",
    ]
    for i, ch in enumerate(chunks, 1):
        n = ch["page_end"] - ch["page_start"] + 1
        lines.append(f"| {i} | {ch['title']} | {ch['page_start']}–{ch['page_end']} | {n} |")

    (output_dir / "_TRANSLATION-PLAN.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return plan


# ─── LLM routing markdown ────────────────────────────────────────────────────


def generate_llm_routing(profile: dict, toc: dict, output_dir: Path) -> Path:
    """Generate _LLM-ROUTING.md — table mapping content-type → LLM."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    route = _pick_llm_route(profile)
    lines = [
        "# LLM Routing",
        "",
        f"**Primary**: `{route['primary']}`",
        f"**Fallback**: `{route['fallback']}`",
        f"**Rationale**: {route['rationale']}",
        "",
        "## Routing per content type",
        "",
        "| Content type | Provider | Model | Notes |",
        "|---|---|---|---|",
        "| Cổ văn (classical Chinese paragraph) | DeepSeek | deepseek-reasoner | Suy luận cổ ngữ |",
        "| Hiện đại (modern Chinese paragraph) | DeepSeek | deepseek-chat | Faster, sufficient |",
        "| Tiêu đề chương (title block) | DeepSeek | deepseek-chat | Short, no reasoning needed |",
        "| Bảng (table cells) | Claude | claude-sonnet | Structured output |",
        "| Hình minh hoạ (image caption) | DeepSeek | deepseek-chat | |",
        "| Phụ lục (appendix index) | Skip translation | — | Extract wiki only |",
        "",
        f"**Auto-detected script**: `{profile.get('script', 'unknown')}`",
        f"**Density**: `{profile.get('density', 'unknown')}`",
        f"**Columns**: `{profile.get('columns', '?')}`",
    ]

    out = output_dir / "_LLM-ROUTING.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# ─── Estimated time ──────────────────────────────────────────────────────────


def _estimate_ocr_hours(pages: int, workers: int, formula_enable: bool) -> float:
    """Rough: 1.5 phút/trang sequential, 85% efficiency per worker."""
    per_page_min = 1.5
    if not formula_enable:
        per_page_min *= 0.9  # slight speedup without formula parsing
    speedup = 1.0 if workers == 1 else workers * 0.85
    return round((pages * per_page_min) / 60 / speedup, 2)


# ─── End-to-end ──────────────────────────────────────────────────────────────


def generate_all_plans(profile: dict, toc: dict, output_dir: Path) -> dict:
    """Generate all 4 plan artifacts. Returns summary dict."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ocr_cfg = generate_ocr_config(profile, toc, output_dir)
    reading_plan_path = generate_reading_plan(profile, toc, output_dir)
    trans_plan = generate_translation_plan(profile, toc, output_dir)
    llm_routing_path = generate_llm_routing(profile, toc, output_dir)

    eta_hours = _estimate_ocr_hours(
        toc["total_pages"], ocr_cfg["workers"], ocr_cfg["formula_enable"]
    )

    summary = {
        "ocr_config": ocr_cfg,
        "chunks_count": len(trans_plan["chunks"]),
        "estimated_ocr_hours": eta_hours,
        "llm_primary": trans_plan["llm_route"]["primary"],
        "files": [
            "_OCR-CONFIG.json",
            "_READING-PLAN.md",
            "_TRANSLATION-PLAN.md",
            "_LLM-ROUTING.md",
        ],
    }

    (output_dir / "_PLAN-SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        f"📋 Plan generated — {summary['chunks_count']} chunks, "
        f"ETA {eta_hours}h OCR (workers={ocr_cfg['workers']})"
    )
    return summary
