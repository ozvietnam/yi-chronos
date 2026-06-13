"""Dữ liệu 4 đồ hình âm dương cổ — phục vụ đồ hình TƯƠNG TÁC trên web.

Bồi từ vòng đọc sâu "Học Thuyết Âm Dương Ngũ Hành" (Lê Văn Sửu) p21-40, 2026-06-13.
Anh duyệt 2026-06-13: trục THỜI GIAN làm trục chính; đầu tư đồ hình luôn.

Trung thực nguồn: vị trí 8 quẻ dùng phương vị CHUẨN (quy ước Kinh Dịch, đối chiếu
văn bản sách); diễn giải hào + hướng + mùa lấy đúng theo Lê Văn Sửu p32-33.
Lạc Thư (ma phương cửu cung) sẽ bổ sung ở vòng 3 sau khi đọc đủ phần Lạc Thư.

8 quẻ — `lines` đọc TỪ DƯỚI LÊN (hào sơ → hào thượng); 1 = hào dương (vạch liền),
0 = hào âm (vạch đứt).
"""
from __future__ import annotations

# Bát quái: tên, ký hiệu unicode, 3 hào (dưới→trên), hành, tượng
QUE = {
    "Càn":  {"symbol": "☰", "lines": [1, 1, 1], "tuong": "trời", "hanh": "kim"},
    "Đoài": {"symbol": "☱", "lines": [1, 1, 0], "tuong": "đầm/hồ", "hanh": "kim"},
    "Ly":   {"symbol": "☲", "lines": [1, 0, 1], "tuong": "lửa", "hanh": "hỏa"},
    "Chấn": {"symbol": "☳", "lines": [1, 0, 0], "tuong": "sấm", "hanh": "mộc"},
    "Tốn":  {"symbol": "☴", "lines": [0, 1, 1], "tuong": "gió", "hanh": "mộc"},
    "Khảm": {"symbol": "☵", "lines": [0, 1, 0], "tuong": "nước", "hanh": "thủy"},
    "Cấn":  {"symbol": "☶", "lines": [0, 0, 1], "tuong": "núi", "hanh": "thổ"},
    "Khôn": {"symbol": "☷", "lines": [0, 0, 0], "tuong": "đất", "hanh": "thổ"},
}

# 8 hướng → góc SVG (độ, 0° = chính trên/Bắc-treo-trên-đầu theo lối vẽ truyền thống
# "trên Nam dưới Bắc"; ta đặt 0°=trên. Mỗi component tự xoay theo quy ước đồ hình của nó).
HUONG_8 = ["trên", "trên-phải", "phải", "dưới-phải", "dưới", "dưới-trái", "trái", "trên-trái"]


def _que(name: str) -> dict:
    q = QUE[name]
    return {"ten": name, "symbol": q["symbol"], "lines": q["lines"],
            "tuong": q["tuong"], "hanh": q["hanh"]}


# ─── Tiên thiên bát quái (Phục Hy) — cái THỂ ─────────────────────────────────
# Phương vị tiên thiên chuẩn: trên Càn, dưới Khôn; các cặp đối tâm trái dấu.
# vị trí theo 8 cung quanh vòng tròn (0°=trên, thuận chiều kim đồng hồ).
TIEN_THIEN = [
    {"pos": "trên",       "que": _que("Càn"),  "doi_tam": "Khôn"},
    {"pos": "trên-phải",  "que": _que("Tốn"),  "doi_tam": "Chấn"},
    {"pos": "phải",       "que": _que("Khảm"), "doi_tam": "Ly"},
    {"pos": "dưới-phải",  "que": _que("Cấn"),  "doi_tam": "Đoài"},
    {"pos": "dưới",       "que": _que("Khôn"), "doi_tam": "Càn"},
    {"pos": "dưới-trái",  "que": _que("Chấn"), "doi_tam": "Tốn"},
    {"pos": "trái",       "que": _que("Ly"),   "doi_tam": "Khảm"},
    {"pos": "trên-trái",  "que": _que("Đoài"), "doi_tam": "Cấn"},
]

