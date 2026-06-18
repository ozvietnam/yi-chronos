"""Lớp luận phái THIÊN LƯƠNG (VN cải cách 1972) — song song Trần Đoàn/Trung Châu.

Wire các phương pháp cải cách đặc trưng (Anh duyệt 2026-06-17), school=thien_luong,
KHÔNG ghi đè engine mặc định (kept_all, đa phái):
- bac_tuoi(can, chi)        : 5 bậc tuổi Can-Chi (đọc TUỔI trước SAO).
- vong_thai_tue / tu_cach   : vòng Thái Tuế CHỦ ĐẠO — tư cách/chánh danh (4 hạng người).
- am_duong_thuan_nghich     : dương nhân ở dương cung mới đắc cách.
- ngu_hanh_duc(hanh)        : Ngũ Hành → Ngũ Thường (đức tính).
- luan_thien_luong(...)     : gộp thành 1 bản đọc đồng dạng (không predict).

Nguồn: Tử Vi Nghiệm Lý Toàn Thư (Cụ Thiên Lương) — skill data/hermes_yi/skills/thien-luong/.
Paradigm: đọc đồng dạng, mệnh là động từ ("đức năng thắng số").
"""
from __future__ import annotations

# canonical lowercase (khớp la_so_input)
CHI = ["ty", "suu", "dan", "mao", "thin", "ti", "ngo", "mui", "than", "dau", "tuat", "hoi"]
CHI_VI = {"ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão", "thin": "Thìn", "ti": "Tỵ",
          "ngo": "Ngọ", "mui": "Mùi", "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi"}
CAN_VI = {"giap": "Giáp", "at": "Ất", "binh": "Bính", "dinh": "Đinh", "mau": "Mậu",
          "ky": "Kỷ", "canh": "Canh", "tan": "Tân", "nham": "Nhâm", "quy": "Quý"}
CAN_HANH = {"giap": "Mộc", "at": "Mộc", "binh": "Hỏa", "dinh": "Hỏa", "mau": "Thổ",
            "ky": "Thổ", "canh": "Kim", "tan": "Kim", "nham": "Thủy", "quy": "Thủy"}
CAN_DUONG = {"giap", "binh", "mau", "canh", "nham"}
CHI_HANH = {"dan": "Mộc", "mao": "Mộc", "ti": "Hỏa", "ngo": "Hỏa", "than": "Kim", "dau": "Kim",
            "hoi": "Thủy", "ty": "Thủy", "thin": "Thổ", "tuat": "Thổ", "suu": "Thổ", "mui": "Thổ"}
_SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
_KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}
NGU_THUONG = {"Mộc": "Nhân (thiện tâm)", "Hỏa": "Lễ", "Thổ": "Tín (thành thực)",
              "Kim": "Nghĩa (minh bạch)", "Thủy": "Trí (sáng suốt)"}

# 12 sao vòng Thái Tuế (offset từ chi năm sinh)
_TT_STARS = ["Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù", "Tử Phù",
             "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù"]
# 4 vòng tư cách (theo offset % 4)
_TT_VONG = {
    0: ("Thái Tuế", "Chính danh — sinh ra như có trách vụ với xã hội, được lòng người, chính nghĩa. "
                    "Không cần Khoa-Quyền-Lộc, có chỉ là 'gấm thêu hoa'."),
    1: ("Thiếu Dương", "Thiên phú thông minh — 'đức đáng trọng bằng ba chữ tài'; tỉnh giác sớm thì cô quả cũng hóa không."),
    2: ("Tuế Phá", "Phản cách — nghị lực ngang Thái Tuế nhưng nghịch lý nên cô thế, thất ý; "
                   "thêm Khoa-Quyền-Lộc dễ sinh việc bạo nghịch để vinh thân (lưu xú)."),
    3: ("Thiếu Âm", "Thiện chí nhưng phận hẩm — bị đời bạc đãi, trôi nổi như cánh bèo; đáng mến."),
}
_BAC = {
    1: ("Can sinh Chi", "Phúc đức quá lớn — căn bản hơn người, nền phong phú"),
    2: ("Can = Chi", "Năng lực khá đầy đủ, vững chắc"),
    3: ("Chi sinh Can", "Đời gặp may nhiều hơn thực lực"),
    4: ("Can khắc Chi", "Đời gặp nhiều trở lực, bế tắc"),
    5: ("Chi khắc Can", "Nghịch cảnh đầy rẫy chua cay — càng phải tu thân, đức năng thắng số"),
}


def _norm(c):
    return c.strip().lower() if isinstance(c, str) else c


