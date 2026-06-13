"""Kiến thức nền Âm Dương Ngũ Hành cho Tử Vi — tầng cơ chế dưới mọi luận giải.

Anh chốt 2026-06-12: "chưa đưa âm dương ngũ hành vào làm kiến thức nền tảng...
tab Bát Tự liên hệ rất nhiều tới ngũ hành và quan hệ tương sinh tương khắc
rất rõ nét dễ hiểu" → tab Tử Vi cần cùng tầng nền đó.

Định nghĩa nền (theo trường phái hiện đại, khớp cổ thư):
- Âm dương = 2 TRẠNG THÁI VẬN ĐỘNG của một sự vật (không phải 2 thứ đối lập).
- Ngũ hành = 5 KIỂU VẬN ĐỘNG của năng lượng: Mộc=sinh trưởng, Hỏa=bùng nổ,
  Thổ=ổn định/chuyển hóa, Kim=thu lại, Thủy=lưu chuyển. Tên gỗ-lửa-đất-kim-nước
  chỉ là cách đặt cho dễ nhớ.
- Sinh không hẳn tốt, khắc không hẳn xấu — "luận bệnh tật sẽ biết:
  không có khắc là toi luôn."

Module này cung cấp:
- Hành của 12 địa chi (cung) + hành/âm dương/hóa khí của 14 chính tinh
  (đọc từ data/tu_vi/chinh_tinh.json — nguồn Q2 đã enrich).
- ``quan_he(a, b)``: quan hệ sinh-khắc giữa 2 hành, kèm nhãn dễ hiểu.
- ``sao_tai_cung(star, chi)``: phân tích sao đứng trên đất cung — tầng CƠ CHẾ
  góp phần giải thích miếu-hãm. LƯU Ý TRUNG THỰC: bảng miếu-hãm cổ (Q2) xét
  nhiều yếu tố hơn sinh-khắc hành đơn (tổ hợp, nhật nguyệt, cách cục...) —
  khi hai tầng lệch nhau, trả cả hai, KHÔNG bịa lý do để ép khớp.
"""
from __future__ import annotations

from functools import lru_cache

from .chinh_tinh import ALL_CHINH_TINH
from .mieu_vuong_ham import level_at

# ── Bảng nền ──────────────────────────────────────────────────────────────────

# Hành của 12 địa chi (đất của cung)
HANH_CHI: dict[str, str] = {
    "Dần": "mộc", "Mão": "mộc",
    "Tỵ": "hỏa", "Ngọ": "hỏa",
    "Thân": "kim", "Dậu": "kim",
    "Hợi": "thủy", "Tý": "thủy",
    "Thìn": "thổ", "Tuất": "thổ", "Sửu": "thổ", "Mùi": "thổ",
}

# Âm dương của 12 địa chi
AM_DUONG_CHI: dict[str, str] = {
    "Tý": "dương", "Dần": "dương", "Thìn": "dương",
    "Ngọ": "dương", "Thân": "dương", "Tuất": "dương",
    "Sửu": "âm", "Mão": "âm", "Tỵ": "âm",
    "Mùi": "âm", "Dậu": "âm", "Hợi": "âm",
}

# Vòng tương sinh / tương khắc
SINH: dict[str, str] = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
KHAC: dict[str, str] = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}

# Tọa độ nhiệt-ẩm của ngũ hành — LƯỢNG HÓA gốc của Lê Văn Sửu (Bảng 3-3 p90).
# Mỗi hành = một điểm trên mặt phẳng (% nhiệt = dương, % ẩm = âm).
NGU_HANH_NHIET_AM: dict[str, dict] = {
    "thủy": {"nhiet": 0,   "am": 50,  "khi": "Hàn", "phuong": "Bắc"},
    "hỏa":  {"nhiet": 100, "am": 50,  "khi": "Thử", "phuong": "Nam"},
    "mộc":  {"nhiet": 50,  "am": 100, "khi": "Phong", "phuong": "Đông"},
    "kim":  {"nhiet": 50,  "am": 0,   "khi": "Táo", "phuong": "Tây"},
    "thổ":  {"nhiet": 50,  "am": 50,  "khi": "Thấp", "phuong": "Trung ương"},
}

# Hành Thổ = trạng thái cân bằng nhiệt-ẩm (tổng luôn 100%) — giải bí ẩn vị trí Thổ (p95-96).
HANH_THO_3_THE: list[dict] = [
    {"the": "quân bình", "phuong": "Trung ương", "nhiet": 50, "am": 50, "ghi_chu": "thuần thổ, thế tĩnh giữa các chuyển động"},
    {"the": "dương thắng", "phuong": "Tây nam", "nhiet": 75, "am": 25, "ghi_chu": "âm trong dương thổ"},
    {"the": "âm thắng", "phuong": "Đông bắc", "nhiet": 25, "am": 75, "ghi_chu": "dương trong âm thổ"},
]

