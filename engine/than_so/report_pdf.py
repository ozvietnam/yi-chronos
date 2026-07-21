"""Báo cáo PDF lá số Thần Số Học Pythagoras (Decoz).

PDF = artifact chính thức. Dùng fpdf2 + DejaVu (Unicode/VI).
"""
from __future__ import annotations

import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from .cast import cast_than_so

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_REG = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"


class ThanSoPDF(FPDF):
    def footer(self):  # noqa: N802
        self.set_y(-12)
        self.set_font("DejaVu", size=8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"YI-CHRONOS · Thần Số Pythagoras · {self.page_no()}/{{nb}}", align="C")


def _safe(text: str) -> str:
    return (text or "").replace("\u00a0", " ").strip()


def _p(pdf: ThanSoPDF, text: str, size: int = 10, bold: bool = False, align: str = "L") -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B" if bold else "", size)
    pdf.multi_cell(
        pdf.epw,
        size * 0.55,
        _safe(text),
        align=align,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )


def generate_than_so_pdf(
    name: str,
    birth_date: str,
    current_name: str | None = None,
    name_order: str = "vn",
    target_year: int | None = None,
) -> bytes:
    """Trả PDF bytes — lá số đầy đủ + luận READ/GAP/IMPROVE."""
    chart = cast_than_so(
        name=name,
        birth_date=birth_date,
        current_name=current_name,
        name_order=name_order,
        target_year=target_year or datetime.now().year,
        include_chaldean=True,
        include_dong_phuong=False,
    )
    pdf = ThanSoPDF(format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_font("DejaVu", "", str(FONT_REG))
    pdf.add_font("DejaVu", "B", str(FONT_BOLD))
    pdf.set_margins(18, 16, 18)
    pdf.add_page()

    _p(pdf, "Lá số Thần Số Học Pythagoras", size=18, bold=True, align="C")
    pdf.ln(2)
    _p(pdf, name, size=12, align="C")
    _p(pdf, f"Ngày sinh: {birth_date}", size=11, align="C")
    _p(pdf, f"Chuẩn hoá: {chart['input']['name_normalized']}", size=10, align="C")
    pdf.ln(3)
    pdf.set_text_color(80, 80, 80)
    _p(pdf, chart["reading"]["paradigm_note"], size=9)
    pdf.set_text_color(0, 0, 0)
    deep = chart.get("deep_reading") or {}
    if deep.get("disclaimer"):
        pdf.ln(1)
        _p(pdf, deep["disclaimer"], size=8)

    pdf.ln(4)
    _p(pdf, "I. Số cốt lõi", size=13, bold=True)
    core = chart["core"]
    for key, label in (
        ("life_path", "Đường Đời"),
        ("expression", "Sứ Mệnh"),
        ("soul_urge", "Linh Hồn"),
        ("personality", "Nhân Cách"),
        ("birthday", "Ngày Sinh"),
        ("maturity", "Trưởng Thành"),
    ):
        node = core[key]
        kd = f" (nợ {node['karmic_debt']})" if node.get("karmic_debt") else ""
        arch = (chart["reading"]["core"].get(key) or {}).get("archetype_vi", "")
        _p(pdf, f"{label}: {node['value']}{kd} — {arch}", size=10)

    pdf.ln(2)
    _p(pdf, "II. Số mở rộng", size=13, bold=True)
    ext = chart["extended"]
    _p(pdf, f"Thái Độ: {ext['attitude']['value']}", size=10)
    _p(pdf, f"Cân Bằng: {ext['balance']['value']}", size=10)
    _p(pdf, f"Tư Duy Lý Trí: {ext['rational_thought']['value']}", size=10)
    _p(pdf, f"Tiềm Thức: {ext['subconscious_self']['value']}", size=10)
    _p(
        pdf,
        f"Đam Mê: {', '.join(str(x) for x in ext['hidden_passion']['values']) or '—'}",
        size=10,
    )
    _p(
        pdf,
        f"Bài học thiếu: {', '.join(str(x) for x in ext['karmic_lessons']['values']) or 'đủ 1–9'}",
        size=10,
    )
    br = ext["bridges"]
    _p(
        pdf,
        f"Cầu ĐĐ↔SM {br['life_path_expression']['value']} · "
        f"LH↔NC {br['soul_personality']['value']} · "
        f"ĐĐ↔NS {br['life_path_birthday']['value']}",
        size=10,
    )
    if ext.get("cornerstone") or ext.get("capstone"):
        _p(
            pdf,
            f"Cornerstone {ext.get('cornerstone', {}).get('letter', '—')} · "
            f"Capstone {ext.get('capstone', {}).get('letter', '—')} · "
            f"First Vowel {ext.get('first_vowel', {}).get('letter', '—')}",
            size=10,
        )
    planes = (ext.get("planes_of_expression") or {}).get("planes") or {}
    if planes:
        plane_txt = " · ".join(
            f"{pl.get('name_vi', k)} {pl.get('value')}" for k, pl in planes.items()
        )
        _p(pdf, f"Mặt phẳng: {plane_txt}", size=9)

    pdf.ln(2)
    _p(pdf, "III. Chu kỳ", size=13, bold=True)
    cy = chart["cycles"]
    _p(
        pdf,
        f"Năm CN {cy['personal_year']['target_year']}: {cy['personal_year']['value']} · "
        f"Tháng: {cy['personal_month']['value']} · Ngày: {cy['personal_day']['value']}",
        size=10,
    )
    _p(
        pdf,
        f"Essence tuổi {cy['age']}: {cy['essence']['value']} · "
        f"Duality {cy['duality']['essence']}×{cy['duality']['personal_year']}",
        size=10,
    )
    for p in cy["pinnacles"]:
        _p(pdf, f"Đỉnh {p['index']}: {p['value']} (tuổi {p['age_range']})", size=9)
    for c in cy["challenges"]:
        tag = " — Chính" if c.get("main") else ""
        _p(pdf, f"Thử thách {c['index']}: {c['value']}{tag}", size=9)

    pdf.add_page()
    _p(pdf, "IV. Luận READ → GAP → IMPROVE", size=13, bold=True)
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        block = (deep.get("core") or {}).get(key)
        if not block:
            continue
        pdf.ln(2)
        _p(
            pdf,
            f"{block['name_vi']} = {block['value']} — {block.get('archetype_vi', '')}",
            size=11,
            bold=True,
        )
        _p(pdf, f"READ: {block['read']}", size=9)
        _p(pdf, f"GAP: {block['gap']}", size=9)
        _p(pdf, f"IMPROVE: {block['improve']}", size=9)

    yg = (deep.get("cycles") or {}).get("personal_year")
    if yg:
        pdf.ln(3)
        _p(pdf, f"V. Năm cá nhân {yg['target_year']}", size=12, bold=True)
        _p(pdf, yg.get("read", ""), size=9)
        for act in yg.get("improve") or []:
            _p(pdf, f"• {act}", size=9)

    pdf.ln(3)
    _p(pdf, "VI. Lịch Personal Month (12 tháng)", size=12, bold=True)
    for row in (cy.get("personal_calendar") or [])[:12]:
        _p(
            pdf,
            f"{row['label']}: Tháng CN {row['personal_month']} (Năm CN {row['personal_year']})",
            size=9,
        )

    pdf.ln(2)
    _p(pdf, "VI.b 9 năm cá nhân tới", size=11, bold=True)
    for row in (cy.get("personal_year_calendar") or [])[:9]:
        _p(pdf, f"{row['year']}: Năm CN {row['personal_year']}", size=9)

    pdf.ln(2)
    _p(pdf, "VI.c 21 ngày cá nhân tới", size=11, bold=True)
    for row in (cy.get("personal_day_window") or [])[:21]:
        _p(
            pdf,
            f"D+{row['offset']} {row['date']}: "
            f"PY/PM/PD {row['personal_year']}/{row['personal_month']}/{row['personal_day']}",
            size=8,
        )

    pins = (deep.get("cycles") or {}).get("pinnacles") or []
    chals = (deep.get("cycles") or {}).get("challenges") or []
    if pins or chals:
        pdf.ln(2)
        _p(pdf, "VI.d Đỉnh vận & Thử thách (đọc sâu)", size=11, bold=True)
        for block in pins:
            _p(pdf, block.get("read", ""), size=8)
            for act in block.get("improve") or []:
                _p(pdf, f"• {act}", size=8)
        for block in chals:
            _p(pdf, block.get("read", ""), size=8)
            for act in block.get("improve") or []:
                _p(pdf, f"• {act}", size=8)

    pdf.ln(3)
    _p(pdf, "VII. Transit / Essence (9 tuổi tới)", size=12, bold=True)
    for row in (cy.get("transit_timeline") or [])[:9]:
        _p(
            pdf,
            f"Tuổi {row['age']}: P={row['physical'] and row['physical'].get('letter')} "
            f"M={row['mental'] and row['mental'].get('letter')} "
            f"S={row['spiritual'] and row['spiritual'].get('letter')} "
            f"→ Essence {row['essence']}",
            size=9,
        )

    audit = chart.get("method_audit") or {}
    if audit:
        pdf.ln(3)
        _p(pdf, "VIII. Kiểm chứng Life Path", size=12, bold=True)
        _p(pdf, audit.get("note", ""), size=8)
        da = audit.get("decoz_method_a") or {}
        _p(
            pdf,
            f"Decoz A: {da.get('value')} · Shortcut: "
            f"{(audit.get('shortcut_digit_string') or {}).get('value')} / "
            f"{(audit.get('shortcut_unit_sum') or {}).get('value')}",
            size=9,
        )
        expr_audit = audit.get("expression") or {}
        if expr_audit:
            pdf.ln(2)
            _p(pdf, "VIII.b Kiểm chứng Expression", size=11, bold=True)
            _p(pdf, expr_audit.get("note", ""), size=8)
            de = expr_audit.get("decoz_per_part") or {}
            flat = expr_audit.get("flat_full_name_shortcut") or {}
            _p(
                pdf,
                f"Decoz từng phần: {de.get('value')} · Flat shortcut: {flat.get('value')}",
                size=9,
            )
            for pt in de.get("parts") or []:
                kd = f" (nợ {pt['karmic_debt']})" if pt.get("karmic_debt") else ""
                _p(pdf, f"  {pt.get('part')}: {pt.get('raw')} → {pt.get('reduced')}{kd}", size=8)
            if expr_audit.get("diverged") or expr_audit.get("master_hidden_by_flat"):
                _p(pdf, "Flat lệch hoặc che Master — YI giữ Decoz per-part.", size=8)

    letters = chart.get("core", {}).get("breakdown") or []
    if letters:
        pdf.ln(2)
        _p(pdf, "IX. Quy đổi chữ cái", size=11, bold=True)
        grid = " ".join(f"{b.get('letter')}={b.get('value')}" for b in letters)
        _p(pdf, grid, size=8)

    pdf.ln(4)
    pdf.set_text_color(100, 100, 100)
    _p(
        pdf,
        f"Spec: Decoz Method A · schema {chart.get('schema_version')} · "
        f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        size=8,
    )

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def safe_filename(name: str, birth_date: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())[:40].strip("_") or "chart"
    return f"ThanSo_{slug}_{birth_date}.pdf"
