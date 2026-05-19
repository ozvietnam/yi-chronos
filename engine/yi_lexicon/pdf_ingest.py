"""PDF → Lexicon ingestion pipeline.

Anh's library is 41 scanned PDFs in `thư viện sách/` — text layer empty,
needs OCR. Pipeline:

1. **pdftoppm**  PDF page → PNG @ 200dpi
2. **tesseract -l vie**  PNG → raw text (Vietnamese OCR, ~85-90% accuracy)
3. **LLM cleanup + extract**  raw text → {cleaned_text, concepts, mappings} JSON
4. **YOLO merge**  auto-add to lexicon, queue for anh review

OCR errors expected (chăm→chấm, thức đỏ→thức đồ, etc.) — LLM cleanup pass restores meaning.

## Cost estimate
- 41 books × ~200 pages = 8200 pages
- Tesseract: free, ~5-10s/page (~12-22h batch)
- LLM cleanup: ~$0.001/page × 8200 ≈ $8 total (DeepSeek-V4-pro)
- Time with concurrency: ~2-3h

## Usage

```python
from engine.yi_lexicon.pdf_ingest import ingest_pdf_book

result = ingest_pdf_book(
    pdf_path="thư viện sách/Nguyen ly chon ngay theo lich Can Chi.pdf",
    book_name="Nguyên lý chọn ngày theo lịch Can Chi",
    author="Hoàng Tuấn",
    school="common",
    page_range=(5, 30),       # optional: only pages 5-30 for first test
    max_pages=None,
)
print(result)
```
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .ingestion import _EXTRACTION_SYSTEM_PROMPT, _merge_extracted
from .tiers import get_book_meta_for_file
from .store import (
    Corpus,
    add_corpus,
    bootstrap_db,
    list_corpora,
)


LIBRARY_DIR = Path(__file__).resolve().parent.parent.parent / "thư viện sách"


# ─── OCR cleanup prompt (LLM stage 2) ────────────────────────────────────────


_OCR_CLEANUP_PROMPT = """Bạn là chuyên gia OCR cleanup + Dịch học. Bạn nhận:
- Raw OCR output từ Tesseract trên scan tiếng Việt cổ
- Có lỗi typical: thiếu ký tự, sai dấu, ghép chữ, mất khoảng trắng

## Nhiệm vụ

1. **Cleanup ngầm**: phục hồi text gần đúng bản gốc trong đầu. Sửa lỗi OCR nếu CHẮC CHẮN (context rõ).
2. **Extract**: trích xuất concept + mapping về cosmology dịch học (Bát Quái, Ngũ Hành,
   Can-Chi, Tứ Trụ, etc.). Mỗi mapping PHẢI có `source_quote` — đoạn 30-100 ký tự cleaned
   từ text gốc làm bằng chứng truy nguyên (anh kiểm chứng được).

## Output JSON

```json
{
  "concepts": [
    {
      "canonical_vi": "tên Việt",
      "canonical_zh": "tên Hán nếu có",
      "concept_type": "object | phenomenon | color | number | action | relation | time | place | concept | symbol",
      "aliases": ["biến thể"],
      "schools": ["mai_hoa", "luc_hao", "bat_tu", "tu_vi", "ha_lac", "lien_hoa", "chiem_tinh", "common"],
      "mappings": [
        {
          "dim_type": "bat_quai | ngu_hanh | am_duong | thien_can | dia_chi | tiet_khi | hexagram | thap_than | than_sat | cung_tu_vi | huong | mua | tang_phu | thoi | khac",
          "dim_value": "Mộc / Đoài / ...",
          "reasoning_vi": "1 câu giải thích, ≤ 25 từ, đơn giản",
          "reasoning_zh": "nếu có nguyên văn Hán",
          "source_quote": "BẮT BUỘC — 30-100 ký tự trích nguyên văn (cleaned từ OCR) làm bằng chứng",
          "confidence": 0.0-1.0
        }
      ]
    }
  ],
  "contextual_meanings": [
    {
      "phrase_vi": "vd: 'lá rơi mùa hạ'",
      "primary_concept_vi": "lá rơi",
      "modifier_concepts_vi": ["mùa hạ"],
      "meaning_vi": "1-2 câu giải nghĩa",
      "source_quote": "đoạn trích bằng chứng",
      "school": "common | mai_hoa | ...",
      "confidence": 0.0-1.0
    }
  ]
}
```

## Nguyên tắc

1. **source_quote BẮT BUỘC** trên mỗi mapping — không có thì SKIP mapping đó.
2. KHÔNG bịa concepts không có trong text. Confidence ≥ 0.8 chỉ khi text khẳng định trực tiếp.
3. Đơn giản hoá `reasoning_vi`: dùng tiếng Việt phổ thông, ≤ 25 từ.
4. Sách cổ có Hán xen kẽ → giữ Hán trong `canonical_zh` và `reasoning_zh`.

