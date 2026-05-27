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

    def runner(*, pdf_path, book_id, start, end, backend, language, mineru_bin, output_root, **kwargs):
        calls.append({"start": start, "end": end, "book_id": book_id})
        # Simulate fast OCR — sleep ~0.01s
        time.sleep(0.01)

    return runner, calls


@pytest.fixture
def slow_ocr_runner():
    """OCR runner that sleeps ~0.2s per chunk (for cancel tests)."""
    calls = []

    def runner(*, pdf_path, book_id, start, end, backend, language, mineru_bin, output_root, **kwargs):
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


# ─── Swarm mode (parallel MinerU workers) ────────────────────────────────────


@pytest.fixture
def swarm_ocr_runner():
    """OCR runner that creates valid MinerU chunk output structure for merge tests."""
    calls = []
    lock = threading.Lock()

    def runner(*, pdf_path, book_id, start, end, backend, language, mineru_bin, output_root, **kwargs):
        with lock:
            calls.append({"start": start, "end": end, "output_root": str(output_root)})
        # Simulate ~0.1s per chunk so parallelism is observable
        time.sleep(0.1)
        out_dir = Path(output_root) / book_id / "auto"
        out_dir.mkdir(parents=True, exist_ok=True)
        pages = end - start + 1
        v2 = [[{"type": "text", "text": f"page {start + i}"}] for i in range(pages)]
        (out_dir / f"{book_id}_content_list_v2.json").write_text(
            json.dumps(v2, ensure_ascii=False), encoding="utf-8"
        )
        v1 = [{"page_idx": start + i} for i in range(pages)]
        (out_dir / f"{book_id}_content_list.json").write_text(
            json.dumps(v1, ensure_ascii=False), encoding="utf-8"
        )
        middle = {
            "version": "1.0",
            "pdf_info": [
                {"page_idx": start + i, "preproc_blocks": [{"lines": [{"spans": []}]}]}
                for i in range(pages)
            ],
        }
        (out_dir / f"{book_id}_middle.json").write_text(
            json.dumps(middle, ensure_ascii=False), encoding="utf-8"
        )
        (out_dir / "images").mkdir(exist_ok=True)
        (out_dir / "images" / f"p{start}_img.png").write_bytes(b"fakepng")
        # page_images (per-page renders): p0001.png, p0002.png, ...
        (out_dir / "page_images").mkdir(exist_ok=True)
        for i in range(pages):
            (out_dir / "page_images" / f"p{start + i:04d}.png").write_bytes(b"fakepage")

    return runner, calls


def test_swarm_spawns_n_workers(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    runner, calls = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="swarm-test", pdf_path=fake_pdf, start_page=1, end_page=20, workers=4
    )
    final = _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)
    assert final["status"] == STATUS_DONE
    assert final["params"]["workers"] == 4
    # 4 workers × 5 pages each
    assert len(calls) == 4
    pages_seen = sorted([(c["start"], c["end"]) for c in calls])
    assert pages_seen == [(1, 5), (6, 10), (11, 15), (16, 20)]


def test_swarm_each_worker_isolated_output(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    runner, calls = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="iso-test", pdf_path=fake_pdf, start_page=1, end_page=8, workers=2
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)
    output_roots = {c["output_root"] for c in calls}
    assert len(output_roots) == 2


def test_swarm_merges_chunks_into_canonical_folder(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    runner, _ = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="merged", pdf_path=fake_pdf, start_page=1, end_page=10, workers=3
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)

    canonical = tmp_path / "data" / "yi_publishing_mineru" / "merged" / "auto"
    v2 = canonical / "merged_content_list_v2.json"
    middle = canonical / "merged_middle.json"
    assert v2.exists()
    assert middle.exists()

    v2_data = json.loads(v2.read_text(encoding="utf-8"))
    assert len(v2_data) == 10

    middle_data = json.loads(middle.read_text(encoding="utf-8"))
    assert len(middle_data["pdf_info"]) == 10

    swarm_tmp = tmp_path / "data" / "yi_publishing_mineru" / "_swarm" / j["job_id"]
    assert not swarm_tmp.exists()


def test_swarm_merge_copies_page_images(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    """After merge, page_images/ folder must have all per-page renders.

    Regression: original merge only copied region images/, not page_images/.
    Result: page-image endpoint failed for pages > first chunk size.
    """
    runner, _ = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="pageimg", pdf_path=fake_pdf, start_page=1, end_page=12, workers=3
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)

    canonical_page_imgs = (
        tmp_path / "data" / "yi_publishing_mineru" / "pageimg" / "auto" / "page_images"
    )
    assert canonical_page_imgs.exists()
    pngs = sorted(p.name for p in canonical_page_imgs.glob("*.png"))
    # All 12 pages should be present (4 per chunk × 3 chunks)
    assert len(pngs) == 12
    assert pngs[0] == "p0001.png"
    assert pngs[-1] == "p0012.png"


def test_swarm_merge_copies_source_pdf_as_origin(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    """After merge, <book_id>_origin.pdf must be the full source PDF.

    Regression: each chunk worker produced its own _origin.pdf for chunk pages
    only; merge previously skipped this file → page-image endpoint rendered
    wrong pages or returned 404 for pages beyond first chunk's slice.
    """
    runner, _ = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="origin", pdf_path=fake_pdf, start_page=1, end_page=10, workers=2
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)

    canonical_origin = (
        tmp_path / "data" / "yi_publishing_mineru" / "origin" / "auto" / "origin_origin.pdf"
    )
    assert canonical_origin.exists()
    # Content should match the source fake_pdf
    assert canonical_origin.read_bytes() == fake_pdf.read_bytes()


