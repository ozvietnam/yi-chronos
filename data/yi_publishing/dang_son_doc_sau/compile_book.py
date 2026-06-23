"""Bookflow Iron #5 — compile 40 vòng đọc sâu Đằng Sơn + Đại tổng hợp → PDF xuất bản.

Cover → TOC → Lời mở (paradigm khoa-học-hóa) → Đại tổng hợp lá số (đồ hình SVG) →
40 vòng (T1 FULL 1-20 + T2 21-40) → Colophon. pandoc (md→HTML+TOC) + WeasyPrint (HTML→PDF).
Chạy:  python data/yi_publishing/dang_son_doc_sau/compile_book.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DESIGN = ROOT / "docs" / "design"
VERSION = "v1.0"
OUT_PDF = ROOT / "data" / "published" / f"Tu-Vi-Dang-Son-Doc-Sau-40-Vong-{VERSION}.pdf"
FIG_PNG = HERE / "dai-tong-hop.png"

EPIGRAPH = ("Đẩu số chí huyền chí vi, lý chỉ dị minh — "
            "ma quân là bạn đạo, giúp ta tu hành thành đạt.")

PARADIGM_MD = """\
# Lời mở — Phái khoa-học-hóa của Đằng Sơn {.nobreak}

Đằng Sơn dựng Tử Vi như một **chuỗi định lý suy từ âm dương**, không phải bảng tra
thuộc lòng. Cuốn này kết tinh **40 vòng đọc sâu** (mỗi vòng 18–20 trang, dừng đúc kết)
xuyên hai tập *Tử Vi Hoàn Toàn Khoa Học* — Tập 1 (nền) và Tập 2 (thần sát · Tuần Triệt).

**Ba trụ paradigm.** (1) Tử Vi *suy diễn được* từ âm dương — mọi sao đều có cái lý, luôn
hỏi "vì sao có sao này". (2) Ngũ hành chỉ là **phép tính gần đúng** của âm dương (ngũ giác
xấp xỉ vòng tròn) → đừng luận sinh-khắc cứng. (3) **Thần sát = tài Thiên-Địa**, không thể bỏ
(khác phái giản lược chỉ giữ 14 chính tinh + Tứ Hóa).

**Chín định lý** đã được mã hóa + kiểm bằng máy (`engine/tu_vi/dang_son_verify.py`, 21 test):
Lộc Tồn = kết hợp Tứ Hóa (đúng-lúc/đúng-chỗ); Kình–Đà phản đề (quá sớm / quá trễ); Khôi Việt
cứu chính tinh cực-hãm-hóa-Kỵ; Hỏa Linh thủy-hỏa giao thoa; vòng Thái Tuế = chu kỳ biểu kiến
5 hành tinh; Đào-Mã-Cái-Sát = vòng Trường Sinh chi-năm; Cô Quả = đạo hạnh cho bậc chân tu;
Tuần Triệt = căn-ngăn / cắt-đứt (Mão Dậu nhị không = trục tu hành); vòng Trường Sinh = nạp-hành
(Thổ đi cùng Thủy).

