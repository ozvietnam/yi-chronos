#!/usr/bin/env python3
"""Compile sách 'Hoàng Cực Số Đồ' → PDF (Bookflow v2, Iron Rule #5).

Thứ tự chắc chắn: BÌA → MỤC LỤC → LỜI MỞ → 5 chương (kèm đồ SVG).
- Bìa + lời mở = HTML thuần (tự kiểm soát).
- Chương = pandoc (markdown → HTML fragment).
- Mục lục = trích <nav id="TOC"> từ một lần pandoc --standalone --toc.
CJK (chữ Hán trong đồ + văn bản) render qua font hệ thống — WeasyPrint 68 OK.
"""
from __future__ import annotations
import re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SACH = HERE / "sach"
VERSION = "v1.0"
PUB_DATE = "2026-06-15"
OUT_PDF = HERE / f"Hoang-Cuc-So-Do-{VERSION}.pdf"

CHAPTERS = [
    "chuong-01-bang-so-khoi-chung.md",
    "chuong-02-bien-hoa-dai-tieu-tu-tuong.md",
    "chuong-03-tri-loan-van-nam.md",
    "chuong-04-van-192-doi-anh.md",
    "chuong-05-nam-que.md",
]

COVER_HTML = f"""<div class="cover">
  <h1 class="cover-title">HOÀNG CỰC SỐ ĐỒ</h1>
  <div class="cover-zh">皇極經世</div>
  <div class="cover-sub">Đọc cấu trúc trời – đất – người bằng lưới số</div>
  <div class="cover-line">Nguyên · Hội · Vận · Thế — và đời một người trong mùa của trời đất</div>
  <div class="cover-epi">"Một vật vốn có một thân, một thân lại có một trời đất.<br/>
  Biết rằng muôn việc đều sẵn nơi ta, mới dám đặt nền móng cho Tam Tài."<br/>
  <span class="cover-epi-src">— Thiệu Khang Tiết, Vận Pháp Thi</span></div>
  <div class="cover-authors">Dịch &amp; biên soạn: <b>Anh Thắng</b> &amp; <b>học trò</b> (YI-Chronos)<br/>
  Phỏng theo 《皇极经世书今说》bộ trọn Thượng–Hạ · {VERSION} · {PUB_DATE}</div>
</div>"""

PARADIGM_HTML = """<div class="paradigm">
  <h1 class="nobreak">Lời mở — đọc đồng dạng, KHÔNG phải bói</h1>
  <p>Sách này theo đúng tuyên ngôn của Tổ sư (Iron Rule #4/#6): Hoàng Cực Kinh Thế
  <b>không phải công cụ tiên tri</b>. Nó là <b>môn đọc đồng dạng</b> — cấu trúc vũ trụ,
  cấu trúc thời, cấu trúc người <b>cùng một khuôn</b>, lồng nhau ở mọi cỡ. Số và đồ ở đây
  là <b>tấm gương soi cấu trúc</b>, không phải lời phán cát–hung.</p>
  <p>Mỗi chương theo kỷ luật <b>đọc → hiểu → vẽ lại</b>: chỉ vẽ lại được thì mới chắc đã
  hiểu. Mỗi đồ đều dựng từ engine <code>hoang_cuc</code> (số liệu thật, đã neo mốc 304 CN =
  thế 2245 theo chính văn), và mỗi chỗ chưa chắc đều <b>nói thẳng GIỚI HẠN</b>, không bịa.</p>
</div>"""

