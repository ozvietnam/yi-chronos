"""Constants for Liên Hoa Độn Pháp.

Source: 'Liên Hoa Độn Pháp' (PDF in thư viện sách/LIENHOADON.pdf),
the user-uploaded canonical text for this school.

Key facts from the book:
- Uses TIÊN THIÊN bát quái order: 1.Càn 2.Đoài 3.Ly 4.Chấn 5.Tốn 6.Khảm 7.Cấn 8.Khôn.
- Ngũ hành bát quái: Kiền+Đoài=Kim, Chấn+Tốn=Mộc, Cấn+Khôn=Thổ, Ly=Hỏa, Khảm=Thủy.
- Lục thân map (đem element của đơn quái so với element của TA quái):
    same    → Huynh Đệ (H)
    sanh TA → Phụ Mẫu (P)
    TA sanh → Tử Tôn (C)
    khắc TA → Quan Quỷ (Q)
    TA khắc → Thê Tài (T)
"""

from __future__ import annotations


# Tiên thiên Phục Hy quái số 1..8.
TIEN_THIEN_TRIGRAMS = (
    "Càn",   # 1
    "Đoài",  # 2
    "Ly",    # 3
    "Chấn",  # 4
    "Tốn",   # 5
    "Khảm",  # 6
    "Cấn",   # 7
    "Khôn",  # 8
)


# Element of each trigram.
TRIGRAM_ELEMENT = {
    "Càn": "kim",
    "Đoài": "kim",
    "Ly": "hỏa",
    "Chấn": "mộc",
    "Tốn": "mộc",
    "Khảm": "thủy",
    "Cấn": "thổ",
    "Khôn": "thổ",
}


# Ngũ hành tương sanh — mộc sanh hỏa, hỏa sanh thổ, ...
ELEMENT_GENERATES = {
    "mộc": "hỏa",
    "hỏa": "thổ",
    "thổ": "kim",
    "kim": "thủy",
    "thủy": "mộc",
}

# Ngũ hành tương khắc — mộc khắc thổ, thổ khắc thủy, ...
ELEMENT_CONTROLS = {
    "mộc": "thổ",
    "thổ": "thủy",
    "thủy": "hỏa",
    "hỏa": "kim",
    "kim": "mộc",
}


# Lục thân — used as keys and Vietnamese names.
LUC_THAN_KEYS = ("H", "P", "C", "Q", "T")  # Huynh, Phụ, Tử, Quan, Tài
LUC_THAN_NAMES = {
    "H": "Huynh Đệ",
    "P": "Phụ Mẫu",
    "C": "Tử Tôn",
    "Q": "Quan Quỷ",
    "T": "Thê Tài",
}

LUC_THAN_DESCRIPTIONS = {
    "H": "Đồng hành với TA — bè đảng, vây cánh, liên kết, tổ hợp.",
    "P": "Sanh nhập TA — quý nhân, cơ may, thời vận tốt, mẫu thân, lành sự.",
    "C": "TA sanh xuất — phải chi ra (sức lực, tiền tài), lo âu, tính toán; với TA nữ là con cái.",
    "Q": "Khắc nhập TA — vận thời xấu, chướng ngại, hung sự; với TA nữ là chồng, với TA nam là con.",
    "T": "TA khắc xuất — tiền tài, thu nhập; với TA nam là vợ.",
}


# Trigram bit pattern (top-down: index 0 = top line, index 2 = bottom line).
# 1 = yang, 0 = yin.
TRIGRAM_BITS = {
    "Càn":  "111",
    "Đoài": "011",
    "Ly":   "101",
    "Chấn": "001",
    "Tốn":  "110",
    "Khảm": "010",
    "Cấn":  "100",
    "Khôn": "000",
}


# Đợt độn → số không thời (book p.19-22).
DOT_COUNT_BY_HAO = {
    1: 2,  # 9 không thời
    2: 3,  # 13 không thời
    3: 1,  # 5 không thời
    4: 2,  # 9 không thời
    5: 3,  # 13 không thời
    6: 1,  # 5 không thời
}

KHONG_THOI_COUNT_BY_DOT = {1: 5, 2: 9, 3: 13}

SOURCE_REF = "Liên Hoa Độn Pháp (thư viện sách/LIENHOADON.pdf)"
METHOD_ID = "lien_hoa_don_v1"
