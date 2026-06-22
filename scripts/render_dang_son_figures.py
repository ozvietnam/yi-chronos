#!/usr/bin/env python3
"""Render 4 đồ hình Đằng Sơn (SVG trong do-hinh-dang-son.html) → PNG nhúng sách PDF.

cairosvg KHÔNG hỗ trợ CSS var() → phải strip `var(--x, fallback)` → `fallback`
trước khi render. cairosvg CÓ áp <style> class + marker/arc (đã test 2026-06-22).

    python3 scripts/render_dang_son_figures.py
"""
from __future__ import annotations

import re
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs/books/tu-vi-sieu-tri-tue/do-hinh-dang-son.html"
OUT = ROOT / "docs/books/tu-vi-sieu-tri-tue/figures"

# Tên file PNG theo thứ tự SVG xuất hiện trong HTML
NAMES = [
    "fig1-dia-ban-12-cung",
    "fig2-ngu-hanh-ngu-giac",
    "fig3-dia-ban-thien-van",
    "fig4-14-chinh-tinh",
]


def strip_var(svg: str) -> str:
    """`var(--token, fallback)` → `fallback` (cairosvg không hiểu var())."""
    return re.sub(r"var\((?:[^,()]+),\s*([^()]+)\)", r"\1", svg)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    html = HTML.read_text(encoding="utf-8")
    svgs = re.findall(r"<svg\b.*?</svg>", html, re.DOTALL)
    print(f"Tìm thấy {len(svgs)} SVG trong {HTML.name}")
    for i, svg in enumerate(svgs):
        name = NAMES[i] if i < len(NAMES) else f"fig{i}"
        png = OUT / f"{name}.png"
        cairosvg.svg2png(
            bytestring=strip_var(svg).encode("utf-8"),
            write_to=str(png),
            output_width=1400,  # 2x cho in A5 nét
        )
        print(f"  ✅ {png.name}: {png.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
