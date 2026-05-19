"""Text-layer extraction backends — cho PDF có embedded text (không cần OCR).

Khi PDF có text layer (born-digital hoặc OCR'd vào PDF từ scanner xịn),
em không cần OCR pixel-by-pixel. MarkItDown (Microsoft) extract trực tiếp
text + cấu trúc → 1300x faster + accurate hơn OCR.

Strategy:
- Probe page 1-3 với pdftotext → nếu có > 200 chars → text layer probably good
- Use MarkItDown extract toàn bộ → cache split by \f (form feed = page break)
- ocr_page(n) → serve cached page text

Backends:
- MarkItDownBackend: chính, dùng Microsoft MarkItDown
- PdfMinerBackend: fallback, dùng pdfminer.six trực tiếp
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .ocr_backends import OcrPageResult


def has_text_layer(pdf_path: Path | str, *, min_chars: int = 200) -> bool:
    """Quick probe: PDF có embedded text layer ngon không?

    Sample 3 pages đầu via `pdftotext`. Return True nếu text > min_chars.
    """
    p = Path(pdf_path)
    if not p.exists():
        return False
    try:
        r = subprocess.run(
            ["pdftotext", "-l", "5", str(p), "-"],
            capture_output=True, text=True, timeout=15,
        )
        return len(r.stdout.strip()) > min_chars
    except Exception:
        return False


class MarkItDownBackend:
    """Extract toàn bộ PDF text layer 1 phát qua MarkItDown, serve per-page.

    Lifecycle:
    - First `ocr_page(n)` call: extract entire PDF (cache in memory)
    - Subsequent calls: serve from cache
    - Multiple instances bound to different PDFs → independent caches
    """
    name = "markitdown"

    def __init__(self, pdf_path: str | Path | None = None, lang: str = "vie"):
        self._pdf_path: Path | None = Path(pdf_path) if pdf_path else None
        self._pages_cache: list[str] | None = None
        self._extracted = False
        self._extract_error: str | None = None
        self.lang = lang  # for kwarg-compat with Tesseract

    def bind_pdf(self, pdf_path: str | Path) -> None:
        """Switch to a different PDF (resets cache)."""
        self._pdf_path = Path(pdf_path)
        self._pages_cache = None
        self._extracted = False
        self._extract_error = None

    def _ensure_extracted(self) -> bool:
        """Extract text once. Returns True on success."""
        if self._extracted:
            return self._pages_cache is not None
        if not self._pdf_path or not self._pdf_path.exists():
            self._extract_error = f"PDF not found: {self._pdf_path}"
            self._extracted = True
            return False
        try:
            from markitdown import MarkItDown
            md = MarkItDown()
            result = md.convert(str(self._pdf_path))
            text = (result.text_content or "")
            # pdfminer separates pages with \f (form feed)
            pages = text.split("\f")
            # Strip trailing empty pages (sometimes pdfminer adds 1 extra)
            while pages and not pages[-1].strip():
                pages.pop()
            self._pages_cache = pages
            self._extracted = True
            return True
        except Exception as e:
            self._extract_error = f"{type(e).__name__}: {e}"
            self._extracted = True
            return False

    def ocr_page_by_number(self, page_no: int) -> OcrPageResult:
        """Get text of page `page_no` (1-based) from cached extraction."""
        if not self._ensure_extracted():
            return OcrPageResult(
                text="", backend=self.name,
                errors=[self._extract_error or "extract failed"],
            )
        if not self._pages_cache:
            return OcrPageResult(text="", backend=self.name, errors=["empty cache"])
        idx = page_no - 1
        if idx < 0 or idx >= len(self._pages_cache):
            return OcrPageResult(
                text="", backend=self.name,
                errors=[f"page {page_no} out of range (1..{len(self._pages_cache)})"],
            )
        raw = self._pages_cache[idx]
        # Clean common artifacts
        cleaned = _clean_pdf_artifacts(raw)
        # MarkItDown text quality is generally high — confidence 0.95
        return OcrPageResult(
            text=cleaned, confidence=0.95 if cleaned.strip() else 0.0,
            raw_output=raw, backend=self.name,
        )

    def ocr_page(self, png_path: Path) -> OcrPageResult:
        """Adapter for OCR-backend interface.

        BUT — MarkItDown doesn't work from a PNG! It works from PDF.
        Pipeline must use ocr_page_by_number() instead. This method exists only
        for interface compatibility; we error out.
        """
        return OcrPageResult(
            text="", backend=self.name,
            errors=["MarkItDownBackend.ocr_page(png_path) not supported — "
                    "use ocr_page_by_number(page_no) instead. "
                    "Pipeline cần check backend type."],
        )

    @property
    def total_pages(self) -> int:
        """Number of pages cached (0 if not extracted)."""
        if not self._ensure_extracted() or not self._pages_cache:
            return 0
        return len(self._pages_cache)


def _clean_pdf_artifacts(text: str) -> str:
    """Strip common watermarks / artifacts từ PDF text layer.

    Sách scan VN thường có lẫn watermark sites như thuviensach.vn, Sachvui.Com.
    """
    if not text:
        return ""
    patterns = [
        r"https?://(www\.)?(thuviensach\.vn|sachvui\.com|sachhayonline\.com|tve-4u\.org)\S*",
        r"Ebook\s+miễn\s+phí\s+tại\s*:?\s*\S+",
        r"Ebook\s+thực\s+hiện\s+dành\s+cho.*?điều\s+kiện\s+mua\s+sách\.",
    ]
    out = text
    for pat in patterns:
        out = re.sub(pat, "", out, flags=re.IGNORECASE)
    # Collapse 3+ blank lines → 2
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()
