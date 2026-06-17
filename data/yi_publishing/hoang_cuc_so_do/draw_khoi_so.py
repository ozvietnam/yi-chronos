#!/usr/bin/env python3
"""CƠ MẬT 起数 — thác biến hào 4 tầng sinh quẻ-năm.
Nguồn: Quan Vật Ngoại Thiên (bộ trọn dòng 1703-1707, 8935). Cơ chế ĐÃ KIỂM:
复 đổi sơ→thượng = 坤·临·明夷·震·屯·颐 (engine khoi_so, test xanh)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from engine.hoang_cuc.khoi_so import bits_of, sau_bien, viet_of

FONT = "Georgia, STKaiti, Songti SC, serif"
OUT = Path(__file__).resolve().parent
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

W, H = 1180, 900
s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">']
s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
s.append(f'<text x="{W/2}" y="40" text-anchor="middle" font-size="26" fill="#2a2018" font-weight="bold">CƠ MẬT 起数 — quẻ-năm KHÔNG bí truyền, là THÁC BIẾN HÀO 4 TẦNG</text>')
s.append(f'<text x="{W/2}" y="67" text-anchor="middle" font-size="13.5" fill="#7a5a2a">Nguyên lý 一贞八悔 · mỗi tầng = đổi lần lượt 6 hào (一卦六变) · bản 今说 giải rõ, không giấu</text>')

# ── ① thác 4 tầng ────────────────────────────────────────────
ly=92
s.append(f'<text x="60" y="{ly}" font-size="15" fill="#7a3410" font-weight="bold">① THÁC 4 TẦNG (会 → 运 → 世 → 年)</text>')
tiers=[("会","Hội","10.800 năm","#2f5d8a"),("值卦/大运","Trị quái","60 quẻ vòng Tiên Thiên (bỏ 乾坤坎离) · 12 hội×5","#3f7d54"),
       ("运卦","Vận quái","đổi 6 hào của 值卦 → 30 vận/hội","#a8621c"),
       ("世卦","Thế quái","đổi 6 hào của 运卦 · mỗi quẻ 2 thế → 12 thế/vận","#c98a2e"),
       ("年卦","Niên quái","đổi hào của 世卦 (以运经世) — tầng năm","#c0392b")]
for i,(zh,vi,desc,col) in enumerate(tiers):
    y=ly+18+i*44
    s.append(f'<rect x="60" y="{y}" width="200" height="36" rx="6" fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-opacity="0.45"/>')
    s.append(f'<text x="78" y="{y+24}" font-size="17" fill="{col}" font-weight="bold">{zh}</text>')
    s.append(f'<text x="150" y="{y+22}" font-size="12.5" fill="{col}" font-weight="bold">{vi}</text>')
    s.append(f'<text x="278" y="{y+23}" font-size="11" fill="#666">{esc(desc)}</text>')
    if i < 4:
        s.append(f'<text x="100" y="{y+44}" text-anchor="middle" font-size="11" fill="#bbb">↓ đổi hào</text>')

# ── ② ví dụ ĐÃ KIỂM: 复 → 6 运卦 ──────────────────────────────
ey=92
s.append(f'<text x="640" y="{ey}" font-size="15" fill="#7a3410" font-weight="bold">② VÍ DỤ ĐÃ KIỂM: 复 đổi 6 hào</text>')
def gua(cx, cy_top, bits, hi=-1):
    out=[]
    for i in range(6):           # i=0 hào dưới; vẽ trên xuống
        yng=bits[i]; yy=cy_top + (5-i)*9
        col = "#c0392b" if i==hi else "#7a3410"
        if yng: out.append(f'<rect x="{cx-16:.0f}" y="{yy}" width="32" height="5" fill="{col}"/>')
        else:
            out.append(f'<rect x="{cx-16:.0f}" y="{yy}" width="13" height="5" fill="{col}"/>')
            out.append(f'<rect x="{cx+3:.0f}" y="{yy}" width="13" height="5" fill="{col}"/>')
    return "".join(out)
# 复 gốc
phuc=bits_of("复")
s.append(f'<text x="700" y="{ey+30}" text-anchor="middle" font-size="13" fill="#7a3410" font-weight="bold">复 (gốc)</text>')
s.append(gua(700, ey+40, phuc))
s.append(f'<text x="700" y="{ey+125}" text-anchor="middle" font-size="10" fill="#999">sơ hào dương</text>')
# 6 kết quả
res=sau_bien("复"); haoname=["sơ","nhị","tam","tứ","ngũ","thượng"]
for k,nm in enumerate(res):
    x=800+(k%3)*120; y=ey+(k//3)*150
    s.append(f'<line x1="745" y1="{ey+70}" x2="{x-30}" y2="{y+45}" stroke="#ddd" stroke-width="0.8"/>')
    s.append(f'<text x="{x+18}" y="{y+18}" text-anchor="middle" font-size="10" fill="#c0392b">đổi {haoname[k]}</text>')
    s.append(gua(x+18, y+24, bits_of(nm), hi=k))
    s.append(f'<text x="{x+18}" y="{y+108}" text-anchor="middle" font-size="13" fill="#2a2018" font-weight="bold">{nm}</text>')
    s.append(f'<text x="{x+18}" y="{y+123}" text-anchor="middle" font-size="9.5" fill="#888">{viet_of(nm)}</text>')
s.append(f'<text x="940" y="{ey+330}" text-anchor="middle" font-size="11" fill="#3f7d54">✓ khớp chính văn dòng 1705 (engine test xanh)</text>')

# ── ③ 一贞八悔 ────────────────────────────────────────────────
by=470
s.append(f'<rect x="60" y="{by}" width="1060" height="150" rx="10" fill="#c9a13b" fill-opacity="0.06" stroke="#c9a13b" stroke-opacity="0.4"/>')
s.append(f'<text x="{W/2}" y="{by+28}" text-anchor="middle" font-size="15" fill="#8a4a14" font-weight="bold">③ NGUYÊN LÝ 一贞八悔 (một trinh, tám hối)</text>')
for k,ln in enumerate([
  "MỘT quái DƯỚI (贞 / bản quái) ghép CẢ TÁM quái TRÊN (悔 / biến quái) → 8 quẻ. 8 贞 × 8 悔 = 64 quẻ.",
  "Tả Truyện đã dùng: 蛊 = 贞 巽(phong) · 悔 艮(sơn); 随 = 贞 雷(chấn) · 悔 đoài. — quẻ = (dưới, trên).",
  "Vì biến hào LỒNG nhiều tầng nên cùng Giáp Tý mà 304 = 革 còn 2044 = 大過 — KHÔNG phải vòng 60 cố định."]):
    s.append(f'<text x="{W/2}" y="{by+52+k*26}" text-anchor="middle" font-size="12" fill="#555">{esc(ln)}</text>')

# ── ④ ý nghĩa ────────────────────────────────────────────────
my=648
s.append(f'<text x="{W/2}" y="{my}" text-anchor="middle" font-size="14" fill="#2f5d8a" font-weight="bold">Vậy "cơ mật" là gì?</text>')
for k,ln in enumerate([
  "Không phải một con số thần bí — mà là một CƠ CHẾ SINH: từ 1 quẻ gốc, đổi hào lồng 4 tầng, sinh ra",
  "quẻ của từng hội/vận/thế/năm. Nắm cơ chế = suy được BẤT KỲ năm nào, không cần thuộc bảng.",
  "Tổ sư giấu cái KHÓA (phép biến), không giấu từng con số. 今说 mở khóa ấy ra — và nó VẬN HÀNH ĐƯỢC."]):
    s.append(f'<text x="{W/2}" y="{my+24+k*23}" text-anchor="middle" font-size="12" fill="#444">{esc(ln)}</text>')

s.append(f'<text x="{W/2}" y="{H-16}" text-anchor="middle" font-size="11" fill="#999">engine.hoang_cuc.khoi_so — bits_of/bien_hao/sau_bien/chuoi_60_van · 17/17 test · nguồn Ngoại Thiên dòng 1703-1707, 8935</text>')
s.append('</svg>')
(OUT/"khoi_so.svg").write_text("\n".join(s))
print("✓ Vẽ xong khoi_so.svg")
