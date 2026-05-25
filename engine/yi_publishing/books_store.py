"""Books store — single source of truth cho danh sách sách dịch.

Persists to `data/yi_publishing/books.json` với atomic write + file lock.

Schema (books.json):
{
  "version": 1,
  "books": [
    {
      "book_id": "tu-vi-q1",                       # slug, primary key
      "title_vi": "Tử Vi Đẩu Số — Quyển 1",
      "hanzi_title": "紫微斗数全书·卷一",
      "author": "Trần Đoàn",
      "year": null,
      "language": "zh",                            # zh | vi | han-nom
      "school": "tu-vi",                           # mai-hoa | tu-vi | luc-hao | other
      "notes": "",
      "pdf_path": "data/raw_pdfs/tu-vi-q1.pdf",
      "cover_path": "data/yi_publishing/covers/tu-vi-q1.jpg",
      "cover_custom": false,
      "page_count": 35,
      "stage": 5,                                  # 1-6 (bookflow v2.0)
      "stage_label": "Dịch thuật",
      "progress": {
        "ocr_pct": 80, "translation_pct": 42,
        "ocr_pages_done": 28, "ocr_pages_total": 35,
        "translation_lines_done": 521, "translation_lines_total": 1240
      },
      "created_at": "2026-05-19T08:30:00",
      "updated_at": "2026-05-22T17:45:00",
      "deleted": false
    }
  ]
}

Stage mapping (bookflow v2.0):
  1 = THÊM SÁCH GỐC          (mới upload, chưa OCR)
  2 = NHẬN DẠNG MỤC LỤC      (TOC + reading plan ready)
  3 = CHỌN LLM PHÙ HỢP       (routing decided)
  4 = XỬ LÝ VĂN BẢN GỐC      (OCR running hoặc done)
  5 = DỊCH THUẬT             (translation in progress)
  6 = SOẠN THÀNH SÁCH        (translation done, ready to publish PDF)
"""
from __future__ import annotations

import json
import logging
import os
import re
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from filelock import FileLock

logger = logging.getLogger(__name__)

# Defaults — overrideable via env for tests
DEFAULT_PROJECT_ROOT = Path(
    os.environ.get("YI_PROJECT_ROOT", "/Users/ozvietnamdesktop/Desktop/yi")
)


# ─── Stage derivation ──────────────────────────────────────────────────────────

STAGE_LABELS = {
    1: "Thêm sách gốc",
    2: "Nhận dạng mục lục",
    3: "Chọn LLM",
    4: "Xử lý văn bản & ảnh",
    5: "Dịch thuật",
    6: "Soạn thành sách",
}


def derive_stage(ocr_pct: float, translation_pct: float) -> int:
    """Map (ocr%, translation%) → stage 1-6."""
    if ocr_pct <= 0:
        return 1
    if ocr_pct < 100:
        return 4
    # OCR == 100
    if translation_pct <= 0:
        return 4  # OCR done, chưa dịch — vẫn ở stage 4 cho đến khi bắt đầu dịch
    if translation_pct < 100:
        return 5
    return 6


def stage_label(stage: int) -> str:
    return STAGE_LABELS.get(stage, "Không xác định")


# ─── Slug ──────────────────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Convert text → slug (a-z, 0-9, hyphen)."""
    if not text:
        return ""
    # Strip Vietnamese diacritics
    import unicodedata

    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = _SLUG_RE.sub("-", ascii_only).strip("-")
    return slug[:64]  # max 64 chars


# ─── Store class ──────────────────────────────────────────────────────────────


