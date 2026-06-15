#!/usr/bin/env python3
"""ĐỒ TIÊN THIÊN (先天圆图 + 方图) — trọn 64 quẻ thành vòng tròn + ô vuông.
Thứ tự tiên thiên kiểm bằng nhị phân (Càn=1 toàn dương … Khôn=64 toàn âm).
Bài trí theo chính văn (tr.~galley): Càn Nam(trên)·Khôn Bắc(dưới)·dương thăng
trái (复→乾)·âm giáng phải (姤→坤). 左东右西上南下北 (lối cổ)."""
import sys, math, colorsys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# Thứ tự tiên thiên 1-64
NAMES = ('乾 夬 大有 大壮 小畜 需 大畜 泰 履 兑 睽 归妹 中孚 节 损 临 同人 革 离 丰 家人 既济 贲 明夷 '
         '无妄 随 噬嗑 震 益 屯 颐 复 姤 大过 鼎 恒 巽 井 蛊 升 讼 困 未济 解 涣 坎 蒙 师 遁 咸 旅 小过 '
         '渐 蹇 艮 谦 否 萃 晋 豫 观 比 剥 坤').split()
def bits_of(n):           # n 1..64 → [b1..b6] dưới→trên (b1 = MSB)
    v = 64 - n
    return [(v >> (6 - i)) & 1 for i in range(1, 7)]
def yang_of(n): return bin(64 - n).count("1")
def color(y):             # 0 âm→indigo, 6 dương→vàng
    t = y / 6
    r, g, b = colorsys.hsv_to_rgb(0.62 - 0.50 * t, 0.55 - 0.2 * t, 0.55 + 0.40 * t)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

W, H = 1180, 1420
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="42" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">ĐỒ TIÊN THIÊN — trọn 64 quẻ Phục Hy</text>')
s.append(f'<text x="{W/2}" y="70" text-anchor="middle" font-size="14" fill="#7a5a2a">先天圆图 + 方图 · cùng đồ Leibniz xem năm 1703 · vạch liền=dương=1, vạch đứt=âm=0</text>')

# ── helper: mini-quẻ 6 hào (dưới→trên) tại (x,y) ─────────────
def mini(x, y, bits, w=15, hh=1.7, gap=1.5, col="#7a3410"):
    out = []
    total = 6 * hh + 5 * gap
    for i, b in enumerate(bits):            # i=0 hào dưới
        yy = y + total/2 - (i+1)*hh - i*gap
        if b:
            out.append(f'<rect x="{x-w/2:.1f}" y="{yy:.1f}" width="{w}" height="{hh}" fill="{col}"/>')
        else:
            g = 4
            out.append(f'<rect x="{x-w/2:.1f}" y="{yy:.1f}" width="{(w-g)/2:.1f}" height="{hh}" fill="{col}"/>')
            out.append(f'<rect x="{x+g/2:.1f}" y="{yy:.1f}" width="{(w-g)/2:.1f}" height="{hh}" fill="{col}"/>')
    return "".join(out)

# ── ① 圆图 — vòng tròn 64 quẻ ────────────────────────────────
cx, cy, R = W/2, 400, 285
s.append(f'<circle cx="{cx}" cy="{cy}" r="{R+30}" fill="none" stroke="#e0d5b8"/>')
s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-34}" fill="none" stroke="#e0d5b8"/>')
def place(n):
    if n <= 32:  ang = 90 + (n - 0.5) / 32 * 180          # nửa trái: dương thăng 乾(trên)→复(dưới)
    else:        ang = 90 - (n - 33 + 0.5) / 32 * 180     # nửa phải: âm giáng 姤(trên)→坤(dưới)
    r = math.radians(ang)
    return cx + R*math.cos(r), cy - R*math.sin(r), ang
for n in range(1, 65):
    x, y, ang = place(n)
    y_ng = yang_of(n)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="{color(y_ng)}" fill-opacity="0.30"/>')
    s.append(mini(x, y, bits_of(n)))
