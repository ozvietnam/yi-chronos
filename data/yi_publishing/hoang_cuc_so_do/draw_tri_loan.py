#!/usr/bin/env python3
"""Chương 3 — ĐỒ TRỊ-LOẠN VẠN NĂM (định tính) từ tập Thượng.
Nguồn: tr.185 Hoàng thị "午会由禹至今, 王降而霸" + suy-cấp Hoàng-Đế-Vương-Bá (Nội Thiên).
KHÔNG vẽ năm chính xác (bảng đó ở tập Trung/Hạ) — chỉ dựng ARC định tính sách nêu rõ."""
from pathlib import Path
FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path("data/yi_publishing/hoang_cuc_so_do")
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# Bốn giai đoạn — cao độ = "đức trị" (cao→thấp = suy giáng). Mùa lịch sử.
STAGES = [
 # (nhãn, hạng, thượng-X, mùa, hội, đại biểu, cao_độ 0..1)
 ("TAM HOÀNG","皇 Hoàng","Đạo (vô vi)","Xuân","Tỵ (cuối)","Phục Hy·Thần Nông·Hoàng Đế",1.00,"#b8862a"),
 ("NGŨ ĐẾ","帝 Đế","Đức (nhường)","Hạ","Tỵ→Ngọ","Nghiêu · Thuấn",0.74,"#c98a2e"),
 ("TAM VƯƠNG","王 Vương","Công (chính)","Thu","Ngọ","Hạ Vũ · Thương · Chu",0.48,"#a85a3a"),
 ("NGŨ BÁ → nay","伯 Bá","Lực (tranh)","Đông","Ngọ","Tề Hoàn·Tấn Văn → hậu thế",0.24,"#7a4a52"),
]
W,H = 1100, 712
gx0, gx1 = 120, 980
gy0, gy1 = 140, 480   # gy0=đỉnh trị, gy1=đáy loạn
s=[f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="48" text-anchor="middle" font-size="29" fill="#2a2018" font-weight="bold">ĐỒ TRỊ–LOẠN VẠN NĂM (định tính)</text>')
s.append(f'<text x="{W/2}" y="78" text-anchor="middle" font-size="15.5" fill="#7a5a2a">皇极经世 · "Ngọ hội do Vũ chí kim, vương giáng nhi bá" (tr.185) — đức trị suy giáng theo mùa lịch sử</text>')
# trục
s.append(f'<line x1="{gx0}" y1="{gy0-20}" x2="{gx0}" y2="{gy1+30}" stroke="#bbb" stroke-width="1.5"/>')
s.append(f'<text x="{gx0-12}" y="{gy0-26}" text-anchor="end" font-size="13" fill="#888" transform="rotate(-90 {gx0-12} {gy0+150})">← ĐỨC TRỊ (cao = thịnh, thấp = loạn)</text>')
s.append(f'<line x1="{gx0}" y1="{gy1+30}" x2="{gx1+20}" y2="{gy1+30}" stroke="#bbb" stroke-width="1.5"/>')
s.append(f'<text x="{gx1}" y="{gy1+52}" text-anchor="middle" font-size="13" fill="#888">THỜI GIAN →</text>')
# đường arc suy giáng
n=len(STAGES); step=(gx1-gx0)/(n-1)
pts=[(gx0+i*step, gy1-(gy1-gy0)*st[6]) for i,st in enumerate(STAGES)]
path="M "+" L ".join(f"{x:.0f} {y:.0f}" for x,y in pts)
s.append(f'<path d="{path}" fill="none" stroke="#a85a3a" stroke-width="3" opacity="0.5"/>')
# vạch hội Tỵ→Ngọ (tại Hạ Vũ, giữa Ngũ Đế và Tam Vương)
vx=(pts[1][0]+pts[2][0])/2
s.append(f'<line x1="{vx}" y1="{gy0-10}" x2="{vx}" y2="{gy1+30}" stroke="#2f5d8a" stroke-width="2" stroke-dasharray="6 4"/>')
s.append(f'<text x="{vx}" y="{gy0-16}" text-anchor="middle" font-size="14" fill="#2f5d8a" font-weight="bold">⟵ HỘI TỴ | HỘI NGỌ ⟶ (Hạ Vũ)</text>')
# nốt
for i,(lab,hang,thuong,mua,hoi,db,h_,col) in enumerate(STAGES):
    x,y=pts[i]
    s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="{col}"/>')
    s.append(f'<text x="{x:.0f}" y="{y-26:.0f}" text-anchor="middle" font-size="18" fill="{col}" font-weight="bold">{esc(hang)}</text>')
    by=gy1+78+ (i%2)*0  # khối mô tả dưới trục
    bx=gx0+i*step- 92 if i< n-1 else gx1-184
    bx=max(40,min(bx,W-200))
    s.append(f'<rect x="{bx}" y="{by}" width="200" height="92" rx="8" fill="{col}" opacity="0.10" stroke="{col}" stroke-opacity="0.4"/>')
    s.append(f'<text x="{bx+100}" y="{by+22}" text-anchor="middle" font-size="15" fill="{col}" font-weight="bold">{esc(lab)}</text>')
    s.append(f'<text x="{bx+100}" y="{by+42}" text-anchor="middle" font-size="12.5" fill="#444">Thượng: {esc(thuong)}</text>')
    s.append(f'<text x="{bx+100}" y="{by+60}" text-anchor="middle" font-size="12" fill="#666">Mùa {esc(mua)} · Hội {esc(hoi)}</text>')
    s.append(f'<text x="{bx+100}" y="{by+78}" text-anchor="middle" font-size="11.5" fill="#888">{esc(db)}</text>')
    # nối nốt xuống khối
    s.append(f'<line x1="{x:.0f}" y1="{y+13:.0f}" x2="{bx+100}" y2="{by}" stroke="{col}" stroke-opacity="0.3" stroke-dasharray="3 3"/>')
# ghi chú Bĩ→Thái
s.append(f'<text x="{W/2}" y="{H-26}" text-anchor="middle" font-size="13.5" fill="#2f5d8a">"Thiên địa đại vận, Bĩ dịch nhi Thái" (tr.185) — suy tới cực thì có cơ xoay lại. Đây là ARC ĐỊNH TÍNH; bảng năm chính xác ở tập Trung/Hạ.</text>')
s.append('</svg>')
(OUT/"tri_loan_van_nam.svg").write_text("\n".join(s))
print("✓ Vẽ xong: tri_loan_van_nam.svg")