# ─── Hậu thiên bát quái (Văn Vương) — cái DỤNG trong KHÔNG GIAN ──────────────
# Mỗi quẻ một hướng + mùa + tiết + diễn giải khí hậu (Lê Văn Sửu p32-33).
# Quy ước vẽ: trên = Nam (Ly), dưới = Bắc (Khảm) theo lối "Nam thượng".
HAU_THIEN = [
    {"pos": "trên",      "huong": "Nam",      "que": _que("Ly"),
     "mua": "hạ", "tiet": "hạ chí", "giai": "khí trời nóng, lửa dễ cháy — dương khí hãm âm khí (2 dương bọc 1 âm)"},
    {"pos": "trên-phải", "huong": "Tây nam",  "que": _que("Khôn"),
     "mua": "cuối hạ", "tiet": "lập thu", "giai": "mùa mưa — âm khí thắng dương khí (cả 3 hào âm)"},
    {"pos": "phải",      "huong": "Tây",      "que": _que("Đoài"),
     "mua": "thu", "tiet": "thu phân", "giai": "hanh khô, dương khí đã chiếm hết mặt đất (1 âm trên, 2 dương dưới)"},
    {"pos": "dưới-phải", "huong": "Tây bắc",  "que": _que("Càn"),
     "mua": "cuối thu", "tiet": "lập đông", "giai": "hanh khô cực độ, vạn vật cứng rắn (cả 3 hào dương)"},
    {"pos": "dưới",      "huong": "Bắc",      "que": _que("Khảm"),
     "mua": "đông", "tiet": "đông chí", "giai": "giá lạnh, nước đóng băng — âm khí hãm dương khí (2 âm bọc 1 dương)"},
    {"pos": "dưới-trái", "huong": "Đông bắc", "que": _que("Cấn"),
     "mua": "cuối đông", "tiet": "lập xuân", "giai": "dương khí vừa thoát khỏi sự bao bọc của âm khí (1 dương trên, 2 âm dưới)"},
    {"pos": "trái",      "huong": "Đông",     "que": _que("Chấn"),
     "mua": "xuân", "tiet": "xuân phân", "giai": "âm dương va chạm thành sấm — 1 dương dưới, 2 âm trên"},
    {"pos": "trên-trái", "huong": "Đông nam", "que": _que("Tốn"),
     "mua": "cuối xuân", "tiet": "lập hạ", "giai": "mùa gió chướng và bão — dương khí lấn át âm khí (2 dương trên, 1 âm dưới)"},
]

# ─── Hà Đồ — 10 số, 3 vòng, cặp sinh-thành cách nhau 5 ───────────────────────
# Vị trí ngũ phương chuẩn: Bắc 1-6 thủy, Nam 2-7 hỏa, Đông 3-8 mộc, Tây 4-9 kim, Trung 5-10 thổ.
# am_duong: số lẻ = dương (trắng), số chẵn = âm (đen).
HA_DO = [
    {"phuong": "Bắc",   "sinh": 1, "thanh": 6,  "hanh": "thủy", "vi_tri": "dưới"},
    {"phuong": "Nam",   "sinh": 2, "thanh": 7,  "hanh": "hỏa",  "vi_tri": "trên"},
    {"phuong": "Đông",  "sinh": 3, "thanh": 8,  "hanh": "mộc",  "vi_tri": "trái"},
    {"phuong": "Tây",   "sinh": 4, "thanh": 9,  "hanh": "kim",  "vi_tri": "phải"},
    {"phuong": "Trung", "sinh": 5, "thanh": 10, "hanh": "thổ",  "vi_tri": "giữa"},
]

