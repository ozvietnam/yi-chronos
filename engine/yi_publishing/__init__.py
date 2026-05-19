"""YI Publishing — Layout-aware book digitization pipeline.

Paradigm Shift #5 (2026-05-18, Anh):
    "Trong bước quét OCR phải nhận biết được các khung bố cục:
     đoạn văn, khung ảnh, khung tranh vẽ. Làm ẩu ngay từ bước 1,
     đọc 1 trang sách không nhìn thấy bố cục, thì xuất bản làm sao?"

Pipeline (Bookflow v3.0 — Layered Output):
    Layer 1 — Raw images          (immutable, PNG/TIFF per page)
    Layer 2 — Layout JSON         (bbox + region types, no text)
    Layer 3 — OCR per region      (source text per region)
    Layer 4 — Translation         (target text per region)
    Layer 5 — Rendered output     (PDF/HTML/EPUB preserving layout)

Each layer NEVER modifies a deeper layer. Re-OCR a region without
re-running layout detection. Re-translate without re-OCR.

Modules:
    schema       — Region/Page dataclasses (8 region types)
    layout_detector — Detect regions per page (wrap unstructured)
    region_ocr   — OCR per region with type-aware tool selection
    compiler     — Reassemble layered JSON → output formats

Spec: docs/BOOKFLOW-V3-LAYOUT-FIRST.md
"""

from .schema import (
    RegionType,
    Region,
    PageLayout,
    BookLayout,
    LayoutConfidence,
)

__all__ = [
    "RegionType",
    "Region",
    "PageLayout",
    "BookLayout",
    "LayoutConfidence",
]

__version__ = "0.1.0"  # Draft — chờ Anh duyệt từng bước
