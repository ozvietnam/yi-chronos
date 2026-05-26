"""Tests for engine.yi_publishing.book_profiler.

The profiler is the heart of "bộ dịch thông minh": auto-detect book
characteristics (columns, script, density) + spike-test multiple OCR
configs to pick the best one, all WITHOUT manual flags.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def pdf_3col_dense(tmp_path: Path) -> Path:
    """Synthesize a Hán-cổ-like 3-column dense page."""
    import fitz

    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    # 3 columns of dense vertical text
    for col in range(3):
        x = 80 + col * 170
        for row in range(40):
            y = 100 + row * 18
            p.insert_text((x, y), "甲乙丙丁戊己庚辛壬", fontsize=12)
    out = tmp_path / "3col.pdf"
    doc.save(out)
    doc.close()
    return out


@pytest.fixture
def pdf_1col(tmp_path: Path) -> Path:
    """Single-column modern text page."""
    import fitz

    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    for row in range(30):
        y = 80 + row * 22
        p.insert_text(
            (60, y),
            "This is a single column of modern text flowing across the page width.",
            fontsize=11,
        )
    out = tmp_path / "1col.pdf"
    doc.save(out)
    doc.close()
    return out


@pytest.fixture
def pdf_2col(tmp_path: Path) -> Path:
    """Two-column layout page."""
    import fitz

    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    for col in range(2):
        x = 60 + col * 270
        for row in range(35):
            y = 80 + row * 20
            p.insert_text((x, y), "Lorem ipsum dolor sit amet", fontsize=10)
    out = tmp_path / "2col.pdf"
    doc.save(out)
    doc.close()
    return out


def _render(pdf_path: Path, tmp_path: Path, page_num: int = 1) -> Path:
    """Render single page to PNG at higher resolution for analysis."""
    import fitz

    out = tmp_path / f"render_{pdf_path.stem}_p{page_num}.png"
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    pix.save(str(out))
    doc.close()
    return out


# ─── Column detection ─────────────────────────────────────────────────────────


def test_detect_columns_one_col(pdf_1col: Path, tmp_path: Path):
    from engine.yi_publishing.book_profiler import detect_columns

    img = _render(pdf_1col, tmp_path)
    n = detect_columns(img)
    assert n == 1


def test_detect_columns_two_col(pdf_2col: Path, tmp_path: Path):
    from engine.yi_publishing.book_profiler import detect_columns

    img = _render(pdf_2col, tmp_path)
    n = detect_columns(img)
    assert n == 2


def test_detect_columns_three_col(pdf_3col_dense: Path, tmp_path: Path):
    from engine.yi_publishing.book_profiler import detect_columns

    img = _render(pdf_3col_dense, tmp_path)
    n = detect_columns(img)
    assert n == 3


# ─── Ink density classification ──────────────────────────────────────────────


def test_density_returns_valid_label(pdf_1col: Path, tmp_path: Path):
    from engine.yi_publishing.book_profiler import classify_density

    img = _render(pdf_1col, tmp_path)
    d = classify_density(img)
    assert d in ("sparse", "normal", "dense", "saturated")


def test_density_saturated_for_full_fill(tmp_path: Path):
    """A completely filled page should classify as 'saturated'."""
    import fitz
    from engine.yi_publishing.book_profiler import classify_density

    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    p.draw_rect(p.rect, color=(0, 0, 0), fill=(0.2, 0.2, 0.2))
    pdf = tmp_path / "filled.pdf"
    doc.save(pdf)
    doc.close()
    img = _render(pdf, tmp_path)
    assert classify_density(img) in ("dense", "saturated")


# ─── Script detection ─────────────────────────────────────────────────────────


def test_script_classical_chinese_from_chars():
    from engine.yi_publishing.book_profiler import classify_script

    sample = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥"
    s = classify_script(sample)
    assert s == "chinese"


def test_script_modern_chinese_with_simplified():
    from engine.yi_publishing.book_profiler import classify_script

    sample = "这是一段现代汉语文本，用来测试"
    s = classify_script(sample)
    assert s == "chinese"


def test_script_vietnamese():
    from engine.yi_publishing.book_profiler import classify_script

    sample = "Đây là tiếng Việt với dấu thanh và chữ đặc biệt như ơ ư ă"
    s = classify_script(sample)
    assert s == "vietnamese"


def test_script_english():
    from engine.yi_publishing.book_profiler import classify_script

    sample = "This is plain English text for testing classification"
    s = classify_script(sample)
    assert s == "latin"


def test_script_mixed_unknown():
    from engine.yi_publishing.book_profiler import classify_script

    s = classify_script("")
    assert s == "unknown"


# ─── Spike OCR comparison ────────────────────────────────────────────────────


@pytest.fixture
def mock_mineru_factory():
    """Factory creating mock MinerU subprocess.run that emits configurable
    equation_ratio per config."""

    def make(equation_ratios: dict[str, float]):
        """equation_ratios: {"with_formula": 0.26, "without_formula": 0.0}"""

        calls = []

        def runner(*, pdf_path, output_root, start, end, backend, language, formula_enable, **kwargs):
            calls.append({
                "start": start, "end": end,
                "formula_enable": formula_enable,
            })
            # Synthesize content_list_v2.json with controlled equation_ratio
            key = "with_formula" if formula_enable else "without_formula"
            ratio = equation_ratios.get(key, 0.0)

            book_id = pdf_path.stem
            out_auto = output_root / book_id / "auto"
            out_auto.mkdir(parents=True, exist_ok=True)
            pages_data = []
            for _ in range(start, end + 1):
                # Build a paragraph with mixed text + equations based on ratio
                n_items = 20
                n_eq = int(n_items * ratio)
                content_items = []
                for i in range(n_items):
                    if i < n_eq:
                        content_items.append({"type": "equation_inline", "content": "x"})
                    else:
                        content_items.append({"type": "text", "content": "甲乙"})
                pages_data.append([{
                    "type": "paragraph",
                    "content": {"paragraph_content": content_items},
                    "bbox": [0, 0, 100, 100],
                }])
            (out_auto / f"{book_id}_content_list_v2.json").write_text(
                json.dumps(pages_data, ensure_ascii=False), encoding="utf-8"
            )

        return runner, calls

    return make


def test_spike_picks_config_with_lower_equation_ratio(pdf_3col_dense, mock_mineru_factory, tmp_path):
    from engine.yi_publishing.book_profiler import spike_ocr_configs

    runner, calls = mock_mineru_factory({
        "with_formula": 0.30,    # 30% false positives
        "without_formula": 0.0,
    })

    result = spike_ocr_configs(
        pdf_path=pdf_3col_dense,
        sample_pages=[1],
        output_root=tmp_path / "spike",
        configs=[
            {"name": "default", "formula_enable": True},
            {"name": "no-formula", "formula_enable": False},
        ],
        mineru_runner=runner,
    )

    assert result["winner"]["name"] == "no-formula"
    assert result["winner"]["equation_ratio"] == 0.0
    # Both configs were tried
    assert len(result["candidates"]) == 2


def test_spike_picks_default_when_no_false_positives(pdf_1col, mock_mineru_factory, tmp_path):
    """If both configs are equal, prefer default (formula_enable=True) since
    some books actually contain real math."""
    from engine.yi_publishing.book_profiler import spike_ocr_configs

    runner, _ = mock_mineru_factory({
        "with_formula": 0.0,
        "without_formula": 0.0,
    })

    result = spike_ocr_configs(
        pdf_path=pdf_1col,
        sample_pages=[1],
        output_root=tmp_path / "spike",
        configs=[
            {"name": "default", "formula_enable": True},
            {"name": "no-formula", "formula_enable": False},
        ],
        mineru_runner=runner,
    )
    assert result["winner"]["name"] == "default"


# ─── Full profile_book ────────────────────────────────────────────────────────


def test_profile_book_dense_classical_chinese(pdf_3col_dense, mock_mineru_factory, tmp_path):
    from engine.yi_publishing.book_profiler import profile_book

    runner, _ = mock_mineru_factory({
        "with_formula": 0.40,
        "without_formula": 0.0,
    })

    profile = profile_book(
        pdf_path=pdf_3col_dense,
        sample_pages=[1],
        output_root=tmp_path / "profile",
        mineru_runner=runner,
    )

    assert profile["columns"] == 3
    assert profile["density"] in ("sparse", "normal", "dense")
    assert profile["ocr_config"]["formula_enable"] is False  # spike-derived
    assert "rationale" in profile["ocr_config"]
    # Profile JSON saved to disk
    assert (tmp_path / "profile" / "book_profile.json").exists()


def test_profile_book_modern_single_col_keeps_default_config(pdf_1col, mock_mineru_factory, tmp_path):
    from engine.yi_publishing.book_profiler import profile_book

    runner, _ = mock_mineru_factory({
        "with_formula": 0.0,
        "without_formula": 0.0,
    })

    profile = profile_book(
        pdf_path=pdf_1col,
        sample_pages=[1],
        output_root=tmp_path / "profile",
        mineru_runner=runner,
    )

    assert profile["columns"] == 1
    # No false-positive equations → keep formula enabled
    assert profile["ocr_config"]["formula_enable"] is True


def test_profile_chinese_multicol_forces_no_formula_even_if_spike_clean(
    pdf_3col_dense, mock_mineru_factory, tmp_path
):
    """Conservative rule: Hán cổ multi-col → -f False regardless of spike result.

    Spike can miss rare table-grid pages with false-positive equation detection
    (as found with Thiết Bản Thần Số: 9/587 pages had issues, none sampled).
    """
    from engine.yi_publishing.book_profiler import profile_book

    # Both configs clean — spike would normally pick "default" (formula_enable=True)
    runner, _ = mock_mineru_factory({
        "with_formula": 0.0,
        "without_formula": 0.0,
    })

    profile = profile_book(
        pdf_path=pdf_3col_dense,
        sample_pages=[1],
        output_root=tmp_path / "profile",
        mineru_runner=runner,
        language="ch",  # explicit Chinese hint
    )

    assert profile["columns"] == 3
    # Conservative override should kick in despite clean spike
    assert profile["ocr_config"]["formula_enable"] is False
    assert "Override" in profile["ocr_config"]["rationale"]
