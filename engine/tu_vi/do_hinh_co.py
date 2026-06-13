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
SAU_THANH = [
    {"ten": "Đoản bình", "dau": "không dấu", "loai": "bằng", "am_duong": "âm",
     "tu_the": "đầu cổ ngay ngắn", "vi_du": "đi, ngang, cân", "pts": [[8, 25], [72, 25]]},
    {"ten": "Trường bình", "dau": "huyền  ` ", "loai": "bằng", "am_duong": "âm",
     "tu_the": "đầu cổ hơi cúi", "vi_du": "từ từ, vừa vừa", "pts": [[8, 22], [72, 34]]},
    {"ten": "Thượng thanh", "dau": "sắc  / ", "loai": "trắc", "am_duong": "dương",
     "tu_the": "đầu cổ ngửa lên", "vi_du": "tiến, tới, cố, gắng", "pts": [[12, 38], [72, 12]]},
    {"ten": "Khứ thanh", "dau": "ngã  ~ ", "loai": "trắc", "am_duong": "dương",
     "tu_the": "hất ngửa rồi hạ", "vi_du": "ngã, cãi vã, vã", "pts": [[8, 28], [24, 28], [40, 13], [56, 26], [70, 28]]},
    {"ten": "Hồi thanh", "dau": "hỏi  ? ", "loai": "trắc", "am_duong": "dương",
     "tu_the": "cúi gập rồi nâng", "vi_du": "nảy, gảy, bảy, tẩy", "pts": [[8, 26], [26, 30], [40, 44], [56, 32], [70, 24]]},
    {"ten": "Hạ thanh", "dau": "nặng  . ", "loai": "trắc", "am_duong": "dương",
     "tu_the": "đầu cổ cúi gập", "vi_du": "rụng, đập, quật", "pts": [[18, 26], [40, 46]]},
]


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
            "ten": "6 Thanh tiếng Việt theo Âm Dương (khí chất sinh học người Việt)",
            "y_nghia": "Tiếng Việt đơn âm: mỗi thanh một 'đường hình' + tư thế đầu-cổ + tính âm dương. "
                       "2 thanh BẰNG (không dấu, huyền) phát triển NGANG = ÂM (êm dịu); 4 thanh TRẮC "
                       "(sắc, ngã, hỏi, nặng) phát triển DỌC = DƯƠNG (mạnh, biến động). Từ chỉ chiều hướng "
                       "nào thường mang thanh có đường hình cùng chiều đó (tính tượng hình). LƯU Ý: đây là "
                       "luận điểm khí chất sinh học người Việt của Lê Văn Sửu (attribution, cần đối chiếu).",
            "thanh": SAU_THANH,
            "nguon": "Lê Văn Sửu — Học Thuyết ÂDNH, Chương 4 p146-153 (luận điểm tác giả)",
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
