"""Concept dictionary cho Kỳ Môn Độn Giáp — UI tooltip + reference.

Theo paradigm Master-Apprentice với tổ sư Lưu Bá Ôn (1311-1375).
Mô tả ngắn (1-2 câu/concept), không nhồi knowledge. Anh thâm nhuần sách
"Bá Ôn Bí Truyền KMDG" sau sẽ enrich qua skill folder hermes_yi/skills/ky-mon/.

Paradigm: 9 cung × 8 môn × 9 tinh × 8 thần là BẢN ĐỒ năng lượng thời-không,
KHÔNG phải fortune dictionary. Mỗi yếu tố = một loại "tính" — đối ứng tâm cảnh người hỏi.
"""

WIKI = {
    # ─── 8 cung Hậu Thiên + Trung cung ───
    "cung": {
        "Khảm": {"zh": "坎", "direction": "Bắc", "ngu_hanh": "Thủy",
                 "desc": "Cung Khảm — nước chảy xuống, hiểm trong êm. Tính: ẩn náu, suy tư, dòng chảy ngầm."},
        "Cấn": {"zh": "艮", "direction": "Đông Bắc", "ngu_hanh": "Thổ",
                "desc": "Cung Cấn — núi đứng yên. Tính: dừng đúng lúc, biết giới hạn, thiền định."},
        "Chấn": {"zh": "震", "direction": "Đông", "ngu_hanh": "Mộc",
                 "desc": "Cung Chấn — sấm động. Tính: khởi động, đột phá, thanh xuân."},
        "Tốn": {"zh": "巽", "direction": "Đông Nam", "ngu_hanh": "Mộc",
                "desc": "Cung Tốn — gió luồn. Tính: thuận theo, len lỏi, lan tỏa."},
        "Ly": {"zh": "離", "direction": "Nam", "ngu_hanh": "Hỏa",
               "desc": "Cung Ly — lửa sáng, phụ thuộc vào chất đốt. Tính: chiếu rọi, văn minh, danh tiếng."},
        "Khôn": {"zh": "坤", "direction": "Tây Nam", "ngu_hanh": "Thổ",
                 "desc": "Cung Khôn — đất rộng nhận hết. Tính: chứa đựng, mẹ, nuôi dưỡng."},
        "Đoài": {"zh": "兌", "direction": "Tây", "ngu_hanh": "Kim",
                 "desc": "Cung Đoài — đầm vui. Tính: vui vẻ, giao đãi, thiếu nữ."},
        "Càn": {"zh": "乾", "direction": "Tây Bắc", "ngu_hanh": "Kim",
                "desc": "Cung Càn — trời cương kiện. Tính: chủ động, lãnh đạo, cha."},
        "Trung": {"zh": "中", "direction": "Trung tâm", "ngu_hanh": "Thổ",
                  "desc": "Trung cung — không có môn (lấy Khôn thay), là trục xoay. Tính: chính giữa, gốc."},
    },

    # ─── 8 môn ───
    "mon": {
        "Hưu": {"zh": "休門", "ngu_hanh": "Thủy", "cat_hung": "cát",
                "desc": "Nghỉ ngơi, dừng việc, ẩn náu. Tốt cho dưỡng sinh, gặp người trên."},
        "Sinh": {"zh": "生門", "ngu_hanh": "Thổ", "cat_hung": "đại cát",
                 "desc": "Khởi sự, sinh sôi, gặt hái. Tốt cho khởi nghiệp, cầu tài, hôn nhân."},
        "Thương": {"zh": "傷門", "ngu_hanh": "Mộc", "cat_hung": "hung",
                   "desc": "Bị tổn thương, va chạm, săn bắt. Đừng đi đường xa, dễ tai nạn. Tốt cho thợ săn, võ tướng."},
        "Đỗ": {"zh": "杜門", "ngu_hanh": "Mộc", "cat_hung": "trung bình",
               "desc": "Đóng kín, ẩn náu, bảo mật. Tốt cho học hành, thiền tĩnh, giấu mình."},
        "Cảnh": {"zh": "景門", "ngu_hanh": "Hỏa", "cat_hung": "trung bình",
                 "desc": "Sáng tỏ, truyền tin, văn thư. Tốt cho thi cử, ký kết, biểu diễn."},
        "Tử": {"zh": "死門", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
               "desc": "Chết, kết thúc, an táng. Đại hung cho khởi sự, tốt cho việc tang."},
        "Kinh": {"zh": "驚門", "ngu_hanh": "Kim", "cat_hung": "hung",
                 "desc": "Giật mình, kinh hãi, kiện tụng. Đừng tranh cãi, cẩn thận tin xấu."},
        "Khai": {"zh": "開門", "ngu_hanh": "Kim", "cat_hung": "đại cát",
                 "desc": "Mở đầu, công khai, hành sự lớn. Tốt cho mọi việc trừ tang lễ."},
    },

    # ─── 9 tinh ───
    "tinh": {
        "Thiên Bồng": {"zh": "天蓬", "ngu_hanh": "Thủy", "cat_hung": "đại hung",
                       "desc": "Đầu hung tinh — Bắc Đẩu thứ nhất. Chủ trộm cướp, dâm dục, mưu kế đen."},
        "Thiên Nhậm": {"zh": "天任", "ngu_hanh": "Thổ", "cat_hung": "cát",
                       "desc": "Bảo trì, đảm nhận. Cát cho việc lâu dài, tích lũy."},
        "Thiên Xung": {"zh": "天沖", "ngu_hanh": "Mộc", "cat_hung": "trung bình",
                       "desc": "Kích phạt, xung đột. Tốt cho người võ, tranh đấu chính nghĩa."},
        "Thiên Phụ": {"zh": "天輔", "ngu_hanh": "Mộc", "cat_hung": "đại cát",
                      "desc": "Phù trợ. Đại cát cho học hành, văn thư, du lịch."},
        "Thiên Cầm": {"zh": "天禽", "ngu_hanh": "Thổ", "cat_hung": "cát",
                      "desc": "Trung tâm, ổn định (luôn ở Trung cung). Đi cùng Trị Phù."},
        "Thiên Tâm": {"zh": "天心", "ngu_hanh": "Kim", "cat_hung": "cát",
                      "desc": "Y dược, lành bệnh. Cát cho sức khỏe, nghiên cứu sâu."},
        "Thiên Trụ": {"zh": "天柱", "ngu_hanh": "Kim", "cat_hung": "trung bình",
                      "desc": "Phòng thủ, cố thủ. Cát cho giữ thành, bất lợi cho công thành."},
        "Thiên Anh": {"zh": "天英", "ngu_hanh": "Hỏa", "cat_hung": "trung bình",
                      "desc": "Chiếu rọi, văn thư, danh tiếng. Hư danh, dễ bị hỏa thiêu."},
        "Thiên Nhuế": {"zh": "天芮", "ngu_hanh": "Thổ", "cat_hung": "đại hung",
                       "desc": "Đầu bệnh tinh. Chủ bệnh tật, tang sự. Tránh đi xa, mua bán quan trọng."},
    },

    # ─── 8 thần ───
    "than": {
        "Trị Phù": {"zh": "值符", "cat_hung": "đại cát",
                    "desc": "Đứng đầu Bát thần — chủ tể vận khí cuộc bàn. Đi đến đâu cát đến đó."},
        "Đằng Xà": {"zh": "螣蛇", "cat_hung": "hung",
                    "desc": "Ảo, biến hoá, mộng mị. Chủ tin đồn, mâu thuẫn nhỏ, lừa đảo."},
        "Thái Âm": {"zh": "太陰", "cat_hung": "cát",
                    "desc": "Kín đáo, mưu sau lưng. Cát cho việc bí mật, không cát cho công khai."},
        "Lục Hợp": {"zh": "六合", "cat_hung": "cát",
                    "desc": "Hòa hợp, kết giao, hôn nhân. Cát cho thương lượng, môi giới."},
        "Câu Trần": {"zh": "勾陳", "cat_hung": "hung",
                     "desc": "Hình thương, kiện tụng, ràng buộc. Chủ việc dây dưa khó dứt."},
        "Chu Tước": {"zh": "朱雀", "cat_hung": "hung",
                     "desc": "Truyền tin (thường tin xấu), thị phi, lời gièm. Cẩn thận khẩu thiệt."},
        "Cửu Địa": {"zh": "九地", "cat_hung": "cát",
                    "desc": "Ẩn náu, mai phục, nuôi dưỡng. Cát cho việc lâu dài, tránh xung đột."},
        "Cửu Thiên": {"zh": "九天", "cat_hung": "đại cát",
                      "desc": "Vươn cao, tiến quân, lập danh. Cát cho hành động mạnh, đi xa."},
    },

    # ─── Cấu trúc cuộc bàn ───
    "structure": {
        "Tam Kỳ": {"zh": "三奇",
                   "desc": "Ất 乙, Bính 丙, Đinh 丁 — 3 thiên can sáng, cát tinh. Ất=Nhật kỳ, Bính=Nguyệt kỳ, Đinh=Tinh kỳ."},
        "Lục Nghi": {"zh": "六儀",
                     "desc": "Mậu 戊, Kỷ 己, Canh 庚, Tân 辛, Nhâm 壬, Quý 癸 — 6 nghi ẩn 6 Giáp tuần thủ."},
        "Dương Cục": {"zh": "陽遁", "range": "Đông Chí → Hạ Chí",
                      "desc": "9 cục từ Đông Chí — số khí dương tăng. Cục số xếp theo tiết khí."},
        "Âm Cục": {"zh": "陰遁", "range": "Hạ Chí → Đông Chí",
                   "desc": "9 cục từ Hạ Chí — số khí âm tăng. Cục số xếp ngược chiều Dương Cục."},
        "Thượng/Trung/Hạ Nguyên": {"zh": "三元",
                                    "desc": "Mỗi tiết khí 15 ngày chia 3 nguyên × 5 ngày. Quyết định cục số cụ thể."},
        "Trị Phù — Trị Sử": {"zh": "值符值使",
                              "desc": "Trị Phù = ngôi sao chủ. Trị Sử = ngôi môn chủ. 2 điểm trục để luận toàn bàn."},
        "Thiên bàn — Địa bàn": {"zh": "天盤地盤",
                                "desc": "Địa bàn = vị trí cố định của Lục Nghi Tam Kỳ. Thiên bàn = vị trí xoay theo Trị Phù."},
        "Tuần thủ — Tuần không": {"zh": "旬首旬空",
                                   "desc": "Tuần thủ = Giáp khởi tuần. Tuần không = 2 chi không thuộc tuần đó (yếu khí)."},
    },

    # ─── Tổ sư ───
    "to_su": {
        "name": "Lưu Bá Ôn",
        "name_zh": "劉伯溫",
        "birth": "1311-07-01",
        "death": "1375-05-16",
        "title": "Tư Mã Hư Tịnh — Cố vấn Minh Thái Tổ Chu Nguyên Chương",
        "work": "Bá Ôn Bí Truyền Kỳ Môn Độn Giáp (truyền thuyết)",
        "lineage": "Cửu Thiên Huyền Nữ → Hoàng Đế → Phong Hậu → Khương Tử Nha → Trương Lương → Gia Cát Lượng → Lưu Bá Ôn",
        "paradigm": "Hệ thống KMDG cận đại stable + procedural. Phù hợp Author-Worldview-First.",
    },
}


def get_concept(category: str, name: str) -> dict | None:
    """Tra cứu 1 khái niệm cụ thể."""
    return WIKI.get(category, {}).get(name)


def list_categories() -> list[str]:
    """List các category trong wiki."""
    return list(WIKI.keys())