# 4 phương + điểm sinh
for nm, vi, n, dx, dy, col in [("乾","Nam ☰",1,0,-1,"#a8621c"),("坤","Bắc ☷",64,0,1,"#2f3a6a"),
                                ("离","Đông",19,-1,0,"#a85a3a"),("坎","Tây",46,1,0,"#2f6d8a")]:
    x,y,_=place(n)
    s.append(f'<text x="{x+dx*38:.0f}" y="{y+dy*44+5:.0f}" text-anchor="middle" font-size="15" fill="{col}" font-weight="bold">{nm}</text>')
    s.append(f'<text x="{x+dx*38:.0f}" y="{y+dy*44+20:.0f}" text-anchor="middle" font-size="9.5" fill="#999">{esc(vi)}</text>')
# 复 / 姤 điểm sinh
for nm,lab,n,col in [("复","一dương sinh →",32,"#c0392b"),("姤","← một âm sinh",33,"#2f3a6a")]:
    x,y,_=place(n)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="none" stroke="{col}" stroke-width="1.8"/>')
s.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-size="13" fill="#888">① 圆图 — vòng tròn</text>')
s.append(f'<text x="{cx}" y="{cy+10}" text-anchor="middle" font-size="11" fill="#aaa">dương thăng bên trái</text>')
s.append(f'<text x="{cx}" y="{cy+26}" text-anchor="middle" font-size="11" fill="#aaa">âm giáng bên phải</text>')
s.append(f'<text x="{cx}" y="{cy+46}" text-anchor="middle" font-size="10" fill="#bbb">(复·姤 khoanh đỏ = điểm sinh 1 dương / 1 âm)</text>')

# ── ② 方图 — ô vuông 8×8 ─────────────────────────────────────
TRI = [("乾",(1,1,1)),("兑",(1,1,0)),("离",(1,0,1)),("震",(1,0,0)),
       ("巽",(0,1,1)),("坎",(0,1,0)),("艮",(0,0,1)),("坤",(0,0,0))]  # 先天: (dưới,giữa,trên)
def hexname(low, up):
    (lb,lm,lt),(ub,um,ut)=low,up
    v = lb<<5|lm<<4|lt<<3|ub<<2|um<<1|ut
    return NAMES[64 - v - 1]
gx0, gy0, cell = (W-8*70)/2, 800, 70
s.append(f'<text x="{W/2}" y="{gy0-30}" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">② 方图 — ô vuông 8×8 (hàng = quái TRÊN · cột = quái DƯỚI, thứ tự tiên thiên 乾兑离震巽坎艮坤)</text>')
for r,(uz,ub) in enumerate(TRI):
    s.append(f'<text x="{gx0-14}" y="{gy0+r*cell+cell/2+5:.0f}" text-anchor="middle" font-size="13" fill="#8a4a14" font-weight="bold">{uz}</text>')
    for c,(lz,lb) in enumerate(TRI):
        if r==0: s.append(f'<text x="{gx0+c*cell+cell/2:.0f}" y="{gy0-8}" text-anchor="middle" font-size="13" fill="#8a4a14" font-weight="bold">{lz}</text>')
        nm = hexname(lb, ub)
        n = NAMES.index(nm)+1
        x0,y0=gx0+c*cell, gy0+r*cell
        s.append(f'<rect x="{x0}" y="{y0}" width="{cell-2}" height="{cell-2}" fill="{color(yang_of(n))}" fill-opacity="0.13" stroke="#d8be86" stroke-opacity="0.6"/>')
        s.append(mini(x0+cell/2, y0+24, bits_of(n), w=24, hh=2.4, gap=2.2))
        s.append(f'<text x="{x0+cell/2:.0f}" y="{y0+cell-10:.0f}" text-anchor="middle" font-size="13" fill="#3a2e20">{nm}</text>')
s.append(f'<text x="{W/2}" y="{H-30}" text-anchor="middle" font-size="11.5" fill="#999">Tịch quái dương (复·临·泰·大壮·夬·乾) nằm đúng vị trí 32·16·8·4·2·1 = lũy thừa 2 (Chương 7) · 乾 góc trên-trái, 坤 góc dưới-phải</text>')
s.append(f'<text x="{W/2}" y="{H-12}" text-anchor="middle" font-size="10.5" fill="#aaa">Đọc nhị phân (âm=0 dương=1): vòng tròn chạy từ 0 (坤) đến 63 (乾) — chính dãy Leibniz nhận ra</text>')
s.append('</svg>')
(OUT/"tien_thien.svg").write_text("\n".join(s))
print("✓ Vẽ xong tien_thien.svg")
