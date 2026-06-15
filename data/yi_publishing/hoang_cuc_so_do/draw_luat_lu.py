#!/usr/bin/env python3
"""LUẬT-LỮ THANH ÂM — nửa 'TIẾNG' của vũ trụ (song song nửa 'THỜI').
Số liệu chính văn Quan Vật Nội Thiên 11 (tr.229-234): thể số 160/192, dụng số
112/152 (tiến 4 thoái 1), xướng-họa 112×152=17.024, thông số 17.024²=289.816.576."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 880
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="27" fill="#2a2018" font-weight="bold">LUẬT-LỮ THANH ÂM — nửa "TIẾNG" của vũ trụ</text>')
s.append(f'<text x="{W/2}" y="68" text-anchor="middle" font-size="14" fill="#7a5a2a">律吕声音 · "Lịch ghi trời-đất, Luật ghi vạn vật; vật có sắc-thanh-khí-vị, mà THANH thịnh nhất" (Nội Thiên 11)</text>')

# ── ① hai cột: LỊCH | LUẬT ───────────────────────────────────
y1=92
s.append(f'<text x="{W/2}" y="{y1+18}" text-anchor="middle" font-size="15" fill="#2f5d8a" font-weight="bold">① MỘT vũ trụ, HAI cách đọc — "đồng dạng"</text>')
for i,(zh,vi,desc,col,cx) in enumerate([
    ("历","LỊCH (thời)","元会运世 · Nguyên-Hội-Vận-Thế · Chương 1-5","#2f5d8a",330),
    ("律","LUẬT (tiếng)","声音唱和 · thanh âm · chương này","#a8621c",850)]):
    s.append(f'<rect x="{cx-230}" y="{y1+30}" width="460" height="58" rx="8" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-opacity="0.45"/>')
    s.append(f'<text x="{cx-195}" y="{y1+68}" font-size="30" fill="{col}" font-weight="bold">{zh}</text>')
    s.append(f'<text x="{cx-150}" y="{y1+57}" font-size="16" fill="{col}" font-weight="bold">{esc(vi)}</text>')
    s.append(f'<text x="{cx-150}" y="{y1+77}" font-size="11.5" fill="#777">{esc(desc)}</text>')
s.append(f'<text x="{W/2}" y="{y1+62}" text-anchor="middle" font-size="20" fill="#999">↔</text>')

# ── ② 8 âm = trời 4 + đất 4 ──────────────────────────────────
y2=200
s.append(f'<text x="{W/2}" y="{y2+10}" text-anchor="middle" font-size="15" fill="#3f7d54" font-weight="bold">② TÁM ÂM = Trời 4 + Đất 4 (chính là 8 đẳng Chương 1) — mỗi âm mang số 10 (dương/cương) hoặc 12 (âm/nhu)</text>')
TROI=[("日","Nhật","太阳",10,"#c98a2e"),("月","Nguyệt","太阴",12,"#3f5d8a"),
      ("星","Tinh","少阳",10,"#c98a2e"),("辰","Thần","少阴",12,"#3f5d8a")]
DAT =[("火","Hỏa","太刚",10,"#a85a3a"),("水","Thủy","太柔",12,"#2f7d8a"),
      ("石","Thạch","少刚",10,"#a85a3a"),("土","Thổ","少柔",12,"#5a7d4a")]
def draw_row(items, y, label):
    s.append(f'<text x="70" y="{y+26}" font-size="13" fill="#555" font-weight="bold">{label}</text>')
    for i,(zh,vi,tt,num,col) in enumerate(items):
        x=190+i*230
        s.append(f'<rect x="{x}" y="{y}" width="200" height="46" rx="6" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.5"/>')
        s.append(f'<text x="{x+16}" y="{y+32}" font-size="24" fill="{col}" font-weight="bold">{zh}</text>')
        s.append(f'<text x="{x+52}" y="{y+20}" font-size="13" fill="#3a2e20" font-weight="bold">{esc(vi)} · {esc(tt)}</text>')
        s.append(f'<text x="{x+52}" y="{y+38}" font-size="12" fill="#777">số {num}</text>')
draw_row(TROI, y2+22, "TRỜI")
draw_row(DAT,  y2+78, "ĐẤT")
s.append(f'<text x="{W/2}" y="{y2+150}" text-anchor="middle" font-size="11" fill="#999">Quẻ ↔ hành đổi theo ngữ cảnh (变象) — sách dặn "đừng kẹt vào tên": cấu trúc 8 là thật, nhãn thì linh hoạt</text>')

# ── ③ thể số → dụng số (tiến 4 thoái 1) ─────────────────────
y3=410
s.append(f'<text x="{W/2}" y="{y3}" text-anchor="middle" font-size="15" fill="#8a4a14" font-weight="bold">③ THỂ SỐ → DỤNG SỐ (tiến 4 thoái 1: lấy 4 lần, trừ đi "thể" của bên kia)</text>')
rows=[("DƯƠNG / CƯƠNG","日星 · 火石 (4 cái ×10)","4×40 = 160","− 48 (thể âm nhu)","112","#a8621c",y3+24),
      ("ÂM / NHU","月辰 · 水土 (4 cái ×12)","4×48 = 192","− 40 (thể dương cương)","152","#2f5d8a",y3+92)]
for lab,base,the,minus,dung,col,yy in rows:
    s.append(f'<text x="90" y="{yy+28}" font-size="13.5" fill="{col}" font-weight="bold">{esc(lab)}</text>')
    s.append(f'<text x="90" y="{yy+46}" font-size="10.5" fill="#888">{esc(base)}</text>')
    s.append(f'<rect x="320" y="{yy+8}" width="150" height="40" rx="6" fill="#eee" stroke="#ccc"/>')
    s.append(f'<text x="395" y="{yy+26}" text-anchor="middle" font-size="12" fill="#666">thể số</text>')
    s.append(f'<text x="395" y="{yy+42}" text-anchor="middle" font-size="15" fill="#333" font-weight="bold">{esc(the)}</text>')
    s.append(f'<text x="575" y="{yy+34}" text-anchor="middle" font-size="13" fill="#a85a3a">{esc(minus)} →</text>')
    s.append(f'<rect x="690" y="{yy+8}" width="120" height="40" rx="6" fill="{col}" fill-opacity="0.14" stroke="{col}"/>')
    s.append(f'<text x="750" y="{yy+26}" text-anchor="middle" font-size="12" fill="{col}">dụng số</text>')
    s.append(f'<text x="750" y="{yy+42}" text-anchor="middle" font-size="17" fill="{col}" font-weight="bold">{dung}</text>')

# ── ④ xướng-họa → số vạn vật ─────────────────────────────────
y4=600
s.append(f'<text x="{W/2}" y="{y4}" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">④ XƯỚNG-HỌA (nhân chéo) → SỐ VẠN VẬT</text>')
# 112 × 152
s.append(f'<rect x="380" y="{y4+22}" width="100" height="44" rx="6" fill="#a8621c" fill-opacity="0.14" stroke="#a8621c"/>')
s.append(f'<text x="430" y="{y4+50}" text-anchor="middle" font-size="20" fill="#a8621c" font-weight="bold">112</text>')
s.append(f'<text x="510" y="{y4+50}" text-anchor="middle" font-size="20" fill="#666">×</text>')
s.append(f'<rect x="540" y="{y4+22}" width="100" height="44" rx="6" fill="#2f5d8a" fill-opacity="0.14" stroke="#2f5d8a"/>')
s.append(f'<text x="590" y="{y4+50}" text-anchor="middle" font-size="20" fill="#2f5d8a" font-weight="bold">152</text>')
s.append(f'<text x="690" y="{y4+50}" text-anchor="middle" font-size="20" fill="#666">=</text>')
s.append(f'<rect x="720" y="{y4+22}" width="150" height="44" rx="6" fill="#3f7d54" fill-opacity="0.16" stroke="#3f7d54"/>')
s.append(f'<text x="795" y="{y4+50}" text-anchor="middle" font-size="20" fill="#2f6d44" font-weight="bold">17.024</text>')
s.append(f'<text x="940" y="{y4+44}" font-size="12" fill="#777">động số = thực số</text>')
s.append(f'<text x="940" y="{y4+60}" font-size="11" fill="#999">(日月星辰 biến · 水火土石 hóa)</text>')
# 17024² = 289,816,576
s.append(f'<line x1="{W/2}" y1="{y4+70}" x2="{W/2}" y2="{y4+92}" stroke="#bbb"/>')
s.append(f'<rect x="320" y="{y4+94}" width="540" height="58" rx="9" fill="#7a3410" fill-opacity="0.07" stroke="#7a3410" stroke-opacity="0.4"/>')
s.append(f'<text x="{W/2}" y="{y4+118}" text-anchor="middle" font-size="15" fill="#7a3410">17.024 × 17.024 =</text>')
s.append(f'<text x="{W/2}" y="{y4+144}" text-anchor="middle" font-size="24" fill="#7a3410" font-weight="bold">289.816.576</text>')
s.append(f'<text x="{W/2}" y="{y4+172}" text-anchor="middle" font-size="13" fill="#8a4a14" font-weight="bold">ĐỘNG-THỰC THÔNG SỐ — con số "vạn vật" của Thiệu Ung</text>')

s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="11" fill="#999">Nguồn: Quan Vật Nội Thiên 11, tr.229-234 (Thiệu Bá Ôn · Hoàng thị · Vương thị · Chúc thị) · Bảng 声音唱和图 chi tiết (chữ nào ứng đâu) = bước sau</text>')
s.append('</svg>')
(OUT/"luat_lu_thanh_am.svg").write_text("\n".join(s))
print("✓ Vẽ xong luat_lu_thanh_am.svg")
