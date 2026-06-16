"""Năm-quẻ (值年卦) — HỆ FLAT 值年 (ĐÃ HẠ CẤP 2026-06-16, founder chốt "bỏ sohu").

⚠ KHÔNG dùng làm hệ chính nữa. Hệ chính = `khoi_so.year_que_method` (经世 nested,
phép sách, kiểm 10/10 chính văn). File này GIỮ lại vì: (1) cụm 304-313 là dữ liệu
GỐC trùng khớp cả hai hệ — làm mốc kiểm chéo; (2) ghi nhận hệ flat phổ thông (sohu
vòng-60) để đối chiếu lịch sử. cast/api/web đã chuyển hết sang year_que_method.

----- (mô tả gốc giữ nguyên bên dưới) -----

Năm-quẻ (值年卦) — quẻ trực năm trong Hoàng Cực Kinh Thế.

Hệ năm-quẻ KHÔNG theo vòng can-chi cố định: cùng năm Giáp Tý mà 304=革 Cách
còn 2044=大過 Đại Quá → quẻ LỒNG theo vận/thế, suy bằng biến hào (邵雍变卦法).
Sách 今说 (tr.~tự tự) chính văn gọi đây là phép bí truyền: "除张行成、祝泌等数
家外，能明其理者甚鲜" — ít người hiểu cách suy.

NGUỒN DỮ LIỆU (2 lớp, có kiểm chéo):
  1) CHÍNH VĂN — 皇极经世书今说 bộ trọn, thế 2245 (304-313 CN), 10 năm đầu:
     甲子革·乙丑同人·丙寅临·丁卯损·戊辰节·己巳中孚·庚午归妹·辛未睽·壬申兑·癸酉履
  2) BẢNG 值年卦 2020-2103 — tổng hợp hiện đại (sohu 737303761), KIỂM CHÉO khớp
     TUYỆT ĐỐI chính văn: 2025-2034 = 革·同人·临·损·节·中孚·归妹·睽·兑·履 (y hệt 304-313).
     → bảng đáng tin trong khoảng 2020-2103.

⚠ GIỚI HẠN TRUNG THỰC:
  - 1988-2019: CHƯA có trong nguồn xác → nam_que() trả None (không suy ngoại để bịa).
  - 2043-2044: nguồn ghi cả hai = 大過 (nghi lỗi bảng, đánh dấu suspect=True).
  - Ngoài [304-313] ∪ [2020-2103]: None — cần bảng 经世 gốc (卷1-6) hoặc tái dựng
    thuật toán biến hào (张行成《索隐》/ 祝泌《起数诀》) rồi kiểm khớp 2 lớp trên.
"""
from __future__ import annotations

# 60 quẻ dùng cho năm-quẻ = 64 quẻ BỎ 4 quẻ thuần (乾坤坎离, page 335 chính văn).
# simplified-Han → (tên Việt ngắn, số King Wen)
HEX_VI: dict[str, tuple[str, int]] = {
    "屯": ("Truân", 3), "蒙": ("Mông", 4), "需": ("Nhu", 5), "讼": ("Tụng", 6),
    "师": ("Sư", 7), "比": ("Tỷ", 8), "小畜": ("Tiểu Súc", 9), "履": ("Lý", 10),
    "泰": ("Thái", 11), "否": ("Bĩ", 12), "同人": ("Đồng Nhân", 13), "大有": ("Đại Hữu", 14),
    "谦": ("Khiêm", 15), "豫": ("Dự", 16), "随": ("Tùy", 17), "蛊": ("Cổ", 18),
    "临": ("Lâm", 19), "观": ("Quán", 20), "噬嗑": ("Phệ Hạp", 21), "贲": ("Bí", 22),
    "剥": ("Bác", 23), "复": ("Phục", 24), "无妄": ("Vô Vọng", 25), "大畜": ("Đại Súc", 26),
    "颐": ("Di", 27), "大过": ("Đại Quá", 28), "咸": ("Hàm", 31), "恒": ("Hằng", 32),
    "遁": ("Độn", 33), "大壮": ("Đại Tráng", 34), "晋": ("Tấn", 35), "明夷": ("Minh Di", 36),
    "家人": ("Gia Nhân", 37), "睽": ("Khuê", 38), "蹇": ("Kiển", 39), "解": ("Giải", 40),
    "损": ("Tổn", 41), "益": ("Ích", 42), "夬": ("Quải", 43), "姤": ("Cấu", 44),
    "萃": ("Tụy", 45), "升": ("Thăng", 46), "困": ("Khốn", 47), "井": ("Tỉnh", 48),
    "革": ("Cách", 49), "鼎": ("Đỉnh", 50), "震": ("Chấn", 51), "艮": ("Cấn", 52),
    "渐": ("Tiệm", 53), "归妹": ("Quy Muội", 54), "丰": ("Phong", 55), "旅": ("Lữ", 56),
    "巽": ("Tốn", 57), "兑": ("Đoài", 58), "涣": ("Hoán", 59), "节": ("Tiết", 60),
    "中孚": ("Trung Phu", 61), "小过": ("Tiểu Quá", 62), "既济": ("Ký Tế", 63), "未济": ("Vị Tế", 64),
}

