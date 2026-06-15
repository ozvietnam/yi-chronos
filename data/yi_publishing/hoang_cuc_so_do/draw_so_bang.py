#!/usr/bin/env python3
"""Vẽ lại BẢNG SỐ KHỞI-CHUNG 8×8 + ĐỒ ĐỒNG DẠNG — SVG sạch, Việt hoá.
Dựng từ so_bang_64.json (đã verify với qwen-VL)."""
import json
from pathlib import Path

D = json.loads(Path("data/yi_publishing/hoang_cuc_so_do/so_bang_64.json").read_text())
cells = {c["que_kep"]: c for c in D["cells"]}
S = D["S_nen"]
TRI = ["乾","兑","离","震","巽","坎","艮","坤"]
TRI_VI = ["Càn","Đoài","Ly","Chấn","Tốn","Khảm","Cấn","Khôn"]
TIME_VI = ["Nguyên","Hội","Vận","Thế","Tuế","Nguyệt","Nhật","Thời"]
BODY_VI = ["Nhật","Nguyệt","Tinh","Thần","Thạch","Thổ","Hỏa","Thủy"]
# màu theo hành quẻ (gradient ấm→lạnh)
COL = ["#b8862a","#c9a13b","#cf7d3a","#a14a3a","#3f7d54","#2f5d8a","#6b5a8f","#3a3a4a"]

def short_num(n):
    if n < 1e4: return f"{n:,}"
    if n < 1e8: return f"{n/1e4:.4g} vạn".replace('.0 ',' ')
    if n < 1e12: return f"{n/1e8:.5g} ức"
    if n < 1e16: return f"{n/1e12:.5g} triệu·ức"
    return f"{n/1e16:.4g}×10¹⁶"

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ── Đồ 1: BẢNG 8×8 ──────────────────────────────────────────
cw, ch = 150, 92          # cell w,h
ox, oy = 175, 140         # origin
W = ox + 8*cw + 40
H = oy + 8*ch + 60
FONT = "Georgia, STKaiti, Songti SC, serif"
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="46" text-anchor="middle" font-size="32" fill="#2a2018" font-weight="bold">BẢNG SỐ KHỞI–CHUNG CỦA TRỜI ĐẤT</text>')
s.append(f'<text x="{W/2}" y="78" text-anchor="middle" font-size="18" fill="#7a5a2a">天地始终之数表 · Hoàng Cực Kinh Thế — Thiệu Khang Tiết · 64 quẻ = 64 vị thời gian</text>')
s.append(f'<text x="{W/2}" y="104" text-anchor="middle" font-size="14" fill="#888">Số mỗi ô = S[quẻ thượng] × S[quẻ hạ] · S = [1, 12, 360, 4.320, 129.600, 1.555.200, 46.656.000, 559.872.000]</text>')
# header cột (quẻ THƯỢNG = ngoài = a)
s.append(f'<text x="{ox-90}" y="{oy-46}" font-size="14" fill="#555">THƯỢNG quái →</text>')
s.append(f'<text x="{ox-90}" y="{oy-26}" font-size="13" fill="#999">(= Nguyên·Hội·Vận·Thế…)</text>')
for a in range(8):
    cx = ox + a*cw + cw/2
    s.append(f'<rect x="{ox+a*cw}" y="{oy-34}" width="{cw}" height="34" fill="{COL[a]}" opacity="0.92"/>')
    s.append(f'<text x="{cx}" y="{oy-12}" text-anchor="middle" font-size="20" fill="#fff" font-weight="bold">{TRI[a]} {TRI_VI[a]}</text>')
# header hàng (quẻ HẠ = trong = b)
s.append(f'<text x="34" y="{oy+8*ch/2}" font-size="14" fill="#555" transform="rotate(-90 34 {oy+8*ch/2})" text-anchor="middle">HẠ quái ↓</text>')
for b in range(8):
    cy = oy + b*ch
    s.append(f'<rect x="{ox-110}" y="{cy}" width="110" height="{ch}" fill="{COL[b]}" opacity="0.55"/>')
    s.append(f'<text x="{ox-55}" y="{cy+ch/2-4}" text-anchor="middle" font-size="18" fill="#fff" font-weight="bold">{TRI[b]} {TRI_VI[b]}</text>')
    s.append(f'<text x="{ox-55}" y="{cy+ch/2+16}" text-anchor="middle" font-size="12" fill="#fff">{TIME_VI[b]}·{BODY_VI[b]}</text>')
