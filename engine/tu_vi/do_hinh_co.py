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


def do_hinh_payload() -> dict:
    """Payload đầy đủ cho component đồ hình tương tác."""
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
            "ten": "Hà Đồ — quy luật nhịp âm dương (số sinh & số thành)",
            "y_nghia": "10 số: lẻ=dương(trắng), chẵn=âm(đen); cặp sinh-thành cách nhau 5 "
                       "(1↔6, 2↔7, 3↔8, 4↔9, 5↔10). Nhịp âm dương nhỏ bị nhịp lớn chi phối.",
            "diem": HA_DO,
        },
    }
