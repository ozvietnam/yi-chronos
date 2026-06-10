"""Tên Việt chuẩn cho sao + cung + can + chi — dùng cho render output user-facing."""
from __future__ import annotations

STAR_VI: dict[str, str] = {
    "tu_vi": "Tử Vi", "thien_co": "Thiên Cơ", "thai_duong": "Thái Dương",
    "vu_khuc": "Vũ Khúc", "thien_dong": "Thiên Đồng", "liem_trinh": "Liêm Trinh",
    "lien_trinh": "Liêm Trinh",
    "thien_phu": "Thiên Phủ", "thai_am": "Thái Âm", "tham_lang": "Tham Lang",
    "cu_mon": "Cự Môn", "thien_tuong": "Thiên Tướng", "thien_luong": "Thiên Lương",
    "that_sat": "Thất Sát", "pha_quan": "Phá Quân",
    # Phụ tinh thông dụng
    "van_xuong": "Văn Xương", "van_khuc": "Văn Khúc",
    "ta_phu": "Tả Phụ", "huu_bat": "Hữu Bật",
    "thien_khoi": "Thiên Khôi", "thien_viet": "Thiên Việt",
    "loc_ton": "Lộc Tồn", "thien_ma": "Thiên Mã",
    "kinh_duong": "Kình Dương", "da_la": "Đà La",
    "hoa_tinh": "Hỏa Tinh", "linh_tinh": "Linh Tinh",
    "dia_khong": "Địa Không", "dia_kiep": "Địa Kiếp",
    "hoa_loc": "Hóa Lộc", "hoa_quyen": "Hóa Quyền",
    "hoa_khoa": "Hóa Khoa", "hoa_ky": "Hóa Kỵ",
}

CHI_VI: dict[str, str] = {
    "ty": "Tý", "suu": "Sửu", "dan": "Dần", "mao": "Mão",
    "thin": "Thìn", "ti": "Tỵ", "ngo": "Ngọ", "mui": "Mùi",
    "than": "Thân", "dau": "Dậu", "tuat": "Tuất", "hoi": "Hợi",
}

CAN_VI: dict[str, str] = {
    "giap": "Giáp", "at": "Ất", "binh": "Bính", "dinh": "Đinh",
    "mau": "Mậu", "ky": "Kỷ", "canh": "Canh", "tan": "Tân",
    "nham": "Nhâm", "quy": "Quý",
}

PALACE_VI: dict[str, str] = {
    "menh": "Mệnh", "phu_mau": "Phụ Mẫu", "phuc_duc": "Phúc Đức",
    "dien_trach": "Điền Trạch", "quan_loc": "Quan Lộc", "no_boc": "Nô Bộc",
    "thien_di": "Thiên Di", "tat_ach": "Tật Ách", "tai_bach": "Tài Bạch",
    "tu_tuc": "Tử Tức", "phu_the": "Phu Thê", "huynh_de": "Huynh Đệ",
    # chi-based palaces dùng CHI_VI
    **CHI_VI,
}

CUC_VI: dict[str, str] = {
    "thuy_nhi_cuc": "Thủy Nhị Cục", "moc_tam_cuc": "Mộc Tam Cục",
    "kim_tu_cuc": "Kim Tứ Cục", "tho_ngu_cuc": "Thổ Ngũ Cục",
    "hoa_luc_cuc": "Hỏa Lục Cục",
}


def vi_star(s: str) -> str:
    return STAR_VI.get(s.lower().strip(), s.replace("_", " ").title())


def vi_chi(c: str) -> str:
    return CHI_VI.get(c.lower().strip(), c.title())


def vi_can(c: str) -> str:
    return CAN_VI.get(c.lower().strip(), c.title())


def vi_palace(p: str) -> str:
    return PALACE_VI.get(p.lower().strip(), p.replace("_", " ").title())


def vi_cuc(c: str) -> str:
    return CUC_VI.get(c.lower().strip(), c.replace("_", " ").title())
