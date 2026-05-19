"""Chain runner — chạy tuần tự các batch còn pending trong plan.

Khác với `nightly.py`: nightly chạy multi-book + round-robin chunk.
Chain runner: 1 book, chạy hết các batch pending theo thứ tự cho đến khi xong
hoặc hết time budget hoặc gặp lỗi liên tiếp.

Usage:
    python3 -m engine.yi_lexicon.restoration.chain_runner \\
        --corpus-id 4 \\
        --provider minimax \\
        --model coding-plan-vlm \\
        --max-batches 17 \\
        --max-consecutive-errors 3
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from pathlib import Path

from ..store import bootstrap_db, get_corpus
from .pipeline import RestorationConfig, restore_book
from .plan import load_plan, mark_batch, save_plan, append_log


LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "yi_restored" / "_logs"


def _open_log(corpus_id: int) -> tuple[Path, "object"]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"chain-c{corpus_id}-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
    return log_path, log_path.open("a", encoding="utf-8")


def _log(fh, event: dict) -> None:
    event["ts"] = int(time.time())
    fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    fh.flush()


def run_chain(
    corpus_id: int,
    *,
    provider: str = "ollama",
    model: str | None = None,
    ocr_backend: str = "qwen-vl",
    ocr_model: str | None = None,
    dpi: int = 200,
    max_batches: int = 20,
    max_consecutive_errors: int = 3,
    max_hours: float = 12.0,
    only_status: tuple = ("pending",),
) -> dict:
    """Run remaining batches sequentially.

    Stop conditions:
    - All batches done
    - max_batches reached
    - max_consecutive_errors hit
    - max_hours exceeded
    - SIGTERM/SIGINT
    """
    bootstrap_db()
    plan = load_plan(corpus_id)
    if not plan:
        return {"status": "error", "message": f"No plan for corpus {corpus_id}"}

    log_path, fh = _open_log(corpus_id)
    started_at = time.time()
    stopped = {"flag": False}

    def _stop(_sig, _frame):
        stopped["flag"] = True
        print("[chain] Stop signal — finishing current batch…", flush=True)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    _log(fh, {
        "event": "start", "corpus_id": corpus_id,
        "provider": provider, "model": model,
        "ocr_backend": ocr_backend, "ocr_model": ocr_model,
        "max_batches": max_batches, "max_hours": max_hours,
    })
    print(f"[chain] Plan: {plan.book_name}  ·  {len(plan.phase1_batches)} batches total",
          flush=True)

    summary = {
        "started_at": int(started_at),
        "batches_run": 0,
        "batches_done": 0,
        "batches_failed": 0,
        "pages_total": 0,
        "errors": [],
        "log_path": str(log_path),
    }

    consecutive_errors = 0

    for batch in plan.phase1_batches:
        if stopped["flag"]:
            break
        if (time.time() - started_at) / 3600.0 >= max_hours:
            print(f"[chain] Time budget {max_hours}h reached", flush=True)
            break
        if summary["batches_run"] >= max_batches:
            print(f"[chain] Max batches {max_batches} reached", flush=True)
            break
        if batch.status not in only_status:
            continue
        if consecutive_errors >= max_consecutive_errors:
            print(f"[chain] {max_consecutive_errors} consecutive errors — stopping", flush=True)
            break

        # Mark in_progress
        plan = load_plan(corpus_id)
        mark_batch(plan, batch.batch_id, status="in_progress", pages_done=0)
        append_log(plan, f"{batch.batch_id} STARTED via chain-runner ({provider}/{model or 'default'})")
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
        _log(fh, {
            "event": "batch-start", "batch_id": batch.batch_id,
            "page_start": batch.page_start, "page_end": batch.page_end,
        })
        print(f"[chain] {batch.batch_id}: pages {batch.page_start}-{batch.page_end}", flush=True)

        try:
            r = restore_book(corpus_id, config=cfg)
        except Exception as e:
            consecutive_errors += 1
            summary["batches_failed"] += 1
            summary["errors"].append({"batch": batch.batch_id, "error": str(e)})
            _log(fh, {"event": "batch-exception", "batch_id": batch.batch_id, "error": str(e)})
            plan = load_plan(corpus_id)
            mark_batch(plan, batch.batch_id, status="failed", notes=f"Exception: {e}")
            save_plan(plan)
            continue

        dt = time.time() - t0
        summary["batches_run"] += 1

        # Decide status
        expected = batch.page_end - batch.page_start + 1
        if r.pages_processed >= max(45, expected - 5):
            status = "done"
            summary["batches_done"] += 1
            consecutive_errors = 0
        elif r.pages_processed == 0:
            status = "failed"
            summary["batches_failed"] += 1
            consecutive_errors += 1
        else:
            status = "pending"
            consecutive_errors = 0  # partial OK

        summary["pages_total"] += r.pages_processed

        plan = load_plan(corpus_id)
        mark_batch(plan, batch.batch_id, status=status, pages_done=r.pages_processed,
                   notes=f"chain {provider}: {r.pages_processed}/{expected} OK · {dt/60:.1f}min · {r.wikilinks_total} wls · {r.figures_extracted} figs")
        append_log(plan, f"{batch.batch_id} FINISHED via chain: {status} · {r.pages_processed}/{expected} · {dt/60:.1f}min")
        save_plan(plan)

        _log(fh, {
            "event": "batch-done", "batch_id": batch.batch_id,
            "status": status, "pages_processed": r.pages_processed,
            "wikilinks_total": r.wikilinks_total,
            "duration_minutes": round(dt / 60, 1),
            "errors_count": len(r.errors),
        })
        print(f"[chain] {batch.batch_id}: {status} · {r.pages_processed}/{expected} · {dt/60:.1f}min · {r.wikilinks_total} wls",
              flush=True)

    summary["finished_at"] = int(time.time())
    summary["duration_seconds"] = summary["finished_at"] - summary["started_at"]
    _log(fh, {"event": "end", **{k: v for k, v in summary.items() if k != "errors"}})
    fh.close()
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="YI-Lexicon chain runner — chạy hết batch pending.")
    parser.add_argument("--corpus-id", type=int, required=True)
    parser.add_argument("--provider", default="ollama",
                        choices=["ollama", "deepseek", "zai", "anthropic", "minimax", "auto"])
    parser.add_argument("--model", default=None)
    parser.add_argument("--ocr-backend", default="qwen-vl")
    parser.add_argument("--ocr-model", default=None)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--max-batches", type=int, default=20)
    parser.add_argument("--max-consecutive-errors", type=int, default=3)
    parser.add_argument("--max-hours", type=float, default=12.0)
    args = parser.parse_args(argv)

    summary = run_chain(
        corpus_id=args.corpus_id,
        provider=args.provider,
        model=args.model,
        ocr_backend=args.ocr_backend,
        ocr_model=args.ocr_model,
        dpi=args.dpi,
        max_batches=args.max_batches,
        max_consecutive_errors=args.max_consecutive_errors,
        max_hours=args.max_hours,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
