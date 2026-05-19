"""Generate "Báo cáo Lá Số Tử Vi" PDF for any person.

Pulls all cached analyses from `data/yi_publishing/analysis_cache/{person_key}/`
and renders to PDF via WeasyPrint. Sections:
    1. Bìa + thông tin lá số (sinh, mệnh, thân, cục)
    2. Cách cục đặc biệt (6-8 cách)
    3. 12 Đại Vận (chu kỳ 10 năm)
    4. Lưu Niên 2026-2030
    5. Lưu Nguyệt 12 tháng 2026
    6. Phú Thái Vi đọc cá nhân (top N)

If a section's cache is missing → skip with note.
"""
from __future__ import annotations

import html as _html
import json
import time
from pathlib import Path
from typing import Optional

from .analyzer import _cache_load, _cache_dir, _cast_chart, _chart_summary, Person, BRANCHES


def _esc(s) -> str:
    if s is None:
        return ""
    return _html.escape(str(s))


def _load_any(person_key: str, kinds: list[str]) -> Optional[dict]:
    for k in kinds:
        d = _cache_load(person_key, k)
        if d:
            return d
    return None


def _format_chart_overview(person: Person, ls: dict) -> str:
    s2b = {**ls.get('chinh_tinh', {}), **ls.get('phu_tinh', {}), **ls.get('sat_tinh', {})}
    branch_to_stars: dict[str, list[str]] = {b: [] for b in BRANCHES}
    for st, idx in s2b.items():
        branch_to_stars[BRANCHES[idx]].append(st)

    palaces_html = "".join(
        f"<tr><td>{_esc(p['name'])}</td><td>{_esc(BRANCHES[p['branch_index']])}</td>"
        f"<td>{_esc(', '.join(branch_to_stars[BRANCHES[p['branch_index']]]) or '—')}</td></tr>"
        for p in ls.get('palaces', [])
    )
    return f"""
    <div class="overview">
      <h2>I. Thông tin lá số</h2>
      <div class="info-grid">
        <div><span class="label">Tên</span><span>{_esc(person.name)}</span></div>
        <div><span class="label">Giới tính</span><span>{_esc(person.gender)}</span></div>
        <div><span class="label">Sinh</span><span>{_esc(person.birth_datetime_local)}</span></div>
        <div><span class="label">Mệnh</span><span>{_esc(ls.get('menh_branch'))}</span></div>
        <div><span class="label">Thân</span><span>{_esc(ls.get('than_branch'))}</span></div>
        <div><span class="label">Cục</span><span>{_esc(ls.get('cuc_name'))}</span></div>
        <div><span class="label">Mệnh chủ</span><span>{_esc(ls.get('menh_chu'))}</span></div>
        <div><span class="label">Thân chủ</span><span>{_esc(ls.get('than_chu'))}</span></div>
      </div>

      <h3>12 cung</h3>
      <table class="palaces">
        <thead><tr><th>Cung</th><th>Địa chi</th><th>Sao tọa</th></tr></thead>
        <tbody>{palaces_html}</tbody>
      </table>
    </div>
    """


def _format_cach_cuc(data: dict) -> str:
    items = data.get('cach_cucs', [])
    if not items:
        return '<section class="empty"><h2>II. Cách Cục</h2><p>Chưa có dữ liệu.</p></section>'
    rows = []
    for c in items:
        lv = c.get('cap_do') or c.get('level') or ''
        rows.append(f"""
        <div class="cc-card cc-{_esc(lv)}">
          <div class="cc-head">
            <strong>{_esc(c.get('ten') or c.get('name'))}</strong>
            <span class="cc-level">{_esc(lv)}</span>
          </div>
          <p class="cc-evi"><em>Bằng chứng:</em> {_esc(c.get('bang_chung') or c.get('evidence'))}</p>
          <p class="cc-y">{_esc(c.get('y_nghia') or c.get('meaning'))}</p>
        </div>
        """)
    return f'<section><h2>II. Cách Cục đặc biệt</h2>{"".join(rows)}</section>'


