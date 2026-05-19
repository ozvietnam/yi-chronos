"""64 quẻ Chu Dịch — bảng tra ngắn gọn.

Source: Mai Hoa Dịch Số trang 270-271 (danh mục 64 quẻ).
Map: (upper_que, lower_que) → (vi_name, zh_name, kc_number, short_meaning).

Dùng để lookup nghĩa quẻ cho interpret engine.
"""

# 8 quẻ → bit pattern (top, mid, bot)
TRIGRAM_BITS = {
    "Càn": (1,1,1),
    "Đoài": (0,1,1),   # thượng khuyết = top âm
    "Ly": (1,0,1),     # trung hư = mid âm
    "Chấn": (0,0,1),   # ngưỡng vu = bot dương
    "Tốn": (1,1,0),    # hạ đoạn = bot âm
    "Khảm": (0,1,0),   # trung mãn = mid dương
    "Cấn": (1,0,0),    # phúc uyển = top dương
    "Khôn": (0,0,0),
}

# Bảng 64 quẻ — King Wen order
# (upper, lower) → (number, vi, zh, short)
HEXAGRAMS_64 = {
    ("Càn", "Càn"): (1, "Thuần Càn", "乾為天", "Trời — sáng tạo, mạnh mẽ"),
    ("Khôn", "Khôn"): (2, "Thuần Khôn", "坤為地", "Đất — nuôi dưỡng, thuận theo"),
    ("Khảm", "Chấn"): (3, "Thuỷ Lôi Truân", "屯", "Khó khăn ban đầu, mọc lên"),
    ("Cấn", "Khảm"): (4, "Sơn Thuỷ Mông", "蒙", "Mờ tối, non yếu, khai sáng"),
    ("Khảm", "Càn"): (5, "Thuỷ Thiên Nhu", "需", "Ăn uống, chờ đợi"),
    ("Càn", "Khảm"): (6, "Thiên Thuỷ Tụng", "訟", "Kiện cáo, tranh giành"),
    ("Khôn", "Khảm"): (7, "Địa Thuỷ Sư", "師", "Quân lĩnh, số đông"),
    ("Khảm", "Khôn"): (8, "Thuỷ Địa Tỷ", "比", "Thân thiết, gần gũi"),
    ("Tốn", "Càn"): (9, "Phong Thiên Tiểu Súc", "小畜", "Chứa nhỏ"),
    ("Càn", "Đoài"): (10, "Thiên Trạch Lý", "履", "Lễ — đi đúng"),
    ("Khôn", "Càn"): (11, "Địa Thiên Thái", "泰", "Thông suốt, hanh thông"),
    ("Càn", "Khôn"): (12, "Thiên Địa Bĩ", "否", "Bế tắc, không thông"),
    ("Càn", "Ly"): (13, "Thiên Hoả Đồng Nhân", "同人", "Cùng với người"),
    ("Ly", "Càn"): (14, "Hoả Thiên Đại Hữu", "大有", "Có nhiều, sở hữu lớn"),
    ("Khôn", "Cấn"): (15, "Địa Sơn Khiêm", "謙", "Khiêm nhường"),
    ("Chấn", "Khôn"): (16, "Lôi Địa Dự", "豫", "Vui vẻ"),
    ("Đoài", "Chấn"): (17, "Trạch Lôi Tuỳ", "隨", "Theo"),
    ("Cấn", "Tốn"): (18, "Sơn Phong Cổ", "蠱", "Mê loạn, đổ nát"),
    ("Khôn", "Đoài"): (19, "Địa Trạch Lâm", "臨", "Lớn, đến gần"),
    ("Tốn", "Khôn"): (20, "Phong Địa Quan", "觀", "Xem xét"),
    ("Ly", "Chấn"): (21, "Hoả Lôi Phệ Hạp", "噬嗑", "Cắn để hợp lại"),
    ("Cấn", "Ly"): (22, "Sơn Hoả Bí", "賁", "Trang sức"),
    ("Cấn", "Khôn"): (23, "Sơn Địa Bác", "剝", "Lột đi, suy"),
    ("Khôn", "Chấn"): (24, "Địa Lôi Phục", "復", "Trở lại"),
    ("Càn", "Chấn"): (25, "Thiên Lôi Vô Vọng", "無妄", "Không làm càn"),
    ("Cấn", "Càn"): (26, "Sơn Thiên Đại Súc", "大畜", "Chứa lớn"),
    ("Cấn", "Chấn"): (27, "Sơn Lôi Di", "頤", "Nuôi dưỡng"),
    ("Đoài", "Tốn"): (28, "Trạch Phong Đại Quá", "大過", "Quá lớn, vượt ngưỡng"),
    ("Khảm", "Khảm"): (29, "Thuần Khảm", "坎為水", "Hiểm trở"),
    ("Ly", "Ly"): (30, "Thuần Ly", "離為火", "Bám vào, sáng"),
    # Hạ kinh
    ("Đoài", "Cấn"): (31, "Trạch Sơn Hàm", "咸", "Giao cảm"),
    ("Chấn", "Tốn"): (32, "Lôi Phong Hằng", "恆", "Lâu dài, bền"),
    ("Càn", "Cấn"): (33, "Thiên Sơn Độn", "遯", "Tránh đi, ẩn dật"),
    ("Chấn", "Càn"): (34, "Lôi Thiên Đại Tráng", "大壯", "Lớn mạnh"),
    ("Ly", "Khôn"): (35, "Hoả Địa Tấn", "晉", "Tiến lên"),
    ("Khôn", "Ly"): (36, "Địa Hoả Minh Di", "明夷", "Sáng bị tổn hại"),
    ("Tốn", "Ly"): (37, "Phong Hoả Gia Nhân", "家人", "Người cùng nhà"),
    ("Ly", "Đoài"): (38, "Hoả Trạch Khuê", "睽", "Ngang trái, ngược nhau"),
    ("Khảm", "Cấn"): (39, "Thuỷ Sơn Kiển", "蹇", "Hiểm trở, gập ghềnh"),
    ("Chấn", "Khảm"): (40, "Lôi Thuỷ Giải", "解", "Mở ra, giải toả"),
    ("Cấn", "Đoài"): (41, "Sơn Trạch Tổn", "損", "Bị tổn hại"),
    ("Tốn", "Chấn"): (42, "Phong Lôi Ích", "益", "Thêm vào, lợi"),
    ("Đoài", "Càn"): (43, "Trạch Thiên Quải", "夬", "Quả quyết, dứt khoát"),
    ("Càn", "Tốn"): (44, "Thiên Phong Cấu", "姤", "Gặp gỡ bất ngờ"),
    ("Đoài", "Khôn"): (45, "Trạch Địa Tuỵ", "萃", "Tụ hợp"),
    ("Khôn", "Tốn"): (46, "Địa Phong Thăng", "升", "Lên, thăng tiến"),
    ("Đoài", "Khảm"): (47, "Trạch Thuỷ Khốn", "困", "Khốn cùng"),
    ("Khảm", "Tốn"): (48, "Thuỷ Phong Tỉnh", "井", "Giếng nước"),
    ("Đoài", "Ly"): (49, "Trạch Hoả Cách", "革", "Biến đổi, cải cách"),
    ("Ly", "Tốn"): (50, "Hoả Phong Đỉnh", "鼎", "Cái vạc, ổn định"),
    ("Chấn", "Chấn"): (51, "Thuần Chấn", "震為雷", "Sấm động, chấn động"),
    ("Cấn", "Cấn"): (52, "Thuần Cấn", "艮為山", "Ngăn lại, dừng"),
    ("Tốn", "Cấn"): (53, "Phong Sơn Tiệm", "漸", "Dần dần"),
    ("Chấn", "Đoài"): (54, "Lôi Trạch Quy Muội", "歸妹", "Gái về nhà chồng"),
    ("Chấn", "Ly"): (55, "Lôi Hoả Phong", "豐", "Lớn thịnh"),
    ("Ly", "Cấn"): (56, "Hoả Sơn Lữ", "旅", "Xa nhà, du khách"),
    ("Tốn", "Tốn"): (57, "Thuần Tốn", "巽為風", "Vào, theo gió"),
    ("Đoài", "Đoài"): (58, "Thuần Đoài", "兌為澤", "Vui, đầm"),
    ("Tốn", "Khảm"): (59, "Phong Thuỷ Hoán", "渙", "Lìa tan"),
    ("Khảm", "Đoài"): (60, "Thuỷ Trạch Tiết", "節", "Hạn chế, tiết chế"),
    ("Tốn", "Đoài"): (61, "Phong Trạch Trung Phu", "中孚", "Lòng có đức tin"),
    ("Chấn", "Cấn"): (62, "Lôi Sơn Tiểu Quá", "小過", "Nhỏ và nhiều"),
    ("Khảm", "Ly"): (63, "Thuỷ Hoả Ký Tế", "既濟", "Việc đã xong"),
    ("Ly", "Khảm"): (64, "Hoả Thuỷ Vị Tế", "未濟", "Việc chưa xong"),
}


