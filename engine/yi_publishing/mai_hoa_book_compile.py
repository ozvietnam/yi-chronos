"""Compile "Mai Hoa Dịch Số — Quyển 1+2: Nguyên Tác Thiệu Khang Tiết".

Source: data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md (672 trang)
Q1 = p15-115 (Chu Dịch quái số + Bát quái tượng lệ)
Q2 = p116-327 (Chiêm bốc huyền cơ)

Output: data/published/mai-hoa-q1q2-nguyen-tac.pdf
"""
from __future__ import annotations

import html as _html
import json
import re
import time
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
SOURCE_MD = ROOT / "data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md"
PER_PAGE = ROOT / "data/yi_publishing/mai_hoa_thamnhuan/per_page"
OUT_DIR = ROOT / "data/published"

Q1_START, Q1_END = 15, 115
Q2_START, Q2_END = 116, 327


def _esc(s) -> str:
    return _html.escape(str(s)) if s else ""


def parse_pages() -> dict[int, str]:
    text = SOURCE_MD.read_text()
    pages: dict[int, str] = {}
    parts = re.split(r'<a id="page-(\d+)"></a>', text)
    for i in range(1, len(parts) - 1, 2):
        try:
            num = int(parts[i])
            content = re.sub(r'<!-- Trang \d+ -->', '', parts[i + 1]).strip()
            if content:
                pages[num] = content
        except (ValueError, IndexError):
            continue
    return pages


CSS = r"""
@page {
  size: A4; margin: 2.2cm 1.8cm 2cm 1.8cm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; }
  @top-right { content: "Mai Hoa Dịch Số — Q.1+2"; font-size: 9pt; color: #9ca3af; font-style: italic; }
}
@page :first { @top-right { content: ""; } @bottom-center { content: ""; } }

body { font-family: "Times New Roman", "Palatino", "Hoefler Text", "Baskerville", serif;
       font-size: 10.5pt; line-height: 1.55; color: #1f2937; }
h1 { font-size: 26pt; text-align: center; color: #831843; margin: 0 0 0.4em; letter-spacing: -0.02em; }
h2 { font-size: 17pt; color: #831843; border-bottom: 1.5pt solid #f9a8d4; padding-bottom: 0.2em;
     margin: 1.8em 0 0.8em; page-break-after: avoid; }
h3 { font-size: 13pt; color: #9d174d; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h4 { font-size: 11pt; color: #9d174d; margin: 0.8em 0 0.3em; }
p { text-align: justify; margin: 0.4em 0; }
blockquote {
  margin: 0.8em 0; padding: 0.5em 1.2em;
  border-left: 3pt solid #f9a8d4; background: #fdf2f8; color: #4b5563; font-style: italic;
}

.cover { text-align: center; padding-top: 4cm; page-break-after: always; }
.cover .han { font-size: 42pt; color: #831843; font-family: "Songti SC", serif; letter-spacing: 0.2em; margin: 0; }
.cover h1 { font-size: 28pt; margin-top: 0.3em; }
.cover .sub { font-size: 14pt; color: #6b7280; margin-top: 0.8em; font-style: italic; }
.cover .author { font-size: 12pt; color: #4b5563; margin-top: 2.5cm; }
.cover .meta { font-size: 10pt; color: #6b7280; margin-top: 1.5cm; }

.preface { page-break-after: always; }

.page-block { page-break-inside: auto; margin: 1em 0; padding-bottom: 0.5em;
              border-bottom: 0.5pt dashed #e5e7eb; }
.page-label { font-size: 9pt; color: #9ca3af; font-style: italic; margin-bottom: 0.3em; }
.page-text {
  white-space: pre-wrap; font-size: 10.5pt; line-height: 1.6;
  color: #1f2937;
}
.summary-vn {
  background: #fdf2f8; border-left: 3pt solid #f9a8d4;
  padding: 6pt 10pt; margin: 0.4em 0; font-size: 10pt; line-height: 1.55; border-radius: 3pt;
}

.method-card {
  border: 0.5pt solid #e5e7eb; border-left: 3pt solid #d946ef;
  border-radius: 4pt; padding: 8pt 10pt; margin: 6pt 0; page-break-inside: avoid;
}
.method-card strong { font-size: 11.5pt; color: #1f2937; }
.method-card .lv { font-size: 9pt; color: #6b7280; font-style: italic; margin-left: 0.3em; }
.method-card .quy-tac { font-size: 9.5pt; color: #6b7280; margin: 0.2em 0; font-style: italic; }
.method-card .y-nghia { font-size: 10pt; margin-top: 0.3em; }

.volume-divider {
  page-break-before: always; page-break-after: always;
  text-align: center; padding-top: 8cm;
  background: linear-gradient(135deg, #fdf2f8, #fbcfe8); height: 24cm;
}
.volume-divider .han { font-size: 60pt; color: #831843; font-family: "Songti SC", serif;
                       letter-spacing: 0.3em; margin: 0; }
.volume-divider h1 { font-size: 36pt; margin-top: 0.5em; color: #831843; }
.volume-divider .vol-sub { font-size: 18pt; color: #4b5563; margin-top: 1em; font-style: italic; }

.book-footer { margin-top: 3em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db;
               font-size: 8.5pt; color: #9ca3af; text-align: center; }
"""


