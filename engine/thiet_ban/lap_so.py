"""LẬP SỐ Thiết Bản — bát tự → 先天命数/本命数/后天命数 → số điều văn.

PHÁI "五音 / 十二辟卦" (北派). Phương pháp = SỰ THẬT về 铁板神数 (không bản quyền);
code này VIẾT LẠI từ phép, KHÔNG copy repo. Mọi bảng tái dựng từ tài liệu chuẩn
(纳音歌 — sách Anh CÓ; 五音 phối số; quy tắc 考刻) + KIỂM CHÉO repo open-source
`xaminxan/tiebanshenshu` (không LICENSE → chỉ học phép) và **DB điều văn của ta**
(`tabular_verses` corpus thiet-ban-than-so — đã xác nhận CÙNG kho 12 集×1000 với repo:
子集 1001 "一树残花有枝复茂" khớp từng chữ).

KIỂM: ví dụ README repo — sinh 1924-06-15 16:00 nam, hỏi 2025-04-20 10:00
→ 先天命数 11 · 五音 2 · 日命 4 · 时运 3 · 初刻 · **本命数 344** (test_lap_so).

Đạo: đọc cái ĐÃ ĐỊNH (THỂ) để HIỂU cái nền, không hù; 考刻 cần lục thân (gia đạo).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from engine.bat_tu.tu_tru import extract_tu_tru

_ROOT = Path(__file__).resolve().parents[2]
_TABLES_PATH = _ROOT / "data/restored_books/thiet-ban-than-so/khoi_so_tables.json"
_DB_PATH = _ROOT / "data/yi_wiki/wiki.sqlite3"
_TABLES = None


def _tables() -> dict:
    global _TABLES
    if _TABLES is None:
        _TABLES = json.loads(_TABLES_PATH.read_text()) if _TABLES_PATH.exists() else {}
    return _TABLES


# Ưu tiên bản 图解 (thẩm quyền, founder chọn) → fallback DB cũ 邵乙 (2 bản khác ~38%).
_CORPUS_PRIORITY = ("thiet-ban-than-so-tujie", "thiet-ban-than-so")


def tra_dieu_van(seq_no: int) -> dict | None:
    """Tra LỜI điều văn: ưu tiên corpus 图解 (`...-tujie`), fallback DB cũ.

    Bản 图解 = thẩm quyền (founder chọn) nhưng pass MinerU mới phủ ~57% → chỗ
    trống dùng DB cũ (đánh dấu nguồn). Trả thêm `nguon` + `do_tin` (seq_confidence)."""
    if not _DB_PATH.exists():
        return None
    c = sqlite3.connect(_DB_PATH)
    try:
        for corpus in _CORPUS_PRIORITY:
            row = c.execute(
                "SELECT volume, seq_no, zh, vi, seq_confidence FROM tabular_verses "
                "WHERE book_corpus_id=? AND seq_no=? AND zh IS NOT NULL LIMIT 1",
                (corpus, seq_no)).fetchone()
            if row:
                return {"so": row[1], "volume": row[0], "zh": row[2], "vi": row[3],
                        "nguon": "图解" if corpus.endswith("tujie") else "DB-邵乙",
                        "do_tin": row[4]}
    finally:
        c.close()
    return None


def tra_luu_nien(letter: str, age: int) -> dict | None:
    """流年条文 theo (CHỮ CÁI lưu niên, TUỔI mụ): 14-14 (字母,岁)→ 条文 = 基数+加数 → tra DB.

    ⚠ Đây là bảng TRA. Cách suy CHỮ CÁI từng năm (letter-walk: 流年字母 từ
    LIUNIAN_START/SEQ + MARKER + LETTER theo 刻/后天命数) CHƯA wire — nên hàm này
    cần đưa SẴN chữ cái. Không bịa chữ cái."""
    key = f"{letter}|{age}"
    seq = (_tables().get("luu_nien_by_letter_age") or {}).get(key)
    if not seq:
        return None
    v = tra_dieu_van(seq)
    return {"chu_cai": letter, "tuoi": age, "so": seq,
            "dieu_van": (v or {}).get("zh"), "vi": (v or {}).get("vi")}


VI2CAN = {"Giáp": "甲", "Ất": "乙", "Bính": "丙", "Đinh": "丁", "Mậu": "戊",
          "Kỷ": "己", "Canh": "庚", "Tân": "辛", "Nhâm": "壬", "Quý": "癸"}
VI2CHI = {"Tý": "子", "Sửu": "丑", "Dần": "寅", "Mão": "卯", "Thìn": "辰", "Tỵ": "巳",
          "Ngọ": "午", "Mùi": "未", "Thân": "申", "Dậu": "酉", "Tuất": "戌", "Hợi": "亥"}
CAN = "甲乙丙丁戊己庚辛壬癸"
CHI = "子丑寅卯辰巳午未申酉戌亥"

# 六十花甲子纳音 五行 (sách Anh CÓ 纳音歌; bảng chuẩn phổ quát)
NAP_AM = {
    "甲子": "金", "乙丑": "金", "丙寅": "火", "丁卯": "火", "戊辰": "木", "己巳": "木",
    "庚午": "土", "辛未": "土", "壬申": "金", "癸酉": "金", "甲戌": "火", "乙亥": "火",
    "丙子": "水", "丁丑": "水", "戊寅": "土", "己卯": "土", "庚辰": "金", "辛巳": "金",
    "壬午": "木", "癸未": "木", "甲申": "水", "乙酉": "水", "丙戌": "土", "丁亥": "土",
    "戊子": "火", "己丑": "火", "庚寅": "木", "辛卯": "木", "壬辰": "水", "癸巳": "水",
    "甲午": "金", "乙未": "金", "丙申": "火", "丁酉": "火", "戊戌": "木", "己亥": "木",
    "庚子": "土", "辛丑": "土", "壬寅": "金", "癸卯": "金", "甲辰": "火", "乙巳": "火",
    "丙午": "水", "丁未": "水", "戊申": "土", "己酉": "土", "庚戌": "金", "辛亥": "金",
    "壬子": "木", "癸丑": "木", "甲寅": "水", "乙卯": "水", "丙辰": "土", "丁巳": "土",
    "戊午": "火", "己未": "火", "庚申": "木", "辛酉": "木", "壬戌": "水", "癸亥": "水",
}
# 五音 → số (宫5商4角3徵2羽1)
NGU_AM_SO = {"宫": 5, "商": 4, "角": 3, "徵": 2, "羽": 1}
# 五音 phối: hàng theo 先天命数 (cặp), cột theo nhóm can → 五音
NGU_AM_MAP = {  # cong_num → {nhóm_can: 五音}
    (1, 2): {"甲己": "羽", "乙庚": "徵", "丙辛": "宫", "丁壬": "角", "戊癸": "商"},
    (3, 4): {"甲己": "徵", "乙庚": "宫", "丙辛": "角", "丁壬": "商", "戊癸": "羽"},
    (5, 6): {"甲己": "角", "乙庚": "商", "丙辛": "羽", "丁壬": "徵", "戊癸": "宫"},
    (7, 8): {"甲己": "宫", "乙庚": "角", "丙辛": "商", "丁壬": "羽", "戊癸": "徵"},
    (9, 10): {"甲己": "商", "乙庚": "羽", "丙辛": "徵", "丁壬": "宫", "戊癸": "角"},
    (11, 12): {"甲己": "徵", "乙庚": "宫", "丙辛": "角", "丁壬": "商", "戊癸": "羽"},
}
NGU_HANH_IDX = {"水": 0, "火": 1, "木": 2, "金": 3, "土": 4}  # cho 日命/时运


def _can_nhom(can_zh: str) -> str:
    return ["甲己", "乙庚", "丙辛", "丁壬", "戊癸"][CAN.index(can_zh) % 5]


def _ngu_am(cong_num: int, year_can: str) -> tuple[str, int]:
    row = next(v for k, v in NGU_AM_MAP.items() if cong_num in k)
    am = row[_can_nhom(year_can)]
    return am, NGU_AM_SO[am]


def _nhat_menh(day_nayin: str, hour_can: str) -> int:
    """日命 = ((can-giờ-SINH idx + nạp-âm-ngày idx) mod 5)+1 (cấu trúc bảng 14-5)."""
    return ((CAN.index(hour_can) + NGU_HANH_IDX[day_nayin]) % 5) + 1


def _thoi_van(hour_nayin: str) -> int:
    """时运 = idx ngũ hành nạp-âm GIỜ SINH +1 (水1火2木3金4土5)."""
    return NGU_HANH_IDX[hour_nayin] + 1


def _zh_pillar(p: dict) -> str:
    return VI2CAN[p["stem"]] + VI2CHI[p["branch"]]


def lap_thiet_ban_so(birth_dt: str, gender: str,
                     timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Bát tự SINH → chuỗi số Thiết Bản CỐ ĐỊNH (THỂ). gender: nam|nữ.

    CHỈ theo giờ SINH — KHÔNG dùng giờ hỏi (founder chốt 19/6: bỏ đường giờ-hỏi vì
    mơ hồ; chốt cái cố định quan sát được trước). 考刻 chính xác khắc sinh → tinh chỉnh
    bằng LỤC THÂN (việc đời / bát tự bố mẹ ở gia đạo), KHÔNG phải giờ hỏi."""
    b = extract_tu_tru(birth_dt, timezone)
    bp = b["pillars"]
    year_can = VI2CAN[bp["year"]["stem"]]
    hour_chi = VI2CHI[bp["hour"]["branch"]]
    hour_can = VI2CAN[bp["hour"]["stem"]]
    day_zh = _zh_pillar(bp["day"])
    hour_zh = _zh_pillar(bp["hour"])
    lunar = b["lunar"]
    lmonth = lunar["month"] + (1 if lunar.get("is_leap_month") else 0)
    if lmonth > 12:
        lmonth = 1
    lday = lunar["day"]

    # ① 先天命数 (giờ sinh)
    cong = lmonth + 3 - (CHI.index(hour_chi) + 1)
    if cong <= 0:
        cong += 12
    # ② 五音命数 (năm sinh)
    am, am_so = _ngu_am(cong, year_can)
    # ③ 日命 + 时运 — đều theo GIỜ SINH (không còn giờ hỏi)
    day_life = _nhat_menh(NAP_AM[day_zh], hour_can)
    time_luck = _thoi_van(NAP_AM[hour_zh])
    s = day_life + time_luck
    # ④ 考刻 (初刻/正刻)
    yang_year = year_can in "甲丙戊庚壬"
    g = "男" if gender in ("nam", "男", "M", "m") else "女"
    nhom = "阳男阴女" if (g == "男") == yang_year else "阴男阳女"
    # 阳男阴女: >6 初刻, ≤6 正刻 | 阴男阳女: ngược lại
    khac = ("初刻" if s > 6 else "正刻") if nhom == "阳男阴女" else ("正刻" if s > 6 else "初刻")
    # ⑤ 本命数
    fact = (am_so * 5 + day_life + time_luck) - (1 if s <= 6 else 6)
    ban_menh = fact * 30 + lday
    # ⑥ 后天命数 (% 8)
    hau_thien = (cong + ban_menh) % 8 or 8
    # ⑦ 十二辟卦 (theo 刻 + 本命数) + 本命条文 (基数+序数+秘数 → tra DB ta)
    T = _tables()
    pq = ((T.get("hex_by_khac_banmenh") or {}).get(f"{khac}|{ban_menh}")
          or (T.get("hex_simple_by_banmenh") or {}).get(str(ban_menh)))
    ban_menh_dieu_van = None
    rec = (T.get("offsets_by_pq_khac_cong") or {}).get(f"{pq}|{khac}|{cong}") if pq else None
    if rec:
        CATS = [("tinh_cach", "Tính cách"), ("tai_nang", "Tài năng & tiền trình"),
                ("tai_van", "Tài vận"), ("huynh_de", "Số anh em")]
        out_cats = []
        for key, label in CATS:
            for off in rec.get(key, []):
                seq = rec["base"] + rec["seq"] + off
                v = tra_dieu_van(seq)
                out_cats.append({"muc": label, "so": seq,
                                 "dieu_van": (v or {}).get("zh"), "vi": (v or {}).get("vi")})
        ban_menh_dieu_van = {"base": rec["base"], "seq_so": rec["seq"], "muc": out_cats}

    return {
        "bat_tu_sinh": f"{_zh_pillar(bp['year'])} {_zh_pillar(bp['month'])} {day_zh} {_zh_pillar(bp['hour'])}",
        "am_lich": f"tháng {lunar['month']}{'(nhuận)' if lunar.get('is_leap_month') else ''} ngày {lday}",
        "tien_thien_menh_so": cong,
        "ngu_am": am, "ngu_am_so": am_so,
        "nhat_menh": day_life, "thoi_van": time_luck, "tong_nhat_thoi": s,
        "khao_khac": khac, "nhom_khac": nhom,
        "ban_menh_so": ban_menh,
        "hau_thien_menh_so": hau_thien,
        "thap_nhi_tich_quai": pq,
        "ban_menh_dieu_van": ban_menh_dieu_van,
        "ghi_chu": ("Bản luận CỐ ĐỊNH theo giờ SINH (THỂ) — để quan sát đúng/sai. " +
                    ("秘数 cho 辟卦 này CHƯA khôi phục đủ → phần điều văn còn trống (không bịa)."
                     if not ban_menh_dieu_van
                     else "Muốn chốt chính xác hơn KHẮC sinh: 考刻 bằng lục thân (gia đạo), KHÔNG dùng giờ hỏi.")),
        "paradigm": "Đọc cái ĐÃ ĐỊNH (THỂ) — cái nền từ lúc sinh — để HIỂU mình, không phán. "
                    "Mệnh là dịch: người là cái biến (DỤNG), tự viết lấy.",
    }