**Cách đọc — đồng dạng, không bói (Iron Rule #4/#6/#8).** Mọi tầng là TÍNH / cấu-trúc / cơ-hội
(disposition), không phải sấm kết cục. *Mệnh là động từ* — "cấu trúc này vận hành tốt nhất khi…",
không "số anh là…". Chính Tổ chốt: *người tu thành tựu hay không còn lệ thuộc nhiều yếu tố khác.*
Lá số cho nguyên-liệu và cánh-cửa; bước vào là việc của đương sự.

# Đại tổng hợp lá số (kết tinh 40 vòng) {.nobreak}

Tổng hợp cấu trúc lá số founder dưới lăng kính Đằng Sơn — THỂ (Mệnh chủ) / DỤNG (chính tinh
Mệnh) / hậu-thiên (Thân chủ) + arc tu-dưỡng 8 đường + cân bằng trung thực. Đọc TÍNH, không predict.

![Đại tổng hợp lá số](file://%FIG%)
"""

COLOPHON_MD = """\
# Colophon {.nobreak}

*Tử Vi Hoàn Toàn Khoa Học — Đọc Sâu 40 Vòng + Đại Tổng Hợp Lá Số* — bản %VER%.

Nguyên tác: **Đằng Sơn** (Cao Hùng, Đài Loan; kế thừa Tạ Phồn Trị). Đọc · dịch · đúc kết ·
biên soạn · kiểm chứng bằng máy: **Anh Thắng + Claude** (YI-CHRONOS), 2026-06-23.

Kỷ luật: mỗi vòng 18–20 trang → dừng đúc kết → cast lá số thật → kiểm định lý bằng test →
commit độc lập. Wiki corpus `tuvi-dang-son` (270 concepts). 9 định lý / 21 test
(`engine/tu_vi/dang_son_verify.py`). Đồ hình dựng từ `engine/tu_vi/render_dai_tong_hop.py`.

Đọc đồng dạng, không bói. Giữ nguyên văn cổ + nghi thức (tiếc dê tiếc lễ) — biểu tượng là hạt
giống phục hưng.
"""


def cover_html() -> str:
    return f"""<div class="cover">
  <h1 class="cover-title">Tử Vi Hoàn Toàn Khoa Học</h1>
  <div class="cover-sub">Đọc Sâu 40 Vòng &amp; Đại Tổng Hợp Lá Số</div>
  <div class="cover-line">Nguyên tác: Đằng Sơn &nbsp;·&nbsp; kế thừa Tạ Phồn Trị</div>
  <div class="cover-epi">"{EPIGRAPH}"
    <div class="cover-epi-src">— Đằng Sơn, Tử Vi Hoàn Toàn Khoa Học</div></div>
  <div class="cover-authors">Đọc · dịch · đúc kết · biên soạn: Anh Thắng + Claude (YI-CHRONOS)<br/>
    {VERSION} · 2026-06-23 · ~738 trang gốc / 40 vòng / 9 định lý kiểm máy</div>
</div>"""


CSS = """
@page { size: A4; margin: 2.2cm 2cm 2.4cm 2cm;
  @bottom-center { content: counter(page); font-size: 9pt; color: #998; }
  @top-left { content: string(chap); font-size: 8.5pt; color: #aa9; font-style: italic; } }
@page :first { margin: 0; @bottom-center { content: none; } @top-left { content: none; } }
body { font-family: 'Times New Roman','Songti SC','PingFang SC',serif;
  line-height: 1.55; color: #221c14; font-size: 11pt; }
h1 { string-set: chap content(text); page-break-before: always; color: #7a3410;
  font-size: 19pt; margin: 0.2cm 0 0.3cm; border-bottom: 2px solid #c9a13b; padding-bottom: .15em; }
h1.nobreak { page-break-before: always; }
h2 { color: #8a4a14; font-size: 13pt; margin-top: 1em; }
h3 { color: #a8621c; font-size: 11.5pt; margin-top: .7em; }
h4 { color: #9a6b27; font-size: 10.8pt; margin-top: .6em; }
p, li { text-align: justify; }
blockquote { background: #fbf4e2; border-left: 3px solid #c9a13b; padding: .4em .8em;
  margin: .6em 0; color: #5c4a2c; font-style: italic; }
table { border-collapse: collapse; width: 100%; margin: .5em 0; font-size: 9.5pt; }
th, td { border: 1px solid #d8be86; padding: .25em .5em; text-align: left; vertical-align: top; }
th { background: #fbeecb; }
img { max-width: 100%; display: block; margin: .8em auto; page-break-inside: avoid; }
hr { border: 0; border-top: 1px dashed #d8be86; margin: 1em 0; }
a { color: #8a4a14; text-decoration: none; }
code { background: #f3e8c8; padding: 0 .25em; border-radius: 2px; font-size: .9em; }
.cover { page-break-after: always; text-align: center; padding-top: 5.5cm; height: 100%; background: #fbf7ef; }
.cover-title { border: 0; color: #5a2d0c; font-size: 34pt; page-break-before: avoid; margin: 0 0 .2cm; }
.cover-sub { color: #7a5a2a; font-size: 17pt; }
.cover-line { color: #8a6a3a; font-size: 12pt; margin-top: .4cm; }
.cover-epi { margin-top: 2.6cm; color: #6a4a2a; font-style: italic; font-size: 12pt; line-height: 1.7; padding: 0 2cm; }
.cover-epi-src { font-style: normal; color: #998; font-size: 10.5pt; margin-top: .3cm; }
.cover-authors { margin-top: 2.4cm; color: #555; font-size: 10.5pt; line-height: 1.6; }
#TOC { page-break-after: always; }
#TOC::before { content: "Mục lục"; display: block; font-size: 19pt; font-weight: bold;
  color: #7a3410; margin-bottom: .5cm; border-bottom: 2px solid #c9a13b; padding-bottom: .15em; }
#TOC ul { list-style: none; padding-left: 0; }
#TOC > ul > li { margin: .25em 0; font-weight: bold; color: #7a3410; font-size: 10pt; }
#TOC ul ul { padding-left: 1.1em; }
#TOC ul ul li { font-weight: normal; color: #666; font-size: 9pt; margin: .05em 0; }
"""


def journals_in_order() -> list[Path]:
    t1 = sorted(DESIGN.glob("tu-vi-dang-son-FULL-vong-*.md"),
                key=lambda p: int(re.search(r"vong-(\d+)", p.name).group(1)))
    t2 = sorted(DESIGN.glob("tu-vi-dang-son-T2-vong-*.md"),
                key=lambda p: int(re.search(r"vong-(\d+)", p.name).group(1)))
    return t1 + t2


def render_figure() -> bool:
    try:
        import cairosvg
        from engine.tu_vi import cast_la_so
        from engine.tu_vi.dai_tong_hop import dai_tong_hop
        from engine.tu_vi.render_dai_tong_hop import to_svg
        la = cast_la_so(lunar_month=4, lunar_day=22, hour_branch="Tý",
                        year_stem="Mậu", year_branch="Thìn", gender="nam")
        svg = to_svg(dai_tong_hop(la))
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(FIG_PNG), output_width=1700)
        return True
    except Exception as e:  # pragma: no cover
        print(f"  ⚠ không render được đồ hình: {e}", file=sys.stderr)
        return False


def pandoc(md_text: str, *extra) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_text)
        src = f.name
    out = src + ".html"
    subprocess.run(["pandoc", src, "-o", out, *extra], check=True)
    return Path(out).read_text(encoding="utf-8")


def main():
    have_fig = render_figure()
    paradigm = PARADIGM_MD.replace("%FIG%", str(FIG_PNG))
    if not have_fig:
        paradigm = paradigm.replace("![Đại tổng hợp lá số](file://%FIG%)",
                                    "*(đồ hình đại tổng hợp — xem bản web)*").replace("%FIG%", "")
    journals = journals_in_order()
    print(f"[journals] {len(journals)} vòng")
    body_md = paradigm + "\n\n" + "\n\n".join(p.read_text(encoding="utf-8") for p in journals) \
        + "\n\n" + COLOPHON_MD.replace("%VER%", VERSION)

    chapters_html = pandoc(body_md)
    full = pandoc(body_md, "--standalone", "--toc", "--toc-depth=1",
                  "--metadata", "title=x", "-V", "lang=vi")
    m = re.search(r'<nav id="TOC".*?</nav>', full, re.DOTALL)
    toc_html = m.group(0) if m else '<nav id="TOC"></nav>'

    html = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8">'
            f'<title>Tử Vi Đằng Sơn — Đọc Sâu 40 Vòng {VERSION}</title>'
            f'<style>{CSS}</style></head><body>\n'
            f'{cover_html()}\n{toc_html}\n{chapters_html}\n</body></html>')
    html_path = OUT_PDF.with_suffix(".html")
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    print(f"[html] {html_path.name}: {len(html):,} bytes")

    subprocess.run([sys.executable, "-m", "weasyprint", str(html_path), str(OUT_PDF)], check=True)
    print(f"\n✅ PDF: {OUT_PDF}  ({OUT_PDF.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
