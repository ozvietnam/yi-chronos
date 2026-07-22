"""HTML → PDF qua WeasyPrint (fallback caller dùng fpdf2 nếu thiếu deps)."""
from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any


def _e(text: Any) -> str:
    return escape(str(text or ""), quote=True)


def _css() -> str:
    return """
    @page { size: A4; margin: 18mm 16mm 20mm; }
    body { font-family: DejaVu Sans, "Noto Sans", sans-serif; font-size: 10.5pt;
           color: #1f1a14; line-height: 1.45; }
    h1 { font-size: 18pt; text-align: center; margin: 0 0 4pt; color: #2c4a3e; }
    h2 { font-size: 13pt; color: #2c4a3e; border-bottom: 1px solid #c9c0b0;
         margin: 14pt 0 6pt; padding-bottom: 2pt; }
    h3 { font-size: 11pt; margin: 10pt 0 4pt; color: #3d3428; }
    .sub { text-align: center; color: #555; margin: 0 0 2pt; }
    .note { background: #f0ebe2; border-left: 3px solid #2c4a3e;
            padding: 6pt 8pt; font-style: italic; font-size: 9pt; margin: 8pt 0; }
    .disc { font-size: 8pt; color: #666; margin: 4pt 0 10pt; }
    table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt; font-size: 9.5pt; }
    th, td { border: 1px solid #d5ccc0; padding: 4pt 6pt; text-align: left; }
    th { background: #f5f1e8; }
    .score { font-size: 22pt; font-weight: 700; color: #2c4a3e; text-align: center; }
    .band { text-align: center; color: #5c4030; margin-bottom: 8pt; }
    .footer { font-size: 8pt; color: #888; margin-top: 16pt; text-align: center; }
    ul { margin: 2pt 0 8pt 14pt; padding: 0; }
    li { margin: 1pt 0; }
    """


