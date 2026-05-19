"""Compile "Tử Vi Đẩu Số Toàn Thư — Quyển 2: An Sao & 12 Cung".

Q2 = source pages 65-126 = OCR p0080-p0141 (62 trang).
Nội dung: bảng quyết an mệnh, an sao chính tinh + phụ tinh + sát tinh + bộ 12 sao Thái Tuế,
         vòng tràng sinh, bảng cát hung từng sao theo cung.

Output: data/published/tu-vi-q2-an-sao.pdf
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

Q2_START = 80
Q2_END = 141


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
  @top-right { content: "Tử Vi Đẩu Số Toàn Thư — Q.2"; font-size: 9pt; color: #9ca3af; font-style: italic; }
}
@page :first { @top-right { content: ""; } @bottom-center { content: ""; } }

body { font-family: "Times New Roman", "Palatino", "Hoefler Text", "Baskerville", serif;
       font-size: 10.5pt; line-height: 1.55; color: #1f2937; }
h1 { font-size: 26pt; text-align: center; color: #0c4a6e; margin: 0 0 0.4em; letter-spacing: -0.02em; }
h2 { font-size: 17pt; color: #0c4a6e; border-bottom: 1.5pt solid #7dd3fc; padding-bottom: 0.2em;
     margin: 1.8em 0 0.8em; page-break-after: avoid; }
h3 { font-size: 13pt; color: #0369a1; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h4 { font-size: 11pt; color: #0369a1; margin: 0.8em 0 0.3em; }
p { text-align: justify; margin: 0.4em 0; }
blockquote {
  margin: 0.8em 0; padding: 0.5em 1.2em;
  border-left: 3pt solid #7dd3fc; background: #f0f9ff; color: #4b5563; font-style: italic;
}

.cover { text-align: center; padding-top: 4cm; page-break-after: always; }
.cover .han { font-size: 42pt; color: #0c4a6e; font-family: "Songti SC", serif; letter-spacing: 0.2em; margin: 0; }
.cover h1 { font-size: 28pt; margin-top: 0.3em; }
.cover .sub { font-size: 14pt; color: #6b7280; margin-top: 0.8em; font-style: italic; }
.cover .author { font-size: 12pt; color: #4b5563; margin-top: 2.5cm; }
.cover .meta { font-size: 10pt; color: #6b7280; margin-top: 1.5cm; }

.preface { page-break-after: always; }

.phu-line { page-break-inside: avoid; margin: 0.5em 0; }
.phu-line .hv { font-style: italic; color: #4b5563; }
.phu-line .lg { color: #1f2937; padding-left: 1.5em; border-left: 2pt solid #bae6fd; margin-top: 0.2em; }

.page-block { page-break-inside: auto; margin: 1em 0; padding-bottom: 0.5em; border-bottom: 0.5pt dashed #e5e7eb; }
.page-label { font-size: 9pt; color: #9ca3af; font-style: italic; margin-bottom: 0.3em; }
.summary-vn {
  background: #f0f9ff; border-left: 3pt solid #7dd3fc;
  padding: 6pt 10pt; margin: 0.4em 0; font-size: 10pt; line-height: 1.55; border-radius: 3pt;
}

.cc-card {
  border: 0.5pt solid #e5e7eb; border-left: 3pt solid #94a3b8;
  border-radius: 4pt; padding: 8pt 10pt; margin: 6pt 0; page-break-inside: avoid;
}
.cc-thượng { border-left-color: #10b981; }
.cc-trung  { border-left-color: #f59e0b; }
.cc-hạ     { border-left-color: #f97316; }
.cc-phá    { border-left-color: #ef4444; }
.cc-head { display: flex; justify-content: space-between; margin-bottom: 0.2em; align-items: baseline; }
.cc-level { font-size: 9pt; text-transform: uppercase; color: #6b7280; font-weight: 600; }
.cc-evi { font-size: 9.5pt; color: #6b7280; margin: 0.2em 0; font-style: italic; }
.cc-y { font-size: 10pt; margin-top: 0.3em; }

.book-footer { margin-top: 3em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db;
               font-size: 8.5pt; color: #9ca3af; text-align: center; }
"""


def section_cover() -> str:
    today = time.strftime("%Y-%m-%d")
    return f"""
    <div class="cover">
      <p class="han">紫微斗數全書·卷二</p>
      <h1>Tử Vi Đẩu Số Toàn Thư</h1>
      <p class="sub">Quyển 2 — An Sao & 12 Cung</p>
      <div class="author">
        Tác giả: <strong>Hi Di Trần tiên sinh</strong> (陳摶, ~872–989)<br>
        Bổ tập: Phan Hy Doãn · Tham duyệt: Dương Nhất Vũ
      </div>
      <div class="meta">
        Dịch và biên soạn AI · YI-CHRONOS<br>
        Phương pháp: DeepSeek-chat + MiniMax-M2 parallel<br>
        Phạm vi: 62 trang OCR (p0080-p0141)<br>
        Đóng góp Q2: 208 cách cục + 125 concepts mới<br>
        Ấn bản 1.0 · {today}
      </div>
    </div>
    """


