"""Thủ thư — Librarian module for YI-Lexicon.

When anh uploads a new book, the librarian:
1. Counts pages (pdftoppm / pdf_info)
2. Generates a cover thumbnail (first page PNG)
3. OCRs first 5-10 pages to capture title page + intro
4. Calls LLM to propose {title, author, tier, schools, summary, justification}
5. Cross-checks against manifest (tier-config from `source_tiers.yaml`)
6. Returns a `LibrarianProposal` — anh approves/edits/rejects via UI

Workflow:
    proposal = analyze_book("path/to/book.pdf")
    # anh edits & confirms via API → corpus row updated with status='queued'
    # later: ingest_pdf_book() picks it up

The librarian does NOT auto-ingest the body — that's a separate step under
anh's tuyên ngôn (he reviews tier classification before deep reading begins).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .tiers import get_book_meta_for_file


LIBRARY_DIR = Path(__file__).resolve().parent.parent.parent / "thư viện sách"
COVER_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_lexicon" / "covers"


# ─── Schools registry (extensible — anh can grow this) ──────────────────────

# 7 core schools + extensible "other". Anh can add new schools via API.
KNOWN_SCHOOLS: dict[str, dict] = {
    "kinh_dich":   {"vi": "Kinh Dịch (Tổng Quát)",     "color": "#fbbf24"},
    "mai_hoa":     {"vi": "Mai Hoa Dịch Số",           "color": "#a78bfa"},
    "lien_hoa":    {"vi": "Liên Hoa",                   "color": "#f472b6"},
    "luc_hao":     {"vi": "Lục Hào",                    "color": "#60a5fa"},
    "bat_tu":      {"vi": "Bát Tự (Tứ Trụ)",            "color": "#34d399"},
    "tu_vi":       {"vi": "Tử Vi Đẩu Số",               "color": "#fb923c"},
    "ha_lac":      {"vi": "Hà Lạc Lý Số",               "color": "#94a3b8"},
    "chiem_tinh":  {"vi": "Chiêm Tinh Tây Phương",      "color": "#a3e635"},
    "phong_thuy":  {"vi": "Phong Thuỷ",                  "color": "#22d3ee"},
    "y_dich":      {"vi": "Y Dịch (Đông Y theo Dịch)",  "color": "#f87171"},
    "common":      {"vi": "Chung (Đa trường phái)",      "color": "#cbd5e1"},
}


@dataclass
class LibrarianProposal:
    """LLM's first-pass classification for a newly-uploaded book."""
    file_path: str
    pages_total: int
    cover_image: str | None = None
    # Proposed metadata
    title: str = ""
    author: str | None = None
    tier: str = "B"
    tier_reason: str = ""
    schools: list[str] = field(default_factory=lambda: ["common"])
    school_reason: str = ""
    summary: str = ""
    quality_signals: list[str] = field(default_factory=list)  # ["hán cổ", "có chú giải", ...]
    confidence: float = 0.5
    # Provenance
    source_tier_from_manifest: bool = False
    raw_llm_response: str | None = None
    errors: list[str] = field(default_factory=list)
    # v5 text-layer classification (decides restore strategy)
    text_layer_method: str = "unknown"        # 'text_layer'|'hybrid'|'pure_scan'
    text_layer_chars_per_page: float = 0.0
    text_layer_estimated_min: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _pdf_page_count(pdf_path: Path) -> int:
    """Count pages via pdfinfo (fast)."""
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


def _make_cover(pdf_path: Path, *, dpi: int = 100) -> Path | None:
    """Render page 1 to PNG; return path or None on failure."""
    if not shutil.which("pdftoppm"):
        return None
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    safe_stem = re.sub(r"[^A-Za-z0-9_-]", "_", pdf_path.stem)[:80]
    out_prefix = COVER_DIR / safe_stem
    final_path = COVER_DIR / f"{safe_stem}.png"
    if final_path.exists():
        return final_path
    try:
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-f", "1", "-l", "1",
             "-png", "-singlefile", str(pdf_path), str(out_prefix)],
            check=True, capture_output=True, timeout=30,
        )
        if final_path.exists():
            return final_path
    except Exception:
        return None
    return None


