"""Figure extraction from scanned PDFs.

Phase A: extract embedded images via PyMuPDF if available. If a page contains
a large image OR has whitespace ratio suggesting a figure region, save as
`figures/fig-<page>-<n>.png`. Mark figure_type='image' (no classification yet).

Phase B (later): Real-ESRGAN upscale + vision LLM classify (Hà Đồ, Lạc Thư,
Bát Quái...) + redraw priority diagrams as SVG.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PageFigures:
    page: int
    figure_paths: list[str] = field(default_factory=list)  # absolute paths
    errors: list[str] = field(default_factory=list)


def extract_figures_from_page(
    pdf_path: Path,
    page_number: int,        # 1-based
    output_dir: Path,
    *,
    min_pixel_area: int = 40_000,  # filter tiny logos
) -> PageFigures:
    """Extract embedded images on a specific page via PyMuPDF (if installed).

    If PyMuPDF unavailable → returns empty figures list (graceful).
    """
    result = PageFigures(page=page_number)
    try:
        import fitz  # type: ignore  # PyMuPDF
    except ImportError:
        result.errors.append("PyMuPDF (fitz) not installed — figures not extracted")
        return result

    try:
        doc = fitz.open(str(pdf_path))
        if page_number < 1 or page_number > doc.page_count:
            result.errors.append(f"page {page_number} out of range (1..{doc.page_count})")
            doc.close()
            return result
        page = doc[page_number - 1]
        images = page.get_images(full=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        for idx, img_info in enumerate(images, start=1):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.width * pix.height < min_pixel_area:
                    pix = None
                    continue
                # Convert CMYK → RGB if needed
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                out_path = output_dir / f"fig-{page_number:04d}-{idx}.png"
                pix.save(str(out_path))
                pix = None
                result.figure_paths.append(str(out_path))
            except Exception as e:
                result.errors.append(f"fig {idx}: {e}")
        doc.close()
    except Exception as e:
        result.errors.append(f"fitz open error: {e}")
    return result
