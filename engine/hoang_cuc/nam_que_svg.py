"""SVG strip năm-quẻ cá nhân hoá — dùng cho web (HoangCucPanel).

nam_que_strip_svg(birth, now) → chuỗi SVG: mỗi năm đời người (trong khoảng có
nguồn 2020-2103) một ô, tô màu theo quẻ, đánh dấu NĂM NAY. Paradigm đọc-đồng-dạng.
SVG chạy thẳng trên trình duyệt (CJK qua font hệ thống user)."""
from __future__ import annotations

import colorsys

from .nam_que import nam_que

DATA_LO, DATA_HI = 2020, 2103  # khoảng bảng 值年卦 có nguồn


def _hue(kw: int) -> str:
    h = ((kw * 47) % 64) / 64.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.34, 0.93)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def nam_que_strip_svg(birth: int, now: int) -> str:
    """Dải năm-quẻ cho đời người sinh năm `birth`, đánh dấu năm `now`."""
    y0 = max(DATA_LO, birth)
    y1 = min(DATA_HI, birth + 80)
    if y1 < y0:                       # đời người ngoài khoảng có nguồn
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 60">'
            '<text x="300" y="34" text-anchor="middle" font-size="13" fill="#999">'
            f'Năm-quẻ chỉ có nguồn cho {DATA_LO}–{DATA_HI} — ngoài khoảng đời này.</text></svg>'
        )
    years = list(range(y0, y1 + 1))
    n = len(years)
    FONT = "'Songti SC','STSong','PingFang SC','Times New Roman',serif"
    W, H = 940, 200
    x0, x1, sy, sh = 16, 924, 56, 116
    cw = (x1 - x0) / n
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">']
    s.append(f'<text x="{W/2}" y="22" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">Năm-quẻ đời mình (值年卦) — {y0} → {y1}</text>')
    note = "mỗi năm một quẻ · đọc cấu trúc của năm, không bói"
    if birth < DATA_LO:
        note = f"{birth}–{DATA_LO-1} chưa có nguồn (không bịa) · " + note
    s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="10.5" fill="#999">{_esc(note)}</text>')
    for i, y in enumerate(years):
        q = nam_que(y)
        x = x0 + i * cw
        col = _hue(q["kw"]) if q else "#e8e2d6"
        s.append(f'<rect x="{x:.1f}" y="{sy}" width="{cw-0.5:.1f}" height="{sh}" fill="{col}" stroke="#fff" stroke-width="0.4"/>')
        if q:
            cxx, cyy = x + cw / 2, sy + sh - 8
            s.append(f'<text x="{cxx:.1f}" y="{cyy:.1f}" font-size="11" fill="#3a2e20" transform="rotate(-90 {cxx:.1f} {cyy:.1f})">{_esc(q["viet"])}</text>')
            s.append(f'<text x="{cxx:.1f}" y="{sy+13:.1f}" text-anchor="middle" font-size="10" fill="#6a5a44">{_esc(q["han"])}</text>')
        if y % 5 == 0 or y == now:
            s.append(f'<text x="{x+cw/2:.1f}" y="{sy+sh+15:.0f}" text-anchor="middle" font-size="9" fill="#999">{y}</text>')
    if y0 <= now <= y1:
        xn = x0 + (now - y0) * cw
        s.append(f'<rect x="{xn:.1f}" y="{sy-2}" width="{cw:.1f}" height="{sh+4}" fill="none" stroke="#c0392b" stroke-width="2.4"/>')
        qn = nam_que(now)
        lab = f'NAY {now}' + (f' · {qn["han"]} {qn["viet"]}' if qn else '')
        s.append(f'<text x="{xn+cw/2:.1f}" y="{sy-6:.0f}" text-anchor="middle" font-size="11.5" fill="#c0392b" font-weight="bold">{_esc(lab)}</text>')
    s.append('</svg>')
    return "\n".join(s)
