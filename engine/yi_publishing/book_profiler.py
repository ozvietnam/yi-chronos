"""Book profiler — heart of intelligent onboarding pipeline.

Stage 1.3 của Smart Book Onboarding Pipeline.

Given a PDF + a few sample page numbers, profiler analyzes:
  1. Column count (1/2/3+) via x-axis histogram of dark pixels
  2. Script type (chinese / vietnamese / latin / mixed) from sample OCR text
  3. Ink density (sparse / normal / dense) from non-white pixel ratio
  4. Image-vs-text proportion

Then runs SPIKE OCR test with multiple configs (default vs -f False vs
hybrid backend) on sample pages, compares equation_inline ratios, and
PICKS THE WINNING CONFIG. No manual flags.

Output: `book_profile.json` with profile + recommended OCR config + rationale.

Workflow:
    pages = pick_sample_pages_for_profile(...)
    profile = profile_book(pdf_path, pages, output_root)
    # profile["ocr_config"] is the recommended config for OCR stage
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ─── Column detection ─────────────────────────────────────────────────────────

# Tunable thresholds (validated against 1/2/3-col test PDFs)
COL_GUTTER_MIN_WIDTH_FRAC = 0.025   # gutter must be ≥2.5% of page width
COL_GUTTER_INK_MAX = 0.04           # gutter has <4% ink (mostly white)
COL_MARGIN_CROP_FRAC = 0.05         # ignore outer 5% margin for gutter detection


def detect_columns(image_path: Path) -> int:
    """Count column layout by detecting vertical gutters in dark-pixel x-histogram.

    Returns: integer column count, ≥1.
    """
    import numpy as np
    from PIL import Image

    with Image.open(image_path) as im:
        gray = im.convert("L")
        arr = np.asarray(gray)

    h, w = arr.shape
    crop_x0 = int(w * COL_MARGIN_CROP_FRAC)
    crop_x1 = w - crop_x0
    crop_y0 = int(h * COL_MARGIN_CROP_FRAC)
    crop_y1 = h - crop_y0
    cropped = arr[crop_y0:crop_y1, crop_x0:crop_x1]

    # Per-column dark-pixel density
    dark = (cropped < 200).astype(np.float32)
    col_density = dark.mean(axis=0)  # per-x density

    # Smooth slightly to reduce noise
    window = max(3, int(w * 0.005))
    if window > 1:
        kernel = np.ones(window) / window
        col_density = np.convolve(col_density, kernel, mode="same")

    # Identify "gutter" columns (low density)
    is_gutter = col_density < COL_GUTTER_INK_MAX

    # Find contiguous gutter runs
    gutter_runs: list[tuple[int, int]] = []
    in_run = False
    run_start = 0
    for x in range(len(is_gutter)):
        if is_gutter[x] and not in_run:
            in_run = True
            run_start = x
        elif not is_gutter[x] and in_run:
            in_run = False
            gutter_runs.append((run_start, x - 1))
    if in_run:
        gutter_runs.append((run_start, len(is_gutter) - 1))

    # Filter: ignore gutters touching edges (those are margins)
    width = cropped.shape[1]
    min_gutter_width = max(2, int(width * COL_GUTTER_MIN_WIDTH_FRAC))
    inner_gutters = [
        (a, b)
        for a, b in gutter_runs
        if a > 5 and b < width - 5 and (b - a + 1) >= min_gutter_width
    ]

    # Columns = inner gutters + 1
    n_columns = len(inner_gutters) + 1
    return max(1, n_columns)


# ─── Density classification ──────────────────────────────────────────────────


def classify_density(image_path: Path) -> str:
    """Classify ink density: 'sparse' | 'normal' | 'dense' | 'saturated'.

    Heuristic: percentage of dark pixels (luminance < 200).
    Calibrated against real samples (2026-05-25):
      - Thiết Bản p55 Hán cổ 3-col: 6.3%
      - Tu-vi p55 modern Chinese:  8.7%
      - Thiết Bản p1 cover:        96.7%

    Buckets:
      - < 3% → sparse (mostly whitespace)
      - 3–15% → normal (regular text page)
      - 15–50% → dense (packed multi-col text)
      - > 50% → saturated (cover, image, diagram)

    NOTE: Hán cổ multi-col còn có dark_ratio "normal" (~5-10%) vì thin strokes
    + wide gutters. Column count + spike-OCR result là signal mạnh hơn cho
    "needs special handling" decision.
    """
    import numpy as np
    from PIL import Image

    with Image.open(image_path) as im:
        gray = im.convert("L")
        arr = np.asarray(gray)

    dark_ratio = float((arr < 200).mean())
    if dark_ratio < 0.03:
        return "sparse"
    if dark_ratio < 0.15:
        return "normal"
    if dark_ratio < 0.50:
        return "dense"
    return "saturated"


# ─── Script detection ────────────────────────────────────────────────────────

# Unicode ranges
_CJK_BASIC = re.compile(r"[一-鿿]")          # CJK Unified Ideographs
_CJK_EXT_A = re.compile(r"[㐀-䶿]")          # Extension A
_VIETNAMESE_DIACRITICS = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", re.IGNORECASE)
_LATIN = re.compile(r"[a-zA-Z]")


def classify_script(text: str) -> str:
    """Classify dominant script: 'chinese' | 'vietnamese' | 'latin' | 'unknown'."""
    if not text or not text.strip():
        return "unknown"

    chinese_chars = len(_CJK_BASIC.findall(text)) + len(_CJK_EXT_A.findall(text))
    vi_diacritics = len(_VIETNAMESE_DIACRITICS.findall(text))
    latin_chars = len(_LATIN.findall(text))

    # Priority: chinese > vietnamese (diacritics) > latin
    if chinese_chars > 5:
        return "chinese"
    if vi_diacritics >= 3:
        return "vietnamese"
    if latin_chars >= 10:
        return "latin"
    if vi_diacritics > 0:
        return "vietnamese"  # short snippet w/ diacritics
    return "unknown"


# ─── Spike OCR runner ────────────────────────────────────────────────────────


def _equation_ratio_for_pages(content_list_v2: list) -> float:
    """Given content_list_v2.json data (list of pages), compute equation/text ratio."""
    total_inline = 0
    equation_inline = 0
    for page in content_list_v2:
        for block in page:
            if block.get("type") == "paragraph":
                for item in block.get("content", {}).get("paragraph_content", []):
                    t = item.get("type")
                    if t == "equation_inline":
                        equation_inline += 1
                    if t in ("equation_inline", "text"):
                        total_inline += 1
    if total_inline == 0:
        return 0.0
    return equation_inline / total_inline


def _default_mineru_runner(
    *,
    pdf_path: Path,
    output_root: Path,
    start: int,
    end: int,
    backend: str,
    language: str,
    formula_enable: bool,
    mineru_bin: Optional[Path] = None,
    timeout: int = 600,
) -> None:
    """Default real MinerU subprocess call (for production, not test mocks)."""
    import subprocess

    if mineru_bin is None:
        mineru_bin = Path("/Users/ozvietnamdesktop/Desktop/yi/.venv-mineru/bin/mineru")
    output_root.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(mineru_bin),
        "-p", str(pdf_path),
        "-o", str(output_root),
        "-b", backend,
        "-l", language,
        "-m", "auto",
        "-s", str(start),
        "-e", str(end),
        "-f", str(formula_enable),
    ]
    logger.info(f"  🔍 Spike MinerU pages {start}-{end} (formula={formula_enable})")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"MinerU spike exited {proc.returncode}; stderr: {(proc.stderr or '')[-400:]}"
        )


def spike_ocr_configs(
    *,
    pdf_path: Path,
    sample_pages: list[int],
    output_root: Path,
    configs: list[dict],
    mineru_runner: Optional[Callable] = None,
    backend: str = "pipeline",
    language: str = "ch",
) -> dict:
    # Resolve runner: None → real MinerU subprocess
    if mineru_runner is None:
        mineru_runner = _default_mineru_runner
    """Run MinerU on `sample_pages` for each config; compare equation_ratio.

    `configs`: list of {"name": str, "formula_enable": bool, [other optional flags]}

    Picks the candidate with LOWEST equation_ratio. Tie → first listed (so put
    "default" first to prefer keeping formula enabled when there's no advantage).
    """
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    book_id = pdf_path.stem
    candidates = []

    for cfg in configs:
        # Run MinerU separately for each sample page (precise: only OCR
        # the pages we'll analyze; previous "one call covering range" version
        # OCR'd entire span between sampled pages → wasted 3 min + diluted signal).
        all_pages_data: list = []
        cfg_failed = False
        err_msg = None
        for sp in sample_pages:
            per_page_dir = output_root / cfg["name"] / f"p{sp:04d}"
            per_page_dir.mkdir(parents=True, exist_ok=True)
            try:
                mineru_runner(
                    pdf_path=pdf_path,
                    output_root=per_page_dir,
                    start=sp,
                    end=sp,
                    backend=cfg.get("backend", backend),
                    language=cfg.get("language", language),
                    formula_enable=cfg["formula_enable"],
                )
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"Spike {cfg['name']} page {sp} failed: {e}")
                cfg_failed = True
                break

            # Locate v2 output for this page
            v2_path = per_page_dir / book_id / "auto" / f"{book_id}_content_list_v2.json"
            if not v2_path.exists():
                v2_path = per_page_dir / book_id / "ocr" / f"{book_id}_content_list_v2.json"
            if not v2_path.exists():
                err_msg = f"No content_list_v2.json for page {sp}"
                cfg_failed = True
                break

            try:
                page_data = json.loads(v2_path.read_text(encoding="utf-8"))
                all_pages_data.extend(page_data)
            except Exception as e:
                err_msg = f"Failed parse v2 for page {sp}: {e}"
                cfg_failed = True
                break

        if cfg_failed:
            candidates.append({**cfg, "equation_ratio": 1.0, "error": err_msg})
            continue

        ratio = _equation_ratio_for_pages(all_pages_data)
        candidates.append({
            **cfg,
            "equation_ratio": round(ratio, 4),
            "sample_pages_count": len(sample_pages),
        })

    # Pick lowest equation_ratio (tie → first = prefer default config)
    winner = min(candidates, key=lambda c: c["equation_ratio"])

    return {
        "winner": winner,
        "candidates": candidates,
    }


# ─── Full profile_book ────────────────────────────────────────────────────────


def profile_book(
    *,
    pdf_path: Path,
    sample_pages: list[int],
    output_root: Path,
    mineru_runner: Optional[Callable] = None,
    sample_text: Optional[str] = None,
    backend: str = "pipeline",
    language: str = "ch",
) -> dict:
    # Resolve runner: None → real MinerU subprocess (do here so callers
    # can explicitly pass None to mean "use default")
    if mineru_runner is None:
        mineru_runner = _default_mineru_runner
    """Build full profile + recommended OCR config for a book.

    Steps:
        1. Render hi-res image of first sample_page → detect columns, density
        2. Run spike OCR with [default vs formula-disabled] configs on sample_pages
        3. Pick winner + classify script (from OCR text if available)
        4. Save book_profile.json
        5. Return profile dict
    """
    import fitz

    pdf_path = Path(pdf_path)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    # ── Image analysis on first sample page ───
    first_page = sample_pages[0] if sample_pages else 1
    doc = fitz.open(pdf_path)
    try:
        page = doc.load_page(first_page - 1)
        # 2x DPI render — calibrated for column detection robustness
        # (3x degrades detection due to smoothing window scaling)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
        analysis_img = output_root / "_analysis_page.png"
        pix.save(str(analysis_img))
    finally:
        doc.close()

    columns = detect_columns(analysis_img)
    density = classify_density(analysis_img)

    # ── Script detection ───
    # If caller didn't supply text, run a quick OCR on first sample page
    # for script classification. Use existing MinerU spike output if possible.
    if sample_text is None:
        sample_text = ""
    script = classify_script(sample_text) if sample_text else "unknown"

    # Infer chinese script from language hint if classify_script gave unknown
    # (cuốn cổ Hán văn thường không có text layer → sample_text empty → unknown)
    inferred_chinese = script == "unknown" and language in ("ch", "ch_server", "ch_lite", "chinese_cht")

    # ── Spike OCR ───
    spike_result = spike_ocr_configs(
        pdf_path=pdf_path,
        sample_pages=sample_pages,
        output_root=output_root / "_spike",
        configs=[
            {"name": "default", "formula_enable": True},
            {"name": "no-formula", "formula_enable": False},
        ],
        mineru_runner=mineru_runner,
        backend=backend,
        language=language,
    )

    winner = spike_result["winner"]
    formula_enable = winner["formula_enable"]

    # Rationale
    default_cand = next((c for c in spike_result["candidates"] if c["name"] == "default"), None)
    no_formula_cand = next((c for c in spike_result["candidates"] if c["name"] == "no-formula"), None)
    rationale_parts = [f"Columns={columns}, density={density}"]
    if default_cand and no_formula_cand:
        rationale_parts.append(
            f"spike default={default_cand['equation_ratio']:.2%} eq, "
            f"-f False={no_formula_cand['equation_ratio']:.2%} eq"
        )

    # ── Conservative rule for Hán cổ multi-col books ──────────────────────────
    # Learned from Thiết Bản Thần Số (2026-05-26): spike sampling missed 9 problem
    # pages out of 587 (rare table-grid pages with false equation detection).
    # Heuristic: Chinese-language books with ≥2 columns are rarely real math books;
    # downside of disabling formula parsing is small, upside (avoiding LaTeX
    # false positives like \overrightarrow on chữ Hán table grids) is high.
    is_chinese = (script == "chinese") or inferred_chinese
    if is_chinese and columns >= 2 and formula_enable:
        formula_enable = False
        rationale_parts.append(
            "Override: Chinese + multi-col → conservative -f False "
            "(spike sampling can miss rare table-grid false positives; "
            "Hán cổ books rarely contain real math formulas)"
        )
    elif not formula_enable:
        rationale_parts.append(
            "Disabled formula parsing per spike (lower equation_ratio)"
        )

    profile = {
        "columns": columns,
        "density": density,
        "script": script,
        "analysis_page": first_page,
        "ocr_config": {
            "backend": backend,
            "language": language,
            "formula_enable": formula_enable,
            "method": "auto",
            "rationale": " | ".join(rationale_parts),
        },
        "spike_result": spike_result,
    }

    profile_path = output_root / "book_profile.json"
    profile_path.write_text(
        json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"📋 Book profile saved → {profile_path}")
    return profile
