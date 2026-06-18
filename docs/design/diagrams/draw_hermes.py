#!/usr/bin/env python3
"""Vẽ sơ đồ kiến trúc Hermes (PNG) bằng Pillow — font DejaVu (hỗ trợ tiếng Việt)."""
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(sz, bold=False): return ImageFont.truetype(FONTB if bold else FONT, sz)

BG = (248, 249, 251); INK = (30, 34, 42); SUB = (90, 98, 110)
BLUE = (219, 234, 254); BLUE_E = (37, 99, 235)
GREEN = (220, 245, 224); GREEN_E = (22, 145, 70)
GOLD = (255, 243, 205); GOLD_E = (191, 134, 0)
PURP = (237, 228, 250); PURP_E = (124, 58, 173)
GREY = (236, 238, 242); GREY_E = (110, 116, 126)
RED = (253, 226, 226); RED_E = (200, 40, 40)


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def box(d, x, y, w, h, title, body="", fill=BLUE, edge=BLUE_E, ts=22, bs=16):
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=fill, outline=edge, width=3)
    cy = y + 14
    for ln in wrap(d, title, f(ts, True), w - 24):
        tw = d.textlength(ln, font=f(ts, True))
        d.text((x + (w - tw) / 2, cy), ln, font=f(ts, True), fill=INK)
        cy += ts + 6
    if body:
        cy += 2
        for ln in body.split("\n"):
            for s in wrap(d, ln, f(bs), w - 24):
                tw = d.textlength(s, font=f(bs))
                d.text((x + (w - tw) / 2, cy), s, font=f(bs), fill=SUB)
                cy += bs + 4


def arrow(d, x1, y1, x2, y2, color=GREY_E, w=3, label=None):
    d.line([x1, y1, x2, y2], fill=color, width=w)
    import math
    ang = math.atan2(y2 - y1, x2 - x1); L = 12
    d.polygon([(x2, y2),
               (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)),
               (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))], fill=color)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tw = d.textlength(label, font=f(14))
        d.rectangle([mx - tw / 2 - 4, my - 11, mx + tw / 2 + 4, my + 11], fill=BG)
        d.text((mx - tw / 2, my - 9), label, font=f(14), fill=SUB)


def title(d, W, t, sub):
    d.text((40, 26), t, font=f(34, True), fill=INK)
    d.text((40, 72), sub, font=f(17), fill=SUB)
    d.line([40, 104, W - 40, 104], fill=(210, 214, 220), width=2)


# ── Ảnh 1: TỔNG QUAN — chỉ huy + roster + luồng trả lời + lưu trữ ──────────────
def img1():
    W, H = 1480, 1080
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    title(d, W, "HỆ HERMES — Tổng quan xử lý & trả lời",
          "8 sage độc lập + arbiter (chánh thẩm) + orchestrator (chỉ huy) · dùng CHUNG cho mọi user")
    box(d, 590, 130, 300, 70, "👤 USER hỏi", "trong ô chat (AppChat / web)", GREY, GREY_E)
    box(d, 540, 230, 400, 84, "CỔNG RÀO (rẻ, chưa tốn)",
        "scope guard · gate gói/free · ngân sách\n'làm hộ'/ngoài miền → từ chối", RED, RED_E, 20, 14)
    arrow(d, 740, 200, 740, 230)
    # chỉ huy
    box(d, 560, 348, 360, 76, "🧭 ORCHESTRATOR = CHỈ HUY",
        "chọn 2–5 sage liên quan · điều phối", PURP, PURP_E, 20, 14)
    arrow(d, 740, 314, 740, 348, label="hợp lệ")
    # quick path (trái)
    box(d, 120, 360, 300, 80, "TRẢ LỜI NHANH", "1 sage liên quan · rẻ ~5–10s", GREEN, GREEN_E, 20, 14)
    arrow(d, 560, 386, 420, 400, label="câu thường")
    # sages
    sages = ["Tử Vi", "Bát Tự", "Mai Hoa", "Lục Hào", "Hà Lạc", "Liên Hoa", "Thần Số", "Chiêm Tinh"]
    sx, sy, sw, sh = 540, 470, 182, 56
    for i, s in enumerate(sages):
        c, r = i % 4, i // 4
        box(d, sx + c * 196, sy + r * 72, sw, sh, s, "", BLUE, BLUE_E, 18)
    arrow(d, 740, 424, 740, 470, label="câu sâu")
    d.text((548, 620), "8 sage đọc ĐỘC LẬP, thuần khiết — KHÔNG nói với nhau", font=f(15), fill=SUB)
    # arbiter
    box(d, 560, 648, 360, 76, "⚖️ ARBITER = chánh thẩm",
        "gom + đối chiếu: đồng thuận / mâu thuẫn", GOLD, GOLD_E, 20, 14)
    arrow(d, 740, 598, 740, 648)
    # post + answer
    box(d, 540, 752, 400, 72, "POST-FILTER (cấm tiên tri) → trả USER",
        "+ lưu lịch sử", GREY, GREY_E, 19, 14)
    arrow(d, 740, 724, 740, 752)
    arrow(d, 270, 440, 690, 760, color=GREEN_E)   # quick → answer
    # storage box
    box(d, 1010, 470, 410, 250, "LƯU TRỮ (cô lập RLS)",
        "DANH TÍNH → AppChat/Firebase\n(SĐT, email, Firebase UID)\n\nHỒ SƠ MỆNH-LÝ RIÊNG → YI Postgres\n• lá số / tứ trụ (dữ kiện)\n• lịch sử hỏi-đáp\n• ký ức user tự kể\n\nLLM chỉ thấy bản ẩn danh", BLUE, BLUE_E, 20, 14)
    arrow(d, 940, 788, 1010, 690, color=BLUE_E, label="lưu")
    im.save("/home/user/hermes_01_tongquan.png")


