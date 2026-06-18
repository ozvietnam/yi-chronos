"""KHỞI SỐ Thiết Bản — cấu hình + bước tính ĐỌC TỪ BẢN GỐC (in rõ, không mờ).

Nguồn: 《邵康节说易·铁板神数》Càn Tập, origin.pdf trang 9-10 (đọc thẳng ảnh scan).
Lỗi "OCR mờ" trước đây là do pipeline MinerU làm rối bảng — bản gốc CHỈNH TỀ.

Đã chốt được (đọc ảnh gốc):
  · 八卦加则: 爻从三十起, 乾卦六为头 … 遇十须不用 (luật cộng, mod-10).
  · 天干配卦 / 地支配卦 / 日主配卦 / 河洛配数 / 地支取数(Hà Đồ) — bên dưới.
  · 安身命 (chuẩn, = Tử Vi) · 五虎遁 khởi tháng · 60 纳音.
  · 考刻: cần bát tự CHA MẸ + sự kiện đời (→ tính năng GIA ĐẠO / luận lá số con cái).

CHƯA cơ học hoá ra SỐ điều văn: phép ráp cuối (八卦加则 → số) cần bảng 纳卦 từng 集
(origin page_idx 17+) + cặp kiểm. KHÔNG bịa số. Xem docs/design/THIET-BAN-KHOI-SO.md.
"""
from __future__ import annotations

CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# 天干配卦 (origin p9): 壬甲从乾, 乙→坤, 庚→艮, 辛→巽, 己→震, 戊→离, 丙→坎, 丁→兑.
# ⚠ Bản gốc chép "乙庚向坤…庚来艮上" → 庚 xuất hiện 2 nơi (坤 & 艮): cần bảng 纳卦
#   từng 集 hoặc cặp kiểm để phân định 乙/庚/癸. Tạm theo lối chuẩn-nhất, ĐÁNH DẤU.
THIEN_CAN_QUAI = {"Nhâm": "Càn", "Giáp": "Càn", "Ất": "Khôn", "Canh": "Cấn",
                  "Tân": "Tốn", "Kỷ": "Chấn", "Mậu": "Ly", "Bính": "Khảm", "Đinh": "Đoài"}
THIEN_CAN_QUAI_NOTE = "Quý chưa rõ; 庚 bản gốc lưỡng vị (坤/艮) — chờ bảng 纳卦 từng 集 phân định"

# 地支配卦 (origin p9, số Hậu Thiên/Lạc Thư): 1坎2坤3震4巽5中6乾【7艮8兑】9离
#   (bản gốc là 7艮8兑 — sửa lại nhận định cũ "7兑8艮" của mình là SAI).
DIA_CHI_QUAI = {"Tý": ("Khảm", 1), "Mùi": ("Khôn", 2), "Mão": ("Chấn", 3), "Tỵ": ("Tốn", 4),
                "Tuất": ("Càn", 6), "Sửu": ("Cấn", 7), "Thân": ("Đoài", 8), "Ngọ": ("Ly", 9)}

# 日主配卦 (origin p9): 亥子坎, 寅震, 巳午离, 丑坤, 卯酉乾, 辰兑, 未艮, 戌巽
NHAT_CHU_QUAI = {"Hợi": "Khảm", "Tý": "Khảm", "Dần": "Chấn", "Tỵ": "Ly", "Ngọ": "Ly",
                 "Sửu": "Khôn", "Mão": "Càn", "Dậu": "Càn", "Thìn": "Đoài",
                 "Mùi": "Cấn", "Tuất": "Tốn", "Thân": None}  # Thân: bản gốc chưa rõ

# 河洛配数 (origin p9, 河洛理数): can & chi → số
HA_LAC_CAN = {"Giáp": 9, "Kỷ": 9, "Ất": 8, "Canh": 8, "Bính": 7, "Tân": 7,
              "Đinh": 6, "Nhâm": 6, "Mậu": 5, "Quý": 5}
HA_LAC_CHI = {"Tý": 9, "Ngọ": 9, "Sửu": 8, "Mùi": 8, "Dần": 7, "Thân": 7,
              "Mão": 6, "Dậu": 6, "Thìn": 5, "Tuất": 5, "Tỵ": 4, "Hợi": 4}

# 地支取数 Hà Đồ (origin p10): 亥子1,6 寅卯3,8 巳午2,7 申酉4,9 辰戌丑未5,10
DIA_CHI_HA_DO = {"Hợi": (1, "Thủy"), "Tý": (6, "Thủy"), "Dần": (3, "Mộc"), "Mão": (8, "Mộc"),
                 "Tỵ": (2, "Hỏa"), "Ngọ": (7, "Hỏa"), "Thân": (4, "Kim"), "Dậu": (9, "Kim"),
                 "Thìn": (5, "Thổ"), "Tuất": (10, "Thổ"), "Sửu": (5, "Thổ"), "Mùi": (10, "Thổ")}

# 五虎遁 (origin p10, khởi 正月 theo can năm): can năm → can tháng Giêng (Dần)
NGU_HO_DON = {"Giáp": "Bính", "Kỷ": "Bính", "Ất": "Mậu", "Canh": "Mậu", "Bính": "Canh",
              "Tân": "Canh", "Đinh": "Nhâm", "Nhâm": "Nhâm", "Mậu": "Giáp", "Quý": "Giáp"}


def an_than_menh(birth_month: int, hour_branch: str, leap: bool = False) -> dict:
    """安身命 (origin p10): từ Dần khởi tháng Giêng thuận tới tháng sinh; rồi từ cung
    tháng khởi giờ Tý, NGHỊCH tới giờ sinh = Mệnh, THUẬN = Thân. Nhuận: +1 tháng."""
    m = birth_month + (1 if leap else 0)
    month_palace = (CHI.index("Dần") + (m - 1)) % 12       # cung tháng sinh
    h = CHI.index(hour_branch)
    menh = (month_palace - h) % 12                          # nghịch
    than = (month_palace + h) % 12                          # thuận
    return {"menh_chi": CHI[menh], "than_chi": CHI[than], "month_palace_chi": CHI[month_palace]}


def phoi_tru(can: str, chi: str) -> dict:
    """Phối quái + lấy số cho 1 TRỤ (can+chi). Phần KIỂM-ĐƯỢC của 起数."""
    q, lt = DIA_CHI_QUAI.get(chi, (None, None))
    ha = DIA_CHI_HA_DO.get(chi, (None, None))
    return {
        "can": can, "chi": chi,
        "can_quai": THIEN_CAN_QUAI.get(can),
        "chi_quai": q, "chi_lacthu_so": lt,
        "chi_hado_so": ha[0], "ngu_hanh": ha[1],
        "ha_lac_can_so": HA_LAC_CAN.get(can), "ha_lac_chi_so": HA_LAC_CHI.get(chi),
    }


NOT_IMPLEMENTED = ("Số điều văn cuối (八卦加则 ráp số) cần bảng 纳卦 từng 集 + cặp kiểm — "
                   "chưa cơ học hoá, không bịa. Xem docs/design/THIET-BAN-KHOI-SO.md")
