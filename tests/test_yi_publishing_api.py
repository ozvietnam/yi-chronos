"""Integration tests for yi-publishing API endpoints (v2.0 Library + Jobs).

Uses FastAPI TestClient with monkey-patched roots to isolate from real data.
"""
from __future__ import annotations

import io
import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def tiny_pdf_bytes() -> bytes:
    """Generate a 2-page PDF in-memory using PyMuPDF."""
    import fitz

    doc = fitz.open()
    for i in range(2):
        page = doc.new_page(width=595, height=842)  # A4
        page.insert_text((100, 100), f"Test page {i + 1}", fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


@pytest.fixture
def isolated_api(tmp_path: Path, monkeypatch, tiny_pdf_bytes: bytes):
    """Isolate API state to tmp_path. Returns (client, project_root)."""
    # Set env BEFORE importing so module-level defaults pick it up if reloaded
    monkeypatch.setenv("YI_PROJECT_ROOT", str(tmp_path))

    # Import & monkey-patch module-level paths used by endpoints
    from api import main as api_main
    from engine.yi_publishing import books_store, jobs

    # Override constants used inside endpoints
    monkeypatch.setattr(api_main, "PUBLISHING_PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(api_main, "COVERS_ROOT", tmp_path / "data" / "yi_publishing" / "covers")
    monkeypatch.setattr(api_main, "RAW_PDFS_ROOT", tmp_path / "data" / "raw_pdfs")
    monkeypatch.setattr(api_main, "UPLOAD_TEMP_ROOT", tmp_path / "tmp_uploads")
    monkeypatch.setattr(api_main, "MINERU_OUTPUT_ROOT", tmp_path / "data" / "yi_publishing_mineru")

    # Replace BooksStore and JobsStore singletons with tmp_path-rooted ones
    monkeypatch.setattr(
        books_store, "_default_store", books_store.BooksStore(project_root=tmp_path)
    )

    # Stub OCR runner so test doesn't actually call MinerU
    call_log = []

    def fake_ocr(*, pdf_path, book_id, start, end, **kwargs):
        call_log.append({"book": book_id, "start": start, "end": end})
        time.sleep(0.01)
        # Synthesize a minimal MinerU output so recompute_progress sees pages
        out_dir = tmp_path / "data" / "yi_publishing_mineru" / book_id / "auto"
        out_dir.mkdir(parents=True, exist_ok=True)
        v2_path = out_dir / f"{book_id}_content_list_v2.json"
        existing = json.loads(v2_path.read_text(encoding="utf-8")) if v2_path.exists() else []
        for _ in range(start, end + 1):
            existing.append([{"type": "text", "text": "x"}])
        v2_path.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")

    test_jobs_store = jobs.JobsStore(
        project_root=tmp_path, ocr_chunk_size=5, ocr_runner=fake_ocr
    )
    monkeypatch.setattr(jobs, "_default_store", test_jobs_store)

    # ALSO patch the literal absolute paths used inside endpoint bodies
    # by replacing the COVERS_ROOT-related logic — since endpoints reference
    # `Path("/Users/ozvietnamdesktop/Desktop/yi")` directly, we cannot monkey-patch
    # that literal. Instead, we point pdf_path absolutely in finalize+OCR flows.

    client = TestClient(api_main.app)

    # Attach helpers
    client.tiny_pdf = tiny_pdf_bytes
    client.project_root = tmp_path
    client.call_log = call_log
    client.books_store = books_store._default_store
    client.jobs_store = test_jobs_store
    return client


def _wait_for_job(client: TestClient, job_id: str, *, target=("done", "failed", "cancelled"), timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"/api/yi-publishing/jobs/{job_id}")
        if r.status_code == 200 and r.json()["job"]["status"] in target:
            return r.json()["job"]
        time.sleep(0.05)
    raise TimeoutError(f"Job {job_id} did not reach {target} in {timeout}s")


# ─── Upload + finalize ───────────────────────────────────────────────────────


def test_upload_pdf_returns_temp_id(isolated_api: TestClient):
    files = {"file": ("test.pdf", isolated_api.tiny_pdf, "application/pdf")}
    r = isolated_api.post("/api/yi-publishing/books/upload", files=files)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "ok"
    assert "temp_id" in data
    assert data["suggested_metadata"]["page_count"] == 2
    assert data["suggested_metadata"]["book_id"] == "test"


def test_upload_rejects_non_pdf(isolated_api: TestClient):
    files = {"file": ("test.txt", b"not a pdf", "text/plain")}
    r = isolated_api.post("/api/yi-publishing/books/upload", files=files)
    assert r.status_code == 400


def test_upload_cover_served_after_upload(isolated_api: TestClient):
    files = {"file": ("c.pdf", isolated_api.tiny_pdf, "application/pdf")}
    up = isolated_api.post("/api/yi-publishing/books/upload", files=files).json()
    r = isolated_api.get(f"/api/yi-publishing/uploads/{up['temp_id']}/cover")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")


def test_finalize_creates_book_entry(isolated_api: TestClient):
    files = {"file": ("hello.pdf", isolated_api.tiny_pdf, "application/pdf")}
    up = isolated_api.post("/api/yi-publishing/books/upload", files=files).json()

    payload = {
        "temp_id": up["temp_id"],
        "book_id": "my-book",
        "title_vi": "Sách Của Tôi",
        "language": "zh",
    }
    r = isolated_api.post("/api/yi-publishing/books/finalize", json=payload)
    assert r.status_code == 200, r.text
    book = r.json()["book"]
    assert book["book_id"] == "my-book"
    assert book["page_count"] == 2

    # Verify books.json + raw_pdf exist
    assert isolated_api.books_store.get_book("my-book") is not None
    assert (isolated_api.project_root / "data" / "raw_pdfs" / "my-book.pdf").exists()


def test_finalize_rejects_duplicate_book_id(isolated_api: TestClient):
    # Upload twice and finalize both with same book_id
    files1 = {"file": ("a.pdf", isolated_api.tiny_pdf, "application/pdf")}
    up1 = isolated_api.post("/api/yi-publishing/books/upload", files=files1).json()
    files2 = {"file": ("b.pdf", isolated_api.tiny_pdf, "application/pdf")}
    up2 = isolated_api.post("/api/yi-publishing/books/upload", files=files2).json()

    payload = {"temp_id": up1["temp_id"], "book_id": "dup", "title_vi": "A", "language": "zh"}
    r1 = isolated_api.post("/api/yi-publishing/books/finalize", json=payload)
    assert r1.status_code == 200

    payload2 = {"temp_id": up2["temp_id"], "book_id": "dup", "title_vi": "B", "language": "zh"}
    r2 = isolated_api.post("/api/yi-publishing/books/finalize", json=payload2)
    assert r2.status_code == 409


def test_finalize_missing_temp_id_returns_404(isolated_api: TestClient):
    payload = {"temp_id": "nonexistent", "book_id": "x", "title_vi": "X", "language": "zh"}
    r = isolated_api.post("/api/yi-publishing/books/finalize", json=payload)
    assert r.status_code == 404


# ─── GET /books (enhanced) ───────────────────────────────────────────────────


def _create_book(client: TestClient, book_id: str, title: str = "T"):
    """Helper: upload+finalize a book, return book dict."""
    files = {"file": (f"{book_id}.pdf", client.tiny_pdf, "application/pdf")}
    up = client.post("/api/yi-publishing/books/upload", files=files).json()
    r = client.post(
        "/api/yi-publishing/books/finalize",
        json={"temp_id": up["temp_id"], "book_id": book_id, "title_vi": title, "language": "zh"},
    )
    assert r.status_code == 200, r.text
    return r.json()["book"]


def test_list_books_returns_progress_fields(isolated_api: TestClient):
    _create_book(isolated_api, "alpha", "Alpha Book")
    r = isolated_api.get("/api/yi-publishing/books")
    assert r.status_code == 200
    books = r.json()["books"]
    alpha = next((b for b in books if b["book_id"] == "alpha"), None)
    assert alpha is not None
    assert alpha["title_vi"] == "Alpha Book"
    assert "progress" in alpha
    assert "stage" in alpha
    assert "cover_url" in alpha
    assert alpha["active_job_id"] is None


# ─── Cover GET/PUT ───────────────────────────────────────────────────────────


def test_cover_get_after_finalize(isolated_api: TestClient):
    _create_book(isolated_api, "covertest")
    r = isolated_api.get("/api/yi-publishing/books/covertest/cover")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")


def test_cover_404_for_nonexistent_book(isolated_api: TestClient):
    r = isolated_api.get("/api/yi-publishing/books/ghost/cover")
    assert r.status_code == 404


def test_put_custom_cover_overrides(isolated_api: TestClient):
    _create_book(isolated_api, "ctest")
    # Make a tiny PNG
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (100, 130), color="red").save(buf, format="PNG")
    files = {"file": ("custom.png", buf.getvalue(), "image/png")}
    r = isolated_api.put("/api/yi-publishing/books/ctest/cover", files=files)
    assert r.status_code == 200, r.text
    book = r.json()["book"]
    assert book["cover_custom"] is True


# ─── PATCH metadata ──────────────────────────────────────────────────────────


def test_patch_book_metadata(isolated_api: TestClient):
    _create_book(isolated_api, "ptest", "Old Title")
    r = isolated_api.patch(
        "/api/yi-publishing/books/ptest",
        json={"title_vi": "New Title", "author": "Anh CEO"},
    )
    assert r.status_code == 200
    book = r.json()["book"]
    assert book["title_vi"] == "New Title"
    assert book["author"] == "Anh CEO"


def test_patch_book_404_for_missing(isolated_api: TestClient):
    r = isolated_api.patch(
        "/api/yi-publishing/books/ghost", json={"title_vi": "X"}
    )
    assert r.status_code == 404


def test_patch_book_400_for_empty_update(isolated_api: TestClient):
    _create_book(isolated_api, "etest")
    r = isolated_api.patch("/api/yi-publishing/books/etest", json={})
    assert r.status_code == 400


# ─── DELETE ──────────────────────────────────────────────────────────────────


def test_delete_book_soft(isolated_api: TestClient):
    _create_book(isolated_api, "dtest")
    r = isolated_api.delete("/api/yi-publishing/books/dtest")
    assert r.status_code == 200
    # No longer in active list
    listed = isolated_api.get("/api/yi-publishing/books").json()["books"]
    assert all(b["book_id"] != "dtest" for b in listed)


def test_delete_missing_returns_404(isolated_api: TestClient):
    r = isolated_api.delete("/api/yi-publishing/books/ghost")
    assert r.status_code == 404


# ─── Jobs ────────────────────────────────────────────────────────────────────


def test_submit_ocr_job_creates_and_completes(isolated_api: TestClient):
    _create_book(isolated_api, "ocrbook")
    r = isolated_api.post(
        "/api/yi-publishing/books/ocrbook/jobs/ocr",
        json={"start_page": 1, "end_page": 2},
    )
    assert r.status_code == 200, r.text
    job_id = r.json()["job"]["job_id"]
    final = _wait_for_job(isolated_api, job_id, target=("done",))
    assert final["status"] == "done"
    assert len(isolated_api.call_log) >= 1


def test_submit_ocr_404_for_missing_book(isolated_api: TestClient):
    r = isolated_api.post(
        "/api/yi-publishing/books/ghost/jobs/ocr",
        json={"start_page": 1, "end_page": 5},
    )
    assert r.status_code == 404


def test_list_jobs_endpoint(isolated_api: TestClient):
    _create_book(isolated_api, "lbook")
    j = isolated_api.post(
        "/api/yi-publishing/books/lbook/jobs/ocr",
        json={"start_page": 1, "end_page": 2},
    ).json()["job"]
    _wait_for_job(isolated_api, j["job_id"])

    r = isolated_api.get("/api/yi-publishing/jobs")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    assert any(jj["job_id"] == j["job_id"] for jj in jobs)


def test_get_job_endpoint(isolated_api: TestClient):
    _create_book(isolated_api, "gbook")
    j = isolated_api.post(
        "/api/yi-publishing/books/gbook/jobs/ocr",
        json={"start_page": 1, "end_page": 2},
    ).json()["job"]
    _wait_for_job(isolated_api, j["job_id"])

    r = isolated_api.get(f"/api/yi-publishing/jobs/{j['job_id']}")
    assert r.status_code == 200
    assert r.json()["job"]["job_id"] == j["job_id"]


def test_get_job_404(isolated_api: TestClient):
    r = isolated_api.get("/api/yi-publishing/jobs/ghost-id")
    assert r.status_code == 404


def test_cancel_job_endpoint(isolated_api: TestClient):
    """Submit a job with slow runner to test cancel mid-flight."""
    from engine.yi_publishing import jobs as jobs_mod

    # Replace runner with slow one
    def slow(*, pdf_path, book_id, start, end, **kwargs):
        time.sleep(0.3)

    jobs_mod._default_store._ocr_runner = slow
    _create_book(isolated_api, "cbook")
    j = isolated_api.post(
        "/api/yi-publishing/books/cbook/jobs/ocr",
        json={"start_page": 1, "end_page": 20},
    ).json()["job"]
    time.sleep(0.05)

    r = isolated_api.delete(f"/api/yi-publishing/jobs/{j['job_id']}")
    assert r.status_code == 200

    final = _wait_for_job(
        isolated_api, j["job_id"], target=("cancelled", "done"), timeout=5
    )
    assert final["status"] == "cancelled"
