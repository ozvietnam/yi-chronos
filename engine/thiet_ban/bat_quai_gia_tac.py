"""八卦加则法 — phép Thiết Bản "thường dùng nhất" (图解 tr.1452-1478, "2.八卦加则法").

Nền cho nhiều phép (先后天卦 / 前后卦 / 日主化卦 / 父母生肖化卦). VALIDATE cặp kiểm sách.

Quy trình (biến thể 1, sách mô tả rõ):
  1. Tứ trụ → 4 quẻ: 干 配卦 (纳甲) = 上卦; 支 配卦 (日主配卦诀) = 下卦.
  2. Mỗi quẻ 6 hào TỪ TRÊN XUỐNG: 阳爻 lần lượt 子寅辰午申戌; 阴爻 lần lượt 丑卯巳未酉亥.
  3. Mỗi hào địa chi → số (子丑30 寅卯60 辰巳90 午未120 申酉150 戌亥180); cộng 6 hào = TỔNG.
  4. 条文数 = 上卦后天数 ×1000 + TỔNG − 下卦后天数.
     (后天数 = 文王洛书: 乾6 坤2 艮8 兑7 坎1 离9 震3 巽4 — = 干配数 sách tr.1486.)

KIỂM cặp kiểm sách (男 癸未 庚申 丁未 丙午): 年柱 地山谦 (坤上艮下) tổng480 → 2×1000+480−8
  = **2472** "其人之亡，定在八月"; 月柱 雷天大壮 (震上乾下) tổng390 → 3×1000+390−6 = **3384**
  "孝服临门，哭泣哀哉". Engine khớp 2/2.

KHÁC 太玄/河洛 các phép khác: 干配卦=纳甲, 支配卦=日主配卦诀, số quẻ = 后天洛书数.
Sách nói có biến thể 2 (干支纳甲 + 子丑30...) — chưa làm; biến thể 1 đã validate.
"""
from __future__ import annotations

from core.hexagram import TRIGRAM_BITS, compose_hexagram_binary, get_hexagram_by_binary
from engine.thiet_ban.khoi_so import THIEN_CAN_QUAI

_BITS_TO_TRI = {v: k for k, v in TRIGRAM_BITS.items()}

# 支 配卦 (日主配卦诀, 图解 tr.1466-1470): 亥子坎·寅卯震·巳午离·丑坤·申酉乾·辰兑·未艮·戌巽
DIA_CHI_QUAI_NHATCHU = {
    "Tý": "Khảm", "Hợi": "Khảm", "Dần": "Chấn", "Mão": "Chấn",
    "Tỵ": "Ly", "Ngọ": "Ly", "Sửu": "Khôn", "Thân": "Càn",
    "Dậu": "Càn", "Thìn": "Đoài", "Mùi": "Cấn", "Tuất": "Tốn",
}
# 后天洛书数 (= 干配数 sách tr.1486): 乾6 坤2 艮8 兑7 坎1 离9 震3 巽4
HAU_THIEN_SO = {"Càn": 6, "Khôn": 2, "Cấn": 8, "Đoài": 7,
                "Khảm": 1, "Ly": 9, "Chấn": 3, "Tốn": 4}
YANG_CHI = ["Tý", "Dần", "Thìn", "Ngọ", "Thân", "Tuất"]   # 阳爻 lần lượt
YIN_CHI = ["Sửu", "Mão", "Tỵ", "Mùi", "Dậu", "Hợi"]       # 阴爻 lần lượt
CHI_SO = {"Tý": 30, "Sửu": 30, "Dần": 60, "Mão": 60, "Thìn": 90, "Tỵ": 90,
          "Ngọ": 120, "Mùi": 120, "Thân": 150, "Dậu": 150, "Tuất": 180, "Hợi": 180}

_TRU_VI = {"year": "năm", "month": "tháng", "day": "ngày", "hour": "giờ"}


def _tac_que(upper: str, lower: str) -> dict:
    """Lõi 八卦加则 cho 1 quẻ (上卦, 下卦 tên Việt) → tổng + 条文数."""
    binary = compose_hexagram_binary(upper, lower)        # top-down (爻6→爻1)
    yi = ii = tong = 0
    hao_chi = []
    for bit in binary:                                    # TỪ TRÊN XUỐNG
        if bit == "1":
            dc = YANG_CHI[yi]; yi += 1
        else:
            dc = YIN_CHI[ii]; ii += 1
        hao_chi.append(dc)
        tong += CHI_SO[dc]
    so = HAU_THIEN_SO[upper] * 1000 + tong - HAU_THIEN_SO[lower]
    return {"upper": upper, "lower": lower, "que": get_hexagram_by_binary(binary).name_vi,
            "tong": tong, "hao_chi": hao_chi, "so": so}


