#!/usr/bin/env python3
"""Compile 《Tử Vi Tính Được》 → PDF xuất bản (bookflow Iron #5, Stage 6).

Pipeline chuẩn nhà: markdown (7 phần + 2 phụ lục) → pandoc → HTML5 → WeasyPrint → PDF A5.
Tái dùng pattern scripts/export_master_pdf.py (pandoc+WeasyPrint) nhưng CSS sách (serif,
@page đánh số trang, TOC clickable). Chạy từ Mac (pandoc + weasyprint đã có).

    python3 scripts/compile_tu_vi_sieu_tri_tue.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "docs/books/tu-vi-sieu-tri-tue"
OUT = ROOT / "data/published"

# Thứ tự chương (mục lục KHÔNG nhồi vào — pandoc tự sinh TOC từ heading)
PARTS = [
    "phan-0-tuyen-ngon.md",
    "phan-1-nen-toan-hoc.md",
    "phan-2-14-sao-toan-tu.md",
    "phan-3-dong-dang.md",
    "phan-4-bien-dong-luc.md",
    "phan-5-gioi-han.md",
    "phan-6-dong-hanh.md",
    "phu-luc-a-ky-hieu.md",
    "phu-luc-b-doi-chieu.md",
]

CSS = """
@page { size: A5; margin: 1.8cm 1.6cm 2cm 1.6cm;
  @bottom-center { content: counter(page); color:#9a7b3a; font-size:9pt; } }
@page :first { @bottom-center { content: ""; } }
body { font-family: Georgia, "Times New Roman", "Noto Serif", serif;
  color:#2b2b2b; line-height:1.62; font-size:10.5pt; text-align:justify; }
h1 { color:#ba4d00; font-size:18pt; border-bottom:2px solid #ba4d00;
  padding-bottom:.25em; margin:1.4em 0 .6em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { color:#806000; font-size:13.5pt; border-bottom:1px solid #e6b843;
  padding-bottom:.15em; margin:1.2em 0 .5em; }
h3 { color:#806000; font-size:11.5pt; margin:1em 0 .4em; }
blockquote { border-left:4px solid #d9a449; background:#fff9e3;
  padding:.7em 1em; margin:1em 0; font-style:italic; color:#5a4a2a; }
table { border-collapse:collapse; width:100%; margin:1em 0; font-size:9pt; }
th,td { border:1px solid #ddd; padding:.4em .5em; vertical-align:top; }
th { background:#fff3d6; color:#806000; }
em { color:#446690; font-style:italic; } strong { color:#ba4d00; }
code { background:#f4efe6; padding:.05em .3em; border-radius:3px; font-size:9pt; }
hr { border:none; border-top:1px solid #e0d4b8; margin:1.5em 0; }
#TOC { page-break-after: always; }
#TOC ul { list-style:none; } #TOC a { color:#806000; text-decoration:none; }
"""

COVER = """---
title: "TỬ VI TÍNH ĐƯỢC"
subtitle: "Hoàn Toàn Khoa Học — Phiên bản Siêu Trí Tuệ AI · Tính được cái TÍNH, không tính sự VẬN HÀNH"
author: "Anh (founder) + AI · YI-CHRONOS — Nhà xuất bản Đông phương học AI-driven · kế thừa TS. Đằng Sơn"
date: "{date}"
lang: vi
---

"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = [p for p in PARTS if not (BOOK / p).exists()]
    if missing:
        print("THIẾU file:", missing); return 1

    master = COVER.format(date=datetime.now().strftime("%d/%m/%Y"))
    for p in PARTS:
        master += (BOOK / p).read_text(encoding="utf-8") + "\n\n"

    with tempfile.TemporaryDirectory() as td:
        md = Path(td) / "master.md"
        html = Path(td) / "master.html"
        css = Path(td) / "book.css"
        md.write_text(master, encoding="utf-8")
        css.write_text(CSS, encoding="utf-8")

        subprocess.run([
            "pandoc", str(md), "-o", str(html),
            "--from", "markdown+pipe_tables+blank_before_blockquote+yaml_metadata_block+tex_math_dollars",
            "--to", "html5", "--standalone", "--toc", "--toc-depth", "2",
            "--metadata", "lang=vi", "--css", str(css),
        ], check=True)

        out_pdf = OUT / "Tu-Vi-Tinh-Duoc-v0.2.pdf"
        from weasyprint import HTML
        HTML(filename=str(html)).write_pdf(str(out_pdf))
        size_kb = out_pdf.stat().st_size // 1024
        print(f"✅ PDF: {out_pdf}  ({size_kb} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
