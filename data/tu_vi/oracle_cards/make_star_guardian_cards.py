from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path("/Users/ozvietnamdesktop/Desktop/yi/data/published/star_guardian_cards")
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

cards = [
    ("THIÊN ĐỒNG", "HỘ MỆNH", "Phúc khí mềm như nước", "Chiêu thức: Hồi Tâm Thủy Ấn", "Tương tác: làm dịu Mệnh Tỵ, giữ Founder biết hồi phục.", "water"),
    ("LỘC TỒN", "TÀI KHỐ", "Kho lộc giữ mệnh", "Chiêu thức: Kim Khố Tỏa Lộc", "Tương tác: tiền đến bền, nhưng phải có luật giữ của.", "vault"),
    ("THAM LANG", "HÓA LỘC", "Đào hoa sinh tài", "Chiêu thức: Trạch Lộc Kiếm", "Tương tác: mở đường đất đai, cơ ngơi, cơ hội lớn.", "blade"),
    ("TỬ VI", "ĐẾ TINH", "Ngai sao của người dẫn đầu", "Chiêu thức: Đế Tọa Triều Tinh", "Tương tác: gọi quý nhân, đội ngũ, tầm nhìn Founder.", "crown"),
    ("THIÊN PHỦ", "BẢO KHỐ", "Ấn tín của người quản trị", "Chiêu thức: Phủ Ấn Tàng Ngọc", "Tương tác: gom nguồn lực, giữ hậu thuẫn gia tộc.", "seal"),
    ("NHẬT NGUYỆT", "PHÚC ĐỨC", "Hai vầng sáng hộ tâm", "Chiêu thức: Song Minh Chiếu Phúc", "Tương tác: soi sáng cung Phúc, nâng đỡ lúc nguy.", "sunmoon"),
    ("THIÊN CƠ", "HÓA KỴ", "Bàn cờ của kế hoạch nghẽn", "Chiêu thức: Kỵ Cơ Phá Trận", "Tương tác: bắt lỗi hợp đồng, pháp lý, chiến lược.", "chess"),
    ("KHÔNG KIẾP", "SONG SÁT", "Gió lốc hao tán", "Chiêu thức: Hư Không Đoạn Tài", "Tương tác: cảnh báo bong bóng và canh bạc quá tay.", "storm"),
    ("ĐẠI VẬN", "KIẾM ĐỒ", "Bốn cổng đường đời", "Chiêu thức: Thập Niên Bộ Pháp", "Tương tác: đi qua vận tốt bằng kỷ luật và tỉnh thức.", "gates"),
    ("KẾT TÂM", "AN", "Mệnh là bản đồ, tâm là tay lái", "Chiêu thức: Tâm Đăng Định Mệnh", "Tương tác: quy tụ các sao thành vòng hộ pháp.", "lamp"),
]

palette = {
    "bg": (18, 24, 34),
    "paper": (244, 232, 207),
    "ink": (37, 45, 61),
    "gold": (200, 154, 74),
    "red": (155, 66, 55),
    "jade": (87, 132, 112),
    "blue": (70, 111, 138),
}

def ft(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def centered(draw, y, text, font, fill, width=1080):
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((width - (box[2]-box[0]))/2, y), text, font=font, fill=fill)

def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi/2 + i * math.pi/5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(a)*rr, cy + math.sin(a)*rr))
    draw.polygon(pts, fill=fill)

