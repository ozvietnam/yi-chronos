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


# ════════ 八卦基本配数表 (图解 tr.96) — bảng 数序 đã có! ════════
# 上卦数 = 180 + (先天数−1)×540 ; 下卦数 = 450 + (先天数−1)×540.
# Số Tự Cơ Bản (基本数) của 1 quẻ = 上卦数[quái trên] + 下卦数[quái dưới].
def _phoi_so(bits_topdown: str, is_upper: bool) -> int:
    tt = TIEN_THIEN_SO[bits_topdown]
    return (180 if is_upper else 450) + (tt - 1) * 540


def so_tu_co_ban(binary: str) -> int:
    """基本数 (Số Tự Cơ Bản): 上卦数[trên] + 下卦数[dưới]. Vd 水火既济=2880+1530=4410."""
    return _phoi_so(binary[0:3], True) + _phoi_so(binary[3:6], False)


# ════════ 卦中取数法 / 太玄取数法 (图解 tr.94-95) — 4 điều văn, CÓ cặp kiểm ════════
# KIỂM: nam 己丑乙亥癸卯乙卯 → 7198, 7157, 9356, 9363 (图解 tr.95) — engine khớp 4/4.
def quai_trung_so_tu_tru(pillars: dict) -> list[dict]:
    """Lõi 卦中取数 từ tứ trụ {pk: (can_vi, chi_vi)} → 4 SỐ điều văn (không tra DB).
    pk ∈ year/month/day/hour. Tách riêng để TEST khớp cặp kiểm sách."""
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI

    def thx(pk):
        return TAI_HUYEN_CAN[pillars[pk][0]], TAI_HUYEN_CHI[pillars[pk][1]]

    def m8(x):
        return x % 8 or 8

    rows = []
    for upk, lok, nhan in (("year", "month", "năm·tháng"), ("day", "hour", "ngày·giờ")):
        ug, uz = thx(upk)
        lg, lz = thx(lok)
        up_so = m8(ug + uz)   # = 先天数 quái trên
        binary = NUM_TO_TRI_BITS[up_so] + NUM_TO_TRI_BITS[m8(lg + lz)]
        hu = ho_quai(binary)
        qian = (up_so + 6) % 10                 # 逢十不用
        t1 = qian * 1000 + up_so * 100 + ug * 10 + uz
        t2 = qian * 1000 + up_so * 100 + TIEN_THIEN_SO[hu[0:3]] * 10 + TIEN_THIEN_SO[hu[3:6]]
        rows += [{"nhan": nhan, "que": ten_que(binary), "so": t1},
                 {"nhan": nhan, "que": ten_que(binary), "so": t2}]
    return rows


def quai_trung_thu_so(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> list[dict]:
    """卦中取数 từ giờ sinh: 年→上/月→下 = quẻ1; 日→上/时→下 = quẻ2 (先天 mod-8). 4 điều văn."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.lap_so import tra_dieu_van
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    pillars = {pk: (p[pk]["stem"], p[pk]["branch"]) for pk in ("year", "month", "day", "hour")}
    out = []
    for r in quai_trung_so_tu_tru(pillars):
        v = tra_dieu_van(r["so"])
        out.append({**r, "dieu_van": (v or {}).get("zh"), "vi": (v or {}).get("vi")})
    return out


NOT_IMPLEMENTED = (
    "八卦滚 → 48 điều văn: hình học 8 quẻ ĐÚNG + 八卦基本配数表 ĐÃ có (so_tu_co_ban). "
    "CÒN: base quẻ 八卦滚 dùng 后天 odd/even (khác base_que hiện theo 先天 月/年) — cần sửa + "
    "validate full vs ví dụ 图解 (地天泰→雷泽归妹). 卦中取数法 thì ĐÃ validate (cặp kiểm 7198...)."
)
