"""TQ ↔ Việt mapping cho engine Kỳ Môn Độn Giáp.

Tổ sư: Lưu Bá Ôn (1311-1375) — "Bá Ôn Bí Truyền Kỳ Môn Độn Giáp".

Paradigm: ĐỌC ĐỒNG DẠNG, không predict (theo Iron Rule #4 + #6).
Bố cục 9 cung × 8 môn × 9 tinh × 8 thần = bản đồ năng lượng thời-không
tại thời điểm cụ thể, phản chiếu cấu trúc vũ trụ. Không phải fortune dictionary.
"""

# 8 cung Hậu Thiên + Trung cung
CUNG_VN = {
    "坎": "Khảm",     # Bắc, Thủy
    "艮": "Cấn",      # Đông Bắc, Thổ
    "震": "Chấn",     # Đông, Mộc
    "巽": "Tốn",      # Đông Nam, Mộc
    "離": "Ly",       # Nam, Hỏa
    "坤": "Khôn",     # Tây Nam, Thổ
    "兌": "Đoài",     # Tây, Kim
    "乾": "Càn",      # Tây Bắc, Kim
    "中": "Trung",    # Trung tâm, Thổ
}

CUNG_DIRECTION = {
    "坎": "Bắc",
    "艮": "Đông Bắc",
    "震": "Đông",
    "巽": "Đông Nam",
    "離": "Nam",
    "坤": "Tây Nam",
    "兌": "Tây",
    "乾": "Tây Bắc",
    "中": "Trung tâm",
}

CUNG_NGU_HANH = {
    "坎": "Thủy",
    "艮": "Thổ",
    "震": "Mộc",
    "巽": "Mộc",
    "離": "Hỏa",
    "坤": "Thổ",
    "兌": "Kim",
    "乾": "Kim",
    "中": "Thổ",
}

# 8 môn
MON_VN = {
    "休": "Hưu",      # Thủy, nghỉ ngơi (吉)
    "生": "Sinh",     # Thổ, khởi sự (đại cát)
    "傷": "Thương",   # Mộc, bị tổn thương
    "杜": "Đỗ",       # Mộc, đóng kín, bảo mật
    "景": "Cảnh",     # Hỏa, sáng tỏ, truyền tin
    "死": "Tử",       # Thổ, kết thúc
    "驚": "Kinh",     # Kim, giật mình, hoang mang
    "開": "Khai",     # Kim, mở đầu (đại cát)
}

MON_NGU_HANH = {
    "休": "Thủy", "生": "Thổ", "傷": "Mộc", "杜": "Mộc",
    "景": "Hỏa", "死": "Thổ", "驚": "Kim", "開": "Kim",
}

# 9 tinh (Cửu tinh)
TINH_VN = {
    "蓬": "Thiên Bồng",    # Thủy, đầu hung tinh
    "任": "Thiên Nhậm",    # Thổ, bảo trì
    "沖": "Thiên Xung",    # Mộc, kích phạt
    "輔": "Thiên Phụ",     # Mộc, phù trợ (đại cát)
    "禽": "Thiên Cầm",     # Thổ, trung tâm, ổn
    "心": "Thiên Tâm",     # Kim, y dược (cát)
    "柱": "Thiên Trụ",     # Kim, phòng thủ
    "英": "Thiên Anh",     # Hỏa, chiếu rọi, văn thư
    "芮": "Thiên Nhuế",    # Thổ, bệnh tật (hung)
}

TINH_NGU_HANH = {
    "蓬": "Thủy", "任": "Thổ", "沖": "Mộc", "輔": "Mộc",
    "禽": "Thổ", "心": "Kim", "柱": "Kim", "英": "Hỏa", "芮": "Thổ",
}

# 8 thần (Bát thần — theo phái Lưu Bá Ôn)
THAN_VN = {
    "符": "Trị Phù",      # 值符, đứng đầu (đại cát)
    "蛇": "Đằng Xà",      # 螣蛇, ảo biến
    "陰": "Thái Âm",      # 太陰, kín mưu (cát)
    "合": "Lục Hợp",      # 六合, hòa hợp (cát)
    "勾": "Câu Trần",     # 勾陳, hình thương (hung)
    "雀": "Chu Tước",     # 朱雀, truyền tin, gian (hung)
    "地": "Cửu Địa",      # 九地, ẩn náu (cát)
    "天": "Cửu Thiên",    # 九天, vươn cao (đại cát)
}

# 10 thiên can
CAN_VN = {
    "甲": "Giáp", "乙": "Ất", "丙": "Bính", "丁": "Đinh", "戊": "Mậu",
    "己": "Kỷ", "庚": "Canh", "辛": "Tân", "壬": "Nhâm", "癸": "Quý",
}

