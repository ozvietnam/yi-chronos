"""Compile "Mai Hoa Dịch Số — BỘ 5 QUYỂN ĐẦY ĐỦ" (nguyên tác Thiệu Khang Tiết).

Source: data/yi_restored/mai-hoa-dich-so-thieu-khang-tiet/content.md (672 pages)

5 quyển:
    Q1: p15-115   — Chu Dịch quái số · Bát quái tượng lệ
    Q2: p116-327  — Chiêm bốc huyền cơ (9 chiêm chuyên đề)
    Q3: p?         — đã có cuốn riêng (Mai Hoa Hành Đạo Toàn Thư v1.9, 613 trang)
    Q4: p328-458  — Chỉ mê phú · Huyền hoàng khắc ứng ca · Hoa áp phú
    Q5: p459-672  — Ngũ hành toàn bị · Lục thân hình thức · Bát quái biện

Output: data/published/mai-hoa-bo-5-quyen.pdf

Note: Q3 (Bát quái phương vị đồ + Quan mai chiêm quyết) đã có cuốn riêng nên trong
BỘ này chúng ta CHỈ in Q1+Q2+Q4+Q5 từ cuốn nguyên tác 672 trang. Q3 link reference.
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
MASTER = ROOT / "data/yi_publishing/mai_hoa_thamnhuan/master"
OUT_DIR = ROOT / "data/published"

Q1 = (15, 115)
Q2 = (116, 327)
Q4 = (328, 458)
Q5 = (459, 672)


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
  @top-right { content: "Mai Hoa Dịch Số — Bộ 5 Quyển"; font-size: 9pt; color: #9ca3af; font-style: italic; }
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
em { color: #6b7280; }
blockquote {
  margin: 0.8em 0; padding: 0.5em 1.2em;
  border-left: 3pt solid #f9a8d4; background: #fdf2f8; color: #4b5563; font-style: italic;
}

.cover { text-align: center; padding-top: 3cm; page-break-after: always; height: 24cm; }
.cover .han { font-size: 56pt; color: #831843; font-family: "Songti SC", serif; letter-spacing: 0.3em; margin: 0; }
.cover h1 { font-size: 32pt; margin-top: 0.4em; }
.cover .sub { font-size: 16pt; color: #6b7280; margin-top: 0.8em; font-style: italic; }
.cover .author { font-size: 13pt; color: #4b5563; margin-top: 3cm; line-height: 1.6; }
.cover .boxed-banner {
  display: inline-block; padding: 8pt 24pt; margin-top: 1cm;
  background: linear-gradient(135deg, #be185d, #ec4899); color: white;
  font-size: 12pt; font-weight: bold; letter-spacing: 0.1em; border-radius: 4pt;
}
.cover .meta { font-size: 11pt; color: #6b7280; margin-top: 1.5cm; line-height: 1.5; }

.toc { page-break-after: always; }
.toc ol { padding-left: 2em; }
.toc li { margin: 0.4em 0; font-size: 11pt; }
.toc .quyen { font-weight: 700; color: #831843; }

.preface { page-break-after: always; }

.volume-divider {
  page-break-before: always; page-break-after: always;
  text-align: center; padding-top: 8cm;
  background: linear-gradient(135deg, #fdf2f8, #fbcfe8); height: 24cm;
}
.volume-divider .han { font-size: 60pt; color: #831843; font-family: "Songti SC", serif; letter-spacing: 0.3em; margin: 0; }
.volume-divider h1 { font-size: 36pt; margin-top: 0.5em; color: #831843; }
.volume-divider .vol-sub { font-size: 18pt; color: #4b5563; margin-top: 1em; font-style: italic; }

.page-block { page-break-inside: auto; margin: 1em 0; padding-bottom: 0.5em;
              border-bottom: 0.5pt dashed #e5e7eb; }
.page-label { font-size: 9pt; color: #9ca3af; font-style: italic; margin-bottom: 0.3em; }
.page-text { white-space: pre-wrap; font-size: 10.5pt; line-height: 1.6; color: #1f2937; }
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

.index-grid { columns: 3; column-gap: 1.2em; font-size: 9.5pt; }
.index-grid p { margin: 0.1em 0; break-inside: avoid; }

.book-footer { margin-top: 3em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db;
               font-size: 8.5pt; color: #9ca3af; text-align: center; }
"""