# ô
for a in range(8):
    for b in range(8):
        c = cells[f"{TRI[a]}之{TRI[b]}"]
        x, y = ox + a*cw, oy + b*ch
        diag = (a == b)
        fill = "#fff" if not diag else "#fdeccd"
        s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{fill}" stroke="#d8cdb5"/>')
        s.append(f'<text x="{x+cw/2}" y="{y+26}" text-anchor="middle" font-size="22" fill="{COL[a]}" font-weight="bold">{esc(c["que"])}</text>')
        s.append(f'<text x="{x+cw/2}" y="{y+44}" text-anchor="middle" font-size="12" fill="#555">{esc(c["que_vi"])}</text>')
        s.append(f'<text x="{x+cw/2}" y="{y+64}" text-anchor="middle" font-size="11" fill="#999">{esc(c["tg_vi"])}</text>')
        s.append(f'<text x="{x+cw/2}" y="{y+82}" text-anchor="middle" font-size="12" fill="#7a5a2a">{c["so"]:,}</text>')
s.append('</svg>')
Path("data/yi_publishing/hoang_cuc_so_do/so_bang_8x8.svg").write_text("\n".join(s))

# ── Đồ 2: ĐỒNG DẠNG 8 ĐẲNG ──────────────────────────────────
W2, H2 = 980, 560
s2 = [f'<svg viewBox="0 0 {W2} {H2}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s2.append(f'<rect width="{W2}" height="{H2}" fill="#fbf7ef"/>')
s2.append(f'<text x="{W2/2}" y="48" text-anchor="middle" font-size="30" fill="#2a2018" font-weight="bold">ĐỒ ĐỒNG DẠNG — 8 ĐẲNG</text>')
s2.append(f'<text x="{W2/2}" y="80" text-anchor="middle" font-size="17" fill="#7a5a2a">Một đẳng = một QUẺ = một ĐƠN VỊ THỜI GIAN = một THIÊN THỂ = một SỐ NỀN</text>')
s2.append(f'<text x="{W2/2}" y="104" text-anchor="middle" font-size="14" fill="#888">"Cấu trúc trời = cấu trúc thời = cấu trúc số" — đồng dạng lập thành bảng</text>')
heads = ["Đẳng","Quẻ (tiên thiên)","Thời gian","Thiên thể","Số nền S"]
colx = [70, 250, 470, 660, 850]
hy = 150
for i,h in enumerate(heads):
    s2.append(f'<text x="{colx[i]}" y="{hy}" text-anchor="middle" font-size="16" fill="#555" font-weight="bold">{h}</text>')
s2.append(f'<line x1="40" y1="{hy+12}" x2="{W2-40}" y2="{hy+12}" stroke="#c9b896" stroke-width="2"/>')
for r in range(8):
    y = hy + 44 + r*48
    s2.append(f'<rect x="40" y="{y-30}" width="{W2-80}" height="44" fill="{COL[r]}" opacity="0.12"/>')
    s2.append(f'<text x="{colx[0]}" y="{y}" text-anchor="middle" font-size="22" fill="{COL[r]}" font-weight="bold">{r+1}</text>')
    s2.append(f'<text x="{colx[1]}" y="{y}" text-anchor="middle" font-size="20" fill="#2a2018">{TRI[r]} · {TRI_VI[r]}</text>')
    s2.append(f'<text x="{colx[2]}" y="{y}" text-anchor="middle" font-size="18" fill="#2a2018">{TIME_VI[r]}</text>')
    s2.append(f'<text x="{colx[3]}" y="{y}" text-anchor="middle" font-size="18" fill="#2a2018">{BODY_VI[r]}</text>')
    s2.append(f'<text x="{colx[4]}" y="{y}" text-anchor="middle" font-size="16" fill="#7a5a2a">{S[r]:,}</text>')
s2.append('</svg>')
Path("data/yi_publishing/hoang_cuc_so_do/dong_dang_8.svg").write_text("\n".join(s2))
print("✓ Vẽ xong: so_bang_8x8.svg + dong_dang_8.svg")