Trả về CHỈ JSON, không markdown wrapper."""


# ─── OCR pipeline ────────────────────────────────────────────────────────────


def _convert_pdf_to_images(
    pdf_path: Path, output_dir: Path, *, first_page: int = 1,
    last_page: int | None = None, dpi: int = 200,
) -> list[Path]:
    """Convert PDF pages to PNG files via pdftoppm. Returns list of PNG paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pdftoppm", "-r", str(dpi), "-f", str(first_page),
    ]
    if last_page:
        cmd += ["-l", str(last_page)]
    cmd += ["-png", str(pdf_path), str(output_dir / "page")]
    subprocess.run(cmd, check=True, capture_output=True)
    return sorted(output_dir.glob("page-*.png"))


def _ocr_page(png_path: Path, *, langs: str = "vie") -> str:
    """OCR one PNG via tesseract. Uses stdin pipe to bypass weird filename issues."""
    with png_path.open("rb") as f:
        result = subprocess.run(
            ["tesseract", "-", "-", "-l", langs],
            stdin=f, capture_output=True, timeout=60,
        )
    return result.stdout.decode("utf-8", errors="replace")


def _llm_cleanup_and_extract(
    raw_text: str, *, llm_provider, model: str, source_tag: str,
    book_name: str | None = None,
) -> dict:
    """Send raw OCR text to LLM. Returns {concepts, contextual_meanings, cleaned_preview}."""
    book_hint = f"(Sách: {book_name})" if book_name else ""
    messages = [
        {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": _OCR_CLEANUP_PROMPT + f"\n\n## Raw OCR {book_hint}\n\n" + raw_text},
    ]
    response = llm_provider.chat(
        messages=messages, model=model, max_tokens=16000, temperature=0.3,
    )
    content = response.content if hasattr(response, "content") else str(response)
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_match:
        return {"concepts": [], "contextual_meanings": []}
    try:
        return json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"concepts": [], "contextual_meanings": []}


# ─── Public API ──────────────────────────────────────────────────────────────


@dataclass
class PdfIngestionResult:
    book_name: str
    pdf_path: str
    pages_processed: int
    pages_ocr_empty: int
    concepts_added: int
    mappings_added: int
    contextual_added: int
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