# 三合 cục: chi năm → nhóm (cho 流年 letter-walk)
_TAM_HOP = {"寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌", "申": "申子辰", "子": "申子辰",
            "辰": "申子辰", "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑",
            "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未"}


def luu_nien_chain(birth_dt: str, gender: str, max_age: int = 80,
                   timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """流年条文 TỰ ĐỘNG từng tuổi (letter-walk đầy đủ) — TẤT ĐỊNH theo giờ SINH.

    Phép (đúng repo tieban, viết lại): từ 先天命数 + 年干 → chuỗi 12 thanh (14-11-2),
    xoay theo 起始数 (14-11-1, nhóm tam-hợp năm + giới). Mỗi tuổi: chi lưu niên + thanh
    → 标记 (14-12, theo 后天命数) → chữ cái (14-13, theo 刻+chẵnlẻ+thanh+标记) →
    条文 (14-14, base+add) → tra DB. KHÔNG dùng giờ hỏi."""
    T = _tables()
    base = lap_thiet_ban_so(birth_dt, gender, timezone)
    cong = base["tien_thien_menh_so"]
    pn = base["hau_thien_menh_so"]
    khac = base["khao_khac"]
    year_zh = base["bat_tu_sinh"].split()[0]      # trụ năm, vd 戊辰
    year_gan, year_chi = year_zh[0], year_zh[1]

    bg = _TAM_HOP.get(year_chi)
    g = "男" if gender in ("nam", "男", "M", "m") else "女"
    start = (T.get("ln_start_zhigroup_gender") or {}).get(f"{bg}|{g}")
    raw_seq = (T.get("ln_seq_cong_gan") or {}).get(f"{cong}|{year_gan}")
    if not start or not raw_seq or len(raw_seq) < 12:
        return {"error": "Thiếu bảng letter-walk cho cấu hình này.", "_base": base}
    off = (13 - start) % 12
    final_seq = [raw_seq[(i + off) % 12] for i in range(12)]

    markers = T.get("ln_marker_zhi_houtian") or {}
    letters = T.get("ln_letter_khac_parity_sound_marker") or {}
    ln_tab = T.get("luu_nien_by_letter_age") or {}
    chi0 = CHI.index(year_chi)
    rows = []
    for age in range(1, max_age + 1):
        cur_dz = CHI[(chi0 + age - 1) % 12]
        sound = final_seq[(age - 1) % 12]
        marker = markers.get(f"{cur_dz}|{pn}")
        parity = "奇数" if age % 2 else "偶数"
        letter = letters.get(f"{khac}|{parity}|{sound}|{marker}") if marker else None
        seq = ln_tab.get(f"{letter}|{age}") if letter else None
        v = tra_dieu_van(seq) if seq else None
        rows.append({
            "tuoi": age, "nam_chi": cur_dz, "thanh": sound, "marker": marker,
            "chu_cai": letter, "so": seq,
            "dieu_van": (v or {}).get("zh"), "vi": (v or {}).get("vi"),
        })
    return {
        "tien_thien_menh_so": cong, "hau_thien_menh_so": pn, "khao_khac": khac,
        "nhom_tam_hop": bg, "khoi_dau_so": start, "chuoi_thanh": final_seq,
        "luu_nien": rows,
        "ghi_chu": "流年 TẤT ĐỊNH theo giờ sinh (không giờ hỏi). Điều văn = base+add (14-14) tra DB ta.",
    }