CAN_NGU_HANH = {
    "甲": "Mộc", "乙": "Mộc", "丙": "Hỏa", "丁": "Hỏa", "戊": "Thổ",
    "己": "Thổ", "庚": "Kim", "辛": "Kim", "壬": "Thủy", "癸": "Thủy",
}

# 12 địa chi
CHI_VN = {
    "子": "Tý", "丑": "Sửu", "寅": "Dần", "卯": "Mão", "辰": "Thìn",
    "巳": "Tỵ", "午": "Ngọ", "未": "Mùi", "申": "Thân", "酉": "Dậu",
    "戌": "Tuất", "亥": "Hợi",
}

# 24 tiết khí
TIET_KHI_VN = {
    "立春": "Lập Xuân", "雨水": "Vũ Thủy", "驚蟄": "Kinh Trập", "春分": "Xuân Phân",
    "清明": "Thanh Minh", "穀雨": "Cốc Vũ", "立夏": "Lập Hạ", "小滿": "Tiểu Mãn",
    "芒種": "Mang Chủng", "夏至": "Hạ Chí", "小暑": "Tiểu Thử", "大暑": "Đại Thử",
    "立秋": "Lập Thu", "處暑": "Xử Thử", "白露": "Bạch Lộ", "秋分": "Thu Phân",
    "寒露": "Hàn Lộ", "霜降": "Sương Giáng", "立冬": "Lập Đông", "小雪": "Tiểu Tuyết",
    "大雪": "Đại Tuyết", "冬至": "Đông Chí", "小寒": "Tiểu Hàn", "大寒": "Đại Hàn",
}

# Tam kỳ + Lục nghi (3 kỳ 6 nghi = 9 thiên can KMDG, ẩn 甲 Giáp)
# Source: Đàm Liên Chương I (pages 25-27) — "Tam kỳ Lục nghi"
TAM_KY = {"乙": "Ất kỳ", "丙": "Bính kỳ", "丁": "Đinh kỳ"}
LUC_NGHI = {
    "戊": "Mậu nghi", "己": "Kỷ nghi", "庚": "Canh nghi",
    "辛": "Tân nghi", "壬": "Nhâm nghi", "癸": "Quý nghi",
}

# Tên đầy đủ Tam Kỳ (3 kỳ = 3 thiên thể sáng)
TAM_KY_FULL_NAME = {
    "乙": {"vn": "Nhật kỳ", "zh": "日奇", "thien_the": "Mặt trời"},
    "丙": {"vn": "Nguyệt kỳ", "zh": "月奇", "thien_the": "Mặt trăng"},
    "丁": {"vn": "Tinh kỳ", "zh": "星奇", "thien_the": "Sao"},
}

# Mapping Lục Nghi ↔ Giáp ẩn (mỗi Lục Nghi ẩn 1 Giáp tuần)
# Source: Đàm Liên Chương I — "Lục Nghi thường đặt Giáp đứng trước các can khác"
LUC_NGHI_GIAP_MAPPING = {
    "戊": {"giap": "甲子", "giap_vn": "Giáp Tý", "tuan": "Giáp Tý tuần (戊)"},
    "己": {"giap": "甲戌", "giap_vn": "Giáp Tuất", "tuan": "Giáp Tuất tuần (己)"},
    "庚": {"giap": "甲申", "giap_vn": "Giáp Thân", "tuan": "Giáp Thân tuần (庚)"},
    "辛": {"giap": "甲午", "giap_vn": "Giáp Ngọ", "tuan": "Giáp Ngọ tuần (辛)"},
    "壬": {"giap": "甲辰", "giap_vn": "Giáp Thìn", "tuan": "Giáp Thìn tuần (壬)"},
    "癸": {"giap": "甲寅", "giap_vn": "Giáp Dần", "tuan": "Giáp Dần tuần (癸)"},
}

