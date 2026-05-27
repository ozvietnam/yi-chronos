"""Báo Mệnh PDF — compose tổng hợp tất cả luận giải Bát Tự + Hà Lạc vào 1 PDF.

Bookflow v2.0 paradigm: PDF là **artifact xuất bản chính thức** (không phải sandbox web).

Pipeline:
1. Cast Bát Tự + Hà Lạc
2. Run all luận giải engines (luan_giai, luu_nien, hon_nhan, su_nghiep, tai_van, suc_khoe, ha_lac_luan)
3. Compose Markdown narrative đầy đủ
4. Convert Markdown → HTML via Pandoc
5. Render HTML → PDF via WeasyPrint

Output: data/user_publications/Bao_Menh_<sanitized_birth>.pdf
"""

from __future__ import annotations

import io
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


# ─── HTML template với CSS đẹp ──────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Mệnh Bát Tự — {{TITLE}}</title>
<style>
@page {
  size: A4;
  margin: 22mm 20mm 22mm 20mm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-size: 9pt;
    color: #888;
  }
  @top-right {
    content: "YI-CHRONOS · Báo Mệnh Bát Tự";
    font-size: 8pt;
    color: #aaa;
  }
}
@page :first {
  @top-right { content: ""; }
}
body {
  font-family: "Charter", "Iowan Old Style", "Noto Serif", Georgia, serif;
  font-size: 11pt;
  line-height: 1.55;
  color: #1f1f1f;
}
h1 {
  font-size: 22pt;
  color: #6b3410;
  border-bottom: 3px double #a87635;
  padding-bottom: 8px;
  margin-top: 0;
}
h2 {
  font-size: 16pt;
  color: #6b3410;
  margin-top: 20px;
  border-bottom: 1px solid #d4b08a;
  padding-bottom: 4px;
  page-break-after: avoid;
}
h3 {
  font-size: 13pt;
  color: #8b4513;
  margin-top: 14px;
  page-break-after: avoid;
}
h4 {
  font-size: 11pt;
  color: #6b3410;
  margin-top: 10px;
}
.cover {
  text-align: center;
  padding: 40mm 0;
  page-break-after: always;
}
.cover h1 {
  font-size: 32pt;
  border-bottom: none;
}
.cover .subtitle {
  font-size: 14pt;
  color: #6b3410;
  margin-top: 10px;
  font-style: italic;
}
.cover .meta {
  margin-top: 60mm;
  font-size: 11pt;
  color: #555;
}
.cover .meta b { color: #1f1f1f; }
.cover .paradigm-quote {
  margin-top: 40mm;
  font-size: 10pt;
  color: #555;
  font-style: italic;
  padding: 0 30mm;
  line-height: 1.7;
}
.paradigm-note {
  background: #f5ebd9;
  border-left: 4px solid #a87635;
  padding: 10px 14px;
  margin: 12px 0;
  font-style: italic;
  font-size: 10pt;
  color: #555;
}
.section-block {
  margin: 12px 0;
  padding: 10px 12px;
  background: #fdfaf5;
  border-left: 3px solid #c89c5f;
  border-radius: 0 4px 4px 0;
}
.warning {
  background: #fdf0eb;
  border-left: 3px solid #d65a4a;
}
.favorable {
  background: #f0f6e8;
  border-left: 3px solid #5ab07a;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  background: #e0ccaa;
  font-size: 9pt;
  font-weight: bold;
  color: #6b3410;
  margin-right: 4px;
}
table {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 10pt;
}
th, td {
  border: 1px solid #d4b08a;
  padding: 4px 8px;
  text-align: left;
}
th { background: #f5ebd9; color: #6b3410; }
ul, ol { margin: 6px 0 6px 22px; }
li { margin: 2px 0; }
.pillar-grid {
  display: table;
  width: 100%;
  margin: 8px 0;
}
.pillar-cell {
  display: table-cell;
  width: 25%;
  text-align: center;
  padding: 8px;
  background: #fdfaf5;
  border: 1px solid #d4b08a;
  font-size: 10pt;
}
.pillar-cell .position {
  font-size: 9pt;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.pillar-cell .ganzhi {
  font-size: 18pt;
  color: #6b3410;
  font-weight: bold;
  margin: 4px 0;
}
.closing {
  margin-top: 14px;
  padding: 10px 14px;
  background: #faf3e6;
  border-left: 3px solid #c89c5f;
  font-style: italic;
  font-size: 10pt;
}
.footer-citation {
  margin-top: 30px;
  padding-top: 8px;
  border-top: 1px solid #d4b08a;
  font-size: 9pt;
  color: #888;
}
</style>
</head>
<body>
{{BODY}}
</body>
</html>
"""


# ─── Helpers ────────────────────────────────────────────────────────────────


def _safe_text(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_md_bold(s: str) -> str:
    """Convert **bold** to <b>."""
    if not s:
        return ""
    s = _safe_text(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return s


def _compose_cover(birth: str, gender: str, tu_tru: dict) -> str:
    p = tu_tru["pillars"]
    return f"""
<div class="cover">
  <h1>📜 Báo Mệnh Bát Tự</h1>
  <div class="subtitle">Tử Bình + Hà Lạc · YI-CHRONOS</div>
  <div class="pillar-grid" style="margin-top:40mm">
    <div class="pillar-cell">
      <div class="position">Trụ Năm</div>
      <div class="ganzhi">{_safe_text(p['year']['stem'])}<br>{_safe_text(p['year']['branch'])}</div>
    </div>
    <div class="pillar-cell">
      <div class="position">Trụ Tháng</div>
      <div class="ganzhi">{_safe_text(p['month']['stem'])}<br>{_safe_text(p['month']['branch'])}</div>
    </div>
    <div class="pillar-cell">
      <div class="position">Trụ Ngày</div>
      <div class="ganzhi" style="color:#a87635">{_safe_text(p['day']['stem'])}<br>{_safe_text(p['day']['branch'])}</div>
    </div>
    <div class="pillar-cell">
      <div class="position">Trụ Giờ</div>
      <div class="ganzhi">{_safe_text(p['hour']['stem'])}<br>{_safe_text(p['hour']['branch'])}</div>
    </div>
  </div>
  <div class="meta">
    <b>Sinh thần</b>: {_safe_text(birth)} ({_safe_text(gender)})<br>
    <b>Nhật Chủ</b>: {_safe_text(tu_tru['day_master']['stem'])} ({_safe_text(tu_tru['day_master']['element'])})<br>
    <b>Ngày phát hành</b>: {datetime.now().strftime('%d/%m/%Y %H:%M')}
  </div>
  <div class="paradigm-quote">
    "Tử Bình KHÔNG dự đoán anh sẽ giàu hay nghèo. Tử Bình phản chiếu cấu trúc khí
    bẩm sinh + lưu biến → giúp tri mệnh + chọn cách đi qua. Mệnh cố kết, vận lưu biến."
    <br>— Iron Rule #4 + #6 (YI-CHRONOS paradigm)
  </div>
</div>
"""


def _compose_luan_giai_section(luan: dict) -> str:
    """Compose luận giải tổng hợp section."""
    parts = ["<h2>I. Luận Giải Tổng Hợp</h2>"]
    parts.append(f'<div class="paradigm-note">{_render_md_bold(luan["paradigm_guard"])}</div>')
    parts.append(f'<p>{_render_md_bold(luan["overview"])}</p>')

    # Cường độ
    c = luan["cuong_do_nhat_chu"]
    parts.append(f'<h3>Cường độ Nhật Chủ</h3>')
    parts.append(f'<p><span class="tag">{_safe_text(c["label"].upper())}</span> '
                 f'Support {c["support_score"]} · Drain {c["drain_score"]} · Δ {c["diff"]:.1f}</p>')
    parts.append(f'<p>{_render_md_bold(c["narrative"])}</p>')

    # Ngũ hành
    n = luan["ngu_hanh_balance"]
    parts.append(f'<h3>Ngũ Hành Balance</h3>')
    parts.append(f'<p>{_render_md_bold(n["narrative"])}</p>')
    if n.get("can_bo"):
        parts.append(f'<p>🎯 <b>Cần Bổ</b>: {", ".join(n["can_bo"])}</p>')

    # Cách Cục
    cc = luan["cach_cuc_luan"]
    if cc.get("present"):
        parts.append(f'<h3>Cách Cục</h3>')
        parts.append(f'<p>{_render_md_bold(cc["narrative"])}</p>')

    # Extreme pattern (nếu có)
    ext = luan.get("extreme_pattern_luan")
    if ext:
        parts.append(f'<h3>{_safe_text(ext["type_label"])} — PARADIGM ĐẢO NGƯỢC</h3>')
        parts.append(f'<div class="section-block warning">'
                     f'<p>{_render_md_bold(ext["narrative"])}</p></div>')

    # Dụng Thần
    dt = luan["dung_than_luan"]
    parts.append(f'<h3>Dụng Thần — thuốc cứu mệnh</h3>')
    parts.append(f'<p>{_render_md_bold(dt["narrative"])}</p>')

    # Thập Thần dominant
    tt = luan["thap_than_pattern"]
    if tt.get("profiles"):
        parts.append(f'<h3>Thập Thần nổi bật</h3>')
        for p in tt["profiles"]:
            parts.append(f'<h4>{_safe_text(p["name"])} (trọng số {p["weight"]:.0f})</h4>')
            parts.append(f'<p><b>Tích cực</b>: {_safe_text(p["tich_cuc"])}</p>')
            parts.append(f'<p><b>Tiêu cực</b>: {_safe_text(p["tieu_cuc"])}</p>')
            parts.append(f'<p>{_render_md_bold(p["cong_nang"])}</p>')

    # Favorable + warnings
    if luan.get("favorable_combinations"):
        parts.append(f'<h3>Cấu hình thuận lợi</h3>')
        for fc in luan["favorable_combinations"]:
            parts.append(f'<div class="section-block favorable">'
                         f'<b>✦ {_safe_text(fc["name"])}</b><br>{_safe_text(fc["narrative"])}</div>')
    if luan.get("warnings"):
        parts.append(f'<h3>Cảnh báo</h3>')
        for w in luan["warnings"]:
            parts.append(f'<div class="section-block warning">'
                         f'<b>⚠ {_safe_text(w["name"])}</b><br>{_safe_text(w["narrative"])}</div>')

    # Đại Vận current
    dv = luan["dai_van_current"]
    parts.append(f'<h3>Đại Vận hiện tại</h3>')
    parts.append(f'<p>{_render_md_bold(dv["narrative"])}</p>')

    # Bổ Hướng
    bh = luan["bo_huong"]
    parts.append(f'<h3>🎯 Bổ Hướng (actionable)</h3>')
    parts.append(f'<p>{_render_md_bold(bh["narrative"])}</p>')
    if bh.get("recommend"):
        parts.append('<table><tr><th>Loại</th><th>Hành</th><th>Nghề</th><th>Màu</th><th>Phương</th></tr>')
        for key, rec in bh["recommend"].items():
            parts.append(
                f'<tr><td>{"★ Dụng" if key=="dung" else "Hỷ"}</td>'
                f'<td>{_safe_text(rec["element"].title())}</td>'
                f'<td>{_safe_text(", ".join(rec["nghe_nghiep"][:3]))}</td>'
                f'<td>{_safe_text(", ".join(rec["mau_sac"]))}</td>'
                f'<td>{_safe_text(", ".join(rec["phuong_vi"]))}</td></tr>'
            )
        parts.append('</table>')

    parts.append(f'<div class="closing">{_render_md_bold(luan["closing"])}</div>')
    return "\n".join(parts)


def _compose_luu_nien_section(luu_nien: dict) -> str:
    parts = [f'<h2>II. Lưu Niên {luu_nien["target_year"]}</h2>']
    parts.append(f'<div class="paradigm-note">{_render_md_bold(luu_nien["paradigm_guard"])}</div>')
    ln = luu_nien["luu_nien"]
    parts.append(f'<p><b>Năm {ln["year_solar"]} = {_safe_text(ln["stem"])} {_safe_text(ln["branch"])}</b> '
                 f'({_safe_text(ln["stem_element"])}/{_safe_text(ln["branch_element"])}) — '
                 f'Thập Thần năm: <b>{_safe_text(ln["thap_than_vs_dm"])}</b></p>')

    ov = luu_nien["overall_verdict"]
    polarity_class = "favorable" if "thuận" in ov["verdict"] else ("warning" if "thử thách" in ov["verdict"] else "")
    parts.append(f'<div class="section-block {polarity_class}">')
    parts.append(f'<p><span class="tag">{_safe_text(ov["verdict"].upper())}</span></p>')
    parts.append(f'<p>{_render_md_bold(ov["narrative"])}</p></div>')

    # 12 tháng
    if luu_nien.get("luu_nguyet"):
        parts.append('<h3>12 Tháng Lưu Nguyệt</h3>')
        parts.append('<table><tr><th>T</th><th>Tiết</th><th>Can-Chi</th><th>Thập Thần</th><th>Verdict</th></tr>')
        for m in luu_nien["luu_nguyet"]:
            parts.append(
                f'<tr><td>{m["month_index"]}</td>'
                f'<td>{_safe_text(m["tiet_khi"])}</td>'
                f'<td>{_safe_text(m["stem"])} {_safe_text(m["branch"])}</td>'
                f'<td>{_safe_text(m["thap_than"])}</td>'
                f'<td>{_safe_text(m["short_marker"])} {_safe_text(m["verdict"])}</td></tr>'
            )
        parts.append('</table>')

    parts.append(f'<p>{_render_md_bold(luu_nien["bo_huong_nam"]["narrative"])}</p>')
    return "\n".join(parts)


def _compose_life_domain_section(title: str, data: dict, sections_layout: list[tuple[str, str]]) -> str:
    """Generic life domain section (hon_nhan / su_nghiep / tai_van / suc_khoe)."""
    parts = [f'<h2>{title}</h2>']
    parts.append(f'<div class="paradigm-note">{_safe_text(data.get("paradigm_guard", ""))}</div>')
    for key, label in sections_layout:
        val = data.get(key)
        if not val:
            continue
        parts.append(f'<h3>{_safe_text(label)}</h3>')
        if isinstance(val, dict) and "narrative" in val:
            parts.append(f'<p>{_render_md_bold(val["narrative"])}</p>')
        elif isinstance(val, list):
            for item in val[:8]:
                if isinstance(item, dict) and "narrative" in item:
                    parts.append(f'<div class="section-block">'
                                 f'<b>{_safe_text(item.get("name", ""))}</b><br>'
                                 f'{_render_md_bold(item["narrative"])}</div>')
                elif isinstance(item, str):
                    parts.append(f'<p>• {_render_md_bold(item)}</p>')
        elif isinstance(val, str):
            parts.append(f'<p>{_render_md_bold(val)}</p>')
    closing = data.get("closing")
    if closing:
        parts.append(f'<div class="closing">{_safe_text(closing)}</div>')
    return "\n".join(parts)


def _compose_ha_lac_section(ha_lac_luan: dict) -> str:
    parts = ['<h2>VII. Bát Tự Hà Lạc (Học Năng 1974)</h2>']
    parts.append(f'<div class="paradigm-note">{_safe_text(ha_lac_luan["paradigm_guard"])}</div>')
    parts.append(f'<p>{_render_md_bold(ha_lac_luan["overview"])}</p>')

    # 2 quẻ
    t = ha_lac_luan["tien_thien_luan"]
    h = ha_lac_luan["hau_thien_luan"]
    parts.append('<table><tr><th>Vai trò</th><th>Quẻ</th><th>Thượng / Hạ</th><th>Nguyên Đường</th></tr>')
    parts.append(f'<tr><td>Tiên Thiên (cốt mệnh)</td>'
                 f'<td><b>{_safe_text(t["name_vi"])}</b> (quẻ {t["king_wen"]})</td>'
                 f'<td>{_safe_text(t["upper_trigram"])} / {_safe_text(t["lower_trigram"])}</td>'
                 f'<td>hào {t["nguyen_duong_line"]}</td></tr>')
    parts.append(f'<tr><td>Hậu Thiên (vận dụng)</td>'
                 f'<td><b>{_safe_text(h["name_vi"])}</b> (quẻ {h["king_wen"]})</td>'
                 f'<td>{_safe_text(h["upper_trigram"])} / {_safe_text(h["lower_trigram"])}</td>'
                 f'<td>hào {h["nguyen_duong_line"]}</td></tr>')
    parts.append('</table>')

    # Comparison
    parts.append(f'<h3>So sánh Tiên ↔ Hậu</h3>')
    parts.append(f'<p><b>{_safe_text(ha_lac_luan["comparison"]["pattern"])}</b> — '
                 f'{_safe_text(ha_lac_luan["comparison"]["narrative"])}</p>')

    # 12 hào
    tj = ha_lac_luan["trajectory_luan"]
    parts.append(f'<h3>Quỹ Đạo 12 Hào</h3>')
    parts.append(f'<p>{_safe_text(tj["summary_narrative"])}</p>')
    if tj.get("current"):
        parts.append(f'<p>{_render_md_bold(tj["current_narrative"])}</p>')
    parts.append('<table><tr><th>S</th><th>Hexagram</th><th>Hào</th><th>Tuổi</th><th>Phase</th></tr>')
    for s in tj["stages"]:
        marker = "★ " if s["is_current"] else ("● " if s["is_nguyen_duong"] else "")
        parts.append(
            f'<tr><td>{marker}{s["stage_index"]}</td>'
            f'<td>{"Tiên" if s["hexagram"]=="tien" else "Hậu"}</td>'
            f'<td>hào {s["line_position"]} ({s["polarity"]}, {s["years_span"]}n)</td>'
            f'<td>{s["age_start"]}-{s["age_end"]}</td>'
            f'<td>{_safe_text(s["phase_label"])}</td></tr>'
        )
    parts.append('</table>')

    parts.append(f'<p>{_render_md_bold(ha_lac_luan["bo_huong_stage"])}</p>')
    parts.append(f'<div class="closing">{_safe_text(ha_lac_luan["closing"])}</div>')
    return "\n".join(parts)


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_bao_menh_pdf_v1"


def compose_bao_menh_html(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
    current_age: int | None = None,
) -> str:
    """Compose full Báo Mệnh as HTML string (ready to convert to PDF)."""
    from . import (
        analyze_hon_nhan,
        analyze_luu_nien,
        analyze_suc_khoe,
        analyze_su_nghiep,
        analyze_tai_van,
        cast_bat_tu,
        compose_luan_giai,
    )
    from engine.ha_lac import cast_ha_lac, compose_ha_lac_luan_giai

    # Auto-compute current_age
    if current_age is None:
        try:
            birth_year = int(birth_datetime_local[:4])
            current_age = datetime.now().year - birth_year
        except (ValueError, IndexError):
            current_age = None

    # Cast + analyze all
    state = cast_bat_tu(birth_datetime_local=birth_datetime_local,
                        timezone=timezone, gender=gender)
    luan = compose_luan_giai(state, current_age=current_age)
    luu_nien = analyze_luu_nien(state, current_age=current_age)
    hon_nhan = analyze_hon_nhan(state)
    su_nghiep = analyze_su_nghiep(state)
    tai_van = analyze_tai_van(state)
    suc_khoe = analyze_suc_khoe(state)
    ha_lac_state = cast_ha_lac(birth_datetime_local=birth_datetime_local,
                                timezone=timezone, gender=gender)
    ha_lac_luan = compose_ha_lac_luan_giai(ha_lac_state, current_age=current_age)

    # Compose body
    body_parts = [
        _compose_cover(birth_datetime_local, gender, state["tu_tru"]),
        _compose_luan_giai_section(luan),
        _compose_luu_nien_section(luu_nien),
        _compose_life_domain_section(
            "III. Hôn Nhân",
            hon_nhan,
            [("cung_phoi", "Cung Phối"), ("partner_star", "Star Vợ/Chồng"),
             ("warnings", "Cảnh báo"), ("overall", "Đánh giá tổng")],
        ),
        _compose_life_domain_section(
            "IV. Sự Nghiệp",
            su_nghiep,
            [("cach_cuc_summary", "Cách Cục Summary"),
             ("career_patterns", "Patterns"),
             ("dominant_thap_than_styles", "Thập Thần Styles")],
        ),
        _compose_life_domain_section(
            "V. Tài Vận",
            tai_van,
            [("dm_tai_balance", "DM-Tài Balance"),
             ("patterns", "Patterns"),
             ("strategy", "Chiến lược")],
        ),
        _compose_life_domain_section(
            "VI. Sức Khỏe",
            suc_khoe,
            [("constitution", "Tinh khí thần"),
             ("tang_phu_warnings", "Tạng phủ cảnh báo"),
             ("dietary", "Dietary")],
        ),
        _compose_ha_lac_section(ha_lac_luan),
        # Citation footer
        '<div class="footer-citation">',
        '<b>Nguồn</b>: ',
        'Thiệu Vĩ Hoa & Trần Viên — <i>Dự đoán theo Tứ trụ</i> (NXB Văn hóa Thông tin, '
        'dịch giả Nguyễn Văn Mậu, tái bản lần 4). ',
        'Học Năng — <i>Bát Tự Hà Lạc Lược Khảo</i> (Saigon 1974). ',
        'Hoàng Đế Nội Kinh + Tử Bình Chân Thuyên. ',
        f'<br>Generated by YI-CHRONOS · {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        '</div>',
    ]
    body = "\n".join(body_parts)
    title = f'{birth_datetime_local}'
    return HTML_TEMPLATE.replace("{{TITLE}}", title).replace("{{BODY}}", body)


def generate_bao_menh_pdf(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
    current_age: int | None = None,
    output_path: str | Path | None = None,
) -> bytes:
    """Generate Báo Mệnh PDF.

    Args:
        birth_datetime_local: ISO datetime
        timezone, gender, current_age: as cast_bat_tu
        output_path: optional path to save the PDF. If None, only returns bytes.

    Returns:
        PDF bytes.
    """
    import weasyprint  # Lazy import

    html = compose_bao_menh_html(
        birth_datetime_local=birth_datetime_local,
        timezone=timezone,
        gender=gender,
        current_age=current_age,
    )
    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(pdf_bytes)
    return pdf_bytes
