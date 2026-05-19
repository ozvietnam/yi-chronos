"""Source tier manifest loader.

Reads `data/yi_lexicon/source_tiers.yaml` and exposes:
- `get_book_meta(book_id)` → tier + author + school + file path + pages
- `get_tier_for_file(filename)` → quickly resolve tier from PDF filename
- `list_books_by_tier(tier)` → all books in tier S/A/B/C
- `current_reading_week()` → next week to ingest per reading_plan
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # graceful — tier defaults to "B" if YAML unavailable


_MANIFEST_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "yi_lexicon" / "source_tiers.yaml"


@dataclass
class BookMeta:
    book_id: str
    title: str
    author: str | None
    tier: str           # 'S' | 'A' | 'B' | 'C'
    schools: list[str]
    file: str
    pages_estimate: int
    notes: str | None = None


_cached_manifest: dict | None = None


def _load_manifest() -> dict:
    global _cached_manifest
    if _cached_manifest is not None:
        return _cached_manifest
    if not yaml or not _MANIFEST_PATH.exists():
        _cached_manifest = {"books": {}, "reading_plan_2026_v1": {"weeks": []}}
        return _cached_manifest
    with _MANIFEST_PATH.open(encoding="utf-8") as f:
        _cached_manifest = yaml.safe_load(f) or {}
    return _cached_manifest


def reload_manifest() -> None:
    """Force reload from disk (for tests / hot-reload)."""
    global _cached_manifest
    _cached_manifest = None
    _load_manifest()


def get_book_meta(book_id: str) -> BookMeta | None:
    m = _load_manifest()
    books = m.get("books", {})
    data = books.get(book_id)
    if not data:
        return None
    return BookMeta(
        book_id=book_id,
        title=data.get("title", book_id),
        author=data.get("author"),
        tier=data.get("tier", "B"),
        schools=data.get("schools", ["common"]),
        file=data.get("file", ""),
        pages_estimate=data.get("pages_estimate", 0),
        notes=data.get("notes"),
    )


def get_tier_for_file(filename: str) -> str:
    """Resolve tier from PDF filename. Defaults to 'B' if not found."""
    m = _load_manifest()
    for book_id, data in m.get("books", {}).items():
        if data.get("file") == filename:
            return data.get("tier", "B")
    return "B"


def get_book_meta_for_file(filename: str) -> BookMeta | None:
    """Lookup by PDF filename."""
    m = _load_manifest()
    for book_id, data in m.get("books", {}).items():
        if data.get("file") == filename:
            return get_book_meta(book_id)
    return None


def list_books_by_tier(tier: str) -> list[BookMeta]:
    m = _load_manifest()
    out: list[BookMeta] = []
    for book_id, data in m.get("books", {}).items():
        if data.get("tier") == tier:
            out.append(get_book_meta(book_id))
    return out


def reading_plan() -> list[dict]:
    """Return ordered weeks plan."""
    m = _load_manifest()
    plan = m.get("reading_plan_2026_v1", {})
    return plan.get("weeks", [])


def current_reading_week() -> dict | None:
    """Next week with status='pending'."""
    for week in reading_plan():
        if week.get("status") == "pending":
            return week
    return None
