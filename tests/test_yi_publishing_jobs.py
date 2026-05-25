"""Tests for engine.yi_publishing.jobs (OCR job queue)."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from engine.yi_publishing.jobs import (
    ACTIVE_STATUSES,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_RUNNING,
    JobsStore,
)


@pytest.fixture
def fake_pdf(tmp_path: Path) -> Path:
    """Create a tiny placeholder PDF file (just exists, not real PDF)."""
    p = tmp_path / "data" / "raw_pdfs" / "test-book.pdf"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF-fake\n")
    return p


@pytest.fixture
def fast_ocr_runner():
    """OCR runner stub that returns instantly. Returns (runner, call_log)."""
    calls = []

    def runner(*, pdf_path, book_id, start, end, backend, language, mineru_bin, output_root):
        calls.append({"start": start, "end": end, "book_id": book_id})
        # Simulate fast OCR — sleep ~0.01s
        time.sleep(0.01)

    return runner, calls


@pytest.fixture
def slow_ocr_runner():
    """OCR runner that sleeps ~0.2s per chunk (for cancel tests)."""
    calls = []

    def runner(*, pdf_path, book_id, start, end, backend, language, mineru_bin, output_root):
        calls.append({"start": start, "end": end})
        time.sleep(0.2)

    return runner, calls


@pytest.fixture
def failing_ocr_runner():
    """OCR runner that raises on first call."""

    def runner(**kwargs):
        raise RuntimeError("Simulated MinerU crash")

    return runner


@pytest.fixture
def store(tmp_path: Path, fast_ocr_runner) -> JobsStore:
    runner, _ = fast_ocr_runner
    return JobsStore(project_root=tmp_path, ocr_chunk_size=5, ocr_runner=runner)


def _wait_for_status(store: JobsStore, job_id: str, target_statuses, timeout: float = 5.0):
    """Poll until job reaches one of target_statuses or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        job = store.get_job(job_id)
        if job and job.get("status") in target_statuses:
            return job
        time.sleep(0.02)
    raise TimeoutError(
        f"Job {job_id} did not reach {target_statuses} within {timeout}s"
    )


# ─── submit_ocr_job ───────────────────────────────────────────────────────────


def test_submit_ocr_job_creates_entry(store: JobsStore, fake_pdf: Path):
    job = store.submit_ocr_job(
        book_id="test-book", pdf_path=fake_pdf, start_page=1, end_page=10
    )
    assert job["job_id"].startswith("ocr-")
    assert job["book_id"] == "test-book"
    assert job["status"] == STATUS_PENDING
    assert job["progress"]["total"] == 10

    # Wait for thread to complete
    final = _wait_for_status(store, job["job_id"], (STATUS_DONE, STATUS_FAILED))
    assert final["status"] == STATUS_DONE


def test_submit_rejects_when_active_job_exists(store: JobsStore, fake_pdf: Path, slow_ocr_runner):
    runner, _ = slow_ocr_runner
    store._ocr_runner = runner

    j1 = store.submit_ocr_job(
        book_id="a", pdf_path=fake_pdf, start_page=1, end_page=20
    )
    # Give it a moment to start
    time.sleep(0.05)
    with pytest.raises(ValueError, match="already active"):
        store.submit_ocr_job(
            book_id="b", pdf_path=fake_pdf, start_page=1, end_page=10
        )

    # Cleanup: cancel + wait
    store.cancel_job(j1["job_id"])
    _wait_for_status(store, j1["job_id"], (STATUS_DONE, STATUS_CANCELLED, STATUS_FAILED))


def test_submit_validates_pdf_exists(store: JobsStore, tmp_path: Path):
    missing = tmp_path / "ghost.pdf"
    with pytest.raises(FileNotFoundError):
        store.submit_ocr_job(
            book_id="x", pdf_path=missing, start_page=1, end_page=5
        )


def test_submit_validates_page_range(store: JobsStore, fake_pdf: Path):
    with pytest.raises(ValueError, match="end_page"):
        store.submit_ocr_job(
            book_id="x", pdf_path=fake_pdf, start_page=10, end_page=5
        )


def test_submit_chunks_call_runner_correctly(tmp_path: Path, fake_pdf: Path, fast_ocr_runner):
    runner, calls = fast_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_chunk_size=5, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=12
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,))

    # Should be 3 chunks: 1-5, 6-10, 11-12
    assert len(calls) == 3
    assert calls[0]["start"] == 1 and calls[0]["end"] == 5
    assert calls[1]["start"] == 6 and calls[1]["end"] == 10
    assert calls[2]["start"] == 11 and calls[2]["end"] == 12


# ─── list_jobs ────────────────────────────────────────────────────────────────


def test_list_jobs_filters_active(store: JobsStore, fake_pdf: Path):
    j = store.submit_ocr_job(
        book_id="a", pdf_path=fake_pdf, start_page=1, end_page=5
    )
    _wait_for_status(store, j["job_id"], (STATUS_DONE,))

    active = store.list_jobs(active=True)
    assert len(active) == 0

    all_jobs = store.list_jobs(active=False)
    assert len(all_jobs) == 1


