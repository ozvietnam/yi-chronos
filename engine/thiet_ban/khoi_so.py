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

# 太玄数 (origin p9 sách gọi "河洛配数例"; KIỂM CHÉO 3 nguồn TQ: 163/sohu/知乎 đều gọi
#   THÁI HUYỀN SỐ): 甲己子午9, 乙庚丑未8, 丙辛寅申7, 丁壬卯酉6, 戊癸辰戌5, 巳亥4.
HA_LAC_CAN = {"Giáp": 9, "Kỷ": 9, "Ất": 8, "Canh": 8, "Bính": 7, "Tân": 7,
              "Đinh": 6, "Nhâm": 6, "Mậu": 5, "Quý": 5}
HA_LAC_CHI = {"Tý": 9, "Ngọ": 9, "Sửu": 8, "Mùi": 8, "Dần": 7, "Thân": 7,
              "Mão": 6, "Dậu": 6, "Thìn": 5, "Tuất": 5, "Tỵ": 4, "Hợi": 4}
TAI_HUYEN_CAN = HA_LAC_CAN  # alias đúng tên
TAI_HUYEN_CHI = HA_LAC_CHI

# 先天八卦数 (Phục Hy): dùng ở bước ráp số (sohu xác nhận). Khác 地支配卦 (Hậu Thiên) ở trên.
TIEN_THIEN_QUAI_SO = {"Càn": 1, "Đoài": 2, "Ly": 3, "Chấn": 4,
                      "Tốn": 5, "Khảm": 6, "Cấn": 7, "Khôn": 8}

# 序数 (số thứ tự) cho công thức base: can 甲1..癸10, chi 子1..亥12.
CAN_SO = {c: i + 1 for i, c in enumerate(CAN)}
CHI_SO = {c: i + 1 for i, c in enumerate(CHI)}

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


def co_so_bac_phai(hour_branch: str, day_stem: str, dieu_chinh_so: int = 0) -> dict:
    """先天命数 base — biến thể BẮC PHÁI (lấy 时 + 日), theo ca tài liệu (163.com):
        基数 = (时支序数 × 30 + 日干序数 + 调整数) ÷ 5
    ⚠ Đây là CÔNG THỨC NỀN tài liệu hoá (北派 giản lược) — KHỚP khẩu quyết sách
    "爻从三十起" (×30). KHÔNG phải số điều văn cuối: thiếu 秘数 (lớp C) + 考刻 phải neo
    bằng lục thân. `dieu_chinh_so` = ẩn số 考刻 (xem kao_khac_khung). Không claim ra 条文."""
    ts = CHI_SO.get(hour_branch)
    ds = CAN_SO.get(day_stem)
    if ts is None or ds is None:
        return {"error": "Cần đúng can ngày + chi giờ."}
    tong = ts * 30 + ds + dieu_chinh_so
    return {
        "cong_thuc": "(时支序数×30 + 日干序数 + 调整数) ÷ 5",
        "thoi_chi_so": ts, "nhat_can_so": ds, "dieu_chinh_so": dieu_chinh_so,
        "tong": tong, "co_so": tong // 5, "du": tong % 5,
        "dong_hao": (tong % 6) or 6,  # 元堂动爻 = base mod 6 (1..6)
        "phai": "bắc (时+日)",
    }


# 考刻 — KHUNG (không phải hàm thuần): vì 调整数 phải "đối" bằng lục thân đã biết.
KAO_KHAC_LUC_THAN = [
    "Số anh chị em (mấy người, thứ mấy)",
    "Cha còn / mất (năm nào) — tuổi/con giáp cha",
    "Mẹ còn / mất (năm nào) — tuổi/con giáp mẹ",
    "Vợ/chồng — con giáp, năm cưới",
    "Số con (trai/gái)",
    "Biến cố lớn đã rồi (năm tuổi)",
]


def kao_khac_khung(known_facts: dict | None = None) -> dict:
    """考刻 = DÒ 调整数 trong không gian '8 khắc × 15 phân' sao cho điều văn lục thân
    KHỚP sự thật đã biết. Đây là phần làm nên độ chuẩn của 铁板 — và cũng là lý do nó
    KHÔNG phải hàm ngày-sinh→số. Hàm này trả KHUNG (cần gì để 考刻), KHÔNG bịa 条文."""
    have = [k for k in (known_facts or {}) if (known_facts or {}).get(k)]
    return {
        "khong_gian_do": "8 khắc × 15 phân (origin p8: 'mỗi giờ suy tám khắc, mỗi khắc suy mười lăm phân')",
        "can_doi_chieu": KAO_KHAC_LUC_THAN,
        "da_co": have,
        "con_thieu": [k for k in ["số anh em", "cha", "mẹ"] if k not in have],
        "nguon_du_kien": "bát tự + lục thân CHA MẸ → trang Gia Đạo (docs/design/GIA-DAO.md)",
        "ghi_chu": "调整数 'không tính ra được, mà đối ra' (163.com). Không đủ lục thân → "
                   "KHÔNG chốt được số điều văn. Đúng đạo: không bịa.",
    }


# Phần GIẤU (lớp C) — KHÔNG ship số điều văn:
NOT_IMPLEMENTED = (
    "Số điều văn cuối = base ± 秘数 → tra bảng 纳卦 8 集 (sách Anh CÓ chứa, page_idx 16+). "
    "Thiếu: (1) giá trị 秘数 từng loại (mọi nguồn TQ GIẤU), (2) ≥1 cặp kiểm (bát tự→số đã biết) "
    "để validate. KHÔNG bịa số đóng đinh lên đời người. Xem docs/design/THIET-BAN-KHOI-SO.md."
)
