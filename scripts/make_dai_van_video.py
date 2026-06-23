#!/usr/bin/env python3
"""Video khoa học Đại Vận — kịch bản CHUYÊN SÂU + thuyết minh tiếng Việt + địa bàn
đồng bộ highlight + ghép ffmpeg. PoC: lá số founder, Đại Vận hiện tại (Thân, 35-44).

Dây chuyền:
  1. Data: build_natal + đại vận + lưu niên (engine, hàm thuần).
  2. Kịch bản: segment {text, highlight} — paradigm-honest (sân khấu/vận hành, KHÔNG predict).
  3. Thuyết minh: edge-tts (vi-VN, free) → mp3/segment + thời lượng.
  4. Khung hình: địa bàn SVG, chủ thể đang nói SÁNG lên, còn lại mờ → cairosvg PNG.
  5. Ghép: ffmpeg (frame giữ theo thời lượng câu) + audio → mp4.

    python3 scripts/make_dai_van_video.py [out.mp4]
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine.natal_universe import build_natal  # noqa: E402
from engine.tu_vi import an_sao  # noqa: E402

VN = timezone(timedelta(hours=7))
FOUNDER = datetime(1988, 6, 5, 23, 30, tzinfo=VN)
TARGET_YEAR = 2026
VOICE = "vi-VN-HoaiMyNeural"

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
# vị trí ô địa bàn 4×4 (col,row)
CELL = {"Tỵ": (0, 0), "Ngọ": (1, 0), "Mùi": (2, 0), "Thân": (3, 0), "Dậu": (3, 1),
        "Tuất": (3, 2), "Hợi": (3, 3), "Tý": (2, 3), "Sửu": (1, 3), "Dần": (0, 3),
        "Mão": (0, 2), "Thìn": (0, 1)}
XUNG = {"Tý": "Ngọ", "Sửu": "Mùi", "Dần": "Thân", "Mão": "Dậu", "Thìn": "Tuất", "Tỵ": "Hợi",
        "Ngọ": "Tý", "Mùi": "Sửu", "Thân": "Dần", "Dậu": "Mão", "Tuất": "Thìn", "Hợi": "Tỵ"}
TAM_HOP = [["Thân", "Tý", "Thìn"], ["Hợi", "Mão", "Mùi"], ["Dần", "Ngọ", "Tuất"], ["Tỵ", "Dậu", "Sửu"]]
HANH_COLOR = {"thuy": "#4a90d9", "moc": "#4caf50", "hoa": "#e05a4a", "tho": "#d4a82a", "kim": "#9aa0a6"}


def hanh_key(s: str) -> str:
    s = (s or "").split("/")[0].strip()
    return {"thủy": "thuy", "mộc": "moc", "hỏa": "hoa", "thổ": "tho", "kim": "kim"}.get(s, "kim")


def compute():
    n = build_natal(FOUNDER, lat=21.03, lon=105.85, target_year=TARGET_YEAR)
    db = n["dia_ban"]
    stars = {c["chi"]: c["chinh_tinh"] for c in db["cung"]}
    chain = an_sao.dai_van_trajectory(
        menh_index=CHI.index(db["menh_chi"]), cuc=db["cuc"],
        year_stem=db["year_can_chi"].split()[0], gender="nam")
    age = TARGET_YEAR - 1988 + 1
    cur = next((d for d in chain if d["start_age"] <= age <= d["end_age"]), chain[3])
    return {"n": n, "db": db, "stars": stars, "dv": cur, "age": age}


# ── KỊCH BẢN CHUYÊN SÂU (paradigm-honest) — highlight = {cung:set, sao:set, rel:'xung'|'tamhop'} ──
def segments(R):
    dv = R["dv"]["branch"]
    return [
        ("Đây là lá số của anh, dựng trên nền vũ trụ thật. Trước khi xem, xin nhớ một điều cốt lõi: "
         "lá số không phải bản án đã định. Nó là một sân khấu. Và mệnh, là động từ — việc anh vận hành sân khấu ấy.",
         {"cung": set(CHI), "sao": set(), "rel": None}),
        (f"Thập niên này, từ tuổi ba mươi lăm đến bốn mươi tư, ánh đèn của đại vận chiếu về cung {dv}.",
         {"cung": {dv}, "sao": set(), "rel": None}),
        (f"Cung {dv} của anh vô chính diệu — không một chính tinh nào toạ thủ. Trong tử vi, đó không phải "
         "khoảng trống, mà là một khoảng mở: nó mượn ánh sáng từ cung đối diện, cung Dần.",
         {"cung": {dv, "Dần"}, "sao": set(), "rel": "xung"}),
        ("Ở Dần, anh có Thiên Cơ và Thái Âm. Thiên Cơ, hành Mộc, là sao của trí xảo, mưu lược, của vận động "
         "không ngừng; nhưng nơi anh, Thiên Cơ mang Hóa Kỵ — cái trí ấy dễ vướng, dễ tự buộc mình. "
         "Thái Âm, hành Thủy, là sao của tài bạch và nội tâm, của sự nuôi dưỡng âm thầm; và Thái Âm nơi anh "
         "mang Hóa Quyền — cái sâu kín ấy có thực quyền.",
         {"cung": {"Dần"}, "sao": {"Thiên Cơ", "Thái Âm"}, "rel": "xung"}),
        (f"Soi rộng ra tam phương của thập niên: cung {dv} hợp với Tý và Thìn. Ở Tý, Thái Dương hãm địa — "
         "dương khí có đó, nhưng như mặt trời lúc nửa đêm, sáng mà chưa toả. Ở Thìn, Cự Môn — sao của khẩu "
         "thiệt, của lời ăn tiếng nói và tranh biện.",
         {"cung": {dv, "Tý", "Thìn"}, "sao": {"Thái Dương", "Cự Môn"}, "rel": "tamhop"}),
        ("Và đây là chỗ lá số sống động. Mỗi năm một sân khấu khác. Năm hai nghìn không trăm hai mươi sáu, "
         "năm Bính, lưu Hóa Quyền lại rơi đúng vào Thiên Cơ — cái trí đang vướng Kỵ của anh, năm nay được tiếp "
         "thêm quyền; còn lưu Hóa Kỵ thì chạm vào Liêm Trinh. Cùng một lá số, mỗi năm thở một nhịp khác.",
         {"cung": {"Dần", "Mùi"}, "sao": {"Thiên Cơ", "Liêm Trinh"}, "rel": None}),
        ("Tất cả những điều này không nói anh sẽ thành hay bại. Nó nói: thập niên này, cái tính của anh — "
         "Thiên Tướng đắc địa ở cung Mệnh, sao của phụ tá, điều phối và ấn tín — vận hành tốt nhất khi anh đi "
         "qua khoảng mở của cung Thân bằng trí của Thiên Cơ và chiều sâu của Thái Âm, mà không để cái Kỵ buộc mình.",
         {"cung": {"Tỵ", dv}, "sao": {"Thiên Tướng"}, "rel": None}),
        ("Số là sân khấu. Còn diễn, là việc của anh.",
         {"cung": set(CHI), "sao": set(), "rel": None}),
    ]


def wrap(text: str, width: int = 64) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def render_frame(R, hl, caption: str) -> str:
    db, stars, dv = R["db"], R["stars"], R["dv"]
    OX, OY, S = 70, 70, 560  # địa bàn 560×560
    cw = S / 4
    P = ['<svg width="100%" viewBox="0 0 1280 720" xmlns="http://www.w3.org/2000/svg">']
    P.append('<rect width="1280" height="720" fill="#0b1016"/>')
    P.append('<style>text{font-family:Georgia,"Times New Roman",serif}</style>')
    # tiêu đề
    P.append(f'<text x="640" y="40" text-anchor="middle" font-size="26" font-weight="700" fill="#e6c45a">'
             f'ĐẠI VẬN cung {dv["branch"]} · tuổi {dv["start_age"]}–{dv["end_age"]} · lá số {db["year_can_chi"]} · lưu niên {R["n"]["luu_nien"]["can_chi"]}</text>')

    def center(chi):
        c, r = CELL[chi]
        return OX + c * cw + cw / 2, OY + r * cw + cw / 2

    # đường quan hệ (xung/tam hợp) — vẽ trước ô
    if hl["rel"] == "xung":
        a = [c for c in hl["cung"]]
        if len(a) >= 2:
            x1, y1 = center(a[0]); x2, y2 = center(a[1])
            P.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#e0a040" stroke-width="2.5" stroke-dasharray="6 4" opacity="0.8"/>')
    if hl["rel"] == "tamhop":
        grp = next((g for g in TAM_HOP if set(g) <= hl["cung"] or hl["cung"] & set(g)), None)
        grp = next((g for g in TAM_HOP if any(c in hl["cung"] for c in g)), None)
        if grp:
            pts = [center(c) for c in grp]
            d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + " Z"
            P.append(f'<path d="{d}" fill="none" stroke="#66c2b5" stroke-width="2.5" opacity="0.75"/>')

    # 12 cung
    for chi, (c, r) in CELL.items():
        x, y = OX + c * cw, OY + r * cw
        on = chi in hl["cung"]
        bg = "#16202c" if on else "#0e141b"
        bd = "#e6c45a" if on else "#26323f"
        op = "1" if on else "0.4"
        P.append(f'<g opacity="{op}"><rect x="{x:.0f}" y="{y:.0f}" width="{cw:.0f}" height="{cw:.0f}" '
                 f'fill="{bg}" stroke="{bd}" stroke-width="{2.5 if on else 1}" rx="6"/>')
        P.append(f'<text x="{x+8:.0f}" y="{y+20:.0f}" font-size="13" fill="#8a9aa6">{chi}</text>')
        sl = stars.get(chi, [])
        for i, st in enumerate(sl):
            col = HANH_COLOR[hanh_key(st["ngu_hanh"])]
            big = st["do_sang"] == "đắc"
            sao_on = st["name"] in hl["sao"]
            fs = (17 if big else 14) + (3 if sao_on else 0)
            txt = st["name"] + (f" ·{st['hoa']}" if st.get("hoa") else "")
            yy = y + cw / 2 + (i - (len(sl) - 1) / 2) * 22
            weight = "700" if sao_on else "600"
            P.append(f'<text x="{x+cw/2:.0f}" y="{yy:.0f}" text-anchor="middle" font-size="{fs}" '
                     f'font-weight="{weight}" fill="{col}">{txt}</text>')
            if sao_on:
                P.append(f'<circle cx="{x+cw/2:.0f}" cy="{yy-fs:.0f}" r="3" fill="#e6c45a"/>')
        P.append('</g>')

    # trung tâm: chú thích đại vận
    P.append(f'<g><rect x="{OX+cw:.0f}" y="{OY+cw:.0f}" width="{2*cw:.0f}" height="{2*cw:.0f}" fill="#0b1016" stroke="#26323f" rx="8"/>')
    cx, cy = OX + 2 * cw, OY + 2 * cw
    P.append(f'<text x="{cx:.0f}" y="{cy-18:.0f}" text-anchor="middle" font-size="15" fill="#9aa6b0">Mệnh {db["menh_chi"]} · {stars[db["menh_chi"]][0]["name"]}</text>')
    P.append(f'<text x="{cx:.0f}" y="{cy+6:.0f}" text-anchor="middle" font-size="22" font-weight="700" fill="#e6c45a">Đại Vận {dv["branch"]}</text>')
    P.append(f'<text x="{cx:.0f}" y="{cy+30:.0f}" text-anchor="middle" font-size="13" font-style="italic" fill="#7a8690">mệnh là động từ</text>')
    P.append('</g>')

    # caption (lời thuyết minh) — panel phải
    px = 680
    P.append(f'<rect x="{px}" y="80" width="540" height="560" fill="#0e141b" stroke="#26323f" rx="10"/>')
    lines = wrap(caption, 46)
    for i, ln in enumerate(lines[:16]):
        P.append(f'<text x="{px+24}" y="{120+i*30}" font-size="19" fill="#dbe4ea">{_esc(ln)}</text>')
    P.append('<text x="1200" y="700" text-anchor="end" font-size="12" font-style="italic" fill="#5a6670">YI-Chronos · tính được SÂN KHẤU, không tính kết cục</text>')
    P.append('</svg>')
    return "\n".join(P)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tts(text: str, out: Path) -> float:
    import time
    last = ""
    for attempt in range(5):
        r = subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text,
                            "--write-media", str(out)], capture_output=True, text=True)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 500:
            break
        last = (r.stderr or r.stdout or "?")[:160]
        time.sleep(2 + attempt * 2)
    else:
        raise RuntimeError(f"edge-tts fail 5×: {last}")
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(out)], capture_output=True, text=True)
    return float(dur.stdout.strip())


def main() -> int:
    out_mp4 = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/published/dai-van-than-founder.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    work = Path("/tmp/dvvideo")
    work.mkdir(exist_ok=True)
    R = compute()
    segs = segments(R)
    print(f"Đại Vận {R['dv']['branch']} (tuổi {R['dv']['start_age']}-{R['dv']['end_age']}) · {len(segs)} câu")

    frames_txt, audio_txt = [], []
    for i, (text, hl) in enumerate(segs):
        a = work / f"seg{i}.mp3"
        dur = tts(text, a)
        svg = render_frame(R, hl, text)
        png = work / f"seg{i}.png"
        cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png), output_width=1280, output_height=720)
        frames_txt.append(f"file '{png}'\nduration {dur:.3f}")
        audio_txt.append(f"file '{a}'")
        print(f"  câu {i+1}: {dur:.1f}s  → {text[:42]}…")

    # concat audio
    (work / "audio.txt").write_text("\n".join(audio_txt), encoding="utf-8")
    narration = work / "narration.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "audio.txt"),
                    "-c", "copy", str(narration)], check=True, capture_output=True)
    # concat frames (lặp file cuối cho demuxer)
    frames_txt.append(f"file '{work / f'seg{len(segs)-1}.png'}'")
    (work / "frames.txt").write_text("\n".join(frames_txt), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "frames.txt"),
                    "-i", str(narration), "-vf", "fps=25,format=yuv420p", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(out_mp4)],
                   check=True, capture_output=True)
    size = out_mp4.stat().st_size // 1024
    print(f"✅ VIDEO: {out_mp4}  ({size} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