CSS = """
@page { size: A4; margin: 2.2cm 2cm 2.4cm 2cm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #998; }
  @top-left { content: string(chap); font-size: 8.5pt; color: #aa9; font-style: italic; } }
@page :first { margin: 0; @bottom-center { content: none; } @top-left { content: none; } }
body { font-family: 'Times New Roman','Songti SC','STSong','PingFang SC',serif;
  line-height: 1.58; color: #221c14; font-size: 11.5pt; }
h1 { string-set: chap content(text); page-break-before: always; color: #7a3410;
  font-size: 21pt; margin: 0.2cm 0 0.3cm; border-bottom: 2px solid #c9a13b; padding-bottom: .15em; }
h1.nobreak { page-break-before: avoid; }
h2 { color: #8a4a14; font-size: 14.5pt; margin-top: 1.1em; }
h3 { color: #a8621c; font-size: 12pt; margin-top: .8em; }
p, li { text-align: justify; }
blockquote { background: #fbf4e2; border-left: 3px solid #c9a13b; padding: .5em .9em;
  margin: .7em 0; color: #5c4a2c; font-style: italic; }
table { border-collapse: collapse; width: 100%; margin: .6em 0; font-size: 10pt; }
th, td { border: 1px solid #d8be86; padding: .3em .55em; text-align: left; vertical-align: top; }
th { background: #fbeecb; }
img { max-width: 100%; display: block; margin: .8em auto; page-break-inside: avoid; }
hr { border: 0; border-top: 1px dashed #d8be86; margin: 1.2em 0; }
a { color: #8a4a14; text-decoration: none; }
code { background: #f3e8c8; padding: 0 .25em; border-radius: 2px; font-size: .92em; }
/* bìa */
.cover { page-break-after: always; text-align: center; padding-top: 6.5cm; height: 100%; background: #fbf7ef; }
.cover-title { border: 0; color: #5a2d0c; font-size: 40pt; page-break-before: avoid; margin: 0 0 .2cm; }
.cover-zh { color: #7a5a2a; font-size: 22pt; letter-spacing: .1em; margin-bottom: .3cm; }
.cover-sub { color: #7a5a2a; font-size: 15pt; }
.cover-line { color: #8a6a3a; font-size: 12pt; margin-top: .5cm; }
.cover-epi { margin-top: 3cm; color: #6a4a2a; font-style: italic; font-size: 12pt; line-height: 1.7; }
.cover-epi-src { font-style: normal; color: #998; font-size: 10.5pt; }
.cover-authors { margin-top: 3cm; color: #555; font-size: 11pt; line-height: 1.6; }
.paradigm { page-break-after: always; }
/* mục lục */
#TOC { page-break-after: always; }
#TOC::before { content: "Mục lục"; display: block; font-size: 21pt; font-weight: bold;
  color: #7a3410; margin-bottom: .5cm; border-bottom: 2px solid #c9a13b; padding-bottom: .15em; }
#TOC ul { list-style: none; padding-left: 0; }
#TOC > ul > li { margin: .35em 0; font-weight: bold; color: #7a3410; }
#TOC ul ul { padding-left: 1.2em; }
#TOC ul ul li { font-weight: normal; color: #555; font-size: 10.5pt; margin: .1em 0; }
"""


def read_chapter(name: str) -> str:
    txt = (SACH / name).read_text(encoding="utf-8")
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end >= 0:
            txt = txt[end + 4:].lstrip()
    return txt


def rewrite_figs(md: str) -> str:
    def repl(m):
        p = (HERE / m.group(1)).resolve()
        if not p.exists():
            print(f"  ⚠ thiếu đồ: {m.group(1)}", file=sys.stderr)
        return f"](file://{p})"
    return re.sub(r"\]\(\.\./([a-z0-9_]+\.svg)\)", repl, md)


def pandoc(md_text: str, *extra) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_text); src = f.name
    out = src + ".html"
    subprocess.run(["pandoc", src, "-o", out, *extra], check=True)
    return Path(out).read_text(encoding="utf-8")


def main():
    chapters_md = "\n\n".join(rewrite_figs(read_chapter(c)) for c in CHAPTERS)

    # 1) chương → HTML fragment (đúng thứ tự, không TOC)
    chapters_html = pandoc(chapters_md)

    # 2) mục lục: chạy standalone+toc rồi trích <nav id="TOC">
    full = pandoc(chapters_md, "--standalone", "--toc", "--toc-depth=2",
                  "--metadata", "title=x", "-V", "lang=vi")
    m = re.search(r'<nav id="TOC".*?</nav>', full, re.DOTALL)
    toc_html = m.group(0) if m else '<nav id="TOC"></nav>'

    # 3) ghép: bìa → mục lục → lời mở → chương
    body = COVER_HTML + "\n" + toc_html + "\n" + PARADIGM_HTML + "\n" + chapters_html
    html = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            f'<title>Hoàng Cực Số Đồ {VERSION}</title><style>{CSS}</style></head>'
            f'<body>\n{body}\n</body></html>')
    html_path = OUT_PDF.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    print(f"[html] {html_path.name}: {len(html):,} bytes")

    venv = ROOT / ".venv" / "bin" / "python3"
    subprocess.run([str(venv), "-m", "weasyprint", str(html_path), str(OUT_PDF)], check=True)
    print(f"\n✅ PDF: {OUT_PDF}  ({OUT_PDF.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
