"""Compile cuốn BỘ Tử Vi Đẩu Số Toàn Thư — Q1 + Q3 + Q4 + bảng tra cứu tổng hợp.

Output: data/published/tu-vi-bo-toan-thu.pdf

Cấu trúc:
    Trang bìa bộ
    Mục lục bộ
    [Q1 nội dung — 35 trang]
    [Q3 nội dung — 135 trang]
    [Q4 nội dung — 91 trang]
    Bảng tra cứu A-Z (985 cách + 576 concepts)
"""
from __future__ import annotations

import html as _html
import json
import time
from pathlib import Path

ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
OUT_DIR = ROOT / "data/published"

# Import section builders from existing compilers
from engine.yi_publishing.q1_book_compile import (
    section_phu_thai_vi, section_cach_cuc_top, section_concepts as q1_concepts,
    section_index as q1_cach_index,
)
from engine.yi_publishing.q2_book_compile import section_pages as q2_pages
from engine.yi_publishing.q3_book_compile import section_pages as q3_pages
from engine.yi_publishing.q4_book_compile import section_pages as q4_pages


CSS = r"""
@page {
  size: A4; margin: 2.2cm 1.8cm 2cm 1.8cm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; }
  @top-right { content: string(book-title); font-size: 9pt; color: #9ca3af; font-style: italic; }
}
@page :first { @top-right { content: ""; } @bottom-center { content: ""; } }

body { font-family: "Times New Roman", "Palatino", "Hoefler Text", "Baskerville", serif;
       font-size: 10.5pt; line-height: 1.55; color: #1f2937; }

h1 { font-size: 26pt; text-align: center; margin: 0 0 0.4em; letter-spacing: -0.02em;
     color: #7c2d12; }
h2 { font-size: 17pt; border-bottom: 1.5pt solid #d6a86b; padding-bottom: 0.2em;
     margin: 1.8em 0 0.8em; page-break-after: avoid; color: #7c2d12;
     string-set: book-title content(); }
h3 { font-size: 13pt; margin: 1.2em 0 0.4em; page-break-after: avoid; color: #92400e; }
h4 { font-size: 11pt; margin: 0.8em 0 0.3em; color: #92400e; }
p { text-align: justify; margin: 0.4em 0; }
em { color: #6b7280; }

blockquote {
  margin: 0.8em 0; padding: 0.5em 1.2em;
  border-left: 3pt solid #d6a86b; background: #fef9c3; color: #4b5563; font-style: italic;
}

.cover {
  text-align: center; padding-top: 3cm; page-break-after: always;
  height: 24cm;
}
.cover .han { font-size: 48pt; color: #7c2d12; font-family: "Songti SC", serif;
              letter-spacing: 0.3em; margin: 0; line-height: 1.2; }
.cover h1 { font-size: 32pt; margin-top: 0.4em; }
.cover .sub { font-size: 16pt; color: #6b7280; margin-top: 0.8em; font-style: italic; }
.cover .author { font-size: 13pt; color: #4b5563; margin-top: 3cm; line-height: 1.6; }
.cover .meta { font-size: 11pt; color: #6b7280; margin-top: 1.5cm; line-height: 1.5; }
.cover .boxed-banner {
  display: inline-block; padding: 8pt 24pt; margin-top: 1cm;
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white; font-size: 12pt; font-weight: bold; letter-spacing: 0.1em;
  border-radius: 4pt;
}

.toc { page-break-after: always; }
.toc ol { padding-left: 2em; }
.toc li { margin: 0.4em 0; font-size: 11pt; }
.toc .quyen { font-weight: 700; color: #7c2d12; }

/* Volume separators */
.volume-divider {
  page-break-before: always; page-break-after: always;
  text-align: center; padding-top: 8cm;
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  height: 24cm;
}
.volume-divider .han { font-size: 60pt; color: #7c2d12; font-family: "Songti SC", serif;
                       letter-spacing: 0.3em; margin: 0; }
.volume-divider h1 { font-size: 36pt; margin-top: 0.5em; color: #7c2d12; }
.volume-divider .vol-sub { font-size: 18pt; color: #4b5563; margin-top: 1em; font-style: italic; }

/* Cách cục cards (from Q1) */
.cc-card {
  border: 0.5pt solid #e5e7eb; border-left: 3pt solid #94a3b8;
  border-radius: 4pt; padding: 8pt 10pt; margin: 6pt 0; page-break-inside: avoid;
}
.cc-thượng { border-left-color: #10b981; }
.cc-trung  { border-left-color: #f59e0b; }
.cc-hạ     { border-left-color: #f97316; }
.cc-phá    { border-left-color: #ef4444; }
.cc-tạp    { border-left-color: #6b7280; }
.cc-head { display: flex; justify-content: space-between; margin-bottom: 0.2em; align-items: baseline; }
.cc-head strong { font-size: 11.5pt; color: #1f2937; }
.cc-level { font-size: 9pt; text-transform: uppercase; color: #6b7280; font-weight: 600; }
.cc-evi { font-size: 9.5pt; color: #6b7280; margin: 0.2em 0; font-style: italic; }
.cc-y { font-size: 10pt; margin-top: 0.3em; }
.cc-meta { font-size: 8.5pt; color: #9ca3af; margin-top: 0.3em; }

/* Phú Thái Vi parallel layout */
.phu-line { page-break-inside: avoid; margin: 0.5em 0; }
.phu-line .hv { font-style: italic; color: #4b5563; }
.phu-line .lg { color: #1f2937; padding-left: 1.5em; border-left: 2pt solid #fde68a; margin-top: 0.2em; }

/* Concepts table */
.concept-table { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 0.6em 0; }
.concept-table th, .concept-table td {
  border: 0.5pt solid #d1d5db; padding: 3pt 6pt; text-align: left; vertical-align: top;
}
.concept-table th { background: #fef3c7; font-weight: 700; }
.concept-table tr:nth-child(even) td { background: #f9fafb; }

/* Index columns */
.index-grid { columns: 3; column-gap: 1.2em; font-size: 9.5pt; }
.index-grid p { margin: 0.1em 0; break-inside: avoid; }

/* Q3 page blocks */
.page-block { page-break-inside: auto; margin: 1em 0; padding-bottom: 0.5em;
              border-bottom: 0.5pt dashed #e5e7eb; }
.page-label { font-size: 9pt; color: #9ca3af; font-style: italic; margin-bottom: 0.3em; }
.summary-vn {
  background: #fef9c3; border-left: 3pt solid #fde68a;
  padding: 6pt 10pt; margin: 0.4em 0; font-size: 10pt; line-height: 1.55; border-radius: 3pt;
}

.book-footer { margin-top: 3em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db;
               font-size: 8.5pt; color: #9ca3af; text-align: center; }
"""