class BooksStore:
    """Books JSON store with file locking and atomic writes.

    Per-instance project_root override useful for tests.
    """

    SCHEMA_VERSION = 1

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or DEFAULT_PROJECT_ROOT)
        self.store_dir = self.project_root / "data" / "yi_publishing"
        self.store_path = self.store_dir / "books.json"
        self.lock_path = self.store_dir / "books.json.lock"
        self.covers_dir = self.store_dir / "covers"
        self.raw_pdfs_dir = self.project_root / "data" / "raw_pdfs"

        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.covers_dir.mkdir(parents=True, exist_ok=True)
        self.raw_pdfs_dir.mkdir(parents=True, exist_ok=True)

    # ─── Persistence ─────────────────────────────────────────────────────────

    def _read_raw(self) -> dict:
        if not self.store_path.exists():
            return {"version": self.SCHEMA_VERSION, "books": []}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            # Backup corrupt + start fresh
            backup = self.store_path.with_suffix(f".corrupt-{int(time.time())}.json")
            self.store_path.rename(backup)
            logger.error(
                f"books.json corrupt ({e}); backed up to {backup}, starting fresh"
            )
            return {"version": self.SCHEMA_VERSION, "books": []}

    def _write_raw(self, data: dict) -> None:
        """Atomic write: temp file in same dir + rename."""
        data["version"] = self.SCHEMA_VERSION
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(self.store_dir),
            prefix=".books-",
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

    # ─── Public API ──────────────────────────────────────────────────────────

    def load_books(self, include_deleted: bool = False) -> list[dict]:
        """Return list of books (filter out deleted by default)."""
        with self._lock():
            data = self._read_raw()
        books = data.get("books", [])
        if not include_deleted:
            books = [b for b in books if not b.get("deleted")]
        return books

    def get_book(self, book_id: str) -> Optional[dict]:
        """Return single book by id, or None."""
        for b in self.load_books(include_deleted=True):
            if b["book_id"] == book_id:
                return b
        return None

    def book_exists(self, book_id: str) -> bool:
        """Check active (non-deleted) book exists."""
        b = self.get_book(book_id)
        return bool(b and not b.get("deleted"))

    def add_book(
        self,
        *,
        book_id: str,
        title_vi: str,
        hanzi_title: str = "",
        author: str = "",
        year: Optional[int] = None,
        language: str = "zh",
        school: str = "",
        notes: str = "",
        pdf_path: str = "",
        cover_path: str = "",
        cover_custom: bool = False,
        page_count: int = 0,
    ) -> dict:
        """Add a new book. Raises ValueError if book_id duplicate (and not deleted)."""
        if not book_id:
            raise ValueError("book_id is required")
        if not title_vi:
            raise ValueError("title_vi is required")
        if language not in ("zh", "vi", "han-nom"):
            raise ValueError(f"language must be zh|vi|han-nom, got {language!r}")

        now = datetime.now().isoformat(timespec="seconds")
        new_book = {
            "book_id": book_id,
            "title_vi": title_vi,
            "hanzi_title": hanzi_title,
            "author": author,
            "year": year,
            "language": language,
            "school": school,
            "notes": notes,
            "pdf_path": pdf_path,
            "cover_path": cover_path,
            "cover_custom": cover_custom,
            "page_count": page_count,
            "stage": 1,
            "stage_label": stage_label(1),
            "progress": {
                "ocr_pct": 0,
                "translation_pct": 0,
                "ocr_pages_done": 0,
                "ocr_pages_total": page_count,
                "translation_lines_done": 0,
                "translation_lines_total": 0,
            },
            "created_at": now,
            "updated_at": now,
            "deleted": False,
        }

        with self._lock():
            data = self._read_raw()
            # Check for active duplicate
            for b in data.get("books", []):
                if b["book_id"] == book_id and not b.get("deleted"):
                    raise ValueError(f"book_id {book_id!r} already exists")
            data.setdefault("books", []).append(new_book)
            self._write_raw(data)

        logger.info(f"📚 Added book {book_id} ({title_vi})")
        return new_book

    def update_book(self, book_id: str, **fields: Any) -> dict:
        """Update fields of an existing book. Returns updated book."""
        # Allowed top-level mutable fields
        allowed = {
            "title_vi",
            "hanzi_title",
            "author",
            "year",
            "language",
            "school",
            "notes",
            "pdf_path",
            "cover_path",
            "cover_custom",
            "page_count",
            "stage",
            "stage_label",
            "progress",
            "deleted",
        }
        invalid = set(fields) - allowed
        if invalid:
            raise ValueError(f"Cannot update fields: {invalid}")

        with self._lock():
            data = self._read_raw()
            for b in data.get("books", []):
                if b["book_id"] == book_id:
                    b.update(fields)
                    b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                    self._write_raw(data)
                    return b
        raise KeyError(f"book_id {book_id!r} not found")

    def delete_book(self, book_id: str, soft: bool = True) -> bool:
        """Soft delete by default (sets deleted=true). Hard delete removes entry."""
        with self._lock():
            data = self._read_raw()
            books = data.get("books", [])
            for i, b in enumerate(books):
                if b["book_id"] == book_id:
                    if soft:
                        b["deleted"] = True
                        b["updated_at"] = datetime.now().isoformat(timespec="seconds")
                    else:
                        books.pop(i)
                    self._write_raw(data)
                    logger.info(
                        f"📚 {'Soft' if soft else 'Hard'} deleted book {book_id}"
                    )
                    return True
        return False

    # ─── Progress recomputation ──────────────────────────────────────────────

    def recompute_progress(self, book_id: str) -> dict:
        """Read MinerU output + translations folder, recompute progress fields.

        Returns updated book dict.
        """
        book = self.get_book(book_id)
        if not book:
            raise KeyError(f"book_id {book_id!r} not found")

        mineru_root = self.project_root / "data" / "yi_publishing_mineru" / book_id
        translations_root = (
            self.project_root / "data" / "yi_publishing" / "translations" / book_id
        )

        ocr_pages_done = 0
        ocr_pages_total = book.get("page_count", 0) or 0
        translation_lines_done = 0
        translation_lines_total = 0

        # OCR pages done: count pages in content_list_v2.json
        if mineru_root.exists():
            v2_files = list(mineru_root.rglob("*_content_list_v2.json"))
            if v2_files:
                try:
                    data = json.loads(v2_files[0].read_text(encoding="utf-8"))
                    ocr_pages_done = len(data) if isinstance(data, list) else 0
                except Exception as e:
                    logger.warning(f"Failed to read MinerU v2 for {book_id}: {e}")
            # Total lines from middle.json
            middle_files = list(mineru_root.rglob("*_middle.json"))
            if middle_files:
                try:
                    middle_data = json.loads(middle_files[0].read_text(encoding="utf-8"))
                    for page in middle_data.get("pdf_info", []):
                        for block in page.get("preproc_blocks", []) or page.get(
                            "para_blocks", []
                        ):
                            translation_lines_total += len(block.get("lines", []))
                except Exception as e:
                    logger.warning(f"Failed to read MinerU middle for {book_id}: {e}")

        # If page_count not set, use ocr_pages_done as fallback
        if ocr_pages_total == 0 and ocr_pages_done > 0:
            ocr_pages_total = ocr_pages_done

        # Translation lines done: count r{NNN}.json files with text_vi.
        #
        # Real schema (production):
        #   {"lines": {"r001-l001": {"text_vi": "...", "status": "auto", ...}}}
        # Lines is a DICT keyed by line_id; text_vi sits at top level of each line.
        #
        # Test/legacy schema also supported:
        #   {"lines": [{"line_id": "...", "translation": {"text_vi": "..."}}]}
        if translations_root.exists():
            for region_file in translations_root.rglob("r*.json"):
                try:
                    rdata = json.loads(region_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if not isinstance(rdata, dict):
                    continue
                lines = rdata.get("lines")
                if isinstance(lines, dict):
                    # Production schema: dict keyed by line_id
                    for _line_id, line_data in lines.items():
                        if isinstance(line_data, dict) and line_data.get("text_vi"):
                            translation_lines_done += 1
                elif isinstance(lines, list):
                    # Legacy/test schema: array with nested .translation.text_vi
                    for line in lines:
                        if not isinstance(line, dict):
                            continue
                        if line.get("translation", {}).get("text_vi") or line.get(
                            "text_vi"
                        ):
                            translation_lines_done += 1

        # Cap at 100% — counting heuristic can over-count when translation files
        # contain line_ids not present in MinerU middle.json (e.g., manual additions
        # or layout re-detection drift).
        ocr_pct = (
            min(100.0, round(ocr_pages_done / max(ocr_pages_total, 1) * 100, 1))
            if ocr_pages_total
            else 0
        )
        translation_pct = (
            min(
                100.0,
                round(
                    translation_lines_done / max(translation_lines_total, 1) * 100, 1
                ),
            )
            if translation_lines_total
            else 0
        )

        stage = derive_stage(ocr_pct, translation_pct)
        progress = {
            "ocr_pct": ocr_pct,
            "translation_pct": translation_pct,
            "ocr_pages_done": ocr_pages_done,
            "ocr_pages_total": ocr_pages_total,
            "translation_lines_done": translation_lines_done,
            "translation_lines_total": translation_lines_total,
        }

        return self.update_book(
            book_id,
            progress=progress,
            stage=stage,
            stage_label=stage_label(stage),
            page_count=ocr_pages_total if ocr_pages_total else book.get("page_count", 0),
        )


# ─── Singleton helper ─────────────────────────────────────────────────────────

_default_store: Optional[BooksStore] = None


def get_store() -> BooksStore:
    """Return default store (singleton)."""
    global _default_store
    if _default_store is None:
        _default_store = BooksStore()
    return _default_store


def reset_default_store() -> None:
    """Reset singleton (useful for tests)."""
    global _default_store
    _default_store = None
