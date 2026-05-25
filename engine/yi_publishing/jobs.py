"""Jobs — background queue cho OCR (MinerU) và các tác vụ dài.

Single worker, single machine. Persisted to data/yi_publishing/jobs.json.

Lifecycle:
    submit_ocr_job() → status=pending
                     → spawn threading.Thread
                     → status=running (incrementally update progress)
                     → status=done | failed | cancelled

Zombie detection:
    On first list_jobs() after server restart, any job with status=running
    but no thread in RUNNING_THREADS is marked status=failed with error
    "Server restarted while job was running".
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from filelock import FileLock

logger = logging.getLogger(__name__)

DEFAULT_PROJECT_ROOT = Path(
    os.environ.get("YI_PROJECT_ROOT", "/Users/ozvietnamdesktop/Desktop/yi")
)

# Default MinerU binary path
DEFAULT_MINERU_BIN = DEFAULT_PROJECT_ROOT / ".venv-mineru" / "bin" / "mineru"

# Chunk size for OCR progress reporting
DEFAULT_OCR_CHUNK_SIZE = 10

# Status values
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
ACTIVE_STATUSES = (STATUS_PENDING, STATUS_RUNNING)


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class JobsStore:
    """In-process jobs queue with JSON persistence.

    Per-instance for tests. App uses get_default_store().
    """

    SCHEMA_VERSION = 1

    def __init__(
        self,
        project_root: Optional[Path] = None,
        *,
        mineru_bin: Optional[Path] = None,
        ocr_chunk_size: int = DEFAULT_OCR_CHUNK_SIZE,
        ocr_runner: Optional[Callable] = None,
    ):
        self.project_root = Path(project_root or DEFAULT_PROJECT_ROOT)
        self.store_dir = self.project_root / "data" / "yi_publishing"
        self.store_path = self.store_dir / "jobs.json"
        self.lock_path = self.store_dir / "jobs.json.lock"
        self.mineru_bin = Path(mineru_bin or DEFAULT_MINERU_BIN)
        self.mineru_output = self.project_root / "data" / "yi_publishing_mineru"
        self.ocr_chunk_size = ocr_chunk_size
        # Allow tests to override the actual MinerU call
        self._ocr_runner = ocr_runner or self._default_ocr_runner

        # In-memory: thread handles + cancel flags
        self._threads: dict[str, threading.Thread] = {}
        self._cancel_flags: dict[str, threading.Event] = {}
        self._zombie_checked = False

        self.store_dir.mkdir(parents=True, exist_ok=True)

    # ─── Persistence ─────────────────────────────────────────────────────────

    def _read_raw(self) -> dict:
        if not self.store_path.exists():
            return {"version": self.SCHEMA_VERSION, "jobs": []}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            backup = self.store_path.with_suffix(f".corrupt-{int(time.time())}.json")
            self.store_path.rename(backup)
            logger.error(f"jobs.json corrupt ({e}); backed up to {backup}")
            return {"version": self.SCHEMA_VERSION, "jobs": []}

    def _write_raw(self, data: dict) -> None:
        data["version"] = self.SCHEMA_VERSION
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(self.store_dir),
            prefix=".jobs-",
            suffix=".tmp",
            delete=False,
        )
        try:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
        finally:
            tmp.close()
        os.replace(tmp.name, self.store_path)

    def _lock(self) -> FileLock:
        return FileLock(str(self.lock_path), timeout=10)

    def _update_job(self, job_id: str, **fields: Any) -> Optional[dict]:
        """Atomic partial update of a job. Returns updated job or None."""
        with self._lock():
            data = self._read_raw()
            for j in data.get("jobs", []):
                if j["job_id"] == job_id:
                    j.update(fields)
                    self._write_raw(data)
                    return j
        return None

    # ─── Zombie detection ────────────────────────────────────────────────────

    def _detect_zombies(self) -> None:
        """Mark running jobs without active thread as failed (run once per process)."""
        if self._zombie_checked:
            return
        self._zombie_checked = True

        with self._lock():
            data = self._read_raw()
            changed = False
            for j in data.get("jobs", []):
                if j.get("status") == STATUS_RUNNING and j["job_id"] not in self._threads:
                    j["status"] = STATUS_FAILED
                    j["error"] = "Server restarted while job was running"
                    j["ended_at"] = _now_iso()
                    changed = True
                    logger.warning(f"Marked zombie job {j['job_id']} as failed")
            if changed:
                self._write_raw(data)

    # ─── Public API ──────────────────────────────────────────────────────────

    def submit_ocr_job(
        self,
        *,
        book_id: str,
        pdf_path: Path,
        start_page: int,
        end_page: int,
        backend: str = "pipeline",
        language: str = "ch",
    ) -> dict:
        """Submit a new OCR job. Returns the job dict (with job_id).

        Raises:
            ValueError if there's already an active OCR job (single-worker)
            FileNotFoundError if pdf_path doesn't exist
        """
        self._detect_zombies()
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if end_page < start_page:
            raise ValueError(f"end_page ({end_page}) < start_page ({start_page})")

        # Single worker check
        with self._lock():
            data = self._read_raw()
            for j in data.get("jobs", []):
                if j.get("type") == "ocr_mineru" and j.get("status") in ACTIVE_STATUSES:
                    raise ValueError(
                        f"Another OCR job is already active: {j['job_id']} "
                        f"(book_id={j.get('book_id')})"
                    )

            job_id = f"ocr-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
            job = {
                "job_id": job_id,
                "book_id": book_id,
                "type": "ocr_mineru",
                "status": STATUS_PENDING,
                "progress": {
                    "current": 0,
                    "total": end_page - start_page + 1,
                    "stage": "queued",
                },
                "params": {
                    "start_page": start_page,
                    "end_page": end_page,
                    "backend": backend,
                    "language": language,
                    "pdf_path": str(pdf_path),
                },
                "started_at": None,
                "ended_at": None,
                "eta_seconds": None,
                "error": None,
                "log_tail": [],
            }
            data.setdefault("jobs", []).append(job)
            self._write_raw(data)

        # Spawn worker thread
        self._cancel_flags[job_id] = threading.Event()
        thread = threading.Thread(
            target=self._run_ocr_job,
            args=(job_id,),
            daemon=True,
            name=f"ocr-job-{job_id}",
        )
        self._threads[job_id] = thread
        thread.start()
        logger.info(
            f"📥 Submitted OCR job {job_id} for {book_id} (pages {start_page}-{end_page})"
        )
        return job

    def get_job(self, job_id: str) -> Optional[dict]:
        self._detect_zombies()
        with self._lock():
            data = self._read_raw()
        for j in data.get("jobs", []):
            if j["job_id"] == job_id:
                return j
        return None

    def list_jobs(
        self,
        *,
        active: bool = False,
        book_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """List jobs newest-first. Filter active or by book_id."""
        self._detect_zombies()
        with self._lock():
            data = self._read_raw()
        jobs = data.get("jobs", [])
        if active:
            jobs = [j for j in jobs if j.get("status") in ACTIVE_STATUSES]
        if book_id:
            jobs = [j for j in jobs if j.get("book_id") == book_id]
        # Sort newest first by job_id (contains timestamp prefix)
        jobs = sorted(jobs, key=lambda j: j.get("job_id", ""), reverse=True)
        return jobs[:limit]

    def cancel_job(self, job_id: str) -> bool:
        """Set cancel flag. Worker thread checks between chunks.

        Returns True if job was in active state and cancel signaled.
        """
        job = self.get_job(job_id)
        if not job:
            return False
        if job.get("status") not in ACTIVE_STATUSES:
            return False

        flag = self._cancel_flags.get(job_id)
        if flag:
            flag.set()

        # If pending and no thread yet, mark cancelled immediately
        if job.get("status") == STATUS_PENDING and job_id not in self._threads:
            self._update_job(
                job_id, status=STATUS_CANCELLED, ended_at=_now_iso()
            )

        logger.info(f"🛑 Cancel signaled for job {job_id}")
        return True

    def has_active_ocr_job(self, book_id: Optional[str] = None) -> bool:
        """Check if any (or for given book) active OCR job exists."""
        jobs = self.list_jobs(active=True, book_id=book_id)
        return any(j.get("type") == "ocr_mineru" for j in jobs)

    # ─── OCR runner (thread target) ──────────────────────────────────────────

    def _should_cancel(self, job_id: str) -> bool:
        flag = self._cancel_flags.get(job_id)
        return bool(flag and flag.is_set())

    def _append_log(self, job_id: str, line: str, max_lines: int = 50) -> None:
        with self._lock():
            data = self._read_raw()
            for j in data.get("jobs", []):
                if j["job_id"] == job_id:
                    tail = deque(j.get("log_tail", []), maxlen=max_lines)
                    tail.append(line)
                    j["log_tail"] = list(tail)
                    self._write_raw(data)
                    return

    def _run_ocr_job(self, job_id: str) -> None:
        """Thread target — process OCR job in chunks."""
        try:
            job = self.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} disappeared before runner started")
                return

            params = job["params"]
            start_page = int(params["start_page"])
            end_page = int(params["end_page"])
            pdf_path = Path(params["pdf_path"])
            backend = params.get("backend", "pipeline")
            language = params.get("language", "ch")
            book_id = job["book_id"]

            total = end_page - start_page + 1
            chunk_size = self.ocr_chunk_size

            self._update_job(
                job_id,
                status=STATUS_RUNNING,
                started_at=_now_iso(),
                progress={"current": 0, "total": total, "stage": "starting"},
            )

            # Process in chunks for progress visibility
            current = 0
            chunk_start = start_page
            chunk_durations: list[float] = []

            while chunk_start <= end_page:
                if self._should_cancel(job_id):
                    self._update_job(
                        job_id,
                        status=STATUS_CANCELLED,
                        ended_at=_now_iso(),
                        progress={
                            "current": current,
                            "total": total,
                            "stage": "cancelled",
                        },
                    )
                    logger.info(f"Job {job_id} cancelled at page {chunk_start}")
                    return

                chunk_end = min(chunk_start + chunk_size - 1, end_page)
                self._append_log(
                    job_id, f"Chunk {chunk_start}-{chunk_end} starting"
                )
                t0 = time.time()

                try:
                    self._ocr_runner(
                        pdf_path=pdf_path,
                        book_id=book_id,
                        start=chunk_start,
                        end=chunk_end,
                        backend=backend,
                        language=language,
                        mineru_bin=self.mineru_bin,
                        output_root=self.mineru_output,
                    )
                except Exception as e:
                    err_msg = f"OCR chunk {chunk_start}-{chunk_end} failed: {e}"
                    logger.exception(err_msg)
                    self._append_log(job_id, err_msg)
                    self._update_job(
                        job_id,
                        status=STATUS_FAILED,
                        ended_at=_now_iso(),
                        error=str(e),
                        progress={
                            "current": current,
                            "total": total,
                            "stage": "failed",
                        },
                    )
                    return

                elapsed = time.time() - t0
                chunk_durations.append(elapsed)
                current = chunk_end - start_page + 1

                # ETA: weighted average of last 3 chunks
                recent = chunk_durations[-3:]
                avg_per_chunk = sum(recent) / len(recent)
                chunks_remaining = max(
                    0, (total - current + chunk_size - 1) // chunk_size
                )
                eta = int(avg_per_chunk * chunks_remaining)

                self._update_job(
                    job_id,
                    progress={
                        "current": current,
                        "total": total,
                        "stage": "ocr",
                    },
                    eta_seconds=eta,
                )
                self._append_log(
                    job_id,
                    f"Chunk {chunk_start}-{chunk_end} done in {elapsed:.1f}s (ETA: {eta}s)",
                )

                chunk_start = chunk_end + 1

            # Done
            self._update_job(
                job_id,
                status=STATUS_DONE,
                ended_at=_now_iso(),
                progress={"current": total, "total": total, "stage": "done"},
                eta_seconds=0,
            )
            logger.info(f"✅ Job {job_id} completed")

            # Trigger progress recompute (best effort)
            try:
                from engine.yi_publishing.books_store import BooksStore

                store = BooksStore(project_root=self.project_root)
                store.recompute_progress(book_id)
            except Exception as e:
                logger.warning(f"Progress recompute failed for {book_id}: {e}")

        finally:
            # Cleanup
            self._threads.pop(job_id, None)
            self._cancel_flags.pop(job_id, None)

    # ─── Default OCR runner (subprocess MinerU) ──────────────────────────────

    @staticmethod
    def _default_ocr_runner(
        *,
        pdf_path: Path,
        book_id: str,
        start: int,
        end: int,
        backend: str,
        language: str,
        mineru_bin: Path,
        output_root: Path,
        timeout: int = 1800,
    ) -> None:
        """Invoke MinerU CLI for a page range. Raises on non-zero exit."""
        output_root.mkdir(parents=True, exist_ok=True)
        cmd = [
            str(mineru_bin),
            "-p", str(pdf_path),
            "-o", str(output_root),
            "-b", backend,
            "-l", language,
            "-s", str(start),
            "-e", str(end),
            "-m", "auto",
        ]
        logger.info(f"  🔍 MinerU pages {start}-{end} (cmd: {' '.join(cmd[:5])}...)")
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if proc.returncode != 0:
            tail = (proc.stderr or "")[-500:]
            raise RuntimeError(
                f"MinerU exited {proc.returncode}; stderr tail: {tail}"
            )


# ─── Singleton ────────────────────────────────────────────────────────────────

_default_store: Optional[JobsStore] = None


def get_default_store() -> JobsStore:
    global _default_store
    if _default_store is None:
        _default_store = JobsStore()
    return _default_store


def reset_default_store() -> None:
    global _default_store
    _default_store = None
