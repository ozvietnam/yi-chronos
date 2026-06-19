"""BÁT QUÁI LĂN (八卦滚) — hình học quẻ (互/变/倒) → 8 quẻ, trên core.hexagram.

ĐỐI CHIẾU tài liệu founder 2026-06-19: tài liệu ĐÚNG khái niệm (互卦/变爻/倒卦 +
3 hệ số 先天/后天/Lạc Thư + 一生万物) NHƯNG **ví dụ tính quẻ có lỗi đếm hào**
(verify bằng toán: 互(风山渐)=火水未济 chứ KHÔNG phải 火泽睽 như tài liệu;
互(天火同人)=天风姤 chứ không phải 地水师). Module này tính ĐÚNG.

KHÔNG ship 条文 cuối: cần (a) "Số Tự Cơ Bản" (基本数序, bảng 配数 thiếu),
(b) "数序" từng quẻ (3 hệ × 2 số — tài liệu nói "varies by school"), (c) 秘数 bí truyền.
→ KHÔNG bịa số. Engine 本命/流年 đã validate dùng phái 五音/辟卦 (lap_so.py), KHÁC phái này.

Quy ước binary (core.hexagram): 6 ký tự TOP-DOWN = upper(3)+lower(3); hào 1=đáy=b[5].
"""
from __future__ import annotations

from core.hexagram import flip_line, get_hexagram_by_binary

# 先天八卦数 (mod-8) → quái → bits top-down (khớp core.TRIGRAM_BITS)
NUM_TO_TRI_BITS = {1: "111", 2: "011", 3: "101", 4: "001",
                   5: "110", 6: "010", 7: "100", 0: "000", 8: "000"}
# quái bits top-down → 先天số (để ráp số sau, khi có bảng)
TIEN_THIEN_SO = {"111": 1, "011": 2, "101": 3, "001": 4, "110": 5, "010": 6, "100": 7, "000": 8}

# Biến hào theo dư (mod 9 / mod 6) — tài liệu
BIEN9 = {1: [1], 2: [2], 3: [3], 4: [4], 5: [5], 6: [6], 7: [1, 4], 8: [2, 5], 0: [3, 6]}
BIEN6 = {1: [1], 2: [2], 3: [3], 4: [4], 5: [5], 0: [6]}


def ten_que(binary: str) -> str:
    return get_hexagram_by_binary(binary).name_vi


def ho_quai(binary: str) -> str:
    """互卦: nội=hào 2,3,4 ; ngoại=hào 3,4,5. binary top-down → b[1:4](ngoại)+b[2:5](nội)."""
    return binary[1:4] + binary[2:5]


def dao_quai(binary: str) -> str:
    """倒卦 (đảo nội-ngoại): upper↔lower = b[3:6]+b[0:3]."""
    return binary[3:6] + binary[0:3]


def bien_hao(binary: str, lines: list[int]) -> str:
    for ln in lines:
        binary = flip_line(binary, ln)
    return binary


def roll_8(base_binary: str, base_seq: int, year_num: int) -> list[dict]:
    """8 quẻ 八卦滚 từ quẻ cơ bản + Số Tự Cơ Bản + số năm sinh.

    base_seq (基本数序) PHẢI đưa vào — bảng 配数 còn thiếu, KHÔNG tự suy (không bịa).
    """
    r9 = (base_seq + year_num) % 9
    r6 = (base_seq + year_num) % 6
    bql1 = ho_quai(base_binary)                       # 互 của quẻ cơ bản
    bql2 = bien_hao(bql1, BIEN9[r9])                  # biến hào (mod 9)
    bql3 = ho_quai(bql1)                              # 互 của BQL1
    bql4 = ho_quai(bql2)                              # 互 của BQL2
    first4 = [bql1, bql2, bql3, bql4]
    last4 = [dao_quai(bien_hao(q, BIEN6[r6])) for q in first4]   # biến (mod6) + đảo
    out = []
    for i, b in enumerate(first4 + last4, 1):
        out.append({"bql": i, "binary": b, "ten": ten_que(b),
                    "tien_thien_so": (TIEN_THIEN_SO[b[0:3]], TIEN_THIEN_SO[b[3:6]])})
    return {"du_mod9": r9, "du_mod6": r6, "bien9": BIEN9[r9], "bien6": BIEN6[r6],
            "tam_quai": out}


def base_que_from_bat_tu(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Quẻ cơ bản (基本卦法): 上卦=(月干+月支 太玄)mod8, 下卦=(年干+年支 太玄)mod8.

    Verify được (太玄 + 先天 mod-8). NHƯNG 'Số Tự Cơ Bản' cần bảng 配数 riêng (thiếu)."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    def th(pk):
        return TAI_HUYEN_CAN[p[pk]["stem"]] + TAI_HUYEN_CHI[p[pk]["branch"]]
    upper_n = th("month") % 8
    lower_n = th("year") % 8
    upper = NUM_TO_TRI_BITS[upper_n]
    lower = NUM_TO_TRI_BITS[lower_n]
    binary = upper + lower
    return {"upper_so": upper_n or 8, "lower_so": lower_n or 8, "binary": binary,
            "ten": ten_que(binary),
            "_thieu": "Số Tự Cơ Bản (基本数序) cần bảng 配数 — chưa có, không bịa."}


NOT_IMPLEMENTED = (
    "八卦滚 → SỐ điều văn: cần bảng 数序 từng quẻ (3 hệ × 2 số, tài liệu nói khác nhau "
    "theo phái) + Số Tự Cơ Bản + 秘数 bí truyền. Hình học (8 quẻ) ĐÃ đúng; số 条文 chưa validate được."
)
