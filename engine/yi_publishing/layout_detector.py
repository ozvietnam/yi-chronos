"""Layout detector — wrap `unstructured.partition_pdf` với hi_res mode.

Bước 1 của Bookflow v3.0: detect regions PER PAGE.
KHÔNG OCR text content here — chỉ structure + bbox.

Output: PageLayout với regions có bbox + type. source_text giữ raw text
từ unstructured (có thể inaccurate) — Layer 3 (region_ocr.py) sẽ re-OCR
per region với engine phù hợp.

Iron Rule (Anh, 2026-05-18):
    "Bố cục là bất biến. Bbox không đổi sau detection.
    Re-OCR đổi source_text. Re-translate đổi translation. Không đổi bbox."
"""
from __future__ import annotations

from typing import Optional, Any
from pathlib import Path
import time
import logging

from .schema import (
    Region,
    PageLayout,
    RegionType,
    LayoutConfidence,
)

log = logging.getLogger(__name__)


# Mapping từ unstructured category → schema RegionType.
# Heuristic — sẽ refine sau spike test trên data thật.
UNSTRUCTURED_CATEGORY_MAP: dict[str, RegionType] = {
    "Title": RegionType.HEADING_2,  # default; refine theo font size sau
    "NarrativeText": RegionType.PARAGRAPH,
    "Text": RegionType.PARAGRAPH,
    "UncategorizedText": RegionType.PARAGRAPH,  # fallback
    "ListItem": RegionType.PARAGRAPH,
    "Table": RegionType.TABLE,
    "Image": RegionType.FIGURE_RASTER,
    "Figure": RegionType.FIGURE_RASTER,
    "FigureCaption": RegionType.CAPTION,
    "Header": RegionType.RUNNING_HEADER,
    "Footer": RegionType.PAGE_NUMBER,  # thường page number ở footer
    "PageNumber": RegionType.PAGE_NUMBER,
    "Footnote": RegionType.FOOTNOTE,
    "Address": RegionType.PARAGRAPH,
    "EmailAddress": RegionType.PARAGRAPH,
    "Formula": RegionType.PARAGRAPH,  # math formula — tạm map paragraph
    "CodeSnippet": RegionType.PARAGRAPH,
}


def _coords_to_bbox(coords: Optional[Any]) -> tuple[float, float, float, float]:
    """Convert unstructured coordinates → (x1, y1, x2, y2) bbox.

    unstructured trả coordinates dạng list of (x, y) points.
    Em lấy min/max để có bbox bao.
    """
    if coords is None:
        return (0.0, 0.0, 0.0, 0.0)
    try:
        points = coords.points if hasattr(coords, "points") else coords
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return (min(xs), min(ys), max(xs), max(ys))
    except Exception as e:
        log.warning(f"Couldn't parse coords: {e}")
        return (0.0, 0.0, 0.0, 0.0)


def _classify_heading_level(text: str, bbox: tuple, page_height: float) -> RegionType:
    """Heuristic: Title → H1/H2/H3 dựa trên font size + position.

    Tạm thời:
      - Y position < 15% page → HEADING_1 (chapter)
      - Y position < 40% page → HEADING_2 (section)
      - Else → HEADING_3 (sub)

    TODO: improve bằng font size extracted từ unstructured metadata.
    """
    y_pos = bbox[1] / page_height if page_height else 0
    if y_pos < 0.15:
        return RegionType.HEADING_1
    if y_pos < 0.40:
        return RegionType.HEADING_2
    return RegionType.HEADING_3


def _score_to_confidence(score: float) -> LayoutConfidence:
    if score >= 0.90:
        return LayoutConfidence.HIGH
    if score >= 0.70:
        return LayoutConfidence.MEDIUM
    return LayoutConfidence.LOW


