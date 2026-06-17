#!/usr/bin/env python3
"""ĐỒ HẬU THIÊN (后天八卦 Văn Vương) — bát quái "để DÙNG", đồng hồ bốn mùa.
Nguồn: Quan Vật Ngoại Thiên ch.5 后天象数 (tr.461); 说卦传 "帝出乎震…成言乎艮".
先天为体 后天为用; 离南坎北震东兑西; 震春离夏兑秋坎冬; nằm trên số Lạc Thư."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 860
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">ĐỒ HẬU THIÊN (后天八卦 Văn Vương) — bát quái "để DÙNG"</text>')
s.append(f'<text x="{W/2}" y="68" text-anchor="middle" font-size="14" fill="#7a5a2a">"先天为体，后天为用" · 帝出乎震 → … → 成言乎艮 · đồng hồ bốn mùa · trên Nam dưới Bắc trái Đông phải Tây</text>')

def yao(cx, y, yang, w=42, h=6):
    if yang: return f'<rect x="{cx-w/2:.1f}" y="{y}" width="{w}" height="{h}" fill="#7a3410"/>'
    g=6
    return (f'<rect x="{cx-w/2:.1f}" y="{y}" width="{(w-g)/2:.1f}" height="{h}" fill="#7a3410"/>'
            f'<rect x="{cx+g/2:.1f}" y="{y}" width="{(w-g)/2:.1f}" height="{h}" fill="#7a3410"/>')
def gua(cx, cy, bits):           # bits=(dưới,giữa,trên); vẽ trên→dưới
    out=[]
    for i in range(3):
        out.append(yao(cx, cy-11 + (2-i)*10, bits[i]))
    return "".join(out)

cx, cy, R = 430, 450, 250
# 8 quái hậu thiên: (tên, vi, bits, góc°, mùa/phương, số Lạc Thư, màu)
BG = [("离","Ly",(1,0,1),90,"Nam · Hạ",9,"#c0392b"),
      ("巽","Tốn",(0,1,1),135,"Đông-Nam",4,"#6a8a3a"),
      ("震","Chấn",(1,0,0),180,"Đông · Xuân",3,"#3f7d54"),
      ("艮","Cấn",(0,0,1),225,"Đông-Bắc",8,"#7a6a52"),
      ("坎","Khảm",(0,1,0),270,"Bắc · mùa Đông",1,"#2f5d8a"),
      ("乾","Càn",(1,1,1),315,"Tây-Bắc",6,"#8a7a55"),
      ("兑","Đoài",(1,1,0),0,"Tây · Thu",7,"#c9a13b"),
      ("坤","Khôn",(0,0,0),45,"Tây-Nam",2,"#7a6a52")]
# vòng dẫn + tâm
s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#d8c89a" stroke-dasharray="5 5"/>')
s.append(f'<circle cx="{cx}" cy="{cy}" r="30" fill="#c9a13b" fill-opacity="0.18" stroke="#a8621c"/>')
s.append(f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">5</text>')
s.append(f'<text x="{cx}" y="{cy+15}" text-anchor="middle" font-size="9.5" fill="#999">Trung</text>')
def pos(ang, r): rad=math.radians(ang); return cx+r*math.cos(rad), cy-r*math.sin(rad)
# mũi tên 帝出乎震 (chu trình: 震→巽→离→坤→兑→乾→坎→艮, theo chiều kim đồng hồ)
order=[180,135,90,45,0,315,270,225]
for i in range(8):
    a0,a1=order[i], order[(i+1)%8]
    x0,y0=pos(a0,R+0); x1,y1=pos(a1,R+0)
    s.append(f'<path d="M {x0:.0f} {y0:.0f} A {R} {R} 0 0 1 {x1:.0f} {y1:.0f}" fill="none" stroke="#bbb" stroke-width="1" marker-end="url(#ar)"/>')
s.append('<defs><marker id="ar" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#bbb"/></marker></defs>')
# các quái
for zh,vi,bits,ang,mp,lac,col in BG:
    x,y=pos(ang,R)
    s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="40" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.45"/>')
    s.append(gua(x,y-6,bits))
    s.append(f'<text x="{x:.0f}" y="{y+24:.0f}" text-anchor="middle" font-size="16" fill="{col}" font-weight="bold">{zh}</text>')
    # nhãn ngoài
    lx,ly=pos(ang,R+72)
    s.append(f'<text x="{lx:.0f}" y="{ly-4:.0f}" text-anchor="middle" font-size="12" fill="{col}" font-weight="bold">{vi} · Lạc {lac}</text>')
    s.append(f'<text x="{lx:.0f}" y="{ly+11:.0f}" text-anchor="middle" font-size="10" fill="#888">{esc(mp)}</text>')
s.append(f'<text x="{cx}" y="{cy+R+95:.0f}" text-anchor="middle" font-size="11" fill="#999">Mũi tên = 帝出乎震 (chu trình năm) · số Lạc = vị trí trên Lạc Thư (洛书 → Hậu Thiên)</text>')

# ── panel phải: THỂ vs DỤNG ──────────────────────────────────
px=820
s.append(f'<rect x="{px}" y="120" width="320" height="300" rx="10" fill="#2f5d8a" fill-opacity="0.05" stroke="#2f5d8a" stroke-opacity="0.3"/>')
s.append(f'<text x="{px+160}" y="148" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">TIÊN THIÊN vs HẬU THIÊN</text>')
rows=[("","Tiên Thiên (Ch8)","Hậu Thiên (đây)"),
      ("Vai","THỂ 体 (gốc)","DỤNG 用 (dùng)"),
      ("Tổ","Phục Hy","Văn Vương"),
      ("Trên-dưới","乾南 坤北","离南 坎北"),
      ("Đông-Tây","日东 月西","震东 兑西"),
      ("Nghĩa","lập thể · vũ trụ","mặt phẳng · bốn mùa"),
      ("Gốc số","Hà Đồ (55)","Lạc Thư (45)")]
for i,(a,b,c) in enumerate(rows):
    yy=176+i*32
    fw=' font-weight="bold"' if i==0 else ''
    s.append(f'<text x="{px+14}" y="{yy}" font-size="10.5" fill="#888">{esc(a)}</text>')
    s.append(f'<text x="{px+92}" y="{yy}" font-size="10.8" fill="#2f5d8a"{fw}>{esc(b)}</text>')
    s.append(f'<text x="{px+210}" y="{yy}" font-size="10.8" fill="#a8621c"{fw}>{esc(c)}</text>')
# 帝出乎震 box
s.append(f'<rect x="{px}" y="440" width="320" height="250" rx="10" fill="#3f7d54" fill-opacity="0.05" stroke="#3f7d54" stroke-opacity="0.3"/>')
s.append(f'<text x="{px+160}" y="468" text-anchor="middle" font-size="14" fill="#2f6d44" font-weight="bold">帝出乎震 — chu trình mùa</text>')
cyc=[("震 Chấn","Xuân — vạn vật khởi động","#3f7d54"),
     ("巽 Tốn","cuối xuân — đều khắp",""),
     ("离 Ly","Hạ — sáng tỏ, gặp nhau","#c0392b"),
     ("坤 Khôn","cuối hạ — nuôi dưỡng",""),
     ("兑 Đoài","Thu — vui, thu hoạch","#c9a13b"),
     ("乾 Càn","cuối thu — giao tranh",""),
     ("坎 Khảm","Đông — nhọc, ẩn tàng","#2f5d8a"),
     ("艮 Cấn","cuối đông — thành, dừng","")]
for i,(q,d,c) in enumerate(cyc):
    yy=492+i*24
    s.append(f'<text x="{px+16}" y="{yy}" font-size="11" fill="{c or "#555"}" font-weight="{"bold" if c else "normal"}">{esc(q)}</text>')
    s.append(f'<text x="{px+92}" y="{yy}" font-size="10" fill="#777">{esc(d)}</text>')

s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="11" fill="#999">Văn Vương đổi vị Phục Hy "để ứng thiên thời, ứng địa phương" — biến THỂ của Dịch thành DỤNG (tr.461) · "vương giả chi pháp"</text>')
s.append('</svg>')
(OUT/"hau_thien.svg").write_text("\n".join(s))
print("✓ Vẽ xong hau_thien.svg")