def _ocr_intro_pages(pdf_path: Path, *, pages: int = 6) -> str:
    """OCR first N pages — for title-page + introduction reading."""
    if not shutil.which("pdftoppm") or not shutil.which("tesseract"):
        return ""
    with tempfile.TemporaryDirectory(prefix="yi_lib_") as tmp:
        tmppath = Path(tmp)
        try:
            subprocess.run(
                ["pdftoppm", "-r", "180", "-f", "1", "-l", str(pages),
                 "-png", str(pdf_path), str(tmppath / "p")],
                check=True, capture_output=True, timeout=120,
            )
        except Exception:
            return ""
        chunks: list[str] = []
        for png in sorted(tmppath.glob("p-*.png")):
            try:
                with png.open("rb") as f:
                    r = subprocess.run(
                        ["tesseract", "-", "-", "-l", "vie"],
                        stdin=f, capture_output=True, timeout=60,
                    )
                txt = r.stdout.decode("utf-8", errors="replace").strip()
                if txt:
                    chunks.append(txt)
            except Exception:
                continue
        return "\n\n---\n\n".join(chunks)


# ─── LLM classification prompt ──────────────────────────────────────────────


_LIBRARIAN_PROMPT = """Bạn là **Thủ Thư** của YI-Lexicon — chuyên gia phân loại sách dịch học, mệnh lý, cosmology Đông Á.

Anh vừa đưa cho bạn 5-6 trang đầu (title page + lời nói đầu) của một cuốn sách. Nhiệm vụ:

1. Đọc kỹ và phân tích:
   - Tên sách (chính xác — bỏ tên file)
   - Tác giả (nếu có)
   - Trường phái(s): chọn từ danh sách [{schools}] hoặc đề xuất tên mới nếu rõ ràng không khớp.
   - Tier authority:
     * **S** = Kinh điển gốc (Kinh Dịch, Hoàng Đế Nội Kinh, các sách cấp Tổ)
     * **A** = Kinh điển trường phái (Trích Thiên Tủy, Tăng San Bốc Dịch, Tử Vi Đẩu Số toàn thư, ...)
     * **B** = Học giả VN hiện đại có uy tín (Nguyễn Duy Cần, Lê Văn Sửu, Hoàng Tuấn, Thiệu Vĩ Hoa, ...)
     * **C** = Đại chúng / phổ thông / sách mẫu / blog tổng hợp
   - Lý do cho tier (1 câu, dựa vào tác giả + cách viết + thời đại)
   - 1-2 câu tóm tắt nội dung chính
   - Tín hiệu chất lượng: ["có chú giải Hán cổ", "trích dẫn Kinh Dịch trực tiếp", "có bảng tra", "viết thiếu căn cứ", ...]
   - Confidence (0.0-1.0): bạn tự tin mức nào về phân loại trên?

2. Tuyệt đối KHÔNG bịa: nếu trang đầu mơ hồ hoặc OCR quá nát → trả `confidence < 0.4` và viết lý do trong `tier_reason`.

3. Nguyên tắc đa trường phái (tuyên ngôn): nếu sách bàn nhiều trường phái → cho cả vào `schools` array. Đừng ép vào 1 trường phái duy nhất.

## Output JSON (CHỈ JSON, không markdown wrapper)

{{
  "title": "...",
  "author": "..." | null,
  "tier": "S" | "A" | "B" | "C",
  "tier_reason": "1 câu",
  "schools": ["mai_hoa", "luc_hao", ...],
  "school_reason": "1 câu",
  "summary": "1-2 câu",
  "quality_signals": ["...", "..."],
  "confidence": 0.0-1.0
}}
"""


def _call_llm_classifier(intro_text: str, *, file_hint: str = "") -> tuple[dict, str]:
    """Send intro pages to LLM. Returns (parsed_dict, raw_response_text)."""
    try:
        from engine.ai.registry import get_registry
        provider = get_registry().first_configured(
            preferred_order=["deepseek", "zai", "anthropic"]
        )
    except Exception as e:
        return {}, f"[provider load error: {e}]"
    if provider is None:
        return {}, "[no LLM provider configured]"

    schools_list = ", ".join(KNOWN_SCHOOLS.keys())
    sys_prompt = _LIBRARIAN_PROMPT.format(schools=schools_list)
    user_msg = f"## Tên file gốc\n{file_hint}\n\n## OCR 5-6 trang đầu\n\n{intro_text[:8000]}"

    try:
        resp = provider.chat(
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg},
            ],
            model="deepseek-v4-flash",
            max_tokens=2000,
            temperature=0.2,
        )
        content = resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        return {}, f"[llm error: {e}]"

    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        return {}, content
    try:
        return json.loads(m.group(0)), content
    except json.JSONDecodeError:
        return {}, content


# ─── Public API ──────────────────────────────────────────────────────────────