def section_box_cover() -> str:
    today = time.strftime("%Y-%m-%d")
    return f"""
    <div class="cover">
      <p class="han">紫微斗數全書</p>
      <h1>Tử Vi Đẩu Số Toàn Thư</h1>
      <p class="sub">Bộ 4 Quyển — Ấn Bản Hoàn Chỉnh</p>
      <div class="boxed-banner">CUỐN BỘ ĐẦY ĐỦ — 4 QUYỂN</div>
      <div class="author">
        Tác giả: <strong>Hi Di Trần tiên sinh</strong> (陳摶, ~872–989)<br>
        Bổ tập: Phan Hy Doãn (江西輔鼎子)<br>
        Tham duyệt: Dương Nhất Vũ
      </div>
      <div class="meta">
        Dịch và biên soạn AI · YI-CHRONOS<br>
        Pipeline: DeepSeek-chat + MiniMax-M2 parallel<br>
        1193 cách cục · 686 concepts · 4 quyển đầy đủ<br>
        Ấn bản Bộ 1.0 · {today}
      </div>
    </div>
    """


def section_box_toc() -> str:
    return """
    <section class="toc">
      <h2>Mục lục cuốn bộ</h2>
      <ol>
        <li class="quyen">Lời nói đầu cuốn bộ</li>
        <li class="quyen">Quyển 1 — Phú Thái Vi & Cách Cục Kinh Điển
          <ol>
            <li>Chương I. Phú Thái Vi (4 trang nguyên bản)</li>
            <li>Chương II. Top 50 cách cục kinh điển</li>
            <li>Chương III. Thư mục thuật ngữ (686 concepts)</li>
            <li>Chương IV. Bảng tra cứu A-Z (1193 cách)</li>
          </ol>
        </li>
        <li class="quyen">Quyển 2 — An Sao & 12 Cung
          <ol>
            <li>Lời nói đầu Quyển 2</li>
            <li>62 trang an mệnh, an sao, bảng quyết</li>
          </ol>
        </li>
        <li class="quyen">Quyển 3 — Diễn Giải 12 Cung × 14 Chính Tinh
          <ol>
            <li>Lời nói đầu Quyển 3</li>
            <li>Diễn giải 57 trang (p0142-p0198)</li>
          </ol>
        </li>
        <li class="quyen">Quyển 4 — Lá Số Cổ Kim
          <ol>
            <li>Lời nói đầu Quyển 4</li>
            <li>60+ case studies (p0199-p0300)</li>
          </ol>
        </li>
        <li class="quyen">Phụ lục — Bảng tra cứu tổng hợp</li>
      </ol>
    </section>
    """