def detect_page(
    pdf_path: str | Path,
    page_num: int,
    *,
    book_id: str = "book",
    page_image: Optional[str] = None,
    strategy: str = "hi_res",
    languages: Optional[list[str]] = None,
    infer_table_structure: bool = True,
) -> PageLayout:
    """Detect layout regions của 1 page.

    Args:
        pdf_path: PDF gốc
        page_num: page number (1-indexed)
        book_id: prefix cho region IDs
        page_image: path tới page image (Layer 1), nếu có
        strategy: "hi_res" (slow, accurate) | "fast" (text-only) | "ocr_only"
        languages: ["chi_sim", "eng"] cho Chinese books
        infer_table_structure: detect table cells

    Returns:
        PageLayout với regions sorted by reading_order (top-to-bottom).
    """
    from unstructured.partition.pdf import partition_pdf

    pdf_path = str(pdf_path)
    languages = languages or ["chi_sim", "eng"]

    t0 = time.time()
    log.info(f"Detecting layout: {pdf_path} page {page_num} (strategy={strategy})")

    elements = partition_pdf(
        filename=pdf_path,
        strategy=strategy,
        starting_page_number=page_num,
        infer_table_structure=infer_table_structure,
        languages=languages,
    )

    # Filter chỉ page hiện tại
    page_elements = [
        el for el in elements
        if getattr(el.metadata, "page_number", page_num) == page_num
    ]

    # Detect page dimensions từ first element có coordinates
    page_width = 595.0  # A4 default
    page_height = 842.0
    for el in page_elements:
        coords = getattr(el.metadata, "coordinates", None)
        if coords and hasattr(coords, "system"):
            sys = coords.system
            if hasattr(sys, "width") and hasattr(sys, "height"):
                page_width = float(sys.width)
                page_height = float(sys.height)
                break

    # Build regions
    regions: list[Region] = []
    for idx, el in enumerate(page_elements):
        category = getattr(el, "category", "UncategorizedText")
        coords = getattr(el.metadata, "coordinates", None)
        bbox = _coords_to_bbox(coords)

        # Map category → RegionType
        region_type = UNSTRUCTURED_CATEGORY_MAP.get(category, RegionType.PARAGRAPH)

        # Refine Title → H1/H2/H3
        if region_type == RegionType.HEADING_2 and category == "Title":
            region_type = _classify_heading_level(str(el), bbox, page_height)

        # source_text từ unstructured (Layer 3 sẽ override với better OCR sau)
        text = str(el).strip() if region_type not in (
            RegionType.FIGURE_RASTER, RegionType.FIGURE_VECTOR
        ) else None

        # OCR confidence từ unstructured (nếu có)
        ocr_conf = getattr(el.metadata, "detection_class_prob", 0.0) or 0.0

        region = Region(
            id=f"{book_id}-p{page_num:04d}-r{idx+1:03d}",
            type=region_type,
            bbox=bbox,
            reading_order=idx + 1,  # tạm theo unstructured order
            source_text=text,
            ocr_confidence=ocr_conf,
            ocr_engine="unstructured-hi_res",
        )
        regions.append(region)

    # Sort by reading order — top-to-bottom by y, then left-to-right by x
    # unstructured đã trả theo reading order natural; ta giữ
    # Tuy nhiên override reading_order theo position để stable
    regions.sort(key=lambda r: (r.bbox[1], r.bbox[0]))
    for i, r in enumerate(regions):
        r.reading_order = i + 1

    # Detect layout template (heuristic)
    layout_template = _detect_template(regions, page_width)

    # Aggregate confidence (mean of region confidences)
    confs = [r.ocr_confidence for r in regions if r.ocr_confidence > 0]
    avg_conf = sum(confs) / len(confs) if confs else 0.85
    layout_conf = _score_to_confidence(avg_conf)

    elapsed = time.time() - t0
    log.info(
        f"  {len(regions)} regions detected, "
        f"template={layout_template}, "
        f"avg_conf={avg_conf:.2f}, "
        f"elapsed={elapsed:.1f}s"
    )

    return PageLayout(
        page_num=page_num,
        page_image=page_image or f"pages/p{page_num:04d}.png",
        width=page_width,
        height=page_height,
        layout_template=layout_template,
        layout_confidence=layout_conf,
        layout_confidence_score=avg_conf,
        detection_engine=f"unstructured-{strategy}",
        regions=regions,
        needs_review=(layout_conf == LayoutConfidence.LOW),
    )


def _detect_template(regions: list[Region], page_width: float) -> str:
    """Heuristic detect: single_column | two_column | three_column | mixed.

    Dựa trên cluster x-coordinate của paragraph regions.
    """
    if not regions:
        return "empty"

    para_regions = [r for r in regions if r.type == RegionType.PARAGRAPH]
    if len(para_regions) < 3:
        return "single_column"

    # Cluster x1 coordinates
    x_starts = sorted({round(r.bbox[0], -1) for r in para_regions})  # round to 10s
    if len(x_starts) >= 3 and page_width > 0:
        # Check if distinct columns
        ratios = [x / page_width for x in x_starts]
        # Two distinct groups → 2-col
        if max(ratios) > 0.45 and min(ratios) < 0.15:
            return "two_column"

    return "single_column"
