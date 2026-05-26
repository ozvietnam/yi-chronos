"""Onboarding orchestrator — runs Stage 1.1 → 2.3 for a book.

Wires together page_splitter, book_profiler, toc_detector, plan_generator
into a single function that takes a PDF + book_id and produces all
analysis artifacts needed before OCR runs.

Output structure:
    data/yi_publishing/onboarding/<book_id>/
        thumbnails/p0001.jpg ... pNNNN.jpg
        page_types.json
        _analysis_page.png           (sample for column detection)
        _spike/default/...           (MinerU spike output config A)
        _spike/no-formula/...        (MinerU spike output config B)
        book_profile.json
        _TOC.md
        _OCR-CONFIG.json
        _READING-PLAN.md
        _TRANSLATION-PLAN.md
        _LLM-ROUTING.md
        _PLAN-SUMMARY.json
        onboarding_log.json          (timing, errors, decisions)

Usage:
    from engine.yi_publishing.onboarding import onboard_book
    summary = onboard_book(
        book_id="shao-yong-...",
        pdf_path=Path("data/raw_pdfs/...pdf"),
        output_dir=Path("data/yi_publishing/onboarding/shao-yong-..."),
    )
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def onboard_book(
    *,
    book_id: str,
    pdf_path: Path,
    output_dir: Path,
    n_sample_pages: int = 3,
    mineru_runner: Optional[Callable] = None,
    skip_thumbnails: bool = False,
) -> dict:
    """Run the full onboarding pipeline for one book.

    Args:
        book_id: stable identifier (slug)
        pdf_path: path to source PDF
        output_dir: where to write all artifacts
        n_sample_pages: number of pages to use for profiling spike test
                        (5 pages × 2 configs × ~21s ≈ 3.5 min for real MinerU)
        mineru_runner: dependency-injected MinerU runner (None = use default).
                       For tests, pass a mock.
        skip_thumbnails: skip thumbnail rendering (faster for re-runs)

    Returns:
        dict with summary: phase timings, profile, toc, plan summary.
    """
    from engine.yi_publishing.book_profiler import profile_book
    from engine.yi_publishing.page_splitter import (
        analyze_book,
        pick_sample_pages_for_profile,
    )
    from engine.yi_publishing.plan_generator import generate_all_plans
    from engine.yi_publishing.toc_detector import detect_toc, save_toc

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    log = {
        "book_id": book_id,
        "pdf_path": str(pdf_path),
        "started_at": time.time(),
        "stages": {},
    }

    # ─── Stage 1.2: page split + thumbnails ──────────────────────────────────
    if not skip_thumbnails:
        t0 = time.time()
        page_analysis = analyze_book(
            pdf_path, output_dir, max_dim=200, skip_existing=True
        )
        log["stages"]["page_split"] = {
            "duration_s": round(time.time() - t0, 2),
            "page_count": page_analysis["page_count"],
            "type_counts": page_analysis["type_counts"],
        }
        logger.info(
            f"📄 Stage 1.2 (page split) done in {log['stages']['page_split']['duration_s']}s — "
            f"{page_analysis['page_count']} pages"
        )
    else:
        page_analysis = json.loads(
            (output_dir / "page_types.json").read_text(encoding="utf-8")
        )

    # ─── Stage 1.3: profile + spike test ─────────────────────────────────────
    sample_pages = pick_sample_pages_for_profile(
        page_analysis, n_samples=n_sample_pages, prefer_type="text"
    )
    if not sample_pages:
        sample_pages = [1]
    log["sample_pages"] = sample_pages

    t0 = time.time()
    profile = profile_book(
        pdf_path=pdf_path,
        sample_pages=sample_pages,
        output_root=output_dir,
        mineru_runner=mineru_runner,  # None → real MinerU subprocess
    )
    log["stages"]["profile"] = {
        "duration_s": round(time.time() - t0, 2),
        "columns": profile["columns"],
        "density": profile["density"],
        "script": profile["script"],
        "ocr_winner": profile["spike_result"]["winner"]["name"],
        "equation_ratio_winner": profile["spike_result"]["winner"].get(
            "equation_ratio"
        ),
    }
    logger.info(
        f"🔍 Stage 1.3 (profile + spike) done in {log['stages']['profile']['duration_s']}s — "
        f"columns={profile['columns']}, "
        f"winner={profile['spike_result']['winner']['name']}"
    )

    # ─── Stage 2.1: TOC detection ────────────────────────────────────────────
    t0 = time.time()
    toc = detect_toc(pdf_path)
    save_toc(toc, output_dir / "_TOC.md")
    log["stages"]["toc"] = {
        "duration_s": round(time.time() - t0, 2),
        "strategy": toc["strategy"],
        "chapters": len(toc["chapters"]),
    }
    logger.info(
        f"📖 Stage 2.1 (TOC) done in {log['stages']['toc']['duration_s']}s — "
        f"{toc['strategy']}, {len(toc['chapters'])} chapters"
    )

    # ─── Stage 2.2: plan generation ──────────────────────────────────────────
    t0 = time.time()
    plan_summary = generate_all_plans(profile, toc, output_dir)
    log["stages"]["plan"] = {
        "duration_s": round(time.time() - t0, 2),
        "chunks": plan_summary["chunks_count"],
        "eta_ocr_hours": plan_summary["estimated_ocr_hours"],
        "workers": plan_summary["ocr_config"]["workers"],
    }
    logger.info(
        f"📋 Stage 2.2 (plan) done in {log['stages']['plan']['duration_s']}s — "
        f"{plan_summary['chunks_count']} chunks, "
        f"ETA {plan_summary['estimated_ocr_hours']}h OCR"
    )

    # ─── Summary ────────────────────────────────────────────────────────────
    log["ended_at"] = time.time()
    log["total_duration_s"] = round(log["ended_at"] - log["started_at"], 2)

    (output_dir / "onboarding_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "book_id": book_id,
        "page_count": page_analysis["page_count"],
        "profile": {
            "columns": profile["columns"],
            "density": profile["density"],
            "script": profile["script"],
        },
        "ocr_config": plan_summary["ocr_config"],
        "toc": {
            "strategy": toc["strategy"],
            "chapter_count": len(toc["chapters"]),
        },
        "plan": {
            "chunks_count": plan_summary["chunks_count"],
            "estimated_ocr_hours": plan_summary["estimated_ocr_hours"],
        },
        "duration_s": log["total_duration_s"],
        "output_dir": str(output_dir),
    }
    return summary
