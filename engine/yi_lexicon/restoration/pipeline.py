"""Restoration pipeline orchestrator.

For each PDF page:
1. Render page → PNG @ 240dpi (pdftoppm)
2. OCR via backend (default Tesseract)
3. Extract embedded figures (PyMuPDF if installed)
4. LLM cleanup → markdown + section_hint + wikilinks
5. Save per-page md + update manifest
6. Update corpora row (restored_pages, restored_status)

After all pages:
- Build full content.md (concat)
- Save manifest.json
- Build wikilink_index aggregating all per-page links
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..store import (
    bootstrap_db, get_corpus, update_corpus,
)
from .manifest import (
    BookManifest, BookPage, BookFigure, BookSection,
    make_book_slug, save_manifest, load_manifest,
    upsert_wikilink, upsert_hashtag, upsert_person,
)
from .ocr_backends import get_backend, OcrPageResult
from .figures import extract_figures_from_page
from .cleanup import cleanup_page, fetch_glossary_terms_for_book
from .exporters import export_full_markdown


RESTORED_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "data" / "yi_restored"


# ─── Public API ─────────────────────────────────────────────────────────────


@dataclass
class RestorationConfig:
    ocr_backend: str = "auto"               # 'auto' | 'tesseract' | 'qwen-vl' | 'markitdown'
                                            # 'auto' = use markitdown nếu có text layer, else qwen-vl
    ocr_model: str | None = None            # for ollama backends: 'qwen2.5-vl:7b' etc.
    ocr_lang: str = "vie"
    dpi: int = 240
    page_range: tuple[int, int] | None = None     # 1-based inclusive
    max_pages: int | None = None
    llm_provider: str = "auto"              # 'auto'|'ollama'|'deepseek'|'zai'|'anthropic'
    llm_model: str = "deepseek-v4-flash"
    extract_figures: bool = True
    skip_llm: bool = False                        # phase A debug: dump raw OCR
    incremental: bool = True                      # resume if pages already done
    force_ocr: bool = False                       # bypass text-layer auto-detect


@dataclass
class RestorationResult:
    corpus_id: int
    book_slug: str
    root_dir: str
    manifest_path: str
    pages_processed: int = 0
    pages_failed: int = 0
    figures_extracted: int = 0
    wikilinks_total: int = 0
    duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _convert_page_to_png(pdf_path: Path, page_no: int, dpi: int, out_dir: Path) -> Path | None:
    """Render a single page → PNG. Returns path or None."""
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / f"page-{page_no:04d}"
    try:
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-f", str(page_no), "-l", str(page_no),
             "-png", "-singlefile", str(pdf_path), str(prefix)],
            check=True, capture_output=True, timeout=120,
        )
        target = out_dir / f"page-{page_no:04d}.png"
        return target if target.exists() else None
    except Exception:
        return None


def _pdf_page_count(pdf_path: Path) -> int:
    try:
        out = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, timeout=15,
        )
        for line in out.stdout.splitlines():
            if line.lower().startswith("pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 0


def _ensure_manifest(
    root_dir: Path, *, slug: str, corpus, config: RestorationConfig,
) -> BookManifest:
    """Load existing manifest or create fresh one."""
    manifest_path = root_dir / "manifest.json"
    if manifest_path.exists():
        try:
            return load_manifest(manifest_path)
        except Exception:
            pass
    return BookManifest(
        book_slug=slug,
        book_name=corpus.name,
        corpus_id=corpus.corpus_id,
        author=corpus.author,
        tier=corpus.tier,
        copyright_status=corpus.copyright_status or "internal_only",
        schools=list(corpus.schools_tags or []),
        original_pdf=corpus.file_path,
        pages_total=corpus.pages_total or 0,
        ocr_backend=config.ocr_backend
            + (f":{config.ocr_model}" if config.ocr_model else ""),
        ocr_lang=config.ocr_lang,
        llm_model=config.llm_model,
        started_at=int(time.time()),
    )


def _existing_page_indices(manifest: BookManifest) -> set[int]:
    return {p.page for p in manifest.pages}


# ─── Main entrypoint ─────────────────────────────────────────────────────────


def restore_book(
    corpus_id: int,
    *,
    config: RestorationConfig | None = None,
    on_progress=None,
) -> RestorationResult:
    """Restore a book end-to-end. Idempotent in 'incremental' mode.

    Args:
        corpus_id: which book in the library to restore
        config: pipeline config (defaults: tesseract + DeepSeek + 240dpi)
        on_progress: optional callback(page_done, page_total)

    Returns RestorationResult with stats + errors.
    """
    bootstrap_db()
    cfg = config or RestorationConfig()
    corpus = get_corpus(corpus_id=corpus_id)
    if not corpus:
        return RestorationResult(
            corpus_id=corpus_id, book_slug="", root_dir="", manifest_path="",
            errors=[f"corpus {corpus_id} not found"],
        )
    if not corpus.file_path:
        return RestorationResult(
            corpus_id=corpus_id, book_slug=corpus.name, root_dir="", manifest_path="",
            errors=["corpus has no file_path"],
        )
    pdf_path = Path(corpus.file_path)
    if not pdf_path.exists():
        return RestorationResult(
            corpus_id=corpus_id, book_slug=corpus.name, root_dir="", manifest_path="",
            errors=[f"PDF not found: {pdf_path}"],
        )

    slug = make_book_slug(corpus.name)
    root_dir = RESTORED_ROOT / slug
    root_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = root_dir / "pages"
    figures_dir = root_dir / "figures"
    raw_dir = root_dir / "raw_ocr"
    for d in (pages_dir, figures_dir, raw_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Update corpus to 'pending'
    update_corpus(corpus.corpus_id, restored_status="pending",
                  restored_path=str(root_dir))

    manifest = _ensure_manifest(root_dir, slug=slug, corpus=corpus, config=cfg)
    existing_pages = _existing_page_indices(manifest) if cfg.incremental else set()

    # Determine page range
    total = corpus.pages_total or _pdf_page_count(pdf_path)
    if total > 0 and not manifest.pages_total:
        manifest.pages_total = total
    first = cfg.page_range[0] if cfg.page_range else 1
    last = cfg.page_range[1] if cfg.page_range else (total or first)
    if cfg.max_pages:
        last = min(last, first + cfg.max_pages - 1)
    if last < first:
        last = first

    # Auto-detect text layer + choose backend
    from .text_backends import has_text_layer, MarkItDownBackend
    use_markitdown = False
    if cfg.ocr_backend == "markitdown":
        use_markitdown = True
    elif cfg.ocr_backend == "auto" and not cfg.force_ocr:
        use_markitdown = has_text_layer(pdf_path)
        if use_markitdown:
            print(f"[restore] ✓ Text layer detected — using MarkItDown (1300x faster than OCR)",
                  flush=True)

    if use_markitdown:
        ocr = MarkItDownBackend(pdf_path=pdf_path, lang=cfg.ocr_lang)
    else:
        # OCR path (Tesseract, qwen-vl, etc.)
        backend_name = cfg.ocr_backend if cfg.ocr_backend not in ("auto", "markitdown") else "qwen-vl"
        ocr_kwargs: dict = {"lang": cfg.ocr_lang}
        if cfg.ocr_model:
            ocr_kwargs["model"] = cfg.ocr_model
        ocr = get_backend(backend_name, **ocr_kwargs)
    glossary = fetch_glossary_terms_for_book(corpus.schools_tags or [])

    # Resolve LLM provider once.
    # Provider preference:
    #   'auto'      → ollama > deepseek > zai > anthropic (free local first)
    #   'ollama'    → only ollama (fails fast if not running)
    #   'deepseek'  → cloud
    llm = None
    effective_model = cfg.llm_model
    if not cfg.skip_llm:
        try:
            from engine.ai.registry import get_registry
            registry = get_registry()
            if cfg.llm_provider == "ollama":
                llm = registry.get("ollama")
                if not llm.is_configured:
                    return RestorationResult(
                        corpus_id=corpus_id, book_slug=slug, root_dir=str(root_dir),
                        manifest_path=str(root_dir / "manifest.json"),
                        errors=["Ollama server not running — `ollama serve` first"],
                    )
                # Use the provider's default model (qwen3:32b) if user didn't override
                if cfg.llm_model.startswith("deepseek"):
                    effective_model = llm.default_model
            elif cfg.llm_provider in ("deepseek", "zai", "anthropic", "minimax", "openrouter", "gemini"):
                llm = registry.get(cfg.llm_provider)
            else:  # auto
                llm = registry.first_configured(
                    preferred_order=["ollama", "deepseek", "zai", "anthropic"]
                )
                # Adjust default model when auto-resolved to ollama
                if getattr(llm, "name", "") == "ollama" and cfg.llm_model.startswith("deepseek"):
                    effective_model = llm.default_model
        except Exception as e:
            return RestorationResult(
                corpus_id=corpus_id, book_slug=slug, root_dir=str(root_dir),
                manifest_path=str(root_dir / "manifest.json"),
                errors=[f"LLM provider init failed: {e}"],
            )
        if llm is None:
            return RestorationResult(
                corpus_id=corpus_id, book_slug=slug, root_dir=str(root_dir),
                manifest_path=str(root_dir / "manifest.json"),
                errors=["No LLM provider configured"],
            )

    result = RestorationResult(
        corpus_id=corpus.corpus_id, book_slug=slug, root_dir=str(root_dir),
        manifest_path=str(root_dir / "manifest.json"),
    )
    start = time.time()
    page_total_to_process = last - first + 1

    # Section state — current open section_id for page assignment
    current_section_id: str | None = None
    next_section_index = len(manifest.sections) + 1

    with tempfile.TemporaryDirectory(prefix="yi_restore_") as tmpd:
        tmp_pngs = Path(tmpd)
        for offset, page_no in enumerate(range(first, last + 1), start=1):
            if page_no in existing_pages:
                continue
            try:
                # MarkItDown serves text directly from PDF — no PNG render needed
                if use_markitdown:
                    ocr_res: OcrPageResult = ocr.ocr_page_by_number(page_no)
                    png = None  # not used downstream for figures (MarkItDown extract handles internally)
                else:
                    png = _convert_page_to_png(pdf_path, page_no, cfg.dpi, tmp_pngs)
                    if not png:
                        result.pages_failed += 1
                        result.errors.append(f"page {page_no}: render failed")
                        continue
                    ocr_res = ocr.ocr_page(png)
                if ocr_res.errors:
                    result.errors.extend([f"page {page_no}: {e}" for e in ocr_res.errors])

                # Persist raw OCR for debugging/audit
                (raw_dir / f"page-{page_no:04d}.txt").write_text(
                    ocr_res.text, encoding="utf-8"
                )

                # Extract figures (per-page; cheap if PyMuPDF available)
                # PyMuPDF extract embedded images directly from PDF — works whether
                # we OCR'd via image render or extracted text via MarkItDown.
                page_fig_ids: list[str] = []
                if cfg.extract_figures:
                    figs = extract_figures_from_page(pdf_path, page_no, figures_dir)
                    for idx, fpath in enumerate(figs.figure_paths, start=1):
                        fig_id = f"fig-{page_no:04d}-{idx}"
                        manifest.figures.append(BookFigure(
                            figure_id=fig_id, page=page_no,
                            image_path=str(Path(fpath).relative_to(root_dir)),
                            figure_type="image",
                        ))
                        page_fig_ids.append(fig_id)
                        result.figures_extracted += 1

                # LLM cleanup
                detected_figs = []
                # Default metadata (filled if cleanup succeeds)
                page_summary = ""
                page_hashtags: list[str] = []
                page_persons: list[str] = []
                page_que: list[str] = []
                if cfg.skip_llm or not ocr_res.text.strip():
                    md = ocr_res.text or ""
                    section_hint = None
                    wls: list[str] = []
                    confidence = ocr_res.confidence
                    warnings: list[str] = []
                    # Even skip-LLM: parse [[FIGURE]] markers from raw OCR
                    from .cleanup import parse_figures
                    detected_figs = parse_figures(md)
                else:
                    clean = cleanup_page(
                        ocr_res.text,
                        glossary_terms=glossary,
                        llm_provider=llm,
                        model=effective_model,
                        book_hint=corpus.name,
                        page_number=page_no,
                    )
                    if clean.errors:
                        result.errors.extend([f"page {page_no}: {e}" for e in clean.errors])
                    md = clean.cleaned_markdown or ocr_res.text
                    section_hint = clean.section_hint
                    wls = clean.wikilinks
                    confidence = clean.confidence
                    warnings = clean.warnings
                    detected_figs = clean.detected_figures
                    page_summary = clean.summary_short
                    page_hashtags = clean.hashtags
                    page_persons = clean.persons
                    page_que = clean.que_mentions

                # Register detected figures (placeholders cần redraw)
                for idx, df in enumerate(detected_figs, start=1):
                    # If we already extracted a real image for this index, skip
                    fig_id = f"fig-{page_no:04d}-detected-{idx}"
                    manifest.figures.append(BookFigure(
                        figure_id=fig_id,
                        page=page_no,
                        image_path=None,
                        description=df.description,
                        figure_type=df.figure_type,
                        source="detected_in_scan",
                        redraw_status="needs_redraw",
                        placeholder=df.placeholder,
                    ))
                    page_fig_ids.append(fig_id)

                # Section detection: open new section if LLM flagged
                if section_hint and section_hint.get("title"):
                    sec_id = f"sec-{next_section_index:03d}"
                    next_section_index += 1
                    # Close previous
                    for s in manifest.sections:
                        if s.section_id == current_section_id and s.end_page is None:
                            s.end_page = page_no - 1
                    manifest.sections.append(BookSection(
                        section_id=sec_id,
                        title=section_hint["title"],
                        level=section_hint.get("level", 1),
                        start_page=page_no,
                    ))
                    current_section_id = sec_id

                # Persist page markdown
                page_md_filename = f"page-{page_no:04d}.md"
                (pages_dir / page_md_filename).write_text(md, encoding="utf-8")

                page_record = BookPage(
                    page=page_no,
                    section_id=current_section_id,
                    md_path=f"pages/{page_md_filename}",
                    word_count=len(md.split()),
                    figure_ids=page_fig_ids,
                    wikilinks=wls,
                    ocr_confidence=confidence,
                    needs_review=(confidence < 0.6 or len(warnings) > 0),
                    summary_short=page_summary,
                    hashtags=page_hashtags,
                    persons=page_persons,
                    que_mentions=page_que,
                )
                manifest.pages.append(page_record)

                # Aggregate wikilink index
                for w in wls:
                    upsert_wikilink(manifest, w, page_no, current_section_id)
                result.wikilinks_total += len(wls)

                # Aggregate hashtag + person + quẻ indexes (v2)
                for t in page_hashtags:
                    upsert_hashtag(manifest, t, page_no)
                for p in page_persons:
                    upsert_person(manifest, p, page_no)
                for q in page_que:
                    # Treat quẻ mention as person-style entity for index reuse
                    upsert_hashtag(manifest, f"#quẻ-{q.lower().replace(' ', '-')}", page_no)

                result.pages_processed += 1

                # Persist manifest incrementally every 5 pages (crash recovery)
                if result.pages_processed % 5 == 0:
                    manifest.pages_restored = len({p.page for p in manifest.pages})
                    save_manifest(manifest, root_dir / "manifest.json")
                    update_corpus(
                        corpus.corpus_id,
                        restored_pages=manifest.pages_restored,
                        restored_manifest=str(root_dir / "manifest.json"),
                    )

                if on_progress:
                    on_progress(offset, page_total_to_process)

            except Exception as e:
                result.pages_failed += 1
                result.errors.append(f"page {page_no}: {type(e).__name__}: {e}")

    # Close trailing section
    if current_section_id:
        for s in manifest.sections:
            if s.section_id == current_section_id and s.end_page is None:
                s.end_page = last

    # Finalize
    manifest.pages_restored = len({p.page for p in manifest.pages})
    manifest.finished_at = int(time.time())
    save_manifest(manifest, root_dir / "manifest.json")
    export_full_markdown(manifest, root_dir)

    # Update corpus row
    full_done = manifest.pages_restored >= (manifest.pages_total or last)
    new_status = "done" if full_done else ("partial" if manifest.pages_restored > 0 else "error")
    update_corpus(
        corpus.corpus_id,
        restored_status=new_status,
        restored_pages=manifest.pages_restored,
        restored_path=str(root_dir),
        restored_manifest=str(root_dir / "manifest.json"),
        bump_restored_at=True,
    )

    result.duration_seconds = time.time() - start
    return result