def _format_dai_van(data: dict) -> str:
    anns = data.get('annotations', [])
    if not anns:
        return '<section class="empty"><h2>III. 12 Đại Vận</h2><p>Chưa có dữ liệu.</p></section>'
    rows = []
    for a in anns:
        cur = '⭐ ĐANG TRẢI QUA' if a.get('is_current') else ''
        co_hoi = ''.join(f'<li>{_esc(c)}</li>' for c in (a.get('co_hoi') or []))
        thach_thuc = ''.join(f'<li>{_esc(c)}</li>' for c in (a.get('thach_thuc') or []))
        rows.append(f"""
        <div class="dv-card {'is-current' if a.get('is_current') else ''}">
          <div class="dv-h">
            <strong>V{a.get('cycle_index')} — tuổi {a.get('start_age')}-{a.get('end_age')}</strong>
            <span>{_esc(a.get('start_year'))}–{_esc(a.get('end_year'))} · {_esc(a.get('branch'))} ({_esc(a.get('palace'))})</span>
            <span class="dv-stars">{_esc(', '.join(a.get('stars') or []))}</span>
            <span class="dv-cur">{cur}</span>
          </div>
          <p><strong>Tổng quan:</strong> {_esc(a.get('tong_quan'))}</p>
          <div class="dv-grid">
            <div><h4>✨ Cơ hội</h4><ul>{co_hoi}</ul></div>
            <div><h4>⚠️ Thách thức</h4><ul>{thach_thuc}</ul></div>
          </div>
          <p class="dv-loi"><strong>💡 Lời khuyên:</strong> {_esc(a.get('loi_khuyen'))}</p>
        </div>
        """)
    return f'<section><h2>III. 12 Đại Vận</h2>{"".join(rows)}</section>'


def _format_luu_nien(data: dict) -> str:
    years = data.get('years', [])
    if not years:
        return '<section class="empty"><h2>IV. Lưu Niên</h2><p>Chưa có dữ liệu.</p></section>'
    rows = []
    for y in years:
        an = y.get('analysis', {}) or {}
        rows.append(f"""
        <div class="ln-card">
          <div class="ln-h">
            <strong>{_esc(y.get('year'))}</strong>
            <span>tuổi {_esc(y.get('age_lunar'))} · Tiểu Hạn {_esc(y.get('tieu_han_branch'))} ({_esc(y.get('tieu_han_palace'))})</span>
            <span class="ln-cat ln-{_esc(an.get('cat_hung_overall',''))}">{_esc(an.get('cat_hung_overall',''))}</span>
          </div>
          <p><em>{_esc(an.get('chu_de',''))}</em></p>
          <p>{_esc(an.get('tong_quan',''))}</p>
          <p><strong>Lời khuyên:</strong> {_esc(an.get('loi_khuyen',''))}</p>
        </div>
        """)
    return f'<section><h2>IV. Lưu Niên {data.get("year_range",[""])[0]}-{data.get("year_range",["",""])[-1]}</h2>{"".join(rows)}</section>'


def _format_luu_nguyet(data: dict) -> str:
    months = data.get('months', [])
    if not months:
        return '<section class="empty"><h2>V. Lưu Nguyệt</h2><p>Chưa có dữ liệu.</p></section>'
    rows = []
    for m in months:
        an = m.get('analysis', {}) or {}
        viec_lam = ''.join(f'<li>{_esc(c)}</li>' for c in (an.get('viec_lam') or []))
        viec_tranh = ''.join(f'<li>{_esc(c)}</li>' for c in (an.get('viec_tranh') or []))
        rows.append(f"""
        <div class="lng-card">
          <div class="lng-h">
            <strong>Tháng {_esc(m.get('thang_am') or m.get('month'))}</strong>
            <span class="lng-cat lng-{_esc(an.get('cat_hung',''))}">{_esc(an.get('cat_hung',''))}</span>
          </div>
          <p><em>{_esc(an.get('chu_de',''))}</em></p>
          <p>{_esc(an.get('tinh_chat',''))}</p>
          <div class="lng-grid">
            <div><h4>Nên làm</h4><ul>{viec_lam}</ul></div>
            <div><h4>Nên tránh</h4><ul>{viec_tranh}</ul></div>
          </div>
        </div>
        """)
    return f'<section><h2>V. Lưu Nguyệt {data.get("year","")}</h2>{"".join(rows)}</section>'