# ── Ảnh 2: VÒNG TRI THỨC 3 TẦNG — sách mới lan tới mọi user ───────────────────
def img2():
    W, H = 1480, 1020
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    title(d, W, "VÒNG TRI THỨC — sách mới → não chung → mọi user",
          "Chuẩn bị trước = DỮ KIỆN + KIẾN THỨC CHUNG · LUẬN GIẢI LLM thì lazy + cache theo version")
    # left: book pipeline
    box(d, 60, 150, 300, 64, "📖 Sách mới", "dịch + chắt lọc (bookflow)", GREY, GREY_E, 20, 14)
    box(d, 60, 250, 300, 84, "CỔNG DUYỆT (evolve_gate)",
        "em chấm độ tự tin:\ncao+nhỏ → tự nhận · phái mới → ANH duyệt", RED, RED_E, 18, 13)
    arrow(d, 210, 214, 210, 250)
    box(d, 60, 372, 300, 76, "bump knowledge_version",
        "→ cache luận giải cũ tự hết hạn", GOLD, GOLD_E, 18, 13)
    arrow(d, 210, 334, 210, 372)
    # 3 tiers (right)
    box(d, 470, 150, 940, 150, "TẦNG 1 — KIẾN THỨC CHUNG (wiki/skill/sage/lăng kính)",
        "Dùng CHUNG mọi user · versioned · SÁCH MỚI BỒI VÀO ĐÂY (1 lần, cả triệu user hưởng)", GREEN, GREEN_E, 21, 15)
    box(d, 470, 330, 940, 150, "TẦNG 2 — DỮ KIỆN RIÊNG user (pre-compute + cache)",
        "lá số / tứ trụ / cách cục của CHÍNH user · tất định, rẻ · CHART KHÔNG ĐỔI khi thêm sách", BLUE, BLUE_E, 21, 15)
    box(d, 470, 510, 940, 150, "TẦNG 3 — LUẬN GIẢI (LLM = T1 × T2)",
        "LAZY sinh khi hỏi + CACHE theo version · tier: free nông / gói sâu · KHÔNG pre-gen cho mọi user", PURP, PURP_E, 21, 15)
    arrow(d, 360, 410, 470, 405, color=GREEN_E, label="bồi T1")
    # fan-out to users
    uy = 740
    box(d, 470, uy, 280, 70, "Hermes user A", "giỏi lên NGAY", GREY, GREY_E, 19, 14)
    box(d, 600, uy, 280, 70, "Hermes user B", "", GREY, GREY_E, 19)
    box(d, 1130, uy, 280, 70, "… triệu user", "cùng hưởng", GREY, GREY_E, 19, 14)
    d.text((905, uy + 22), ". . .", font=f(30, True), fill=SUB)
    arrow(d, 700, 660, 610, uy)
    arrow(d, 940, 660, 1000, uy)
    box(d, 470, uy + 100, 940, 64, "📨 BÁO CHỦ ĐỘNG cho user liên quan: 'có lăng kính mới soi việc của bạn' (gói)",
        "", GOLD, GOLD_E, 18)
    arrow(d, 940, uy + 70, 940, uy + 100)
    im.save("/home/user/hermes_02_tri_thuc_3tang.png")


# ── Ảnh 3: PHÒNG QUẢN TRỊ ─────────────────────────────────────────────────────
def img3():
    W, H = 1480, 900
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    title(d, W, "PHÒNG QUẢN TRỊ HERMES (owner-only)",
          "Founder chỉ huy cả hệ · audit mọi hành động · chỉ huy ĐỀ XUẤT, đụng não-chung phải anh xác nhận")
    box(d, 600, 140, 280, 78, "👑 FOUNDER (anh)", "owner-only", GOLD, GOLD_E, 21, 14)
    box(d, 560, 260, 360, 78, "🧭 CHAT CHỈ HUY", "orchestrator (operator)\nbáo cáo + đề xuất", PURP, PURP_E, 20, 13)
    arrow(d, 740, 218, 740, 260)
    panels = [
        ("ROSTER", "10 vai · bật/tắt · xem/sửa SOUL", BLUE, BLUE_E, 80),
        ("CỔNG DUYỆT", "hàng đợi tri thức mới\n→ Duyệt / Bác (độ tự tin)", GREEN, GREEN_E, 430),
        ("GIÁM SÁT", "chi phí vs ngân sách · lượt\n#cờ vi-phạm-paradigm · cache", GOLD, GOLD_E, 780),
        ("AUDIT", "nhật ký mọi thao tác admin", GREY, GREY_E, 1130),
    ]
    for t, b, c, e, x in panels:
        box(d, x, 410, 280, 120, t, b, c, e, 21, 14)
        arrow(d, 740, 338, x + 140, 410, color=e)
    box(d, 360, 600, 760, 92, "RÀNG BUỘC QUẢN TRỊ",
        "owner-only + audit toàn bộ · chỉ huy không tự phá (xác nhận tay) · tách Hermes-sản-phẩm khỏi\nHermes-quản-trị · giữ paradigm (không tiên tri) · KHÔNG lộ PII end-user", RED, RED_E, 21, 14)
    arrow(d, 740, 530, 740, 600)
    im.save("/home/user/hermes_03_phong_quan_tri.png")


img1(); img2(); img3()
print("OK: 3 PNG saved to /home/user/")
