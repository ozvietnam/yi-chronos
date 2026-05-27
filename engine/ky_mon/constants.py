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
TINH_CAT_HUNG = {
    "蓬": "đại hung", "任": "cát", "沖": "trung bình", "輔": "đại cát",
    "禽": "cát", "心": "cát", "柱": "trung bình", "英": "trung bình", "芮": "đại hung",
}
THAN_CAT_HUNG = {
    "符": "đại cát", "蛇": "hung", "陰": "cát", "合": "cát",
    "勾": "hung", "雀": "hung", "地": "cát", "天": "đại cát",
}
