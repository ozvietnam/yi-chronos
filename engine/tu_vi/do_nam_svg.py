"""ĐỒ NĂM — lá số lưu niên SVG (3 lớp: mùa của thời + Đại Vận + Lưu Niên tứ hóa).

do_nam_svg(birth, gender, year) → SVG 12 cung + tứ hóa năm rọi lên cung của người đó
+ header 3 lớp (Hoàng Cực năm-quẻ · Đại Vận · Lưu Niên). Paradigm đọc-đồng-dạng:
đọc CẤU TRÚC của năm để HÀNH cho thuận, KHÔNG phán việc (Iron Rule #4/#6/#8).
SVG chạy thẳng trên trình duyệt (sao tiếng Việt; CJK năm-quẻ qua font hệ thống).
"""
from __future__ import annotations

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

# Tứ hóa theo CAN năm (Bắc phái chuẩn): (Lộc, Quyền, Khoa, Kỵ) — tên sao tiếng Việt
TU_HOA = {
    "Giáp": ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),
    "Ất":   ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
    "Bính": ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"),
    "Đinh": ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
    "Mậu":  ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),
    "Kỷ":   ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
    "Canh": ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),
    "Tân":  ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
    "Nhâm": ("Thiên Lương", "Tử Vi", "Tả Phụ", "Vũ Khúc"),
    "Quý":  ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),
}
HOA_LABEL = ["Lộc", "Quyền", "Khoa", "Kỵ"]
HOA_COLOR = {"Lộc": "#2f8a4a", "Quyền": "#2f5d8a", "Khoa": "#8a6a1a", "Kỵ": "#c0392b"}
# vị trí cung trên lưới 4×4 (chuẩn Tử Vi: 巳午未申 trên, 寅丑子亥 dưới)
POS = {"Tỵ": (0, 0), "Ngọ": (0, 1), "Mùi": (0, 2), "Thân": (0, 3),
       "Thìn": (1, 0), "Dậu": (1, 3), "Mão": (2, 0), "Tuất": (2, 3),
       "Dần": (3, 0), "Sửu": (3, 1), "Tý": (3, 2), "Hợi": (3, 3)}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def do_nam_svg(birth: str, gender: str, year: int) -> str:
    from engine.tu_vi.analyzer import _cast_chart
    from engine.hoang_cuc.khoi_so import year_que_method

    ls = _cast_chart(birth, gender)
    sb = {}                                  # sao → chi
    for s, b in ls["chinh_tinh"].items():
        sb[s] = CHI[b]
    for s, b in (ls.get("phu_tinh") or {}).items():
        sb[s] = CHI[b] if isinstance(b, int) else b
    pal = {p["branch"]: p["name"] for p in ls["palaces"]}
    ct_b = {}
    for s, b in ls["chinh_tinh"].items():
        ct_b.setdefault(CHI[b], []).append(s)

    can = CAN[(year - 4) % 10]
    chi_nam = CHI[(year - 4) % 12]
    hoa_at = {}                              # chi → [(label, star)]
    for lab, star in zip(HOA_LABEL, TU_HOA[can]):
        b = sb.get(star)
        if b:
            hoa_at.setdefault(b, []).append((lab, star))

    nq = year_que_method(year)
    birth_year = int(str(birth)[:4]); age = year - birth_year + 1
    dv = next((d for d in ls["dai_van"] if d["start_age"] <= age <= d["end_age"]), None)
    dv_branch = dv["branch"] if dv else None
    menh_branch = ls.get("menh_branch") or CHI[ls["menh_index"]]

    FONT = "'Songti SC','STSong','PingFang SC','Times New Roman',serif"
    W, H = 980, 760
    mx, my = 20, 96
    cw, ch = (W - 2 * mx) / 4, (H - my - 20) / 4
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">']
    s.append(f'<rect width="{W}" height="{H}" fill="#fbf7ef"/>')
    s.append(f'<text x="{W/2}" y="34" text-anchor="middle" font-size="22" fill="#2a2018" font-weight="bold">ĐỒ {year} — {can} {chi_nam} · lá số lưu niên</text>')
    s.append(f'<text x="{W/2}" y="58" text-anchor="middle" font-size="12.5" fill="#7a5a2a">Mùa của thời: năm-quẻ {_esc(nq["han"])} {_esc(nq["viet"])} (thế {_esc(nq["the_que"])}) · Đại Vận: cung {_esc(pal.get(dv_branch,"?"))} ({_esc(dv_branch)}) · Lưu Niên: tứ hóa {can}</text>')
    s.append(f'<text x="{W/2}" y="76" text-anchor="middle" font-size="11" fill="#999">đọc cấu trúc của năm để HÀNH cho thuận — không phán việc (Lộc xanh · Quyền lam · Khoa vàng · Kỵ đỏ)</text>')

    for b, (r, c) in POS.items():
        x, y = mx + c * cw, my + r * ch
        is_menh = b == menh_branch
        is_dv = b == dv_branch
        is_ln = b == chi_nam
        fill = "#fbe9e7" if is_menh else ("#fdf3d8" if is_dv else "#fff")
        s.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{cw-3:.0f}" height="{ch-3:.0f}" fill="{fill}" stroke="#d8be86" stroke-width="1"/>')
        if is_ln:
            s.append(f'<rect x="{x+1:.0f}" y="{y+1:.0f}" width="{cw-5:.0f}" height="{ch-5:.0f}" fill="none" stroke="#2f5d8a" stroke-width="2" stroke-dasharray="4 3"/>')
        # chính tinh (giữa)
        stars = ct_b.get(b, [])
        sy = y + 30
        if stars:
            for st in stars:
                s.append(f'<text x="{x+cw/2-1:.0f}" y="{sy:.0f}" text-anchor="middle" font-size="14" fill="#5a2d0c" font-weight="bold">{_esc(st)}</text>')
                sy += 18
        else:
            s.append(f'<text x="{x+cw/2-1:.0f}" y="{sy:.0f}" text-anchor="middle" font-size="11" fill="#bbb">(vô chính tinh)</text>')
        # tứ hóa năm (badges)
        by = y + ch - 8
        for lab, star in reversed(hoa_at.get(b, [])):
            col = HOA_COLOR[lab]
            s.append(f'<text x="{x+8:.0f}" y="{by:.0f}" font-size="11.5" fill="{col}" font-weight="bold">▸ {lab} {_esc(star)}</text>')
            by -= 16
        # cung chức năng (góc dưới phải) + chi (góc trên phải)
        s.append(f'<text x="{x+cw-8:.0f}" y="{y+16:.0f}" text-anchor="end" font-size="10.5" fill="#999">{_esc(b)}</text>')
        nm = pal.get(b, "")
        nmcol = "#c0392b" if is_menh else "#8a4a14"
        tag = " ★Mệnh" if is_menh else (" ◆ĐV" if is_dv else (" ○LN" if is_ln else ""))
        s.append(f'<text x="{x+8:.0f}" y="{y+16:.0f}" font-size="11" fill="{nmcol}" font-weight="bold">{_esc(nm)}{tag}</text>')

    # tâm: 2×2 giữa
    ix, iy = mx + cw, my + ch
    iw, ih = cw * 2, ch * 2
    s.append(f'<rect x="{ix:.0f}" y="{iy:.0f}" width="{iw-3:.0f}" height="{ih-3:.0f}" fill="#2f5d8a" fill-opacity="0.05" stroke="#c9a13b"/>')
    s.append(f'<text x="{ix+iw/2:.0f}" y="{iy+34:.0f}" text-anchor="middle" font-size="17" fill="#7a3410" font-weight="bold">Năm {year} · {age} tuổi (ta)</text>')
    lines = [
        f'Mệnh: {pal.get(menh_branch)} ({menh_branch})',
        f'Đại Vận {age}t: cung {pal.get(dv_branch,"?")}',
        f'Lưu Niên Mệnh: {pal.get(chi_nam,"?")} ({chi_nam})',
        "",
        "Tứ hóa năm rọi vào:",
    ]
    for lab, star in zip(HOA_LABEL, TU_HOA[can]):
        b = sb.get(star, "?")
        lines.append(f'  {lab} {star} → {pal.get(b, b)}')
    yy = iy + 64
    for ln in lines:
        col = "#444"
        for lab in HOA_LABEL:
            if ln.strip().startswith(lab + " "):
                col = HOA_COLOR[lab]
        s.append(f'<text x="{ix+22:.0f}" y="{yy:.0f}" font-size="12.5" fill="{col}">{_esc(ln)}</text>')
        yy += 21
    s.append(f'<text x="{ix+iw/2:.0f}" y="{iy+ih-14:.0f}" text-anchor="middle" font-size="10.5" fill="#999">★Mệnh · ◆Đại Vận · ○Lưu Niên Mệnh</text>')
    s.append('</svg>')
    return "\n".join(s)
