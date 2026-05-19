"""Manifest schema for a restored book.

Each restored book lives at `data/yi_restored/<book_slug>/`:
    manifest.json         -- this file: structure + provenance
    content.md            -- full markdown, wikilinks intact
    pages/                -- one file per page: page-0001.md
    figures/              -- 001.png (extracted), 001.svg (redrawn — phase B)
    raw_ocr/              -- raw tesseract output (debugging)
    original.pdf          -- symlink to thư viện sách/

Manifest tracks:
- Section hierarchy (Chương 1 / Tiết 2 / ...)
- Page → section mapping (for jump navigation)
- Figure list with placeholders
- WikiLinks extracted (which concepts appear, with page anchors)
- Restoration provenance (OCR backend, LLM model, dates)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class BookFigure:
    """An image/diagram extracted or DETECTED on a page.

    Two ways figures get registered:
    1. **extracted**: PyMuPDF found an embedded image → image_path = real PNG path
       (rare for scanned PDFs — most are 1 big raster per page)
    2. **detected_in_scan**: Qwen-VL OCR saw a figure and emitted
       `[[FIGURE:type|desc]]` placeholder → image_path = None, redraw_status='needs_redraw'.
       Anh sau review danh sách → vẽ lại bằng SVG hoặc vision-LLM redraw (phase B).
    """
    figure_id: str                # "fig-0042-1" = page 42, fig 1
    page: int
    image_path: str | None = None # None nếu chỉ là placeholder cần redraw
    caption: str = ""             # for extracted figures
    description: str = ""         # for detected_in_scan: detailed redraw hint
    figure_type: str = "image"    # 'ha_do' | 'lac_thu' | 'bat_quai_*' | 'bang' | ...
    source: str = "extracted"     # 'extracted' | 'detected_in_scan'
    redraw_status: str = "none"   # 'none' | 'needs_redraw' | 'in_progress' | 'done' | 'skip'
    redrawn_svg: str | None = None  # phase B: vector version
    placeholder: str | None = None  # original `[[FIGURE:...]]` text for in-page replace
    classified_as: str | None = None  # cross-ref to Lexicon concept if any


@dataclass
class BookSection:
    """A section in the book (Chương, Tiết, Bài, ...)."""
    section_id: str               # "ch-01" / "ch-01-sec-02"
    title: str
    level: int                    # 1 = top, 2 = sub, 3 = sub-sub
    start_page: int
    end_page: int | None = None
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)


@dataclass
class BookPage:
    """One page of restored content."""
    page: int
    section_id: str | None = None
    md_path: str | None = None    # relative path to pages/page-NNNN.md
    word_count: int = 0
    figure_ids: list[str] = field(default_factory=list)
    wikilinks: list[str] = field(default_factory=list)  # ["Càn", "Khôn", ...]
    ocr_confidence: float = 0.0   # 0-1, from OCR backend if available
    needs_review: bool = False    # flagged if confidence low or LLM warned
    # v2 metadata (2026-05-12 — anh đề xuất hashtag/search/wiki support)
    summary_short: str = ""                       # 1-2 câu TLDR (skim 938 trang nhanh)
    hashtags: list[str] = field(default_factory=list)        # search filter
    persons: list[str] = field(default_factory=list)         # NER người
    que_mentions: list[str] = field(default_factory=list)    # tên quẻ trong trang


def sections_for_reader(sections: list[BookSection]) -> list[BookSection]:
    """Return sections in page order for the reader TOC."""
    return sorted(
        sections,
        key=lambda s: (
            s.start_page or 0,
            s.level or 9,
            s.section_id,
        ),
    )


@dataclass
class WikiLinkIndex:
    """For each concept name → list of (page, section_id) where it appears."""
    concept_vi: str
    occurrences: list[dict] = field(default_factory=list)
    # occurrences = [{"page": 42, "section_id": "ch-01"}, ...]


@dataclass
class HashtagIndex:
    """Reverse lookup: hashtag → list of pages."""
    tag: str                     # "#âm-dương"
    pages: list[int] = field(default_factory=list)
    count: int = 0               # convenience: len(pages)


@dataclass
class PersonIndex:
    """NER index: person → pages mentioning them."""
    name: str                    # "Chu Hy"
    pages: list[int] = field(default_factory=list)
    count: int = 0


@dataclass
class BookManifest:
    """Top-level manifest for a restored book."""
    book_slug: str                # filesystem-safe slug
    book_name: str                # human-readable title
    corpus_id: int | None = None
    author: str | None = None
    tier: str = "B"
    copyright_status: str = "internal_only"
    schools: list[str] = field(default_factory=list)
    original_pdf: str | None = None
    pages_total: int = 0
    pages_restored: int = 0
    sections: list[BookSection] = field(default_factory=list)
    pages: list[BookPage] = field(default_factory=list)
    figures: list[BookFigure] = field(default_factory=list)
    wikilink_index: list[WikiLinkIndex] = field(default_factory=list)
    # v2 reverse indexes (2026-05-12)
    hashtag_index: list[HashtagIndex] = field(default_factory=list)
    person_index: list[PersonIndex] = field(default_factory=list)
    # Provenance
    ocr_backend: str = "tesseract"
    ocr_lang: str = "vie"
    llm_model: str = "deepseek-v4-flash"
    pipeline_version: str = "phase-a/2026-05-12"
    started_at: int = 0
    finished_at: int | None = None
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def save_manifest(manifest: BookManifest, path: str | Path) -> Path:
    """Persist manifest with file-lock + merge.

    PARALLEL SAFETY: multiple processes có thể save đồng thời. Em dùng fcntl
    LOCK_EX để serialize, và RE-READ disk trước khi write để merge pages/figures
    từ các process khác (chống mất data).
    """
    import fcntl
    import os
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lock_path = p.with_suffix(p.suffix + ".lock")
    # Acquire exclusive lock
    with lock_path.open("w") as lock_f:
        fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        try:
            # Re-read latest disk state if exists, merge in our additions
            if p.exists():
                try:
                    disk = load_manifest(p)
                    manifest = _merge_manifests(disk, manifest)
                except Exception:
                    pass  # corrupt disk — use our state
            # Atomic write via temp + rename
            tmp = p.with_suffix(p.suffix + ".tmp")
            tmp.write_text(
                json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, p)
        finally:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_UN)
    return p


def _merge_manifests(disk: BookManifest, mine: BookManifest) -> BookManifest:
    """Merge two manifests — used when parallel processes update concurrently.

    Strategy: pages dedup by page number, figures by figure_id, indexes union.
    Provenance fields (started_at, etc.) keep earliest non-zero.
    """
    # Pages: dedupe by page number (last writer wins for that page)
    pages_by_no: dict[int, BookPage] = {p.page: p for p in disk.pages}
    for p in mine.pages:
        pages_by_no[p.page] = p

    # Figures: dedupe by figure_id
    figs_by_id: dict[str, BookFigure] = {f.figure_id: f for f in disk.figures}
    for f in mine.figures:
        figs_by_id[f.figure_id] = f

    # Sections: dedupe by section_id, prefer mine if same
    secs_by_id: dict[str, BookSection] = {s.section_id: s for s in disk.sections}
    for s in mine.sections:
        secs_by_id[s.section_id] = s

    # WikiLink index — merge occurrences
    wl_by_concept: dict[str, WikiLinkIndex] = {w.concept_vi: w for w in disk.wikilink_index}
    for w in mine.wikilink_index:
        if w.concept_vi in wl_by_concept:
            existing = wl_by_concept[w.concept_vi]
            seen = {(o.get("page"), o.get("section_id")) for o in existing.occurrences}
            for o in w.occurrences:
                if (o.get("page"), o.get("section_id")) not in seen:
                    existing.occurrences.append(o)
        else:
            wl_by_concept[w.concept_vi] = w

    # Hashtag + Person — merge pages list
    ht_by_tag: dict[str, HashtagIndex] = {h.tag: h for h in disk.hashtag_index}
    for h in mine.hashtag_index:
        if h.tag in ht_by_tag:
            existing = ht_by_tag[h.tag]
            for pg in h.pages:
                if pg not in existing.pages:
                    existing.pages.append(pg)
            existing.count = len(existing.pages)
        else:
            ht_by_tag[h.tag] = h

    pe_by_name: dict[str, PersonIndex] = {p.name: p for p in disk.person_index}
    for p in mine.person_index:
        if p.name in pe_by_name:
            existing = pe_by_name[p.name]
            for pg in p.pages:
                if pg not in existing.pages:
                    existing.pages.append(pg)
            existing.count = len(existing.pages)
        else:
            pe_by_name[p.name] = p

    # Construct merged
    out = BookManifest(
        book_slug=mine.book_slug or disk.book_slug,
        book_name=mine.book_name or disk.book_name,
        corpus_id=mine.corpus_id or disk.corpus_id,
        author=mine.author or disk.author,
        tier=mine.tier or disk.tier,
        copyright_status=mine.copyright_status or disk.copyright_status,
        schools=mine.schools or disk.schools,
        original_pdf=mine.original_pdf or disk.original_pdf,
        pages_total=max(mine.pages_total, disk.pages_total),
        pages_restored=max(
            len(pages_by_no),
            disk.pages_restored,
            mine.pages_restored,
        ),
        sections=list(secs_by_id.values()),
        pages=sorted(pages_by_no.values(), key=lambda p: p.page),
        figures=list(figs_by_id.values()),
        wikilink_index=list(wl_by_concept.values()),
        hashtag_index=list(ht_by_tag.values()),
        person_index=list(pe_by_name.values()),
        ocr_backend=mine.ocr_backend or disk.ocr_backend,
        ocr_lang=mine.ocr_lang or disk.ocr_lang,
        llm_model=mine.llm_model or disk.llm_model,
        pipeline_version=mine.pipeline_version or disk.pipeline_version,
        started_at=min(x for x in [mine.started_at, disk.started_at] if x) if (mine.started_at or disk.started_at) else 0,
        finished_at=max(mine.finished_at or 0, disk.finished_at or 0) or None,
        notes=mine.notes or disk.notes,
    )
    return out


def load_manifest(path: str | Path) -> BookManifest:
    """Load manifest from JSON. Lenient — missing fields use defaults."""
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    # Convert nested dataclasses
    sections = [BookSection(**s) for s in data.pop("sections", [])]
    pages = [BookPage(**pg) for pg in data.pop("pages", [])]
    figures = [BookFigure(**fg) for fg in data.pop("figures", [])]
    wikilinks = [WikiLinkIndex(**w) for w in data.pop("wikilink_index", [])]
    hashtags = [HashtagIndex(**h) for h in data.pop("hashtag_index", [])]
    persons = [PersonIndex(**p) for p in data.pop("person_index", [])]
    return BookManifest(
        sections=sections, pages=pages, figures=figures,
        wikilink_index=wikilinks, hashtag_index=hashtags,
        person_index=persons, **data,
    )


def make_book_slug(name: str) -> str:
    """Filesystem-safe slug from book name."""
    import re
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_text = re.sub(r"[^A-Za-z0-9]+", "-", ascii_text).strip("-").lower()
    return ascii_text[:80] or "untitled"


# ─── Helpers for building manifest incrementally ───────────────────────────

def upsert_wikilink(
    manifest: BookManifest, concept_vi: str, page: int, section_id: str | None = None,
) -> None:
    """Add an occurrence of `concept_vi` at `page`. Creates index entry if new."""
    norm = concept_vi.strip()
    if not norm:
        return
    for idx in manifest.wikilink_index:
        if idx.concept_vi == norm:
            for occ in idx.occurrences:
                if occ.get("page") == page:
                    return  # already recorded
            idx.occurrences.append({"page": page, "section_id": section_id})
            return
    manifest.wikilink_index.append(
        WikiLinkIndex(concept_vi=norm, occurrences=[{"page": page, "section_id": section_id}])
    )


def upsert_hashtag(manifest: BookManifest, tag: str, page: int) -> None:
    """Add page to hashtag's reverse index."""
    t = tag.strip()
    if not t:
        return
    for idx in manifest.hashtag_index:
        if idx.tag == t:
            if page not in idx.pages:
                idx.pages.append(page)
                idx.count = len(idx.pages)
            return
    manifest.hashtag_index.append(HashtagIndex(tag=t, pages=[page], count=1))


def upsert_person(manifest: BookManifest, name: str, page: int) -> None:
    """Add page to person's reverse index."""
    n = name.strip()
    if not n:
        return
    for idx in manifest.person_index:
        if idx.name == n:
            if page not in idx.pages:
                idx.pages.append(page)
                idx.count = len(idx.pages)
            return
    manifest.person_index.append(PersonIndex(name=n, pages=[page], count=1))