def section_cover() -> str:
    today = time.strftime("%Y-%m-%d")
    return f"""
    <div class="cover">
      <p class="han">梅花易數</p>
      <h1>Mai Hoa Dịch Số</h1>
      <p class="sub">Quyển 1 + 2 — Nguyên Tác Thiệu Khang Tiết</p>
      <div class="author">
        Tác giả: <strong>Thiệu Khang Tiết</strong> (邵雍, 1011-1077)<br>
        Hiệu: Khang Tiết tiên sinh
      </div>
      <div class="meta">
        Dịch và biên soạn AI · YI-CHRONOS<br>
        Pipeline: DeepSeek-chat + MiniMax-M2 parallel<br>
        Phạm vi: 312 trang OCR (p15-p327) — Chu Dịch quái số + Chiêm bốc huyền cơ<br>
        Ấn bản 1.0 · {today}
      </div>
    </div>
    """


def section_preface() -> str:
    return """
    <section class="preface">
      <h2>Lời nói đầu Mai Hoa Q1+Q2</h2>
      <p>Bộ sách <strong>Mai Hoa Dịch Số</strong> (梅花易數) tương truyền của
      <strong>Thiệu Khang Tiết</strong> (邵雍, 1011-1077) — nhà đại triết học và đại dịch học
      đời Tống. Toàn bộ gồm 5 quyển:</p>

      <ul>
        <li><strong>Quyển 1</strong> — Chu Dịch quái số, Ngũ hành sinh khắc, Bát cung sở thuộc ngũ hành.
        Quái khí suy, Thập thiên can, Thập nhị địa chi, Bát quái tượng lệ, Chiêm pháp, Ngoạn pháp.</li>
        <li><strong>Quyển 2</strong> — Chiêm bốc huyền cơ: Chiêm quái tổng quyết, Thiên thời chiêm,
        Nhân sự chiêm (Gia trạch, Hôn nhân, Sinh sản, Cầu danh, Giao dịch, Xuất hành, Thất vật,
        Tật bệnh, Quan tụng, Phần mộ...)</li>
        <li><strong>Quyển 3</strong> — Bát quái phương vị đồ, Quan mai chiêm quyết, Thể dụng quyết,
        Khắc ứng quyết, Vạn vật phú. <em>(Đã thâm nhuần + xuất bản riêng — Mai Hoa Hành Đạo Toàn Thư v1.9)</em></li>
        <li><strong>Quyển 4</strong> — Chỉ mê phú, Huyền hoàng khắc ứng ca, Hoa áp phú, Thám huyền phú.</li>
        <li><strong>Quyển 5</strong> — Ngũ hành toàn bị, Lục thân hình thức, Bát quái biện, Dịch lý huyền vi.</li>
      </ul>

      <h3>Paradigm bất di bất dịch (Iron Rule #4)</h3>
      <blockquote>
        Mai Hoa Dịch Số = ĐỌC ĐỒNG DẠNG, không phải predict.<br>
        Quẻ là tấm gương phản chiếu khoảnh khắc — không phải bản án tương lai.
      </blockquote>

      <h3>Pipeline biên soạn (Bookflow v2.0)</h3>
      <ol>
        <li>OCR layout-aware 672 trang PDF gốc Việt-Hán</li>
        <li>Phân quyển qua TOC markers</li>
        <li>Trích structured methods + concepts (DeepSeek-chat JSON mode)</li>
        <li>Tóm tắt VN dễ hiểu (MiniMax-M2 paragraph)</li>
        <li>Compile PDF (WeasyPrint, Times font, A4)</li>
      </ol>
    </section>
    """


