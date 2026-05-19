"""Nightly batch runner — phục chế hàng loạt khi anh ngủ.

Cách dùng:
    # Chạy tay: phục chế tất cả sách tier S+A đến khi hết hoặc đạt time_budget
    python3 -m engine.yi_lexicon.restoration.nightly --max-hours 8 --tiers S A

    # Chạy 1 sách cụ thể
    python3 -m engine.yi_lexicon.restoration.nightly --corpus-id 4

    # Chạy mặc định (Ollama + Qwen2.5 + tier ưu tiên)
    python3 -m engine.yi_lexicon.restoration.nightly

Cron (chạy 22:00 đêm, dừng 06:00 sáng):
    0 22 * * * cd /Users/.../yi && python3 -m engine.yi_lexicon.restoration.nightly \\
        --max-hours 8 --provider ollama --ocr-backend qwen-vl >> nightly.log 2>&1

Đặc tính:
- **Idempotent**: dùng `incremental=True` của pipeline, trang đã phục chế bỏ qua
- **Time budget**: dừng đúng giờ, lưu state, đêm sau resume
- **Priority queue**: ưu tiên tier S → A → B → C, sách `restored_status='pending'` ưu tiên
- **Per-book chunk**: mỗi sách phục chế chunk N trang rồi sang sách khác (anh có nhiều sách dở dang đều đặn)
- **Log JSONL**: mỗi page event 1 dòng → grep + analytics
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from dataclasses import asdict
from pathlib import Path

from ..store import bootstrap_db, get_corpus, list_corpora, update_corpus
from .pipeline import RestorationConfig, restore_book


LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "yi_restored" / "_logs"


def _now() -> int:
    return int(time.time())


def _open_log() -> tuple[Path, "object"]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"nightly-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
    return log_path, log_path.open("a", encoding="utf-8")


def _log(fh, event: dict) -> None:
    event["ts"] = _now()
    fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    fh.flush()


# Tier priority — lower number = higher priority
_TIER_RANK = {"S": 0, "A": 1, "B": 2, "C": 3}


def select_queue(
    *,
    tiers: list[str] | None = None,
    only_corpus_id: int | None = None,
    skip_done: bool = True,
) -> list:
    """Pick books to process this run, sorted by priority.

    Priority:
    1. Books with restored_status='partial' (resume in-flight first)
    2. Books with restored_status='none' OR 'pending'
    3. Higher tier first within each bucket
    """
    bootstrap_db()
    all_books = list_corpora()
    queue = []
    for c in all_books:
        if only_corpus_id and c.corpus_id != only_corpus_id:
            continue
        if tiers and c.tier not in tiers:
            continue
        if skip_done and c.restored_status == "done":
            continue
        if c.restored_status == "skip":
            continue
        if not c.file_path:
            continue
        queue.append(c)

    def sort_key(c):
        status_rank = (
            0 if c.restored_status == "partial" else
            1 if c.restored_status in ("none", "pending") else
            2
        )
        tier_rank = _TIER_RANK.get(c.tier, 9)
        return (status_rank, tier_rank, c.corpus_id)

    queue.sort(key=sort_key)
    return queue


class TimeBudget:
    """Track elapsed time + provide kill signal handler."""
    def __init__(self, max_hours: float):
        self.max_seconds = max_hours * 3600 if max_hours > 0 else None
        self.start = _now()
        self.stopped = False

    def exceeded(self) -> bool:
        if self.stopped:
            return True
        if self.max_seconds is None:
            return False
        return (_now() - self.start) >= self.max_seconds

    def remaining(self) -> float:
        if self.max_seconds is None:
            return float("inf")
        return max(0.0, self.max_seconds - (_now() - self.start))


def run_nightly(
    *,
    max_hours: float = 8.0,
    tiers: list[str] | None = None,
    only_corpus_id: int | None = None,
    pages_per_chunk: int = 20,
    provider: str = "ollama",
    ocr_backend: str = "qwen-vl",
    ocr_model: str | None = None,
    llm_model: str | None = None,
    dpi: int = 200,
    dry_run: bool = False,
) -> dict:
    """Run the nightly batch. Returns summary dict.

    Loops: for each book in priority queue, restore `pages_per_chunk` pages,
    then move to next book. Repeats until queue exhausted or time runs out.
    Books với progress dở dang sẽ được resume vào lần chạy sau (incremental).
    """
    budget = TimeBudget(max_hours)

    # Graceful shutdown: SIGTERM/SIGINT → mark stopped (sẽ exit sau page hiện tại)
    def _stop(_sig, _frame):
        budget.stopped = True
        print(f"[nightly] Stop signal received — finishing current page…", flush=True)
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    log_path, fh = _open_log()
    _log(fh, {
        "event": "start", "max_hours": max_hours, "tiers": tiers,
        "provider": provider, "ocr_backend": ocr_backend,
        "ocr_model": ocr_model, "llm_model": llm_model,
        "pages_per_chunk": pages_per_chunk, "dpi": dpi,
    })

    queue = select_queue(tiers=tiers, only_corpus_id=only_corpus_id)
    _log(fh, {"event": "queue", "count": len(queue),
              "books": [{"corpus_id": c.corpus_id, "name": c.name,
                          "tier": c.tier, "status": c.restored_status,
                          "pages_total": c.pages_total} for c in queue[:30]]})
    print(f"[nightly] Queue: {len(queue)} books · budget {max_hours}h", flush=True)

    if dry_run:
        fh.close()
        return {"dry_run": True, "queue_size": len(queue), "log": str(log_path)}

    totals = {
        "books_touched": 0, "pages_processed": 0, "pages_failed": 0,
        "wikilinks_total": 0, "figures_extracted": 0, "errors": [],
        "started_at": _now(), "log": str(log_path),
    }

    # Iterate rounds: each round give each book `pages_per_chunk` pages
    cycle_no = 0
    while queue and not budget.exceeded():
        cycle_no += 1
        any_progress = False
        for c in list(queue):
            if budget.exceeded():
                break
            fresh = get_corpus(corpus_id=c.corpus_id)
            if not fresh:
                queue.remove(c)
                continue
            if fresh.restored_status == "done":
                queue.remove(c)
                continue
            # How many pages remaining for this book?
            done = fresh.restored_pages or 0
            total = fresh.pages_total or 0
            remaining = total - done if total > 0 else pages_per_chunk
            chunk = min(pages_per_chunk, remaining if remaining > 0 else pages_per_chunk)
            if chunk <= 0:
                queue.remove(c)
                continue
            page_start = done + 1
            page_end = page_start + chunk - 1

            _log(fh, {
                "event": "chunk-start", "corpus_id": fresh.corpus_id,
                "name": fresh.name, "tier": fresh.tier,
                "page_start": page_start, "page_end": page_end,
                "cycle": cycle_no,
            })
            print(f"[nightly] cycle {cycle_no} · {fresh.name} · "
                  f"pages {page_start}-{page_end} ({done}/{total})", flush=True)

            cfg = RestorationConfig(
                ocr_backend=ocr_backend,
                ocr_model=ocr_model,
                dpi=dpi,
                page_range=(page_start, page_end),
                llm_provider=provider,
                llm_model=llm_model or "qwen2.5:7b",
                incremental=True,
            )
            t0 = time.time()
            try:
                res = restore_book(fresh.corpus_id, config=cfg)
            except Exception as e:
                _log(fh, {"event": "chunk-error", "corpus_id": fresh.corpus_id,
                          "error": f"{type(e).__name__}: {e}"})
                totals["errors"].append({"corpus_id": fresh.corpus_id, "error": str(e)})
                continue
            dt = time.time() - t0
            _log(fh, {
                "event": "chunk-done", "corpus_id": fresh.corpus_id,
                "pages_processed": res.pages_processed,
                "pages_failed": res.pages_failed,
                "wikilinks_total": res.wikilinks_total,
                "figures_extracted": res.figures_extracted,
                "duration_seconds": round(dt, 1),
                "errors": res.errors[:5],
            })
            totals["pages_processed"] += res.pages_processed
            totals["pages_failed"] += res.pages_failed
            totals["wikilinks_total"] += res.wikilinks_total
            totals["figures_extracted"] += res.figures_extracted
            if res.pages_processed > 0:
                any_progress = True
                totals["books_touched"] = len({
                    b.corpus_id for b in queue if get_corpus(corpus_id=b.corpus_id).restored_pages
                })

            # If book is done, remove from queue
            after = get_corpus(corpus_id=fresh.corpus_id)
            if after and after.restored_status == "done":
                _log(fh, {"event": "book-done", "corpus_id": after.corpus_id, "name": after.name})
                queue.remove(c)

        if not any_progress:
            _log(fh, {"event": "no-progress-stall", "cycle": cycle_no})
            break  # avoid infinite loop if all books error out

    totals["finished_at"] = _now()
    totals["duration_seconds"] = totals["finished_at"] - totals["started_at"]
    totals["budget_exceeded"] = budget.exceeded()
    _log(fh, {"event": "end", **{k: v for k, v in totals.items() if k != "errors"}})
    fh.close()
    return totals


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="YI-Lexicon nightly restoration runner."
    )
    parser.add_argument("--max-hours", type=float, default=8.0,
                        help="Time budget in hours (0 = unlimited). Default 8.")
    parser.add_argument("--tiers", nargs="+", default=["S", "A"],
                        help="Tier(s) to prioritize. Default: S A.")
    parser.add_argument("--corpus-id", type=int, default=None,
                        help="Restore only this corpus (overrides --tiers).")
    parser.add_argument("--pages-per-chunk", type=int, default=20,
                        help="Pages to restore per book before moving on. Default 20.")
    parser.add_argument("--provider", default="ollama",
                        choices=["ollama", "deepseek", "zai", "anthropic", "auto"],
                        help="LLM provider for cleanup. Default ollama (free, local).")
    parser.add_argument("--ocr-backend", default="qwen-vl",
                        choices=["tesseract", "qwen-vl", "minicpm-v", "ollama-vision"],
                        help="OCR backend. Default qwen-vl (Ollama vision).")
    parser.add_argument("--ocr-model", default=None,
                        help="Override OCR model (e.g. qwen2.5-vl:7b).")
    parser.add_argument("--llm-model", default=None,
                        help="LLM model for cleanup (e.g. qwen2.5:7b).")
    parser.add_argument("--dpi", type=int, default=200, help="Render DPI.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show queue + plan, don't process.")
    args = parser.parse_args(argv)

    summary = run_nightly(
        max_hours=args.max_hours,
        tiers=args.tiers,
        only_corpus_id=args.corpus_id,
        pages_per_chunk=args.pages_per_chunk,
        provider=args.provider,
        ocr_backend=args.ocr_backend,
        ocr_model=args.ocr_model,
        llm_model=args.llm_model,
        dpi=args.dpi,
        dry_run=args.dry_run,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
