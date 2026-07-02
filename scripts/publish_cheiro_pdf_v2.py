#!/usr/bin/env python3
"""Publish Cheiro (core) → PDF v0.2 — design pass WeasyPrint chuẩn nhà (đóng nợ #30).

v0.1 (reportlab) là DRAFT vì môi trường cloud thiếu pandoc/WeasyPrint. Bản này chạy từ
Mac (pandoc 3.9 + weasyprint 68) theo pipeline chuẩn: markdown → pandoc → HTML5 →
WeasyPrint → PDF A5 (CSS sách của compile_tu_vi_sieu_tri_tue.py — serif, @page đánh số
trang, TOC clickable). Nguồn gốc scan + text-layer + OCR đã attach tại
data/restored_books/cheiro-book-of-numbers/source/ (Stage 1 hoàn tất).

    python3 scripts/publish_cheiro_pdf_v2.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/restored_books/cheiro-book-of-numbers/content.md"
OUT = ROOT / "data/published"

# CSS sách chuẩn nhà (đồng bộ compile_tu_vi_sieu_tri_tue.py)
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
title: "SÁCH VỀ NHỮNG CON SỐ"
subtitle: "Cheiro's Book of Numbers (1926) — phục dựng cốt lõi hệ Chaldean · bản EN→VI"
author: "Cheiro (Count Louis Hamon) · YI-CHRONOS — Nhà xuất bản Đông phương học AI-driven"
date: "{date}"
lang: vi
---

"""


def main() -> int:
    if not SRC.exists():
        print("THIẾU nguồn:", SRC)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)

    master = COVER.format(date=datetime.now().strftime("%d/%m/%Y"))
    master += SRC.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        md = Path(td) / "master.md"
        html = Path(td) / "master.html"
        css = Path(td) / "book.css"
        md.write_text(master, encoding="utf-8")
        css.write_text(CSS, encoding="utf-8")

        subprocess.run([
            "pandoc", str(md), "-o", str(html),
            "--from", "markdown+pipe_tables+blank_before_blockquote+yaml_metadata_block",
            "--to", "html5", "--standalone", "--toc", "--toc-depth", "2",
            "--metadata", "lang=vi", "--css", str(css),
            "--embed-resources",
        ], check=True)

        out_pdf = OUT / "cheiro-book-of-numbers-core-v0.2.pdf"
        from weasyprint import HTML
        HTML(filename=str(html)).write_pdf(str(out_pdf))
        print(f"✅ PDF: {out_pdf}  ({out_pdf.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