def bac_tuoi(can: str, chi: str) -> dict:
    """5 bậc tuổi Can-Chi (Can=gốc/Phúc đức, Chi=ngọn/Thân thế)."""
    can, chi = _norm(can), _norm(chi)
    ch, cz = CAN_HANH.get(can), CHI_HANH.get(chi)
    if not ch or not cz:
        return {"bac": None}
    if _SINH.get(ch) == cz:
        b = 1
    elif ch == cz:
        b = 2
    elif _SINH.get(cz) == ch:
        b = 3
    elif _KHAC.get(ch) == cz:
        b = 4
    elif _KHAC.get(cz) == ch:
        b = 5
    else:
        b = 2
    ten, nghia = _BAC[b]
    return {"bac": b, "quan_he": ten, "y_nghia": nghia,
            "can_hanh": ch, "chi_hanh": cz, "can": CAN_VI.get(can, can), "chi": CHI_VI.get(chi, chi)}


def tu_cach_thai_tue(year_chi: str, palace_chi: str) -> dict:
    """Tư cách 1 cung theo vòng Thái Tuế (an theo chi năm sinh)."""
    year_chi, palace_chi = _norm(year_chi), _norm(palace_chi)
    if year_chi not in CHI or palace_chi not in CHI:
        return {}
    off = (CHI.index(palace_chi) - CHI.index(year_chi)) % 12
    vong, mo_ta = _TT_VONG[off % 4]
    return {"sao_thai_tue": _TT_STARS[off], "vong": vong, "mo_ta": mo_ta,
            "chinh_danh": off % 4 == 0}


def am_duong_thuan_nghich(can: str, palace_chi: str) -> dict:
    """Dương nhân ở dương cung (hoặc âm-âm) = thuận lý, đắc cách; nghịch → mang chữ 'Thiếu'."""
    can, palace_chi = _norm(can), _norm(palace_chi)
    if can not in CAN_HANH or palace_chi not in CHI:
        return {}
    nguoi_duong = can in CAN_DUONG
    cung_duong = CHI.index(palace_chi) % 2 == 0
    thuan = nguoi_duong == cung_duong
    return {"nguoi": "dương" if nguoi_duong else "âm", "cung": "dương" if cung_duong else "âm",
            "thuan_ly": thuan,
            "nhan_dinh": ("Thuận lý âm dương — đắc cách, chánh danh có nền."
                          if thuan else
                          "Nghịch lý âm dương — thua thiệt buổi ban sơ (mang chữ 'Thiếu'); "
                          "Quyền-Lộc rực rỡ cũng chỉ là 'phù vân' nếu không tu để bù.")}


def ngu_hanh_duc(hanh: str) -> str:
    return NGU_THUONG.get(hanh, "")


def luan_thien_luong(can: str, chi: str, menh_chi: str, than_chi: str) -> dict:
    """Gộp 1 bản đọc theo phái Thiên Lương (Tam Tài 3 vòng, đọc TUỔI trước SAO)."""
    can = _norm(can)
    bac = bac_tuoi(can, chi)
    menh_tc = tu_cach_thai_tue(chi, menh_chi)
    than_tc = tu_cach_thai_tue(chi, than_chi)
    menh_ad = am_duong_thuan_nghich(can, menh_chi)
    duc = ngu_hanh_duc(CAN_HANH.get(can, ""))
    # đời người = động lực Mệnh→Thân theo Thái Tuế
    dong_luc = None
    mv, tv = menh_tc.get("vong"), than_tc.get("vong")
    if mv == "Thái Tuế" and tv == "Tuế Phá":
        dong_luc = "Mệnh Thái Tuế – Thân Tuế Phá: khởi đầu đẹp rồi 'ăn năn đã muộn' — giữ mình lúc thịnh."
    elif mv == "Tuế Phá" and tv == "Thái Tuế":
        dong_luc = "Mệnh Tuế Phá – Thân Thái Tuế: chịu sóng gió trước, về sau thỏa mãn + thọ — bền chí thì hậu vận sáng."
    return {
        "school": "thien_luong",
        "bac_tuoi": bac,
        "tu_cach_menh": menh_tc,
        "tu_cach_than": than_tc,
        "am_duong_menh": menh_ad,
        "duc_ban_menh": duc,
        "dong_luc_doi_nguoi": dong_luc,
        "tong_chi": "Phái Thiên Lương đọc TUỔI (Can-Chi, vòng Thái Tuế = chánh danh) TRƯỚC chính tinh. "
                    "Mệnh là dự thảo, Thân + Đức sửa chữa — 'đức năng thắng số', 'chữ Tâm bằng ba chữ Tài'. "
                    "Đây là GÓC NHÌN phái Thiên Lương, đặt cạnh Trần Đoàn/Trung Châu (đa phái, không thay thế).",
        "paradigm": "Đọc đồng dạng, không predict. Tư cách/chánh danh là nền để VẬN HÀNH, không phải bản án.",
    }
