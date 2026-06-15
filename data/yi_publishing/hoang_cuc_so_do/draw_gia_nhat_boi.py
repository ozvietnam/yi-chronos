#!/usr/bin/env python3
"""GIA-NHẤT-BỘI (加一倍法) — cây nhân đôi sinh 64 quẻ = số nhị phân.
Nguồn: Quan Vật Ngoại Thiên (bộ trọn, tr.~29-31 tự tự): 道→1太极→2两仪→4四象→
8八卦→64卦. Trình Hạo gọi 加一倍法. Triết lý chữ Một (一→vạn→一)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 900
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">GIA-NHẤT-BỘI (加一倍法) — cây nhân đôi sinh 64 quẻ</text>')
s.append(f'<text x="{W/2}" y="67" text-anchor="middle" font-size="14" fill="#7a5a2a">道→1 Thái Cực→2 Lưỡng Nghi→4 Tứ Tượng→8 Bát Quái→…→64 · Trình Hạo gọi "phép thêm một gấp đôi"</text>')

# ── helper vẽ hào (yang = vạch liền, yin = vạch đứt) ─────────
def yao(cx, y, yang, w=44, h=7):
    if yang:
        return f'<rect x="{cx-w/2:.0f}" y="{y}" width="{w}" height="{h}" fill="#7a3410"/>'
    g=6
    return (f'<rect x="{cx-w/2:.0f}" y="{y}" width="{(w-g)/2:.0f}" height="{h}" fill="#7a3410"/>'
            f'<rect x="{cx+g/2:.0f}" y="{y}" width="{(w-g)/2:.0f}" height="{h}" fill="#7a3410"/>')

def gua(cx, y_top, lines):  # lines bottom→top (list yang bool), vẽ từ dưới lên
    out=[]
    for i,yng in enumerate(lines):
        out.append(yao(cx, y_top + (len(lines)-1-i)*11, yng))
    return "".join(out)

# ── cây nhân đôi: 太极 → 两仪 → 四象 → 八卦 ──────────────────
top=95
s.append(f'<text x="{W/2}" y="{top}" text-anchor="middle" font-size="14" fill="#7a3410" font-weight="bold">① CÂY NHÂN ĐÔI — vạch liền = dương (1), vạch đứt = âm (0)</text>')
# Thái cực
s.append(f'<circle cx="{W/2}" cy="{top+34}" r="17" fill="#c9a13b" fill-opacity="0.3" stroke="#a8621c"/>')
s.append(f'<text x="{W/2}" y="{top+39}" text-anchor="middle" font-size="14" fill="#7a3410" font-weight="bold">太极</text>')
s.append(f'<text x="{W/2+26}" y="{top+39}" font-size="11" fill="#888">1 — Thái Cực</text>')
# 两仪 (1 hào): dương, âm
ly=top+72
for cx,yng,lab in [(W/2-260,True,"dương"),(W/2+260,False,"âm")]:
    s.append(yao(cx,ly,yng))
    s.append(f'<line x1="{W/2}" y1="{top+51}" x2="{cx}" y2="{ly-3}" stroke="#ccc"/>')
s.append(f'<text x="{W/2}" y="{ly+6}" text-anchor="middle" font-size="11" fill="#888">2 — Lưỡng Nghi</text>')
# 四象 (2 hào)
sy=ly+30
si=[(True,True),(False,True),(True,False),(False,False)]  # (bottom,top)
for i,(b,t) in enumerate(si):
    cx=W/2-330+i*220
    s.append(yao(cx,sy+11,b)); s.append(yao(cx,sy,t))
s.append(f'<text x="{W-70}" y="{sy+12}" text-anchor="end" font-size="11" fill="#888">4 — Tứ Tượng</text>')
# 八卦 (3 hào) — thứ tự tiên thiên 乾兑离震巽坎艮坤
gy=sy+44
TRIGRAMS=[((1,1,1),"乾","Càn"),((1,1,0),"兑","Đoài"),((1,0,1),"离","Ly"),((1,0,0),"震","Chấn"),
          ((0,1,1),"巽","Tốn"),((0,1,0),"坎","Khảm"),((0,0,1),"艮","Cấn"),((0,0,0),"坤","Khôn")]
n=len(TRIGRAMS); slot=(W-160)/n
for i,(bits,zh,vi) in enumerate(TRIGRAMS):
    cx=80+slot*(i+0.5)
    s.append(gua(cx,gy,list(bits)))   # bits = (bottom,mid,top)
    s.append(f'<text x="{cx:.0f}" y="{gy+58}" text-anchor="middle" font-size="14" fill="#7a3410" font-weight="bold">{zh}</text>')
    s.append(f'<text x="{cx:.0f}" y="{gy+74}" text-anchor="middle" font-size="10.5" fill="#777">{vi}</text>')
s.append(f'<text x="{W-70}" y="{gy+12}" text-anchor="end" font-size="11" fill="#888">8 — Bát Quái</text>')
s.append(f'<text x="{W/2}" y="{gy+98}" text-anchor="middle" font-size="11.5" fill="#999">…mỗi quẻ thêm 1 hào lại gấp đôi: 8→16→32→<tspan fill="#7a3410" font-weight="bold">64 quẻ</tspan> (6 hào)</text>')

# ── ② thang lũy thừa 2 ───────────────────────────────────────
py=gy+128
s.append(f'<text x="80" y="{py}" font-size="14" fill="#2f5d8a" font-weight="bold">② Đây chính là LŨY THỪA CỦA 2:</text>')
ladder=[("2⁰","1","太极"),("2¹","2","两仪"),("2²","4","四象"),("2³","8","八卦"),("2⁴","16",""),("2⁵","32",""),("2⁶","64","64 quẻ")]
for i,(p,v,lab) in enumerate(ladder):
    x=120+i*150
    s.append(f'<rect x="{x}" y="{py+14}" width="120" height="44" rx="6" fill="#2f5d8a" fill-opacity="{0.06+i*0.02}" stroke="#2f5d8a" stroke-opacity="0.4"/>')
    s.append(f'<text x="{x+60}" y="{py+34}" text-anchor="middle" font-size="13" fill="#2f5d8a">{p} = <tspan font-weight="bold" font-size="16">{v}</tspan></text>')
    s.append(f'<text x="{x+60}" y="{py+51}" text-anchor="middle" font-size="10" fill="#888">{esc(lab)}</text>')
    if i<len(ladder)-1: s.append(f'<text x="{x+132}" y="{py+40}" text-anchor="middle" font-size="15" fill="#bbb">×2</text>')

# ── ③ cầu nối nhị phân → Leibniz → AI ───────────────────────
by=py+86
s.append(f'<rect x="80" y="{by}" width="{(W-180)/2:.0f}" height="120" rx="9" fill="#3f7d54" fill-opacity="0.06" stroke="#3f7d54" stroke-opacity="0.4"/>')
s.append(f'<text x="110" y="{by+26}" font-size="14" fill="#2f6d44" font-weight="bold">③ Cầu nối: NHỊ PHÂN</text>')
for k,ln in enumerate([
  "Âm = vạch đứt = 0 · Dương = vạch liền = 1",
  "Một quẻ = 6 hào = 6 chữ số nhị phân = 2⁶ = 64",
  "Leibniz (1703) thấy đồ Tiên Thiên Phục Hy →",
  "nhận ra chính là số học nhị phân → máy tính/AI"]):
    s.append(f'<text x="110" y="{by+48+k*19}" font-size="11.5" fill="#444">{esc(ln)}</text>')
# ── ④ triết lý chữ Một ───────────────────────────────────────
bx=80+(W-180)/2+20
s.append(f'<rect x="{bx:.0f}" y="{by}" width="{(W-180)/2:.0f}" height="120" rx="9" fill="#a8621c" fill-opacity="0.06" stroke="#a8621c" stroke-opacity="0.4"/>')
s.append(f'<text x="{bx+30:.0f}" y="{by+26}" font-size="14" fill="#a8621c" font-weight="bold">④ Triết lý chữ MỘT (一)</text>')
s.append(f'<text x="{bx+(W-180)/2/2:.0f}" y="{by+58}" text-anchor="middle" font-size="20" fill="#7a3410" font-weight="bold">一 → vạn → 一</text>')
for k,ln in enumerate([
  "Vạn vật khởi từ MỘT, phân thành vạn, rồi quy MỘT",
  "Sách tự nối hiện đại (tr.31): cải gen, nhân bản —",
  "một tế bào phân thành nghìn vạn tế bào, cùng lý ấy"]):
    s.append(f'<text x="{bx+(W-180)/2/2:.0f}" y="{by+76+k*17}" text-anchor="middle" font-size="10.8" fill="#444">{esc(ln)}</text>')

s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="11" fill="#999">Nguồn: Quan Vật Ngoại Thiên (tự tự bộ trọn) · "加一倍法" = lời Trình Minh Đạo · Thái thị: "Tần Hán đến nay, một người mà thôi"</text>')
s.append('</svg>')
(OUT/"gia_nhat_boi.svg").write_text("\n".join(s))
print("✓ Vẽ xong gia_nhat_boi.svg")