def section_box_preface() -> str:
    return """
    <section class="preface">
      <h2>Lời nói đầu cuốn bộ</h2>

      <p>Đây là ấn bản <strong>bộ 3 quyển</strong> đầu tiên của
      "Tử Vi Đẩu Số Toàn Thư" — đại tác phẩm mệnh lý của Trần Đoàn (Hi Di tiên sinh) đời Tống —
      được dịch và biên soạn hoàn chỉnh bằng AI cho người đọc Việt hiện đại.</p>

      <h3>Tại sao ấn bản này quan trọng</h3>
      <ul>
        <li>Tử Vi Đẩu Số Toàn Thư là <em>sách gốc</em> của hầu hết các trường phái Tử Vi
        hiện đại (Bắc Phái, Nam Phái, Sài Gòn, Đài Loan)</li>
        <li>Trước đây bản tiếng Việt chủ yếu là <em>biên dịch lựa chọn</em>, không có ấn bản
        nào dịch đầy đủ 4 quyển kèm chú giải khoa học</li>
        <li>Ấn bản này dịch <strong>nguyên văn Hán-Việt + luận giải hiện đại</strong>, mỗi câu
        đều truy nguyên về trang gốc PDF</li>
      </ul>

      <h3>Cấu trúc 3 quyển trong bộ</h3>
      <p><strong>Quyển 1 (35 trang)</strong> — Nền móng lý thuyết: Phú Thái Vi (bài phú khai
      môn của tổ sư) + 50 cách cục kinh điển. Đây là tinh hoa được Trần Đoàn cô đọng lại.</p>

      <p><strong>Quyển 3 (135 trang)</strong> — Diễn giải 12 cung × 14 chính tinh = 168 combos.
      Đây là phần áp dụng — khi sao X tọa cung Y thì có ý nghĩa gì.</p>

      <p><strong>Quyển 4 (91 trang)</strong> — 60+ lá số cổ kim với phân tích của Trần Đoàn:
      Khổng Tử, Lý Bạch, Bạch Khởi, Mã Viện, Bạch Cư Dị, các vua Đường-Tống... Đây là
      "training set" để hiểu sách áp dụng vào đời thực thế nào.</p>

      <p><strong>Quyển 2 (~70 trang)</strong> — An sao + cách lập 12 cung — bảng quyết
      lập Mệnh-Thân-Cục-Tử Vi-14 chính tinh-6 phụ tinh-7 sát tinh-12 sao Thái Tuế-Tam Thai Bát Tọa...
      Ấn bản BỘ này <strong>in đầy đủ Quyển 2</strong> để Anh có tài liệu tham chiếu khi cần verify
      engine YI-CHRONOS hoặc lập lá số thủ công.</p>

      <h3>Paradigm bất di bất dịch (Iron Rule #6)</h3>
      <blockquote>
        Tử Vi = ĐỌC ĐỒNG DẠNG, KHÔNG predict.<br>
        Lá số là tấm gương phản chiếu cấu trúc tâm-thân-thiên,<br>
        không phải bản án tương lai.
      </blockquote>

      <h3>Pipeline biên soạn (Bookflow v2.0)</h3>
      <ol>
        <li>OCR layout-aware 346 trang PDF gốc Trung văn</li>
        <li>Phân quyển chính xác qua mục lục markers</li>
        <li>Dịch 2-layer: Hán-Việt + Luận giải tiếng Việt hiện đại</li>
        <li>Trích structured (DeepSeek-chat, JSON mode strict):
            <strong>985 cách cục + 576 concepts</strong> với truy nguyên trang</li>
        <li>Tóm tắt VN dễ hiểu (MiniMax-M2): mỗi trang 1 paragraph</li>
        <li>Compile PDF (WeasyPrint, Times font, A4)</li>
      </ol>

      <p>Tổng chi phí biên soạn: <strong>~$0.50 DeepSeek + $0 MiniMax</strong> (~15 phút wall-time).</p>
    </section>
    """


