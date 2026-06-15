#!/usr/bin/env python3
"""Chương 3 — ĐỒ TRỊ-LOẠN VẠN NĂM (ĐỊNH LƯỢNG — engine đã neo đúng 2026).
Nguồn: tr.185 "午会由禹至今" + mốc neo tự tự bộ trọn (304 CN = thế 2245, vận 188).
Năm/thế thật lấy từ engine.hoang_cuc (verify 4 mốc khớp sách)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.nguyen_hoi_van_the import locate_year

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def vy(y): return f"{y} CN" if y > 0 else f"{-y+1} TCN"
def the_of(y): return locate_year(y)["the"]["so_toan_nguyen"]

# 4 giai đoạn — năm đại biểu (astronomical), engine tính thế thật
STAGES = [
 ("TAM HOÀNG","皇 Hoàng","Đạo · vô vi","Xuân", None, "Phục Hy → Hoàng Đế", 1.00, "#b8862a"),
 ("NGŨ ĐẾ","帝 Đế","Đức · nhường","Hạ", -2356, "Nghiêu (Giáp Thìn) · Thuấn", 0.74, "#c98a2e"),
 ("TAM VƯƠNG","王 Vương","Công · chính","Thu", -2070, "Hạ Vũ · Thương · Chu", 0.48, "#a85a3a"),
 ("NGŨ BÁ → nay","伯 Bá","Lực · tranh","Đông", -770, "Bình Vương → Tống → nay", 0.24, "#7a4a52"),
]
# ranh hội Tỵ/Ngọ: vận 181 đầu hội Ngọ
hoi_ngo_start = None
for y in range(-2300, -1900):
    if locate_year(y)["van"]["so_toan_nguyen"] == 181:
        hoi_ngo_start = y; break

W, H = 1120, 720
gx0, gx1 = 130, 990
gy0, gy1 = 150, 470
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="46" text-anchor="middle" font-size="28" fill="#2a2018" font-weight="bold">ĐỒ TRỊ–LOẠN VẠN NĂM</text>')
s.append(f'<text x="{W/2}" y="74" text-anchor="middle" font-size="15" fill="#7a5a2a">皇极经世 · "Ngọ hội do Vũ chí kim, vương giáng nhi bá" — engine neo 304 CN = thế 2245 (tự tự bộ trọn)</text>')
# trục
s.append(f'<line x1="{gx0}" y1="{gy0-16}" x2="{gx0}" y2="{gy1+24}" stroke="#bbb" stroke-width="1.5"/>')
s.append(f'<text x="{gx0-14}" y="{(gy0+gy1)/2}" font-size="12.5" fill="#888" transform="rotate(-90 {gx0-14} {(gy0+gy1)/2})" text-anchor="middle">ĐỨC TRỊ (cao=thịnh · thấp=loạn)</text>')
s.append(f'<line x1="{gx0}" y1="{gy1+24}" x2="{gx1+24}" y2="{gy1+24}" stroke="#bbb" stroke-width="1.5"/>')
s.append(f'<text x="{gx1+10}" y="{gy1+44}" text-anchor="middle" font-size="12.5" fill="#888">THỜI GIAN →</text>')
n = len(STAGES); step = (gx1-gx0)/(n-1)
pts = [(gx0+i*step, gy1-(gy1-gy0)*st[6]) for i, st in enumerate(STAGES)]
s.append(f'<path d="M {" L ".join(f"{x:.0f} {y:.0f}" for x,y in pts)}" fill="none" stroke="#a85a3a" stroke-width="3" opacity="0.45"/>')
# ranh hội Tỵ → Ngọ (giữa Ngũ Đế và Tam Vương)
vx = (pts[1][0]+pts[2][0])/2
s.append(f'<line x1="{vx}" y1="{gy0-8}" x2="{vx}" y2="{gy1+24}" stroke="#2f5d8a" stroke-width="2" stroke-dasharray="6 4"/>')
s.append(f'<text x="{vx}" y="{gy0-14}" text-anchor="middle" font-size="13.5" fill="#2f5d8a" font-weight="bold">⟵ HỘI TỴ | HỘI NGỌ ⟶ (vận 181, ~{vy(hoi_ngo_start)})</text>')
for i, (lab, hang, thuong, mua, yr, db, h_, col) in enumerate(STAGES):
    x, y = pts[i]
    s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="12" fill="{col}"/>')
    s.append(f'<text x="{x:.0f}" y="{y-24:.0f}" text-anchor="middle" font-size="17" fill="{col}" font-weight="bold">{esc(hang)}</text>')
    bx = max(36, min(gx0+i*step-96, W-204)); by = gy1+66
    s.append(f'<rect x="{bx}" y="{by}" width="200" height="108" rx="8" fill="{col}" opacity="0.10" stroke="{col}" stroke-opacity="0.4"/>')
    s.append(f'<text x="{bx+100}" y="{by+22}" text-anchor="middle" font-size="14.5" fill="{col}" font-weight="bold">{esc(lab)}</text>')
    s.append(f'<text x="{bx+100}" y="{by+41}" text-anchor="middle" font-size="12" fill="#444">Thượng: {esc(thuong)} · Mùa {esc(mua)}</text>')
    if yr is not None:
        L = locate_year(yr)
        s.append(f'<text x="{bx+100}" y="{by+60}" text-anchor="middle" font-size="11.5" fill="#2f5d8a">{esc(vy(yr))} · hội {L["hoi"]["chi"]} · thế {L["the"]["so_toan_nguyen"]}</text>')
    else:
        s.append(f'<text x="{bx+100}" y="{by+60}" text-anchor="middle" font-size="11.5" fill="#888">trước hội Ngọ (hội Tỵ)</text>')
    s.append(f'<text x="{bx+100}" y="{by+80}" text-anchor="middle" font-size="11" fill="#777">{esc(db)}</text>')
    s.append(f'<line x1="{x:.0f}" y1="{y+12:.0f}" x2="{bx+100}" y2="{by}" stroke="{col}" stroke-opacity="0.3" stroke-dasharray="3 3"/>')
s.append(f'<text x="{W/2}" y="{H-18}" text-anchor="middle" font-size="13" fill="#2f5d8a">"Thiên địa đại vận, Bĩ dịch nhi Thái" — suy tới cực thì có cơ xoay lại · Nay (2026) = hội Ngọ, vận 192, thế 2302</text>')
s.append('</svg>')
(OUT/"tri_loan_van_nam.svg").write_text("\n".join(s))
print(f"✓ Vẽ xong tri_loan_van_nam.svg · ranh hội Ngọ ~{vy(hoi_ngo_start)} · 2026=thế {the_of(2026)}")
