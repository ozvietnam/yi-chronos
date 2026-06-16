"""SVG strip năm-quẻ cá nhân hoá — dùng cho web (HoangCucPanel).

nam_que_strip_svg(birth, now) → SVG: mỗi năm CẢ ĐỜI người một ô, tô màu theo quẻ,
đánh dấu NĂM NAY + ranh THẾ (mỗi 30 năm 世卦 reset). Dùng PHÉP 经世 (year_que_method)
— hệ duy nhất sau khi bỏ sohu/flat. Paradigm đọc-đồng-dạng. CJK qua font hệ thống.
"""
from __future__ import annotations

import colorsys

from .khoi_so import year_que_method, chuoi_60_van


def _hue(idx: int) -> str:
    h = ((idx * 47) % 60) / 60.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.34, 0.93)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nam_que_strip_svg(birth: int, now: int) -> str:
    """Dải năm-quẻ CẢ ĐỜI người sinh năm `birth` (80 năm), đánh dấu năm `now`."""
    c60 = chuoi_60_van()
    y0, y1 = birth, birth + 80
    years = list(range(y0, y1 + 1))
    try:
        ques = {y: year_que_method(y) for y in years}
    except ValueError:  # đời ngoài chu kỳ nguyên (cực hiếm)
        return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 60">'
                '<text x="300" y="34" text-anchor="middle" font-size="13" fill="#999">'
                'Đời người ngoài chu kỳ Nguyên hiện tại.</text></svg>')
    n = len(years)
    FONT = "'Songti SC','STSong','PingFang SC','Times New Roman',serif"
    W, H = 940, 214
    x0, x1, sy, sh = 16, 924, 56, 112
    cw = (x1 - x0) / n
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">']
    s.append(f'<text x="{W/2}" y="22" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">Năm-quẻ đời mình (值年卦) — {y0} → {y1}</text>')
    s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="10.5" fill="#999">mỗi năm một quẻ · phép 经世 (世卦 reset mỗi 30 năm) · đọc cấu trúc của năm, không bói</text>')
    for i, y in enumerate(years):
        q = ques[y]
        x = x0 + i * cw
        col = _hue(c60.index(q["han"]) if q["han"] in c60 else 0)
        s.append(f'<rect x="{x:.1f}" y="{sy}" width="{cw-0.5:.1f}" height="{sh}" fill="{col}" stroke="#fff" stroke-width="0.4"/>')
        cxx, cyy = x + cw / 2, sy + sh - 8
        s.append(f'<text x="{cxx:.1f}" y="{cyy:.1f}" font-size="11" fill="#3a2e20" transform="rotate(-90 {cxx:.1f} {cyy:.1f})">{_esc(q["viet"])}</text>')
        s.append(f'<text x="{cxx:.1f}" y="{sy+13:.1f}" text-anchor="middle" font-size="10" fill="#6a5a44">{_esc(q["han"])}</text>')
        # ranh THẾ: năm đầu một thế (世卦 reset) → vạch mảnh
        if q["nam_trong_the"] == 1 and i > 0:
            s.append(f'<line x1="{x:.1f}" y1="{sy-4}" x2="{x:.1f}" y2="{sy+sh+4}" stroke="#8a7a55" stroke-width="1" stroke-dasharray="2 2"/>')
        if y % 5 == 0 or y == now:
            s.append(f'<text x="{x+cw/2:.1f}" y="{sy+sh+15:.0f}" text-anchor="middle" font-size="9" fill="#999">{y}</text>')
            s.append(f'<text x="{x+cw/2:.1f}" y="{sy+sh+28:.0f}" text-anchor="middle" font-size="8.5" fill="#bbb">{y-birth} tuổi</text>')
    if y0 <= now <= y1:
        xn = x0 + (now - y0) * cw
        s.append(f'<rect x="{xn:.1f}" y="{sy-2}" width="{cw:.1f}" height="{sh+4}" fill="none" stroke="#c0392b" stroke-width="2.4"/>')
        qn = ques[now]
        lab = "NAY {} · {} tuổi · {} {}".format(now, now - birth, qn["han"], qn["viet"])
        s.append(f'<text x="{xn+cw/2:.1f}" y="{sy-6:.0f}" text-anchor="middle" font-size="11.5" fill="#c0392b" font-weight="bold">{_esc(lab)}</text>')
    s.append('</svg>')
    return "\n".join(s)
