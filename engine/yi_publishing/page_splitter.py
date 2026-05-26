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
    """Categorize a page: 'blank' | 'text' | 'image' | 'mixed'."""
    info = detect_page_info(thumbnail_path)
    return info["type"]


def detect_page_info(thumbnail_path: Path) -> dict:
    """Return type + ink_ratio for a page (for density-biased sampling)."""
    from PIL import Image

    with Image.open(thumbnail_path) as im:
        ws = _whitespace_ratio(im)
        ink_ratio = 1.0 - ws

    if ink_ratio < BLANK_INK_THRESHOLD:
        ptype = "blank"
    elif ink_ratio > IMAGE_HEAVY_INK_THRESHOLD:
        ptype = "image"
    else:
        ptype = "text"
    return {"type": ptype, "ink_ratio": round(ink_ratio, 4)}


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
        info = detect_page_info(p)
        ptype = info["type"]
        type_counts[ptype] = type_counts.get(ptype, 0) + 1
        pages_info.append({
            "page_num": page_num,
            "type": ptype,
            "ink_ratio": info["ink_ratio"],
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

    Density-biased strategy (Level B):
      - Skip first 5% cover + last 5% index
      - From `prefer_type` pages, blend:
          • 40% top-density pages (catch dense Hán cổ + woodblock sections)
          • 60% evenly distributed (catch typical content)
      - Always include 1 page from front 10-25% range if exists (where
        cổ books often have problematic dense intro sections)
    """
    total = page_types_json["page_count"]
    if total == 0:
        return []

    skip_front = max(1, total // 20)   # skip 5%, not 10% — keep more early pages
    skip_back = max(0, total // 20)
    middle = page_types_json["pages"][skip_front : total - skip_back]

    # Filter by prefer_type + fallback mixed
    candidates = [p for p in middle if p.get("type") == prefer_type]
    if len(candidates) < n_samples * 2:
        candidates += [p for p in middle
                       if p.get("type") == "mixed" and p not in candidates]

    if not candidates:
        return []

    # Sort by ink_ratio descending (dense pages first)
    has_ink = all("ink_ratio" in p for p in candidates)
    if has_ink:
        by_density = sorted(candidates, key=lambda p: p["ink_ratio"], reverse=True)
        n_dense = max(1, int(n_samples * 0.4))  # 40% top-density
        n_even = n_samples - n_dense

        dense_pages = [p["page_num"] for p in by_density[:n_dense]]
        # Evenly distributed across positional order (not density order)
        rest = [p for p in candidates if p["page_num"] not in dense_pages]
        if rest:
            step = len(rest) / max(n_even, 1)
            even_pages = [rest[min(int(i * step), len(rest) - 1)]["page_num"]
                          for i in range(n_even)]
        else:
            even_pages = []

        # Bonus: 1 from front 10-25% range if not already covered
        front_range = page_types_json["pages"][total // 10 : total // 4]
        front_text = [p["page_num"] for p in front_range
                      if p.get("type") == prefer_type]
        picked = list(set(dense_pages + even_pages))
        if front_text and not any(p in front_text for p in picked):
            # Replace last "even" pick with a front pick (median of front range)
            picked = picked[:-1] + [front_text[len(front_text) // 2]]

        return sorted(set(picked))[:n_samples]

    # Fallback: original evenly-spaced sampling (no ink_ratio)
    preferred = [p["page_num"] for p in candidates]
    # Evenly-spaced sampling
    if len(preferred) <= n_samples:
        return preferred
    step = len(preferred) / n_samples
    return [preferred[int(i * step)] for i in range(n_samples)]