# ─── Lạc Thư — ma phương cửu cung (mỗi hàng/cột/chéo = 15) ───────────────────
# Vị trí 8 hướng + giữa (Lê Văn Sửu p44). ô lưới 3×3 theo quy ước trên=Nam dưới=Bắc.
# loai: 'duong'(số lẻ/nhiệt) | 'am'(số chẵn/ẩm). row/col cho lưới SVG (0..2).
LAC_THU = [
    {"so": 4, "phuong": "Đông nam", "loai": "am",     "row": 0, "col": 0},
    {"so": 9, "phuong": "Nam",      "loai": "duong",  "row": 0, "col": 1},
    {"so": 2, "phuong": "Tây nam",  "loai": "am",     "row": 0, "col": 2},
    {"so": 3, "phuong": "Đông",     "loai": "duong",  "row": 1, "col": 0},
    {"so": 5, "phuong": "Trung",    "loai": "duong",  "row": 1, "col": 1},
    {"so": 7, "phuong": "Tây",      "loai": "duong",  "row": 1, "col": 2},
    {"so": 8, "phuong": "Đông bắc", "loai": "am",     "row": 2, "col": 0},
    {"so": 1, "phuong": "Bắc",      "loai": "duong",  "row": 2, "col": 1},
    {"so": 6, "phuong": "Tây bắc",  "loai": "am",     "row": 2, "col": 2},
]


# ─── Ngũ giác Sinh-Khắc-Chế-Hóa (Hình 3-14, Lê Văn Sửu p109) ────────────────
# 5 hành trên 5 đỉnh ngũ giác, thứ tự TỪ ĐỈNH TRÊN thuận chiều kim đồng hồ.
# Cạnh ngoài nối đỉnh kề = TƯƠNG SINH; sao 5 cánh nối cách-một-đỉnh = TƯƠNG KHẮC.
NGU_GIAC = ["hỏa", "thổ", "kim", "thủy", "mộc"]

# ─── Đồng hồ sinh học 12 canh giờ — Thập nhị kinh nạp địa chi ────────────────
# Dương Kế Châu, Châm cứu đại thành (in 1601) tr.153 — bài ca "Thập nhị kinh nạp
# địa chi": mỗi canh giờ (2 tiếng) một đường kinh/tạng phủ vượng. Lê Văn Sửu p136-137
# nêu đây là bằng chứng TRỤC THỜI GIAN của ngũ hành ("nhịp thời sinh học"): Tây phương
# đo 30.000 ca viêm gan cấp phát ~2h sáng = giờ Sửu = kinh Can (gan); thứ tự hoạt động
# tạng phủ trùng chu kỳ 12 địa chi. Tý đặt ở đỉnh, thuận chiều kim đồng hồ.
THAP_NHI_KINH = [
    {"chi": "Tý",   "gio": "23–1h",  "kinh": "Đảm (mật)",    "hanh": "mộc"},
    {"chi": "Sửu",  "gio": "1–3h",   "kinh": "Can (gan)",    "hanh": "mộc"},
    {"chi": "Dần",  "gio": "3–5h",   "kinh": "Phế (phổi)",   "hanh": "kim"},
    {"chi": "Mão",  "gio": "5–7h",   "kinh": "Đại trường",   "hanh": "kim"},
    {"chi": "Thìn", "gio": "7–9h",   "kinh": "Vị (dạ dày)",  "hanh": "thổ"},
    {"chi": "Tỵ",   "gio": "9–11h",  "kinh": "Tỳ (lá lách)", "hanh": "thổ"},
    {"chi": "Ngọ",  "gio": "11–13h", "kinh": "Tâm (tim)",    "hanh": "hỏa"},
    {"chi": "Mùi",  "gio": "13–15h", "kinh": "Tiểu trường",  "hanh": "hỏa"},
    {"chi": "Thân", "gio": "15–17h", "kinh": "Bàng quang",   "hanh": "thủy"},
    {"chi": "Dậu",  "gio": "17–19h", "kinh": "Thận",         "hanh": "thủy"},
    {"chi": "Tuất", "gio": "19–21h", "kinh": "Tâm bào",      "hanh": "hỏa"},
    {"chi": "Hợi",  "gio": "21–23h", "kinh": "Tam tiêu",     "hanh": "hỏa"},
]