def analyze_book(
    pdf_path: str | Path,
    *,
    ocr_pages: int = 6,
    skip_llm: bool = False,
) -> LibrarianProposal:
    """Run full librarian analysis on a PDF: counts, cover, OCR intro, LLM classify.

    Args:
        pdf_path: path to PDF (absolute or relative to thư viện sách/)
        ocr_pages: how many initial pages to OCR (default 6 — title + intro)
        skip_llm: if True, skip LLM call (for fast metadata-only scanning)

    Returns LibrarianProposal — anh can edit/approve via UI.
    """
    pdf_path = Path(pdf_path) if not isinstance(pdf_path, Path) else pdf_path
    if not pdf_path.is_absolute():
        candidate = LIBRARY_DIR / pdf_path.name
        if candidate.exists():
            pdf_path = candidate
        elif pdf_path.exists():
            pdf_path = pdf_path.resolve()

    proposal = LibrarianProposal(
        file_path=str(pdf_path),
        pages_total=0,
        title=pdf_path.stem,
    )

    if not pdf_path.exists():
        proposal.errors.append(f"PDF not found: {pdf_path}")
        return proposal

    # Step 1: page count + cover (fast, always done)
    proposal.pages_total = _pdf_page_count(pdf_path)
    cover = _make_cover(pdf_path)
    if cover:
        proposal.cover_image = str(cover)

    # Step 1b: probe text layer — KEY classification, decides MarkItDown vs OCR
    text_layer_info = classify_text_layer(pdf_path)
    # Attach to proposal for UI display
    proposal.text_layer_method = text_layer_info.get("method", "unknown")
    proposal.text_layer_chars_per_page = text_layer_info.get("chars_per_page", 0.0)
    proposal.text_layer_estimated_min = text_layer_info.get("estimated_time_min", 0)

    # Step 2: check manifest first — if listed, that's authoritative
    book_meta = get_book_meta_for_file(pdf_path.name)
    if book_meta:
        proposal.title = book_meta.title
        proposal.author = book_meta.author
        proposal.tier = book_meta.tier
        proposal.tier_reason = "Đã có trong manifest tier-config (anh đã duyệt từ trước)."
        proposal.schools = list(book_meta.schools)
        proposal.school_reason = "Theo manifest."
        proposal.confidence = 0.95
        proposal.source_tier_from_manifest = True
        if book_meta.pages_estimate and not proposal.pages_total:
            proposal.pages_total = book_meta.pages_estimate
        return proposal

    if skip_llm:
        proposal.errors.append("LLM skipped — proposal uses filename only.")
        return proposal

    # Step 3: OCR intro + LLM classify
    intro = _ocr_intro_pages(pdf_path, pages=ocr_pages)
    if not intro:
        proposal.errors.append("OCR returned empty — sách có thể quá mờ hoặc thiếu tesseract.")
        return proposal

    data, raw = _call_llm_classifier(intro, file_hint=pdf_path.name)
    proposal.raw_llm_response = raw
    if not data:
        proposal.errors.append("LLM không trả về JSON hợp lệ — anh review thủ công.")
        return proposal

    proposal.title = data.get("title") or proposal.title
    proposal.author = data.get("author")
    tier = (data.get("tier") or "B").upper()
    proposal.tier = tier if tier in ("S", "A", "B", "C") else "B"
    proposal.tier_reason = data.get("tier_reason", "")
    schools = data.get("schools") or ["common"]
    proposal.schools = [s for s in schools if isinstance(s, str)] or ["common"]
    proposal.school_reason = data.get("school_reason", "")
    proposal.summary = data.get("summary", "")
    sigs = data.get("quality_signals") or []
    proposal.quality_signals = [s for s in sigs if isinstance(s, str)]
    try:
        proposal.confidence = float(data.get("confidence", 0.5))
    except Exception:
        proposal.confidence = 0.5
    return proposal


def scan_library_dir(
    *,
    skip_llm: bool = True,
    limit: int | None = None,
) -> list[dict]:
    """Walk `thư viện sách/`, returning a metadata-only proposal for every PDF.

    `skip_llm=True` (default) → only filename + manifest lookup + page count.
    Fast scan for the dashboard. Anh triggers full LLM analysis later for unclassified books.
    """
    out: list[dict] = []
    if not LIBRARY_DIR.exists():
        return out
    pdfs = sorted(LIBRARY_DIR.glob("*.pdf"))
    if limit:
        pdfs = pdfs[:limit]
    for p in pdfs:
        prop = analyze_book(p, skip_llm=skip_llm)
        out.append(prop.to_dict())
    return out


