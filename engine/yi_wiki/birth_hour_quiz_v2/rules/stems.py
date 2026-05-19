"""Ten Heavenly Stems — element, yin/yang, and day-master physical baseline."""
from __future__ import annotations

STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

STEM_ELEMENTS = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hoả", "Đinh": "Hoả",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thuỷ", "Quý": "Thuỷ",
}

STEM_YIN_YANG = {
    "Giáp": "Dương", "Ất": "Âm",
    "Bính": "Dương", "Đinh": "Âm",
    "Mậu": "Dương", "Kỷ": "Âm",
    "Canh": "Dương", "Tân": "Âm",
    "Nhâm": "Dương", "Quý": "Âm",
}

# Day Master baseline — physical defaults derived from Tướng Pháp Cổ.
# Modifiers from năm/tháng/giờ chi adjust these in physical.py.
DAY_MASTER_BASELINE = {
    "Giáp": {"body_height": "cao",        "body_build": "gay_thon",   "face_shape": "dai",   "skin_tone": "trang",    "hair_quality": "thang_cung"},
    "Ất":   {"body_height": "cao",        "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
    "Bính": {"body_height": "trung_binh", "body_build": "trung_binh", "face_shape": "nhon",  "skin_tone": "hong_hao", "hair_quality": "day_muot"},
    "Đinh": {"body_height": "trung_binh", "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "hong_hao", "hair_quality": "mong"},
    "Mậu":  {"body_height": "trung_binh", "body_build": "dam_chac",   "face_shape": "vuong", "skin_tone": "sam",      "hair_quality": "thang_cung"},
    "Kỷ":   {"body_height": "trung_binh", "body_build": "day_dan",    "face_shape": "tron",  "skin_tone": "vua",      "hair_quality": "day_muot"},
    "Canh": {"body_height": "trung_binh", "body_build": "dam_chac",   "face_shape": "vuong", "skin_tone": "trang",    "hair_quality": "thang_cung"},
    "Tân":  {"body_height": "trung_binh", "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
    "Nhâm": {"body_height": "cao",        "body_build": "day_dan",    "face_shape": "tron",  "skin_tone": "vua",      "hair_quality": "xoan"},
    "Quý":  {"body_height": "trung_binh", "body_build": "gay_thon",   "face_shape": "oval",  "skin_tone": "trang",    "hair_quality": "day_muot"},
}
