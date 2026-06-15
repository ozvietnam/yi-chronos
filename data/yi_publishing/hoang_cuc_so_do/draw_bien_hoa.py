#!/usr/bin/env python3
"""Chương 2 — VẼ LẠI 大小四象图 (bảng đối ứng tổng) + 经世变化图 (đồ sinh hóa).
Dữ liệu giải mã + verify từ tr.263-264 (qwen-VL). Đọc → hiểu → vẽ lại."""
from pathlib import Path

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path("data/yi_publishing/hoang_cuc_so_do")
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# 8 ĐẲNG: Trời 4 (dương/động) + Đất 4 (âm/tĩnh) × 10 thuộc tính.
# (thời, quẻ, thiên-thể, khí-hậu, mùa/kinh, cai-trị/đạo, đức/giai-cấp, tính/sinh-vật, pháp/đoạn, số)
TROI = [
 ("元","Nguyên","乾","Càn","日","Nhật","暑","Thử·nóng","春","Xuân","皇","Hoàng","仁","Nhân","性","Tính","化","Hóa","1"),
 ("会","Hội","兑","Đoài","月","Nguyệt","寒","Hàn·lạnh","夏","Hạ","帝","Đế","义","Nghĩa","情","Tình","教","Giáo","10"),
 ("运","Vận","离","Ly","星","Tinh","昼","Trú·ngày","秋","Thu","王","Vương","礼","Lễ","形","Hình","劝","Khuyến","100"),
 ("世","Thế","震","Chấn","辰","Thần","夜","Dạ·đêm","冬","Đông","伯","Bá","智","Trí","体","Thể","率","Suất","1.000"),
]
DAT = [
 ("岁","Tuế","坤","Khôn","水","Thủy","雨","Vũ·mưa","易","Dịch","道","Đạo","士","Sĩ","走","Tẩu·thú","生","Sinh","1"),
 ("月","Nguyệt","艮","Cấn","火","Hỏa","风","Phong·gió","书","Thư","德","Đức","农","Nông","飞","Phi·chim","长","Trưởng","10"),
 ("日","Nhật","坎","Khảm","土","Thổ","露","Lộ·sương","诗","Thi","功","Công","工","Thợ","草","Thảo·cỏ","收","Thu","100"),
 ("辰","Thần","巽","Tốn","石","Thạch","雷","Lôi·sấm","春秋","Xuân Thu","力","Lực","商","Thương","木","Mộc·cây","藏","Tàng","1.000"),
]
HEADS = ["Thời","Quẻ","Thiên thể","Khí hậu","Mùa / Kinh","Cai trị/Đạo","Đức/Giai cấp","Tính/Sinh vật","Pháp/Đoạn","Số"]
TC, DC = "#b8862a", "#2f5d8a"

# ── ĐỒ A: 大小四象图 ────────────────────────────────────────
colw = [86, 86, 108, 128, 124, 120, 128, 142, 118, 72]
ox, oy, rh = 40, 200, 62
W = ox + sum(colw) + 40
H = oy + 8*rh + 56
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="48" text-anchor="middle" font-size="31" fill="#2a2018" font-weight="bold">BẢNG ĐỐI ỨNG TỔNG — ĐẠI TIỂU TỨ TƯỢNG</text>')
s.append(f'<text x="{W/2}" y="80" text-anchor="middle" font-size="17" fill="#7a5a2a">大小四象图 · Hoàng Cực Kinh Thế — mọi tầng vạn vật quy về 8 đẳng</text>')
s.append(f'<text x="{W/2}" y="104" text-anchor="middle" font-size="13.5" fill="#888">Trên = TRỜI (4 đẳng · dương · động) · Dưới = ĐẤT (4 đẳng · âm · tĩnh) — đối xứng qua Thái Cực</text>')
hx = ox
for i, h in enumerate(HEADS):
    s.append(f'<text x="{hx+colw[i]/2}" y="{oy-14}" text-anchor="middle" font-size="13" fill="#444" font-weight="bold">{h}</text>')
    hx += colw[i]
s.append(f'<line x1="{ox}" y1="{oy-4}" x2="{ox+sum(colw)}" y2="{oy-4}" stroke="#c9b896" stroke-width="2"/>')

def draw_rows(rows, base_y, color, label):
    s.append(f'<text x="18" y="{base_y+4*rh/2}" font-size="15" fill="{color}" font-weight="bold" transform="rotate(-90 18 {base_y+4*rh/2})" text-anchor="middle">{label}</text>')
    for r, row in enumerate(rows):
        y = base_y + r*rh
        s.append(f'<rect x="{ox}" y="{y}" width="{sum(colw)}" height="{rh}" fill="{color}" opacity="{0.05+r*0.018:.3f}"/>')
        pairs = [(row[0],row[1]),(row[2],row[3]),(row[4],row[5]),(row[6],row[7]),(row[8],row[9]),
                 (row[10],row[11]),(row[12],row[13]),(row[14],row[15]),(row[16],row[17]),("",row[18])]
        cx = ox
        for i,(han,vi) in enumerate(pairs):
            mid = cx + colw[i]/2
            if han:
                s.append(f'<text x="{mid}" y="{y+27}" text-anchor="middle" font-size="19" fill="{color}" font-weight="bold">{esc(han)}</text>')
                s.append(f'<text x="{mid}" y="{y+46}" text-anchor="middle" font-size="11.5" fill="#444">{esc(vi)}</text>')
            else:
                s.append(f'<text x="{mid}" y="{y+37}" text-anchor="middle" font-size="15" fill="#7a5a2a" font-weight="bold">{esc(vi)}</text>')
            cx += colw[i]
        s.append(f'<line x1="{ox}" y1="{y+rh}" x2="{ox+sum(colw)}" y2="{y+rh}" stroke="#e3d9c2"/>')

