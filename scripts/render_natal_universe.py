#!/usr/bin/env python3
"""Nguyên mẫu: VẼ LÁ SỐ TRÊN NỀN VŨ TRỤ THẬT.

Hai vòng đồng tâm, nối bằng Mặt Trời:
  - VÒNG NGOÀI = bầu trời THẬT lúc sinh: 12 cung hoàng đạo Tây + 10 thiên thể
    (vị trí hoàng đạo thật từ skyfield/DE440s).
  - VÒNG TRONG = ĐỊA BÀN Tử Vi (KÝ HIỆU): 12 địa chi neo vào TIẾT KHÍ (中氣 =
    vị trí THẬT của Mặt Trời), cung Mệnh tô đậm. Sao Tử Vi KHÔNG phải sao thật.
  - CẦU NỐI = Mặt Trời: vị trí thật của nó (hoàng đạo) chính là cái neo địa bàn.

Tôn trọng Iron #4/#6 (giả tướng — đọc đồng dạng, không predict): nền thật + lớp
ký hiệu suy ra TỪ nền thật, KHÔNG rắc sao Tử Vi lên trời thật.

    python3 scripts/render_natal_universe.py [out.svg]
"""
from __future__ import annotations

import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.sky import calculate_sky_chart

# ---- Đầu vào (mặc định: lá số founder) ----
BIRTH_LOCAL = datetime(1988, 6, 5, 23, 30, tzinfo=timezone(timedelta(hours=7)))
LAT, LON = 21.03, 105.85  # Hà Nội
LUNAR_MONTH = 4           # âm lịch (sxtwl)
HOUR_IDX = 0              # giờ Tý = 0
YEAR_CANCHI = "Mậu Thìn"

CX, CY = 340.0, 360.0
R_ZOD_OUT, R_ZOD_IN = 268.0, 232.0
R_PLANET = 196.0
R_DIA_OUT, R_DIA_IN = 150.0, 96.0
R_EARTH = 30.0

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
# tâm 中氣 (độ hoàng đạo) cho từng chi
CHI_LON = {"Mão": 0, "Thìn": 30, "Tỵ": 60, "Ngọ": 90, "Mùi": 120, "Thân": 150,
           "Dậu": 180, "Tuất": 210, "Hợi": 240, "Tý": 270, "Sửu": 300, "Dần": 330}
CHI_HANH = {"Tý": "thuy", "Hợi": "thuy", "Dần": "moc", "Mão": "moc", "Tỵ": "hoa",
            "Ngọ": "hoa", "Thân": "kim", "Dậu": "kim",
            "Thìn": "tho", "Tuất": "tho", "Sửu": "tho", "Mùi": "tho"}
HANH_COLOR = {"thuy": "#2563a8", "moc": "#3f8a3f", "hoa": "#c0392b", "tho": "#b8860b", "kim": "#6b7280"}

ZODIAC = ["Bạch Dương", "Kim Ngưu", "Song Tử", "Cự Giải", "Sư Tử", "Xử Nữ",
          "Thiên Bình", "Hổ Cáp", "Nhân Mã", "Ma Kết", "Bảo Bình", "Song Ngư"]
ZOD_ELEM = ["fire", "earth", "air", "water"] * 3
ELEM_TINT = {"fire": "#f6e7e3", "earth": "#e9efe6", "air": "#f3eedd", "water": "#e4edf3"}

# Tên Việt thuần (glyph chiêm tinh ☉☽ font serif không có → hiện ô vuông)
PLANET_VI = {"sun": "Nhật", "moon": "Nguyệt", "mercury": "Thủy", "venus": "Kim",
             "mars": "Hỏa", "jupiter": "Mộc", "saturn": "Thổ", "uranus": "Thiên",
             "neptune": "Hải", "pluto": "Diêm"}


def polar(theta_deg: float, r: float) -> tuple[float, float]:
    """Hoàng đạo θ (0=Bạch Dương, ngược kim đồng hồ) → toạ độ SVG (y hướng xuống)."""
    a = math.radians(theta_deg)
    return CX + r * math.cos(a), CY - r * math.sin(a)


def menh_chi() -> str:
    idx = (1 + LUNAR_MONTH - HOUR_IDX) % 12  # Tý=0..Hợi=11
    return CHI[idx]


