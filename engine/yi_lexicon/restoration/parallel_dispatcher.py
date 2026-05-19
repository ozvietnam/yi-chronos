"""Parallel batch dispatcher — chạy N batch đồng thời với N provider khác nhau.

Tận dụng tối đa: anh có Ollama local + MiniMax + DeepSeek + ZAI + Gemini
+ OpenRouter. Mỗi provider chạy 1 batch riêng → 5-6 batch xong song song.

Strategy:
- Pool of (provider, model) — em probe trước cái nào configured
- Pop next pending batch + next available worker → spawn single_batch subprocess
- When subprocess exits, free worker, pop next batch
- Loop cho đến hết batch hoặc max_concurrent quota / max_hours

Khác chain runner (sequential): nhanh hơn 3-5x bằng cách dùng nhiều provider.

Safety:
- manifest + plan đã có file-lock + merge (parallel-safe)
- Mỗi worker write logs riêng → grep được

CLI:
    python3 -m engine.yi_lexicon.restoration.parallel_dispatcher \\
        --corpus-id 4 \\
        --max-concurrent 5 \\
        --max-hours 8
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from ..store import bootstrap_db
from .plan import load_plan


LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "yi_restored" / "_logs"
VENV_PYTHON = "/Users/ozvietnamdesktop/Desktop/yi/.venv/bin/python3"


# Worker definitions — provider + model + OCR backend.
# Order = priority (em pop từ trên xuống). 8 slots, configurable concurrency.
# OpenRouter models chọn theo probe 2026-05-12: 3 model verified work với privacy on.
# Backend "auto" = MarkItDown nếu có text layer (1300x faster), fallback qwen-vl OCR.
WORKERS = [
    # name                  provider        model                                      ocr_backend  ocr_model
    # Cloud paid/coding-plan — chất lượng cao
    ("ollama-vl-q8",        "ollama",       "qwen2.5:7b-instruct-q8_0",                "auto",      None),
    ("minimax-m2",          "minimax",      "MiniMax-M2",                              "auto",      None),
    ("deepseek-chat",       "deepseek",     "deepseek-chat",                           "auto",      None),
    ("zai-flash",           "zai",          "glm-4.5-flash",                           "auto",      None),
    # OpenRouter free tier — verified workers (privacy opt-in required)
    ("or-gpt-oss-120b",     "openrouter",   "openai/gpt-oss-120b:free",                "auto",      None),
    ("or-nvidia-120b",      "openrouter",   "nvidia/nemotron-3-super-120b-a12b:free",  "auto",      None),
    ("or-gpt-oss-20b",      "openrouter",   "openai/gpt-oss-20b:free",                 "auto",      None),
    # Gemini — last (free quota mỏng, 250 RPD trên 2.5-flash). Dùng 2.0 cho quota cao hơn.
    ("gemini-flash-2",      "gemini",       "gemini-2.0-flash",                        "auto",      None),
]


def _check_provider_configured(provider: str) -> bool:
    """Quick check if provider is usable (key set / server reachable)."""
    try:
        from engine.ai.registry import get_registry
        p = get_registry().get(provider)
        return p.is_configured
    except Exception:
        return False


def _pick_available_workers(max_concurrent: int) -> list[tuple]:
    """Return list of (name, provider, model, ocr_backend, ocr_model) — only configured ones."""
    available = []
    for w in WORKERS:
        if len(available) >= max_concurrent:
            break
        if _check_provider_configured(w[1]):
            available.append(w)
    return available


def _pending_batches(corpus_id: int) -> list:
    """List of batches in plan that are 'pending' (not done/in_progress)."""
    plan = load_plan(corpus_id)
    if not plan:
        return []
    return [b for b in plan.phase1_batches if b.status == "pending"]


def _spawn_worker(
    corpus_id: int, batch_id: str,
    worker: tuple,
    log_dir: Path,
) -> tuple["subprocess.Popen", str]:
    """Launch single_batch.py subprocess. Returns (proc, log_path)."""
    name, provider, model, ocr_backend, ocr_model = worker
    log_path = log_dir / f"par-{batch_id}-{name}.log"
    cmd = [
        VENV_PYTHON, "-u", "-m", "engine.yi_lexicon.restoration.single_batch",
        "--corpus-id", str(corpus_id),
        "--batch-id", batch_id,
        "--provider", provider,
        "--model", model,
        "--ocr-backend", ocr_backend,
    ]
    if ocr_model:
        cmd += ["--ocr-model", ocr_model]

    env = os.environ.copy()
    env.setdefault("OLLAMA_KEEP_ALIVE", "8h")
    env.setdefault("PYTHONUNBUFFERED", "1")

    log_f = log_path.open("w", encoding="utf-8")
    log_f.write(f"# Launched at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_f.write(f"# Command: {' '.join(cmd)}\n\n")
    log_f.flush()

    proc = subprocess.Popen(
        cmd,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=env,
        cwd="/Users/ozvietnamdesktop/Desktop/yi",
    )
    return proc, str(log_path)


def run_parallel(
    corpus_id: int,
    *,
    max_concurrent: int = 5,
    max_hours: float = 8.0,
    max_batches: int | None = None,
) -> dict:
    """Main dispatcher loop.

    1. Probe configured providers → workers
    2. Queue pending batches
    3. Pop worker + batch → spawn subprocess
    4. When any subprocess exits, free worker, pop next
    5. Stop on: queue empty / max_hours / SIGTERM
    """
    bootstrap_db()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start = time.time()
    stopped = {"flag": False}

    def _stop(_s, _f):
        stopped["flag"] = True
        print(f"[disp] Stop signal — letting workers finish…", flush=True)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    # Probe workers
    workers = _pick_available_workers(max_concurrent)
    if not workers:
        return {"status": "error", "message": "No provider configured"}

    print(f"[disp] Workers ready ({len(workers)}):", flush=True)
    for w in workers:
        print(f"  - {w[0]:18s} provider={w[1]:10s} model={w[2]}", flush=True)

    pending_queue = _pending_batches(corpus_id)
    if max_batches:
        pending_queue = pending_queue[:max_batches]
    if not pending_queue:
        return {"status": "ok", "message": "No pending batches"}

    print(f"[disp] Queue: {len(pending_queue)} batches", flush=True)

    summary_log = LOG_DIR / f"dispatcher-{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
    sum_fh = summary_log.open("a", encoding="utf-8")

    def _slog(event: dict):
        event["ts"] = int(time.time())
        sum_fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        sum_fh.flush()

    _slog({"event": "start", "workers": len(workers), "queue": len(pending_queue)})

    # Active: dict[worker_idx] = (proc, batch_id, started_at, log_path)
    active: dict[int, tuple] = {}
    worker_avail = list(range(len(workers)))
    completed = 0
    failed = 0

    while (pending_queue or active) and not stopped["flag"]:
        # Time budget
        if (time.time() - start) / 3600.0 >= max_hours:
            print(f"[disp] Time budget {max_hours}h reached", flush=True)
            break

        # Spawn workers while we have queue + free slots
        while pending_queue and worker_avail and not stopped["flag"]:
            w_idx = worker_avail.pop(0)
            batch = pending_queue.pop(0)
            worker = workers[w_idx]
            try:
                proc, log_path = _spawn_worker(corpus_id, batch.batch_id, worker, LOG_DIR)
                active[w_idx] = (proc, batch.batch_id, time.time(), log_path)
                _slog({
                    "event": "spawn",
                    "worker": worker[0], "provider": worker[1],
                    "batch_id": batch.batch_id, "pid": proc.pid,
                })
                print(f"[disp] SPAWN {batch.batch_id} → {worker[0]} (pid {proc.pid})", flush=True)
            except Exception as e:
                _slog({"event": "spawn-failed", "batch_id": batch.batch_id, "error": str(e)})
                worker_avail.append(w_idx)  # release slot

        if not active:
            break  # nothing running, nothing in queue

        # Poll active workers
        time.sleep(8)
        finished_idxs = []
        for w_idx, (proc, batch_id, started_at, log_path) in active.items():
            rc = proc.poll()
            if rc is not None:
                dt = time.time() - started_at
                worker = workers[w_idx]
                if rc == 0:
                    completed += 1
                    print(f"[disp] ✓ {batch_id} done by {worker[0]} ({dt/60:.1f}min)", flush=True)
                    _slog({"event": "complete", "worker": worker[0], "batch_id": batch_id,
                           "duration_min": round(dt/60, 1)})
                else:
                    failed += 1
                    print(f"[disp] ✗ {batch_id} FAILED by {worker[0]} (rc={rc}, see {log_path})", flush=True)
                    _slog({"event": "fail", "worker": worker[0], "batch_id": batch_id, "rc": rc})
                finished_idxs.append(w_idx)

        for idx in finished_idxs:
            del active[idx]
            worker_avail.append(idx)

    # Cleanup — wait remaining workers
    if active:
        print(f"[disp] Waiting for {len(active)} remaining workers…", flush=True)
        for w_idx, (proc, batch_id, started_at, _) in active.items():
            try:
                proc.wait(timeout=300)
                completed += 1 if proc.returncode == 0 else 0
            except subprocess.TimeoutExpired:
                proc.terminate()

    summary = {
        "status": "ok",
        "duration_minutes": round((time.time() - start) / 60, 1),
        "batches_completed": completed,
        "batches_failed": failed,
        "queue_remaining": len(pending_queue),
        "log": str(summary_log),
    }
    _slog({"event": "end", **summary})
    sum_fh.close()
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parallel batch dispatcher.")
    parser.add_argument("--corpus-id", type=int, required=True)
    parser.add_argument("--max-concurrent", type=int, default=5)
    parser.add_argument("--max-hours", type=float, default=8.0)
    parser.add_argument("--max-batches", type=int, default=None)
    args = parser.parse_args(argv)

    summary = run_parallel(
        corpus_id=args.corpus_id,
        max_concurrent=args.max_concurrent,
        max_hours=args.max_hours,
        max_batches=args.max_batches,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