def section_cover() -> str:
    today = time.strftime("%Y-%m-%d")
    return f"""
    <div class="cover">
      <p class="han">梅花易數</p>
      <h1>Mai Hoa Dịch Số</h1>
      <p class="sub">Bộ 5 Quyển — Ấn Bản Hoàn Chỉnh</p>
      <div class="boxed-banner">CUỐN BỘ NGUYÊN TÁC</div>
      <div class="author">
        Tác giả: <strong>Thiệu Khang Tiết</strong> (邵雍, 1011-1077)<br>
        Hiệu: Khang Tiết tiên sinh
      </div>
      <div class="meta">
        Dịch và biên soạn AI · YI-CHRONOS<br>
        Pipeline: DeepSeek-chat + MiniMax-M2 parallel · 655 trang processed<br>
        482 methods · 1,060 concepts trích xuất<br>
        Ấn bản BỘ 1.0 · {today}
      </div>
    </div>
    """


def section_toc() -> str:
    return """
    <section class="toc">
      <h2>Mục lục cuốn bộ</h2>
      <ol>
        <li class="quyen">Lời nói đầu cuốn bộ</li>
        <li class="quyen">Quyển 1 — Chu Dịch Quái Số · Bát Quái Tượng Lệ
          <ol>
            <li>Chu Dịch quái số, Ngũ hành sinh khắc</li>
            <li>Bát cung sở thuộc ngũ hành, Quái khí suy</li>
            <li>Thập thiên can, Thập nhị địa chi</li>
            <li>Bát quái tượng lệ, Chiêm pháp, Ngoạn pháp</li>
          </ol>
        </li>
        <li class="quyen">Quyển 2 — Chiêm Bốc Huyền Cơ (9 chiêm)
          <ol>
            <li>Chiêm quái tổng quyết</li>
            <li>Thiên thời, Gia trạch, Hôn nhân, Sinh sản chiêm</li>
            <li>Cầu danh, Giao dịch, Xuất hành chiêm</li>
            <li>Thất vật, Tật bệnh, Quan tụng, Phần mộ chiêm</li>
          </ol>
        </li>
        <li class="quyen">Quyển 3 — Bát Quái Phương Vị Đồ · Quan Mai Chiêm Quyết
          <ol>
            <li><em>Đã xuất bản riêng: Mai Hoa Hành Đạo Toàn Thư v1.9 (613 trang)</em></li>
            <li><em>data/published/Q3-mai-hoa-toan-thu-v1.9.pdf</em></li>
          </ol>
        </li>
        <li class="quyen">Quyển 4 — Chỉ Mê Phú · Huyền Hoàng Khắc Ứng Ca</li>
        <li class="quyen">Quyển 5 — Ngũ Hành Toàn Bị · Lục Thân Hình Thức</li>
        <li class="quyen">Phụ lục — Bảng tra cứu 482 methods + 1,060 concepts</li>
      </ol>
    </section>
    """


