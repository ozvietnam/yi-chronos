"""Export master PDF — gộp 5 bản Word của founder thành 1 sách xuất bản.

Pipeline: markdown master → pandoc → HTML → WeasyPrint → PDF A4
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/ozvietnamdesktop/Desktop/yi")
PUB = PROJECT_ROOT / "data/published"

# Order of chapters in master PDF
CHAPTERS = [
    ("Founder_PheMenhSau_V4_Q4Enriched.md", "I. PHÊ MỆNH SÂU — Tử Vi Đẩu Số Chính Thống", "Theo 10 BƯỚC methodology Trần Đoàn (Q4 p0266)"),
    ("Founder_CDK_TongDoanCuocDoi.md", "II. TỔNG ĐOÁN CUỘC ĐỜI — Chiếu Đởm Kinh Synthesis", "Synthesis CƠ + BIẾN, 6 sections narrative"),
    ("Founder_CDK_12Cung_VietThuan.md", "III. 12 CUNG CDK — Tiên Thiên Chi Tiết", "Mỗi cung 3 lớp: Bản chất + Sao + Áp dụng"),
    ("Founder_CDK_DaiHan_8Vong.md", "IV. ĐẠI HẠN 8 VÒNG — 80 Năm Cuộc Đời", "Mỗi vòng 10 năm: Tổng quan + Cơ hội + Lời khuyên"),
    ("Founder_CDK_LuuNien_10nam.md", "V. LƯU NIÊN 10 NĂM — Vận Khí Từng Năm 2026-2035", "Can-chi + Lưu Thái Tuế + Tương tác Đại Hạn"),
]


def build_master_markdown() -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    lines = [
        "---",
        "title: 'TỔNG ĐOÁN MỆNH — BỘ HOÀN CHỈNH'",
        "subtitle: 'Anh (Founder) · sinh 05/06/1988 23:30 · Mệnh chủ Vũ Khúc'",
        "author: 'YI-CHRONOS — Nhà xuất bản Đông phương học AI-driven'",
        f"date: '{today}'",
        "documentclass: book",
        "papersize: a4",
        "fontsize: 11pt",
        "geometry:",
        "  - margin=2cm",
        "  - top=2.5cm",
        "  - bottom=2.5cm",
        "---",
        "",
        "# Lời mở đầu",
        "",
        "> _\"Đẩu số chí huyền chí vi, lý chỉ dị minh. Cẩu hoặc bất sát kỳ cơ, cánh vong kỳ biến, tắc số chi tạo hóa viễn hĩ.\"_",
        "> ",
        "> — **Trần Đoàn** (Hi Di tiên sinh), Phú Thái Vi",
        "",
        "Bộ sách này gồm **5 chương** tổng đoán đầy đủ về mệnh của chủ nhân:",
        "",
        "1. **Phê mệnh sâu** theo 10 bước Trần Đoàn (TVĐS chính thống Bắc phái)",
        "2. **Tổng đoán cuộc đời** Chiếu Đởm Kinh (synthesis CƠ + BIẾN)",
        "3. **12 cung CDK** chi tiết (lớp CƠ tiên thiên)",
        "4. **Đại Hạn 8 vòng** — 80 năm cuộc đời (lớp BIẾN dài)",
        "5. **Lưu Niên 10 năm** — 2026-2035 (lớp BIẾN ngắn)",
        "",
        "## Paradigm — Iron Rule #6 YI-CHRONOS",
        "",
        "> Tử Vi là môn **ĐỌC ĐỒNG DẠNG**, KHÔNG dự đoán cứng.",
        "> ",
        "> Lá số chỉ là tấm gương phản chiếu cấu trúc tâm-thiên-thân tại điểm sinh.",
        "> Đại Hạn là nhịp thời gian. Người là người cầm la bàn — biến thông trong tâm là then chốt.",
        "",
        "## Đa trường phái — Iron Rule #3",
        "",
        "Hai trường phái song hành cho cùng một lá số:",
        "",
        "| | **TVĐS Bắc Phái** (chính thống) | **Chiếu Đởm Kinh** (phái khác) |",
        "|---|---|---|",
        "| Sách gốc | Tử Vi Đẩu Số Toàn Thư Q1-Q3 | Q4 p0269-p0299 |",
        "| Số sao | 14 chính tinh + Tứ Hóa + phụ-sát | 18 Phi Tinh |",
        "| Convention | Âm-Dương chính thống | Âm-Dương **ĐẢO** |",
        "| Cung Mệnh founder | **Tỵ** (Thiên Đồng + Lộc Tồn) | **Dậu** (Quý/Trượng/Khốc) |",
        "| Mệnh chủ founder | **Vũ Khúc** (Q.2 Phú Thái Vi) | (CDK không dùng) |",
        "",
        "Cả 2 đều ĐÚNG trong paradigm riêng. Đối chiếu chéo = tăng độ chính xác.",
        "",
        "\\newpage",
        "",
    ]

    for idx, (filename, title, subtitle) in enumerate(CHAPTERS, 1):
        p = PUB / filename
        if not p.exists():
            print(f"⚠ Missing: {filename}")
            continue
        content = p.read_text(encoding="utf-8")
        # Strip individual header (we'll add ours)
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"_{subtitle}_")
        lines.append("")
        lines.append("---")
        lines.append("")
        # Promote chapter content's H1 to H2, etc. (shift all headings down 1 level)
        for line in content.split("\n"):
            if line.startswith("# "):
                lines.append("## " + line[2:])
            elif line.startswith("## "):
                lines.append("### " + line[3:])
            elif line.startswith("### "):
                lines.append("#### " + line[4:])
            else:
                lines.append(line)
        lines.append("")
        lines.append("\\newpage")
        lines.append("")

    # Footer chapter
    lines.extend([
        "# 🙏 Lời kết người biên soạn",
        "",
        "Bộ sách này được biên soạn bởi **YI-CHRONOS** — nhà xuất bản Đông phương học AI-driven, dùng:",
        "",
        "- **DeepSeek V4 Pro** (LLM chính cho 5 chapters, ~70k tokens)",
        "- **Engine an sao** Bắc Phái + Chiếu Đởm Kinh (Python custom)",
        "- **Q1-Q4 Tử Vi Đẩu Số Toàn Thư** + 786 phú thi corpus",
        "- **Cron auto-extract** wisdom mới vào wiki sau mỗi luận giải",
        "",
        "Người đọc giữ **TÂM TỈNH THỨC** xuyên suốt:",
        "",
        "> _\"Thập bát tinh chuyển, tại nhân biến thông.\"_",
        "> — sao chỉ vận hành, người là người biến thông cuộc đời.",
        "",
        "---",
        "",
        f"_© YI-CHRONOS · Bộ tổng đoán mệnh hoàn chỉnh · Xuất bản {today}_",
    ])

    return "\n".join(lines)


def main():
    out_md = PUB / "Founder_BoTongDoanMenh_2026.md"
    out_pdf = PUB / "Founder_BoTongDoanMenh_2026.pdf"
    md_content = build_master_markdown()
    out_md.write_text(md_content, encoding="utf-8")
    total_chars = len(md_content)
    print(f"📝 Master markdown: {out_md} ({total_chars:,} chars)")

    # Generate PDF via pandoc → HTML → WeasyPrint
    html_path = out_md.with_suffix(".html")
    result = subprocess.run(
        ["pandoc", str(out_md), "-o", str(html_path),
         "--from", "markdown+pipe_tables+blank_before_blockquote+yaml_metadata_block",
         "--to", "html5",
         "--standalone",
         "--toc",
         "--toc-depth", "2",
         "--metadata", "lang=vi",
         "--css", "data:text/css;base64,Ym9keXtmb250LWZhbWlseTonU2Vnb2UgVUknLEFyaWFsLHNhbnMtc2VyaWY7Y29sb3I6IzMzMztsaW5lLWhlaWdodDoxLjY7bWF4LXdpZHRoOjk1MHB4O21hcmdpbjphdXRvO3BhZGRpbmc6MmVtfWgxe2NvbG9yOiNiYTRkMDA7Ym9yZGVyLWJvdHRvbToycHggc29saWQjYmE0ZDAwO3BhZGRpbmctYm90dG9tOjAuM2VtO21hcmdpbi10b3A6MS41ZW19aDJ7Y29sb3I6IzgwNjAwMDtib3JkZXItYm90dG9tOjFweCBzb2xpZCNlNmI4NDM7cGFkZGluZy1ib3R0b206MC4yZW19aDN7Y29sb3I6IzgwNjAwMH1ibG9ja3F1b3Rle2JvcmRlci1sZWZ0OjRweCBzb2xpZCNkOWE0NDk7YmFja2dyb3VuZDojZmZmOWUzO3BhZGRpbmc6MWVtO21hcmdpbjoxZW0gMH10YWJsZXtib3JkZXItY29sbGFwc2U6Y29sbGFwc2U7d2lkdGg6MTAwJTttYXJnaW46MWVtIDB9dGgsdGR7Ym9yZGVyOjFweCBzb2xpZCNkZGQ7cGFkZGluZzowLjVlbX10aHtiYWNrZ3JvdW5kOiNmZmY5ZTM7Y29sb3I6IzgwNjAwMH1lbXtjb2xvcjojNDQ2NjkwfXN0cm9uZ3tjb2xvcjojYmE0ZDAwfQ==",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"❌ Pandoc HTML failed:\n{result.stderr[:500]}")
        sys.exit(1)
    print(f"📄 HTML: {html_path} ({html_path.stat().st_size:,} bytes)")

    # WeasyPrint HTML → PDF
    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(str(out_pdf))
        size_mb = out_pdf.stat().st_size / 1024 / 1024
        print(f"📕 PDF: {out_pdf} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"❌ WeasyPrint failed: {e}")
        # Fallback: keep HTML only
        print(f"   Anh có thể mở HTML trong browser → Print → Save as PDF")


if __name__ == "__main__":
    main()
