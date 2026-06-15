#!/usr/bin/env python3
"""VẬN 192 — 360 năm chứa trọn đời Anh. Hai băng đồng dạng:
  ① khí hội Ngọ (Cấu) — gần như PHẲNG suốt vận (cùng một 'mùa trời')
  ② lịch sử người — BIẾN ĐỘNG dữ dội (nông nghiệp→công nghiệp→số)
Đời Anh (1988-2068) bắt trúng đoạn dốc nhất. Số thật từ engine.hoang_cuc."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.constants import NGUYEN_START_ASTRO, can_chi_year

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

V0, V1 = 1744, 2103            # vận 192 span (engine: thế 2293–2304)
THE0 = 2293
BIRTH, NOW, END = 1988, 2026, 2068
W, H = 1180, 760
gx0, gx1 = 70, 1110
def X(y): return gx0 + (y-V0)/(V1-V0)*(gx1-gx0)

s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">VẬN 192 — 360 năm chứa trọn đời Anh</text>')
s.append(f'<text x="{W/2}" y="68" text-anchor="middle" font-size="14.5" fill="#7a5a2a">Hội Ngọ · quẻ Cấu (姤) · vận thứ 12/30 của hội · 12 thế · năm {V0}–{V1} CN — engine neo 304CN=thế2245</text>')

# ── BĂNG 1: khí hội Ngọ — gần như phẳng ──────────────────────
b1=110
s.append(f'<text x="{gx0}" y="{b1-10}" font-size="14.5" fill="#3f7d54" font-weight="bold">① KHÍ HỘI NGỌ (Cấu — "mùa đua tranh") · gần như PHẲNG suốt vận: cùng một mùa trời</text>')
s.append(f'<rect x="{gx0}" y="{b1}" width="{gx1-gx0}" height="30" fill="#3f7d54" fill-opacity="0.14" stroke="#3f7d54" stroke-opacity="0.4"/>')
s.append(f'<line x1="{gx0}" y1="{b1+15}" x2="{gx1}" y2="{b1+15}" stroke="#3f7d54" stroke-width="1.5" stroke-opacity="0.5"/>')
s.append(f'<text x="{(gx0+gx1)/2}" y="{b1+45}" text-anchor="middle" font-size="11" fill="#888">Trong 1 vận, "mùa" của hội đổi không đáng kể (chỉ ~37%→40% chặng hội Ngọ 10.800 năm)</text>')

# ── BĂNG 2: lịch sử người — biến động ─────────────────────────
b2=210
s.append(f'<text x="{gx0}" y="{b2-10}" font-size="14.5" fill="#a85a3a" font-weight="bold">② LỊCH SỬ NGƯỜI · BIẾN ĐỘNG dữ dội: nông nghiệp → công nghiệp → số/AI</text>')
# đường dốc lên (mức "biến động vật chất" của nhân loại) — phi tuyến, tăng tốc về sau
import math
pts=[]
for i in range(0,361,12):
    y=V0+i; t=i/360
    lvl=t**2.2            # tăng tốc — cách mạng công nghiệp về sau
    pts.append((X(y), b2+70 - lvl*60))
s.append(f'<path d="M {" L ".join(f"{x:.0f} {yy:.0f}" for x,yy in pts)}" fill="none" stroke="#a85a3a" stroke-width="2.5" opacity="0.6"/>')
s.append(f'<rect x="{gx0}" y="{b2}" width="{gx1-gx0}" height="72" fill="none" stroke="#ddd"/>')
# mốc sử
for y,lab in [(1744,"Càn Long\nThanh đỉnh · Lê-Trịnh"),(1840,"nha phiến\nThanh bắt đầu suy"),
              (1912,"Thanh vong\nhết 2000+ năm quân chủ"),(1945,"2 thế chiến\nkết · trật tự mới"),
              (2103,"hết vận 192\n→ vận 193 (2104)")]:
    xx=X(y)
    s.append(f'<line x1="{xx:.0f}" y1="{b2}" x2="{xx:.0f}" y2="{b2+72}" stroke="#bbb" stroke-width="0.7"/>')
    for k,ln in enumerate(lab.split("\n")):
        s.append(f'<text x="{xx:.0f}" y="{b2+88+k*13:.0f}" text-anchor="middle" font-size="10" fill="#888">{esc(ln)}</text>')

# ── BĂNG 3: 12 THẾ + đời Anh ─────────────────────────────────
b3=380
s.append(f'<text x="{gx0}" y="{b3-10}" font-size="14.5" fill="#b8862a" font-weight="bold">③ 12 THẾ (mỗi 30 năm) — đời Anh nằm ở 3 thế CUỐI vận (thế 2301–2303, ô thứ 9–11/12)</text>')
cw=(gx1-gx0)/12
for i in range(12):
    t=THE0+i; ys=NGUYEN_START_ASTRO+(t-1)*30; ye=ys+29
    x0=gx0+i*cw
    inlife = ys<=END and ye>=BIRTH
    col = "#c0392b" if inlife else "#b8862a"
    op = 0.18 if inlife else 0.07
    s.append(f'<rect x="{x0:.0f}" y="{b3}" width="{cw-2:.0f}" height="64" fill="{col}" fill-opacity="{op}" stroke="{col}" stroke-opacity="0.5"/>')
    s.append(f'<text x="{x0+cw/2:.0f}" y="{b3+18}" text-anchor="middle" font-size="11" fill="{col}" font-weight="bold">thế {t}</text>')
    s.append(f'<text x="{x0+cw/2:.0f}" y="{b3+34}" text-anchor="middle" font-size="9.5" fill="#555">{ys}-{ye}</text>')
    s.append(f'<text x="{x0+cw/2:.0f}" y="{b3+50}" text-anchor="middle" font-size="9" fill="#999">{can_chi_year(ys)}</text>')
    s.append(f'<text x="{x0+cw/2:.0f}" y="{b3+61}" text-anchor="middle" font-size="8.5" fill="#bbb">{i+1}/12</text>')

# cửa sổ đời Anh — dải đỏ vắt qua băng 3
wx0,wx1=X(BIRTH),X(END)
s.append(f'<rect x="{wx0:.0f}" y="{b3-4}" width="{wx1-wx0:.0f}" height="72" fill="none" stroke="#c0392b" stroke-width="2.2"/>')
for y,lab in [(BIRTH,"SINH 1988"),(NOW,"NAY 2026"),(END,"~80t · 2068")]:
    xx=X(y)
    s.append(f'<line x1="{xx:.0f}" y1="{b3+64}" x2="{xx:.0f}" y2="{b3+82}" stroke="#c0392b" stroke-width="1.6"/>')
    s.append(f'<text x="{xx:.0f}" y="{b3+96}" text-anchor="middle" font-size="10.5" fill="#c0392b" font-weight="bold">{esc(lab)}</text>')

# ── chốt ý ───────────────────────────────────────────────────
cy=560
s.append(f'<rect x="{gx0}" y="{cy}" width="{gx1-gx0}" height="118" rx="10" fill="#2f5d8a" fill-opacity="0.06" stroke="#2f5d8a" stroke-opacity="0.3"/>')
lines=[
 ("Mùa trời gần như đứng yên — lịch sử người thì lộn nhào.", "#2f5d8a", 15, True),
 ("Cùng một khí Cấu (đua tranh) phủ suốt 360 năm, nhưng bên trong: thế giới đi từ cày trâu sang vệ tinh & AI.", "#444", 12.5, False),
 ("Anh sinh ở thế 2301 — ô thứ 9 của 12 = CUỐI vận. Cuối vận = giao thời: cái cũ tàn, cái mới (vận 193) đang kết hạt.", "#444", 12.5, False),
 ("Đó không phải lời bói — là TOẠ ĐỘ. Lá số nói Anh LÀ AI; vận 192 nói Anh đứng ở KHÚC NÀO của dòng lớn.", "#a85a3a", 12.5, True),
]
for k,(t,c,fs,bold) in enumerate(lines):
    s.append(f'<text x="{(gx0+gx1)/2}" y="{cy+28+k*24}" text-anchor="middle" font-size="{fs}" fill="{c}"{" font-weight=\"bold\"" if bold else ""}>{esc(t)}</text>')
s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="11.5" fill="#999">Năm-quẻ từng năm (vd 304=革 Cách) đã có trong bộ trọn 950tr (OCR xong) → Chương 5 tô từng năm · Hội-quẻ = Cấu</text>')
s.append('</svg>')
(OUT/"van_192.svg").write_text("\n".join(s))
print("✓ Vẽ xong van_192.svg")