def section_preface() -> str:
    return """
    <section class="preface">
      <h2>Lời nói đầu cuốn bộ</h2>

      <p>Đây là ấn bản <strong>bộ 5 quyển</strong> đầu tiên của
      <strong>Mai Hoa Dịch Số</strong> (梅花易數) — kỳ thư của Thiệu Khang Tiết
      (1011-1077), nhà đại triết học đời Tống — được dịch và biên soạn hoàn chỉnh
      bằng AI cho người đọc Việt hiện đại.</p>

      <h3>Tại sao ấn bản này quan trọng</h3>
      <ul>
        <li>Mai Hoa Dịch Số là <em>"kỳ thư đích thực"</em> trong văn hóa Trung Hoa,
        cùng với Kinh Dịch và Ma Y tướng thuật được coi là Tam đại kỳ thư về tướng học
        và dự trắc học.</li>
        <li>Sách rất hiếm bản dịch tiếng Việt đầy đủ. Lưu truyền chủ yếu là Quyển 3
        (Bát quái phương vị đồ + Quan mai chiêm quyết).</li>
        <li>Ấn bản này dịch <strong>cả 5 quyển</strong> với nguyên văn + tóm tắt hiện đại
        + 482 methods + 1,060 concepts trích xuất có truy nguyên trang gốc.</li>
      </ul>

      <h3>Cấu trúc 5 quyển</h3>
      <p><strong>Quyển 1 (101 trang)</strong> — Nền móng: Chu Dịch quái số, Ngũ hành,
      Bát cung, Bát quái tượng lệ, Chiêm pháp, Ngoạn pháp.</p>

      <p><strong>Quyển 2 (210 trang)</strong> — Chiêm bốc huyền cơ: 9 chiêm chuyên đề
      (Thiên thời, Gia trạch, Hôn nhân, Sinh sản, Cầu danh, Giao dịch, Xuất hành,
      Thất vật, Tật bệnh, Quan tụng, Phần mộ). Đây là phần ứng dụng trực tiếp nhất.</p>

      <p><strong>Quyển 3 (xuất bản riêng — 613 trang)</strong> — Lý thuyết Thể-Dụng,
      Quan Mai chiêm quyết, Vạn vật phú. <em>Mai Hoa Hành Đạo Toàn Thư v1.9.</em></p>

      <p><strong>Quyển 4 (131 trang)</strong> — Chỉ mê phú, Huyền hoàng khắc ứng ca,
      Hoa áp phú, Thám huyền phú. Phú thi tổng kết.</p>

      <p><strong>Quyển 5 (213 trang)</strong> — Ngũ hành toàn bị, Lục thân hình thức,
      Bát quái biện, Quý thần — Hỉ thần, Dịch lý huyền vi, Cách vật chương.</p>

      <h3>Paradigm bất di bất dịch (Iron Rule #4)</h3>
      <blockquote>
        Mai Hoa Dịch Số = ĐỌC ĐỒNG DẠNG, không phải predict.<br>
        Quẻ là tấm gương phản chiếu khoảnh khắc.<br>
        Không phải bản án tương lai.
      </blockquote>

      <h3>Quy tắc Tâm (từ Vận Pháp Thi Q3)</h3>
      <ul>
        <li><em>"Không nghi không bói"</em> — chỉ bói khi thật sự nghi</li>
        <li><em>"Một việc chỉ bói một lần"</em> — bói lại = xúc phạm thần linh</li>
        <li><em>"Một câu hỏi → một phép → một quẻ"</em></li>
      </ul>

      <h3>Pipeline biên soạn (Bookflow v2.0)</h3>
      <ol>
        <li>OCR layout-aware 672 trang PDF gốc Việt-Hán</li>
        <li>Phân quyển qua TOC markers (Q3 đã xuất bản riêng)</li>
        <li>Trích structured methods + concepts (DeepSeek-chat JSON mode)</li>
        <li>Tóm tắt VN dễ hiểu (MiniMax-M2)</li>
        <li>Compile PDF (WeasyPrint, Times font, A4)</li>
      </ol>

      <p>Tổng chi phí biên soạn: <strong>~$0.44 DeepSeek + $0 MiniMax</strong>.</p>
    </section>
    """


def render_page_block(page_num: int, content: str) -> str:
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
    parts.append(f'<div class="page-label">━━━ Trang {page_num} (OCR) ━━━</div>')

    nhan_xet = meta.get("nhan_xet", "").strip()
    if nhan_xet:
        parts.append(f'<p><strong>Chủ đề:</strong> <em>{_esc(nhan_xet)}</em></p>')

    parts.append('<h4>Nguyên văn</h4>')
    parts.append(f'<div class="page-text">{_esc(content[:6000])}</div>')

    summary = meta.get("summary_vn", "").strip()
    if summary:
        parts.append(f'<h4>Tóm tắt hiện đại</h4>')
        parts.append(f'<div class="summary-vn">{_esc(summary)}</div>')

    methods = meta.get("methods", [])[:4]
    if methods:
        parts.append('<h4>Phương pháp / Quyết</h4>')
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


