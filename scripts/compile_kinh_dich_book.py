#!/usr/bin/env python3
"""Compile 64 quẻ + 7 tâm pháp thành sách PDF 'Kinh Dịch Tâm Pháp Trình Di & Chu Hy'.

Pipeline (theo Bookflow v2.0 Iron Rule #5):
1. Read 64 quẻ files (data/hermes_yi/skills/kinh-dich/quẻ/01-64.md)
2. Read 7 tâm pháp synthesis files
3. Compile master markdown:
   - Cover + manifesto
   - TOC clickable
   - Phần I: Lời mở đầu + paradigm
   - Phần II: 64 quẻ (1 chương/quẻ)
   - Phần III: 7 tâm pháp synthesis
   - Phần IV: Index Hán-Việt
4. Pandoc → HTML
5. WeasyPrint → PDF với cover page, page numbers, TOC

Output: data/published_books/kinh-dich-tam-phap/Kinh-Dich-Tam-Phap-v1.0.pdf
"""
from __future__ import annotations

import re
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "data" / "hermes_yi" / "skills" / "kinh-dich"
OUT_DIR = ROOT / "data" / "published_books" / "kinh-dich-tam-phap"
VERSION = "v1.0"
PUB_DATE = date.today().isoformat()


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end < 0:
        return text
    return text[end + 4:].lstrip()


def _read_md(rel: str) -> str:
    f = SKILLS / rel
    if not f.exists():
        return ""
    return _strip_frontmatter(f.read_text(encoding="utf-8"))


def _list_que_files() -> list[Path]:
    """64 quẻ theo thứ tự 01-64."""
    files = sorted((SKILLS / "quẻ").glob("*.md"))
    # Filter only NN-*.md format
    out = []
    for f in files:
        m = re.match(r"^(\d{2})-", f.name)
        if m and 1 <= int(m.group(1)) <= 64:
            out.append(f)
    out.sort(key=lambda p: int(p.name[:2]))
    return out


def _list_tam_phap_files() -> list[Path]:
    return sorted((SKILLS / "tam-phap").glob("*.md"))


def _demote_headers(text: str, by: int = 1) -> str:
    """Demote # → ## (by=1) để chương con không conflict với chương lớn."""
    lines = []
    for ln in text.split("\n"):
        if ln.startswith("#"):
            lines.append("#" * by + ln)
        else:
            lines.append(ln)
    return "\n".join(lines)


def _h1_to_h2_h3(text: str) -> str:
    """Convert # → ## (chapter), ## → ### (section), ### → #### (subsection)."""
    out = []
    for ln in text.split("\n"):
        if ln.startswith("####"):
            out.append("#####" + ln[4:])
        elif ln.startswith("###"):
            out.append("####" + ln[3:])
        elif ln.startswith("##"):
            out.append("###" + ln[2:])
        elif ln.startswith("#"):
            out.append("##" + ln[1:])
        else:
            out.append(ln)
    return "\n".join(out)


