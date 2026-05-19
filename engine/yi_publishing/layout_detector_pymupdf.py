"""Layout detector — PyMuPDF backend.

Lý do chọn PyMuPDF over unstructured hi_res:
    - Fast (1-2s per page vs 30-120s)
    - Deterministic (không download model lớn, không HTTP)
    - PDF có text layer → blocks + bbox đã có sẵn, không cần OCR ML
    - get_images() detect raster images với bbox
    - find_tables() detect table structure (1.23+)

Trade-off: PyMuPDF chỉ work tốt với PDF có text layer. Cho scan-only PDFs
cần fallback sang qwen-vl OCR mode (Layer 3).
"""
from __future__ import annotations

from typing import Optional
from pathlib import Path
import time
import logging

from .schema import (
    Region, PageLayout, RegionType, LayoutConfidence,
)

log = logging.getLogger(__name__)


def _block_to_region_type(block: dict, page_height: float) -> RegionType:
    """Phân loại block dựa trên content + font + position.

    Heuristic:
      - Block có "image" key → FIGURE_RASTER
      - Font size > 16pt → HEADING_1
      - Font size > 14pt → HEADING_2
      - Font size > 11.5pt → HEADING_3
      - Y position top 5% → RUNNING_HEADER
      - Y position bottom 5% → PAGE_NUMBER
      - Else → PARAGRAPH
    """
    # Image block
    if block.get("type") == 1:  # PyMuPDF: 0=text, 1=image
        return RegionType.FIGURE_RASTER

    # Text block — analyze font sizes
    max_font = 0
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            size = span.get("size", 10)
            if size > max_font:
                max_font = size

    # Position check
    bbox = block.get("bbox", (0, 0, 0, 0))
    y_top = bbox[1]
    y_bottom = bbox[3]

    # Header/footer detection
    if y_top < page_height * 0.07:
        # Could be running header or chapter title
        if max_font > 14:
            return RegionType.HEADING_1
        return RegionType.RUNNING_HEADER

    if y_bottom > page_height * 0.93:
        # Footer area
        text = _block_text(block).strip()
        if len(text) < 20 and text.replace(' ', '').replace('-', '').isdigit():
            return RegionType.PAGE_NUMBER
        return RegionType.RUNNING_HEADER  # treat as footer

    # Body — by font size
    if max_font >= 18:
        return RegionType.HEADING_1
    if max_font >= 14:
        return RegionType.HEADING_2
    if max_font >= 11.5:
        return RegionType.HEADING_3
    return RegionType.PARAGRAPH


def _block_text(block: dict) -> str:
    """Extract plain text từ PyMuPDF block dict."""
    if block.get("type") == 1:
        return ""  # image
    lines = []
    for line in block.get("lines", []):
        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
        lines.append(line_text)
    return "\n".join(lines)


def _detect_layout_template(blocks: list[dict], page_width: float) -> str:
    """Detect single_column vs two_column based on x-position clustering."""
    text_blocks = [b for b in blocks if b.get("type") == 0]
    if len(text_blocks) < 4:
        return "single_column"

    # X-start positions
    x_starts = [b["bbox"][0] for b in text_blocks]
    x_min = min(x_starts)
    x_mid_threshold = page_width * 0.45

    left_count = sum(1 for x in x_starts if x < x_mid_threshold)
    right_count = sum(1 for x in x_starts if x >= x_mid_threshold)

    # Need significant blocks on both sides for 2-col
    if left_count >= 3 and right_count >= 3:
        return "two_column"
    return "single_column"