# ─── 6 Thanh tiếng Việt theo Âm Dương — khí chất sinh học người Việt ─────────
# Lê Văn Sửu Chương 4 p146-153 (LUẬN ĐIỂM TÁC GIẢ — attribution): tiếng Việt đơn âm,
# mỗi thanh có 'đường hình' + tư thế đầu-cổ + tính âm dương. 2 thanh BẰNG phát triển
# NGANG = ÂM; 4 thanh TRẮC phát triển DỌC = DƯƠNG. `pts` = đường hình (hộp 80×50, y nhỏ
# = cao độ cao); minh họa theo mô tả Hình 4-1..4-6 của tác giả.
# `hanh / do_cao / tam_sinh_ly / tang` từ Bảng 4-6, 4-7 (p169-170): 6 thanh ánh xạ
# vào ngũ hành qua độ cao + độ dài + tâm sinh lý + tạng phủ → nối 6 thanh vào hệ ngũ hành.
SAU_THANH = [
    {"ten": "Thượng thanh", "dau": "sắc  / ", "loai": "trắc", "am_duong": "dương", "hanh": "hỏa",
     "do_cao": "rất cao", "tam_sinh_ly": "thần minh, vui", "tang": "Tâm, Tiểu trường",
     "tu_the": "đầu cổ ngửa lên", "vi_du": "tiến, tới, cố, gắng", "pts": [[12, 38], [72, 12]]},
    {"ten": "Khứ thanh", "dau": "ngã  ~ ", "loai": "trắc", "am_duong": "dương", "hanh": "mộc",
     "do_cao": "hơi cao", "tam_sinh_ly": "mưu lự, giận", "tang": "Can, Đởm",
     "tu_the": "hất ngửa rồi hạ", "vi_du": "ngã, cãi vã, vã", "pts": [[8, 28], [24, 28], [40, 13], [56, 26], [70, 28]]},
    {"ten": "Đoản bình", "dau": "không dấu", "loai": "bằng", "am_duong": "âm", "hanh": "thổ",
     "do_cao": "vừa phải", "tam_sinh_ly": "bình thản", "tang": "Tỳ, Vị",
     "tu_the": "đầu cổ ngay ngắn", "vi_du": "đi, ngang, cân", "pts": [[8, 25], [72, 25]]},
    {"ten": "Trường bình", "dau": "huyền  ` ", "loai": "bằng", "am_duong": "âm", "hanh": "thổ",
     "do_cao": "hơi thấp", "tam_sinh_ly": "lo lắng", "tang": "Tỳ, Vị",
     "tu_the": "đầu cổ hơi cúi", "vi_du": "từ từ, vừa vừa", "pts": [[8, 22], [72, 34]]},
    {"ten": "Hồi thanh", "dau": "hỏi  ? ", "loai": "trắc", "am_duong": "dương", "hanh": "kim",
     "do_cao": "thấp", "tam_sinh_ly": "trị tiết, buồn", "tang": "Phế, Đại trường",
     "tu_the": "cúi gập rồi nâng", "vi_du": "nảy, gảy, bảy, tẩy", "pts": [[8, 26], [26, 30], [40, 44], [56, 32], [70, 24]]},
    {"ten": "Hạ thanh", "dau": "nặng  . ", "loai": "trắc", "am_duong": "dương", "hanh": "thủy",
     "do_cao": "rất thấp", "tam_sinh_ly": "kỹ xảo, kinh hãi", "tang": "Thận, Bàng quang",
     "tu_the": "đầu cổ cúi gập", "vi_du": "rụng, đập, quật", "pts": [[18, 26], [40, 46]]},
]

