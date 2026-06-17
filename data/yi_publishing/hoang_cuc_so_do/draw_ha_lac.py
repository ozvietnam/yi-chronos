#!/usr/bin/env python3
"""HÀ ĐỒ – LẠC THƯ (河图洛书) — hai đồ số nguyên thủy.
Hà Đồ: 55 = thiên-địa-số (1-6 Thủy·2-7 Hỏa·3-8 Mộc·4-9 Kim·5-10 Thổ); lẻ=trắng/dương,
chẵn=đen/âm; sinh-số trong, thành-số ngoài. Lạc Thư: 45, ma phương 3×3, mọi hàng=15.
Nguồn: Quan Vật Ngoại Thiên ch.1 "河图天地全数" (tr.276, 57 tiết); dòng 7566, 7848."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 720
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">HÀ ĐỒ – LẠC THƯ — gốc của mọi con số</text>')
s.append(f'<text x="{W/2}" y="67" text-anchor="middle" font-size="14" fill="#7a5a2a">河图 (55 = thiên-địa-số) · 洛书 (45 = ma phương) · lẻ=○ trắng/dương · chẵn=● đen/âm · trên Nam dưới Bắc trái Đông phải Tây</text>')

def dots(cx, cy, n, yang, r=4.5, pitch=12):
    """n chấm thành 2 cột, trắng(dương/lẻ) hoặc đen(âm/chẵn), tâm (cx,cy)."""
    out=[]; cols = 1 if n==1 else 2
    rows = (n + cols - 1)//cols
    for i in range(n):
        c = i % cols; rr = i // cols
        x = cx + (c - (cols-1)/2)*pitch
        y = cy + (rr - (rows-1)/2)*pitch
        if yang: out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" stroke="#7a3410" stroke-width="1.3"/>')
        else:    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#2a2018"/>')
    return "".join(out)

# ── HÀ ĐỒ (trái) ─────────────────────────────────────────────
hx, hy = 320, 400
s.append(f'<text x="{hx}" y="110" text-anchor="middle" font-size="17" fill="#a8621c" font-weight="bold">① HÀ ĐỒ (河图) — tổng 55</text>')
# vị trí: (tên, sinh-số, thành-số, ngũ hành, phương, dx, dy)  trên Nam dưới Bắc trái Đông phải Tây
POS=[("Nam·Hỏa",2,7,"火",0,-1),("Bắc·Thủy",1,6,"水",0,1),
     ("Đông·Mộc",3,8,"木",-1,0),("Tây·Kim",4,9,"金",1,0),("Trung·Thổ",5,10,"土",0,0)]
arm=134
for nm,sinh,thanh,nh,dx,dy in POS:
    px,py = hx+dx*arm, hy+dy*arm
    # sinh-số (trong, gần tâm) + thành-số (ngoài)
    sx,sy = px-dx*28, py-dy*28      # nhích vào trong
    tx,ty = px+dx*34, py+dy*34      # ra ngoài
    if dx==0 and dy==0:             # trung tâm: 5 trên, 10 dưới
        sx,sy,tx,ty = px,py-24,px,py+28
    s.append(dots(sx,sy,sinh,sinh%2==1))
    s.append(dots(tx,ty,thanh,thanh%2==1))
    lx,ly = px+ (dx*74 if dx else 0), py + (dy*74 if dy else (-66 if dx else 0))
    if dx==0 and dy==0: lx,ly=px, py+66
    s.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="11.5" fill="#8a4a14" font-weight="bold">{esc(nh)} {esc(nm)}</text>')
    s.append(f'<text x="{lx:.0f}" y="{ly+15:.0f}" text-anchor="middle" font-size="10" fill="#999">{sinh}·{thanh}</text>')
s.append(f'<text x="{hx}" y="640" text-anchor="middle" font-size="11.5" fill="#777">Sinh-số 1·2·3·4·5 (trong) + Thành-số 6·7·8·9·10 (ngoài) · sinh + 5 = thành</text>')
s.append(f'<text x="{hx}" y="658" text-anchor="middle" font-size="11" fill="#999">Thiên-số lẻ (25) + Địa-số chẵn (30) = 55 · THỂ · tròn · → Tiên Thiên</text>')

# ── LẠC THƯ (phải) ───────────────────────────────────────────
lcx, lcy = 860, 400; cell=110
s.append(f'<text x="{lcx}" y="110" text-anchor="middle" font-size="17" fill="#2f5d8a" font-weight="bold">② LẠC THƯ (洛书) — tổng 45, ma phương</text>')
MAGIC=[[4,9,2],[3,5,7],[8,1,6]]
gx0,gy0 = lcx-1.5*cell, lcy-1.5*cell
for r in range(3):
    for c in range(3):
        n=MAGIC[r][c]; x0,y0=gx0+c*cell, gy0+r*cell
        s.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{cell-4}" height="{cell-4}" fill="#2f5d8a" fill-opacity="0.05" stroke="#bcd" stroke-width="1"/>')
        s.append(dots(x0+cell/2-2, y0+cell/2-12, n, n%2==1, r=4, pitch=11))
        s.append(f'<text x="{x0+cell/2-2:.0f}" y="{y0+cell-14:.0f}" text-anchor="middle" font-size="15" fill="#2f5d8a" font-weight="bold">{n}</text>')
# nhãn vị trí
s.append(f'<text x="{lcx}" y="{gy0-8:.0f}" text-anchor="middle" font-size="10.5" fill="#c0392b">戴九 (đội 9 trên đầu)</text>')
s.append(f'<text x="{lcx}" y="{gy0+3*cell+14:.0f}" text-anchor="middle" font-size="10.5" fill="#c0392b">履一 (đạp 1 dưới chân)</text>')
s.append(f'<text x="{lcx}" y="638" text-anchor="middle" font-size="11.5" fill="#777">Mọi hàng·cột·chéo đều = 15 · tổng 45 · DỤNG · vuông-vức · → Hậu Thiên</text>')
s.append(f'<text x="{lcx}" y="658" text-anchor="middle" font-size="11" fill="#999">戴九履一·左三右七·二四為肩·六八為足·五居中</text>')

s.append(f'<text x="{W/2}" y="{H-14}" text-anchor="middle" font-size="11" fill="#999">Cả hai đều có 5 ở giữa (Chu Hy) · sinh ra Thi-số 50 và quái-số · Hà Đồ THỂ, Lạc Thư DỤNG — gốc số của toàn bộ lưới Hoàng Cực</text>')
s.append('</svg>')
(OUT/"ha_lac.svg").write_text("\n".join(s))
print("✓ Vẽ xong ha_lac.svg")