# Lục khí — 6 cặp địa chi (tư thiên / tại tuyền), chu kỳ 6 năm (y học vận khí, Bảng 3-5 p97).
# Điểm nối engine dong_y; reference data, KHÔNG dùng predict.
LUC_KHI: dict[str, dict] = {
    "Tý-Ngọ":   {"tu_thien": "Thiếu âm quân hỏa",   "tai_tuyen": "Dương minh táo kim"},
    "Sửu-Mùi":  {"tu_thien": "Thái âm thấp thổ",    "tai_tuyen": "Thái dương hàn thủy"},
    "Dần-Thân": {"tu_thien": "Thiếu dương tướng hỏa", "tai_tuyen": "Quyết âm phong mộc"},
    "Mão-Dậu":  {"tu_thien": "Dương minh táo kim",  "tai_tuyen": "Thiếu âm quân hỏa"},
    "Thìn-Tuất": {"tu_thien": "Thái dương hàn thủy", "tai_tuyen": "Thái âm thấp thổ"},
    "Tỵ-Hợi":   {"tu_thien": "Quyết âm phong mộc",  "tai_tuyen": "Thiếu dương tướng hỏa"},
}

# Hai cách gán thiên can ↔ ngũ hành (p100): ngũ vận (vận khí, chu kỳ 5) vs bản khí (Bát Tự, chu kỳ 10).
THIEN_CAN_NGU_VAN: dict[str, str] = {"Giáp": "thổ", "Kỷ": "thổ", "Ất": "kim", "Canh": "kim",
                                     "Bính": "thủy", "Tân": "thủy", "Đinh": "mộc", "Nhâm": "mộc",
                                     "Mậu": "hỏa", "Quý": "hỏa"}
THIEN_CAN_BAN_KHI: dict[str, str] = {"Giáp": "mộc", "Ất": "mộc", "Bính": "hỏa", "Đinh": "hỏa",
                                     "Mậu": "thổ", "Kỷ": "thổ", "Canh": "kim", "Tân": "kim",
                                     "Nhâm": "thủy", "Quý": "thủy"}

# 5 kiểu vận động của năng lượng (định nghĩa nền — không phải vật chất)
HANH_VAN_DONG: dict[str, str] = {
    "mộc": "sinh trưởng — vươn lên, mở rộng",
    "hỏa": "bùng nổ — phát sáng, lan tỏa",
    "thổ": "ổn định — nuôi giữ, chuyển hóa",
    "kim": "thu lại — kết tinh, định hình",
    "thủy": "lưu chuyển — thấm sâu, linh hoạt",
}

# Tên CỔ CHUẨN của 5 kiểu vận động theo khí hóa 5 mùa (Lê Văn Sửu p49):
# "Xuân Sinh, Hạ Trưởng, Trưởng Hạ Hóa, Thu Thâu, Đông Tàng".
# phuong: phương vị chủ (Đổng Trọng Thư p64); khi: loại khí (Tuệ Tĩnh p65).
KHI_HOA_MUA: dict[str, dict] = {
    "mộc":  {"dong_tu": "Sinh",   "mua": "xuân", "phuong": "đông",       "khi": "phong (gió)",  "ý": "nảy mầm, phát triển mạnh"},
    "hỏa":  {"dong_tu": "Trưởng", "mua": "hạ",   "phuong": "nam",        "khi": "thử (nóng)",   "ý": "trưởng thành, khai hoa kết trái"},
    "thổ":  {"dong_tu": "Hóa",    "mua": "trưởng hạ (cuối hạ đầu thu)", "phuong": "trung ương", "khi": "thấp (ẩm)", "ý": "chuyển hóa, nuôi giữ, giúp các hành khác"},
    "kim":  {"dong_tu": "Thâu",   "mua": "thu",  "phuong": "tây",        "khi": "táo (khô)",    "ý": "thu liễm, nhựa gom về thân, lá rụng"},
    "thủy": {"dong_tu": "Tàng",   "mua": "đông", "phuong": "bắc",        "khi": "hàn (lạnh)",   "ý": "tàng ẩn, gom về gốc rễ giữ sự sống"},
}

# ── Tương CHẾ / tương HÓA — Lê Văn Sửu p108-110 (đủ 4 quy luật ngũ hành) ──────
# Sách giảng tới chế/hóa ở đây → kích hoạt gợi ý #2 (Anh duyệt 2026-06-13: bổ
# sung chế/hóa KHI sách dạy tới). Khớp cổ thư "Thần bí dịch tinh tượng"
# (NXB Nhân dân Quảng Tây, tr.117-118).
#
# Với cặp khắc  X ⊣khắc⊣ Y  (X = sở thắng/kẻ đi khắc; Y = sở bất thắng/kẻ bị khắc):
#   • CHẾ = con của Y  (= SINH[Y]). Con của kẻ bị khắc quay lại khắc kẻ đi khắc,
#           "có ý cứu trợ" cho Y. VD: Kim khắc Mộc → Hỏa (con Mộc) chế Kim.
#   • HÓA = con của X  (= SINH[X]). X sinh Z rồi Z sinh Y → "thông quan", biến
#           thế khắc thành chuỗi sinh nuôi Y ("hóa ác quy thiện"). VD: Kim khắc
#           Mộc → Thủy (con Kim) hóa: Kim sinh Thủy, Thủy sinh Mộc.