def build_svg() -> str:
    utc = BIRTH_LOCAL.astimezone(timezone.utc)
    chart = calculate_sky_chart(dt_utc=utc, lat=LAT, lon=LON)
    bodies = {b.name: b for b in chart.bodies}
    menh = menh_chi()
    sun_lon = bodies["sun"].ecliptic_longitude

    P: list[str] = []
    P.append(f'<svg width="100%" viewBox="0 0 680 760" role="img" xmlns="http://www.w3.org/2000/svg">')
    P.append('<title>Lá số trên nền vũ trụ thật — nguyên mẫu</title>')
    P.append('<desc>Hai vòng đồng tâm quanh Trái Đất: vòng ngoài là bầu trời thật lúc sinh '
             '(12 cung hoàng đạo Tây + 10 thiên thể ở vị trí thật), vòng trong là địa bàn Tử Vi '
             '(12 địa chi ký hiệu, neo vào vị trí thật của Mặt Trời), cung Mệnh tô đậm.</desc>')
    P.append('<style>text{font-family:Georgia,"Times New Roman",serif}'
             '.z{font-size:11px;fill:#6a6356}.zd{font-size:8px;fill:#9a917c}'
             '.chi{font-size:14px;font-weight:700}.pl{font-size:10.5px;font-weight:600}'
             '.pld{font-size:8px;fill:#8a8273}.ttl{font-size:18px;font-weight:700;fill:#8a5a00}'
             '.sub{font-size:11.5px;fill:#5a5446}.note{font-size:10px;fill:#6a6356}'
             '.lg{font-size:11px;fill:#5a5446}</style>')
    P.append(f'<text class="ttl" x="{CX}" y="30" text-anchor="middle">LÁ SỐ TRÊN NỀN VŨ TRỤ THẬT</text>')
    P.append(f'<text class="sub" x="{CX}" y="49" text-anchor="middle">'
             f'{BIRTH_LOCAL.strftime("%d/%m/%Y %H:%M")} (+07) · {YEAR_CANCHI} · Mệnh tại {menh}</text>')

    # ---- VÒNG NGOÀI: 12 cung hoàng đạo Tây (bầu trời thật) ----
    for i in range(12):
        a0, a1 = i * 30, (i + 1) * 30
        x0o, y0o = polar(a0, R_ZOD_OUT)
        x0i, y0i = polar(a0, R_ZOD_IN)
        # nan quạt nền nhạt theo nguyên tố
        large = 0
        xa, ya = polar(a0, R_ZOD_OUT)
        xb, yb = polar(a1, R_ZOD_OUT)
        xc, yc = polar(a1, R_ZOD_IN)
        xd, yd = polar(a0, R_ZOD_IN)
        P.append(f'<path d="M{xa:.1f},{ya:.1f} A{R_ZOD_OUT},{R_ZOD_OUT} 0 0 0 {xb:.1f},{yb:.1f} '
                 f'L{xc:.1f},{yc:.1f} A{R_ZOD_IN},{R_ZOD_IN} 0 0 1 {xd:.1f},{yd:.1f} Z" '
                 f'fill="{ELEM_TINT[ZOD_ELEM[i]]}" stroke="#e3d9bf" stroke-width="0.8"/>')
        xl, yl = polar(a0 + 15, (R_ZOD_OUT + R_ZOD_IN) / 2)
        P.append(f'<text class="z" x="{xl:.1f}" y="{yl:.1f}" text-anchor="middle" dominant-baseline="central">{ZODIAC[i]}</text>')

    # ---- VÒNG TRONG: địa bàn 12 chi (ký hiệu, neo tiết khí) ----
    for chi in CHI:
        c = CHI_LON[chi]
        a0, a1 = c - 15, c + 15
        xa, ya = polar(a0, R_DIA_OUT)
        xb, yb = polar(a1, R_DIA_OUT)
        xc, yc = polar(a1, R_DIA_IN)
        xd, yd = polar(a0, R_DIA_IN)
        is_menh = chi == menh
        col = HANH_COLOR[CHI_HANH[chi]]
        fill = col if is_menh else "#fbf8f1"
        op = "0.16" if is_menh else "1"
        P.append(f'<path d="M{xa:.1f},{ya:.1f} A{R_DIA_OUT},{R_DIA_OUT} 0 0 0 {xb:.1f},{yb:.1f} '
                 f'L{xc:.1f},{yc:.1f} A{R_DIA_IN},{R_DIA_IN} 0 0 1 {xd:.1f},{yd:.1f} Z" '
                 f'fill="{fill}" fill-opacity="{op}" stroke="{col if is_menh else "#ddd5c4"}" '
                 f'stroke-width="{1.8 if is_menh else 0.8}"/>')
        xl, yl = polar(c, (R_DIA_OUT + R_DIA_IN) / 2)
        P.append(f'<text class="chi" x="{xl:.1f}" y="{yl:.1f}" text-anchor="middle" '
                 f'dominant-baseline="central" fill="{col}">{chi}</text>')
        if is_menh:
            xm, ym = polar(c, R_DIA_IN - 9)
            P.append(f'<text x="{xm:.1f}" y="{ym:.1f}" text-anchor="middle" dominant-baseline="central" '
                     f'font-size="8.5" font-weight="700" fill="{col}">MỆNH</text>')

    # ---- TRÁI ĐẤT ở tâm ----
    P.append(f'<circle cx="{CX}" cy="{CY}" r="{R_EARTH}" fill="#3b6ea5" stroke="#2a5080" stroke-width="1.5"/>')
    P.append(f'<ellipse cx="{CX-7}" cy="{CY-4}" rx="10" ry="7" fill="#5a9e63" opacity="0.85"/>')
    P.append(f'<ellipse cx="{CX+9}" cy="{CY+8}" rx="7" ry="5" fill="#5a9e63" opacity="0.85"/>')
    P.append(f'<text x="{CX}" y="{CY+R_EARTH+13}" text-anchor="middle" font-size="9.5" fill="#5a5446">Trái Đất</text>')

    # ---- CẦU NỐI Mặt Trời: tia từ tâm ra mép, qua vị trí thật của Mặt Trời ----
    sx, sy = polar(sun_lon, R_ZOD_IN)
    ex, ey = polar(sun_lon, R_DIA_IN)
    P.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
             f'stroke="#e8a838" stroke-width="2" stroke-dasharray="4 3" opacity="0.85"/>')

    # ---- 10 thiên thể tại vị trí THẬT (vòng giữa), né chồng ----
    items = sorted(((bodies[k].ecliptic_longitude, k, bodies[k]) for k in PLANET_VI), key=lambda t: t[0])
    last_lon, tier = -99.0, 0
    for lon, key, b in items:
        if lon - last_lon < 9:
            tier += 1
        else:
            tier = 0
        last_lon = lon
        r = R_PLANET - tier * 23
        x, y = polar(lon, r)
        is_sun = key == "sun"
        dot = "#e8a838" if is_sun else ("#c9c2b4" if key == "moon" else "#5a5446")
        P.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6.5 if is_sun else 4.5}" fill="{dot}" '
                 f'stroke="#fff" stroke-width="1"/>')
        # nhãn đặt hơi ra ngoài tâm; chữ nghiêng = nghịch hành
        lx, ly = polar(lon, r + 13)
        fst = "italic" if b.is_retrograde else "normal"
        P.append(f'<text class="pl" x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                 f'dominant-baseline="central" font-style="{fst}" '
                 f'fill="{"#b5701a" if is_sun else "#33302a"}">{PLANET_VI[key]}</text>')

    # ASC marker
    ax, ay = polar(chart.ascendant.ecliptic_longitude, R_ZOD_OUT + 6)
    P.append(f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" dominant-baseline="central" '
             f'font-size="10" font-weight="700" fill="#7a5320">Asc</text>')

    # ---- chú giải ----
    ly = 712
    P.append(f'<line x1="60" y1="{ly-22}" x2="620" y2="{ly-22}" stroke="#e3d9bf"/>')
    P.append(f'<circle cx="92" cy="{ly-4}" r="5" fill="#e8a838"/>'
             f'<text class="lg" x="104" y="{ly}" >Vòng ngoài = bầu trời THẬT (skyfield/DE440s)</text>')
    P.append(f'<rect x="372" y="{ly-9}" width="10" height="10" rx="2" fill="#c0392b" fill-opacity="0.3" stroke="#c0392b"/>'
             f'<text class="lg" x="388" y="{ly}">Vòng trong = địa bàn KÝ HIỆU · ⸺ Mặt Trời neo địa bàn</text>')
    P.append('</svg>')
    return "\n".join(P)


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/natal_universe.svg"
    svg = build_svg()
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ SVG: {out}  ({len(svg)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