def build_master_md() -> str:
    """Build full markdown ~1MB."""
    parts = []

    # === Cover + Manifesto ===
    parts.append(f"""---
title: "Kinh Dịch Tâm Pháp"
subtitle: "Trình Di Truyện · Bản nghĩa Chu Hy · 64 Quẻ"
author: "YI-CHRONOS · Anh + em (học trò Thiệu Khang Tiết)"
date: "{PUB_DATE}"
version: "{VERSION}"
keywords: [kinh dịch, chu dịch, trình di, chu hy, mai hoa, 64 quẻ]
lang: vi
---

# Lời mở đầu

> _"Vật bất khả cùng"_ — Vị Tế (quẻ 64, kết Kinh Dịch)
> Kinh Dịch KHÔNG kết bằng Ký Tế (đã hoàn) mà bằng Vị Tế (chưa hoàn).
> Đây là paradigm gốc: **không có "FINAL".** Mỗi cuối là 1 đầu mới.

Cuốn sách này biên soạn từ:

- **Trình Di Truyện** 程頤傳 (1033–1107) — Tống Nho, "Y Xuyên Tiên sinh"
- **Bản nghĩa Chu Hy** 周易本義 (1130–1200) — Tống Nho lớn nhất
- **Bản dịch Ngô Tất Tố** *Kinh Dịch Trọn Bộ* (1936)
- **Tâm pháp Thiệu Khang Tiết** 邵康節 (1011–1077) — Mai Hoa Dịch Số

## Paradigm CỐT — Iron Rule #4

> _"Một vật vốn có một thân, một thân lại có một trời đất._
> _Biết rằng muôn việc đều sẵn nơi ta, mới dám đặt nền móng cho Tam Tài."_
> — Thiệu Khang Tiết, **Vận Pháp Thi** (Mai Hoa Q3 tr.78)

Kinh Dịch là **MÔN HỌC ĐỒNG DẠNG**:

- Cấu trúc vũ trụ = cấu trúc người = cấu trúc khoảnh khắc
- Người và vũ trụ **NGANG NHAU** (Tam Tài)
- **Quan vật trace tính** — KHÔNG predict cát/hung tĩnh

❌ **TRÁNH** paradigm fortune-telling:
- "Quẻ này dự đoán cát/hung"
- "Anh sẽ thành công/thất bại"

✅ **DÙNG** paradigm Tổ sư:
- "Khoảnh khắc anh hỏi phản chiếu cái gì lớn hơn trong vũ trụ?"
- "Vũ trụ đang nói qua khoảnh khắc này: ..."

## Cấu trúc sách

- **Phần I — Lời mở đầu + manifesto** (đang đọc)
- **Phần II — 64 Quẻ Trình Di & Chu Hy** (64 chương, mỗi quẻ ~3-6 trang)
- **Phần III — 7 Tâm Pháp Synthesis** (cross-quẻ insight)

> _"Quân tử chi quang, hữu phu, cát."_ — Vị Tế Lục Ngũ

Đức sáng của quân tử, có chí thành, tốt.

\\newpage
""")

    # === Phần II: 64 quẻ ===
    parts.append("# Phần II — 64 Quẻ Trình Di & Chu Hy\n\n\\newpage\n")
    que_files = _list_que_files()
    print(f"[compile] {len(que_files)} quẻ files")
    for f in que_files:
        body = _strip_frontmatter(f.read_text(encoding="utf-8"))
        body = _h1_to_h2_h3(body)  # H1 → H2 (chapter under "Phần II")
        parts.append(body)
        parts.append("\n\n\\newpage\n")

    # === Phần III: Tâm pháp synthesis ===
    parts.append("# Phần III — 7 Tâm Pháp Synthesis\n\n\\newpage\n")
    tp_files = _list_tam_phap_files()
    print(f"[compile] {len(tp_files)} tâm-pháp files")
    for f in tp_files:
        body = _strip_frontmatter(f.read_text(encoding="utf-8"))
        body = _h1_to_h2_h3(body)
        parts.append(body)
        parts.append("\n\n\\newpage\n")

    # === Phần IV: Index quẻ Hán-Việt ===
    parts.append("# Phần IV — Index 64 Quẻ\n\n")
    parts.append("| # | Quẻ Việt | Quẻ Hán | Cấu trúc | Trang |\n|---|---|---|---|---|\n")
    for f in que_files:
        m = re.match(r"^(\d{2})-(.+)\.md$", f.name)
        if not m:
            continue
        num = int(m.group(1))
        slug = m.group(2)
        # Parse name from H1
        body = _strip_frontmatter(f.read_text(encoding="utf-8"))
        h1_match = re.search(r"^#\s+Quẻ\s+\d+\s+—\s+([^·]+)·\s+([☰☱☲☳☴☵☶☷]+)", body, re.M)
        name = h1_match.group(1).strip() if h1_match else slug
        struct = h1_match.group(2).strip() if h1_match else ""
        zh = ""
        # Try parse Hán
        zh_match = re.search(r"^#\s+Quẻ\s+\d+\s+—\s+\S+\s+(\S+)\s+·", body, re.M)
        if zh_match:
            zh = zh_match.group(1)
        parts.append(f"| {num} | {name} | {zh} | {struct} | — |\n")

    return "\n".join(parts)


