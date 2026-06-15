"""Constants — hệ số Nguyên-Hội-Vận-Thế (chuẩn hóa từ chính văn).

Cấu trúc (Quan Vật Nội Thiên + truyền thống chuẩn hóa):
    1 nguyên = 12 hội · 1 hội = 30 vận · 1 vận = 12 thế · 1 thế = 30 năm
    → 1 vận = 360 năm · 1 hội = 10.800 năm · 1 nguyên = 129.600 năm

MỐC QUY CHIẾU (NEO LẠI 2026 — trích trực tiếp bảng 经世 trong tự tự bộ trọn
Thượng-Hạ, dẫn 何氏《皇极经世解知要》观物篇三十三 以运经世, PDF p16/in tr.11):
    经元之甲一 · 经会之午七 · 经运之辛【188】· 经世之子【2245】(一世为三十年)
    "晋怀帝...岁逢甲子, 年卦为萃" → năm GIÁP TÝ = 304 CN (Lưu Uyên xưng Hán).
    → 304 CN = Nguyên Giáp-1 · Hội NGỌ-7 · Vận 188 · Thế 2245, NĂM 1 của thế.
    (10 năm 甲子→癸酉 = 304-313 là đầu thế 2245.)
    Tự kiểm nội tại: ceil(2245/12)=188 (vận) ✓ · ceil(188/30)=7 (hội Ngọ) ✓

Suy ra NGUYEN_START_ASTRO = 304 - ((2245-1)*30 + 1) + 1 = -67016 (= 67017 TCN).
Kiểm chéo văn bản (ĐỀU KHỚP):
  · Nghiêu 2357 TCN → hội Tỵ (6), cuối hội — "trước Ngọ hội ngôi Nghiêu Thuấn" (tr.185) ✓
  · Hạ Vũ ~2070 TCN → đầu hội Ngọ (hội Ngọ khởi ~2217 TCN) — "午会由禹至今" (tr.185) ✓
  · 304 CN → thế 2245 vận 188 hội Ngọ ✓ (chính mốc neo)

(Anchor CŨ "1980=vận186/thế2227" SAI — misread; đã thay. Lệch ~74 thế so với sách.)

⚠ Bảng PHỐI QUẺ vận/thế (năm-quẻ như 304=萃 Tụy): hệ năm-quẻ chi tiết — sẽ trích
   từ bảng 经世 đầy đủ khi OCR xong bộ trọn (data/yi_publishing_mineru/hoang-cuc-kinh-the-toan-bo).
   Hội-quẻ (12 bích quái) đã có; hội Ngọ = Cấu.
"""
from __future__ import annotations

NAM_MOI_THE = 30
THE_MOI_VAN = 12
VAN_MOI_HOI = 30
HOI_MOI_NGUYEN = 12

NAM_MOI_VAN = NAM_MOI_THE * THE_MOI_VAN          # 360
NAM_MOI_HOI = NAM_MOI_VAN * VAN_MOI_HOI          # 10 800
NAM_MOI_NGUYEN = NAM_MOI_HOI * HOI_MOI_NGUYEN    # 129 600

# Mốc neo lại 2026 — bảng 经世 trong tự tự bộ trọn Thượng-Hạ (PDF p16/in tr.11)
ANCHOR_YEAR = 304           # Giáp Tý — Lưu Uyên xưng Hán (晋怀帝, 304 CN)
ANCHOR_THE = 2245           # thế thứ 2245 của nguyên
ANCHOR_NAM_TRONG_THE = 1    # 304 = năm đầu của thế 2245 (甲子 khởi thế)
ANCHOR_CITATION = "皇极经世书今说 trọn bộ, tự tự p16 (何氏皇极经世解知要 · 以运经世): 元甲1·会午7·运188·世2245, 甲子=304 CN"

# Năm đầu nguyên hiện tại (astronomical year: 0 = 1 TCN)
NGUYEN_START_ASTRO = ANCHOR_YEAR - ((ANCHOR_THE - 1) * NAM_MOI_THE + ANCHOR_NAM_TRONG_THE) + 1

HOI_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
           "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# 12 BÍCH QUÁI (辟卦) — quẻ tầng HỘI, theo vòng tiêu tức Hoàng thị Kê giải
# (tr.123 bản dịch 今说): "nhất dương sinh tại Tý (Phục) → tam dương Thái tại
# Dần → lục dương thuần Càn tại Tỵ; nhất âm Cấu tại Ngọ → tam âm Bĩ tại Thân
# → lục âm thuần Khôn tại Hợi". Khớp data point tr.167 (Bình Vương Đông thiên,
# hội Ngọ, "vận nhập vào Cấu"). Anh duyệt đưa vào engine 2026-06-11.
# Quẻ tầng VẬN/THẾ: chờ bảng chi tiết ở tập Trung/Hạ (中册/下册) — KHÔNG bịa.
HOI_QUE = {
    "Tý": {"que": "Phục", "han": "復", "tuong": "Nhất dương sinh — trời mở"},
    "Sửu": {"que": "Lâm", "han": "臨", "tuong": "Nhị dương tiến"},
    "Dần": {"que": "Thái", "han": "泰", "tuong": "Tam dương — thiên địa giao, người sinh"},
    "Mão": {"que": "Đại Tráng", "han": "大壯", "tuong": "Tứ dương tráng thịnh"},
    "Thìn": {"que": "Quải", "han": "夬", "tuong": "Ngũ dương quyết"},
    "Tỵ": {"que": "Càn", "han": "乾", "tuong": "Lục dương thuần — cực thịnh"},
    "Ngọ": {"que": "Cấu", "han": "姤", "tuong": "Nhất âm mới sinh giữa cực thịnh"},
    "Mùi": {"que": "Độn", "han": "遯", "tuong": "Nhị âm — lui ẩn"},
    "Thân": {"que": "Bĩ", "han": "否", "tuong": "Tam âm — thiên địa bất giao"},
    "Dậu": {"que": "Quán", "han": "觀", "tuong": "Tứ âm — quan chiêm"},
    "Tuất": {"que": "Bác", "han": "剝", "tuong": "Ngũ âm bác lạc"},
    "Hợi": {"que": "Khôn", "han": "坤", "tuong": "Lục âm thuần — bế tàng"},
}
HOI_QUE_CITATION = "皇极经世书今说 tr.123 (12 bích quái tiêu tức, Hoàng thị Kê) + tr.167 (kiểm chứng Bình Vương vận Cấu)"

# Đặc trưng từng hội theo truyền thống Hoàng Cực (khái lược — sẽ giàu thêm từ sách)
HOI_NOTES = {
    "Tý": "Thiên khai ư Tý — trời mở",
    "Sửu": "Địa tịch ư Sửu — đất thành",
    "Dần": "Nhân sinh ư Dần — người sinh",
    "Ngọ": "Cực thịnh chuyển vận — 'Ngọ hội về sau, vương giáng nhi bá' (tr.149)",
    "Hợi": "Bế tàng — chu kỳ khép",
}

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def can_chi_year(year: int) -> str:
    """Can chi năm dương lịch (astronomical: 1984 = Giáp Tý)."""
    return f"{CAN[(year - 4) % 10]} {CHI[(year - 4) % 12]}"