draw_rows(TROI, oy, TC, "TRỜI 阳动")
draw_rows(DAT, oy+4*rh+6, DC, "ĐẤT 阴静")
s.append('</svg>')
(OUT/"dai_tieu_tu_tuong.svg").write_text("\n".join(s))

# ── ĐỒ B: 经世变化图 (Thái Cực → 2 nghi → 8 đẳng) ────────────
W2, H2 = 1060, 760
s2 = [f'<svg viewBox="0 0 {W2} {H2}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s2.append(f'<rect width="{W2}" height="{H2}" fill="#fbf7ef"/>')
s2.append(f'<text x="{W2/2}" y="46" text-anchor="middle" font-size="28" fill="#2a2018" font-weight="bold">ĐỒ SINH HÓA — KINH THẾ BIẾN HÓA</text>')
s2.append(f'<text x="{W2/2}" y="74" text-anchor="middle" font-size="15.5" fill="#7a5a2a">经世变化图 · TRỜI BIẾN tính-tình-hình-thể (暑寒昼夜) · ĐẤT HÓA tẩu-phi-thảo-mộc (雨风露雷)</text>')
midy = 400

def line(x1, y1, x2, y2, c="#c9b896", w=1.4):
    s2.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"/>')

# Thái Cực
tcx, tcy = 116, midy
s2.append(f'<circle cx="{tcx}" cy="{tcy}" r="46" fill="#fff" stroke="#2a2018" stroke-width="2.5"/>')
s2.append(f'<path d="M{tcx} {tcy-46} A23 23 0 0 1 {tcx} {tcy} A23 23 0 0 0 {tcx} {tcy+46} A46 46 0 0 0 {tcx} {tcy-46} Z" fill="#2a2018"/>')
s2.append(f'<circle cx="{tcx}" cy="{tcy-23}" r="6" fill="#fff"/><circle cx="{tcx}" cy="{tcy+23}" r="6" fill="#2a2018"/>')
s2.append(f'<text x="{tcx}" y="{tcy+72}" text-anchor="middle" font-size="15" fill="#2a2018" font-weight="bold">THÁI CỰC 太极</text>')

nyT, nyD = 230, 570
line(164, tcy, 236, nyT); line(164, tcy, 236, nyD)
for ny, han, vi, sub, col in [(nyT,"动 Dương","TRỜI","biến 变","#b8862a"), (nyD,"静 Âm","ĐẤT","hóa 化","#2f5d8a")]:
    s2.append(f'<circle cx="276" cy="{ny}" r="40" fill="{col}" opacity="0.92"/>')
    s2.append(f'<text x="276" y="{ny-3}" text-anchor="middle" font-size="15" fill="#fff" font-weight="bold">{esc(han)}</text>')
    s2.append(f'<text x="276" y="{ny+15}" text-anchor="middle" font-size="11" fill="#fff">{esc(vi)}</text>')
    s2.append(f'<text x="276" y="{ny+57}" text-anchor="middle" font-size="12.5" fill="#777">{esc(sub)}</text>')

def panel(rows, col, y0, ny, action, target_label):
    bx, bw, bh, gap = 430, 580, 64, 12
    for r, row in enumerate(rows):
        y = y0 + r*(bh+gap)
        line(316, ny, bx-6, y+bh/2)
        s2.append(f'<rect x="{bx}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="{col}" opacity="{0.09+r*0.02:.3f}" stroke="{col}" stroke-opacity="0.45"/>')
        s2.append(f'<text x="{bx+24}" y="{y+41}" font-size="27" fill="{col}" font-weight="bold">{esc(row[2])}</text>')
        s2.append(f'<text x="{bx+66}" y="{y+26}" font-size="14.5" fill="#2a2018">{esc(row[3])} ({esc(row[5])}/{esc(row[1])}) · khí {esc(row[6])} {esc(row[7].split("·")[1] if "·" in row[7] else row[7])}</text>')
        s2.append(f'<text x="{bx+66}" y="{y+48}" font-size="12.5" fill="#777">{action} {esc(row[14])} {esc(row[15])} · sinh vật {esc(row[16])}{esc(row[17].split("·")[1] if "·" in row[17] else "")}</text>')

panel(TROI, TC, 96, nyT, "biến", "tính")
panel(DAT, DC, 96 + 4*76 + 20, nyD, "hóa", "sinh vật")
s2.append('</svg>')
(OUT/"kinh_the_bien_hoa.svg").write_text("\n".join(s2))
print("✓ Vẽ xong: dai_tieu_tu_tuong.svg + kinh_the_bien_hoa.svg")