def register_proposal_as_corpus(
    proposal: LibrarianProposal | dict,
    *,
    status: str = "queued",
    tier_decided_by: str = "librarian_llm",
):
    """Persist a librarian proposal into the corpora table.

    Returns the resulting Corpus row (dataclass).
    """
    from .store import add_corpus, get_corpus, update_corpus
    p = proposal if isinstance(proposal, dict) else proposal.to_dict()
    name = p.get("title") or Path(p.get("file_path", "unknown")).stem
    schools_tags = p.get("schools") or ["common"]
    primary_school = schools_tags[0] if schools_tags else "common"

    # Insert (or fetch if name already exists)
    corpus = add_corpus(
        name=name,
        author=p.get("author"),
        school=primary_school,
        language="vi",
        file_path=p.get("file_path"),
        notes=p.get("summary"),
        status=status,
        tier=p.get("tier", "B"),
        tier_decided_by=(
            "manifest" if p.get("source_tier_from_manifest") else tier_decided_by
        ),
        pages_total=p.get("pages_total", 0),
        schools_tags=schools_tags,
        cover_image=p.get("cover_image"),
        librarian_summary=p.get("summary"),
        librarian_proposal_json=json.dumps(p, ensure_ascii=False),
    )

    # v5: also persist text-layer classification (auto-probed by analyze_book)
    method = p.get("text_layer_method", "unknown")
    chars = p.get("text_layer_chars_per_page", 0.0)
    if method != "unknown":
        update_corpus(
            corpus.corpus_id,
            restore_method=method,
            text_layer_chars_per_page=chars,
            bump_text_layer_probed_at=True,
        )

    # If existing row had stale data, also patch fields (so re-classify updates)
    existing = get_corpus(corpus_id=corpus.corpus_id)
    if existing and existing.tier_decided_by != "anh":  # don't overwrite anh's manual decision
        update_corpus(
            corpus.corpus_id,
            tier=p.get("tier", "B"),
            tier_decided_by=(
                "manifest" if p.get("source_tier_from_manifest") else tier_decided_by
            ),
            pages_total=p.get("pages_total") or existing.pages_total,
            schools_tags=schools_tags,
            cover_image=p.get("cover_image") or existing.cover_image,
            librarian_summary=p.get("summary") or existing.librarian_summary,
            librarian_proposal_json=json.dumps(p, ensure_ascii=False),
            author=p.get("author") or existing.author,
        )
    return corpus


def sync_library_to_corpora(*, skip_llm: bool = True) -> dict:
    """Discover all PDFs in `thư viện sách/` and register them as corpora rows.

    Idempotent — running again only inserts missing books + updates metadata
    for any whose manifest entry changed.

    Returns: {"scanned": n, "registered": n, "updated": n, "errors": [...]}
    """
    from .store import get_corpus
    scanned = 0
    registered = 0
    updated = 0
    errors: list[str] = []
    if not LIBRARY_DIR.exists():
        errors.append(f"Library dir not found: {LIBRARY_DIR}")
        return {"scanned": 0, "registered": 0, "updated": 0, "errors": errors}

    for pdf in sorted(LIBRARY_DIR.glob("*.pdf")):
        scanned += 1
        try:
            prop = analyze_book(pdf, skip_llm=skip_llm)
            existed = get_corpus(name=prop.title) is not None
            register_proposal_as_corpus(prop)
            if existed:
                updated += 1
            else:
                registered += 1
        except Exception as e:
            errors.append(f"{pdf.name}: {e}")
    return {
        "scanned": scanned, "registered": registered,
        "updated": updated, "errors": errors,
    }


# ─── Text-layer classifier (v5, 2026-05-12) ──────────────────────────────────