# ⭐ Lời quẻ (Quái từ) — chi tiết một số quẻ quan trọng
# Source: Chu Dịch Đại Toàn (Hồ Quảng + Kim Ân Thi đời Minh) qua Ngô Tất Tố
HEXAGRAM_QUAITU = {
    1: "Càn: nguyên, hanh, lợi, trinh. (Khởi đầu, hanh thông, lợi, giữ chính)",
    2: "Khôn: nguyên, hanh, lợi tẫn mã chi trinh. (Khởi đầu hanh thông, lợi như ngựa cái giữ chính)",
    3: "Truân: nguyên, hanh, lợi, trinh. Vật dụng hữu du vãng, lợi kiến hầu.",
    11: "Thái: tiểu vãng đại lai, cát, hanh. (Nhỏ đi lớn đến, tốt, hanh thông)",
    12: "Bĩ: bĩ chi phỉ nhân, bất lợi quân tử trinh. (Bế tắc của kẻ tiểu nhân, bất lợi cho quân tử)",
    21: "Phệ Hạp: hanh, lợi dụng ngục. (Hanh thông, lợi việc xử ngục)",
    28: "Đại Quá: đống nạo, lợi hữu du vãng, hanh. (Cột nhà cong, lợi có nơi tiến, hanh thông)",
    32: "Hằng: hanh, vô cữu, lợi trinh, lợi hữu du vãng. (Hanh thông, không lỗi, lợi giữ chính, lợi có nơi tiến)",
    39: "Kiển: lợi tây nam, bất lợi đông bắc, lợi kiến đại nhân, trinh cát.",
    43: "Quải: dương vu vương đình, phu hiệu hữu lệ, cáo tự ấp, bất lợi tức nhung, lợi hữu du vãng. (Tuyên ở triều, kêu gọi có nguy, nói tự ấp trước, không lợi binh, lợi tiến)",
    51: "Chấn: hanh. Chấn lai khích khích, tiếu ngôn nha nha, chấn kinh bách lý, bất táng chuỷ sưởng.",
    63: "Ký Tế: hanh tiểu, lợi trinh, sơ cát chung loạn. (Đã xong, hanh thông nhỏ, lợi giữ chính, đầu tốt cuối loạn)",
    64: "Vị Tế: hanh, tiểu hồ ngất tế, nhu kỳ vĩ, vô du lợi. (Chưa xong, hanh, hồ con vừa qua đã ướt đuôi, không có lợi)",
}

