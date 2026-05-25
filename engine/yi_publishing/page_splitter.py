"""Page splitter — render thumbnails + detect page types.

Stage 1.2 của Smart Book Onboarding Pipeline.

Sau S1.1 (intake), trước khi gọi book_profiler (S1.3), em render thumbnails
cho TOÀN BỘ pages + detect type cơ bản (blank / text / image / mixed).
Mục đích:
- Gallery preview cho anh xem ngay (no OCR yet, fast)
- Skip blank/cover pages khi profiling (sample only "text" pages)
- Identify TOC pages cho stage 2.1

Output structure:
    <out_dir>/
        thumbnails/p0001.jpg ... pNNNN.jpg   (~30KB each, max 200px)
        page_types.json                       (analysis summary)

Performance: ~30s for 600 pages on M4 (single-threaded fitz render).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Page type heuristic thresholds.
# These are tuned for 200-300px thumbnails. Real Hán cổ woodblock at 200px
# has chars compressed to ~5 px/char, so ink_ratio stays low (~3-5%) even
# for dense pages. KISS — use 2 thresholds:
BLANK_INK_THRESHOLD = 0.02                  # <2% non-white ink → blank
IMAGE_HEAVY_INK_THRESHOLD = 0.35            # >35% non-white ink → image (large filled area)

DEFAULT_THUMB_DIM = 200
DEFAULT_JPEG_QUALITY = 80


# ─── Image analysis helpers ──────────────────────────────────────────────────


def _whitespace_ratio(img) -> float:
    """Fraction of near-white pixels (luminance > 240)."""
    import numpy as np
    from PIL import Image

    gray = img.convert("L") if img.mode != "L" else img
    arr = np.asarray(gray)
    return float((arr > 240).mean())


def _row_density_stddev(img) -> float:
    """Stddev of per-row dark-pixel density. Text → high (rows alternate); image → low."""
    import numpy as np

    gray = img.convert("L") if img.mode != "L" else img
    arr = np.asarray(gray)
    # Per-row mean of "darkness" = (255 - pixel_value) / 255
    row_darkness = (255 - arr).mean(axis=1) / 255
    return float(row_darkness.std() * 100)  # scale to 0-100ish


# ─── Page type detection ─────────────────────────────────────────────────────


def detect_page_type(thumbnail_path: Path) -> str:
    """Categorize a page: 'blank' | 'text' | 'image' | 'mixed'.

    Heuristic (cheap, no ML):
        1. ink_ratio < 2% → blank
        2. ink_ratio > 35% → image (large filled area)
        3. else → text (some content but not dense fill)

    Note: "text" is a default-bucket for anything with meaningful but non-overwhelming
    ink. For finer-grained classification (text vs sparse-illustration), do this in
    book_profiler.py with more samples + spike OCR.
    """
    from PIL import Image

    with Image.open(thumbnail_path) as im:
        ws = _whitespace_ratio(im)
        ink_ratio = 1.0 - ws

        if ink_ratio < BLANK_INK_THRESHOLD:
            return "blank"
        if ink_ratio > IMAGE_HEAVY_INK_THRESHOLD:
            return "image"
        return "text"


# ─── Thumbnail rendering ─────────────────────────────────────────────────────


def render_thumbnails(
    pdf_path: Path,
    out_dir: Path,
    *,
    max_dim: int = DEFAULT_THUMB_DIM,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
    skip_existing: bool = False,
) -> list[Path]:
    """Render each PDF page as a JPEG thumbnail.

    Returns list of output paths in page order.
    """
    import fitz
    from PIL import Image

    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    paths: list[Path] = []
    try:
        for i in range(doc.page_count):
            page_num = i + 1
            out_path = out_dir / f"p{page_num:04d}.jpg"
            paths.append(out_path)

            if skip_existing and out_path.exists():
                continue

            # Render at low DPI (thumbnail), then resize to max_dim
            page = doc.load_page(i)
            # Scale so longest side ≈ 2× max_dim (extra for crispness then downsample)
            rect = page.rect
            scale = (2 * max_dim) / max(rect.width, rect.height)
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            img.save(out_path, format="JPEG", quality=jpeg_quality, optimize=True)
    finally:
        doc.close()

    logger.info(f"📸 Rendered {len(paths)} thumbnails to {out_dir}")
    return paths


# ─── Book-level analysis ──────────────────────────────────────────────────────


def analyze_book(
    pdf_path: Path,
    out_dir: Path,
    *,
    max_dim: int = DEFAULT_THUMB_DIM,
    skip_existing: bool = False,
) -> dict:
    """Render all thumbnails + detect page types.

    Output:
        out_dir/
            thumbnails/p0001.jpg ... pNNNN.jpg
            page_types.json {
                page_count, pages: [
                    {page_num, type, thumbnail, whitespace_ratio}
                ]
            }
    """
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    thumb_dir = out_dir / "thumbnails"

    paths = render_thumbnails(
        pdf_path,
        thumb_dir,
        max_dim=max_dim,
        skip_existing=skip_existing,
    )

    pages_info = []
    type_counts: dict[str, int] = {"blank": 0, "text": 0, "image": 0, "mixed": 0}
    for i, p in enumerate(paths):
        page_num = i + 1
        ptype = detect_page_type(p)
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
        pages_info.append({
            "page_num": page_num,
            "type": ptype,
            "thumbnail": f"thumbnails/{p.name}",
        })

    result = {
        "page_count": len(paths),
        "type_counts": type_counts,
        "pages": pages_info,
    }

    (out_dir / "page_types.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(
        f"📊 Book analysis: {len(paths)} pages "
        f"({type_counts['text']} text, {type_counts['blank']} blank, "
        f"{type_counts['image']} image, {type_counts['mixed']} mixed)"
    )
    return result


def pick_sample_pages_for_profile(
    page_types_json: dict, *, n_samples: int = 5, prefer_type: str = "text"
) -> list[int]:
    """Pick representative page numbers for profiling.

    Strategy: skip first 10% (cover/TOC) + last 5% (index), sample from
    pages of `prefer_type`. If not enough, fall back to "mixed".
    """
    total = page_types_json["page_count"]
    if total == 0:
        return []

    skip_front = max(1, total // 10)
    skip_back = max(0, total // 20)
    middle = page_types_json["pages"][skip_front : total - skip_back]
    preferred = [p["page_num"] for p in middle if p["type"] == prefer_type]
    if len(preferred) < n_samples:
        preferred += [
            p["page_num"]
            for p in middle
            if p["type"] == "mixed" and p["page_num"] not in preferred
        ]

    # Evenly-spaced sampling
    if len(preferred) <= n_samples:
        return preferred
    step = len(preferred) / n_samples
    return [preferred[int(i * step)] for i in range(n_samples)]