# Giọng vùng miền ↔ ngũ hành địa lý (Lê Văn Sửu p176-178) — tập quán phát âm theo môi
# trường sinh học từng vùng. Phương vị → hành (chỉ tag nơi tác giả gán hành rõ).
TIENG_VUNG_MIEN = [
    {"vung": "Đồng bằng Bắc Bộ", "phuong": "bắc", "hanh": "thủy",
     "dac_diem": "nói hơi nhanh, chuẩn cao độ, dứt khoát; thay phụ âm uốn lưỡi",
     "vi_du": "thái thịt → xái xịt; con trâu trắng → con tâu tặng; làm lụng → nàm nụng"},
    {"vung": "Miền Trung (Thanh-Nghệ-Tĩnh-Bình-Trị-Thiên)", "phuong": "đông (giữa)", "hanh": "mộc",
     "dac_diem": "nói chậm, giằn giọng nặng nề, giảm thanh thượng 3-4 bậc, đưa trường bình lên đoản",
     "vi_du": "chào đồng chí → chao đông chỉ; uống nước → uổng nược"},
    {"vung": "Đồng bằng Nam Bộ", "phuong": "nam", "hanh": "hỏa",
     "dac_diem": "kéo dài trường độ thanh, thêm nguyên/phụ âm; có khi đổi dấu để kéo dài",
     "vi_du": "vô ý → giô ý; anh ơi → eng ơi; anh ấy → ảnh ấy"},
]

# ─── Ngũ hành trong NGHỆ THUẬT TẠO HÌNH (chương NHÌN, Lê Văn Sửu p190-200) ────
# Ngũ hành ↔ hình thể + màu + dáng người + tâm lý (Bảng 4-11, 4-13, Hình 4-19).
# `hinh_loai` cho renderer: chu_nhat | tron | vuong | tam_giac | uon_khuc.
# `net_pts` (Bảng 4-14 p206): đường nét đại biểu mỗi hành (toạ độ tương đối tâm, hộp ±12×±9).
# `do_cao` + `do_cao_vat` (Bảng 4-16 p214): độ cao thị giác ↔ vật đại biểu ↔ hành.
# `dau_thanh` (Bảng 4-15 p213): dấu thanh chữ Việt TRÙNG đường nét cùng hành (hợp nhất 6 thanh).
NGU_HANH_TAO_HINH: dict[str, dict] = {
    "mộc":  {"hinh": "chữ nhật", "hinh_loai": "chu_nhat", "mau": "xanh", "tinh_cach": "tướng quân",
             "dang_nguoi": "đứng hiên ngang, chống đỡ", "tam_ly": "mưu lự, giận",
             "duong_net": "đường uốn ngửa (khứ văn)", "net_pts": [[-12, 6], [0, -8], [12, 6]],
             "do_cao": "trên trung bình", "do_cao_vat": "cây", "dau_thanh": "ngã (~)",
             "ly_do": "thân cây, cột, dầm nhà — chống đỡ, ngay thẳng, cứng rắn, gây lòng tin"},
    "hỏa":  {"hinh": "tròn", "hinh_loai": "tron", "mau": "đỏ", "tinh_cach": "quân chủ",
             "dang_nguoi": "mừng đón, vui sướng", "tam_ly": "thần minh, vui",
             "duong_net": "đường cong tròn (nguyệt huyền văn)", "net_pts": [[-12, -4], [-6, 6], [6, 6], [12, -4]],
             "do_cao": "cao nhất", "do_cao_vat": "mặt trời", "dau_thanh": "sắc (/)",
             "ly_do": "quả cầu, bánh xe, đầu người, mặt trời — linh hoạt, ấm sáng, nguồn lửa-sự sống"},
    "thổ":  {"hinh": "vuông", "hinh_loai": "vuong", "mau": "vàng", "tinh_cach": "điều hòa",
             "dang_nguoi": "lo lắng, bình thản", "tam_ly": "bình thản, lo lắng",
             "duong_net": "đường thẳng ngang (trực văn)", "net_pts": [[-12, 0], [12, 0]],
             "do_cao": "trung bình", "do_cao_vat": "mặt đất", "dau_thanh": "không dấu / huyền (`)",
             "ly_do": "khối vuông — vững trãi, sức ì; cuối hạ đất ẩm nhão, tỳ vị hay bệnh → lo vu vơ"},
    "kim":  {"hinh": "tam giác", "hinh_loai": "tam_giac", "mau": "trắng", "tinh_cach": "tướng phó",
             "dang_nguoi": "suy tính, buồn rầu", "tam_ly": "trị tiết, buồn",
             "duong_net": "đường cong câu (hồi văn)", "net_pts": [[-7, -9], [-7, 4], [1, 8], [6, 2]],
             "do_cao": "dưới trung bình", "do_cao_vat": "quặng kim thạch", "dau_thanh": "hỏi (?)",
             "ly_do": "giáo mác, mũi tên, mảnh vỡ, góc nhọn — phá nát cái mềm hơn, gây cảm giác buồn"},
    "thủy": {"hinh": "uốn khúc", "hinh_loai": "uon_khuc", "mau": "đen", "tinh_cach": "tác cường",
             "dang_nguoi": "chuẩn bị kỹ thuật, bắt bóng, nhảy, múa khéo léo", "tam_ly": "kỹ xảo, kinh hãi",
             "duong_net": "đường gấp khúc (thủy ba văn)", "net_pts": [[-12, 6], [-6, -6], [0, 6], [6, -6], [12, 6]],
             "do_cao": "thấp nhất", "do_cao_vat": "nước (mạch ngầm)", "dau_thanh": "nặng (.)",
             "ly_do": "nước chảy quanh co, dáng múa, sóng, tia chớp — khéo léo luồn lách / sợ hãi"},
}