# Cửu tinh — tên thay thế theo SỐ + MÀU (Huyền Không Phi Tinh hệ + KMDG)
# Source: Đàm Liên Chương I (pages 21-25) — "9 sao: Nhất bạch, Nhị hắc, ..."
# Mapping song song với 9 tinh KMDG (Thiên Bồng etc).
CUU_TINH_NUMBER_NAME = {
    1: {"vn": "Nhất bạch", "zh": "一白", "color": "trắng", "kmdg_tinh": "Thiên Bồng"},
    2: {"vn": "Nhị hắc", "zh": "二黑", "color": "đen", "kmdg_tinh": "Thiên Nhuế"},
    3: {"vn": "Tam bích", "zh": "三碧", "color": "lục", "kmdg_tinh": "Thiên Xung"},
    4: {"vn": "Tứ lục", "zh": "四綠", "color": "xanh lá", "kmdg_tinh": "Thiên Phụ"},
    5: {"vn": "Ngũ hoàng", "zh": "五黃", "color": "vàng", "kmdg_tinh": "Thiên Cầm"},
    6: {"vn": "Lục bạch", "zh": "六白", "color": "trắng", "kmdg_tinh": "Thiên Tâm"},
    7: {"vn": "Thất xích", "zh": "七赤", "color": "đỏ", "kmdg_tinh": "Thiên Trụ"},
    8: {"vn": "Bát bạch", "zh": "八白", "color": "trắng", "kmdg_tinh": "Thiên Nhậm"},
    9: {"vn": "Cửu tử", "zh": "九紫", "color": "tím", "kmdg_tinh": "Thiên Anh"},
}

# Phân loại 12 địa chi theo Tam Hợp / Tứ chính
# Source: Đàm Liên Chương I — dùng để xác định Thượng/Trung/Hạ Nguyên (nguyệt gia)
TU_MANH = ["寅", "申", "巳", "亥"]   # Tứ Mạnh: Dần Thân Tỵ Hợi
TU_TRONG = ["子", "午", "卯", "酉"]  # Tứ Trọng: Tý Ngọ Mão Dậu
TU_QUY = ["辰", "戌", "丑", "未"]    # Tứ Quý: Thìn Tuất Sửu Mùi

# Nguyên xác định cho Kỳ Môn Nguyệt Gia (5 năm = 1 nguyên, 60 tháng)
# Source: Đàm Liên Chương I (page 22-23)
NGUYET_GIA_NGUYEN_RULE = {
    "Thượng Nguyên": {
        "nien_chi_class": "Tứ Mạnh",
        "nien_chi_list": TU_MANH,
        "starting_cung": "Khảm số 1",
        "note": "Niên can Giáp/Kỷ + niên chi Tứ Mạnh → năm Giáp Tý của Thượng Nguyên",
    },
    "Trung Nguyên": {
        "nien_chi_class": "Tứ Trọng",
        "nien_chi_list": TU_TRONG,
        "starting_cung": "Đoài số 7",
        "note": "Niên chi Tứ Trọng → năm Giáp Tý của Trung Nguyên",
    },
    "Hạ Nguyên": {
        "nien_chi_class": "Tứ Quý",
        "nien_chi_list": TU_QUY,
        "starting_cung": "Tốn số 4",
        "note": "Niên chi Tứ Quý → năm Giáp Tý của Hạ Nguyên (đều là âm độn)",
    },
}

