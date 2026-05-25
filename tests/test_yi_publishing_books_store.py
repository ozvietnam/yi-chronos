"""Tests for engine.yi_publishing.books_store.

Uses tmp_path fixture to isolate each test from real data.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from engine.yi_publishing.books_store import (
    BooksStore,
    derive_stage,
    slugify,
    stage_label,
)


@pytest.fixture
def store(tmp_path: Path) -> BooksStore:
    """Fresh BooksStore rooted in tmp_path."""
    return BooksStore(project_root=tmp_path)


# ─── slugify ──────────────────────────────────────────────────────────────────


def test_slugify_basic():
    assert slugify("Tử Vi Đẩu Số") == "tu-vi-au-so"


def test_slugify_removes_special_chars():
    assert slugify("Q1 — Phú Thái Vi") == "q1-phu-thai-vi"


def test_slugify_max_length():
    long = "a" * 100
    assert len(slugify(long)) == 64


def test_slugify_empty():
    assert slugify("") == ""


# ─── derive_stage ─────────────────────────────────────────────────────────────


def test_derive_stage_uploaded():
    assert derive_stage(0, 0) == 1


def test_derive_stage_ocr_running():
    assert derive_stage(45, 0) == 4


def test_derive_stage_ocr_done_no_translation():
    assert derive_stage(100, 0) == 4


def test_derive_stage_translating():
    assert derive_stage(100, 50) == 5


def test_derive_stage_ready_publish():
    assert derive_stage(100, 100) == 6


def test_stage_label_known():
    assert stage_label(1) == "Thêm sách gốc"
    assert stage_label(5) == "Dịch thuật"


def test_stage_label_unknown():
    assert stage_label(99) == "Không xác định"


# ─── add_book ─────────────────────────────────────────────────────────────────


def test_add_book_persists_to_json(store: BooksStore):
    book = store.add_book(book_id="test-q1", title_vi="Sách Test", language="zh")
    assert book["book_id"] == "test-q1"
    assert book["stage"] == 1
    assert book["progress"]["ocr_pct"] == 0
    assert store.store_path.exists()

    raw = json.loads(store.store_path.read_text(encoding="utf-8"))
    assert raw["version"] == 1
    assert len(raw["books"]) == 1
    assert raw["books"][0]["book_id"] == "test-q1"


def test_add_book_rejects_duplicate_book_id(store: BooksStore):
    store.add_book(book_id="dup", title_vi="A", language="zh")
    with pytest.raises(ValueError, match="already exists"):
        store.add_book(book_id="dup", title_vi="B", language="zh")


def test_add_book_allows_reuse_after_soft_delete(store: BooksStore):
    store.add_book(book_id="reusable", title_vi="A", language="zh")
    store.delete_book("reusable", soft=True)
    # Should be allowed since soft-deleted books are filtered
    book = store.add_book(book_id="reusable", title_vi="B", language="zh")
    assert book["title_vi"] == "B"


def test_add_book_requires_title(store: BooksStore):
    with pytest.raises(ValueError, match="title_vi"):
        store.add_book(book_id="x", title_vi="", language="zh")


def test_add_book_validates_language(store: BooksStore):
    with pytest.raises(ValueError, match="language"):
        store.add_book(book_id="x", title_vi="T", language="es")


def test_add_book_requires_book_id(store: BooksStore):
    with pytest.raises(ValueError, match="book_id"):
        store.add_book(book_id="", title_vi="T", language="zh")


# ─── get_book / load_books ────────────────────────────────────────────────────


def test_get_book_returns_none_for_missing(store: BooksStore):
    assert store.get_book("nonexistent") is None


def test_load_books_filters_deleted_by_default(store: BooksStore):
    store.add_book(book_id="a", title_vi="A", language="zh")
    store.add_book(book_id="b", title_vi="B", language="zh")
    store.delete_book("a", soft=True)

    active = store.load_books()
    assert len(active) == 1
    assert active[0]["book_id"] == "b"

    all_books = store.load_books(include_deleted=True)
    assert len(all_books) == 2


def test_book_exists_excludes_deleted(store: BooksStore):
    store.add_book(book_id="a", title_vi="A", language="zh")
    assert store.book_exists("a") is True
    store.delete_book("a", soft=True)
    assert store.book_exists("a") is False


# ─── update_book ──────────────────────────────────────────────────────────────


def test_update_book_only_changes_specified_fields(store: BooksStore):
    store.add_book(book_id="x", title_vi="Old", author="A1", language="zh")
    updated = store.update_book("x", title_vi="New")
    assert updated["title_vi"] == "New"
    assert updated["author"] == "A1"  # unchanged
    assert updated["updated_at"] >= updated["created_at"]


def test_update_book_rejects_unknown_fields(store: BooksStore):
    store.add_book(book_id="x", title_vi="A", language="zh")
    with pytest.raises(ValueError, match="Cannot update"):
        store.update_book("x", weird_field="oops")


def test_update_book_missing_raises_keyerror(store: BooksStore):
    with pytest.raises(KeyError):
        store.update_book("ghost", title_vi="X")


# ─── delete_book ──────────────────────────────────────────────────────────────


def test_delete_book_soft_sets_flag(store: BooksStore):
    store.add_book(book_id="x", title_vi="A", language="zh")
    assert store.delete_book("x", soft=True) is True
    b = store.get_book("x")
    assert b is not None
    assert b["deleted"] is True


def test_delete_book_hard_removes_entry(store: BooksStore):
    store.add_book(book_id="x", title_vi="A", language="zh")
    assert store.delete_book("x", soft=False) is True
    assert store.get_book("x") is None


def test_delete_book_returns_false_for_missing(store: BooksStore):
    assert store.delete_book("ghost") is False


# ─── concurrency ──────────────────────────────────────────────────────────────


def test_concurrent_writes_use_lock(store: BooksStore):
    """Spawn 10 threads each adding 1 book; all should succeed without corruption."""
    errors = []

    def worker(i: int):
        try:
            store.add_book(book_id=f"book-{i}", title_vi=f"T{i}", language="zh")
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Concurrency errors: {errors}"
    assert len(store.load_books()) == 10


# ─── corrupt JSON recovery ────────────────────────────────────────────────────


def test_corrupt_json_backed_up_and_recovered(store: BooksStore):
    # Write garbage
    store.store_path.write_text("{not json", encoding="utf-8")
    # Reading should not raise — should backup + return empty
    books = store.load_books()
    assert books == []
    # Backup file exists
    backups = list(store.store_dir.glob("books.corrupt-*.json"))
    assert len(backups) == 1


# ─── recompute_progress ──────────────────────────────────────────────────────


def _setup_mineru_output(project_root: Path, book_id: str, *, pages: int, lines_per_page: int):
    """Synthesize MinerU output structure for testing recompute_progress."""
    book_dir = project_root / "data" / "yi_publishing_mineru" / book_id / "auto"
    book_dir.mkdir(parents=True, exist_ok=True)

    # content_list_v2.json — array, each entry = 1 page
    v2 = [[{"type": "text", "text": "x"}] for _ in range(pages)]
    (book_dir / f"{book_id}_content_list_v2.json").write_text(
        json.dumps(v2, ensure_ascii=False), encoding="utf-8"
    )

    # middle.json — has pdf_info with blocks/lines (for total lines count)
    middle = {
        "pdf_info": [
            {
                "preproc_blocks": [
                    {"lines": [{"spans": []} for _ in range(lines_per_page)]}
                ]
            }
            for _ in range(pages)
        ]
    }
    (book_dir / f"{book_id}_middle.json").write_text(
        json.dumps(middle, ensure_ascii=False), encoding="utf-8"
    )


def _setup_translations(
    project_root: Path, book_id: str, *, lines_done: int, schema: str = "production"
):
    """Synthesize translation region files with N completed lines.

    Two schemas supported:
      - "production" (real): {"lines": {"r1-l001": {"text_vi": "...", "status": ...}}}
      - "legacy" (older spec): {"lines": [{"line_id": ..., "translation": {"text_vi": ...}}]}
    """
    trans_dir = (
        project_root / "data" / "yi_publishing" / "translations" / book_id / "p0001"
    )
    trans_dir.mkdir(parents=True, exist_ok=True)

    if schema == "production":
        region_data = {
            "lines": {
                f"r1-l{i:03d}": {
                    "text_vi": "đã dịch",
                    "status": "auto",
                    "translator": "test",
                    "version": 1,
                }
                for i in range(lines_done)
            }
        }
    elif schema == "legacy":
        region_data = {
            "lines": [
                {"line_id": f"r1-l{i:03d}", "translation": {"text_vi": "đã dịch"}}
                for i in range(lines_done)
            ]
        }
    else:
        raise ValueError(f"Unknown schema: {schema}")

    (trans_dir / "r001.json").write_text(
        json.dumps(region_data, ensure_ascii=False), encoding="utf-8"
    )


def test_recompute_progress_empty_book(store: BooksStore):
    store.add_book(book_id="empty", title_vi="E", language="zh", page_count=100)
    book = store.recompute_progress("empty")
    assert book["progress"]["ocr_pct"] == 0
    assert book["progress"]["translation_pct"] == 0
    assert book["stage"] == 1


def test_recompute_progress_partial_ocr(store: BooksStore):
    store.add_book(book_id="partial", title_vi="P", language="zh", page_count=10)
    _setup_mineru_output(store.project_root, "partial", pages=5, lines_per_page=4)

    book = store.recompute_progress("partial")
    assert book["progress"]["ocr_pages_done"] == 5
    assert book["progress"]["ocr_pages_total"] == 10
    assert book["progress"]["ocr_pct"] == 50.0
    assert book["progress"]["translation_lines_total"] == 20
    assert book["progress"]["translation_pct"] == 0
    assert book["stage"] == 4  # ocr in progress


def test_recompute_progress_ocr_done_translating(store: BooksStore):
    store.add_book(book_id="trans", title_vi="T", language="zh", page_count=5)
    _setup_mineru_output(store.project_root, "trans", pages=5, lines_per_page=4)
    _setup_translations(store.project_root, "trans", lines_done=10)

    book = store.recompute_progress("trans")
    assert book["progress"]["ocr_pct"] == 100.0
    assert book["progress"]["translation_lines_done"] == 10
    assert book["progress"]["translation_lines_total"] == 20
    assert book["progress"]["translation_pct"] == 50.0
    assert book["stage"] == 5


def test_recompute_progress_full_done(store: BooksStore):
    store.add_book(book_id="full", title_vi="F", language="zh", page_count=2)
    _setup_mineru_output(store.project_root, "full", pages=2, lines_per_page=3)
    _setup_translations(store.project_root, "full", lines_done=6)

    book = store.recompute_progress("full")
    assert book["progress"]["ocr_pct"] == 100.0
    assert book["progress"]["translation_pct"] == 100.0
    assert book["stage"] == 6


def test_recompute_progress_legacy_schema(store: BooksStore):
    """Older translation files use array+nested translation.text_vi schema."""
    store.add_book(book_id="legacy", title_vi="L", language="zh", page_count=2)
    _setup_mineru_output(store.project_root, "legacy", pages=2, lines_per_page=3)
    _setup_translations(
        store.project_root, "legacy", lines_done=4, schema="legacy"
    )

    book = store.recompute_progress("legacy")
    assert book["progress"]["translation_lines_done"] == 4
    assert book["progress"]["translation_lines_total"] == 6


def test_recompute_progress_production_schema_with_status(store: BooksStore):
    """Production schema: lines is dict {line_id: {text_vi, status, ...}}.

    Counts entries with non-empty text_vi.
    """
    store.add_book(book_id="prod", title_vi="P", language="zh", page_count=1)
    _setup_mineru_output(store.project_root, "prod", pages=1, lines_per_page=5)

    trans_dir = (
        store.project_root / "data" / "yi_publishing" / "translations" / "prod" / "p0001"
    )
    trans_dir.mkdir(parents=True, exist_ok=True)
    # Mix: 3 done, 2 empty
    region_data = {
        "lines": {
            "r1-l001": {"text_vi": "Khang Tiết...", "status": "auto"},
            "r1-l002": {"text_vi": "thuyết Dịch", "status": "approved"},
            "r1-l003": {"text_vi": "", "status": "pending"},
            "r1-l004": {"status": "pending"},  # no text_vi field at all
            "r1-l005": {"text_vi": "third line", "status": "draft"},
        }
    }
    (trans_dir / "r001.json").write_text(
        json.dumps(region_data, ensure_ascii=False), encoding="utf-8"
    )

    book = store.recompute_progress("prod")
    assert book["progress"]["translation_lines_done"] == 3
    assert book["progress"]["translation_lines_total"] == 5
    assert book["progress"]["translation_pct"] == 60.0


def test_recompute_progress_missing_book_raises(store: BooksStore):
    with pytest.raises(KeyError):
        store.recompute_progress("ghost")