def md_to_pdf(master_md: Path, out_pdf: Path) -> None:
    """Pandoc md → HTML, then WeasyPrint HTML → PDF."""
    html_path = out_pdf.with_suffix(".html")

    # Pandoc: md → standalone HTML with embedded CSS
    css_inline = """
    @page {
      size: A4;
      margin: 2.2cm 2cm 2.2cm 2cm;
      @bottom-right { content: counter(page); font-size: 9pt; color: #888; }
      @top-left { content: string(chapter); font-size: 9pt; color: #888; font-style: italic; }
    }
    @page :first { @top-left { content: none; } @bottom-right { content: none; } }
    body { font-family: 'Times New Roman', 'Source Han Serif VN', serif; line-height: 1.55; color: #222; }
    h1 { string-set: chapter content(text); page-break-before: always; color: #7c2d12; font-size: 22pt; margin-top: 0.4cm; }
    h1:first-of-type { page-break-before: avoid; }
    h2 { color: #92400e; font-size: 16pt; border-bottom: 1px solid #d4a574; padding-bottom: 0.2em; margin-top: 1em; }
    h3 { color: #b45309; font-size: 13pt; margin-top: 0.8em; }
    h4 { color: #b45309; font-size: 11pt; }
    blockquote {
      background: #fef9e7; border-left: 3px solid #d4a574;
      padding: 0.5em 0.8em; margin: 0.5em 0;
      font-style: italic; color: #6b4f3c;
    }
    table { border-collapse: collapse; width: 100%; margin: 0.5em 0; font-size: 9.5pt; }
    th, td { border: 1px solid #d4a574; padding: 0.3em 0.5em; text-align: left; vertical-align: top; }
    th { background: #fef3c7; }
    code { background: #f3e8c0; padding: 0 0.25em; border-radius: 2px; font-size: 0.9em; }
    a { color: #92400e; text-decoration: none; }
    hr { border: 0; border-top: 1px dashed #d4a574; margin: 1.2em 0; }
    """

    print(f"[pandoc] {master_md.name} → HTML")
    subprocess.run([
        "pandoc",
        str(master_md),
        "-o", str(html_path),
        "--standalone",
        "--metadata", f"title=Kinh Dịch Tâm Pháp {VERSION}",
        "--toc", "--toc-depth=2",
        "-V", "lang=vi",
    ], check=True)

    # Inject CSS into HTML <head>
    html = html_path.read_text(encoding="utf-8")
    html = html.replace("</head>", f"<style>{css_inline}</style></head>", 1)
    html_path.write_text(html, encoding="utf-8")

    # WeasyPrint
    print(f"[weasyprint] HTML → PDF")
    venv_py = ROOT / ".venv" / "bin" / "python3"
    subprocess.run([
        str(venv_py), "-m", "weasyprint",
        str(html_path),
        str(out_pdf),
    ], check=True)
    print(f"[done] {out_pdf}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master_md = OUT_DIR / f"Kinh-Dich-Tam-Phap-{VERSION}.md"
    out_pdf = OUT_DIR / f"Kinh-Dich-Tam-Phap-{VERSION}.pdf"

    print(f"[compile] Building master markdown...")
    md = build_master_md()
    master_md.write_text(md, encoding="utf-8")
    print(f"[compile] {master_md.name}: {len(md):,} chars, {md.count(chr(10)):,} lines")

    # Check deps
    if not shutil.which("pandoc"):
        print("ERROR: pandoc not installed", file=sys.stderr)
        sys.exit(1)

    md_to_pdf(master_md, out_pdf)
    pdf_size_kb = out_pdf.stat().st_size / 1024
    print(f"\n✅ PDF: {out_pdf}")
    print(f"   Size: {pdf_size_kb:.1f} KB ({pdf_size_kb/1024:.1f} MB)")


if __name__ == "__main__":
    main()
