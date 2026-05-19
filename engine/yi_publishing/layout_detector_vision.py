"""Vision-based layout detector — qwen2.5vl backend.

Cho scan-only PDFs (như sách Q3 — 图解梅花易数).
PyMuPDF text-layer FAIL → 1 image/page.
Em dùng qwen2.5vl với prompt layout-aware return JSON.

Output bbox: percentage of page (0.0-1.0) — vision model dễ output hơn pixels.
Sau khi parse → scale lên PDF coords.
"""
from __future__ import annotations

import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import Optional

import requests

from .schema import (
    Region, PageLayout, RegionType, LayoutConfidence,
)

log = logging.getLogger(__name__)


# Map qwen output strings → RegionType
VL_TYPE_MAP = {
    "heading_1": RegionType.HEADING_1,
    "heading_2": RegionType.HEADING_2,
    "heading_3": RegionType.HEADING_3,
    "title": RegionType.HEADING_1,
    "subtitle": RegionType.HEADING_2,
    "paragraph": RegionType.PARAGRAPH,
    "body": RegionType.PARAGRAPH,
    "text": RegionType.PARAGRAPH,
    "table": RegionType.TABLE,
    "figure_raster": RegionType.FIGURE_RASTER,
    "figure_vector": RegionType.FIGURE_VECTOR,
    "image": RegionType.FIGURE_RASTER,
    "drawing": RegionType.FIGURE_VECTOR,
    "diagram": RegionType.FIGURE_VECTOR,
    "caption": RegionType.CAPTION,
    "running_header": RegionType.RUNNING_HEADER,
    "header": RegionType.RUNNING_HEADER,
    "page_number": RegionType.PAGE_NUMBER,
    "footnote": RegionType.FOOTNOTE,
}


LAYOUT_PROMPT = """Phân tích bố cục trang sách Trung văn (图解梅花易数). Trả về JSON list các vùng (regions).

Mỗi region phải có:
  - "type": một trong:
      "heading_1" (tựa lớn, chapter)
      "heading_2" (section heading)
      "heading_3" (sub-heading)
      "paragraph" (text đoạn văn)
      "table" (bảng có cells)
      "figure_raster" (ảnh chụp / scan / photo)
      "figure_vector" (biểu đồ, sơ đồ, ký hiệu cổ — Bát Quái, Hà Đồ, Lạc Thư)
      "caption" (chú thích dưới ảnh/bảng)
      "running_header" (tựa sách top/bottom)
      "page_number" (số trang)
      "footnote" (chú thích lề)
  - "bbox_pct": [x1, y1, x2, y2] trong khoảng 0.0-1.0 (% kích thước trang)
  - "reading_order": số thứ tự đọc (1, 2, 3...)
  - "summary": mô tả 5-15 chữ ngắn về nội dung (không phải OCR full text)

CHỈ trả JSON, không thêm text giải thích. Format:
[
  {"type": "heading_1", "bbox_pct": [0.1, 0.05, 0.9, 0.15], "reading_order": 1, "summary": "Tựa sách Mai Hoa Dịch Số"},
  {"type": "figure_raster", "bbox_pct": [0.2, 0.3, 0.8, 0.7], "reading_order": 2, "summary": "Hình Tổ sư đứng cạnh cây mai"}
]"""


def _call_qwen_vl(img_path: str | Path, prompt: str = LAYOUT_PROMPT,
                  model: str = "qwen2.5vl:7b", timeout: int = 180) -> str:
    """Call ollama qwen2.5vl with image + layout prompt."""
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
            "format": "json",  # force JSON output
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
                "num_predict": 2048,
            },
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def _parse_regions(vl_output: str) -> list[dict]:
    """Parse qwen output → list of region dicts.

    qwen format=json should return clean JSON. But also handle:
      - JSON wrapped in markdown ```json ... ```
      - Object with key like "regions" or top-level list
    """
    text = vl_output.strip()

    # Strip markdown fence if present
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        log.warning(f"JSON parse fail: {e}; raw: {text[:200]!r}")
        return []

    # Could be list or wrapped object
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("regions", "items", "results", "layout"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # Single region as dict?
        if "type" in data and "bbox_pct" in data:
            return [data]
    return []


def detect_page_vision(
    image_path: str | Path,
    page_num: int,
    *,
    book_id: str = "book",
    page_width: float = 595.0,
    page_height: float = 842.0,
    model: str = "qwen2.5vl:7b",
) -> PageLayout:
    """Detect layout dùng qwen2.5vl trên page image.

    Args:
        image_path: PNG/JPG của 1 page
        page_num: 1-indexed
        book_id: prefix region IDs
        page_width/height: PDF coords để scale bbox_pct → bbox

    Returns:
        PageLayout với regions detected.
    """
    image_path = str(image_path)
    t0 = time.time()
    log.info(f"Detecting layout (qwen-vl): {image_path}")

    raw = _call_qwen_vl(image_path, model=model)
    parsed = _parse_regions(raw)

    regions: list[Region] = []
    for idx, item in enumerate(parsed):
        # Validate
        type_str = str(item.get("type", "paragraph")).lower().strip()
        region_type = VL_TYPE_MAP.get(type_str, RegionType.PARAGRAPH)

        bbox_pct = item.get("bbox_pct", [0, 0, 1, 1])
        if not isinstance(bbox_pct, list) or len(bbox_pct) != 4:
            continue

        # Scale percentage → PDF coords
        x1 = float(bbox_pct[0]) * page_width
        y1 = float(bbox_pct[1]) * page_height
        x2 = float(bbox_pct[2]) * page_width
        y2 = float(bbox_pct[3]) * page_height

        reading_order = int(item.get("reading_order", idx + 1))
        summary = str(item.get("summary", "")).strip()

        regions.append(Region(
            id=f"{book_id}-p{page_num:04d}-r{idx+1:03d}",
            type=region_type,
            bbox=(x1, y1, x2, y2),
            reading_order=reading_order,
            source_text=None,  # Layer 3 sẽ OCR per region
            ocr_confidence=0.0,
            ocr_engine="",
            image_description=summary or None,
        ))

    # Sort by reading order
    regions.sort(key=lambda r: r.reading_order)

    # Detect template
    layout_template = _detect_template(regions, page_width)

    # Confidence — based on whether we got any regions
    score = 0.85 if len(regions) >= 2 else 0.5
    conf = LayoutConfidence.HIGH if score >= 0.85 else LayoutConfidence.MEDIUM

    elapsed = time.time() - t0
    log.info(f"  {len(regions)} regions, template={layout_template}, "
             f"elapsed={elapsed:.1f}s")

    return PageLayout(
        page_num=page_num,
        page_image=image_path,
        width=page_width,
        height=page_height,
        layout_template=layout_template,
        layout_confidence=conf,
        layout_confidence_score=score,
        detection_engine=f"qwen-vl:{model}",
        regions=regions,
        needs_review=(conf != LayoutConfidence.HIGH),
    )


def _detect_template(regions: list[Region], page_width: float) -> str:
    """Heuristic: cluster x-starts of paragraph regions."""
    paras = [r for r in regions if r.type == RegionType.PARAGRAPH]
    if len(paras) < 3:
        return "single_column"
    x_starts = [r.bbox[0] for r in paras]
    mid = page_width * 0.45
    left = sum(1 for x in x_starts if x < mid)
    right = sum(1 for x in x_starts if x >= mid)
    if left >= 2 and right >= 2:
        return "two_column"
    return "single_column"
