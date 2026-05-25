"""Extract page-1 thumbnail + metadata from PDF.

Uses PyMuPDF (fitz) — already installed in main venv.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Target cover thumbnail size
COVER_WIDTH = 480   # ×1.5 retina for 240px display
COVER_HEIGHT = 640
COVER_QUALITY = 85  # JPEG quality


def extract_cover(pdf_path: Path, out_path: Path) -> Path:
    """Render page 1 of PDF as JPEG cover thumbnail.

    Returns path to written file.
    Raises if PDF can't be opened or has 0 pages.
    """
    import fitz  # PyMuPDF
    from PIL import Image

    pdf_path = Path(pdf_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    try:
        if doc.page_count == 0:
            raise ValueError(f"PDF has 0 pages: {pdf_path}")
        page = doc.load_page(0)
        # Render at 2x zoom for crisp thumbnail
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    finally:
        doc.close()

    # Resize maintaining aspect ratio, fit within COVER_WIDTH × COVER_HEIGHT
    img.thumbnail((COVER_WIDTH, COVER_HEIGHT), Image.Resampling.LANCZOS)
    img.save(out_path, format="JPEG", quality=COVER_QUALITY, optimize=True)
    logger.info(f"📸 Cover extracted → {out_path} ({out_path.stat().st_size} bytes)")
    return out_path


def extract_pdf_metadata(pdf_path: Path) -> dict:
    """Extract metadata from PDF: page_count, title, author, year.

    Returns dict (all fields may be None except page_count).
    """
    import fitz

    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    try:
        meta = doc.metadata or {}
        page_count = doc.page_count
    finally:
        doc.close()

    # Try to parse year from creationDate (format: "D:20230515120000+00'00'")
    year: Optional[int] = None
    creation = meta.get("creationDate", "")
    if creation.startswith("D:") and len(creation) >= 6:
        try:
            year = int(creation[2:6])
        except ValueError:
            year = None

    return {
        "page_count": page_count,
        "title": (meta.get("title") or "").strip() or None,
        "author": (meta.get("author") or "").strip() or None,
        "year": year,
        "raw_metadata": meta,
    }


def save_uploaded_cover(image_bytes: bytes, out_path: Path) -> Path:
    """Save user-uploaded cover, normalize to JPEG within COVER size."""
    import io

    from PIL import Image

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((COVER_WIDTH, COVER_HEIGHT), Image.Resampling.LANCZOS)
    img.save(out_path, format="JPEG", quality=COVER_QUALITY, optimize=True)
    return out_path
