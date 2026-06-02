"""Mệnh Hợp Cách — 10 tiêu chuẩn scorer (Xuân Cang p.48-60).

Paradigm Xuân Cang (BÀI NĂM):
> "Mệnh hợp cách là Mệnh hoặc Cấu trúc Mệnh hợp với quy luật thuận hành
>  của Trời Đất."

10 tiêu chuẩn hợp cách (lấy quẻ Tiên Thiên làm chuẩn — quẻ chính của mệnh):

1. **Tên quẻ tốt** — Càn/Khôn/Hàm/Thái/Đại Hữu/Phong/Tỉnh/Đỉnh/Phong/Đại Tráng/Phục
   vs xấu — Truân/Khốn/Khuê/Bác/Bĩ/Khảm/Cấu/Tốn/Cách (cách mạng)
2. **Vị trí hào Nguyên Đường tốt** — 2, 5 tốt; 1, 4 TB; 3 phân tích; 6 ngoại lệ tốt cho vài quẻ
3. **Lời hào NĐ tốt** — manual flag (cần wiki citation)
4. **Được mùa sinh** — quẻ Nguyệt lệnh
5. **NĐ có yểm trợ** — hào Thế-Ứng khác cực (Dương-Âm hoặc Âm-Dương)
6. **Trị số Âm-Dương hợp mùa sinh** — Dương cao cho mùa Hạ, Âm cao cho mùa Đông, etc.
7. **Hành Mệnh gặp quẻ thuận** — Mạng Kim/Mộc/Thủy/Hỏa/Thổ × 8 quẻ (bảng 16)
8. **NĐ đáng vị** — Dương vị hào dương + 21 hào tốt
9. **Can năm sinh hợp quẻ + hợp mùa**
10. **Quần chúng theo** vs **bị quần chúng ghét**

Scoring: mỗi tiêu chuẩn đạt → +1. Tổng 0-10.
- 8-10: Khanh Tướng (top)
- 5-7: Phú Quý
- 3-4: Trung bình (đạt 3-4 đã là quý)
- 0-2: Mệnh không hợp cách

⚠️ Iron Rule #4+6: scorer là TÍN HIỆU CẤU TRÚC, không predict tĩnh.
   Anh đọc đồng dạng — quẻ phản chiếu cấu trúc khoảnh khắc sinh.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# -----------------------------------------------------------------------------
# TC1 — Tên quẻ tốt / xấu
# -----------------------------------------------------------------------------

# Nguồn: Xuân Cang p.49 + truyền thống
GOOD_NAME_HEXAGRAMS: frozenset[str] = frozenset({
    "Càn", "Khôn",                          # 2 quẻ gốc
    "Hàm", "Thái", "Đại Hữu",               # quẻ "hợp" mẫu
    "Đại Tráng", "Tấn", "Phong", "Phục",   # cát phổ thông
    "Đỉnh", "Tỉnh",                         # ổn định nuôi dưỡng
    "Khiêm",                                # nhún nhường được lòng
    "Hàm",                                  # cảm ứng giao thoa
    "Phong",                                # thịnh đại
    "Gia Nhân",                             # gia đạo
    "Tiết",                                 # tiết chế
    "Trung Phu",                            # niềm tin trong lòng
    "Tùy",                                  # thuận theo thời
})

BAD_NAME_HEXAGRAMS: frozenset[str] = frozenset({
    "Truân", "Khốn", "Khuê",                # Xuân Cang nêu rõ p.49
    "Bác",                                  # tan rã (trừ ngoại lệ tháng 9 nữ)
    "Bĩ",                                   # bế tắc
    "Cấu",                                  # bị ghét (Hào 1 Âm)
    "Khảm",                                 # tập Khảm — hãm sâu
    "Tốn",                                  # độn (ẩn trốn) — trừ tháng 6
    "Cách",                                 # cách mạng động loạn
    "Vô Vọng",                              # ngoại lệ TB (Xuân Cang p.49: "không xấu lắm")
    "Quải",                                 # bị ghét hào 6 Âm
    "Đồng Nhân",                            # bị ghét hào 2 Âm (phái phiệt)
})


# -----------------------------------------------------------------------------
# TC2 — Vị trí hào Nguyên Đường (theo Xuân Cang p.49)
# -----------------------------------------------------------------------------

# Quẻ có hào 6 cũng tốt (ngoại lệ): Cổ, Đỉnh (theo Xuân Cang)
HAO_6_TOT_QUE: frozenset[str] = frozenset({"Cổ", "Đỉnh"})


def score_hao_nguyen_duong_position(nguyen_duong_line: int, source_quai: str) -> tuple[int, str]:
    """Trả về (score, reason). Score: 1=tốt, 0=trung bình/xấu."""
    if nguyen_duong_line in (2, 5):
        return 1, f"NĐ hào {nguyen_duong_line} = đắc Trung (vị trí tốt nhất)"
    if nguyen_duong_line in (1, 4):
        return 0, f"NĐ hào {nguyen_duong_line} = trung bình"
    if nguyen_duong_line == 3:
        return 0, "NĐ hào 3 = phải cân nhắc lời hào (vị thế bất chính)"
    if nguyen_duong_line == 6:
        if source_quai in HAO_6_TOT_QUE:
            return 1, f"NĐ hào 6 = ngoại lệ tốt cho quẻ {source_quai}"
        return 0, "NĐ hào 6 = thời mạt (thường không tốt)"
    return 0, "unknown"


# -----------------------------------------------------------------------------
# TC4 — Nguyệt lệnh (quẻ chỉ định bởi tháng sinh âm lịch)
# -----------------------------------------------------------------------------

# Bảng Nguyệt Lệnh chuẩn (Xuân Cang p.51) — 12 quẻ theo 12 tháng âm lịch
# Bắt đầu tháng 11 (Tý) — quẻ Phục (1 hào dương đầu tiên)
NGUYET_LENH_TABLE: dict[int, str] = {
    11: "Phục",        # Địa Lôi Phục — 1 dương sinh
    12: "Lâm",         # Địa Trạch Lâm — 2 dương
    1: "Thái",         # Địa Thiên Thái — 3 dương 3 âm (cân bằng xuân)
    2: "Đại Tráng",    # Lôi Thiên Đại Tráng — 4 dương
    3: "Quải",         # Trạch Thiên Quải — 5 dương
    4: "Càn",          # Thuần Càn — 6 dương
    5: "Cấu",          # Thiên Phong Cấu — 1 âm đầu tiên
    6: "Độn",          # Thiên Sơn Độn — 2 âm
    7: "Bĩ",           # Thiên Địa Bĩ — 3 âm 3 dương (cân bằng thu)
    8: "Quan",         # Phong Địa Quan — 4 âm
    9: "Bác",          # Sơn Địa Bác — 5 âm
    10: "Khôn",        # Thuần Khôn — 6 âm
}


def get_nguyet_lenh(birth_month_amlich: int) -> str:
    """Lookup quẻ Nguyệt lệnh từ tháng âm lịch."""
    return NGUYET_LENH_TABLE.get(birth_month_amlich, "?")


# -----------------------------------------------------------------------------
# TC5 — Yểm trợ (Thế-Ứng khác cực)
# -----------------------------------------------------------------------------

def score_yem_tro(binary_top_down: str, the_line: int) -> tuple[int, str]:
    """Hào Thế = NĐ. Hào Ứng = cách 2 hào.
    1↔4, 2↔5, 3↔6.

    Yểm trợ TỐT khi Thế-Ứng KHÁC cực (Dương vs Âm).
    """
    # binary_top_down: index 0 = hào 6, index 5 = hào 1
    # → hào N: binary_top_down[6 - N]
    if the_line < 1 or the_line > 6:
        return 0, "invalid line"
    ung_line = the_line + 3 if the_line <= 3 else the_line - 3
    the_polarity = binary_top_down[6 - the_line]
    ung_polarity = binary_top_down[6 - ung_line]
    if the_polarity != ung_polarity:
        # Quality of support depends on positions
        if the_line in (2, 5):
            quality = "rất tốt"
        elif the_line == 1:
            quality = "tương đối tốt (hào 4 mạnh hơn ở trên)"
        elif the_line == 6:
            quality = "đáng lo (hào 3 thường bất chính)"
        else:
            quality = "trung bình"
        return 1, f"Có yểm trợ: NĐ hào {the_line} ({the_polarity_label(the_polarity)}) - hào Ứng {ung_line} ({the_polarity_label(ung_polarity)}) — {quality}"
    return 0, f"Không yểm trợ: cả Thế (hào {the_line}) và Ứng (hào {ung_line}) cùng cực {the_polarity_label(the_polarity)}"


def the_polarity_label(c: str) -> str:
    return "dương" if c == "1" else "âm"


# -----------------------------------------------------------------------------
# TC6 — Trị số Âm Dương hợp mùa sinh (Xuân Cang p.52-54)
# -----------------------------------------------------------------------------

def score_so_am_duong_hop_mua(so_duong: int, so_am: int, season_key: str) -> tuple[int, str]:
    """Mùa: 'xuan' (1-4), 'ha' (5-6 đầu 7), 'thu' (7-8-9), 'dong' (11-12 đầu 1).
    Ranh giới chính xác cần tiết khí.

    Quy tắc:
    - Xuân/Thu: ngang hòa (số Dương ~25, số Âm ~30)
    - Hạ: Dương cao + Âm thấp
    - Đông: Âm cao + Dương thấp
    """
    if season_key == "ha":
        if so_duong >= 30 and so_am <= 30:
            return 1, f"Hợp mùa Hạ: Dương {so_duong} cao, Âm {so_am} thấp (hoặc cân bằng)"
        return 0, f"Mùa Hạ cần Dương cao Âm thấp — Dương {so_duong}, Âm {so_am} (chưa hợp)"
    if season_key == "dong":
        if so_am >= 35 and so_duong <= 25:
            return 1, f"Hợp mùa Đông: Âm {so_am} cao, Dương {so_duong} thấp"
        return 0, f"Mùa Đông cần Âm cao Dương thấp — Âm {so_am}, Dương {so_duong}"
    # xuân, thu = ngang hòa
    if 18 <= so_duong <= 30 and 25 <= so_am <= 35:
        return 1, f"Hợp mùa {season_key} (ngang hòa): Dương {so_duong}, Âm {so_am}"
    return 0, f"Mùa {season_key} cần ngang hòa — Dương {so_duong}, Âm {so_am}"


# -----------------------------------------------------------------------------
# TC7 — Hành của Mệnh gặp quẻ (Bảng 16, Xuân Cang p.55-57)
# -----------------------------------------------------------------------------

# Mạng → {trigram: rating}  rating ∈ {"tốt", "tb", "xấu"}
MANG_VS_TRIGRAM: dict[str, dict[str, str]] = {
    "Kim": {
        "Càn": "tốt", "Khôn": "tốt", "Đoài": "tốt",        # phú quý / phúc / đắc địa
        "Chấn": "tốt",                                       # sở đắc
        "Cấn": "tb", "Tốn": "tb", "Khảm": "tb",             # ẩn cư / mát-lạnh / chìm nổi
        "Ly": "xấu",                                         # nghịch chiều
    },
    "Mộc": {
        "Chấn": "tốt",                                       # vinh hoa
        "Cấn": "tb", "Khôn": "tb", "Đoài": "tb",             # thuận xuân hạ / đợi thời / khởi thu
        "Càn": "tb", "Tốn": "tb",                            # hão huyền / dao động
        "Ly": "xấu", "Khảm": "xấu",                          # hương sắc tốn / hãm
    },
    "Thủy": {
        "Càn": "tốt",                                        # phát đạt
        "Chấn": "tốt", "Khôn": "tốt", "Đoài": "tốt",         # nhu thuận / hanh thông
        "Cấn": "tb", "Tốn": "tb",                            # hiểm trở / sóng gió
        "Khảm": "xấu", "Ly": "xấu",                          # hãm sâu / tranh đấu
    },
    "Hỏa": {
        "Càn": "tốt", "Tốn": "tốt", "Khôn": "tốt",           # quang minh / khởi cơ / tương đắc
        "Đoài": "tb",                                        # nên hoãn
        "Khảm": "xấu", "Cấn": "xấu", "Chấn": "xấu", "Ly": "xấu",   # phản phúc / ích kỷ / thiêu đốt / mừng giận thất thường
    },
    "Thổ": {
        "Khôn": "tốt", "Cấn": "tốt", "Ly": "tốt", "Đoài": "tốt",   # phúc trùng trùng / phát tháng tứ quý / phúc / như Càn
        "Càn": "tb",                                         # có lành có dữ
        "Khảm": "xấu", "Chấn": "xấu", "Tốn": "xấu",          # hãm / thương tổn / ồn ào
    },
}


def score_hanh_menh_vs_que(mang: str, upper_trigram: str, lower_trigram: str) -> tuple[int, str]:
    """Đánh giá Mạng (nạp âm hoặc Can-Chi) với 2 trigram quẻ Tiên Thiên."""
    table = MANG_VS_TRIGRAM.get(mang)
    if not table:
        return 0, f"Mạng {mang} không có trong bảng"
    ratings = []
    for t in (upper_trigram, lower_trigram):
        ratings.append(table.get(t, "tb"))
    tot_count = ratings.count("tốt")
    xau_count = ratings.count("xấu")
    if tot_count >= 1 and xau_count == 0:
        return 1, f"Mạng {mang} gặp {upper_trigram}-{lower_trigram} = {ratings} → thuận"
    return 0, f"Mạng {mang} gặp {upper_trigram}-{lower_trigram} = {ratings} → chưa thuận"


# -----------------------------------------------------------------------------
# TC8 — NĐ đáng vị (Dương vị hào dương + 21 hào tốt + 14 hào xấu)
# -----------------------------------------------------------------------------

# 21 hào đáng vị (Xuân Cang p.57) — partial extract, OCR có nhiễu
# Format: (quẻ, hào)
HAO_DANG_VI: frozenset[tuple[str, int]] = frozenset({
    ("Cấu", 5),
    ("Tấn", 3),
    ("Tiết", 4),
    ("Ký Tế", 5),
    ("Lý", 6),
    ("Tỉnh", 5),
    ("Tùy", 5),
    ("Tốn", 5),
    ("Gia Nhân", 4),
    ("Khiêm", 2),
    ("Cổ", 2),
    ("Hoán", 2),
    ("Đồng Nhân", 2),
    ("Khôn", 4),
    ("Lâm", 2),
    ("Quải", 5),
    ("Kiển", 5),
})

# 14 hào KHÔNG đáng vị
HAO_KHONG_DANG_VI: frozenset[tuple[str, int]] = frozenset({
    ("Bĩ", 3),
    ("Tấn", 4),
    ("Khuê", 3),
    ("Trung Phu", 3),
    ("Phong", 4),
    ("Chấn", 4),
    ("Dự", 3),
    ("Thăng", 3),
    ("Vị Tế", 3),
    ("Quải", 3),
    ("Nhu", 4),
    ("Đoài", 3),
    ("Tụy", 3),
    ("Tiểu Quá", 4),
})


def score_dang_vi(source_quai: str, nguyen_duong_line: int, year_polarity: str, binary_top_down: str) -> tuple[int, str]:
    """3 điều kiện:
    1. Năm Dương → NĐ ngồi hào Dương; Năm Âm → NĐ ngồi hào Âm
    2. Đối chiếu 21 hào đáng vị
    3. Đối chiếu 14 hào không đáng vị
    """
    nd_polarity = binary_top_down[6 - nguyen_duong_line]
    nd_is_yang = nd_polarity == "1"
    year_is_yang = year_polarity == "dương"

    reasons = []
    score = 0

    # ĐK1
    if year_is_yang == nd_is_yang:
        reasons.append(f"Năm {year_polarity} + NĐ {'dương' if nd_is_yang else 'âm'} = đồng cực (đáng vị)")
        score += 1
    else:
        reasons.append(f"Năm {year_polarity} + NĐ {'dương' if nd_is_yang else 'âm'} = trái cực")

    # ĐK2 + ĐK3
    if (source_quai, nguyen_duong_line) in HAO_DANG_VI:
        reasons.append(f"({source_quai}, hào {nguyen_duong_line}) ∈ 21 hào đáng vị")
        score += 1
    if (source_quai, nguyen_duong_line) in HAO_KHONG_DANG_VI:
        reasons.append(f"⚠️ ({source_quai}, hào {nguyen_duong_line}) ∈ 14 hào KHÔNG đáng vị")
        score -= 1

    final = 1 if score >= 1 else 0
    return final, " | ".join(reasons)


# -----------------------------------------------------------------------------
# TC10 — Quần chúng theo / bị ghét
# -----------------------------------------------------------------------------

# 8 quẻ có quần chúng theo (Xuân Cang p.59) — quẻ + hào chủ
QUE_QUAN_CHUNG_THEO: dict[str, int] = {
    "Phục":     1,  # hào 1 dương
    "Sư":       2,  # hào 2 dương
    "Khiêm":    3,  # hào 3 dương
    "Dự":       4,  # hào 4 dương
    "Tỷ":       5,  # hào 5 dương
    "Tiểu Súc": 4,  # hào 4 âm
    "Đỉnh":     5,  # hào 5 âm
    "Bác":      6,  # hào 6 dương
}

# 3 quẻ bị quần chúng ghét
QUE_BI_GHET: dict[str, int] = {
    "Cấu":       1,  # hào 1 âm
    "Đồng Nhân": 2,  # hào 2 âm
    "Quải":      6,  # hào 6 âm
}


def score_quan_chung(source_quai: str, nguyen_duong_line: int) -> tuple[int, str]:
    """+1 nếu quẻ có quần chúng theo + NĐ trùng hào chủ.
    -1 nếu quẻ bị ghét."""
    if source_quai in QUE_QUAN_CHUNG_THEO:
        hao_chu = QUE_QUAN_CHUNG_THEO[source_quai]
        if hao_chu == nguyen_duong_line:
            return 1, f"Quẻ {source_quai} = quần chúng theo + NĐ trùng hào chủ ({hao_chu}) → Mệnh công tác quần chúng tốt"
        return 1, f"Quẻ {source_quai} = quần chúng theo (NĐ hào {nguyen_duong_line} ≠ hào chủ {hao_chu})"
    if source_quai in QUE_BI_GHET:
        return -1, f"⚠️ Quẻ {source_quai} = quần chúng ghét"
    return 0, "Quẻ trung tính về quần chúng"


# -----------------------------------------------------------------------------
# ORCHESTRATOR
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class MenhHopCachResult:
    score: int                       # 0-10 (có thể âm nếu bị ghét)
    grade: str                       # "khanh_tuong" | "phu_quy" | "trung_binh" | "khong_hop_cach"
    breakdown: dict                  # tc1..tc10 details
    verdict: str                     # human-readable summary
    paradigm_guard: str

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_menh_hop_cach(
    *,
    source_quai_name: str,           # tên quẻ Tiên Thiên (vd "Tiết")
    upper_trigram: str,              # vd "Khảm"
    lower_trigram: str,              # vd "Đoài"
    binary_top_down: str,            # 6 char
    nguyen_duong_line: int,          # 1-6
    year_polarity: str,              # "dương" | "âm"
    so_duong: int,                   # số Dương raw
    so_am: int,                      # số Âm raw
    season_key: str,                 # "xuan"|"ha"|"thu"|"dong"
    birth_month_amlich: int | None = None,
    mang_nap_am: str | None = None,  # "Kim"|"Mộc"|"Thủy"|"Hỏa"|"Thổ"
) -> MenhHopCachResult:
    """Compute Mệnh Hợp Cách score (0-10).

    Lấy quẻ Tiên Thiên + NĐ Tiên Thiên làm chuẩn (quẻ chính của mệnh).
    """
    breakdown = {}
    total = 0

    # TC1 — Tên quẻ
    if source_quai_name in GOOD_NAME_HEXAGRAMS:
        breakdown["tc1_ten_que"] = {"score": 1, "reason": f"Tên quẻ {source_quai_name} = tốt"}
        total += 1
    elif source_quai_name in BAD_NAME_HEXAGRAMS:
        breakdown["tc1_ten_que"] = {"score": 0, "reason": f"⚠️ Tên quẻ {source_quai_name} = xấu"}
    else:
        breakdown["tc1_ten_que"] = {"score": 0, "reason": f"Tên quẻ {source_quai_name} = trung tính"}

    # TC2 — Vị trí NĐ
    s2, r2 = score_hao_nguyen_duong_position(nguyen_duong_line, source_quai_name)
    breakdown["tc2_vi_tri_nd"] = {"score": s2, "reason": r2}
    total += s2

    # TC3 — Lời hào NĐ (cần wiki citation, để TODO)
    breakdown["tc3_loi_hao_nd"] = {"score": 0, "reason": "TODO: cần wiki Hà Lạc citation cho 384 hào"}

    # TC4 — Nguyệt lệnh
    if birth_month_amlich:
        nl_que = get_nguyet_lenh(birth_month_amlich)
        if nl_que == source_quai_name:
            breakdown["tc4_nguyet_lenh"] = {"score": 1, "reason": f"Quẻ {source_quai_name} = quẻ Nguyệt Lệnh tháng {birth_month_amlich}"}
            total += 1
        else:
            breakdown["tc4_nguyet_lenh"] = {"score": 0, "reason": f"Tháng {birth_month_amlich} Nguyệt Lệnh = {nl_que}, quẻ Mệnh = {source_quai_name}"}
    else:
        breakdown["tc4_nguyet_lenh"] = {"score": 0, "reason": "Thiếu tháng âm lịch"}

    # TC5 — Yểm trợ
    s5, r5 = score_yem_tro(binary_top_down, nguyen_duong_line)
    breakdown["tc5_yem_tro"] = {"score": s5, "reason": r5}
    total += s5

    # TC6 — Số Âm Dương hợp mùa
    s6, r6 = score_so_am_duong_hop_mua(so_duong, so_am, season_key)
    breakdown["tc6_so_am_duong"] = {"score": s6, "reason": r6}
    total += s6

    # TC7 — Hành Mệnh gặp quẻ
    if mang_nap_am:
        s7, r7 = score_hanh_menh_vs_que(mang_nap_am, upper_trigram, lower_trigram)
        breakdown["tc7_hanh_menh"] = {"score": s7, "reason": r7}
        total += s7
    else:
        breakdown["tc7_hanh_menh"] = {"score": 0, "reason": "Thiếu nạp âm"}

    # TC8 — Đáng vị
    s8, r8 = score_dang_vi(source_quai_name, nguyen_duong_line, year_polarity, binary_top_down)
    breakdown["tc8_dang_vi"] = {"score": s8, "reason": r8}
    total += s8

    # TC9 — Can năm hợp quẻ + hợp mùa: cần CAN_TO_TRIGRAM lookup (đã có ở hoa_cong.py)
    # Cross-ref đơn giản: nếu TNK present (đã xét ở hoa_cong) → +1
    breakdown["tc9_can_nam"] = {"score": 0, "reason": "TODO: cross-ref TNK từ hoa_cong"}

    # TC10 — Quần chúng
    s10, r10 = score_quan_chung(source_quai_name, nguyen_duong_line)
    breakdown["tc10_quan_chung"] = {"score": s10, "reason": r10}
    total += s10

    # Grade
    if total >= 8:
        grade = "khanh_tuong"
        verdict = f"Đạt {total}/10 — Khanh Tướng (có thể đạt chức vị cao)"
    elif total >= 5:
        grade = "phu_quy"
        verdict = f"Đạt {total}/10 — Phú Quý (3-4 đã quý, 5-7 phú quý)"
    elif total >= 3:
        grade = "trung_binh"
        verdict = f"Đạt {total}/10 — Đạt 3-4 tiêu chuẩn đã là quý"
    else:
        grade = "khong_hop_cach"
        verdict = f"Đạt {total}/10 — Mệnh không hợp cách (cần xét kỹ paradigm Iron Rule #4+6)"

    return MenhHopCachResult(
        score=total,
        grade=grade,
        breakdown=breakdown,
        verdict=verdict,
        paradigm_guard=(
            "⚠️ Mệnh Hợp Cách = đọc đồng dạng cấu trúc khoảnh khắc sinh, "
            "KHÔNG phải predict tĩnh đời người. Iron Rule #4+6."
        ),
    )
