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


# 文王后天数 → quái bits (top-down). 后天: 坎1坤2震3巽4中5乾6兑7艮8离9.
HAU_THIEN_TO_BITS = {1: "010", 2: "000", 3: "001", 4: "110", 5: "000",
                     6: "111", 7: "011", 8: "100", 0: "100", 9: "101"}


def nguyen_cua_nam(year: int) -> str:
    """元: 上(1864-1923)/中(1924-1983)/下(1984-2043), chu kỳ 180 năm."""
    return ["上元", "中元", "下元"][((year - 1864) // 60) % 3]


def nam_so_bql(year: int, can_tx: int, chi_tx: int, yang_year: bool, is_male: bool) -> int:
    """Số năm theo 元 (图解 tr.96): 上=干×10+支; 下=支×10+干;
    中: 阳年男/阴年女=干×100+支×10, 阳年女/阴年男=支×100+干×10."""
    ng = nguyen_cua_nam(year)
    if ng == "上元":
        return can_tx * 10 + chi_tx
    if ng == "下元":
        return chi_tx * 10 + can_tx
    if (yang_year and is_male) or ((not yang_year) and (not is_male)):
        return can_tx * 100 + chi_tx * 10
    return chi_tx * 100 + can_tx * 10


def base_que_bat_quai_lan(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Quẻ cơ bản 八卦滚 (图解 tr.97): 上卦=(太玄 LẺ)mod8→后天; 下卦=(太玄 CHẴN)mod8→后天.
    KIỂM: 女 2006 丙戌庚寅丁亥辛亥 → odd26→坤, even22→乾 → 地天泰 (4410)."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    nums = []
    for pk in ("year", "month", "day", "hour"):
        nums += [TAI_HUYEN_CAN[p[pk]["stem"]], TAI_HUYEN_CHI[p[pk]["branch"]]]
    odd = sum(x for x in nums if x % 2)
    even = sum(x for x in nums if x % 2 == 0)
    binary = HAU_THIEN_TO_BITS[odd % 8] + HAU_THIEN_TO_BITS[even % 8]
    return {"odd": odd, "even": even, "binary": binary,
            "ten": ten_que(binary), "base_seq": so_tu_co_ban(binary)}


def roll_bat_quai_lan(birth_dt: str, gender: str = "nam",
                      timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Trọn 八卦滚: base (后天 lẻ/chẵn) + 元-năm → roll 8 quẻ. Geometry VALIDATE 8/8 vs 图解."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI, CAN
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    base = base_que_bat_quai_lan(birth_dt, timezone)
    yc = p["year"]["stem"]
    year = int(birth_dt[:4])
    yang = CAN.index(yc) % 2 == 0   # CAN (khoi_so) là tên Việt; yc cũng Việt
    is_male = gender in ("nam", "男", "M", "m")
    nam_so = nam_so_bql(year, TAI_HUYEN_CAN[yc], TAI_HUYEN_CHI[p["year"]["branch"]], yang, is_male)
    r = roll_8(base["binary"], base["base_seq"], nam_so)
    return {"base": base, "nguyen": nguyen_cua_nam(year), "nam_so": nam_so, **r,
            "_thieu_dieu_van": "48 điều văn cần bảng 序/先天/后天数 từng quẻ (密码本) + "
                               "kho 条文 SẠCH (DB ta lệch số vài 集). Hình học 8 quẻ ĐÃ validate."}


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
        v = tra_dieu_van(r["so"], prefer_tujie=True)   # 卦中 = phép 图解-native
        out.append({**r, "dieu_van": (v or {}).get("zh"), "vi": (v or {}).get("vi")})
    return out


NOT_IMPLEMENTED = (
    "八卦滚 → 48 điều văn: hình học 8 quẻ ĐÚNG + 八卦基本配数表 ĐÃ có (so_tu_co_ban). "
    "CÒN: base quẻ 八卦滚 dùng 后天 odd/even (khác base_que hiện theo 先天 月/年) — cần sửa + "
    "validate full vs ví dụ 图解 (地天泰→雷泽归妹). 卦中取数法 thì ĐÃ validate (cặp kiểm 7198...)."
)