# Lớp 1 — CHÍNH VĂN (thế 2245, 304-313 CN)
_CHINH_VAN_HAN = "革 同人 临 损 节 中孚 归妹 睽 兑 履".split()
NAM_QUE_CHINH_VAN: dict[int, str] = {304 + i: h for i, h in enumerate(_CHINH_VAN_HAN)}

# Lớp 2 — BẢNG 值年卦 2020-2103 (sohu, kiểm chéo khớp chính văn)
_BANG_2020 = (
    "明夷 贲 既济 家人 丰 革 同人 临 损 节 "          # 2020-2029
    "中孚 归妹 睽 兑 履 泰 大畜 需 小畜 大壮 "        # 2030-2039
    "大有 夬 姤 大过 大过 鼎 恒 巽 井 蛊 "            # 2040-2049 (2043-2044 đều 大过: nghi lỗi)
    "升 讼 困 未济 解 涣 蒙 师 遁 咸 "                # 2050-2059
    "旅 小过 渐 蹇 艮 谦 否 萃 晋 豫 "                # 2060-2069
    "观 比 剥 复 颐 屯 益 震 噬嗑 随 "                # 2070-2079
    "无妄 明夷 贲 既济 家人 丰 革 同人 临 损 "        # 2080-2089
    "节 中孚 归妹 睽 兑 履 泰 大畜 需 小畜 "          # 2090-2099
    "大壮 大有 夬 姤"                                  # 2100-2103
).split()
NAM_QUE_2020_2103: dict[int, str] = {2020 + i: h for i, h in enumerate(_BANG_2020)}

SUSPECT_YEARS = {2043, 2044}  # nguồn ghi trùng 大过 — cần kiểm bảng 经世 gốc

SRC_CHINH_VAN = "皇极经世书今说 bộ trọn (chính văn, thế 2245, 304-313 CN)"
SRC_BANG = "Bảng 值年卦 2020-2103 (tổng hợp hiện đại; kiểm chéo khớp chính văn 2025-2034≡304-313)"


def nam_que(year: int) -> dict | None:
    """Trả quẻ-năm của một năm dương lịch, KÈM nguồn. None nếu chưa có trong nguồn.

    KHÔNG suy ngoại/bịa — ngoài 304-313 và 2020-2103 đều trả None trung thực.
    """
    if year in NAM_QUE_CHINH_VAN:
        han, src, lop = NAM_QUE_CHINH_VAN[year], SRC_CHINH_VAN, "chính văn"
    elif year in NAM_QUE_2020_2103:
        han, src, lop = NAM_QUE_2020_2103[year], SRC_BANG, "bảng kiểm chéo"
    else:
        return None
    viet, kw = HEX_VI.get(han, (han, 0))
    return {
        "year": year,
        "han": han,
        "viet": viet,
        "kw": kw,
        "lop_nguon": lop,
        "source": src,
        "suspect": year in SUSPECT_YEARS,
    }


def nam_que_range(y0: int, y1: int) -> list[dict | None]:
    """Danh sách quẻ-năm [y0, y1] (None cho năm chưa có nguồn)."""
    return [nam_que(y) for y in range(y0, y1 + 1)]