def volume_divider(han: str, title: str, sub: str) -> str:
    return f"""
    <div class="volume-divider">
      <p class="han">{han}</p>
      <h1>{title}</h1>
      <p class="vol-sub">{sub}</p>
    </div>
    """


def section_box_appendix() -> str:
    """Bảng tra cứu tổng hợp 985 cách + 576 concepts."""
    cach = json.loads((ROOT / "data/yi_publishing/q1_tuvi/master/cach_cuc_index.json").read_text())
    parts = ['<section><h2>Phụ lục — Bảng tra cứu tổng hợp</h2>']
    parts.append('<h3>985 cách cục (A-Z)</h3>')
    parts.append('<div class="index-grid">')
    for n in sorted(cach.keys(), key=lambda x: x.lower()):
        srcs = cach[n].get("sources", [])
        page_str = f"p{srcs[0]['page']}" if srcs else "-"
        occ = cach[n].get("occurrences", 0)
        occ_str = f" <em>×{occ}</em>" if occ >= 2 else ""
        parts.append(f'<p>{_html.escape(n)} <em>({page_str})</em>{occ_str}</p>')
    parts.append('</div></section>')
    return "\n".join(parts)


def build_html() -> str:
    return "\n".join([
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">',
        '<title>Tử Vi Đẩu Số Toàn Thư — Bộ 3 Quyển</title>',
        f'<style>{CSS}</style></head><body>',
        section_box_cover(),
        section_box_toc(),
        section_box_preface(),

        # Q1
        volume_divider("卷一", "Quyển Thứ Nhất", "Phú Thái Vi & Cách Cục Kinh Điển"),
        section_phu_thai_vi(),
        section_cach_cuc_top(50),
        q1_concepts(),
        q1_cach_index(),

        # Q2
        volume_divider("卷二", "Quyển Thứ Hai", "An Sao & 12 Cung"),
        q2_pages(),

        # Q3
        volume_divider("卷三", "Quyển Thứ Ba", "Diễn Giải 12 Cung × 14 Chính Tinh"),
        q3_pages(),

        # Q4
        volume_divider("卷四", "Quyển Thứ Tư", "60+ Lá Số Cổ Kim & Phân Tích Mẫu"),
        q4_pages(),

        # Appendix
        volume_divider("附錄", "Phụ Lục", "Bảng Tra Cứu Tổng Hợp"),
        section_box_appendix(),

        '<div class="book-footer">YI-CHRONOS · Tử Vi Đẩu Số Toàn Thư — Bộ 3 Quyển · Ấn bản 1.0</div>',
        '</body></html>',
    ])


def generate_pdf() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "tu-vi-bo-toan-thu.pdf"
    (OUT_DIR / "tu-vi-bo-toan-thu.html").write_text(build_html())
    from weasyprint import HTML
    HTML(string=build_html()).write_pdf(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    p = generate_pdf()
    print(f"✅ PDF: {p}")
    print(f"   Size: {p.stat().st_size / 1024 / 1024:.2f} MB")