# Quy luật Dương độn vs Âm độn — xếp 9 thiên can theo chiều
# Source: Đàm Liên Chương I (hình 5, 6, 7) — bảng Dương độn + Âm độn
# 25+ Cách Cục KMDG canon (Đàm Liên Chương I phần V — pages 43-50)
# Mỗi cách cục có:
#   - vn / zh: tên Việt / Hán
#   - loai: "cat" | "hung"
#   - tom: tóm tắt 1 câu
#   - dieu_kien: điều kiện text (cho display)
#   - usage: nên làm gì
#   - check: optional function name cho auto-detection (None = browse-only)
CACH_CUC_CANON = {
    # ──── CÁT CÁCH ────
    "Thanh Long Hồi Thủ": {
        "zh": "青龍回首", "loai": "đại cát",
        "tom": "Trăm sự bình an",
        "dieu_kien": "Thiên Bàn Lục Giáp tại vị trí Trực Phù, Địa Bàn số Bính",
        "usage": "Mọi sự đều bình an, tốt cho khởi sự lớn",
        "check": "thanh_long_hoi_thu",
    },
    "Phi Điểu Trật Huyệt": {
        "zh": "飛鳥跌穴", "loai": "đại cát",
        "tom": "Trăm sự thuận lợi",
        "dieu_kien": "Thiên Bàn số Bính, Địa Bàn Lục Giáp (cùng cung)",
        "usage": "Mọi việc dễ thành công",
        "check": "phi_dieu_trat_huyet",
    },
    "Thiên Độn": {
        "zh": "天遁", "loai": "đại cát",
        "tom": "Mọi sự thịnh vượng — chiến trận, học tập, cầu quan, trừ ác, hôn nhân, kinh doanh",
        "dieu_kien": "Thiên Bàn số Bính + Trung Bàn Sinh Môn (hoặc Khai Môn) + Địa Bàn số Đinh (theo Đàm Liên page 45)",
        "usage": "Mọi sự thịnh vượng. Thuận lợi trong chiến trận, học tập, cầu quan, trừ ác, hôn nhân, kinh doanh",
        "check": None,
    },
    "Địa Độn": {
        "zh": "地遁", "loai": "cát",
        "tom": "Cố thủ dưỡng binh, tu sửa, cầu tiền tài",
        "dieu_kien": "Thiên Bàn số Ất + Trung Bàn Khai Môn + Địa Bàn Giáp Mậu Kỷ",
        "usage": "Cố thủ dưỡng binh, tu sửa, cầu tiền tài",
        "check": None,
    },
    "Nhân Độn": {
        "zh": "人遁", "loai": "cát",
        "tom": "Ẩn giấu, tập kích, thám thính, cưới gả",
        "dieu_kien": "Thiên Bàn số Đinh + Trung Bàn Hưu Môn + Thần Bàn Thái Âm",
        "usage": "Ẩn giấu, tập kích, thám thính, gặp người quyền quý, cưới gả, giao dịch",
        "check": None,
    },
    "Thần Độn": {
        "zh": "神遁", "loai": "đại cát",
        "tom": "Đánh điểm yếu, đánh nhanh, mở đường",
        "dieu_kien": "Thiên Bàn số Đinh + Trung Bàn Sinh Môn + Thần Bàn Cửu Thiên",
        "usage": "Đánh điểm yếu, đánh nhanh, mở đường, ngăn sông, tạo tượng",
        "check": None,
    },
    "Nhị Cơ đắc Sử": {
        "zh": "二奇得使", "loai": "cát",
        "tom": "Cơ + Sử kết hợp",
        "dieu_kien": "Thiên Bàn Ất + Địa Bàn Giáp Tuất/Ngọ (Ất Cơ đắc Sử); Thiên Bàn Đinh + Địa Bàn Giáp Thìn/Dần (Đinh Cơ đắc Sử)",
        "usage": "Cát cho công việc — KỴ ma chay",
        "check": None,
    },
    "Ngọc Nữ Thủ Môn": {
        "zh": "玉女守門", "loai": "cát",
        "tom": "Lợi hội hè, đình đám, việc riêng + việc chung",
        "dieu_kien": "Trung Bàn Trực Sử + Địa Bàn Đinh Kỳ",
        "usage": "Hội hè, đình đám, việc riêng tư hay việc chung",
        "check": None,
    },
    "Cự Trá": {
        "zh": "巨詐", "loai": "cát",
        "tom": "Ban ơn, ẩn náu, xuất quân, chiêu hàng",
        "dieu_kien": "Thiên Bàn tam kỳ (Ất/Bính/Đinh) + Trung Bàn 3 cát môn (Khai/Hưu/Sinh) + Thần Bàn Cửu Địa",
        "usage": "Ban ơn, ẩn náu, xuất quân, chiêu hàng",
        "check": None,
    },
    "Vật Giả": {
        "zh": "物假", "loai": "cát",
        "tom": "Mai táng, cất chứa, giao dịch làm ăn",
        "dieu_kien": "Thiên Bàn Đinh/Kỷ/Quý + Trung Bàn Thương Môn + Thần Bàn Cửu Địa",
        "usage": "Mai táng, cất chứa, giao dịch làm ăn",
        "check": None,
    },
    "Nhân Giả": {
        "zh": "人假", "loai": "cát",
        "tom": "Bắt bớ, tù đày",
        "dieu_kien": "Thiên Bàn Lục Nhậm + Trung Bàn Kinh Môn + Thần Bàn Cửu Thiên",
        "usage": "Bắt bớ, tù đày",
        "check": None,
    },
    "Quy Giả": {
        "zh": "鬼假", "loai": "cát",
        "tom": "Sửa mộ, đi săn",
        "dieu_kien": "Thiên Bàn Đinh/Kỷ/Quý + Trung Bàn Tử Môn + Thần Bàn Cửu Địa",
        "usage": "Sửa mộ, đi săn",
        "check": None,
    },
    "Tam Cơ Thăng Điện": {
        "zh": "三奇升殿", "loai": "đại cát",
        "tom": "VẠN SỰ TỐT LÀNH — cực kì tốt (nhưng kị gặp Mộ bức)",
        "dieu_kien": "Thiên Bàn số Ất đến Chấn, số Bính đến Ly, số Đinh đến Đoài",
        "usage": "Xuất binh, đi xa, tu tạo, kết hôn, thăng quan, di đời, cầu tài, mai táng — vạn sự đều tốt lành",
        "check": "tam_co_thang_dien",
    },
    "Tam Kỳ đắc Lộc": {
        "zh": "三奇得祿", "loai": "cát",
        "tom": "Trăm sự như ý — thăng quan, cầu tài",
        "dieu_kien": "Số Ất đến Chấn; số Bính đến Tốn; số Đinh đến Ly (vị trí sao Lộc của tam kỳ)",
        "usage": "Thăng quan, cầu tài",
        "check": None,
    },
    "Hoán Đi": {
        "zh": "煥移", "loai": "cát",
        "tom": "Trăm sự đều thích hợp",
        "dieu_kien": "Thiên Bàn tam kỳ + Địa Bàn Lục Giáp Trực Phù",
        "usage": "Trăm sự đều thích hợp",
        "check": None,
    },
    "Tương Tá": {
        "zh": "相佐", "loai": "cát",
        "tom": "Trăm sự thuận lợi",
        "dieu_kien": "Thiên Bàn Lục Giáp Trực Phù + Địa Bàn tam kỳ (Ất/Bính/Đinh)",
        "usage": "Trăm sự thuận lợi",
        "check": None,
    },
    "Yêu Vận Xương Khí": {
        "zh": "妖運昌氣", "loai": "cát",
        "tom": "Mưu sự đều thành",
        "dieu_kien": "Thiên Bàn Cơ Đinh + Địa Bàn Cơ Ất + gặp cát môn",
        "usage": "Mưu sự đều thành",
        "check": None,
    },
    "Hoa Nghĩa": {
        "zh": "和義", "loai": "cát",
        "tom": "Sinh khắc Môn ↔ Cung thuận: Hoà (Môn sinh Cung) / Nghĩa (Cung sinh Môn)",
        "dieu_kien": "Môn sinh Cung = Hoà 和; Cung sinh Môn = Nghĩa 義 (tốt hơn Hoà)",
        "usage": "Gặp cát môn + Hoà/Nghĩa → làm việc gì cũng tốt",
        "check": "hoa_nghia",
    },

    # ──── HUNG CÁCH (mở rộng) ────
    "Huỳnh Nhập Thái Bạch": {
        "zh": "熒入太白", "loai": "hung",
        "tom": "Quân địch lui — không nên truy kích",
        "dieu_kien": "Thiên Bàn Cơ Bính + Địa Bàn Lục Canh",
        "usage": "Tượng địch lui quân — nhưng KHÔNG truy kích",
        "check": None,
    },
    "Phi Cung Cách": {
        "zh": "飛宮格", "loai": "hung",
        "tom": "Phòng thủ chờ thời cơ",
        "dieu_kien": "Thiên Bàn Lục Giáp Trực Phù + Địa Bàn Lục Canh",
        "usage": "Chủ + khách đều bất lợi, bại trận. PHÒNG THỦ chờ thời cơ",
        "check": None,
    },
    "Phục Cung Cách": {
        "zh": "伏宮格", "loai": "đại hung",
        "tom": "Xe gãy ngựa chết",
        "dieu_kien": "Thiên Bàn Lục Canh + Địa Bàn Trực Phù (= Nguyệt Cách context khác)",
        "usage": "Chủ + Khách đều bất lợi, xe gãy, ngựa chết, trăm việc bất lợi",
        "check": None,
    },
    "Phi Can Cách": {
        "zh": "飛干格", "loai": "hung",
        "tom": "Chủ khách đều thương",
        "dieu_kien": "Thiên Bàn Nhật Can + Địa Bàn Lục Canh",
        "usage": "Chủ và khách đều thương, xuất hành gặp họa",
        "check": None,
    },
    "Đại Cách": {
        "zh": "大格", "loai": "hung",
        "tom": "Trăm sự bất lợi NHƯNG bắt tù binh thì được",
        "dieu_kien": "Thiên Bàn Lục Canh + Địa Bàn Lục Quý",
        "usage": "Xuất hành: xe hỏng ngựa ốm, không đi xa được. PARADOX: BẮT TÙ BINH thì được",
        "check": None,
    },
    "Tiểu Cách": {
        "zh": "小格", "loai": "hung",
        "tom": "ĐẠI KỴ xuất binh",
        "dieu_kien": "Thiên Bàn Lục Canh + Địa Bàn Lục Nhâm",
        "usage": "Trăm sự bất lợi, đại kị đưa quân xuất hành",
        "check": None,
    },
    "Niên Cách": {
        "zh": "年格", "loai": "hung",
        "tom": "Thiên Bàn Canh đến Niên Can",
        "dieu_kien": "Thiên Bàn Lục Canh + Địa Bàn Niên Can (cần state năm)",
        "usage": "Tránh dùng năm có Canh xung Niên Can",
        "check": None,
    },
    "Nguyệt Cách": {
        "zh": "月格", "loai": "hung",
        "tom": "Thiên Bàn Canh đến Nguyệt Can",
        "dieu_kien": "Thiên Bàn Lục Canh + Địa Bàn Nguyệt Can",
        "usage": "Tránh dùng tháng có Canh xung Nguyệt Can",
        "check": None,
    },
    "Bột Cách": {
        "zh": "悖格", "loai": "hung",
        "tom": "Lợi chủ, cố thủ",
        "dieu_kien": "Thiên Bàn Bính + Địa Bàn số dương (năm/tháng/ngày/giờ)",
        "usage": "Lợi cho ngôi chủ, nên cố thủ. Nếu là khách KHÔNG nên làm loạn",
        "check": None,
    },
    "Trực Phù Phản Ngâm": {
        "zh": "值符反吟", "loai": "đại hung",
        "tom": "Trăm việc đều không hợp",
        "dieu_kien": "Lục Giáp Trực Phù: Thiên ↔ Địa Bàn đối xung (VD Giáp Tý Thiên + Giáp Ngọ Địa, Giáp Tuất Thiên + Giáp Thìn Địa)",
        "usage": "Trăm việc đều không hợp",
        "check": None,
    },
    "Ngũ Bất Ngộ": {
        "zh": "五不遇", "loai": "đại hung",
        "tom": "MỌI VIỆC HUNG — DÙ ĐẮC CƠ ĐẮC MÔN cũng không dùng",
        "dieu_kien": "Can GIỜ KHẮC Can NGÀY: Canh Ngọ/Giáp; Tân Tỵ/Ất; Nhâm Thìn/Bính; Quý Mão/Đinh; Giáp Dần/Mậu; Ất Sửu/Kỷ; Bính Tý/Canh; Đinh Dậu/Tân; Mậu Thân/Nhâm; Kỷ Tỵ/Quý",
        "usage": "Mọi việc đều hung, DÙ ĐẮC CƠ ĐẮC MÔN cũng KHÔNG dùng được",
        "check": "ngu_bat_ngo",
    },
    "Thiên Phá": {
        "zh": "天破", "loai": "hung",
        "tom": "Giờ kỵ theo ngày",
        "dieu_kien": "Ngày Giáp/Kỷ kỵ giờ Kỷ Tỵ; Ngày Ất/Canh kỵ giờ Giáp Thân; Ngày Bính/Tân kỵ giờ Giáp Ngọ; Ngày Đinh/Nhâm kỵ giờ Giáp Thìn; Ngày Mậu/Quý kỵ giờ Giáp Dần",
        "usage": "Tránh các giờ kỵ trên cho khởi sự",
        "check": None,
    },
    "Quỷ Độn": {
        "zh": "鬼遁", "loai": "cát",
        "tom": "Đánh lén, đánh nhanh",
        "dieu_kien": "Thiên Bàn Ất + Trung Bàn Đỗ Môn + Thần Bàn Cửu Địa",
        "usage": "Đánh lén, mai phục bất ngờ",
        "check": None,
    },
    "Phong Độn": {
        "zh": "風遁", "loai": "cát",
        "tom": "Phục binh, hoả công",
        "dieu_kien": "Thiên Bàn Ất hoặc Kỷ + Trung Bàn Khai/Hưu/Sinh + Địa Bàn cung 4 Tốn",
        "usage": "Phục binh, dùng hỏa công",
        "check": None,
    },
    "Vân Độn": {
        "zh": "雲遁", "loai": "cát",
        "tom": "Cầu mưa, mai phục",
        "dieu_kien": "Thiên Bàn Ất + Trung Bàn Khai/Hưu/Sinh + Địa Bàn Giáp Ngọ Tân",
        "usage": "Cầu mưa, phục kích, lập doanh trại",
        "check": None,
    },
    "Long Độn": {
        "zh": "龍遁", "loai": "cát",
        "tom": "Cầu mưa, thuỷ chiến",
        "dieu_kien": "Thiên Bàn Ất + Trung Bàn Khai/Hưu/Sinh + Địa Bàn cung 1 Khảm hoặc Giáp Dần Quý",
        "usage": "Cầu mưa, mở đường, săn bắn, thuỷ chiến",
        "check": None,
    },
    "Hổ Độn": {
        "zh": "虎遁", "loai": "cát",
        "tom": "Lập trại, chiêu hàng",
        "dieu_kien": "Thiên Bàn Ất + Trung Bàn Hưu/Sinh + Địa Bàn cung 8 Cấn hoặc Giáp Ngọ Tân",
        "usage": "Lập doanh trại, chiêu hàng",
        "check": None,
    },
    "Trùng Trá": {
        "zh": "重詐", "loai": "cát",
        "tom": "Cầu tài, gặp người quyền quý, mai phục",
        "dieu_kien": "Thiên Bàn Tam Kỳ (Ất/Bính/Đinh) + Trung Bàn Khai/Hưu/Sinh + Thần Bàn Cửu Địa + Lục Hợp",
        "usage": "Cầu tài, nhận người, gặp quan, xuất quân",
        "check": None,
    },
    "Hưu Trá": {
        "zh": "休詐", "loai": "cát",
        "tom": "Uống thuốc, trị bệnh",
        "dieu_kien": "Thiên Bàn Tam Kỳ + Địa Bàn 3 cát môn + Thần Bàn Lục Hợp",
        "usage": "Uống thuốc, trị bệnh",
        "check": None,
    },
    "Đại Giả": {
        "zh": "大假", "loai": "cát",
        "tom": "Gặp người quyền quý, dâng kế",
        "dieu_kien": "Thiên Bàn Tam Kỳ + Trung Bàn Cảnh môn + Thần Bàn Cửu Thiên",
        "usage": "Gặp quý nhân, dâng kế sách, phát lệnh, kết giao ước",
        "check": None,
    },
    "Địa Giả": {
        "zh": "地假", "loai": "cát",
        "tom": "Ẩn mình, lánh nạn",
        "dieu_kien": "Thiên Bàn Tam Kỳ + Trung Bàn Đỗ môn + Thần Bàn Cửu Địa",
        "usage": "Ẩn mình lánh nạn, thăm dò, điều tra",
        "check": None,
    },
    "Giao Thái": {
        "zh": "交泰", "loai": "cát",
        "tom": "Đại lợi",
        "dieu_kien": "Thiên Bàn Ất Kỳ + Địa Bàn Đinh Kỳ (hoặc Thiên Bàn Đinh + Địa Bàn Bính)",
        "usage": "Đại lợi, cát môn",
        "check": "giao_thai",
    },

    # ──── HUNG CÁCH ────
    "Thanh Long Đào Tẩu": {
        "zh": "青龍逃走", "loai": "đại hung",
        "tom": "Bại trận, bỏ trốn",
        "dieu_kien": "Thiên Bàn Ất, Địa Bàn Lục Tân (cùng cung)",
        "usage": "Không dấy binh, tướng sĩ bỏ trốn, mất của",
        "check": "thanh_long_dao_tau",
    },
    "Bạch Hổ Xương Cuồng": {
        "zh": "白虎猖狂", "loai": "đại hung",
        "tom": "Đại hung",
        "dieu_kien": "Thiên Bàn Tân, Địa Bàn Ất (cùng cung)",
        "usage": "Không dấy binh, hao tài, thị phi. Đi thuyền + kết hôn + tu tạo đều ĐẠI HUNG",
        "check": "bach_ho_xuong_cuong",
    },
    "Đằng Xà Yêu Dược": {
        "zh": "螣蛇妖矯", "loai": "hung",
        "tom": "Kiện tụng",
        "dieu_kien": "Thiên Bàn Lục Quý, Địa Bàn Cơ Đinh (cùng cung)",
        "usage": "Vạn sự không tốt, dính kiện tụng",
        "check": "dang_xa_yeu_duoc",
    },
    "Chu Tước Đầu Giang": {
        "zh": "朱雀投江", "loai": "hung",
        "tom": "Không thuận đi xa, lộ thông tin",
        "dieu_kien": "Thiên Bàn Cơ Đinh, Địa Bàn Lục Quý (cùng cung)",
        "usage": "Không đi xa, không thăng quan, không hôn nhân. Thủy tai, lộ thông tin",
        "check": "chu_tuoc_dau_giang",
    },
    "Thái Bạch Nhập Huỳnh": {
        "zh": "太白入熒", "loai": "hung",
        "tom": "Phục binh cố thủ",
        "dieu_kien": "Thiên Bàn Lục Canh, Địa Bàn Cơ Bính (cùng cung)",
        "usage": "Phục binh cố thủ, không tấn công",
        "check": None,
    },
    "Phục Can Cách": {
        "zh": "伏干格", "loai": "đại hung",
        "tom": "Bị bắt, tai hung",
        "dieu_kien": "Thiên Bàn Lục Canh, Địa Bàn nhật can",
        "usage": "Chủ và khách đều bị thương. Tham chiến bị bắt",
        "check": None,
    },
    "Tam Kỳ Nhập Mộ": {
        "zh": "三奇入墓", "loai": "hung",
        "tom": "Mưu sự không thành",
        "dieu_kien": "Ất đến cung 6 Càn (mộ); Đinh đến cung 8 Cấn (mộ); hoặc Bính/Đinh đến cung 6 Càn",
        "usage": "Mọi việc không tốt, mưu sự không thành",
        "check": None,
    },
    "Lục Nghi Kích Hình": {
        "zh": "六儀擊刑", "loai": "đại hung",
        "tom": "Cực hung",
        "dieu_kien": "Giáp Tý→cung 3 Chấn; Giáp Tuất→cung 2 Khôn; Giáp Thân→cung 8 Cấn; Giáp Ngọ→cung 9 Ly; Giáp Thìn→cung 4 Tốn; Giáp Dần→cung 4 Tốn",
        "usage": "ĐẠI KỴ xuất hành, không xây doanh trại",
        "check": None,
    },
    "Hình Cách": {
        "zh": "刑格", "loai": "đại hung",
        "tom": "Khởi binh cực hung",
        "dieu_kien": "Thiên Bàn Lục Canh, Địa Bàn Lục Kỷ (cùng cung)",
        "usage": "Khởi binh cực hung, xuất hành nhiều khó khăn",
        "check": "hinh_cach",
    },
    "Phục Ngâm (Tinh/Môn)": {
        "zh": "伏吟", "loai": "hung",
        "tom": "Bàn không động",
        "dieu_kien": "Sao Thiên Bàn nằm chính cung chưa động (gọi 'sao Phục Ngâm'); Môn ở chính cung chưa động (gọi 'cửa Phục Ngâm')",
        "usage": "Rất xấu. Dù đắc cát môn cũng không nên dùng",
        "check": None,
    },
    "Phản Ngâm (Tinh/Môn)": {
        "zh": "反吟", "loai": "hung",
        "tom": "Bàn đối xung",
        "dieu_kien": "Tinh Thiên Bàn đối xung với Tinh Địa Bàn (cùng cung)",
        "usage": "Rất xấu, gấp đôi áp lực",
        "check": None,
    },
    "Môn Cung Chế Bức": {
        "zh": "門宮克剝", "loai": "hung",
        "tom": "Môn khắc cung hoặc cung khắc môn",
        "dieu_kien": "Hưu môn→cung 9 Ly (Thủy bị Hỏa); Sinh/Tử→cung 1 Khảm; Thương/Đỗ→cung 2 Khôn/8 Cấn; Khai/Kinh→cung 3 Chấn/4 Tốn",
        "usage": "Môn bị suy giảm cát khí, hoặc tăng hung",
        "check": "mon_cung_che_buc",
    },
}

