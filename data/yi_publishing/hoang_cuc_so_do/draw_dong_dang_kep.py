#!/usr/bin/env python3
"""ĐỒNG DẠNG KÉP — đời người (đồng hồ nhỏ) lồng trong mùa trời đất (đồng hồ lớn).
Minh hoạ: Tử Vi/Bát Tự = Anh là ai; Hoàng Cực = Anh ở mùa nào của trời đất.
Số liệu thật từ engine.hoang_cuc (neo 304CN=thế2245). Founder sinh 1988."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def vy(y): return f"{y}" if y > 0 else f"{-y+1}TCN"

NGO0, NGO1 = -2216, 8583       # hội Ngọ span (astro)
BIRTH, NOW, END = 1988, 2026, 2068
W, H = 1180, 1010
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="44" text-anchor="middle" font-size="28" fill="#2a2018" font-weight="bold">ĐỒNG DẠNG KÉP — Đời người trong mùa của trời đất</text>')
s.append(f'<text x="{W/2}" y="72" text-anchor="middle" font-size="15" fill="#7a5a2a">Tử Vi/Bát Tự = ANH LÀ AI · Hoàng Cực = ANH Ở MÙA NÀO · ghép lại = đời Anh diễn ra TRONG mùa nào</text>')

# ── ĐỒNG HỒ LỚN: hội Ngọ (10.800 năm) ──────────────────────
bx0, bx1, by = 80, 1100, 170
s.append(f'<text x="{bx0}" y="{by-26}" font-size="16" fill="#2f5d8a" font-weight="bold">① ĐỒNG HỒ LỚN — Hội NGỌ (10.800 năm) · quẻ Cấu · "vương giáng nhi bá"</text>')
def X(y): return bx0 + (y-NGO0)/(NGO1-NGO0)*(bx1-bx0)
# nền gradient mùa (xuân→đông): thịnh đầu hội, suy về sau
s.append(f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#c9a13b" stop-opacity="0.5"/><stop offset="1" stop-color="#3a3a4a" stop-opacity="0.5"/></linearGradient></defs>')
s.append(f'<rect x="{bx0}" y="{by}" width="{bx1-bx0}" height="34" fill="url(#g)" stroke="#c9b896"/>')
# mốc sử
for y, lab in [(-2070,"Hạ Vũ\n(đầu Ngọ)"),(-1046,"Chu"),(-221,"Tần"),(960,"Tống"),(1988,""),(8583,"cuối Ngọ\n~8583 CN")]:
    xx=X(y)
    s.append(f'<line x1="{xx:.0f}" y1="{by}" x2="{xx:.0f}" y2="{by+34}" stroke="#8a7a55" stroke-width="0.8"/>')
    for k,ln in enumerate((lab or "").split("\n")):
        s.append(f'<text x="{xx:.0f}" y="{by+48+k*13:.0f}" text-anchor="middle" font-size="10.5" fill="#777">{esc(ln)}</text>')
s.append(f'<text x="{X(NGO0):.0f}" y="{by-6}" text-anchor="start" font-size="10.5" fill="#777">{vy(NGO0)} (vận 181)</text>')
# cửa sổ đời Anh — gần như 1 vạch
wx0, wx1 = X(BIRTH), X(END)
s.append(f'<rect x="{wx0-1:.0f}" y="{by-6}" width="{max(3,wx1-wx0):.0f}" height="46" fill="#c0392b" opacity="0.9"/>')
s.append(f'<text x="{wx0:.0f}" y="{by+74}" text-anchor="middle" font-size="11" fill="#c0392b" font-weight="bold">đời Anh ▼</text>')
s.append(f'<text x="{(bx0+bx1)/2}" y="{by+96}" text-anchor="middle" font-size="12.5" fill="#888">Một đời 80 năm = chấm đỏ = <tspan fill="#c0392b" font-weight="bold">0,74%</tspan> của một hội. Cả đời Anh nằm trọn trong VẬN 192.</text>')

# ── kính lúp nối xuống ──────────────────────────────────────
zx0, zx1, zy = 120, 1060, 360
s.append(f'<path d="M {wx0-1:.0f} {by+40} L {zx0} {zy}" stroke="#c0392b" stroke-dasharray="4 3" stroke-width="1"/>')
s.append(f'<path d="M {wx1+1:.0f} {by+40} L {zx1} {zy}" stroke="#c0392b" stroke-dasharray="4 3" stroke-width="1"/>')

# ── ĐỒNG HỒ NHỎ: đời Anh 1988-2068 ─────────────────────────
s.append(f'<text x="{zx0}" y="{zy-14}" font-size="16" fill="#b8862a" font-weight="bold">② ĐỒNG HỒ NHỎ (phóng to) — Đời Anh: sinh 1988 · Mệnh Thiên Đồng tại Tỵ · Nhật chủ Nhâm Thủy</text>')
s.append(f'<rect x="{zx0}" y="{zy}" width="{zx1-zx0}" height="60" fill="#3a3a4a" opacity="0.08" stroke="#c9b896"/>')
s.append(f'<text x="{(zx0+zx1)/2}" y="{zy+78}" text-anchor="middle" font-size="11.5" fill="#888">Nền xám = khí hội Ngọ (mùa đua tranh) — bối cảnh CHUNG cho mọi người sống thời này</text>')
def Z(y): return zx0 + (y-BIRTH)/(END-BIRTH)*(zx1-zx0)
# 8 Đại Vận (khởi tuổi 4 → 1992, mỗi 10 năm)
dv_cols=["#b8862a","#c98a2e","#cf7d3a","#a85a3a","#7a4a52","#5a4a6a","#3f5d54","#2f5d8a"]
for i in range(8):
    y0=1992+i*10
    x0,x1=Z(y0),Z(min(y0+10,END+3))
    cur = y0<=NOW<y0+10
    s.append(f'<rect x="{x0:.0f}" y="{zy}" width="{x1-x0:.0f}" height="60" fill="{dv_cols[i]}" opacity="{0.30 if cur else 0.16}" stroke="{dv_cols[i]}" stroke-opacity="0.5"/>')
    s.append(f'<text x="{(x0+x1)/2:.0f}" y="{zy+24}" text-anchor="middle" font-size="11" fill="{dv_cols[i]}" font-weight="bold">ĐV{i+1}</text>')
    s.append(f'<text x="{(x0+x1)/2:.0f}" y="{zy+40}" text-anchor="middle" font-size="9.5" fill="#666">{y0}–{y0+9}</text>')
    s.append(f'<text x="{(x0+x1)/2:.0f}" y="{zy+54}" text-anchor="middle" font-size="9" fill="#999">tuổi {4+i*10}-{13+i*10}</text>')
# mốc sinh / nay / 80
for y,lab,col in [(BIRTH,"SINH 1988\nMậu Thìn","#c0392b"),(NOW,"NAY 2026\nBính Ngọ · 38t","#c0392b"),(END,"~80 tuổi\n2068","#888")]:
    xx=Z(y)
    s.append(f'<line x1="{xx:.0f}" y1="{zy-6}" x2="{xx:.0f}" y2="{zy+60}" stroke="{col}" stroke-width="1.6"/>')
    for k,ln in enumerate(lab.split("\n")):
        s.append(f'<text x="{xx:.0f}" y="{zy-22+k*13:.0f}" text-anchor="middle" font-size="10.5" fill="{col}" font-weight="bold">{esc(ln)}</text>')

# ── khối kết: 3 thang lồng nhau + câu chốt ──────────────────
ky=500
s.append(f'<text x="{W/2}" y="{ky}" text-anchor="middle" font-size="16" fill="#2a2018" font-weight="bold">BA THANG LỒNG NHAU — cùng MỘT cấu trúc (đồng dạng)</text>')
rings=[("NGUYÊN","129.600 năm","cả vũ trụ một chu kỳ","#2f5d8a"),
       ("HỘI NGỌ","10.800 năm","mùa thời đại — quẻ Cấu","#3f7d54"),
       ("VẬN 192","360 năm","đoạn chứa trọn đời Anh","#cf7d3a"),
       ("ĐỜI ANH","80 năm","8 Đại Vận · lá số riêng","#c0392b")]
cx=W/2; cy=ky+270
for i,(nm,dur,desc,col) in enumerate(rings):
    r=240-i*54
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" fill-opacity="0.05" stroke="{col}" stroke-width="2" opacity="0.85"/>')
    s.append(f'<text x="{cx}" y="{cy-r+22:.0f}" text-anchor="middle" font-size="13" fill="{col}" font-weight="bold">{nm} · {dur}</text>')
    s.append(f'<text x="{cx}" y="{cy-r+38:.0f}" text-anchor="middle" font-size="10" fill="#888">{esc(desc)}</text>')
s.append(f'<text x="{cx}" y="{cy+2}" text-anchor="middle" font-size="13" fill="#c0392b" font-weight="bold">Anh ở đây</text>')
s.append(f'<text x="{cx}" y="{cy+20}" text-anchor="middle" font-size="10" fill="#999">1988→2068</text>')
s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="13" fill="#2f5d8a">"Một thân lại có một trời đất" (Vận Pháp Thi) · lá số nói Anh LÀ AI, Hoàng Cực nói Anh ở MÙA NÀO — đọc cùng nhau mới đủ</text>')
s.append('</svg>')
(OUT/"dong_dang_kep.svg").write_text("\n".join(s))
print("✓ Vẽ xong dong_dang_kep.svg")
