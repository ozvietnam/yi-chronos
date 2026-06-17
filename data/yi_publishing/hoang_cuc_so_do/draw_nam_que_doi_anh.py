#!/usr/bin/env python3
"""NĂM-QUẺ ĐỜI ANH (值年卦) 2020-2068 — mỗi năm một quẻ, tô màu từng năm.
Dữ liệu thật: engine.hoang_cuc.nam_que (chính văn 304-313 + bảng 2020-2103 kiểm chéo).
Hàng dưới = chứng cứ kiểm chéo: chính văn 304-313 ≡ 2025-2034 (cùng 革...履)."""
import sys, colorsys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.nam_que import nam_que

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def hue(kw):  # KW 1..64 → màu pastel ổn định, chữ đọc được
    h = ((kw * 47) % 64) / 64.0
    r, g, b = colorsys.hsv_to_rgb(h, 0.34, 0.93)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

Y0, Y1 = 2020, 2068          # khoảng có dữ liệu nguồn, = đời Anh tuổi 32-80
BIRTH, NOW = 1988, 2026
years = list(range(Y0, Y1 + 1))
W, H = 1180, 660
x0, x1 = 56, 1124
cw = (x1 - x0) / len(years)
sy, sh = 150, 250            # strip y, height

s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="26" fill="#2a2018" font-weight="bold">NĂM-QUẺ ĐỜI ANH (值年卦) — 2020 → 2068</text>')
s.append(f'<text x="{W/2}" y="67" text-anchor="middle" font-size="13.5" fill="#7a5a2a">Mỗi năm một quẻ · suy bằng biến hào theo vận/thế (không theo can-chi) · dữ liệu kiểm chéo khớp chính văn 304-313</text>')

# Đại Vận founder: khởi tuổi 4 (1992), mỗi 10 năm → mốc trong khoảng: 2022,2032,2042,2052,2062
dv_marks = [y for y in range(1992, 2069, 10) if Y0 <= y <= Y1]

def X(y): return x0 + (y - Y0) * cw

# strip năm-quẻ
for y in years:
    q = nam_que(y)
    xx = X(y)
    col = hue(q["kw"]) if q else "#e8e2d6"
    s.append(f'<rect x="{xx:.1f}" y="{sy}" width="{cw-0.6:.1f}" height="{sh}" fill="{col}" stroke="#fff" stroke-width="0.5"/>')
    if q:
        # tên quẻ Việt — xoay dọc đọc từ dưới lên
        cxx, cyy = xx + cw/2, sy + sh - 12
        s.append(f'<text x="{cxx:.1f}" y="{cyy:.1f}" font-size="12.5" fill="#3a2e20" transform="rotate(-90 {cxx:.1f} {cyy:.1f})">{esc(q["viet"])}</text>')
        # chữ Hán nhỏ trên đầu cột
        s.append(f'<text x="{cxx:.1f}" y="{sy+15:.1f}" text-anchor="middle" font-size="11" fill="#6a5a44">{esc(q["han"])}</text>')
    # năm: ghi mỗi 4 năm + năm mốc
    if y % 4 == 0 or y in (NOW,):
        s.append(f'<text x="{xx+cw/2:.1f}" y="{sy+sh+15:.0f}" text-anchor="middle" font-size="9.5" fill="#999">{y}</text>')

# vạch Đại Vận
for y in dv_marks:
    xx = X(y)
    s.append(f'<line x1="{xx:.1f}" y1="{sy-8}" x2="{xx:.1f}" y2="{sy+sh+4}" stroke="#8a7a55" stroke-width="0.8" stroke-dasharray="3 3"/>')
    s.append(f'<text x="{xx:.1f}" y="{sy-12}" text-anchor="middle" font-size="9.5" fill="#8a7a55">ĐV tuổi {y-BIRTH}</text>')

# mốc NAY 2026
xn = X(NOW)
s.append(f'<rect x="{xn:.1f}" y="{sy-2}" width="{cw:.1f}" height="{sh+4}" fill="none" stroke="#c0392b" stroke-width="2.6"/>')
s.append(f'<text x="{xn+cw/2:.1f}" y="{sy+sh+34:.0f}" text-anchor="middle" font-size="12.5" fill="#c0392b" font-weight="bold">NAY 2026 · 同人 Đồng Nhân · 38 tuổi</text>')
# mốc ~80
x80 = X(2068)
s.append(f'<text x="{x80+cw/2:.1f}" y="{sy+sh+34:.0f}" text-anchor="end" font-size="11" fill="#888">2068 · 晋 Tấn · ~80t</text>')

# ── hàng chứng cứ kiểm chéo: chính văn 304-313 ──────────────
ey = sy + sh + 70
s.append(f'<text x="{x0}" y="{ey-8}" font-size="12.5" fill="#2f5d8a" font-weight="bold">⤷ CHỨNG CỨ KIỂM CHÉO — chính văn 皇极经世 ghi cho 304-313 CN (thế 2245):</text>')
ccw = 70
for i in range(304, 314):
    q = nam_que(i); xx = x0 + (i-304)*ccw
    s.append(f'<rect x="{xx}" y="{ey}" width="{ccw-3}" height="34" fill="{hue(q["kw"])}" stroke="#fff"/>')
    s.append(f'<text x="{xx+(ccw-3)/2:.0f}" y="{ey+15}" text-anchor="middle" font-size="11" fill="#3a2e20">{esc(q["han"])}</text>')
    s.append(f'<text x="{xx+(ccw-3)/2:.0f}" y="{ey+29}" text-anchor="middle" font-size="9.5" fill="#5a4a34">{esc(q["viet"])}</text>')
s.append(f'<text x="{x0+10*ccw+12}" y="{ey+22}" font-size="12" fill="#2f5d8a" font-weight="bold">≡ 2025-2034</text>')
s.append(f'<text x="{x0+10*ccw+12}" y="{ey+37}" font-size="10" fill="#888">(y hệt → bảng đáng tin)</text>')

s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="11" fill="#999">Nguồn: chính văn 304-313 + bảng 值年卦 2020-2103 (kiểm chéo) · 1988-2019 chưa có nguồn (không bịa) · 2043-44 nghi lỗi bảng</text>')
s.append('</svg>')
(OUT/"nam_que_doi_anh.svg").write_text("\n".join(s))
print(f"✓ Vẽ xong nam_que_doi_anh.svg ({len(years)} năm)")