CSS = """
@page { size: A4; margin: 1.6cm 1.4cm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #666; } }
body { font-family: "Times New Roman", "Palatino", "Hoefler Text", "Baskerville", serif; font-size: 10.5pt; line-height: 1.55; color: #1f2937; }
h1 { font-size: 22pt; text-align: center; color: #7c2d12; margin: 0 0 0.4em; }
h2 { font-size: 15pt; color: #7c2d12; border-bottom: 1.5pt solid #d6a86b; padding-bottom: 0.2em; margin-top: 1.4em; page-break-after: avoid; }
h3 { font-size: 12pt; color: #92400e; margin-top: 1em; }
h4 { font-size: 11pt; color: #92400e; margin: 0.4em 0 0.2em; }
section { page-break-inside: auto; }
.cover { text-align: center; padding-top: 3cm; page-break-after: always; }
.cover h1 { font-size: 28pt; }
.cover .sub { font-size: 14pt; color: #6b7280; margin-top: 0.5em; }
.cover .meta { font-size: 11pt; color: #4b5563; margin-top: 2cm; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5em 1.5em; margin: 1em 0; }
.info-grid div { padding: 0.3em 0; border-bottom: 0.5pt solid #e5e7eb; }
.info-grid .label { display: inline-block; min-width: 6em; color: #6b7280; font-weight: 600; }
table.palaces { width: 100%; border-collapse: collapse; margin-top: 0.5em; font-size: 9.5pt; }
table.palaces th, table.palaces td { border: 0.5pt solid #d1d5db; padding: 4pt 6pt; text-align: left; }
table.palaces th { background: #fef3c7; font-weight: 700; }
.cc-card, .dv-card, .ln-card, .lng-card { border: 0.5pt solid #e5e7eb; border-radius: 4pt; padding: 8pt 10pt; margin: 6pt 0; page-break-inside: avoid; }
.cc-card { border-left: 3pt solid #94a3b8; }
.cc-thượng { border-left-color: #10b981; }
.cc-trung { border-left-color: #f59e0b; }
.cc-hạ { border-left-color: #f97316; }
.cc-card.cc-phá { border-left-color: #ef4444; }
.cc-head { display: flex; justify-content: space-between; margin-bottom: 0.3em; }
.cc-level { font-size: 9pt; text-transform: uppercase; color: #6b7280; }
.cc-evi { font-size: 9.5pt; color: #6b7280; margin: 0.2em 0; }
.dv-card.is-current { background: #fef9c3; border-color: #f59e0b; }
.dv-h { display: flex; flex-wrap: wrap; gap: 0.6em; margin-bottom: 0.4em; }
.dv-stars { font-size: 9pt; color: #15803d; }
.dv-cur { color: #b45309; font-weight: 700; }
.dv-grid, .lng-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8em; }
.dv-grid ul, .lng-grid ul { margin: 0; padding-left: 1.2em; }
.dv-loi { background: #eff6ff; border-left: 2pt solid #60a5fa; padding: 4pt 8pt; margin-top: 0.4em; }
.ln-h, .lng-h { display: flex; gap: 0.6em; margin-bottom: 0.3em; }
.ln-cat, .lng-cat { font-size: 9pt; padding: 1pt 6pt; border-radius: 2pt; }
.ln-cát.đa.số, .lng-cát { background: #d1fae5; color: #065f46; }
.ln-cảnh.báo, .lng-cảnh.báo { background: #fee2e2; color: #991b1b; }
.footer { margin-top: 2em; padding-top: 0.5em; border-top: 0.5pt solid #d1d5db; font-size: 8pt; color: #9ca3af; text-align: center; }
.empty { color: #6b7280; font-style: italic; }
"""