# Sinh-Vượng-Mộ — 3 giai đoạn của vật theo mùa ↔ 3 mức mùa (Bảng 3-10 p106).
# Đây là NỀN LÝ THUYẾT của vòng Tràng Sinh 12 cung trong Tử Vi
# (xem engine/tu_vi/paradigm/trang_sinh.py — vòng 12 sao thực thi).
SINH_VUONG_MO: dict[str, dict] = {
    "sinh":  {"chi": ["Dần", "Thân", "Tỵ", "Hợi"],   "muc_mua": "mạnh",  "y": "khởi sinh — đầu mùa"},
    "vượng": {"chi": ["Tý", "Ngọ", "Mão", "Dậu"],    "muc_mua": "trọng", "y": "cực thịnh — giữa mùa"},
    "mộ":    {"chi": ["Thìn", "Tuất", "Sửu", "Mùi"], "muc_mua": "quý",   "y": "tàng thu — cuối mùa, đất tứ quý"},
}

# Bảng tra tổng: ngũ hành tương ứng trong các quy luật (Bảng 3-12 p110-113).
# Một hành hiện diện đồng dạng xuyên mùa / lục khí / ngũ vận / thiên can / địa chi /
# tiết quý / bát quái / cửu cung / phương hướng / khí — bằng chứng "đọc đồng dạng".
NGU_HANH_QUY_LUAT: dict[str, dict] = {
    "mộc": {"mua": "xuân", "tu_thien": "quyết âm phong mộc (năm Tỵ, Hợi)", "ngu_van": "Đinh, Nhâm",
            "thien_can": "Giáp, Ất", "dia_chi": "Dần, Mão", "tiet_quy": "mạnh xuân, trọng xuân",
            "bat_quai": "Chấn, Tốn", "cuu_cung": "3, 4", "phuong": "đông, đông nam", "khi": "phong"},
    "hỏa": {"mua": "hạ", "tu_thien": "thiếu âm quân hỏa (Tý, Ngọ) + thiếu dương tướng hỏa (Dần, Thân)",
            "ngu_van": "Mậu, Quý", "thien_can": "Bính, Đinh", "dia_chi": "Tỵ, Ngọ",
            "tiet_quy": "mạnh hạ, trọng hạ", "bat_quai": "Ly", "cuu_cung": "9", "phuong": "nam", "khi": "thử"},
    "thổ": {"mua": "trưởng hạ", "tu_thien": "thái âm thấp thổ (Sửu, Mùi)", "ngu_van": "Giáp, Kỷ",
            "thien_can": "Mậu, Kỷ", "dia_chi": "Thìn, Tuất, Sửu, Mùi", "tiet_quy": "tứ quý (quý xuân/hạ/thu/đông)",
            "bat_quai": "Cấn, Khôn", "cuu_cung": "8, 2, 5", "phuong": "đông bắc, tây nam, trung ương", "khi": "thấp"},
    "kim": {"mua": "thu", "tu_thien": "dương minh táo kim (Mão, Dậu)", "ngu_van": "Ất, Canh",
            "thien_can": "Canh, Tân", "dia_chi": "Thân, Dậu", "tiet_quy": "mạnh thu, trọng thu",
            "bat_quai": "Càn, Đoài", "cuu_cung": "6, 7", "phuong": "tây, tây bắc", "khi": "táo"},
    "thủy": {"mua": "đông", "tu_thien": "thái dương hàn thủy (Thìn, Tuất)", "ngu_van": "Bính, Tân",
             "thien_can": "Nhâm, Quý", "dia_chi": "Hợi, Tý", "tiet_quy": "mạnh đông, trọng đông",
             "bat_quai": "Khảm", "cuu_cung": "1", "phuong": "bắc", "khi": "hàn"},
}

# Tương ứng ngũ hành ↔ tạng phủ ↔ giác quan ↔ sắc ↔ vị ↔ ngũ âm (Lê Văn Sửu p143-147,
# dẫn Châm cứu đại thành). Bảng tương ứng THÂN THỂ — nền y học cổ + nhịp thời sinh học.
# (Giác quan theo cách trình bày của tác giả: Tâm↔tay sờ, Tỳ↔lưỡi nếm.)
NGU_HANH_THAN: dict[str, dict] = {
    "mộc":  {"tang": "Can (gan)",     "phu": "Đởm (mật)",   "quan": "mắt — nhìn",   "sac": "xanh",  "vi": "chua", "am": "Giốc",   "tieng": "hô (gọi)",  "am_tc": "đều mà thẳng"},
    "hỏa":  {"tang": "Tâm (tim)",     "phu": "Tiểu trường", "quan": "tay — sờ",     "sac": "đỏ",    "vi": "đắng", "am": "Chủy",   "tieng": "cười",      "am_tc": "êm mà dài"},
    "thổ":  {"tang": "Tỳ (lá lách)",  "phu": "Vị (dạ dày)", "quan": "lưỡi — nếm",   "sac": "vàng",  "vi": "ngọt", "am": "Cung",   "tieng": "ca (hát)",  "am_tc": "to mà êm"},
    "kim":  {"tang": "Phế (phổi)",    "phu": "Đại trường",  "quan": "mũi — ngửi",   "sac": "trắng", "vi": "cay",  "am": "Thương", "tieng": "khóc",      "am_tc": "nhẹ mà động"},
    "thủy": {"tang": "Thận",          "phu": "Bàng quang",  "quan": "tai — nghe",   "sac": "đen",   "vi": "mặn",  "am": "Vũ",     "tieng": "rên",       "am_tc": "trầm mà sâu"},
}

