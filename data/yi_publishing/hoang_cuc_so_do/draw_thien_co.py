#!/usr/bin/env python3
"""ĐỒ THIÊN CƠ — đồng hồ một NGUYÊN (129.600 năm).
12 hội = 12 bích quái tiêu-tức = câu chuyện trời-đất-người: sinh→đỉnh→suy→đóng→tái sinh.
Số năm thật từ engine (NGUYEN_START -67016). 天开于子·人生于寅·物闭于戌 (dòng 1403)."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.constants import NGUYEN_START_ASTRO, NAM_MOI_HOI, HOI_CHI, HOI_QUE

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def vy(y): return f"{y}" if y > 0 else f"{-y+1}TCN"

# 12 bích quái (hào dưới→trên) + góc trên đồng hồ (乾 đỉnh, 坤 đáy)
BICH = {  # chi: (bits, góc°, mốc cosmogenesis, màu)
 "Tý":  ([1,0,0,0,0,0], 240, "天开 · trời mở", "#3f7d54"),
 "Sửu": ([1,1,0,0,0,0], 210, "地辟 · đất thành", "#3f7d54"),
 "Dần": ([1,1,1,0,0,0], 180, "人生 · người/vật sinh (开物)", "#2f6d44"),
 "Mão": ([1,1,1,1,0,0], 150, "", "#c9a13b"),
 "Thìn":([1,1,1,1,1,0], 120, "", "#c9a13b"),
 "Tỵ":  ([1,1,1,1,1,1],  90, "đỉnh · cực dương", "#c0392b"),
 "Ngọ": ([0,1,1,1,1,1],  60, "★ NAY (2026) · một âm sinh", "#c0392b"),
 "Mùi": ([0,0,1,1,1,1],  30, "", "#a85a3a"),
 "Thân":([0,0,0,1,1,1],   0, "天地 bất giao (否)", "#7a5a3a"),
 "Dậu": ([0,0,0,0,1,1], 330, "", "#5a4a6a"),
 "Tuất":([0,0,0,0,0,1], 300, "物闭 · đóng vật (闭物)", "#3a3a5a"),
 "Hợi": ([0,0,0,0,0,0], 270, "混沌 · hỗn mang → tái sinh", "#2f3a5a"),
}

W, H = 1180, 1020
cx, cy, R = W/2, 520, 320
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="42" text-anchor="middle" font-size="28" fill="#2a2018" font-weight="bold">ĐỒ THIÊN CƠ — đồng hồ một NGUYÊN</text>')
s.append(f'<text x="{W/2}" y="70" text-anchor="middle" font-size="14.5" fill="#7a5a2a">一元 = 129.600 năm = 12 hội · 12 bích quái = câu chuyện trời-đất-người: sinh → đỉnh → suy → đóng → tái sinh</text>')

s.append(f'<circle cx="{cx}" cy="{cy}" r="{R+72}" fill="none" stroke="#e0d5b8"/>')
s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-78}" fill="none" stroke="#e0d5b8"/>')
# cung dương thăng (trái) / âm giáng (phải)
s.append(f'<text x="{cx-R-30}" y="{cy}" text-anchor="middle" font-size="13" fill="#3f7d54" font-weight="bold" transform="rotate(-90 {cx-R-30} {cy})">DƯƠNG THĂNG (sinh trưởng)</text>')
s.append(f'<text x="{cx+R+34}" y="{cy}" text-anchor="middle" font-size="13" fill="#5a4a6a" font-weight="bold" transform="rotate(90 {cx+R+34} {cy})">ÂM GIÁNG (thâu tàng)</text>')

def yao(cx_, y, yng, w=30, h=4.5):
    if yng: return f'<rect x="{cx_-w/2:.0f}" y="{y}" width="{w}" height="{h}" fill="#5a3410"/>'
    g=5
    return (f'<rect x="{cx_-w/2:.0f}" y="{y}" width="{(w-g)/2:.0f}" height="{h}" fill="#5a3410"/>'
            f'<rect x="{cx_+g/2:.0f}" y="{y}" width="{(w-g)/2:.0f}" height="{h}" fill="#5a3410"/>')

for chi, (bits, ang, tag, col) in BICH.items():
    rad = math.radians(ang)
    x, y = cx + R*math.cos(rad), cy - R*math.sin(rad)
    que = HOI_QUE[chi]["que"]; han = HOI_QUE[chi]["han"]
    i = HOI_CHI.index(chi); ys = NGUYEN_START_ASTRO + i*NAM_MOI_HOI; ye = ys + NAM_MOI_HOI - 1
    now = chi == "Ngọ"
    s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="46" fill="{col}" fill-opacity="{0.16 if now else 0.09}" stroke="{col}" stroke-opacity="{0.9 if now else 0.45}" stroke-width="{2.4 if now else 1}"/>')
    for k in range(6):  # vẽ hào trên→dưới
        s.append(yao(x, y-16 + (5-k)*6, bits[k]))
    s.append(f'<text x="{x:.0f}" y="{y+30:.0f}" text-anchor="middle" font-size="13" fill="{col}" font-weight="bold">{han} {que}</text>')
    # nhãn ngoài: chi + năm + mốc
    lr = R + 52
    lx, ly = cx + lr*math.cos(rad), cy - lr*math.sin(rad)
    anchor = "middle"
    if math.cos(rad) > 0.3: anchor = "start"
    elif math.cos(rad) < -0.3: anchor = "end"
    s.append(f'<text x="{lx:.0f}" y="{ly-4:.0f}" text-anchor="{anchor}" font-size="12" fill="{col}" font-weight="bold">hội {chi}</text>')
    s.append(f'<text x="{lx:.0f}" y="{ly+11:.0f}" text-anchor="{anchor}" font-size="9.5" fill="#888">{vy(ys)}–{vy(ye)}</text>')
    if tag:
        s.append(f'<text x="{lx:.0f}" y="{ly+25:.0f}" text-anchor="{anchor}" font-size="10" fill="{"#c0392b" if now else "#777"}" font-weight="{"bold" if now else "normal"}">{esc(tag)}</text>')

# kim chỉ NAY → hội Ngọ
radn = math.radians(60)
xn, yn = cx + (R-90)*math.cos(radn), cy - (R-90)*math.sin(radn)
s.append(f'<line x1="{cx}" y1="{cy}" x2="{xn:.0f}" y2="{yn:.0f}" stroke="#c0392b" stroke-width="2.5" marker-end="url(#a)"/>')
s.append('<defs><marker id="a" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 z" fill="#c0392b"/></marker></defs>')
# tâm
s.append(f'<circle cx="{cx}" cy="{cy}" r="58" fill="#fbf7ef" stroke="#c9a13b"/>')
s.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">一元</text>')
s.append(f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="11" fill="#888">129.600 năm</text>')
s.append(f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-size="9.5" fill="#aaa">67017 TCN→62583 CN</text>')

# chốt
s.append(f'<text x="{W/2}" y="{H-44}" text-anchor="middle" font-size="13.5" fill="#2f5d8a">Ta đang ở <tspan fill="#c0392b" font-weight="bold">hội Ngọ</tspan> — vừa qua đỉnh (Càn), một âm mới sinh (Cấu): "vương giáng nhi bá". Còn ~39.000 năm tới 闭物.</text>')
s.append(f'<text x="{W/2}" y="{H-22}" text-anchor="middle" font-size="12" fill="#999">"Khang Tiết vốn là học KINH THẾ — coi nó chỉ để đoán việc tương lai là làm NHỎ học vấn ông" (尹和靖) · thiên cơ để HÀNH, không để bói</text>')
s.append('</svg>')
(OUT/"thien_co.svg").write_text("\n".join(s))
print("✓ Vẽ xong thien_co.svg")