def chart_to_html(chart: dict) -> str:
    core = chart.get("core") or {}
    ext = chart.get("extended") or {}
    cy = chart.get("cycles") or {}
    deep = chart.get("deep_reading") or {}
    audit = chart.get("method_audit") or {}
    inp = chart.get("input") or {}

    rows = []
    for key, label in (
        ("life_path", "Đường Đời"),
        ("expression", "Sứ Mệnh"),
        ("soul_urge", "Linh Hồn"),
        ("personality", "Nhân Cách"),
        ("birthday", "Ngày Sinh"),
        ("maturity", "Trưởng Thành"),
    ):
        node = core.get(key) or {}
        kd = f" (nợ {node['karmic_debt']})" if node.get("karmic_debt") else ""
        arch = ((chart.get("reading") or {}).get("core") or {}).get(key, {}).get("archetype_vi", "")
        rows.append(f"<tr><td>{_e(label)}</td><td><strong>{_e(node.get('value'))}</strong>{_e(kd)}</td><td>{_e(arch)}</td></tr>")

    deep_blocks = []
    for key in ("life_path", "expression", "soul_urge", "personality", "birthday", "maturity"):
        b = (deep.get("core") or {}).get(key)
        if not b:
            continue
        deep_blocks.append(
            f"<h3>{_e(b.get('name_vi'))} = {_e(b.get('value'))}</h3>"
            f"<p><strong>READ:</strong> {_e(b.get('read'))}</p>"
            f"<p><strong>GAP:</strong> {_e(b.get('gap'))}</p>"
            f"<p><strong>IMPROVE:</strong> {_e(b.get('improve'))}</p>"
        )

    year_rows = "".join(
        f"<tr><td>{_e(r.get('year'))}</td><td>{_e(r.get('personal_year'))}</td></tr>"
        for r in (cy.get("personal_year_calendar") or [])[:9]
    )
    day_rows = "".join(
        f"<tr><td>D+{_e(r.get('offset'))} {_e(r.get('date'))}</td>"
        f"<td>{_e(r.get('personal_year'))}/{_e(r.get('personal_month'))}/{_e(r.get('personal_day'))}</td></tr>"
        for r in (cy.get("personal_day_window") or [])[:21]
    )

    expr_audit = audit.get("expression") or {}
    expr_html = ""
    if expr_audit:
        parts = "".join(
            f"<li>{_e(p.get('part'))}: {_e(p.get('raw'))} → {_e(p.get('reduced'))}</li>"
            for p in (expr_audit.get("decoz_per_part") or {}).get("parts") or []
        )
        expr_html = (
            f"<h2>Kiểm chứng Expression</h2><p class='disc'>{_e(expr_audit.get('note'))}</p>"
            f"<p>Decoz: <strong>{_e((expr_audit.get('decoz_per_part') or {}).get('value'))}</strong> · "
            f"Flat: {_e((expr_audit.get('flat_full_name_shortcut') or {}).get('value'))}</p>"
            f"<ul>{parts}</ul>"
        )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{_css()}</style></head><body>
    <h1>Lá số Thần Số Học Pythagoras</h1>
    <p class="sub">{_e(inp.get('name_raw'))}</p>
    <p class="sub">Ngày sinh: {_e(inp.get('birth_date'))} · Chuẩn hoá: {_e(inp.get('name_normalized'))}</p>
    <div class="note">{_e((chart.get('reading') or {}).get('paradigm_note'))}</div>
    <p class="disc">{_e(deep.get('disclaimer'))}</p>
    <h2>I. Số cốt lõi</h2>
    <table><thead><tr><th>Số</th><th>Giá trị</th><th>Nguyên mẫu</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>
    <h2>II. Mở rộng</h2>
    <p>Thái Độ {_e((ext.get('attitude') or {}).get('value'))} ·
       Cân Bằng {_e((ext.get('balance') or {}).get('value'))} ·
       Lý Trí {_e((ext.get('rational_thought') or {}).get('value'))} ·
       Tiềm Thức {_e((ext.get('subconscious_self') or {}).get('value'))}</p>
    <h2>III. Chu kỳ</h2>
    <p>Năm CN {_e((cy.get('personal_year') or {}).get('target_year'))}:
       {_e((cy.get('personal_year') or {}).get('value'))} ·
       Tháng {_e((cy.get('personal_month') or {}).get('value'))} ·
       Ngày {_e((cy.get('personal_day') or {}).get('value'))}</p>
    <h2>IV. Luận READ → GAP → IMPROVE</h2>
    {''.join(deep_blocks)}
    <h2>V. 9 năm cá nhân</h2>
    <table><thead><tr><th>Năm</th><th>Năm CN</th></tr></thead><tbody>{year_rows}</tbody></table>
    <h2>VI. 21 ngày cá nhân</h2>
    <table><thead><tr><th>Ngày</th><th>PY/PM/PD</th></tr></thead><tbody>{day_rows}</tbody></table>
    <h2>VII. Kiểm chứng Life Path</h2>
    <p class="disc">{_e(audit.get('note'))}</p>
    <p>Decoz A: <strong>{_e((audit.get('decoz_method_a') or {}).get('value'))}</strong></p>
    {expr_html}
    <p class="footer">YI-CHRONOS · Decoz Method A · schema {_e(chart.get('schema_version'))} ·
    {_e(datetime.now().strftime('%Y-%m-%d %H:%M'))}</p>
    </body></html>"""


def compatibility_to_html(report: dict) -> str:
    a = report.get("person_a") or {}
    b = report.get("person_b") or {}
    overall = report.get("overall") or {}
    aspects_rows = []
    for asp in report.get("aspects") or []:
        aspects_rows.append(
            f"<tr><td>{_e(asp.get('name_vi'))}</td>"
            f"<td>{_e(asp.get('a'))} × {_e(asp.get('b'))}</td>"
            f"<td>{_e(asp.get('label_vi'))}</td>"
            f"<td>{_e(asp.get('read'))}</td></tr>"
        )
        aspects_rows.append(
            f"<tr><td colspan='4'><strong>GAP:</strong> {_e(asp.get('gap'))} · "
            f"<strong>IMPROVE:</strong> {_e(asp.get('improve'))}</td></tr>"
        )

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{_css()}</style></head><body>
    <h1>Báo cáo tương hợp Thần Số Pythagoras</h1>
    <p class="sub">{_e(a.get('name'))} × {_e(b.get('name'))}</p>
    <p class="sub">{_e(a.get('birth_date'))} · {_e(b.get('birth_date'))} ·
       loại: {_e(report.get('relationship_type'))}</p>
    <div class="note">{_e(report.get('paradigm_note'))}</div>
    <p class="disc">{_e(report.get('disclaimer'))}</p>
    <div class="score">{_e(overall.get('percent'))}/100</div>
    <div class="band">{_e(overall.get('label_vi'))}</div>
    <p>{_e(overall.get('read'))}</p>
    <p><strong>GAP:</strong> {_e(overall.get('gap'))}</p>
    <p><strong>IMPROVE:</strong> {_e(overall.get('improve'))}</p>
    <h2>Bốn lớp số</h2>
    <table><thead><tr><th>Lớp</th><th>A × B</th><th>Khí</th><th>Đọc</th></tr></thead>
    <tbody>{''.join(aspects_rows)}</tbody></table>
    <h2>Số ghép Đường Đời</h2>
    <p>{_e((report.get('composite_life_path') or {}).get('read'))}</p>
    <h2>Năm cá nhân</h2>
    <p>{_e((report.get('personal_year') or {}).get('read'))}</p>
    <p><strong>IMPROVE:</strong> {_e((report.get('personal_year') or {}).get('improve'))}</p>
    <p class="footer">YI-CHRONOS · tương hợp Pythagoras ·
    {_e(datetime.now().strftime('%Y-%m-%d %H:%M'))}</p>
    </body></html>"""


def render_html_pdf(html: str) -> bytes:
    from weasyprint import HTML

    return HTML(string=html).write_pdf()