def classify_text_layer(pdf_path: str | Path) -> dict:
    """Probe PDF text layer + classify restoration method.

    Strategy:
    1. Sample 10 spread pages via `pdftotext` (fast, system tool)
    2. Compute avg chars/page
    3. Classify:
       - chars >= 200/page → 'text_layer' (use MarkItDown, fast)
       - chars between 50-200 → 'hybrid' (some scan some text — MarkItDown + OCR fallback)
       - chars < 50 → 'pure_scan' (must OCR via qwen-vl)

    Returns:
    {
      'method': 'text_layer' | 'hybrid' | 'pure_scan',
      'chars_per_page': 1234.5,
      'pages_probed': 10,
      'pages_total': 938,
      'estimated_time_min': 5 (for text_layer) | 180 (pure_scan),
      'errors': [],
    }
    """
    p = Path(pdf_path)
    out: dict = {
        "method": "unknown",
        "chars_per_page": 0.0,
        "pages_probed": 0,
        "pages_total": 0,
        "estimated_time_min": 0,
        "errors": [],
    }
    if not p.exists():
        out["errors"].append(f"PDF not found: {p}")
        return out

    # Get total pages
    total = _pdf_page_count(p)
    out["pages_total"] = total
    if total == 0:
        out["errors"].append("Could not determine page count")
        return out

    # Pick 10 spread sample pages
    if total <= 10:
        sample_pages = list(range(1, total + 1))
    else:
        step = total // 10
        sample_pages = [max(1, i * step) for i in range(1, 11)]
    out["pages_probed"] = len(sample_pages)

    # Probe each page via pdftotext (fast, no LLM)
    total_chars = 0
    successful_probes = 0
    for pn in sample_pages:
        try:
            r = subprocess.run(
                ["pdftotext", "-f", str(pn), "-l", str(pn), str(p), "-"],
                capture_output=True, text=True, timeout=10,
            )
            text = r.stdout.strip()
            total_chars += len(text)
            successful_probes += 1
        except Exception as e:
            out["errors"].append(f"page {pn} probe failed: {e}")

    if successful_probes == 0:
        out["method"] = "pure_scan"
        out["chars_per_page"] = 0.0
        out["estimated_time_min"] = total * 0.5  # ~30s/page OCR estimate
        return out

    avg = total_chars / successful_probes
    out["chars_per_page"] = round(avg, 1)

    # Classify
    if avg >= 200:
        out["method"] = "text_layer"
        # MarkItDown extract + LLM cleanup: ~2-3s/page total
        out["estimated_time_min"] = round((total * 2.5) / 60, 1)
    elif avg >= 50:
        out["method"] = "hybrid"
        out["estimated_time_min"] = round((total * 15) / 60, 1)  # mixed
    else:
        out["method"] = "pure_scan"
        out["estimated_time_min"] = round((total * 30) / 60, 1)  # OCR + LLM

    return out


def scan_library_text_layers(
    *, update_corpora: bool = True, only_unprobed: bool = False,
) -> dict:
    """Probe ALL PDFs trong `thư viện sách/` và classify text-layer.

    `update_corpora`: nếu True, write back vào DB (restore_method, chars/page).
    `only_unprobed`: skip sách đã có `text_layer_probed_at`.

    Returns: {scanned, classified, by_method, errors}
    """
    from .store import list_corpora, update_corpus
    scanned = 0
    classified_by_method: dict[str, int] = {
        "text_layer": 0, "hybrid": 0, "pure_scan": 0, "unknown": 0,
    }
    errors: list[str] = []
    book_results: list[dict] = []

    corpora = list_corpora()
    for c in corpora:
        if not c.file_path:
            continue
        if only_unprobed and c.text_layer_probed_at:
            continue
        scanned += 1
        try:
            classification = classify_text_layer(c.file_path)
            method = classification.get("method", "unknown")
            chars = classification.get("chars_per_page", 0.0)
            classified_by_method[method] = classified_by_method.get(method, 0) + 1
            book_results.append({
                "corpus_id": c.corpus_id,
                "name": c.name,
                "tier": c.tier,
                "method": method,
                "chars_per_page": chars,
                "pages_total": classification.get("pages_total", 0),
                "estimated_time_min": classification.get("estimated_time_min", 0),
            })
            if update_corpora:
                update_corpus(
                    c.corpus_id,
                    restore_method=method,
                    text_layer_chars_per_page=chars,
                    bump_text_layer_probed_at=True,
                )
        except Exception as e:
            errors.append(f"{c.name}: {e}")

    return {
        "scanned": scanned,
        "by_method": classified_by_method,
        "books": book_results,
        "errors": errors,
    }


def list_schools() -> list[dict]:
    """Return all registered schools (extensible — anh can add more via API)."""
    return [
        {"key": k, **v}
        for k, v in KNOWN_SCHOOLS.items()
    ]


def add_school(key: str, vi_label: str, color: str = "#94a3b8") -> dict:
    """Register a new school dynamically. Persists only in-memory for now."""
    if key in KNOWN_SCHOOLS:
        return {"key": key, **KNOWN_SCHOOLS[key], "already_exists": True}
    KNOWN_SCHOOLS[key] = {"vi": vi_label, "color": color}
    return {"key": key, **KNOWN_SCHOOLS[key]}
