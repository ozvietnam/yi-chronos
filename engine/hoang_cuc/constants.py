"""Constants — hệ số Nguyên-Hội-Vận-Thế (chuẩn hóa từ chính văn).

Cấu trúc (Quan Vật Nội Thiên + truyền thống chuẩn hóa):
    1 nguyên = 12 hội · 1 hội = 30 vận · 1 vận = 12 thế · 1 thế = 30 năm
    → 1 vận = 360 năm · 1 hội = 10.800 năm · 1 nguyên = 129.600 năm

MỐC QUY CHIẾU (trích từ bản dịch 今说, tr.149 & tr.185):
    "Hiện nay... hội thứ bảy của Ngọ, vận 186, thế 2227, năm Canh Thân thứ 16"
    → Canh Thân thời tác giả = 1980 CN.
    Kiểm chéo nội tại: ceil(186/30)=7 (hội Ngọ) ✓ · ceil(2227/12)=186 ✓
    Kiểm chéo văn bản: "Nghiêu Giáp Thìn ở cuối hội Tỵ" (tr.149) ✓ với epoch này.

Suy ra: năm-trong-nguyên của 1980 = (2227-1)*30 + 16 = 66.796
        → năm đầu nguyên (astronomical) = 1980 - 66796 + 1 = -64815 (= 64.816 TCN)

⚠ Bảng PHỐI QUẺ vận/thế (60 quẻ trừ Càn Khôn Khảm Ly): CHƯA nhập —
   nằm ở phần sau sách, sẽ trích khi đọc sâu tới (KHÔNG bịa).
"""
from __future__ import annotations

NAM_MOI_THE = 30
THE_MOI_VAN = 12
VAN_MOI_HOI = 30
HOI_MOI_NGUYEN = 12

NAM_MOI_VAN = NAM_MOI_THE * THE_MOI_VAN          # 360
NAM_MOI_HOI = NAM_MOI_VAN * VAN_MOI_HOI          # 10 800
NAM_MOI_NGUYEN = NAM_MOI_HOI * HOI_MOI_NGUYEN    # 129 600

# Mốc từ sách (tr.149, tr.185 bản dịch 今说)
ANCHOR_YEAR = 1980          # Canh Thân
ANCHOR_THE = 2227           # thế thứ 2227 của nguyên
ANCHOR_NAM_TRONG_THE = 16   # năm thứ 16 trong thế
ANCHOR_CITATION = "皇极经世书今说 tr.149 & tr.185 (bản dịch yi-chronos)"

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