_STAR_BY_NAME = {s.ten_vi: s for s in ALL_CHINH_TINH}


def _hanh_chinh(ngu_hanh_raw: str) -> tuple[str, str | None]:
    """Tách hành chính + hành phụ ('mộc / thủy' → ('mộc', 'thủy'))."""
    parts = [p.strip().lower() for p in str(ngu_hanh_raw).split("/") if p.strip()]
    if not parts:
        return "", None
    return parts[0], (parts[1] if len(parts) > 1 else None)


def quan_he(hanh_a: str, hanh_b: str) -> dict:
    """Quan hệ giữa hành A (chủ thể) và hành B (đối tượng).

    Returns {code, label, arrow}:
      dong_hanh | a_sinh_b | b_sinh_a | a_khac_b | b_khac_a
    """
    a, b = hanh_a.lower().strip(), hanh_b.lower().strip()
    if not a or not b:
        return {"code": "unknown", "label": "không rõ", "arrow": "?"}
    if a == b:
        return {"code": "dong_hanh", "label": "đồng hành", "arrow": f"{a} = {b}"}
    if SINH.get(a) == b:
        return {"code": "a_sinh_b", "label": "tương sinh (A sinh B)", "arrow": f"{a} → sinh → {b}"}
    if SINH.get(b) == a:
        return {"code": "b_sinh_a", "label": "tương sinh (B sinh A)", "arrow": f"{b} → sinh → {a}"}
    if KHAC.get(a) == b:
        return {"code": "a_khac_b", "label": "tương khắc (A khắc B)", "arrow": f"{a} ⊣ khắc ⊣ {b}"}
    if KHAC.get(b) == a:
        return {"code": "b_khac_a", "label": "tương khắc (B khắc A)", "arrow": f"{b} ⊣ khắc ⊣ {a}"}
    return {"code": "unknown", "label": "không rõ", "arrow": "?"}


def che_hoa(attacker: str, victim: str) -> dict | None:
    """Hành CHẾ và hành HÓA cho cặp khắc ``attacker ⊣ victim`` (Lê Văn Sửu p108-110).

    None nếu (attacker, victim) không phải cặp khắc thật.
    """
    a, v = attacker.lower().strip(), victim.lower().strip()
    if KHAC.get(a) != v:
        return None
    che = SINH[v]   # con của kẻ bị khắc, quay lại khắc kẻ đi khắc
    hoa = SINH[a]   # con của kẻ đi khắc, thông quan sinh xuống kẻ bị khắc
    return {
        "khac": [a, v],
        "che": {
            "hanh": che,
            "co_che": f"{v} sinh {che}, {che} khắc {a} → {che} chế {a}, cứu {v}",
            "y_nghia": "phản chế — con của kẻ bị khắc quay lại khắc kẻ đi khắc",
        },
        "hoa": {
            "hanh": hoa,
            "co_che": f"{a} sinh {hoa}, {hoa} sinh {v} → {hoa} thông quan, hóa khắc thành sinh",
            "y_nghia": "thông quan — chuyển thế tương khắc thành chuỗi tương sinh nuôi kẻ bị khắc",
        },
    }


_VONG_HANH = ["mộc", "hỏa", "thổ", "kim", "thủy"]


def sinh_khac_che_hoa_payload() -> dict:
    """5 vòng quan hệ ngũ hành (sinh/khắc) + 5 cặp khắc kèm chế·hóa — cho đồ hình + UI."""
    return {
        "dinh_nghia": {
            "sinh": "Cái trước là MẸ sinh cái sau là CON: Thủy→Mộc→Hỏa→Thổ→Kim→Thủy.",
            "khac": "Cách một hành thì khắc; kẻ đi khắc = 'sở thắng', kẻ bị khắc = 'sở bất thắng'.",
            "che": "Tương chế: con của kẻ bị khắc quay lại khắc kẻ đi khắc → cứu trợ kẻ bị khắc.",
            "hoa": "Tương hóa: 'thông quan' — chèn một hành ở giữa để khắc biến thành chuỗi sinh "
                   "('hóa ác quy thiện').",
            "can_co_khac": "Sinh không hẳn tốt, khắc không hẳn xấu — không có khắc thì không có "
                           "định hình, không có chế-hóa thì hệ mất cân bằng.",
        },
        "sinh": [[h, SINH[h]] for h in _VONG_HANH],
        "khac": [[h, KHAC[h]] for h in _VONG_HANH],
        "che_hoa": [che_hoa(h, KHAC[h]) for h in _VONG_HANH],
        "than": NGU_HANH_THAN,
        "nguon": "Lê Văn Sửu — Học Thuyết Âm Dương Ngũ Hành, p108-110 "
                 "(khớp 'Thần bí dịch tinh tượng' NXB Nhân dân Quảng Tây tr.117-118)",
    }