def ingest_pdf_book(
    pdf_path: str | Path,
    *,
    book_name: str,
    author: str | None = None,
    school: str = "common",
    page_range: tuple[int, int] | None = None,
    max_pages: int | None = None,
    llm_provider=None,
    model: str = "deepseek-v4-flash",
    pages_per_llm_chunk: int = 1,
    dpi: int = 200,
    ocr_langs: str = "vie",
    on_progress=None,
) -> PdfIngestionResult:
    """Ingest a scanned PDF: OCR → LLM cleanup → extract concepts → merge.

    Args:
        pdf_path: path to PDF (relative or absolute)
        book_name: human-readable name for Corpus record
        author, school: metadata
        page_range: (first, last) inclusive. None = all pages.
        max_pages: cap (for testing). None = full range.
        llm_provider: LLMProvider instance. Auto-loaded from registry if None.
        pages_per_llm_chunk: combine N pages of OCR text per LLM call (cost↓)
        dpi: image resolution for OCR
        ocr_langs: tesseract language list (e.g. "vie+chi_sim")
        on_progress: optional callback(page_num, total) for live UI

    Returns: PdfIngestionResult with stats + errors.
    """
    bootstrap_db()
    pdf_path = Path(pdf_path) if not isinstance(pdf_path, Path) else pdf_path
    if not pdf_path.is_absolute():
        # Try library dir first, then cwd
        if (LIBRARY_DIR / pdf_path.name).exists():
            pdf_path = LIBRARY_DIR / pdf_path.name
        elif pdf_path.exists():
            pdf_path = pdf_path.resolve()

    if not pdf_path.exists():
        return PdfIngestionResult(
            book_name=book_name, pdf_path=str(pdf_path),
            pages_processed=0, pages_ocr_empty=0,
            concepts_added=0, mappings_added=0, contextual_added=0,
            errors=[f"PDF not found: {pdf_path}"],
        )

    # Resolve LLM provider
    if llm_provider is None:
        try:
            from engine.ai.registry import get_registry
            llm_provider = get_registry().first_configured(
                preferred_order=["deepseek", "zai", "anthropic"]
            )
        except Exception:
            pass
    if llm_provider is None:
        return PdfIngestionResult(
            book_name=book_name, pdf_path=str(pdf_path),
            pages_processed=0, pages_ocr_empty=0,
            concepts_added=0, mappings_added=0, contextual_added=0,
            errors=["No LLM provider configured — set DEEPSEEK_API_KEY"],
        )

    # Register corpus
    corpus = add_corpus(
        name=book_name, author=author, school=school,
        language="vi", file_path=str(pdf_path),
        notes=f"Ingested via pdf_ingest pipeline. OCR langs={ocr_langs}, dpi={dpi}.",
    )

    start = time.time()
    source_tag = f"corpus:pdf:{book_name}:{int(start)}"

    # Auto-detect tier from manifest if available
    pdf_filename = pdf_path.name
    book_meta = get_book_meta_for_file(pdf_filename)
    source_tier = book_meta.tier if book_meta else "B"
    if book_meta and not author:
        author = book_meta.author

    # OCR pipeline — use tmpdir for PNGs (cleanup automatic)
    total = {"concepts": 0, "mappings": 0, "contextual": 0}
    errors: list[str] = []
    pages_processed = 0
    pages_empty = 0

    with tempfile.TemporaryDirectory(prefix="yi_ocr_") as tmpdir:
        tmppath = Path(tmpdir)
        first_page = page_range[0] if page_range else 1
        last_page = page_range[1] if page_range else None
        if max_pages and last_page is None:
            last_page = first_page + max_pages - 1
        elif max_pages and last_page:
            last_page = min(last_page, first_page + max_pages - 1)

        # Step 1: convert all requested pages to PNG (one batch — fast)
        try:
            png_files = _convert_pdf_to_images(
                pdf_path, tmppath, first_page=first_page,
                last_page=last_page, dpi=dpi,
            )
        except Exception as e:
            return PdfIngestionResult(
                book_name=book_name, pdf_path=str(pdf_path),
                pages_processed=0, pages_ocr_empty=0,
                concepts_added=0, mappings_added=0, contextual_added=0,
                errors=[f"pdftoppm failed: {e}"],
                duration_seconds=time.time() - start,
            )

        # Step 2: OCR each page → accumulate into chunks of N pages per LLM call
        chunk_buf: list[str] = []
        chunk_start_page = first_page

        for idx, png in enumerate(png_files):
            current_page = first_page + idx
            if on_progress:
                on_progress(current_page, len(png_files))
            try:
                ocr_text = _ocr_page(png, langs=ocr_langs).strip()
                if not ocr_text or len(ocr_text) < 50:
                    pages_empty += 1
                    continue
                chunk_buf.append(f"## Trang {current_page}\n\n{ocr_text}")
                pages_processed += 1

                # When chunk is full, send to LLM
                if len(chunk_buf) >= pages_per_llm_chunk:
                    chunk_text = "\n\n---\n\n".join(chunk_buf)
                    try:
                        extracted = _llm_cleanup_and_extract(
                            chunk_text, llm_provider=llm_provider,
                            model=model,
                            source_tag=f"{source_tag}:p{chunk_start_page}-{current_page}",
                            book_name=book_name,
                        )
                        merged = _merge_extracted(
                            extracted,
                            source_tag=f"{source_tag}:p{chunk_start_page}-{current_page}",
                            source_meta={
                                "tier": source_tier,
                                "book_name": book_name,
                                "page": chunk_start_page,
                            },
                        )
                        for k in total:
                            total[k] += merged[k]
                    except Exception as e:
                        errors.append(f"LLM chunk p{chunk_start_page}-{current_page}: {e}")
                    chunk_buf = []
                    chunk_start_page = current_page + 1
            except subprocess.TimeoutExpired:
                errors.append(f"OCR timeout on page {current_page}")
            except Exception as e:
                errors.append(f"OCR page {current_page}: {e}")

        # Flush any remaining chunk
        if chunk_buf:
            chunk_text = "\n\n---\n\n".join(chunk_buf)
            try:
                extracted = _llm_cleanup_and_extract(
                    chunk_text, llm_provider=llm_provider, model=model,
                    source_tag=f"{source_tag}:p{chunk_start_page}-final",
                    book_name=book_name,
                )
                merged = _merge_extracted(
                    extracted,
                    source_tag=f"{source_tag}:p{chunk_start_page}-final",
                    source_meta={
                        "tier": source_tier,
                        "book_name": book_name,
                        "page": chunk_start_page,
                    },
                )
                for k in total:
                    total[k] += merged[k]
            except Exception as e:
                errors.append(f"LLM final chunk: {e}")

    duration = time.time() - start

    # Update corpus row stats
    from .store import _conn
    with _conn() as c:
        c.execute(
            "UPDATE corpora SET ingested_at=?, concepts_extracted=?, mappings_extracted=? "
            "WHERE corpus_id=?",
            (int(time.time()), total["concepts"], total["mappings"], corpus.corpus_id),
        )

    return PdfIngestionResult(
        book_name=book_name,
        pdf_path=str(pdf_path),
        pages_processed=pages_processed,
        pages_ocr_empty=pages_empty,
        concepts_added=total["concepts"],
        mappings_added=total["mappings"],
        contextual_added=total["contextual"],
        errors=errors,
        duration_seconds=duration,
    )


def list_library_pdfs() -> list[dict]:
    """Scan `thư viện sách/` and return [{name, path, size_mb}] for all PDFs."""
    if not LIBRARY_DIR.exists():
        return []
    out = []
    for p in sorted(LIBRARY_DIR.glob("*.pdf")):
        out.append({
            "name": p.stem,
            "path": str(p),
            "size_mb": round(p.stat().st_size / 1024 / 1024, 2),
        })
    return out
