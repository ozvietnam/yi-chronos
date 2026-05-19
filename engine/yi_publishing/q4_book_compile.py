"""Compile "Tử Vi Đẩu Số Toàn Thư — Quyển 4: 60+ Lá Số Cổ Kim".

Q4 = OCR p0199-p0300 (102 trang) — case studies.
"""
from __future__ import annotations

import html as _html
import json
import time
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
PER_PAGE = ROOT / "data/yi_publishing/q1_tuvi/per_page"
TRANSL_ROOT = ROOT / "data/yi_publishing/translations/tuvidauso-zh"
OUT_DIR = ROOT / "data/published"

Q4_START = 199
Q4_END = 300


def _esc(s) -> str:
    return _html.escape(str(s)) if s else ""


def _read_page_lines(page_num: int):
    pdir = TRANSL_ROOT / f"p{page_num:04d}"
    out = []
    if not pdir.exists():
        return out
    for jf in sorted(pdir.glob("r*.json")):
        try:
            d = json.loads(jf.read_text())
        except Exception:
            continue
        for lid, v in sorted(d.get("lines", {}).items()):
            out.append((lid, v.get("text_vi", ""), v.get("text_vi_luangiai", "")))
    return out


CSS = r"""
@page {
  size: A4; margin: 2.2cm 1.8cm 2cm 1.8cm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; }
  @top-right { content: "Tử Vi Đẩu Số Toàn Thư — Q.4"; font-size: 9pt; color: #9ca3af; font-style: italic; }
}
@page :first { @top-right { content: ""; } @bottom-center { content: ""; } }

body { font-family: "Times New Roman", "Palatino", "Hoefler Text", "Baskerville", serif;
       font-size: 10.5pt; line-height: 1.55; color: #1f2937; }
h1 { font-size: 26pt; text-align: center; color: #14532d; margin: 0 0 0.4em; letter-spacing: -0.02em; }
h2 { font-size: 17pt; color: #14532d; border-bottom: 1.5pt solid #86efac; padding-bottom: 0.2em;
     margin: 1.8em 0 0.8em; page-break-after: avoid; }
h3 { font-size: 13pt; color: #166534; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h4 { font-size: 11pt; color: #166534; margin: 0.8em 0 0.3em; }
p { text-align: justify; margin: 0.4em 0; }
blockquote {
  margin: 0.8em 0; padding: 0.5em 1.2em;
  border-left: 3pt solid #86efac; background: #f0fdf4; color: #4b5563; font-style: italic;
}

.cover { text-align: center; padding-top: 4cm; page-break-after: always; }
.cover .han { font-size: 42pt; color: #14532d; font-family: "Songti SC", serif; letter-spacing: 0.2em; margin: 0; }
.cover h1 { font-size: 28pt; margin-top: 0.3em; }
.cover .sub { font-size: 14pt; color: #6b7280; margin-top: 0.8em; font-style: italic; }
.cover .author { font-size: 12pt; color: #4b5563; margin-top: 2.5cm; }
.cover .meta { font-size: 10pt; color: #6b7280; margin-top: 1.5cm; }

.preface { page-break-after: always; }

.phu-line { page-break-inside: avoid; margin: 0.5em 0; }
.phu-line .hv { font-style: italic; color: #4b5563; }
.phu-line .lg { color: #1f2937; padding-left: 1.5em; border-left: 2pt solid #bbf7d0; margin-top: 0.2em; }

.page-block { page-break-inside: auto; margin: 1em 0; padding-bottom: 0.5em; border-bottom: 0.5pt dashed #e5e7eb; }
.page-label { font-size: 9pt; color: #9ca3af; font-style: italic; margin-bottom: 0.3em; }
.summary-vn {
  background: #f0fdf4; border-left: 3pt solid #86efac;
  padding: 6pt 10pt; margin: 0.4em 0; font-size: 10pt; line-height: 1.55; border-radius: 3pt;
}

.book-footer { margin-top: 3em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db;
               font-size: 8.5pt; color: #9ca3af; text-align: center; }
"""


def section_cover() -> str:
    today = time.strftime("%Y-%m-%d")
    return f"""
    <div class="cover">
      <p class="han">紫微斗數全書·卷四</p>
      <h1>Tử Vi Đẩu Số Toàn Thư</h1>
      <p class="sub">Quyển 4 — Lá Số Cổ Kim & Phân Tích Mẫu</p>
      <div class="author">
        Tác giả: <strong>Hi Di Trần tiên sinh</strong> (陳摶, ~872–989)<br>
        Bổ tập: Phan Hy Doãn · Tham duyệt: Dương Nhất Vũ
      </div>
      <div class="meta">
        Dịch và biên soạn AI · YI-CHRONOS<br>
        Phương pháp: DeepSeek-chat + MiniMax-M2 parallel<br>
        Phạm vi: 102 trang OCR (p0199-p0300) — 60+ lá số mẫu<br>
        Ấn bản 1.0 · {today}
      </div>
    </div>
    """


