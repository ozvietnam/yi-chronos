"""Render đại tổng hợp lá số → SVG đồ hình (poster) — founder học bằng hình.

Lấy dict từ dai_tong_hop.dai_tong_hop() + arc tu-dưỡng (narrative 40 vòng) → SVG poster
dùng được trên web (nhúng) lẫn PDF (Bookflow Iron #5). Iron #4/#6: disclaimer đọc-TÍNH ở chân.
"""
from __future__ import annotations

from html import escape

# Arc tu-dưỡng 8 đường — narrative kết tinh 40 vòng (Đằng Sơn T2), mỗi đường 1 nguồn.
ARC_TU_DUONG = [
    ("Thiên Tướng cận-đạo", "V20 · T1 Ch.23 · kém tranh quyền thế tục, bù lại dễ gần tu hành/giác ngộ"),
    ("Cụm cửa-tu tại Mệnh", "V30 · T2 Ch.14 · Thiên Tướng + Thiên Không + Thiếu Dương đồng tọa"),
    ("Cô Thần = đạo hạnh", "V32 · T2 tr.198 · 'bậc chân tu thì Cô Quả lại cốt chính là đạo hạnh'"),
    ("Tuổi Tứ Mộ tu-dưỡng", "V33 · T2 tr.223 · 4 sao duyên-nghiệp chế-hóa tại 1 góc = dễ tu tâm dưỡng tính"),
    ("Ma quân là bạn đạo", "V34 · T2 tr.241 · sát tinh = nhiên liệu tu-dưỡng, chuyển nghịch-cảnh thành đạo"),
    ("Mệnh tại Tuyệt", "V35 · T2 tr.267 · tuyệt-xứ-phùng-sinh, 'cùng tắc biến: tướng chết tìm sinh lộ'"),
    ("Tu-dưỡng vượt sát", "V36 · T2 tr.290 · lá thoát Không Kiếp Hình = 'người có nỗ lực tu tâm dưỡng tánh'"),
    ("Tuần Triệt = công cụ tu", "V38 · T2 tr.322 · 'cảnh tu hành Tuần và Triệt lại là công cụ sắc bén giúp ta'"),
]