def render_page_block(page_num: int, content: str) -> str:
    """Render 1 page với nguyên văn + tóm tắt + methods extracted."""
    meta_file = PER_PAGE / f"p{page_num:04d}.json"
    meta = {}
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text())
        except Exception:
            pass
    if meta.get("skipped"):
        return ""

    parts = ['<div class="page-block">']
    parts.append(f'<div class="page-label">━━━ Trang {page_num} (OCR gốc) ━━━</div>')

    nhan_xet = meta.get("nhan_xet", "").strip()
    if nhan_xet:
        parts.append(f'<p><strong>Chủ đề:</strong> <em>{_esc(nhan_xet)}</em></p>')

    # Original text
    parts.append('<h4>Nguyên văn</h4>')
    parts.append(f'<div class="page-text">{_esc(content[:6000])}</div>')

    # Vietnamese summary
    summary = meta.get("summary_vn", "").strip()
    if summary:
        parts.append(f'<h4>Tóm tắt hiện đại</h4>')
        parts.append(f'<div class="summary-vn">{_esc(summary)}</div>')

    # Methods extracted
    methods = meta.get("methods", [])[:5]
    if methods:
        parts.append('<h4>Phương pháp / Quyết trích xuất</h4>')
        for m in methods:
            parts.append('<div class="method-card">')
            parts.append(f'  <strong>{_esc(m.get("ten",""))}</strong>'
                         f'<span class="lv">[{_esc(m.get("linh_vuc","?"))}]</span>')
            if m.get("quy_tac"):
                parts.append(f'  <div class="quy-tac">"{_esc(m["quy_tac"][:200])}"</div>')
            if m.get("y_nghia"):
                parts.append(f'  <div class="y-nghia">{_esc(m["y_nghia"][:280])}</div>')
            parts.append('</div>')

    parts.append('</div>')
    return "\n".join(parts)


def section_pages(start: int, end: int) -> str:
    pages = parse_pages()
    parts = []
    for p in range(start, end + 1):
        if p not in pages:
            continue
        block = render_page_block(p, pages[p])
        if block:
            parts.append(block)
    return "\n".join(parts)


def build_html() -> str:
    return "\n".join([
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">',
        '<title>Mai Hoa Dịch Số — Q1+Q2</title>',
        f'<style>{CSS}</style></head><body>',
        section_cover(),
        section_preface(),
        '<div class="volume-divider"><p class="han">卷一</p><h1>Quyển Thứ Nhất</h1>'
        '<p class="vol-sub">Chu Dịch Quái Số · Bát Quái Tượng Lệ</p></div>',
        '<section><h2>Quyển 1 — nội dung</h2>',
        section_pages(Q1_START, Q1_END),
        '</section>',
        '<div class="volume-divider"><p class="han">卷二</p><h1>Quyển Thứ Hai</h1>'
        '<p class="vol-sub">Chiêm Bốc Huyền Cơ</p></div>',
        '<section><h2>Quyển 2 — nội dung</h2>',
        section_pages(Q2_START, Q2_END),
        '</section>',
        '<div class="book-footer">YI-CHRONOS · Mai Hoa Dịch Số — Quyển 1+2 · Ấn bản 1.0</div>',
        '</body></html>',
    ])


def generate_pdf() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "mai-hoa-q1q2-nguyen-tac.pdf"
    (OUT_DIR / "mai-hoa-q1q2-nguyen-tac.html").write_text(build_html())
    from weasyprint import HTML
    HTML(string=build_html()).write_pdf(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    p = generate_pdf()
    print(f"✅ PDF: {p}")
    print(f"   Size: {p.stat().st_size / 1024 / 1024:.2f} MB")
