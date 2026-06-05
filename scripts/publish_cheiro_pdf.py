"""Publish bản dịch Cheiro (core) → PDF (Stage 6 bookflow, bản draft).

Môi trường ephemeral KHÔNG có pandoc + WeasyPrint (network allowlist chặn apt).
→ Dùng reportlab (pure-Python) + font DejaVuSans (hỗ trợ tiếng Việt) làm fallback.
Đây là PDF DRAFT v0.1 — chưa qua design pass WeasyPrint của project.

Run: python3 scripts/publish_cheiro_pdf.py
"""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "restored_books" / "cheiro-book-of-numbers" / "content.md"
OUT = ROOT / "data" / "published" / "cheiro-book-of-numbers-core-v0.1.pdf"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))


def _styles():
    ss = getSampleStyleSheet()
    base = ParagraphStyle("body", parent=ss["BodyText"], fontName="DejaVu",
                          fontSize=9.5, leading=14, alignment=TA_JUSTIFY)
    return {
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=20,
                                leading=24, alignment=TA_CENTER, spaceAfter=10),
        "subtitle": ParagraphStyle("subtitle", fontName="DejaVu", fontSize=11,
                                   leading=15, alignment=TA_CENTER, textColor=colors.grey),
        "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=15, leading=19,
                             spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#4a2f7a")),
        "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=12.5, leading=16,
                             spaceBefore=9, spaceAfter=5, textColor=colors.HexColor("#6b4ea8")),
        "h3": ParagraphStyle("h3", fontName="DejaVu-Bold", fontSize=10.5, leading=14,
                             spaceBefore=7, spaceAfter=3),
        "body": base,
        "bullet": ParagraphStyle("bullet", parent=base, leftIndent=10, bulletIndent=2, spaceAfter=2),
        "quote": ParagraphStyle("quote", parent=base, leftIndent=10, fontSize=8.8,
                               textColor=colors.HexColor("#555555"), leading=12),
    }


def _esc(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # **bold** → <b>
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font face='DejaVu'>\1</font>", text)
    return text


def md_to_flow(md: str, S: dict) -> list:
    flow: list = []
    lines = md.splitlines()
    i = 0
    table_buf: list[list[str]] = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = [[Paragraph(_esc(c), S["body"]) for c in r] for r in table_buf]
        t = Table(rows, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ccbfe6")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#efe9fb")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        flow.append(t)
        flow.append(Spacer(1, 4))
        table_buf = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("|") and "|" in line[1:]:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue  # separator row
            table_buf.append(cells)
            continue
        else:
            flush_table()

        if not line.strip():
            continue
        if line.startswith("# "):
            flow.append(Paragraph(_esc(line[2:]), S["h1"]))
        elif line.startswith("## "):
            flow.append(Paragraph(_esc(line[3:]), S["h2"]))
        elif line.startswith("### "):
            flow.append(Paragraph(_esc(line[4:]), S["h3"]))
        elif line.startswith("> "):
            flow.append(Paragraph(_esc(line[2:]), S["quote"]))
        elif re.match(r"^[-*] ", line):
            flow.append(Paragraph("• " + _esc(line[2:]), S["bullet"]))
        elif line.strip() == "---":
            flow.append(Spacer(1, 6))
        else:
            flow.append(Paragraph(_esc(line), S["body"]))
    flush_table()
    return flow


def main() -> int:
    S = _styles()
    md = SRC.read_text(encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    story: list = [
        Spacer(1, 60),
        Paragraph("Sách Về Những Con Số", S["title"]),
        Paragraph("Cheiro's Book of Numbers (1926)", S["subtitle"]),
        Spacer(1, 8),
        Paragraph("Hệ Chaldean · Bản phục dựng cốt lõi EN→VI", S["subtitle"]),
        Spacer(1, 40),
        Paragraph("YI-CHRONOS — Nhà xuất bản Đông phương học AI-driven", S["subtitle"]),
        Paragraph("Public domain · v0.1 draft (Stage 6, reportlab fallback)", S["subtitle"]),
        PageBreak(),
    ]
    story += md_to_flow(md, S)

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A5,
        leftMargin=16 * mm, rightMargin=16 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
        title="Sách Về Những Con Số (Cheiro) — YI-Chronos",
    )
    doc.build(story)
    size_kb = OUT.stat().st_size / 1024
    print(f"✅ PDF: {OUT} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