# Palette (poster — không theo --read-* vì còn render PDF)
_BG = "#fbf7ef"
_INK = "#2b2117"
_GOLD = "#9a6b27"
_GOLD_SOFT = "#e7d4ad"
_JADE = "#2e6b54"
_AMBER = "#a86a1d"
_LINE = "#d9c9a8"
_PAPER = "#fffdf8"


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _text(x, y, s, size=13, fill=_INK, weight="400", anchor="start", spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{sp}>{escape(s)}</text>')


def _card(x, y, w, h, fill=_PAPER, stroke=_LINE, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')


def to_svg(syn: dict, arc=ARC_TU_DUONG, *, person="Founder (Mậu Thìn · 1988-06-05 23:30, giờ Tý)") -> str:
    W, H = 920, 1030
    co = syn["co"]
    tdh = syn["the_dung_hau_thien"]
    cua = syn["cua_tu"]
    tm = syn["tu_mo_tu_duong"]
    tt = syn["tuan_triet"]
    cb = syn["can_bang"]
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia, \'Times New Roman\', serif">')
    s.append(f'<rect width="{W}" height="{H}" fill="{_BG}"/>')
    s.append(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" rx="16" fill="none" stroke="{_GOLD_SOFT}" stroke-width="2"/>')

    # Header
    s.append(_text(W/2, 64, "ĐẠI TỔNG HỢP LÁ SỐ", 30, _GOLD, "700", "middle", "2"))
    s.append(_text(W/2, 92, "kết tinh 40 vòng đọc sâu — Tử Vi Hoàn Toàn Khoa Học · Đằng Sơn", 14, _INK, "400", "middle"))
    s.append(_text(W/2, 114, person, 12.5, _GOLD, "italic" and "400", "middle"))
    s.append(f'<line x1="60" y1="132" x2="{W-60}" y2="132" stroke="{_LINE}" stroke-width="1"/>')

    y = 158
    # ── CƠ snapshot ──
    s.append(_card(40, y, W-80, 76))
    s.append(_text(58, y+26, "CƠ — snapshot", 12, _GOLD, "700", "start", "1.5"))
    snap = (f"Mệnh {co['menh_branch']}  ·  {co['cuc_name']}  ·  Mệnh tại giai đoạn "
            f"{co['menh_truong_sinh_stage']} (tuyệt-xứ-phùng-sinh)")
    s.append(_text(58, y+50, snap, 15, _INK, "700"))
    s.append(_text(58, y+68, "Sao tại Mệnh: " + ", ".join(co["menh_stars"][:9]), 11.5, "#6b5d49"))
    y += 96

    # ── THỂ–DỤNG–HẬU THIÊN ──
    s.append(_text(58, y+8, "THỂ – DỤNG – HẬU THIÊN  ·  \"tướng quân cầm bút dựng nhà xuất bản đạo học\"", 13, _GOLD, "700"))
    y += 22
    cols = [
        ("THỂ (tiên thiên)", tdh["the"]["sao"], tdh["the"]["vai"], _GOLD),
        ("DỤNG (diện mạo)", ", ".join(tdh["dung"]["sao"]) or "—", tdh["dung"]["vai"], _JADE),
        ("HẬU THIÊN (hướng)", tdh["hau_thien"]["sao"], tdh["hau_thien"]["vai"], _AMBER),
    ]
    cw, gap = (W-80-2*16)/3, 16
    for i, (lab, sao, vai, col) in enumerate(cols):
        cx = 40 + i*(cw+gap)
        s.append(_card(cx, y, cw, 92, _PAPER, col, 10))
        s.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="5" rx="2" fill="{col}"/>')
        s.append(_text(cx+cw/2, y+28, lab, 10.5, col, "700", "middle", "0.5"))
        s.append(_text(cx+cw/2, y+54, sao, 18, _INK, "700", "middle"))
        for j, ln in enumerate(_wrap(vai, 30)):
            s.append(_text(cx+cw/2, y+72+j*14, ln, 10.5, "#6b5d49", "400", "middle"))
    y += 112

    # ── ARC TU-DƯỠNG (8 đường) ──
    s.append(_card(40, y, W-80, 26+len(arc)*30+8, "#fbfaf4", _GOLD_SOFT))
    s.append(_text(58, y+24, f"ARC TU-DƯỠNG — {len(arc)} đường độc lập hội tụ → cấu trúc Mệnh = LÒ TU-DƯỠNG", 13, _GOLD, "700"))
    yy = y + 46
    for i, (name, src) in enumerate(arc):
        s.append(f'<circle cx="64" cy="{yy-4}" r="9" fill="{_GOLD}"/>')
        s.append(_text(64, yy-0.5, str(i+1), 11, "#fff", "700", "middle"))
        s.append(_text(84, yy, name, 13.5, _INK, "700"))
        s.append(_text(290, yy, src, 11, "#6b5d49"))
        yy += 30
    y += 26+len(arc)*30+8 + 18

    # ── 2 chip: tứ mộ + tuần triệt ──
    chip_h = 56
    cw2 = (W-80-16)/2
    s.append(_card(40, y, cw2, chip_h, _PAPER, _JADE))
    s.append(_text(56, y+22, "TỨ MỘ TU-DƯỠNG", 11, _JADE, "700", "start", "0.5"))
    tm_txt = (f"góc {tm['corner']} — 4 sao duyên-nghiệp chế-hóa" if tm["cua_khong_colocated_corner"]
              else "không ứng")
    s.append(_text(56, y+42, ("Có · " if tm["cua_khong_colocated_corner"] else "— ") + tm_txt, 13, _INK, "400"))
    s.append(_card(40+cw2+16, y, cw2, chip_h, _PAPER, _JADE))
    s.append(_text(56+cw2+16, y+22, "TUẦN / TRIỆT", 11, _JADE, "700", "start", "0.5"))
    s.append(_text(56+cw2+16, y+42, ("Có · Mệnh THÔNG" if tt["menh_thong"] else "Mệnh bị án") +
                   " — đắc Thiên Tướng giữ nguyên", 13, _INK, "400"))
    y += chip_h + 22

    # ── CÂN BẰNG (sáng | xấu-nhẹ) ──
    s.append(_text(58, y, "CÂN BẰNG TRUNG THỰC — không tô hồng", 13, _GOLD, "700"))
    y += 12
    colw = (W-80-16)/2
    sang, xau = cb["sang"], cb["xau_nhe"]
    rows = max(len(sang), len(xau))
    box_h = 34 + rows*30
    s.append(_card(40, y, colw, box_h, "#f2f7f3", _JADE))
    s.append(_text(58, y+24, "SÁNG", 12, _JADE, "700"))
    for i, t in enumerate(sang):
        for j, ln in enumerate(_wrap(t, 42)):
            s.append(_text(58, y+46+i*30+j*13, ("·  " if j == 0 else "   ") + ln, 11, _INK))
    s.append(_card(40+colw+16, y, colw, box_h, "#fbf3e9", _AMBER))
    s.append(_text(58+colw+16, y+24, "XẤU-NHẸ (đọc nhịp, không phán hung)", 11.5, _AMBER, "700"))
    for i, t in enumerate(xau):
        for j, ln in enumerate(_wrap(t, 42)):
            s.append(_text(58+colw+16, y+46+i*30+j*13, ("·  " if j == 0 else "   ") + ln, 11, _INK))
    y += box_h + 22

    # ── Disclaimer footer ──
    s.append(_card(40, y, W-80, 70, "#2b2117", "#2b2117"))
    for j, ln in enumerate(_wrap(syn["disclaimer"], 92)):
        s.append(_text(58, y+26+j*16, ln, 11.5, "#e7d4ad" if j == 0 else "#cbb88f", "400"))
    s.append('</svg>')
    return "\n".join(s)
