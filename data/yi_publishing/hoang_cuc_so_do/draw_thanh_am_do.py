#!/usr/bin/env python3
"""ĐỒ XƯỚNG-HỌA THANH ÂM (声音唱和图) — khung tiếng người trong lưới số.
天声 (vận, 10, ×平上去入, dương, ứng 10 thiên can; dùng 7 bỏ 3) ⊗ 地音 (thanh mẫu,
12, ×开发收闭, âm, theo 唇舌牙齿喉半). Nguồn: Ngoại Thiên (bộ trọn tr.677-680, dòng
18816/18832/18836). CHỈ phục hồi LEADERS + khung — toàn ô nằm trong ảnh gốc."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 840
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="26" fill="#2a2018" font-weight="bold">ĐỒ XƯỚNG-HỌA THANH ÂM (声音唱和图)</text>')
s.append(f'<text x="{W/2}" y="67" text-anchor="middle" font-size="14" fill="#7a5a2a">Thiệu Ung xếp MỌI TIẾNG NGƯỜI vào lưới số: vận (trời) ⊗ thanh-mẫu (đất) — "声音之道与政通"</text>')

# ── ① 天声 (trái) ────────────────────────────────────────────
hx0=70
s.append(f'<rect x="{hx0}" y="92" width="500" height="36" rx="6" fill="#c0392b" fill-opacity="0.10" stroke="#c0392b" stroke-opacity="0.4"/>')
s.append(f'<text x="{hx0+250}" y="108" text-anchor="middle" font-size="14" fill="#a8341c" font-weight="bold">① 天声 — TIẾNG TRỜI (vận / nguyên âm)</text>')
s.append(f'<text x="{hx0+250}" y="123" text-anchor="middle" font-size="11" fill="#888">10 声 × 平·上·去·入 (4 thanh) · thuộc DƯƠNG · ứng 10 thiên can</text>')
TS=[("甲","多"),("乙","良"),("丙","千"),("丁","刀"),("戊","妻"),("己","宫"),("庚","心"),("辛","〇"),("壬","〇"),("癸","〇")]
for i,(can,ld) in enumerate(TS):
    x=hx0+10+i*49; sounded = ld!="〇"
    col = "#c0392b" if sounded else "#ccc"
    s.append(f'<rect x="{x}" y="150" width="44" height="58" rx="5" fill="{col}" fill-opacity="{0.12 if sounded else 0.05}" stroke="{col}" stroke-opacity="0.5"/>')
    s.append(f'<text x="{x+22}" y="172" text-anchor="middle" font-size="10" fill="#999">{can}</text>')
    s.append(f'<text x="{x+22}" y="196" text-anchor="middle" font-size="22" fill="{"#7a3410" if sounded else "#bbb"}" font-weight="bold">{ld}</text>')
s.append(f'<text x="{hx0+250}" y="228" text-anchor="middle" font-size="11.5" fill="#777">Mỗi 声 mở ra 4 thanh 平上去入 · DÙNG 7 (đỏ) · BỎ 3 (〇 vô thanh)</text>')
s.append(f'<text x="{hx0+250}" y="245" text-anchor="middle" font-size="10.5" fill="#999">清 nhẹ: 多良千刀 · 浊 nặng: 禾光元毛 · 辟 mở: 古黑安夫 · 翕 khép: 黄父兑</text>')

# ── ② 地音 (phải) ────────────────────────────────────────────
gx0=70
s.append(f'<rect x="{gx0}" y="280" width="1040" height="36" rx="6" fill="#2f5d8a" fill-opacity="0.08" stroke="#2f5d8a" stroke-opacity="0.4"/>')
s.append(f'<text x="{gx0+520}" y="296" text-anchor="middle" font-size="14" fill="#2f5d8a" font-weight="bold">② 地音 — TIẾNG ĐẤT (thanh mẫu / phụ âm)</text>')
s.append(f'<text x="{gx0+520}" y="311" text-anchor="middle" font-size="11" fill="#888">12 音 × 开·发·收·闭 (4 phát âm) · thuộc ÂM · theo 唇·舌·牙·齿·喉·半 (chỗ phát)</text>')
DA=[("古","Cổ"),("黑","Hắc"),("安","An"),("夫","Phu"),("卜","Bốc"),("东","Đông"),("乃","Nãi"),("走","Tẩu"),("思","Tư")]
for i,(zh,vi) in enumerate(DA):
    x=gx0+30+i*112
    s.append(f'<rect x="{x}" y="334" width="96" height="56" rx="5" fill="#2f5d8a" fill-opacity="0.10" stroke="#2f5d8a" stroke-opacity="0.45"/>')
    s.append(f'<text x="{x+48}" y="364" text-anchor="middle" font-size="22" fill="#2f5d8a" font-weight="bold">{zh}</text>')
    s.append(f'<text x="{x+48}" y="382" text-anchor="middle" font-size="10.5" fill="#888">{vi}</text>')
s.append(f'<text x="{gx0+520}" y="410" text-anchor="middle" font-size="11.5" fill="#777">…12 音, một số ô vô âm (代表无音无字者) · mỗi 音 mở ra 4 phát âm 开发收闭</text>')

# ── ③ Xướng-Họa + đồng dạng ──────────────────────────────────
yy=448
s.append(f'<text x="{W/2}" y="{yy}" text-anchor="middle" font-size="15" fill="#7a3410" font-weight="bold">③ XƯỚNG-HỌA: trời ⊗ đất → mọi âm tiết → SỐ</text>')
s.append(f'<rect x="280" y="{yy+18}" width="200" height="50" rx="8" fill="#c0392b" fill-opacity="0.10" stroke="#c0392b"/>')
s.append(f'<text x="380" y="{yy+40}" text-anchor="middle" font-size="13" fill="#a8341c" font-weight="bold">天声 (dương)</text>')
s.append(f'<text x="380" y="{yy+58}" text-anchor="middle" font-size="10.5" fill="#888">10 vận × 4 thanh</text>')
s.append(f'<text x="520" y="{yy+50}" text-anchor="middle" font-size="22" fill="#666">⊗</text>')
s.append(f'<rect x="560" y="{yy+18}" width="200" height="50" rx="8" fill="#2f5d8a" fill-opacity="0.10" stroke="#2f5d8a"/>')
s.append(f'<text x="660" y="{yy+40}" text-anchor="middle" font-size="13" fill="#2f5d8a" font-weight="bold">地音 (âm)</text>')
s.append(f'<text x="660" y="{yy+58}" text-anchor="middle" font-size="10.5" fill="#888">12 thanh-mẫu × 4 phát âm</text>')
s.append(f'<text x="800" y="{yy+50}" text-anchor="middle" font-size="22" fill="#666">→</text>')
s.append(f'<rect x="830" y="{yy+18}" width="240" height="50" rx="8" fill="#3f7d54" fill-opacity="0.10" stroke="#3f7d54"/>')
s.append(f'<text x="950" y="{yy+40}" text-anchor="middle" font-size="12.5" fill="#2f6d44" font-weight="bold">mọi tiếng người = SỐ</text>')
s.append(f'<text x="950" y="{yy+58}" text-anchor="middle" font-size="10" fill="#888">dụng 112 × 152 = 17.024 → … (Ch.6)</text>')

# đồng dạng box
s.append(f'<rect x="180" y="{yy+92}" width="820" height="120" rx="10" fill="#c9a13b" fill-opacity="0.06" stroke="#c9a13b" stroke-opacity="0.4"/>')
s.append(f'<text x="{W/2}" y="{yy+118}" text-anchor="middle" font-size="14" fill="#8a4a14" font-weight="bold">ĐỒNG DẠNG: tiếng ↔ ánh sáng ↔ số</text>')
for k,ln in enumerate([
  "天声 có 10 nhưng DÙNG 7 — vì hạ chí mặt trời HIỆN 7 giờ (寅→戌), còn 亥·子·丑 ba giờ mặt trời LẶN (vô sáng).",
  "Ba 声 vô thanh (〇〇〇) = ba giờ vô sáng. Số tiếng KHỚP số giờ — không phải trùng hợp, mà cùng MỘT lưới.",
  "Đây là cốt Hoàng Cực: ngôn ngữ, thời gian, ánh sáng — đọc bằng cùng một bộ số. Đọc cấu trúc, không bói."]):
    s.append(f'<text x="{W/2}" y="{yy+140+k*22}" text-anchor="middle" font-size="11.5" fill="#555">{esc(ln)}</text>')

s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="11" fill="#999">Nguồn: Quan Vật Ngoại Thiên (bộ trọn tr.677-680) · CHỈ phục hồi leaders + khung; toàn ô (mỗi cell một chữ) nằm trong ảnh gốc = bước sau</text>')
s.append('</svg>')
(OUT/"thanh_am_do.svg").write_text("\n".join(s))
print("✓ Vẽ xong thanh_am_do.svg")