def detect_page(
    pdf_path: str | Path,
    page_num: int,
    *,
    book_id: str = "book",
    page_image: Optional[str] = None,
    extract_tables: bool = True,
) -> PageLayout:
    """Detect layout regions của 1 page bằng PyMuPDF.

    Args:
        pdf_path: PDF gốc
        page_num: 1-indexed page number
        book_id: prefix cho region IDs
        page_image: path tới page image (Layer 1)
        extract_tables: detect tables (PyMuPDF 1.23+)

    Returns:
        PageLayout với regions sorted by reading order.
    """
    import fitz  # PyMuPDF

    pdf_path = str(pdf_path)
    t0 = time.time()
    log.info(f"Detecting layout (PyMuPDF): {pdf_path} page {page_num}")

    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    page_width, page_height = page.rect.width, page.rect.height

    # Get text + image blocks with structure
    page_dict = page.get_text("dict")
    blocks = page_dict.get("blocks", [])

    # Detect tables (if requested)
    table_bboxes: list[tuple] = []
    if extract_tables:
        try:
            tables = page.find_tables()
            for table in tables:
                table_bboxes.append(tuple(table.bbox))
        except Exception as e:
            log.debug(f"Table detection error: {e}")

    # Build regions
    regions: list[Region] = []
    idx = 0
    for block in blocks:
        bbox = tuple(block.get("bbox", (0, 0, 0, 0)))
        if bbox == (0, 0, 0, 0):
            continue

        # Check if bbox overlaps with detected table
        is_table = False
        for tb in table_bboxes:
            if _bbox_overlap(bbox, tb) > 0.5:
                is_table = True
                break

        if is_table:
            region_type = RegionType.TABLE
            text = _block_text(block)
        else:
            region_type = _block_to_region_type(block, page_height)
            text = _block_text(block) if block.get("type") == 0 else None

        idx += 1
        region = Region(
            id=f"{book_id}-p{page_num:04d}-r{idx:03d}",
            type=region_type,
            bbox=bbox,
            reading_order=idx,
            source_text=text,
            ocr_confidence=1.0,  # PDF text layer = ground truth
            ocr_engine="pymupdf-text-layer",
        )
        regions.append(region)

    # Add standalone images (from get_images)
    try:
        for img_idx, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            img_rects = page.get_image_rects(xref)
            for rect in img_rects:
                bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
                # Check if already covered by a block (PyMuPDF blocks include images)
                already_covered = any(
                    _bbox_overlap(bbox, r.bbox) > 0.7 for r in regions
                )
                if not already_covered:
                    idx += 1
                    regions.append(Region(
                        id=f"{book_id}-p{page_num:04d}-r{idx:03d}",
                        type=RegionType.FIGURE_RASTER,
                        bbox=bbox,
                        reading_order=idx,
                        ocr_engine="pymupdf-images",
                    ))
    except Exception as e:
        log.debug(f"Image extract error: {e}")

    doc.close()

    # Sort by reading order (top-to-bottom, then left-to-right)
    regions.sort(key=lambda r: (r.bbox[1], r.bbox[0]))
    for i, r in enumerate(regions):
        r.reading_order = i + 1

    layout_template = _detect_layout_template(blocks, page_width)

    elapsed = time.time() - t0
    log.info(
        f"  {len(regions)} regions detected, "
        f"template={layout_template}, elapsed={elapsed:.2f}s"
    )

    return PageLayout(
        page_num=page_num,
        page_image=page_image or f"pages/p{page_num:04d}.png",
        width=page_width,
        height=page_height,
        layout_template=layout_template,
        layout_confidence=LayoutConfidence.HIGH,  # PDF text layer = reliable
        layout_confidence_score=0.95,
        detection_engine="pymupdf-textdict",
        regions=regions,
    )


def _bbox_overlap(b1: tuple, b2: tuple) -> float:
    """Return overlap ratio of b1 with b2 (intersection / area_b1)."""
    x1_max = max(b1[0], b2[0])
    y1_max = max(b1[1], b2[1])
    x2_min = min(b1[2], b2[2])
    y2_min = min(b1[3], b2[3])
    if x1_max >= x2_min or y1_max >= y2_min:
        return 0.0
    inter = (x2_min - x1_max) * (y2_min - y1_max)
    area_b1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    return inter / area_b1 if area_b1 > 0 else 0.0