def section_preface() -> str:
    return """
    <section class="preface">
      <h2>Lời nói đầu Quyển 2</h2>
      <p>Sau Quyển 1 đặt nền lý thuyết (Phú Thái Vi + cách cục), Quyển 2 trình bày
      <strong>cách an sao</strong> — phương pháp lập lá số chính xác.</p>

      <h3>Nội dung chính</h3>
      <ul>
        <li><strong>An Mệnh cung + Thân cung</strong> (theo tháng và giờ sinh)</li>
        <li><strong>An Mệnh chủ + Thân chủ + Đẩu Quân</strong></li>
        <li><strong>Cục số</strong> (Thủy Nhị / Mộc Tam / Kim Tứ / Thổ Ngũ / Hỏa Lục) — định vị Tử Vi</li>
        <li><strong>An 14 chính tinh</strong> (Tử Vi → 13 sao còn lại)</li>
        <li><strong>An 6 phụ tinh</strong>: Tả Phụ, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt</li>
        <li><strong>An 7 sát tinh</strong>: Kình Dương, Đà La, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp, Lộc Tồn</li>
        <li><strong>An bộ 12 sao Thái Tuế</strong>: Thái Tuế · Thiếu Dương · Thiếu Âm · Tang Môn · Bạch Hổ · Quan Phù · Tử Phù · Long Đức · Phúc Đức · Điếu Khách · Tiểu Hao · Phi Liêm</li>
        <li><strong>An các sao phụ trợ</strong>: Tam Thai · Bát Tọa · Thiên Khốc · Thiên Hư · Long Trì · Phượng Các...</li>
        <li><strong>Tứ Hóa</strong> (Lộc/Quyền/Khoa/Kỵ) theo Thiên Can năm sinh</li>
        <li><strong>Đại Vận, Tiểu Hạn, Lưu Niên</strong></li>
      </ul>

      <blockquote>
        "An Mệnh chủ: Tý → Tham Lang. Sửu, Hợi → Cự Môn. Dần, Tuất → Lộc Tồn..."<br>
        — Q2 An Mệnh chủ quyết
      </blockquote>

      <h3>YI-CHRONOS engine implementation</h3>
      <p>Quyển 2 này đã được implement dưới dạng code Python trong <code>engine/tu_vi/an_sao.py</code> —
      cho phép lập lá số instant không cần tra bảng thủ công.</p>

      <p><strong>Engine functions</strong> tương ứng với từng quyết trong Q2:</p>
      <ul>
        <li><code>cast_la_so()</code> — orchestrator chính</li>
        <li><code>cung_menh_index()</code> + <code>cung_than_index()</code> — Q2 p65-67</li>
        <li><code>menh_chu()</code> + <code>than_chu()</code> — Q2 p90</li>
        <li><code>dau_quan()</code> — Q2 An Đẩu Quân quyết</li>
        <li><code>cuc_so()</code>, <code>tu_vi_position()</code>, <code>place_14_chinh_tinh()</code></li>
        <li><code>tu_hoa_assignments()</code></li>
        <li><code>dai_van_trajectory()</code> + <code>tieu_han_for_age()</code></li>
      </ul>

      <p>Ấn bản này dùng làm <strong>tài liệu tham chiếu</strong> để verify engine + bổ sung
      các bảng quyết chưa có (12 sao Thái Tuế, Tam Thai Bát Tọa...).</p>
    </section>
    """


def section_pages() -> str:
    parts = ['<section><h2>Cách an sao theo trang</h2>']
    for page in range(Q2_START, Q2_END + 1):
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
        cach_cuc = meta.get("cach_cuc", [])[:6]

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

        if cach_cuc:
            parts.append('<h4>Bảng quyết / cách trích xuất</h4>')
            for c in cach_cuc:
                lv = c.get("cap_do", "?")
                cls = f"cc-{lv.split()[0]}"
                parts.append(f'<div class="cc-card {cls}">')
                parts.append(f'  <div class="cc-head"><strong>{_esc(c.get("ten",""))}</strong>'
                             f'<span class="cc-level">{_esc(lv)}</span></div>')
                bc = c.get("bang_chung_text", "") or c.get("dieu_kien", "")
                if bc:
                    parts.append(f'  <div class="cc-evi">"{_esc(bc[:200])}"</div>')
                if c.get("y_nghia"):
                    parts.append(f'  <div class="cc-y">{_esc(c["y_nghia"][:280])}</div>')
                parts.append('</div>')

        parts.append('</div>')

    parts.append('</section>')
    return "\n".join(parts)


def build_html() -> str:
    return "\n".join([
        '<!doctype html><html lang="vi"><head><meta charset="utf-8">',
        '<title>Tử Vi Đẩu Số Toàn Thư — Quyển 2</title>',
        f'<style>{CSS}</style></head><body>',
        section_cover(),
        section_preface(),
        section_pages(),
        '<div class="book-footer">YI-CHRONOS · Tử Vi Đẩu Số Toàn Thư — Quyển 2 · Ấn bản 1.0</div>',
        '</body></html>',
    ])


def generate_pdf() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT_DIR / "tu-vi-q2-an-sao.pdf"
    (OUT_DIR / "tu-vi-q2-an-sao.html").write_text(build_html())
    from weasyprint import HTML
    HTML(string=build_html()).write_pdf(str(pdf_path))
    return pdf_path


if __name__ == "__main__":
    p = generate_pdf()
    print(f"✅ PDF: {p}")
    print(f"   Size: {p.stat().st_size / 1024:.1f} KB")
