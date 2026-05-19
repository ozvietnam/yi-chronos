"""Visualize PageLayout: draw bbox overlay trên page image.

Mục đích: Anh visual đối chiếu detection có đúng không
— so với việc đọc raw JSON.

Output: PNG với bbox đa màu + label region type.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .schema import PageLayout, RegionType


# Color theo region type — distinguishable + meaningful
REGION_COLORS: dict[RegionType, str] = {
    RegionType.HEADING_1: "#dc2626",       # red — most prominent
    RegionType.HEADING_2: "#ea580c",       # orange
    RegionType.HEADING_3: "#d97706",       # amber
    RegionType.PARAGRAPH: "#2563eb",       # blue — body text
    RegionType.TABLE: "#7c3aed",           # purple — structured data
    RegionType.FIGURE_RASTER: "#16a34a",   # green — image
    RegionType.FIGURE_VECTOR: "#0891b2",   # teal — drawing/diagram
    RegionType.CAPTION: "#64748b",         # gray — caption
    RegionType.RUNNING_HEADER: "#94a3b8",  # slate light
    RegionType.PAGE_NUMBER: "#94a3b8",     # slate light
    RegionType.FOOTNOTE: "#a78bfa",        # violet light
}


def render_page_to_image(
    pdf_path: str | Path,
    page_num: int,
    dpi: int = 100,
) -> Image.Image:
    """Render 1 PDF page → PIL Image."""
    import fitz  # PyMuPDF

    doc = fitz.open(str(pdf_path))
    page = doc[page_num - 1]  # 0-indexed
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def draw_overlay(
    page_image: Image.Image,
    layout: PageLayout,
    *,
    show_labels: bool = True,
    show_reading_order: bool = True,
    line_width: int = 3,
    opacity: int = 80,  # 0-255 for fill
) -> Image.Image:
    """Draw bbox + label overlay lên page image.

    Bbox coords trong layout là PDF points; image là pixel.
    Scale ratio = image_width / pdf_width.
    """
    # Scale factor
    scale_x = page_image.width / layout.width if layout.width else 1
    scale_y = page_image.height / layout.height if layout.height else 1

    # Use RGBA for transparency
    img = page_image.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Try load a font
    try:
        font = ImageFont.truetype(
            "/System/Library/Fonts/Helvetica.ttc", 14
        )
        font_small = ImageFont.truetype(
            "/System/Library/Fonts/Helvetica.ttc", 11
        )
    except Exception:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    for region in layout.regions:
        color_hex = REGION_COLORS.get(region.type, "#000000")
        # Convert hex → RGB
        r, g, b = (
            int(color_hex[1:3], 16),
            int(color_hex[3:5], 16),
            int(color_hex[5:7], 16),
        )
        fill = (r, g, b, opacity)
        outline = (r, g, b, 255)

        # Scale bbox
        x1, y1, x2, y2 = region.bbox
        bbox_scaled = (
            x1 * scale_x,
            y1 * scale_y,
            x2 * scale_x,
            y2 * scale_y,
        )

        # Draw rect with semi-transparent fill + solid outline
        draw.rectangle(bbox_scaled, fill=fill, outline=outline, width=line_width)

        # Label
        if show_labels:
            label = region.type.value
            if show_reading_order:
                label = f"#{region.reading_order} {label}"
            # Background for text
            text_bbox = draw.textbbox((bbox_scaled[0] + 4, bbox_scaled[1] + 4),
                                      label, font=font_small)
            draw.rectangle(
                (text_bbox[0] - 2, text_bbox[1] - 2,
                 text_bbox[2] + 4, text_bbox[3] + 2),
                fill=(255, 255, 255, 230),
            )
            draw.text(
                (bbox_scaled[0] + 4, bbox_scaled[1] + 4),
                label, fill=outline, font=font_small,
            )

    # Composite
    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")


def make_overlay_png(
    pdf_path: str | Path,
    layout: PageLayout,
    output_path: str | Path,
    dpi: int = 100,
) -> None:
    """End-to-end: PDF page + layout → PNG overlay."""
    page_img = render_page_to_image(pdf_path, layout.page_num, dpi=dpi)
    overlay = draw_overlay(page_img, layout)
    overlay.save(str(output_path), "PNG", optimize=True)
