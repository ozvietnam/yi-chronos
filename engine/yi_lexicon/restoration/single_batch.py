"""Single-batch runner — chạy đúng 1 batch rồi exit.

Dùng bởi parallel_dispatcher.py: launch nhiều instance đồng thời với khác
batch_id + provider để tận dụng đa-provider.

CLI:
    python3 -m engine.yi_lexicon.restoration.single_batch \\
        --corpus-id 4 \\
        --batch-id p1-batch-03 \\
        --provider minimax \\
        --model MiniMax-M2
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from ..store import bootstrap_db
from .pipeline import RestorationConfig, restore_book
from .plan import load_plan, mark_batch, save_plan, append_log


def run_single(
    corpus_id: int,
    batch_id: str,
    *,
    provider: str = "ollama",
    model: str | None = None,
    ocr_backend: str = "qwen-vl",
    ocr_model: str | None = None,
    dpi: int = 200,
) -> dict:
    """Restore exactly the batch with given batch_id. Returns summary."""
    bootstrap_db()
    plan = load_plan(corpus_id)
    if not plan:
        return {"status": "error", "message": f"no plan for corpus {corpus_id}"}
    batch = next((b for b in plan.phase1_batches if b.batch_id == batch_id), None)
    if not batch:
        return {"status": "error", "message": f"batch {batch_id} not found"}

    # Mark in_progress
    mark_batch(plan, batch_id, status="in_progress", pages_done=0,
               notes=f"single-batch via {provider}/{model or 'default'}")
    append_log(plan, f"{batch_id} STARTED via single-batch ({provider}/{model or 'default'})")
    save_plan(plan)

    cfg = RestorationConfig(
        ocr_backend=ocr_backend,
        ocr_model=ocr_model,
        dpi=dpi,
        page_range=(batch.page_start, batch.page_end),
        llm_provider=provider,
        llm_model=model or "qwen2.5:7b-instruct-q8_0",
        incremental=True,
        extract_figures=True,
    )

    t0 = time.time()
    expected = batch.page_end - batch.page_start + 1
    print(f"[{time.strftime('%H:%M:%S')}] {batch_id} START · pages {batch.page_start}-{batch.page_end} · {provider}/{model}", flush=True)

    try:
        r = restore_book(corpus_id, config=cfg)
    except Exception as e:
        plan = load_plan(corpus_id)
        mark_batch(plan, batch_id, status="failed", notes=f"Exception: {e}")
        append_log(plan, f"{batch_id} FAILED via single-batch — {e}")
        save_plan(plan)
        return {"status": "error", "batch_id": batch_id, "error": str(e)}

    dt = time.time() - t0
    if r.pages_processed >= max(45, expected - 5):
        status = "done"
    elif r.pages_processed == 0:
        status = "failed"
    else:
        status = "pending"

    plan = load_plan(corpus_id)
    mark_batch(plan, batch_id, status=status, pages_done=r.pages_processed,
               notes=f"{provider} {r.pages_processed}/{expected} · {dt/60:.1f}min · {r.wikilinks_total}wls · {r.figures_extracted}fig")
    append_log(plan, f"{batch_id} FINISHED via single-batch: {status} · {r.pages_processed}/{expected} · {dt/60:.1f}min · provider={provider}")
    save_plan(plan)

    print(f"[{time.strftime('%H:%M:%S')}] {batch_id} DONE · status={status} · {r.pages_processed}/{expected} · {dt/60:.1f}min", flush=True)

    return {
        "status": "ok",
        "batch_id": batch_id,
        "batch_status": status,
        "pages_processed": r.pages_processed,
        "pages_failed": r.pages_failed,
        "wikilinks_total": r.wikilinks_total,
        "figures_extracted": r.figures_extracted,
        "duration_minutes": round(dt / 60, 1),
        "provider": provider,
        "model": model,
        "errors": r.errors[:5],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run exactly one Phase 1 batch.")
    parser.add_argument("--corpus-id", type=int, required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--provider", default="ollama",
                        choices=["ollama", "deepseek", "zai", "anthropic", "minimax",
                                 "gemini", "openrouter", "auto"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--ocr-backend", default="qwen-vl")
    parser.add_argument("--ocr-model", default=None)
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args(argv)

    summary = run_single(
        corpus_id=args.corpus_id,
        batch_id=args.batch_id,
        provider=args.provider,
        model=args.model,
        ocr_backend=args.ocr_backend,
        ocr_model=args.ocr_model,
        dpi=args.dpi,
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
