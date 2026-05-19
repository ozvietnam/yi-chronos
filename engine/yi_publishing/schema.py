"""Canonical schema cho layout-aware book pipeline.

8 region types (Anh chỉ 2026-05-18 — paradigm shift #5):
    Em đã miss FIGURE_VECTOR + CAPTION trong Q3 → 48 placeholder errors cascading.
    Schema này enforces explicit type per region từ Bước 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Any
import json
from pathlib import Path


class RegionType(str, Enum):
    """8 region types — đầy đủ cho sách Đông phương + sách hiện đại."""

    # ── Text content ──
    HEADING_1 = "heading_1"  # Chapter / Phần
    HEADING_2 = "heading_2"  # Section / Mục
    HEADING_3 = "heading_3"  # Sub-section
    PARAGRAPH = "paragraph"  # Body text

    # ── Visual content (KHÔNG OCR text — giữ nguyên image) ──
    FIGURE_RASTER = "figure_raster"  # Ảnh chụp / scan thật
    FIGURE_VECTOR = "figure_vector"  # Đồ hình, biểu tượng cổ (Bát Quái, Hà Đồ, Lạc Thư)

    # ── Tables ──
    TABLE = "table"  # Markdown-style với cells + headers

    # ── Auxiliary ──
    CAPTION = "caption"  # Text dưới ảnh/bảng
    RUNNING_HEADER = "running_header"  # Tựa sách top/bottom
    FOOTNOTE = "footnote"  # Chú thích, lề
    PAGE_NUMBER = "page_number"  # Số trang


class LayoutConfidence(str, Enum):
    """Confidence cấp trang — flag cho human review."""
    HIGH = "high"          # ≥ 0.90  — auto-pass
    MEDIUM = "medium"      # 0.70-0.90 — review nếu có time
    LOW = "low"            # < 0.70  — BẮT BUỘC human review


class TranslationStatus(str, Enum):
    """Region-level translation lifecycle."""
    PENDING = "pending"
    AUTO = "auto"          # LLM draft
    DRAFT = "draft"        # Human-edited draft
    REVIEWED = "reviewed"  # Reviewer pass
    APPROVED = "approved"  # Final, locked


@dataclass
class Region:
    """Một region trong layout của 1 page.

    Iron Rule: bbox là bất biến sau khi layout detection.
    Re-OCR có thể đổi source_text. Re-translate có thể đổi translation.
    KHÔNG ĐƯỢC đổi bbox/type sau khi đã commit layout.
    """

    id: str  # vd "book123-p020-r02"
    type: RegionType
    bbox: tuple[float, float, float, float]  # (x1, y1, x2, y2) in PDF coords
    reading_order: int  # 1, 2, 3... thứ tự đọc trên page
    column: int = 1  # 1 = single, 1/2 = 2-col, etc.

    # OCR layer
    source_text: Optional[str] = None  # None cho figure types
    ocr_confidence: float = 0.0
    ocr_engine: str = ""

    # Image layer (cho figure_raster / figure_vector)
    image_crop: Optional[str] = None  # path relative to book root
    image_description: Optional[str] = None  # AI-generated mô tả ngắn

    # Translation layer
    translation_vi: Optional[str] = None
    translation_status: TranslationStatus = TranslationStatus.PENDING
    translator: Optional[str] = None  # model name hoặc human ID
    reviewer: Optional[str] = None
    translation_version: int = 0  # tăng mỗi lần update

    # Metadata
    notes: list[str] = field(default_factory=list)  # editorial notes
    flags: list[str] = field(default_factory=list)  # vd ["needs_redraw", "ambiguous"]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        d["translation_status"] = self.translation_status.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Region":
        d = dict(d)
        d["type"] = RegionType(d["type"])
        d["translation_status"] = TranslationStatus(
            d.get("translation_status", "pending")
        )
        d["bbox"] = tuple(d["bbox"])
        return cls(**d)


@dataclass
class PageLayout:
    """Layout của 1 page — Layer 2 của pipeline."""

    page_num: int  # 1-indexed page number trong sách gốc
    page_image: str  # path tới raw image (Layer 1)
    width: float  # PDF page width in points
    height: float  # PDF page height in points

    language_source: str = "zh-Hans"
    language_target: str = "vi"
    layout_template: str = "single_column"  # vd "two_column", "three_column"
    layout_confidence: LayoutConfidence = LayoutConfidence.HIGH
    layout_confidence_score: float = 1.0  # raw 0-1 từ detection model
    detection_engine: str = ""  # vd "unstructured-hi_res"

    regions: list[Region] = field(default_factory=list)

    # QA flags
    needs_review: bool = False
    review_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["regions"] = [r.to_dict() for r in self.regions]
        d["layout_confidence"] = self.layout_confidence.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PageLayout":
        d = dict(d)
        d["regions"] = [Region.from_dict(r) for r in d.get("regions", [])]
        d["layout_confidence"] = LayoutConfidence(
            d.get("layout_confidence", "high")
        )
        return cls(**d)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "PageLayout":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    # Convenience
    def regions_by_type(self, t: RegionType) -> list[Region]:
        return [r for r in self.regions if r.type == t]

    def figure_count(self) -> int:
        return len([
            r for r in self.regions
            if r.type in (RegionType.FIGURE_RASTER, RegionType.FIGURE_VECTOR)
        ])


@dataclass
class BookLayout:
    """Layout của toàn cuốn sách — index của pages."""

    book_id: str  # vd "thieu-khang-tiet-tq"
    title_zh: str
    title_vi: str
    author: str
    total_pages: int
    pages_dir: str  # folder chứa per-page PageLayout JSONs

    pages_processed: int = 0
    pages_needing_review: int = 0

    detection_engine: str = ""
    created_at: float = 0.0  # unix timestamp

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "BookLayout":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))