def do_hinh_payload() -> dict:
    """Payload đầy đủ cho component đồ hình tương tác."""
    from .ngu_hanh_nen import NGU_HANH_NHIET_AM, HANH_THO_3_THE, sinh_khac_che_hoa_payload
    # Tọa độ ngũ hành nhiệt-ẩm: x = % nhiệt (0..100), y = % ẩm (0..100).
    nhiet_am = [
        {"hanh": h, "khi": d["khi"], "phuong": d["phuong"],
         "nhiet": d["nhiet"], "am": d["am"]}
        for h, d in NGU_HANH_NHIET_AM.items()
    ]
    skch = sinh_khac_che_hoa_payload()
    return {
        "nguon": "Lê Văn Sửu — Học Thuyết Âm Dương Ngũ Hành, p21-40 (vòng đọc sâu 2, 2026-06-13)",
        "truc_chinh": "thời gian — mọi đồ hình đọc theo nhịp vận động của vũ trụ tính bằng đơn vị thời gian (nhịp thời sinh học)",
        "thai_cuc": {
            "mo_ta": "Hình tròn 2 nửa đen-trắng, ranh giới chữ S; trắng=dương, đen=âm; "
                     "nơi cực đại mỗi nửa có một điểm trái dấu (trong dương có âm, trong âm có dương).",
            "tac_gia": "Tương truyền Trần Đoàn (thời Ngũ Đại) được bí chỉ ở Ma Y Đạo vẽ ra "
                       "— cùng là chính tổ Tử Vi Đẩu Số.",
            "tinh_chat": [
                "Trong cái toàn nhất có 2 nửa âm-dương",
                "Trong dương có âm, trong âm có dương",
                "Dương giảm thì âm tăng (và ngược lại)",
                "Nhịp: dương trước, âm sau",
                "Chiều: thuận = dương→âm, nghịch = âm→dương",
            ],
        },
        "tien_thien": {
            "ten": "Tiên thiên bát quái (Phục Hy) — cái THỂ",
            "y_nghia": "Hai hệ quy chiếu: nửa dương đi ngược (nhật tâm), nửa âm đi thuận (địa tâm). "
                       "Các cặp quẻ đối tâm trái dấu âm dương → hút nhau như hai cực nam châm "
                       "= kết cấu bền vững của vũ trụ.",
            "cung": TIEN_THIEN,
        },
        "hau_thien": {
            "ten": "Hậu thiên bát quái (Văn Vương) — cái DỤNG trong KHÔNG GIAN",
            "y_nghia": "Mỗi quẻ ở một hướng + mùa + tiết; hình tượng hào khớp khí hậu phương đó. "
                       "Phân biệt với Cửu cung = cái dụng của âm dương trong THỜI GIAN (tính theo năm).",
            "cung": HAU_THIEN,
        },
        "ha_do": {
            "ten": "Hà Đồ — quy luật nhịp âm dương (số sinh & số thành) · tính THỜI GIAN",
            "y_nghia": "10 số: lẻ=dương(trắng), chẵn=âm(đen); cặp sinh-thành cách nhau 5 "
                       "(1↔6, 2↔7, 3↔8, 4↔9, 5↔10). Nhịp âm dương nhỏ bị nhịp lớn chi phối.",
            "diem": HA_DO,
        },
        "lac_thu": {
            "ten": "Lạc Thư — ma phương cửu cung · tính KHÔNG GIAN",
            "y_nghia": "9 số xếp ma phương 3×3, mọi hàng/cột/chéo đều = 15. Dương (số lẻ) = "
                       "NHIỆT ĐỘ (tối đa Nam 9 → Bắc 1); âm (số chẵn) = ĐỘ ẨM (tối đa Đông bắc 8 "
                       "→ Tây nam 2). Cơ sở là khí hậu thật vùng Phương Đông (đông biển ẩm, tây "
                       "núi khô, nam nóng, bắc lạnh) — 'sản phẩm khoa học thực nghiệm, không phải "
                       "nguồn gốc thần bí'.",
            "tong": 15,
            "o": LAC_THU,
        },
        "nhiet_am": {
            "ten": "Ngũ Hành = tọa độ Nhiệt × Ẩm (lượng hóa của Lê Văn Sửu)",
            "y_nghia": "Mỗi hành là một ĐIỂM trên mặt phẳng % nhiệt (trục ngang = dương) × % ẩm "
                       "(trục dọc = âm). Hỏa nóng nhất, Thủy lạnh nhất, Mộc ẩm nhất, Kim khô nhất; "
                       "Thổ ở TÂM (50-50) — trạng thái cân bằng, điểm tĩnh giữa các chuyển động. "
                       "Đây là cách giải bí ẩn hành Thổ mà các học giả nghìn năm bí.",
            "diem": nhiet_am,
            "tho_3_the": HANH_THO_3_THE,
        },
        "sinh_khac_che_hoa": {
            "ten": "Sinh · Khắc · Chế · Hóa của Ngũ Hành (Hình 3-14)",
            "y_nghia": "Cạnh ngoài ngũ giác = TƯƠNG SINH (vòng nuôi nhau, thuận chiều kim đồng hồ); "
                       "sao 5 cánh bên trong = TƯƠNG KHẮC (cách một hành). Khi một hành bị khắc quá tay: "
                       "CHẾ = con của nó quay lại khắc kẻ đi khắc; HÓA = chèn một hành thông quan, "
                       "biến thế khắc thành chuỗi sinh nuôi nó. Đủ 4 quy luật mới thành hệ cân bằng.",
            "ngu_giac": NGU_GIAC,
            "sinh": skch["sinh"],
            "khac": skch["khac"],
            "che_hoa": skch["che_hoa"],
            "than": skch["than"],
            "dinh_nghia": skch["dinh_nghia"],
            "nguon": skch["nguon"],
        },
        "sau_thanh_tieng_viet": {
            "ten": "6 Thanh tiếng Việt → Âm Dương → Ngũ Hành (khí chất sinh học người Việt)",
            "y_nghia": "Tiếng Việt đơn âm: mỗi thanh một 'đường hình' + tư thế đầu-cổ. 2 thanh BẰNG "
                       "(không dấu, huyền) = ÂM (êm dịu, ngang); 4 thanh TRẮC (sắc, ngã, hỏi, nặng) = "
                       "DƯƠNG (mạnh, dọc). Sâu hơn: mỗi thanh ánh xạ một NGŨ HÀNH qua độ cao + tâm sinh "
                       "lý + tạng phủ (Thượng=Hỏa/vui, Khứ=Mộc/giận, Đoản+Trường=Thổ/bình thản-lo, "
                       "Hồi=Kim/buồn, Hạ=Thủy/kinh hãi) → 6 thanh nối thẳng vào hệ ngũ hành. Tô màu "
                       "theo hành. LƯU Ý: luận điểm khí chất sinh học người Việt của Lê Văn Sửu (attribution).",
            "thanh": SAU_THANH,
            "tieng_vung_mien": TIENG_VUNG_MIEN,
            "nguon": "Lê Văn Sửu — Học Thuyết ÂDNH, Chương 4 p146-178 (luận điểm tác giả)",
        },
        "ngu_hanh_tao_hinh": {
            "ten": "Ngũ Hành trong Nghệ thuật Tạo hình (hình · màu · đường nét · độ cao · dáng người)",
            "y_nghia": "Mọi yếu tố thị giác đều quy về ngũ hành: HÌNH (Mộc=chữ nhật, Hỏa=tròn, "
                       "Thổ=vuông, Kim=tam giác, Thủy=uốn khúc) · ĐƯỜNG NÉT (uốn ngửa/cong tròn/"
                       "thẳng/cong câu/gấp khúc) · ĐỘ CAO (mặt trời cao nhất=Hỏa → nước thấp nhất=Thủy) "
                       "· DÁNG NGƯỜI · MÀU. Hai yếu tố cạnh nhau cộng hưởng theo sinh-khắc (tương đồng "
                       "= ổn định, tương sinh = êm dịu, tương khắc = chói gắt). HỢP NHẤT ĐẸP: 5 dấu "
                       "thanh chữ Việt TRÙNG 5 đường nét ngũ hành (sắc=cong tròn=Hỏa, ngã=uốn ngửa="
                       "Mộc, không dấu/huyền=thẳng=Thổ, hỏi=cong câu=Kim, nặng=gấp khúc=Thủy) → "
                       "6 thanh tiếng Việt và nét vẽ là MỘT hệ ngũ hành. Nền 'đọc đồng dạng' thị giác.",
            "bang": NGU_HANH_TAO_HINH,
            "vn_khac_tq": "LƯU Ý (attribution): bảng hình thể người Việt KHÁC người Trung Quốc — "
                          "3 hành Thủy/Mộc/Thổ trùng, nhưng HỎA↔KIM HOÁN VỊ (Kim người Việt = tam "
                          "giác = Hỏa người TQ). Lê Văn Sửu cho bảng Việt khớp cảm quan bản năng hơn, "
                          "bảng TQ chỉ là quy ước. (p198, Địa lý ngũ quyết)",
            "khi_hoa_mau": "Tuệ Tĩnh (Hồng nghĩa giác tư y thư, 'Khí hóa âm dương' tr.66): khí đen → "
                           "thủy sinh, khí đỏ → hỏa sinh, khí xanh → mộc sinh, khí trắng → kim sinh, "
                           "khí vàng → thổ sinh.",
            "nguon": "Lê Văn Sửu — Học Thuyết ÂDNH, Chương 4 p190-200 (Bảng 4-11, 4-13, Hình 4-19)",
        },
        "dong_ho_12_canh": {
            "ten": "Đồng hồ sinh học 12 canh giờ (Thập nhị kinh nạp địa chi)",
            "y_nghia": "Mỗi canh giờ (2 tiếng) một đường kinh / tạng phủ vượng, tô màu theo "
                       "ngũ hành. Đây là TRỤC THỜI GIAN của ngũ hành — 'nhịp thời sinh học'. "
                       "Tây phương đo 30.000 ca viêm gan cấp phát ~2h sáng = giờ Sửu = kinh Can "
                       "(gan); thứ tự hoạt động tạng phủ trùng chu kỳ 12 địa chi. Bằng chứng: "
                       "thí nghiệm cách xa hàng ngàn dặm + hàng ngàn năm vẫn cho tương ứng như nhau.",
            "kinh": THAP_NHI_KINH,
            "nguon": "Dương Kế Châu — Châm cứu đại thành (in 1601) tr.153, Lê Văn Sửu dẫn p136-137",
        },
    }
