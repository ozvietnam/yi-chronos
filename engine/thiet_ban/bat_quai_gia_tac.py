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

from core.hexagram import compose_hexagram_binary, get_hexagram_by_binary
from engine.thiet_ban.khoi_so import THIEN_CAN_QUAI

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