# Diễn giải sao-đứng-trên-đất-cung theo từng quan hệ (A = sao, B = đất cung).
# Giọng: cơ chế năng lượng + bài học — KHÔNG phán tốt/xấu.
_NHAN_DINH_SAO_CUNG: dict[str, str] = {
    "dong_hanh": (
        "Sao về đúng quê hành của mình — khí thuận, lực biểu hiện tự nhiên, "
        "không phải gồng. Bài học ở đây là dùng cái thuận cho khéo, đừng để thành quán tính."
    ),
    "b_sinh_a": (
        "Đất cung SINH cho sao — như cây trồng đúng thổ nhưỡng: lực sao được bồi đắp "
        "liên tục, vào đà nhanh. Cẩn thận một điều: được nuôi dễ thì cũng dễ ỷ vào đà."
    ),
    "a_sinh_b": (
        "Sao phải NHẢ lực ra nuôi bối cảnh — làm được việc cho nơi này nhưng hao khí. "
        "Bài học: tiết chế nhịp, biết nạp lại, đừng cho đi đến cạn."
    ),
    "b_khac_a": (
        "Đất cung KHẮC sao — lực bị nén lại, biểu hiện chậm và khó hơn. Nén không phải "
        "án phạt: nén đúng cách thành độ chắc, thành bản lĩnh; nén sai cách thành ức chế."
    ),
    "a_khac_b": (
        "Sao KHẮC đất cung — lực đủ mạnh để áp đặt lên bối cảnh, nhưng tốn sức kiểm soát, "
        "dễ căng. Bài học: thắng bối cảnh chưa phải là xong, giữ được lâu mới là xong."
    ),
}


def sao_tai_cung(star_vi: str, chi_vi: str) -> dict | None:
    """Phân tích nền ngũ hành: sao ``star_vi`` đứng trên đất cung ``chi_vi``.

    Returns dict cho UI:
      {sao, hanh_sao, hanh_phu, am_duong_sao, hoa_khi, cung_chi, hanh_cung,
       am_duong_cung, quan_he{code,label,arrow}, nhan_dinh, mieu_ham,
       ghi_chu_lech (nếu bảng miếu-hãm cổ lệch chiều với sinh-khắc hành đơn)}
    """
    star = _STAR_BY_NAME.get(star_vi)
    hanh_cung = HANH_CHI.get(chi_vi)
    if star is None or hanh_cung is None:
        return None
    hanh_sao, hanh_phu = _hanh_chinh(star.ngu_hanh)
    qh = quan_he(hanh_sao, hanh_cung)
    nhan_dinh = _NHAN_DINH_SAO_CUNG.get(qh["code"], "")

    level = level_at(star_vi, chi_vi)

    # Trung thực đa tầng: sinh-khắc hành đơn vs bảng miếu-hãm cổ truyền
    ghi_chu_lech = None
    thuan_codes = {"dong_hanh", "b_sinh_a"}
    nghich_codes = {"b_khac_a", "a_sinh_b"}
    if level in ("miếu", "vượng") and qh["code"] in nghich_codes:
        ghi_chu_lech = (
            f"Bảng cổ truyền (Q2) xếp {star_vi} {level.upper()} tại {chi_vi} dù hành đơn "
            f"không thuận — cổ nhân xét thêm tổ hợp sao, thế nhật nguyệt và cách cục, "
            "không chỉ một cặp hành. Hai tầng cùng được giữ để đối chiếu."
        )
    elif level in ("hãm", "lạc") and qh["code"] in thuan_codes:
        ghi_chu_lech = (
            f"Hành đơn thuận nhưng bảng cổ truyền (Q2) xếp {star_vi} {level.upper()} tại "
            f"{chi_vi} — cổ nhân xét thêm nhiều yếu tố ngoài một cặp hành. "
            "Hai tầng cùng được giữ để đối chiếu."
        )

    return {
        "sao": star_vi,
        "hanh_sao": hanh_sao,
        "hanh_phu": hanh_phu,
        "hanh_sao_van_dong": HANH_VAN_DONG.get(hanh_sao),
        "am_duong_sao": star.am_duong,
        "hoa_khi": star.hoa_khi,
        "cung_chi": chi_vi,
        "hanh_cung": hanh_cung,
        "hanh_cung_van_dong": HANH_VAN_DONG.get(hanh_cung),
        "am_duong_cung": AM_DUONG_CHI.get(chi_vi),
        "quan_he": qh,
        "nhan_dinh": nhan_dinh,
        "mieu_ham": level,
        "ghi_chu_lech": ghi_chu_lech,
    }