def test_swarm_caps_at_max_workers(tmp_path: Path, fake_pdf: Path, swarm_ocr_runner):
    runner, _ = swarm_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="cap-test", pdf_path=fake_pdf, start_page=1, end_page=12, workers=100
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,), timeout=10)
    # MAX_WORKERS = 4 per current limit
    assert j["params"]["workers"] == 4


def test_swarm_failure_marks_whole_job_failed(tmp_path: Path, fake_pdf: Path):
    call_count = {"n": 0}
    lock = threading.Lock()

    def flaky_runner(*, pdf_path, book_id, start, end, **kwargs):
        with lock:
            call_count["n"] += 1
            n = call_count["n"]
        time.sleep(0.05)
        if n == 2:
            raise RuntimeError(f"Synthetic fail on call {n}")
        out_dir = Path(kwargs["output_root"]) / book_id / "auto"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{book_id}_content_list_v2.json").write_text("[]", encoding="utf-8")

    s = JobsStore(project_root=tmp_path, ocr_runner=flaky_runner)
    j = s.submit_ocr_job(
        book_id="flaky", pdf_path=fake_pdf, start_page=1, end_page=8, workers=3
    )
    final = _wait_for_status(s, j["job_id"], (STATUS_FAILED,), timeout=10)
    assert final["status"] == STATUS_FAILED
    assert "fail" in final["error"].lower()


def test_workers_param_clamped_to_positive(tmp_path: Path, fake_pdf: Path, fast_ocr_runner):
    runner, _ = fast_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)
    j = s.submit_ocr_job(
        book_id="z", pdf_path=fake_pdf, start_page=1, end_page=3, workers=0
    )
    _wait_for_status(s, j["job_id"], (STATUS_DONE,))
    assert j["params"]["workers"] == 1


# ─── Onboard job ──────────────────────────────────────────────────────────────


def test_submit_onboard_job_creates_entry(tmp_path: Path, monkeypatch):
    """Onboard job submission creates entry with type=onboard."""
    import engine.yi_publishing.onboarding as onb

    # Replace onboard_book with a fast stub that creates expected output
    def fake_onboard(*, book_id, pdf_path, output_dir, n_sample_pages=3, **kwargs):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return {
            "book_id": book_id,
            "page_count": 10,
            "profile": {"columns": 1, "density": "normal", "script": "chinese"},
            "ocr_config": {"workers": 2, "formula_enable": True},
            "toc": {"strategy": "fallback", "chapter_count": 1},
            "plan": {"chunks_count": 2, "estimated_ocr_hours": 0.5},
            "duration_s": 1.0,
            "output_dir": str(output_dir),
        }

    monkeypatch.setattr(onb, "onboard_book", fake_onboard)

    # Fake PDF
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-fake\n")

    s = JobsStore(project_root=tmp_path)
    job = s.submit_onboard_job(
        book_id="test", pdf_path=pdf, output_dir=tmp_path / "out", n_sample_pages=2
    )
    assert job["type"] == "onboard"
    assert job["job_id"].startswith("onboard-")
    assert job["status"] == STATUS_PENDING

    final = _wait_for_status(s, job["job_id"], (STATUS_DONE, STATUS_FAILED), timeout=5)
    assert final["status"] == STATUS_DONE
    assert final["result"]["plan"]["chunks_count"] == 2
    assert final["result"]["profile"]["columns"] == 1


def test_onboard_rejects_when_ocr_active(tmp_path: Path, fake_pdf, slow_ocr_runner):
    """Cannot start onboard when OCR job already running (single-job rule)."""
    runner, _ = slow_ocr_runner
    s = JobsStore(project_root=tmp_path, ocr_runner=runner)

    j1 = s.submit_ocr_job(
        book_id="a", pdf_path=fake_pdf, start_page=1, end_page=20
    )
    time.sleep(0.05)
    with pytest.raises(ValueError, match="already active"):
        s.submit_onboard_job(
            book_id="b", pdf_path=fake_pdf, output_dir=tmp_path / "out"
        )
    s.cancel_job(j1["job_id"])
    _wait_for_status(s, j1["job_id"], (STATUS_DONE, STATUS_CANCELLED, STATUS_FAILED))


def test_ocr_rejects_when_onboard_active(tmp_path: Path, fake_pdf, monkeypatch):
    """Cannot start OCR when onboard job running."""
    import engine.yi_publishing.onboarding as onb

    onboard_started = threading.Event()

    def slow_onboard(*, book_id, pdf_path, output_dir, **kwargs):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        onboard_started.set()
        time.sleep(0.3)
        return {
            "book_id": book_id,
            "page_count": 5,
            "profile": {"columns": 1, "density": "normal", "script": "chinese"},
            "ocr_config": {"workers": 1, "formula_enable": True},
            "toc": {"strategy": "fallback", "chapter_count": 1},
            "plan": {"chunks_count": 1, "estimated_ocr_hours": 0.1},
            "duration_s": 0.3,
            "output_dir": str(output_dir),
        }

    monkeypatch.setattr(onb, "onboard_book", slow_onboard)
    s = JobsStore(project_root=tmp_path)

    j_onb = s.submit_onboard_job(
        book_id="x", pdf_path=fake_pdf, output_dir=tmp_path / "out"
    )
    onboard_started.wait(timeout=2)
    time.sleep(0.05)  # Ensure onboard transitioned to STATUS_RUNNING

    with pytest.raises(ValueError, match="already active"):
        s.submit_ocr_job(
            book_id="y", pdf_path=fake_pdf, start_page=1, end_page=5
        )

    _wait_for_status(s, j_onb["job_id"], (STATUS_DONE, STATUS_FAILED), timeout=3)