def render_quyen(pages_dict: dict[int, str], start: int, end: int) -> str:
    parts = []
    for p in range(start, end + 1):
        if p not in pages_dict:
            continue
        block = render_page_block(p, pages_dict[p])
        if block:
            parts.append(block)
    return "\n".join(parts)


def volume_divider(han: str, title: str, sub: str) -> str:
    return f"""
    <div class="volume-divider">
      <p class="han">{han}</p>
      <h1>{title}</h1>
      <p class="vol-sub">{sub}</p>
    </div>
    """


def section_appendix() -> str:
    """Bảng tra cứu 482 methods + 1060 concepts."""
    methods = json.loads((MASTER / "methods_index.json").read_text())
    parts = ['<section><h2>Phụ lục — Bảng tra cứu Methods</h2>']
    parts.append(f'<h3>482 phương pháp / quyết (A-Z)</h3>')
    parts.append('<div class="index-grid">')
    for n in sorted(methods.keys(), key=lambda x: x.lower()):
        m = methods[n]
        page = m.get("first_page", 0)
        occ = m.get("occurrences", 0)
        occ_str = f" <em>×{occ}</em>" if occ >= 2 else ""
        parts.append(f'<p>{_esc(n[:50])} <em>(p{page})</em>{occ_str}</p>')
    parts.append('</div></section>')
    return "\n".join(parts)


def build_html() -> str:
    pages = parse_pages()
    return "\n".join([
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">',
        '<title>Mai Hoa Dịch Số — Bộ 5 Quyển</title>',
        f'<style>{CSS}</style></head><body>',
        section_cover(),
        section_toc(),
        section_preface(),

        volume_divider("卷一", "Quyển Thứ Nhất", "Chu Dịch Quái Số · Bát Quái Tượng Lệ"),
        '<section><h2>Quyển 1</h2>',
        render_quyen(pages, *Q1),
        '</section>',

        volume_divider("卷二", "Quyển Thứ Hai", "Chiêm Bốc Huyền Cơ"),
        '<section><h2>Quyển 2</h2>',
        render_quyen(pages, *Q2),
        '</section>',

        volume_divider("卷三", "Quyển Thứ Ba", "Đã xuất bản riêng: Mai Hoa Hành Đạo Toàn Thư"),
        '<section><h2>Quyển 3 — tham chiếu</h2>'
        '<p>Quyển 3 (Bát quái phương vị đồ, Quan mai chiêm quyết, Thể-Dụng quyết, '
        'Vạn vật phú) đã được biên soạn riêng từ cuốn <em>Đồ giải Mai Hoa Dịch Số</em> '
        '(图解梅花易数) của Vương Hy Quý — <strong>613 trang A4, 10.25 MB</strong>.</p>'
        '<p>File: <code>data/published/Q3-mai-hoa-toan-thu-v1.9.pdf</code></p></section>',

        volume_divider("卷四", "Quyển Thứ Tư", "Chỉ Mê Phú · Huyền Hoàng Khắc Ứng Ca"),
        '<section><h2>Quyển 4</h2>',
        render_quyen(pages, *Q4),
        '</section>',

        volume_divider("卷五", "Quyển Thứ Năm", "Ngũ Hành Toàn Bị · Lục Thân Hình Thức"),
        '<section><h2>Quyển 5</h2>',
        render_quyen(pages, *Q5),
        '</section>',

        volume_divider("附錄", "Phụ Lục", "Bảng Tra Cứu Tổng Hợp"),
        section_appendix(),

        '<div class="book-footer">YI-CHRONOS · Mai Hoa Dịch Số — Bộ 5 Quyển · Ấn bản 1.0</div>',
        '</body></html>',
    ])


def generate_pdf() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "mai-hoa-bo-5-quyen.pdf"
    (OUT_DIR / "mai-hoa-bo-5-quyen.html").write_text(build_html())
    from weasyprint import HTML
    HTML(string=build_html()).write_pdf(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    p = generate_pdf()
    print(f"✅ PDF: {p}")
    print(f"   Size: {p.stat().st_size / 1024 / 1024:.2f} MB")