@lru_cache(maxsize=1)
def vong_sinh_khac() -> dict:
    """Bảng nền cho UI trang kiến thức: vòng sinh, vòng khắc, định nghĩa 5 hành.

    Khối ``nguon_goc`` bồi từ vòng đọc sâu "Học Thuyết Âm Dương Ngũ Hành"
    (Lê Văn Sửu) — vòng 1 p1-20, 2026-06-13.
    """
    return {
        "dinh_nghia": {
            "am_duong": "Âm dương là 2 trạng thái vận động của một sự vật — "
                        "hoạt động/nghỉ, mở/thu, nóng/lạnh — không phải 2 phe tốt xấu.",
            "ngu_hanh": "Ngũ hành là 5 kiểu vận động của năng lượng; tên gỗ-lửa-đất-"
                        "kim-nước chỉ là cách đặt cho dễ nhớ.",
            "sinh_khac": "Sinh không hẳn tốt, khắc không hẳn xấu — không có khắc thì "
                         "không có định hình, như luận bệnh: không có khắc là hỏng.",
            "khi_hoa": "Ngũ hành KHÔNG phải 5 chất liệu cấu thành vật chất (cách hiểu sai "
                       "phổ biến). Theo Tuệ Tĩnh (thiền sư Việt thế kỷ 13): 'khí hóa' là khi "
                       "khí hậu môi trường biến đổi (biểu thị bằng năm màu) làm vạn vật biến "
                       "đổi tương ứng (biểu thị bằng năm hành) — diễn đạt bằng chữ 'sinh'. "
                       "Năm khí theo tỷ lệ nhiệt-ẩm: phong, hàn, thử, thấp, táo.",
            "khong_phai_dinh_menh": "Ngũ hành trước hết là quy luật vận động TỰ NHIÊN của "
                       "thiên nhiên, vạn vật, con người — không phù hợp với bất kỳ suy diễn chủ "
                       "quan nào trái quy luật tự nhiên (Lê Văn Sửu phê phán việc gán ngũ hành "
                       "làm công cụ định mệnh/chính trị).",
            "dinh_nghia_nguon": "Tuệ Tĩnh (khí hóa) + Lê Văn Sửu phân tích, p65, p68",
        },
        "ung_dung_da_mon": [
            "Thiên văn (ngũ tinh, 28 tú)", "Địa lý / phong thủy (bát trạch, tam nguyên)",
            "Binh pháp", "Vũ thuật (ngũ hình)", "Ngôn ngữ", "Văn học (nhân vật theo ngũ hành)",
            "Nghệ thuật tạo hình", "Tướng pháp (Ma Y Thần Tướng)",
            "Chiêm tinh (Bát Tự Hà Lạc · Tử Bình · Tử Vi)", "Y học (kinh lạc, tạng phủ, ngũ vận lục khí)",
        ],
        "tu_vi_dung_sinh_khac": "Sách xác nhận: luận Tử Vi dựa phần lớn vào quan hệ SINH-KHẮC "
                       "ngũ hành — so sánh sao↔cung, sao↔sao, sao↔địa chi (Lê Văn Sửu p73-74).",
        "nguon_goc": {
            "tom_tat": (
                "Học thuyết sinh từ nhu cầu sinh tồn ở Phương Đông — vùng đất kẹp giữa "
                "các cực đối nghịch lớn nhất (biển lớn nhất phía đông, núi cao nhất phía tây, "
                "hàn đới bắc, xích đạo nam) với gió bốn mùa bốn tính chất. Người xưa ghi chép "
                "'khí ứng' (vật biến đổi tương ứng với thời gian, nơi chốn), so sánh các 'tượng' "
                "đối lập mà quy thành hai loại âm–dương; rồi vì hai mặt không đủ tả trọn quá trình "
                "sinh → trưởng → suy → diệt nên chia thành NĂM BƯỚC — đó là ngũ hành. "
                "Ngũ hành nguyên thủy là 5 giai đoạn của một quá trình, không phải 5 chất liệu."
            ),
            "bon_quy_luat": (
                "Năm bước tác động qua lại thành 4 quy luật: tương sinh, tương khắc, "
                "tương chế, tương hóa (hệ hiện hiển thị sinh–khắc; chế–hóa sẽ bổ sung "
                "khi đọc tới chương chuyên sâu)."
            ),
            "the_dung": (
                "Tiên thiên bát quái (Phục Hy) là cái THỂ của âm dương; Hậu thiên bát quái "
                "(Văn Vương, theo tứ thời bát tiết) là cái DỤNG — hai tầng chức năng, "
                "không phải hai phiên bản cạnh tranh."
            ),
            "truc_thoi_gian": (
                "Cái quyết định sự thay đổi giá trị tương tác của âm dương trong vạn vật "
                "là sự vận động của vũ trụ tính bằng ĐƠN VỊ THỜI GIAN — đối ứng hiện đại "
                "là 'nhịp thời sinh học' (chronobiology)."
            ),
            "nguon": "Lê Văn Sửu — Học Thuyết Âm Dương Ngũ Hành, p4-20 (vòng đọc sâu 1, 2026-06-13)",
        },
        "hanh": HANH_VAN_DONG,
        "khi_hoa_mua": KHI_HOA_MUA,
        "khi_hoa_nguon": "Lê Văn Sửu p49 — 'Xuân Sinh, Hạ Trưởng, Trưởng Hạ Hóa, Thu Thâu, Đông Tàng'",
        "nhiet_am": NGU_HANH_NHIET_AM,
        "hanh_tho_3_the": HANH_THO_3_THE,
        "nhiet_am_nguon": "Lê Văn Sửu p90 (Bảng 3-3) — lượng hóa ngũ hành thành tọa độ nhiệt × ẩm; "
                          "hành Thổ = trạng thái cân bằng (tổng nhiệt+ẩm = 100%), giải bí ẩn vị trí Thổ",
        "vong_sinh": [["mộc", "hỏa"], ["hỏa", "thổ"], ["thổ", "kim"], ["kim", "thủy"], ["thủy", "mộc"]],
        "vong_khac": [["mộc", "thổ"], ["thổ", "thủy"], ["thủy", "hỏa"], ["hỏa", "kim"], ["kim", "mộc"]],
        "sinh_khac_che_hoa": sinh_khac_che_hoa_payload(),
        "sinh_vuong_mo": {
            "bang": SINH_VUONG_MO,
            "y_nghia": "Mỗi mùa chia 3 giai đoạn sinh-vượng-mộ ↔ 3 mức mạnh-trọng-quý. Là NỀN của "
                       "vòng Tràng Sinh 12 cung trong Tử Vi (Tràng Sinh / Đế Vượng / Mộ...).",
            "nguon": "Lê Văn Sửu p106 (Bảng 3-10)",
        },
        "ngu_hanh_quy_luat": {
            "bang": NGU_HANH_QUY_LUAT,
            "y_nghia": "Một hành hiện diện ĐỒNG DẠNG xuyên mùa / lục khí / ngũ vận / thiên can / "
                       "địa chi / tiết quý / bát quái / cửu cung / phương hướng / khí — "
                       "bằng chứng cụ thể của paradigm 'đọc đồng dạng', không phải predict.",
            "nguon": "Lê Văn Sửu p110-113 (Bảng 3-12)",
        },
        "nap_am_menh": {
            "la_gi": "Ngũ hành nạp âm 60 hoa giáp = 'MỆNH' của tuổi trong phép Tử Vi — ngũ hành "
                     "TỔNG HỢP nhiều quy luật thời gian (can chi năm, nhịp âm dương, cung độ âm "
                     "dương, bát quái, ngũ vận lục khí), mô tả một mặt khí chất con người.",
            "thuat_toan": "Lê Văn Sửu p102-103: số thứ tự can chi trong 60 hoa giáp → quy về ≤30 → "
                          "đổi chẵn-lẻ theo mốc 12 → chia 8 lấy dư → tra cung quái → lấy hành cung "
                          "quái làm nạp âm. VD Giáp Thân (21) → 22 → chia 8 dư 6 = Khảm = Thủy.",
            "biet_le": "Mậu Tý, Kỷ Sửu, Mậu Ngọ, Kỷ Mùi: theo bát quái ra Kim nhưng lấy HỎA "
                       "(tích lịch hỏa / thiên thượng hỏa) — vì là năm 'thiên phù' (vận đồng với khí "
                       "đều là hỏa), hỏa khí lấn át nhịp âm dương + cung quái.",
            "bang_tra": "Bảng nạp âm đầy đủ 60 hoa giáp đã có trong engine Bát Tự (NAP_AM_MAP) — khớp.",
            "nguon": "Lê Văn Sửu p102-105 (Bảng 3-8, 3-9)",
        },
        "the_dung_tinh_menh": {
            "nguyen_ly": "Cổ thư 'Thần bí dịch tinh tượng' (tr.117-118): trong tinh mệnh học, NGÃ "
                         "(người được đo mệnh / mệnh cung) = THỂ; sao vận hành đến = DỤNG (khách). "
                         "DỤNG sinh THỂ thì tốt; THỂ sinh DỤNG thì không tốt (vì tổn ở thể).",
            "luu_y_goc_nhin": "Trung thực: bảng miếu-hãm cổ phần nhiều xét SỨC SAO (sao mạnh/yếu ở "
                              "đất cung); thể-dụng ở đây xét LỢI CHO NGƯỜI (mệnh được nuôi hay bị rút). "
                              "Hai câu hỏi khác nhau, có thể lệch chiều — hệ giữ cả hai để đối chiếu.",
            "nguon": "Lê Văn Sửu p108 dẫn Thần bí dịch tinh tượng tr.117-118",
        },
        "xuat_xu": {
            "ban_chat_la_ty_le_khi": "BẢN CHẤT ngũ hành là TỶ LỆ KHÍ (nhiệt-ẩm), KHÔNG phải "
                       "phương hướng. Phương hướng (đông=mộc, tây=kim...) chỉ đúng với địa lý "
                       "Phương Đông (đông biển ẩm, tây núi khô). Sang địa hình khác (vd bờ tây "
                       "lục địa Âu-Á: gió đông lại hanh khô) thì BỎ tương ứng phương hướng, chỉ "
                       "lấy TỶ LỆ KHÍ theo hành làm chính. Các tương ứng khác (màu-tạng, mùa-tâm "
                       "sinh lý) thì bất biến khắp nơi. (Lê Văn Sửu p138-140)",
            "lac_thu_khong_than_bi": "Lạc thư KHÔNG do trời định: gốc là bảng ghi Cửu Cung (chu kỳ "
                       "9 năm), mỗi năm một cung bát quái theo hướng khí tới. Bảng tỷ lệ khí theo "
                       "hướng gió, chỉ đổi một vị trí (đông nam↔tây bắc), thành ma phương tổng 300 "
                       "— cùng tính chất Lạc thư (tổng 15). 'Sự trùng lặp = cân bằng âm dương trong "
                       "tổng thể', không phải thần bí. (Lê Văn Sửu p127-130)",
            "luan_diem_tac_gia": "LUẬN ĐIỂM RIÊNG của Lê Văn Sửu (quy kết nguồn — không phải kết "
                       "luận đã được giới học thuật xác lập): học thuyết Âm Dương Ngũ Hành là của "
                       "VĂN HÓA VIỆT NAM. Lập luận: (1) địa lý sinh ra ngũ hành phải có đông-biển/"
                       "tây-núi/bắc-lạnh/nam-nóng — loại trừ chỉ còn lưu vực Dương Tử và lưu vực "
                       "HỒNG HÀ; (2) khí chất sinh học người Việt ở hai giác quan nghe-nhìn khớp "
                       "quy luật âm dương ngũ hành (tác giả hứa chứng minh ở cuối sách). Hệ TÔN "
                       "TRỌNG nhưng GẮN NHÃN ATTRIBUTION: đây là position của tác giả, cần đối "
                       "chiếu đa nguồn, KHÔNG khẳng định như sự thật lịch sử. (Lê Văn Sửu p122,133)",
            "phe_phan_dinh_menh_hoa": "Cổ nhân phong kiến biến ngũ hành (vốn là quy luật TỰ NHIÊN) "
                       "thành công cụ cai trị: 'vua = con trời thay trời điều hành'; thuận quy luật "
                       "= minh quân, trái thì đổ tội cho trời phạt cả dân tộc → ngũ hành thành mê "
                       "tín, phản quyền lợi con người. Coi ngũ hành là quy luật xã hội học/triết "
                       "học = NHẬN THỨC SAI. Củng cố Iron Rule không-predict/không-định-mệnh. "
                       "(Lê Văn Sửu p124-125)",
            "nguon": "Lê Văn Sửu — chương 'Xuất xứ quy luật ngũ hành' + 'Triển vọng', p121-140",
        },
        "ngu_hanh_than": {
            "bang": NGU_HANH_THAN,
            "y_nghia": "Ngũ hành tương ứng tạng phủ + giác quan + sắc + vị + ngũ âm — nền y học cổ. "
                       "Mỗi tạng nối một giác quan (Can-mắt, Thận-tai, Tỳ-lưỡi, Tâm-tay, Phế-mũi); "
                       "màu/vị/âm vào tạng tương ứng (xanh-chua-Giốc→Can...). Tây phương kiểm chứng: "
                       "màu xanh ảnh hưởng gan, màu đỏ ảnh hưởng tim. Ngũ âm Cung-Thương-Giốc-Chủy-Vũ "
                       "= thang ngũ cung nhạc cổ, mỗi âm một tạng một loại tiếng (ca/khóc/hô/cười/rên).",
            "nguon": "Lê Văn Sửu p143-147 (dẫn Châm cứu đại thành)",
        },
        "nhip_thoi_sinh_hoc": {
            "y_nghia": "Trục thời gian của ngũ hành được Tây phương kiểm chứng: viêm gan cấp phát "
                       "~2h sáng (giờ Sửu = Can/gan); chu kỳ tạng phủ trùng 12 địa chi; màu sắc "
                       "tác động tim mạch trùng tương ứng ngũ hành. Nơi thí nghiệm cách xa hàng "
                       "ngàn dặm + hàng ngàn năm vẫn cho tương ứng như nhau.",
            "nguon": "Lê Văn Sửu p136-137 (Dương Kế Châu, Châm cứu đại thành 1601) — điểm nối engine dong_y",
        },
        "hanh_chi": HANH_CHI,
    }