def figure(draw, kind):
    cx, cy = 540, 660
    gold, ink, red, jade, blue = palette["gold"], palette["ink"], palette["red"], palette["jade"], palette["blue"]
    draw.ellipse((cx-138, cy-120, cx+138, cy+156), fill=(236, 214, 170), outline=gold, width=7)
    draw.ellipse((cx-52, cy-258, cx+52, cy-154), fill=(238, 221, 190), outline=ink, width=5)
    draw.polygon([(cx-120, cy-126), (cx+120, cy-126), (cx+172, cy+220), (cx-172, cy+220)], fill=(48, 62, 78), outline=gold)
    draw.line((cx, cy-150, cx, cy+200), fill=gold, width=7)
    for dx in [-220, 220]:
        draw.line((cx + (90 if dx>0 else -90), cy-80, cx+dx, cy+90), fill=gold, width=8)
    if kind == "water":
        for i in range(4):
            draw.arc((cx-260+i*30, cy+130+i*8, cx+260-i*30, cy+260+i*8), 190, 350, fill=blue, width=8)
        draw.ellipse((cx-38, cy-72, cx+38, cy+36), outline=blue, width=7)
    elif kind == "vault":
        draw.rounded_rectangle((cx-165, cy+35, cx+165, cy+230), 22, fill=(69, 54, 42), outline=gold, width=8)
        draw.ellipse((cx-40, cy+90, cx+40, cy+170), outline=gold, width=7)
        draw.line((cx, cy+130, cx, cy+175), fill=gold, width=7)
    elif kind == "blade":
        draw.polygon([(cx+210, cy-260), (cx+255, cy-180), (cx-155, cy+220), (cx-190, cy+185)], fill=(221, 226, 224), outline=ink)
        draw.line((cx-135, cy+200, cx-210, cy+275), fill=red, width=14)
        draw.ellipse((cx-275, cy+225, cx-170, cy+330), outline=gold, width=8)
    elif kind == "crown":
        draw.polygon([(cx-95, cy-262), (cx-40, cy-340), (cx, cy-260), (cx+44, cy-340), (cx+96, cy-262)], fill=gold, outline=ink)
        for x in [cx-40, cx, cx+44]: star(draw, x, cy-340, 18, (255,244,190))
    elif kind == "seal":
        draw.rounded_rectangle((cx-95, cy-312, cx+95, cy-175), 12, fill=red, outline=gold, width=7)
        draw.text((cx-45, cy-280), "府", font=ft(68, True), fill=(255,238,205))
    elif kind == "sunmoon":
        draw.ellipse((cx-245, cy-265, cx-95, cy-115), fill=(233, 174, 62), outline=gold, width=5)
        draw.ellipse((cx+95, cy-265, cx+245, cy-115), fill=(214, 225, 232), outline=blue, width=5)
        draw.ellipse((cx+135, cy-265, cx+285, cy-115), fill=palette["paper"])
    elif kind == "chess":
        for i in range(4):
            for j in range(4):
                fill = (238, 224, 196) if (i+j)%2 else (58, 63, 76)
                draw.rectangle((cx-160+i*80, cy-310+j*70, cx-80+i*80, cy-240+j*70), fill=fill, outline=gold)
        star(draw, cx+180, cy-185, 42, red)
    elif kind == "storm":
        for i in range(3):
            draw.arc((cx-265+i*50, cy-300+i*55, cx+265-i*50, cy+210-i*10), 250, 95, fill=red if i==1 else blue, width=16)
        star(draw, cx-185, cy-190, 36, (225,225,230)); star(draw, cx+180, cy-80, 36, (225,225,230))
    elif kind == "gates":
        for i in range(4):
            x = cx-255+i*170
            draw.rounded_rectangle((x, cy-290, x+105, cy+120), 18, outline=gold, width=8)
            draw.text((x+20, cy-100), ["25", "35", "45", "55"][i], font=ft(34, True), fill=gold)
        draw.line((cx-300, cy+165, cx+310, cy-250), fill=red, width=10)
    else:
        draw.rounded_rectangle((cx-55, cy-320, cx+55, cy-120), 18, fill=(236,226,190), outline=gold, width=7)
        draw.ellipse((cx-22, cy-270, cx+22, cy-226), fill=(255,214,96))
        draw.arc((cx-250, cy+80, cx+250, cy+230), 180, 360, fill=jade, width=10)

def make_card(i, title, subtitle, tagline, move, interact, kind):
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), palette["bg"])
    d = ImageDraw.Draw(img)
    for y in range(H):
        shade = int(22 + y/H*18)
        d.line((0, y, W, y), fill=(shade, shade+5, shade+13))
    for n in range(70):
        x = (n * 157) % W
        y = (n * 263) % H
        star(d, x, y, 5+(n%3)*2, (116, 102, 74))
    d.rounded_rectangle((70, 70, W-70, H-70), 34, fill=palette["paper"], outline=palette["gold"], width=8)
    d.rounded_rectangle((104, 104, W-104, H-104), 24, outline=(116, 86, 48), width=3)
    d.rectangle((104, 104, W-104, 248), fill=(39, 49, 66))
    centered(d, 126, f"THẺ {i:02d}", ft(30, True), palette["gold"])
    centered(d, 166, title, ft(66, True), (255, 247, 225))
    centered(d, 242, subtitle, ft(36, True), palette["red"])
    figure(d, kind)
    centered(d, 900, tagline, ft(38, True), palette["ink"])
    y = 970
    for label, text in [("CHIÊU THỨC", move), ("TƯƠNG TÁC LÁ SỐ", interact)]:
        d.rounded_rectangle((142, y, W-142, y+112), 14, fill=(250, 242, 224), outline=(207, 177, 124), width=3)
        d.text((170, y+18), label, font=ft(22, True), fill=palette["gold"])
        for line in wrap(d, text, ft(27), 700)[:2]:
            d.text((170, y+50), line, font=ft(27), fill=palette["ink"])
            y += 31
        y += 68
    centered(d, 1248, "võ hiệp tinh tú · hộ mệnh founder", ft(24), (98, 86, 65))
    out = OUT / f"{i:02d}_{title.lower().replace(' ', '_')}.png"
    img.save(out, quality=95)
    return out

paths = [make_card(i, *card) for i, card in enumerate(cards, 1)]

thumb_w, thumb_h = 270, 338
sheet = Image.new("RGB", (thumb_w*5, thumb_h*2), (26, 30, 38))
for idx, p in enumerate(paths):
    im = Image.open(p)
    im.thumbnail((thumb_w-16, thumb_h-16))
    x, y = (idx % 5) * thumb_w + 8, (idx // 5) * thumb_h + 8
    sheet.paste(im, (x, y))
sheet_path = OUT / "star_guardian_cards_contact_sheet.png"
sheet.save(sheet_path, quality=95)
print(sheet_path)