# ⭐ Hào từ — lời hào cụ thể (cho từng vị trí 1-6)
HEXAGRAM_HAOTU = {
    # Quẻ 32 Hằng — đầy đủ 6 hào
    (32, 1): "Hằng kỳ sơ, tuấn hằng, trinh hung, vô du lợi. (Đầu cứng nhắc, hằng quá độ, chính cũng hung)",
    (32, 2): "Hằng kỳ vị, hối vong. (Bền với chỗ ngồi, hối tan)",
    (32, 3): "Bất hằng kỳ đức, hoặc thừa chi tu, trinh lận. (Không bền đức, có khi thấy nhục)",
    (32, 4): "Điền, vô cầm. (Săn không được chim — không kết quả)",
    (32, 5): "Hằng kỳ đức, trinh, phụ nhân cát, phu tử hung. ★ (Bền đức chính, đàn bà tốt, ĐÀN ÔNG XẤU)",
    (32, 6): "Chấn hằng, hung. (Hằng động loạn, hung)",
    # Quẻ 28 Đại Quá — hào 5 (quan trọng cho biến)
    (28, 5): "Khô dương sinh hoa, lão phụ đắc kỳ sĩ phu, vô cữu vô dự. (Dương khô sinh hoa, đàn bà già có chồng trẻ, không lỗi không khen)",
    # Quẻ 21 Phệ Hạp — hào 1 (quan trọng cho prediction #1)
    (21, 1): "Lý hiệu diệt chỉ, vô cữu. (Mang gông cụt ngón chân, không lỗi)",
    # Quẻ 51 Thuần Chấn — hào 1
    (51, 1): "Chấn lai khích khích, hậu tiếu ngôn nha nha, cát.",
}


def lookup(upper: str, lower: str) -> dict | None:
    """Tra cứu hexagram bằng cặp (upper_que, lower_que).

    Returns:
        {number, vi, zh, short, quaitu, haotu} hoặc None.
    """
    key = (upper, lower)
    if key in HEXAGRAMS_64:
        n, vi, zh, short = HEXAGRAMS_64[key]
        return {
            "number": n, "vi": vi, "zh": zh, "short": short,
            "upper": upper, "lower": lower,
            "quaitu": HEXAGRAM_QUAITU.get(n, ""),
        }
    return None


def hao_lookup(hex_number: int, hao_position: int) -> str:
    """Tra cứu lời hào (1-6 từ dưới lên)."""
    return HEXAGRAM_HAOTU.get((hex_number, hao_position), "")
