"""YI-Lexicon Restoration — phục chế sách scan thành bản đẹp.

Phase A (Conservative, 2026-05-12):
- Pipeline: pdftoppm → tesseract OCR → DeepSeek cleanup → Markdown + manifest
- Hình vẽ: extract (chưa redraw) — placeholder vào markdown
- Output: Markdown + WikiLinks tới Lexicon concepts
- Policy: NỘI BỘ, không phân phối, allow_download=0 mặc định

Future (Phase B/C):
- Backends pluggable: olmOCR, MinerU, Surya
- Vision LLM redraw diagrams → SVG
- Real-ESRGAN upscale hình vẽ
"""

from .pipeline import restore_book, RestorationResult, RestorationConfig
from .manifest import (
    BookManifest, BookSection, BookPage, BookFigure,
    save_manifest, load_manifest,
)
from .plan import (
    RestorationPlan, PlanBatch,
    create_plan, load_plan, save_plan,
    mark_batch, advance_phase, append_log,
)

__all__ = [
    "restore_book",
    "RestorationResult",
    "RestorationConfig",
    "BookManifest",
    "BookSection",
    "BookPage",
    "BookFigure",
    "save_manifest",
    "load_manifest",
    "RestorationPlan",
    "PlanBatch",
    "create_plan",
    "load_plan",
    "save_plan",
    "mark_batch",
    "advance_phase",
    "append_log",
]