def gia_tac_mot_que(can: str, chi: str) -> dict:
    """1 trụ (can, chi) → 1 quẻ + 条文数 (八卦加则). 干→上卦(纳甲), 支→下卦(日主配卦)."""
    return _tac_que(THIEN_CAN_QUAI[can], DIA_CHI_QUAI_NHATCHU[chi])


def phu_mau_sinh_tieu(cha_chi: str, me_chi: str) -> dict:
    """父母生肖化卦取数法 (图解 tr.4253) — LỤC THÂN: 父支→上卦, 母支→下卦 (日主配卦),
    rồi 八卦加则 → 1 条文. Dùng lại lõi 八卦加则 ĐÃ validate (cặp kiểm 2472/3384)."""
    return _tac_que(DIA_CHI_QUAI_NHATCHU[cha_chi], DIA_CHI_QUAI_NHATCHU[me_chi])


def _pm96(base: int, cong: bool) -> list:
    """递加/递减 96 bốn lần (图解 tr.2759-2761): 先天卦 +96×4, 后天卦 −96×4."""
    step = 96 if cong else -96
    return [base + step * i for i in range(1, 5)]


def tien_hau_thien_gia_tac(birth_dt: str, gender: str = "nam",
                           timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """先后天卦八卦加则法 (图解 tr.2751): 先天卦/后天卦 (河洛真数, từ engine.ha_lac) →
    mỗi quẻ 八卦加则 → 先天 +96×4, 后天 −96×4 = 8 条文.

    VALIDATE: 八卦加则 + ±96 khớp ví dụ sách (震为雷→3387→[3483,3579,3675,3771];
    后天 2477→[2381,2285,2189,2093]). 先天卦/后天卦 lấy từ ha_lac (engine 河洛 của hệ)."""
    from engine.ha_lac.cast import cast_ha_lac
    from engine.thiet_ban.lap_so import tra_dieu_van
    hl = cast_ha_lac(birth_datetime_local=birth_dt, timezone=timezone, gender=gender)
    tt, ht = hl["tien_thien_quai"], hl["hau_thien_quai"]
    tt_q = _tac_que(tt["upper_trigram"], tt["lower_trigram"])
    ht_q = _tac_que(ht["upper_trigram"], ht["lower_trigram"])

    def pack(sos):
        out = []
        for s in sos:
            v = tra_dieu_van(s, prefer_tujie=True) or {}
            out.append({"so": s, "dieu_van": v.get("zh"), "vi": v.get("vi")})
        return out

    return {
        "tien_thien_que": tt.get("name_vi"), "hau_thien_que": ht.get("name_vi"),
        "tien_thien_base": tt_q["so"], "hau_thien_base": ht_q["so"],
        "dieu_van_tien_thien": pack(_pm96(tt_q["so"], True)),    # +96×4
        "dieu_van_hau_thien": pack(_pm96(ht_q["so"], False)),    # −96×4
        "_phap": "先后天卦八卦加则法 — 先天卦/后天卦 (河洛真数) → 八卦加则 → ±96×4. "
                 "Cơ chế validate cặp kiểm sách; quẻ tiên/hậu thiên từ engine ha_lac.",
    }


def _tx_to_trigram(can_tx: int, chi_tx: int) -> str:
    """太玄(干)+太玄(支) → 后天卦 (>8 thì %8). 9→坎,18→坤... (KIỂM ví dụ sách)."""
    s = can_tx + chi_tx
    du = s if s <= 8 else (s % 8)
    from engine.thiet_ban.bat_quai_lan import HAU_THIEN_TO_BITS
    return _BITS_TO_TRI[HAU_THIEN_TO_BITS[du]]


def truoc_sau_que_tu_taixuan(yc, yz, mc, mz, dc, dz, hc, hz) -> dict:
    """Lõi 前后卦 từ 8 太玄数 (thuần, test cặp kiểm). 前卦=年(上)月(下), 后卦=日(上)时(下)."""
    truoc = _tac_que(_tx_to_trigram(yc, yz), _tx_to_trigram(mc, mz))   # 前卦
    sau = _tac_que(_tx_to_trigram(dc, dz), _tx_to_trigram(hc, hz))     # 后卦
    return {"truoc_que": truoc["que"], "sau_que": sau["que"],
            "truoc_base": truoc["so"], "sau_base": sau["so"],
            "truoc_sos": _pm96(truoc["so"], True),    # 前卦 +96×4
            "sau_sos": _pm96(sau["so"], False)}       # 后卦 −96×4


# 12 辟卦 (消息卦) theo NGUYỆT CHI (图解 tr.4257): (上卦, 下卦)
TICH_QUAI = {
    "Tý": ("Khôn", "Chấn"), "Sửu": ("Khôn", "Đoài"), "Dần": ("Khôn", "Càn"),
    "Mão": ("Chấn", "Càn"), "Thìn": ("Đoài", "Càn"), "Tỵ": ("Càn", "Càn"),
    "Ngọ": ("Càn", "Tốn"), "Mùi": ("Càn", "Cấn"), "Thân": ("Càn", "Khôn"),
    "Dậu": ("Tốn", "Khôn"), "Tuất": ("Cấn", "Khôn"), "Hợi": ("Khôn", "Khôn"),
}


# 先天数 theo tên quái (Fuxi): 乾1兑2离3震4巽5坎6艮7坤8
TT_SO = {"Càn": 1, "Đoài": 2, "Ly": 3, "Chấn": 4,
         "Tốn": 5, "Khảm": 6, "Cấn": 7, "Khôn": 8}


def _co_so_hu(binary: str, so_map: dict) -> int:
    """基数 #10 = 上卦数(千) + 下卦数(百) + 互卦上数(十) + 互卦下数(个). so_map = 先天/后天."""
    from engine.thiet_ban.bat_quai_lan import ho_quai
    hu = ho_quai(binary)
    return (so_map[_BITS_TO_TRI[binary[0:3]]] * 1000 + so_map[_BITS_TO_TRI[binary[3:6]]] * 100
            + so_map[_BITS_TO_TRI[hu[0:3]]] * 10 + so_map[_BITS_TO_TRI[hu[3:6]]])


def _pm48(base: int) -> list:
    """±48 × {2,4,8,16} → 8 条文 (图解 tr.3019); >13000 thì −12000."""
    out = [base + 48 * k for k in (2, 4, 8, 16)] + [base - 48 * k for k in (2, 4, 8, 16)]
    return [s - 12000 if s > 13000 else s for s in out]


def tien_hau_thien_thu_so(birth_dt: str, gender: str = "nam",
                          timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """先后天卦取数法 #10 (图解 tr.3007): 先天卦/后天卦 + 互卦 → 2 基数 → ±48×{2,4,8,16} = 16 条文.
    VALIDATE: 先天基数 夬→互乾→2111; 后天基数 睽→互既济→9719 (cặp kiểm sách)."""
    from engine.ha_lac.cast import cast_ha_lac
    from engine.thiet_ban.lap_so import tra_dieu_van
    hl = cast_ha_lac(birth_datetime_local=birth_dt, timezone=timezone, gender=gender)
    tt, ht = hl["tien_thien_quai"], hl["hau_thien_quai"]
    tt_bin = compose_hexagram_binary(tt["upper_trigram"], tt["lower_trigram"])
    ht_bin = compose_hexagram_binary(ht["upper_trigram"], ht["lower_trigram"])
    tt_base = _co_so_hu(tt_bin, TT_SO)              # 先天基数 (先天数)
    ht_base = _co_so_hu(ht_bin, HAU_THIEN_SO)       # 后天基数 (后天数)

    def pack(sos):
        return [{"so": s, "dieu_van": (tra_dieu_van(s, prefer_tujie=True) or {}).get("zh"),
                 "vi": (tra_dieu_van(s, prefer_tujie=True) or {}).get("vi")} for s in sos]

    return {"tien_thien_que": tt.get("name_vi"), "hau_thien_que": ht.get("name_vi"),
            "tien_thien_base": tt_base, "hau_thien_base": ht_base,
            "dieu_van_tien_thien": pack(_pm48(tt_base)),
            "dieu_van_hau_thien": pack(_pm48(ht_base)),
            "_phap": "先后天卦取数法 #10 — 先天卦/后天卦 + 互卦 → 2 基数 → ±48×{2,4,8,16}."}


def nhat_chu_hoa_que(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """日主化卦取数法 (图解 tr.2357): CHỈ 日柱 → 八卦加则 → base ±96×4 mỗi chiều = 8 条文.
    KIỂM 壬午日 → 乾(壬)上离(午)下 天火同人 → base 6471."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.lap_so import tra_dieu_van
    d = extract_tu_tru(birth_dt, timezone)["pillars"]["day"]
    q = gia_tac_mot_que(d["stem"], d["branch"])
    sos = _pm96(q["so"], True) + _pm96(q["so"], False)         # +96×4 ∪ −96×4
    return {"que": q["que"], "base": q["so"],
            "dieu_van": [{"so": s, "dieu_van": (tra_dieu_van(s) or {}).get("zh"),
                          "vi": (tra_dieu_van(s) or {}).get("vi")} for s in sos],
            "_phap": "日主化卦取数法 — chỉ 日柱 → 八卦加则 → ±96×4 (8 条文)."}


def thap_nhi_tich_hoa_que(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """十二辟卦化卦取数 (图解 tr.4257): NGUYỆT CHI → 辟卦 (消息) → 八卦加则 → 1 条文."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.lap_so import tra_dieu_van
    m = extract_tu_tru(birth_dt, timezone)["pillars"]["month"]
    up, lo = TICH_QUAI[m["branch"]]
    q = _tac_que(up, lo)
    v = tra_dieu_van(q["so"]) or {}
    return {"nguyet_chi": m["branch"], "tich_que": q["que"], "so": q["so"],
            "dieu_van": v.get("zh"), "vi": v.get("vi"),
            "_phap": "十二辟卦化卦取数 — nguyệt chi → 辟卦 → 八卦加则."}


def truoc_sau_que(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """前后卦取数法 (图解 tr.3133): 年月→前卦, 日时→后卦 (太玄%8→后天) → 八卦加则 → ±96×4.
    VALIDATE cặp kiểm sách: 前卦 水地比 → 1478, 后卦 水雷屯 → 1387 (+/−96×4)."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.khoi_so import TAI_HUYEN_CAN, TAI_HUYEN_CHI
    from engine.thiet_ban.lap_so import tra_dieu_van
    p = extract_tu_tru(birth_dt, timezone)["pillars"]

    def tx(pk):
        return TAI_HUYEN_CAN[p[pk]["stem"]], TAI_HUYEN_CHI[p[pk]["branch"]]

    (yc, yz), (mc, mz), (dc, dz), (hc, hz) = tx("year"), tx("month"), tx("day"), tx("hour")
    s = truoc_sau_que_tu_taixuan(yc, yz, mc, mz, dc, dz, hc, hz)

    def pack(sos):
        return [{"so": x, "dieu_van": (tra_dieu_van(x, prefer_tujie=True) or {}).get("zh"),
                 "vi": (tra_dieu_van(x, prefer_tujie=True) or {}).get("vi")} for x in sos]

    return {"truoc_que": s["truoc_que"], "sau_que": s["sau_que"],
            "truoc_base": s["truoc_base"], "sau_base": s["sau_base"],
            "dieu_van_truoc": pack(s["truoc_sos"]), "dieu_van_sau": pack(s["sau_sos"]),
            "_phap": "前后卦取数法 — 年月→前卦(+96×4), 日时→后卦(−96×4). Cặp kiểm 1478/1387."}


def bat_quai_gia_tac_tu_tru(pillars: dict) -> list:
    """Tứ trụ {pk:(can,chi)} → 4 quẻ + 4 条文 SỐ (thuần, để test cặp kiểm)."""
    out = []
    for pk in ("year", "month", "day", "hour"):
        r = gia_tac_mot_que(*pillars[pk])
        out.append({"tru": _TRU_VI[pk], **r})
    return out


def bat_quai_gia_tac(birth_dt: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """八卦加则 từ giờ sinh → 4 quẻ (năm/tháng/ngày/giờ) + 条文 tra DB."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.thiet_ban.lap_so import tra_dieu_van
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    pillars = {pk: (p[pk]["stem"], p[pk]["branch"]) for pk in ("year", "month", "day", "hour")}
    rows = bat_quai_gia_tac_tu_tru(pillars)
    for r in rows:
        v = tra_dieu_van(r["so"], prefer_tujie=True) or {}
        r["dieu_van"] = v.get("zh")
        r["vi"] = v.get("vi")
        r["nguon"] = v.get("nguon")
    return {"bat_tu": " ".join(f"{p[pk]['stem']}{p[pk]['branch']}"
                               for pk in ("year", "month", "day", "hour")),
            "quai": rows,
            "_phap": "八卦加则法 (biến thể 1, validate cặp kiểm 2472/3384). "
                     "Mỗi trụ → 1 quẻ → 1 条文. Đọc cái ĐÃ ĐỊNH, KHÔNG bói."}