def build_html(person_key: str) -> tuple[str, Person]:
    """Build the full HTML report. Returns (html, Person)."""
    # Try to resolve person: cached first, then synthesize from cach_cuc data
    cc = _cache_load(person_key, "cach_cuc") or _cache_load(person_key, "deep_analysis")
    name = cc.get("person_name") if cc else person_key
    birth = cc.get("anh_birth") if cc else None
    gender = "nam"  # default

    # If no birth in cache, try to get from auth DB
    if not birth:
        try:
            import sqlite3
            from pathlib import Path as _P
            db = _P("/Users/ozvietnamdesktop/Desktop/yi/data/yi_users/users.sqlite3")
            if db.exists():
                conn = sqlite3.connect(str(db))
                row = conn.execute(
                    "SELECT name, gender, birth_datetime_local FROM user_persons WHERE person_key=?",
                    (person_key,),
                ).fetchone()
                conn.close()
                if row:
                    name, gender, birth = row[0], row[1] or "nam", row[2]
        except Exception:
            pass

    # Founder fallback
    if person_key == "_founder" and not birth:
        birth = "1988-06-05T23:30:00"
        gender = "nam"
        name = "anh (Founder)"

    if not birth:
        raise ValueError(f"Cannot resolve birth datetime for person_key={person_key}")

    person = Person(person_key=person_key, name=name or person_key, birth_datetime_local=birth, gender=gender or "nam")
    ls = _cast_chart(birth, gender or "nam")

    sections = [_format_chart_overview(person, ls)]

    cc_data = _load_any(person_key, ["cach_cuc", "deep_analysis"])
    if cc_data:
        sections.append(_format_cach_cuc(cc_data))

    dv = _cache_load(person_key, "dai_van")
    if dv:
        sections.append(_format_dai_van(dv))

    # Lưu niên cached as luu_nien or luu_nien_{start}_{end}
    ln = _cache_load(person_key, "luu_nien") or _cache_load(person_key, "luu_nien_2026_2030")
    if ln:
        sections.append(_format_luu_nien(ln))

    lng = _cache_load(person_key, "luu_nguyet") or _cache_load(person_key, "luu_nguyet_2026")
    if lng:
        sections.append(_format_luu_nguyet(lng))

    generated = time.strftime("%Y-%m-%d %H:%M")

    html_doc = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Báo cáo lá số Tử Vi — {_esc(name)}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="cover">
    <h1>BÁO CÁO LÁ SỐ TỬ VI</h1>
    <div class="sub">{_esc(name)}</div>
    <div class="meta">
      Sinh: {_esc(birth)} ({_esc(gender)})<br>
      Mệnh {_esc(ls.get('menh_branch'))} · Thân {_esc(ls.get('than_branch'))} · Cục {_esc(ls.get('cuc_name'))}<br>
      <em>YI-CHRONOS — Tử Vi Đẩu Số Toàn Thư · Trần Đoàn · Biên soạn AI</em><br>
      Xuất bản: {generated}
    </div>
  </div>

  {''.join(sections)}

  <div class="footer">
    <em>Báo cáo này tổng hợp từ cache phân tích DeepSeek + thuật toán an sao chính thống.
    Tử Vi không phải predict — là phản chiếu cấu trúc thân-trời.</em>
  </div>
</body>
</html>"""
    return html_doc, person


def generate_pdf(person_key: str, output_path: Optional[Path] = None) -> Path:
    """Generate the PDF report. Returns path."""
    html_doc, person = build_html(person_key)
    if output_path is None:
        out_dir = _cache_dir(person_key)
        output_path = out_dir / f"report_la_so_{int(time.time())}.pdf"

    from weasyprint import HTML
    HTML(string=html_doc).write_pdf(str(output_path))
    return output_path