def test_list_jobs_filters_by_book_id(store: JobsStore, fake_pdf: Path):
    j1 = store.submit_ocr_job(
        book_id="alpha", pdf_path=fake_pdf, start_page=1, end_page=5
    )
    _wait_for_status(store, j1["job_id"], (STATUS_DONE,))
    j2 = store.submit_ocr_job(
        book_id="beta", pdf_path=fake_pdf, start_page=1, end_page=5
    )
    _wait_for_status(store, j2["job_id"], (STATUS_DONE,))

    alpha_jobs = store.list_jobs(book_id="alpha")
    assert len(alpha_jobs) == 1
    assert alpha_jobs[0]["book_id"] == "alpha"


def test_list_jobs_sorted_newest_first(store: JobsStore, fake_pdf: Path):
    ids = []
    for i in range(3):
        j = store.submit_ocr_job(
            book_id=f"b{i}", pdf_path=fake_pdf, start_page=1, end_page=3
        )
        _wait_for_status(store, j["job_id"], (STATUS_DONE,))
        ids.append(j["job_id"])
        time.sleep(0.01)  # ensure timestamp difference

    listed = store.list_jobs()
    assert [j["job_id"] for j in listed] == list(reversed(ids))


# ─── cancel_job ───────────────────────────────────────────────────────────────


def test_cancel_job_sets_status(tmp_path: Path, fake_pdf: Path, slow_ocr_runner):
    runner, _ = slow_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_chunk_size=3, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=30
    )
    time.sleep(0.1)  # let it process some chunks
    assert s.cancel_job(j["job_id"]) is True

    final = _wait_for_status(s, j["job_id"], (STATUS_CANCELLED, STATUS_DONE))
    assert final["status"] == STATUS_CANCELLED


def test_cancel_nonexistent_returns_false(store: JobsStore):
    assert store.cancel_job("ghost") is False


def test_cancel_already_done_returns_false(store: JobsStore, fake_pdf: Path):
    j = store.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=2
    )
    _wait_for_status(store, j["job_id"], (STATUS_DONE,))
    assert store.cancel_job(j["job_id"]) is False


# ─── failures ─────────────────────────────────────────────────────────────────


def test_runner_exception_marks_failed(tmp_path: Path, fake_pdf: Path, failing_ocr_runner):
    s = JobsStore(
        project_root=tmp_path, ocr_chunk_size=5, ocr_runner=failing_ocr_runner
    )
    j = s.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=10
    )
    final = _wait_for_status(s, j["job_id"], (STATUS_FAILED,))
    assert final["status"] == STATUS_FAILED
    assert "Simulated" in final["error"]


# ─── zombie detection ────────────────────────────────────────────────────────


def test_zombie_job_marked_failed(tmp_path: Path):
    """Simulate server restart: write running job to disk, then create new store
    (no thread). list_jobs should mark it failed."""
    # Pre-populate jobs.json with a "running" job
    store_dir = tmp_path / "data" / "yi_publishing"
    store_dir.mkdir(parents=True, exist_ok=True)
    jobs_path = store_dir / "jobs.json"
    jobs_path.write_text(
        json.dumps(
            {
                "version": 1,
                "jobs": [
                    {
                        "job_id": "ocr-zombie",
                        "book_id": "x",
                        "type": "ocr_mineru",
                        "status": STATUS_RUNNING,
                        "progress": {"current": 5, "total": 10, "stage": "ocr"},
                        "params": {},
                        "started_at": "2026-05-22T10:00:00",
                        "ended_at": None,
                        "eta_seconds": None,
                        "error": None,
                        "log_tail": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    s = JobsStore(project_root=tmp_path)
    jobs = s.list_jobs()
    assert len(jobs) == 1
    assert jobs[0]["status"] == STATUS_FAILED
    assert "restart" in jobs[0]["error"].lower()


# ─── has_active_ocr_job ──────────────────────────────────────────────────────


def test_has_active_ocr_job(tmp_path: Path, fake_pdf: Path, slow_ocr_runner):
    runner, _ = slow_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_chunk_size=3, ocr_runner=runner)
    assert s.has_active_ocr_job() is False
    j = s.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=10
    )
    time.sleep(0.05)
    assert s.has_active_ocr_job() is True
    s.cancel_job(j["job_id"])
    _wait_for_status(s, j["job_id"], (STATUS_DONE, STATUS_CANCELLED, STATUS_FAILED))
    assert s.has_active_ocr_job() is False


# ─── log_tail ────────────────────────────────────────────────────────────────


def test_log_tail_captures_progress(store: JobsStore, fake_pdf: Path):
    j = store.submit_ocr_job(
        book_id="x", pdf_path=fake_pdf, start_page=1, end_page=10
    )
    final = _wait_for_status(store, j["job_id"], (STATUS_DONE,))
    assert len(final["log_tail"]) > 0
    assert any("Chunk" in line for line in final["log_tail"])
