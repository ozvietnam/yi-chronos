"""大运取数法 + 流年取数法 — phép Thiết Bản theo VẬN (đại vận) + NIÊN (lưu niên).
图解 tr.103 (method 15-16). TẤT ĐỊNH theo giờ sinh + năm.

Quy trình chung:
  1-2. Tứ trụ + 天干配数 theo 《大运取数诀》: 甲己乙庚=4, 丙辛=6, 丁壬戊癸=3.
  3. 基本数 = 月干(千) · 日干(百) · 时干(十) · 年干(个)  → 1 số 4 chữ.
  4. Lập 大运 (đại vận) / 流年 (năm).
  5. Mỗi 大运/流年: 天干配数 (như trên), 地支配数 《地支取数诀》 (亥子1,6 寅卯3,8 巳午2,7
     申酉4,9 辰戌丑未5,10 — mỗi chi 2 SỐ).
  6. 条文 = 基本数 + 大运/流年天干数 ×1000 + 大运/流年地支数 (×2 → 2 条文 mỗi vận/niên).

VALIDATE (图解 tr.3922-3962): 女, 月甲日(3)时(4)年癸 → 基本数 = **4343**.
大运 lập từ engine.bat_tu.dai_van (đã có). 流年: năm → 干支 (chu kỳ 60).
Đọc cái ĐÃ ĐỊNH theo vận/niên — KHÔNG bói; 大运 là khung THỂ, không phán DỤNG.
"""
from __future__ import annotations

# 大运取数诀: 甲己乙庚 4, 丙辛 6, 丁壬戊癸 3
DV_CAN_SO = {"Giáp": 4, "Kỷ": 4, "Ất": 4, "Canh": 4, "Bính": 6, "Tân": 6,
             "Đinh": 3, "Nhâm": 3, "Mậu": 3, "Quý": 3}
# 地支取数诀 (河图 sinh-thành, mỗi chi 2 số): 亥子1,6 寅卯3,8 巳午2,7 申酉4,9 辰戌丑未5,10
DV_CHI_SO = {"Tý": (1, 6), "Hợi": (1, 6), "Dần": (3, 8), "Mão": (3, 8),
             "Tỵ": (2, 7), "Ngọ": (2, 7), "Thân": (4, 9), "Dậu": (4, 9),
             "Thìn": (5, 10), "Tuất": (5, 10), "Sửu": (5, 10), "Mùi": (5, 10)}
CAN10 = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI12 = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
         "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def basic_so(month_can: str, day_can: str, hour_can: str, year_can: str) -> int:
    """基本数 = 月干(千)·日干(百)·时干(十)·年干(个) theo 大运取数诀. KIỂM 月甲日戊时甲年癸=4343."""
    return (DV_CAN_SO[month_can] * 1000 + DV_CAN_SO[day_can] * 100
            + DV_CAN_SO[hour_can] * 10 + DV_CAN_SO[year_can])


def _van_dieu_van(base: int, van_can: str, van_chi: str) -> list[int]:
    """1 vận/niên → 2 条文: base + 天干数×1000 + mỗi 地支数 (>13000 thì −12000)."""
    out = []
    for cs in DV_CHI_SO[van_chi]:
        so = base + DV_CAN_SO[van_can] * 1000 + cs
        out.append(so - 12000 if so > 13000 else so)
    return out


def year_can_chi(year: int) -> tuple[str, str]:
    """Năm dương lịch → 干支 (chu kỳ 60). 1984=甲子."""
    return CAN10[(year - 4) % 10], CHI12[(year - 4) % 12]


def _basic_from_birth(birth_dt: str, timezone: str):
    from engine.bat_tu.tu_tru import extract_tu_tru
    p = extract_tu_tru(birth_dt, timezone)["pillars"]
    base = basic_so(p["month"]["stem"], p["day"]["stem"],
                    p["hour"]["stem"], p["year"]["stem"])
    return base, p


def _pack(sos, tra):
    return [{"so": s, "dieu_van": (tra(s) or {}).get("zh"),
             "vi": (tra(s) or {}).get("vi")} for s in sos]


def dai_van_thu_so(birth_dt: str, gender: str = "nam",
                   timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """大运取数法: 基本数 + mỗi 大运 (干支) → 2 条文/vận (8 đại vận)."""
    from engine.bat_tu.dai_van import compute_dai_van, determine_direction, estimate_starting_age
    from datetime import datetime
    from engine.thiet_ban.lap_so import tra_dieu_van
    base, p = _basic_from_birth(birth_dt, timezone)
    direction = determine_direction(p["year"]["stem"], gender)
    try:
        start_age = estimate_starting_age(datetime.fromisoformat(birth_dt), direction)
    except Exception:
        start_age = 3 if direction > 0 else 7
    cycles = compute_dai_van(month_pillar_stem=p["month"]["stem"],
                             month_pillar_branch=p["month"]["branch"],
                             year_stem=p["year"]["stem"], gender=gender,
                             starting_age=start_age)
    tra = lambda s: tra_dieu_van(s, prefer_tujie=True)  # noqa: E731
    rows = []
    for c in cycles:
        sos = _van_dieu_van(base, c["stem"], c["branch"])
        rows.append({"van": f"{c['stem']}{c['branch']}", "tuoi": c.get("start_age"),
                     "dieu_van": _pack(sos, tra)})
    return {"basic_so": base, "dai_van": rows,
            "_phap": "大运取数法 — 基本数(月日时年干) + mỗi đại vận(干支) → 2 条文. "
                     "Đọc khung VẬN (THỂ), không phán."}


def luu_nien_thu_so(birth_dt: str, from_age: int = 1, to_age: int = 60,
                    timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """流年取数法: 基本数 + mỗi năm (干支) → 2 条文/năm (theo tuổi mụ)."""
    from engine.thiet_ban.lap_so import tra_dieu_van
    base, p = _basic_from_birth(birth_dt, timezone)
    birth_year = int(birth_dt[:4])
    tra = lambda s: tra_dieu_van(s, prefer_tujie=True)  # noqa: E731
    rows = []
    for age in range(max(1, from_age), to_age + 1):
        year = birth_year + age - 1
        yc, yz = year_can_chi(year)
        sos = _van_dieu_van(base, yc, yz)
        rows.append({"tuoi": age, "nam": year, "can_chi": f"{yc}{yz}",
                     "dieu_van": _pack(sos, tra)})
    return {"basic_so": base, "luu_nien": rows,
            "_phap": "流年取数法 — 基本数 + mỗi năm(干支) → 2 条文. Khung NIÊN (THỂ)."}