def section_preface() -> str:
    return """
    <section class="preface">
      <h2>Lời nói đầu Quyển 4</h2>
      <p>Sau khi đã trình bày <em>nguyên lý</em> (Q1), <em>an sao</em> (Q2), <em>diễn giải 12 cung</em>
      (Q3), Quyển 4 trình bày <strong>các lá số cổ kim cụ thể</strong> để minh họa cách Trần Đoàn
      đọc đồng dạng giữa sao – cung – vận của một người với cuộc đời họ.</p>

      <p>Trong Quyển 4 có lá số của: <strong>Khổng Tử</strong>, <strong>Lý Bạch</strong>,
      <strong>Bạch Khởi</strong>, <strong>Mã Viện</strong>, <strong>Bạch Cư Dị</strong>,
      <strong>Tư Mã Bật</strong>, <strong>Hoàng Vũ</strong>, các vua triều Đường-Tống,
      cùng nhiều nhân vật lịch sử khác — tổng cộng ~60 lá số.</p>

      <blockquote>
        "Cổ nhân chi mệnh, đại để bất ngoại hồ thử. Mỗi nhân tự hữu tinh thần,
        bất khả khái luận."<br>
        — Quyển 4
      </blockquote>
      <p><em>(Mệnh người xưa, đại để không nằm ngoài những điều này. Mỗi người tự có tinh thần riêng,
      không thể luận chung.)</em></p>

      <h3>Tinh thần đọc</h3>
      <p>Người đọc Quyển 4 nên:</p>
      <ol>
        <li>Đọc lá số như <em>case study</em>, không phải bản án</li>
        <li>So sánh các pattern (chính tinh, cách cục, vận hạn) chứ không bắt chước máy móc</li>
        <li>Hiểu rằng <em>"mỗi người tự có tinh thần riêng"</em> — đồng cách không đồng đời</li>
      </ol>
    </section>
    """


def section_pages() -> str:
    parts = ['<section><h2>60+ lá số cổ kim — theo trang</h2>']
    for page in range(Q4_START, Q4_END + 1):
        meta_file = PER_PAGE / f"p{page:04d}.json"
        if not meta_file.exists():
            continue
        try:
            meta = json.loads(meta_file.read_text())
        except Exception:
            continue
        if meta.get("skipped"):
            continue

        lines = _read_page_lines(page)
        nhan_xet = meta.get("nhan_xet", "").strip()
        summary_vn = meta.get("summary_vn", "").strip()

        parts.append('<div class="page-block">')
        parts.append(f'<div class="page-label">━━━ Trang {page} (OCR) ━━━</div>')

        if nhan_xet:
            parts.append(f'<p><strong>Chủ đề:</strong> <em>{_esc(nhan_xet)}</em></p>')

        if lines:
            parts.append('<h4>Nguyên văn</h4>')
            for lid, hv, lg in lines:
                if not hv:
                    continue
                parts.append(f'<div class="phu-line">')
                parts.append(f'  <div class="hv">{_esc(hv)}</div>')
                if lg:
                    parts.append(f'  <div class="lg">→ {_esc(lg)}</div>')
                parts.append('</div>')

        if summary_vn:
            parts.append(f'<h4>Tóm tắt hiện đại</h4>')
            parts.append(f'<div class="summary-vn">{_esc(summary_vn)}</div>')

        parts.append('</div>')

    parts.append('</section>')
    return "\n".join(parts)


def build_html() -> str:
    return "\n".join([
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">',
        '<title>Tử Vi Đẩu Số Toàn Thư — Quyển 4</title>',
        f'<style>{CSS}</style></head><body>',
        section_cover(),
        section_preface(),
        section_pages(),
        '<div class="book-footer">YI-CHRONOS · Tử Vi Đẩu Số Toàn Thư — Quyển 4 · Ấn bản 1.0</div>',
        '</body></html>',
    ])


def generate_pdf() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "tu-vi-q4-la-so-co-kim.pdf"
    (OUT_DIR / "tu-vi-q4-la-so-co-kim.html").write_text(build_html())
    from weasyprint import HTML
    HTML(string=build_html()).write_pdf(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    p = generate_pdf()
    print(f"✅ PDF: {p}")
    print(f"   Size: {p.stat().st_size / 1024:.1f} KB")