DUONG_AM_DON_RULE = {
    "Dương độn 陽遁": {
        "chieu": "thuận chiều (theo cung số 1→9)",
        "tiet_khi_range": "Đông Chí → Hạ Chí (6 tháng dương khí tăng)",
        "cuc_so_range": "1 đến 9 (9 cục)",
        "vd_part_1": "Giáp Tý Mậu → cung Khảm số 1, Giáp Tuất Kỷ → cung Khôn số 2, ... Ất Kỳ → cung Ly số 9",
    },
    "Âm độn 陰遁": {
        "chieu": "ngược chiều (theo cung số 9→1)",
        "tiet_khi_range": "Hạ Chí → Đông Chí (6 tháng âm khí tăng)",
        "cuc_so_range": "1 đến 9 (9 cục)",
        "vd_part_1": "Giáp Tý Mậu → cung Ly số 9, Giáp Tuất Kỷ → cung Cấn số 8, ... Ất Kỳ → cung Khảm số 1",
    },
}

# Cát/hung tổng quát của môn, tinh, thần (tham khảo cổ điển — không tuyệt đối)
MON_CAT_HUNG = {
    "休": "cát", "生": "đại cát", "傷": "hung", "杜": "trung bình",
    "景": "trung bình", "死": "đại hung", "驚": "hung", "開": "đại cát",
}
# Corrected per Đàm Liên Chương I phần IV (pages 39-40):
# - 5 cát tinh: Phụ Cầm Tâm (đại cát) + Xung Nhậm (tiểu cát)
# - 4 hung tinh: Bồng Nhuế (đại hung) + Trụ Anh (tiểu hung)
TINH_CAT_HUNG = {
    "蓬": "đại hung", "任": "cát", "沖": "cát", "輔": "đại cát",
    "禽": "đại cát", "心": "đại cát", "柱": "hung", "英": "hung", "芮": "đại hung",
}
THAN_CAT_HUNG = {
    "符": "đại cát", "蛇": "hung", "陰": "cát", "合": "cát",
    "勾": "hung", "雀": "hung", "地": "cát", "天": "đại cát",
}
