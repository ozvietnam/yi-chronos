"""Auspicious Day — chọn ngày tốt theo Bát Tự + Mai Hoa + truyền thống.

Công thức tổng hợp:
  - Bát Tự đệ tử (Tứ Trụ) → Nhật chủ, dụng thần, ngũ hành thiếu
  - Năm chi (con giáp tuổi) → Xung/Hại/Hình/Hợp với chi của ngày
  - Tam Sát theo mùa (mùa hạ: Bắc — Hợi-Tý-Sửu)
  - Hoàng Đạo / Hắc Đạo theo tháng âm
  - Thiên Ất Quý Nhân theo Nhật can hoặc Năm can
  - Lục Hợp, Tam Hợp theo chi
  - Intent: chuyển nhà (gia trạch) / khai trương / hôn nhân / khởi công / xuất hành / cầu tài

Output structured: list ngày với score + breakdown chi tiết cho UI hiển thị.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ─── Constants ──────────────────────────────────────────────────────────

STEM_HANH = {
    "Giáp": "Mộc", "Ất": "Mộc",
    "Bính": "Hoả", "Đinh": "Hoả",
    "Mậu": "Thổ", "Kỷ": "Thổ",
    "Canh": "Kim", "Tân": "Kim",
    "Nhâm": "Thuỷ", "Quý": "Thuỷ",
}
BRANCH_HANH = {
    "Tý": "Thuỷ", "Sửu": "Thổ", "Dần": "Mộc", "Mão": "Mộc",
    "Thìn": "Thổ", "Tỵ": "Hoả", "Ngọ": "Hoả", "Mùi": "Thổ",
    "Thân": "Kim", "Dậu": "Kim", "Tuất": "Thổ", "Hợi": "Thuỷ",
}
STEM_POLARITY = {  # Dương/Âm
    "Giáp": "D", "Bính": "D", "Mậu": "D", "Canh": "D", "Nhâm": "D",
    "Ất": "Â", "Đinh": "Â", "Kỷ": "Â", "Tân": "Â", "Quý": "Â",
}
SINH = {"Kim": "Thuỷ", "Thuỷ": "Mộc", "Mộc": "Hoả", "Hoả": "Thổ", "Thổ": "Kim"}
KHAC = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thuỷ", "Thuỷ": "Hoả", "Hoả": "Kim"}


# Quan hệ 12 chi
XUNG_CHI = {
    "Tý": "Ngọ", "Ngọ": "Tý",
    "Sửu": "Mùi", "Mùi": "Sửu",
    "Dần": "Thân", "Thân": "Dần",
    "Mão": "Dậu", "Dậu": "Mão",
    "Thìn": "Tuất", "Tuất": "Thìn",
    "Tỵ": "Hợi", "Hợi": "Tỵ",
}
LUC_HOP = {  # Lục hợp — 2 chi
    "Tý": ("Sửu", "Thổ"),
    "Sửu": ("Tý", "Thổ"),
    "Dần": ("Hợi", "Mộc"),
    "Hợi": ("Dần", "Mộc"),
    "Mão": ("Tuất", "Hoả"),
    "Tuất": ("Mão", "Hoả"),
    "Thìn": ("Dậu", "Kim"),
    "Dậu": ("Thìn", "Kim"),
    "Tỵ": ("Thân", "Thuỷ"),
    "Thân": ("Tỵ", "Thuỷ"),
    "Ngọ": ("Mùi", "Hoả"),
    "Mùi": ("Ngọ", "Hoả"),
}
TAM_HOP = {  # 3 chi → hành
    frozenset(["Thân", "Tý", "Thìn"]): "Thuỷ",
    frozenset(["Tỵ", "Dậu", "Sửu"]): "Kim",
    frozenset(["Dần", "Ngọ", "Tuất"]): "Hoả",
    frozenset(["Hợi", "Mão", "Mùi"]): "Mộc",
}
HAI_CHI = {  # Tương hại
    "Tý": "Mùi", "Mùi": "Tý",
    "Sửu": "Ngọ", "Ngọ": "Sửu",
    "Dần": "Tỵ", "Tỵ": "Dần",
    "Mão": "Thìn", "Thìn": "Mão",
    "Thân": "Hợi", "Hợi": "Thân",
    "Dậu": "Tuất", "Tuất": "Dậu",
}
HINH_CHI = {  # Tương hình (đơn giản hoá)
    "Dần": "Tỵ", "Tỵ": "Thân", "Thân": "Dần",   # Tam hình Dần-Tỵ-Thân
    "Sửu": "Tuất", "Tuất": "Mùi", "Mùi": "Sửu",  # Tam hình Sửu-Tuất-Mùi
    "Tý": "Mão", "Mão": "Tý",                    # Tương hình Tý-Mão
}
TU_HINH = {"Thìn", "Ngọ", "Dậu", "Hợi"}  # Tự hình (trùng chi)


# Thiên Ất Quý Nhân theo Nhật Can hoặc Năm Can
THIEN_AT_QUY_NHAN = {
    "Giáp": ("Sửu", "Mùi"), "Mậu": ("Sửu", "Mùi"),
    "Ất": ("Tý", "Thân"), "Kỷ": ("Tý", "Thân"),
    "Bính": ("Hợi", "Dậu"), "Đinh": ("Hợi", "Dậu"),
    "Nhâm": ("Mão", "Tỵ"), "Quý": ("Mão", "Tỵ"),
    "Canh": ("Sửu", "Mùi"), "Tân": ("Dần", "Ngọ"),
}


# Tam Sát theo mùa (4 tiết khí)
# Mùa xuân (Dần-Mão-Thìn): Tam Sát phương TÂY = Thân-Dậu-Tuất
# Mùa hạ (Tỵ-Ngọ-Mùi): Tam Sát phương BẮC = Hợi-Tý-Sửu
# Mùa thu (Thân-Dậu-Tuất): Tam Sát phương ĐÔNG = Dần-Mão-Thìn
# Mùa đông (Hợi-Tý-Sửu): Tam Sát phương NAM = Tỵ-Ngọ-Mùi
TAM_SAT_BY_SEASON = {
    "xuan": {"Thân", "Dậu", "Tuất"},
    "ha": {"Hợi", "Tý", "Sửu"},
    "thu": {"Dần", "Mão", "Thìn"},
    "dong": {"Tỵ", "Ngọ", "Mùi"},
}


# Hoàng Đạo / Hắc Đạo theo tháng âm (Kiến Trừ pháp đơn giản hoá)
# Mỗi tháng âm có set Hoàng Đạo + Hắc Đạo
HOANG_HAC_BY_LUNAR_MONTH = {
    # tháng âm 1-12 — set của các CHI thuộc Hoàng Đạo
    1:  {"hoang": {"Tý","Sửu","Tỵ","Mùi","Tuất","Hợi"}, "hac": {"Dần","Mão","Thìn","Ngọ","Thân","Dậu"}},
    2:  {"hoang": {"Dần","Mão","Mùi","Dậu","Tý","Sửu"}, "hac": {"Thìn","Tỵ","Ngọ","Thân","Tuất","Hợi"}},
    3:  {"hoang": {"Thìn","Tỵ","Dậu","Hợi","Dần","Mão"}, "hac": {"Ngọ","Mùi","Thân","Tuất","Tý","Sửu"}},
    4:  {"hoang": {"Ngọ","Mùi","Hợi","Sửu","Thìn","Tỵ"}, "hac": {"Thân","Dậu","Tuất","Tý","Dần","Mão"}},
    5:  {"hoang": {"Thân","Dậu","Sửu","Mão","Ngọ","Mùi"}, "hac": {"Tuất","Hợi","Tý","Dần","Thìn","Tỵ"}},
    6:  {"hoang": {"Tuất","Hợi","Mão","Tỵ","Thân","Dậu"}, "hac": {"Tý","Sửu","Dần","Thìn","Ngọ","Mùi"}},
    7:  {"hoang": {"Tý","Sửu","Tỵ","Mùi","Tuất","Hợi"}, "hac": {"Dần","Mão","Thìn","Ngọ","Thân","Dậu"}},
    8:  {"hoang": {"Dần","Mão","Mùi","Dậu","Tý","Sửu"}, "hac": {"Thìn","Tỵ","Ngọ","Thân","Tuất","Hợi"}},
    9:  {"hoang": {"Thìn","Tỵ","Dậu","Hợi","Dần","Mão"}, "hac": {"Ngọ","Mùi","Thân","Tuất","Tý","Sửu"}},
    10: {"hoang": {"Ngọ","Mùi","Hợi","Sửu","Thìn","Tỵ"}, "hac": {"Thân","Dậu","Tuất","Tý","Dần","Mão"}},
    11: {"hoang": {"Thân","Dậu","Sửu","Mão","Ngọ","Mùi"}, "hac": {"Tuất","Hợi","Tý","Dần","Thìn","Tỵ"}},
    12: {"hoang": {"Tuất","Hợi","Mão","Tỵ","Thân","Dậu"}, "hac": {"Tý","Sửu","Dần","Thìn","Ngọ","Mùi"}},
}


# Intent weights — mỗi intent có ưu tiên hành riêng
INTENT_WEIGHTS = {
    "chuyen_nha": {
        "label": "Chuyển nhà (gia trạch)",
        "needs": ["Mộc", "Thổ"],  # Mộc sinh khí + Thổ ổn định
        "avoids": ["Hoả-Hoả"],     # quá nóng
        "prefer_quy_nhan": True,
        "prefer_luc_hop": True,
    },
    "khai_truong": {
        "label": "Khai trương / Mở cửa hàng",
        "needs": ["Mộc", "Hoả"],  # Mộc phát triển + Hoả tài
        "avoids": ["Tỵ tháng đông"],
        "prefer_quy_nhan": True,
    },
    "khoi_cong": {
        "label": "Khởi công / Động thổ",
        "needs": ["Thổ"],
        "avoids": [],
        "prefer_quy_nhan": False,
    },
    "hon_nhan": {
        "label": "Hôn nhân / Cưới hỏi",
        "needs": ["Mộc"],
        "avoids": [],
        "prefer_quy_nhan": True,
        "prefer_luc_hop": True,
    },
    "xuat_hanh": {
        "label": "Xuất hành / Đi xa",
        "needs": ["Mộc"],
        "avoids": [],
        "prefer_quy_nhan": False,
    },
    "cau_tai": {
        "label": "Cầu tài / Ký hợp đồng",
        "needs": ["Mộc", "Kim"],
        "avoids": [],
        "prefer_quy_nhan": True,
    },
    "general": {
        "label": "Tổng quát",
        "needs": ["Mộc"],
        "avoids": [],
        "prefer_quy_nhan": False,
    },
}


# Phương vị thuộc hành (hướng nhà → bổ sung)
DIRECTION_HANH = {
    "đông": "Mộc", "tây": "Kim",
    "nam": "Hoả", "bắc": "Thuỷ",
    "đông nam": "Mộc", "đông bắc": "Thổ",
    "tây nam": "Thổ", "tây bắc": "Kim",
}


@dataclass
class BatTu:
    """Tứ Trụ đệ tử."""
    year_stem: str
    year_branch: str
    month_stem: str
    month_branch: str
    day_stem: str       # Nhật chủ
    day_branch: str
    hour_stem: str
    hour_branch: str

    @property
    def nhat_chu_hanh(self) -> str:
        return STEM_HANH[self.day_stem]

    @property
    def all_hanh(self) -> dict[str, int]:
        c = {"Mộc": 0, "Hoả": 0, "Thổ": 0, "Kim": 0, "Thuỷ": 0}
        for s in [self.year_stem, self.month_stem, self.day_stem, self.hour_stem]:
            c[STEM_HANH[s]] += 1
        for b in [self.year_branch, self.month_branch, self.day_branch, self.hour_branch]:
            c[BRANCH_HANH[b]] += 1
        return c

    @property
    def thieu_hanh(self) -> list[str]:
        """Hành nào có 0 hoặc 1 → thiếu, cần bổ sung."""
        c = self.all_hanh
        return [h for h, n in c.items() if n <= 1]


@dataclass
class DayScore:
    """Một ngày với điểm + breakdown."""
    date: str               # YYYY-MM-DD
    day_num: int
    weekday: str
    stem: str
    branch: str
    can_hanh: str
    chi_hanh: str
    score: int = 0
    notes: list[str] = field(default_factory=list)
    flag: str = ""
    is_taboo: bool = False  # cấm hẳn (xung tuổi)
    suggested_hour: str = ""


def _season_for_lunar(lunar_month: int) -> str:
    if lunar_month in (1, 2, 3): return "xuan"
    if lunar_month in (4, 5, 6): return "ha"
    if lunar_month in (7, 8, 9): return "thu"
    return "dong"


def _solar_to_lunar_month_approx(solar_month: int) -> int:
    """Approximate (solar month - 1) = lunar month — không chính xác 100%
    nhưng đủ cho mục đích chọn Hoàng/Hắc Đạo."""
    # Lich tháng 6 dương ≈ tháng 5 âm phần lớn
    return max(1, solar_month - 1)


def calculate_auspicious_days(
    bat_tu: BatTu,
    target_year: int,
    target_month: int,
    intent: str = "chuyen_nha",
    direction: str = "",
    location_zone: str = "",  # "bac"/"nam"/"đông"/"tây" - khu vực sống
) -> list[DayScore]:
    """Tính điểm + xếp hạng ngày trong tháng cho intent cụ thể.

    Args:
        bat_tu: Tứ trụ đệ tử
        target_year, target_month: tháng cần chọn ngày
        intent: loại việc
        direction: hướng cửa nhà mới ("đông", "tây bắc", ...)
        location_zone: khu vực đệ tử sống ("bac" cho Lạng Sơn — tăng cường tránh Tam Sát Bắc)
    """
    from datetime import datetime
    from calendar import monthrange

    from core.chronos import calculate_chronos_state

    weights = INTENT_WEIGHTS.get(intent, INTENT_WEIGHTS["general"])
    quy_nhan_set = set(THIEN_AT_QUY_NHAN.get(bat_tu.day_stem, ()))
    quy_nhan_year_set = set(THIEN_AT_QUY_NHAN.get(bat_tu.year_stem, ()))
    quy_nhan_all = quy_nhan_set | quy_nhan_year_set

    lunar_m = _solar_to_lunar_month_approx(target_month)
    season = _season_for_lunar(lunar_m)
    tam_sat = TAM_SAT_BY_SEASON[season]
    hoang_hac = HOANG_HAC_BY_LUNAR_MONTH[lunar_m]

    # Hành thiếu trong bát tự → bù
    thieu = bat_tu.thieu_hanh

    # Direction hành
    dir_hanh = DIRECTION_HANH.get(direction.lower().strip(), "")

    # Năm chi đệ tử (cho xung-hợp)
    nam_chi = bat_tu.year_branch

    days_in_month = monthrange(target_year, target_month)[1]
    results = []

    for day_num in range(1, days_in_month + 1):
        date_str = f"{target_year}-{target_month:02d}-{day_num:02d}"
        iso = f"{date_str}T08:00:00"
        try:
            state = calculate_chronos_state(iso, "Asia/Ho_Chi_Minh")
        except Exception:
            continue
        d_stem, d_branch = state.ganzhi.day.split()
        d_can_h = STEM_HANH[d_stem]
        d_chi_h = BRANCH_HANH[d_branch]

        dt = datetime(target_year, target_month, day_num)
        weekday = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"][dt.weekday()]

        score = 0
        notes = []
        is_taboo = False

        # 1. XUNG TUỔI (taboo)
        if d_branch == XUNG_CHI.get(nam_chi):
            score -= 100
            notes.append(f"⛔⛔⛔ XUNG TUỔI ({nam_chi}-{d_branch})")
            is_taboo = True

        # 2. Tam Sát mùa
        if d_branch in tam_sat:
            score -= 6
            notes.append(f"⛔ Tam Sát mùa {season}")
        # 3. Tam Sát + người ở khu vực — Lạng Sơn (bắc) → mùa hạ
        if location_zone == "bac" and d_branch in TAM_SAT_BY_SEASON["ha"] and season == "ha":
            score -= 2
            notes.append("⚠️ vùng Bắc — Tam Sát cộng dồn")

        # 4. Tự hình
        if d_branch == nam_chi and d_branch in TU_HINH:
            score -= 4
            notes.append(f"⚠️ Tự hình {nam_chi}")

        # 5. Tương hại
        if HAI_CHI.get(nam_chi) == d_branch:
            score -= 2
            notes.append(f"⚠️ Tương hại {nam_chi}-{d_branch}")

        # 6. Tương hình
        if HINH_CHI.get(nam_chi) == d_branch:
            score -= 2
            notes.append(f"⚠️ Tương hình {nam_chi}-{d_branch}")

        # 7. Lục Hợp với tuổi
        luc_hop = LUC_HOP.get(nam_chi)
        if luc_hop and d_branch == luc_hop[0]:
            score += 5
            notes.append(f"⭐ Lục Hợp {nam_chi}-{d_branch} ({luc_hop[1]})")

        # 8. Tam Hợp với tuổi
        for combo, hanh in TAM_HOP.items():
            if nam_chi in combo and d_branch in combo and d_branch != nam_chi:
                score += 4
                notes.append(f"⭐ Tam Hợp {hanh} với tuổi")

        # 9. Thiên Ất Quý Nhân (theo Nhật Can + Năm Can)
        if weights.get("prefer_quy_nhan") and d_branch in quy_nhan_all:
            score += 3
            notes.append(f"✨ Thiên Ất Quý Nhân ({d_branch})")

        # 10. Hoàng Đạo / Hắc Đạo
        if d_branch in hoang_hac["hoang"]:
            score += 2
            notes.append("✨ Hoàng Đạo")
        elif d_branch in hoang_hac["hac"]:
            score -= 2
            notes.append("⚠️ Hắc Đạo")

        # 11. Bổ hành thiếu
        for h in thieu:
            if d_can_h == h:
                score += 2
                notes.append(f"➕ Bù {h} thiếu (can)")
            if d_chi_h == h:
                score += 2
                notes.append(f"➕ Bù {h} thiếu (chi)")

        # 12. Hành cần theo intent
        for needed in weights["needs"]:
            if d_can_h == needed or d_chi_h == needed:
                score += 1
                notes.append(f"hợp intent '{weights['label']}' ({needed})")

        # 13. Cộng hưởng hướng cửa
        if dir_hanh:
            if d_can_h == dir_hanh or d_chi_h == dir_hanh:
                score += 2
                notes.append(f"🚪 cộng hưởng cửa {direction} ({dir_hanh})")

        # 14. Cuối tuần
        if weekday in ("T7", "CN"):
            score += 1
            notes.append("📅 cuối tuần")

        # Flag
        if is_taboo:
            flag = "❌❌ CẤM TUYỆT ĐỐI"
        elif score >= 10:
            flag = "⭐⭐⭐ XUẤT SẮC"
        elif score >= 7:
            flag = "⭐⭐ RẤT TỐT"
        elif score >= 4:
            flag = "⭐ Tốt"
        elif score <= -5:
            flag = "❌ Tránh"
        elif score < 0:
            flag = "⚠️ Không nên"
        else:
            flag = "bình"

        # Suggested hour: giờ Thìn an toàn, tránh xung
        xung_hour = XUNG_CHI.get(d_branch, "")
        if xung_hour == "Thìn":
            suggested_hour = "Tỵ 9-11h (Thìn xung)"
        else:
            suggested_hour = "Thìn 7-9h"

        results.append(DayScore(
            date=date_str, day_num=day_num, weekday=weekday,
            stem=d_stem, branch=d_branch,
            can_hanh=d_can_h, chi_hanh=d_chi_h,
            score=score, notes=notes, flag=flag, is_taboo=is_taboo,
            suggested_hour=suggested_hour,
        ))

    return results


def parse_bat_tu_from_birthdate(birth_iso: str, timezone: str = "Asia/Ho_Chi_Minh") -> BatTu:
    """Tính Bát Tự từ ngày sinh."""
    from core.chronos import calculate_chronos_state
    state = calculate_chronos_state(birth_iso, timezone)
    ys, yb = state.ganzhi.year.split()
    ms, mb = state.ganzhi.month.split()
    ds, db = state.ganzhi.day.split()
    hs, hb = state.ganzhi.hour.split()
    return BatTu(ys, yb, ms, mb, ds, db, hs, hb)


def analyze_full(
    birth_iso: str,
    target_year: int,
    target_month: int,
    intent: str = "chuyen_nha",
    direction: str = "",
    location_zone: str = "",
    timezone: str = "Asia/Ho_Chi_Minh",
) -> dict:
    """Top-level entry: phân tích Bát Tự + chọn ngày tốt."""
    bt = parse_bat_tu_from_birthdate(birth_iso, timezone)
    days = calculate_auspicious_days(
        bt, target_year, target_month, intent, direction, location_zone
    )

    # Sort, exclude taboo
    valid = [d for d in days if not d.is_taboo]
    valid.sort(key=lambda x: -x.score)
    top = valid[:7]
    taboos = [d for d in days if d.is_taboo or d.score <= -5]

    quy_nhan = THIEN_AT_QUY_NHAN.get(bt.day_stem, ())
    quy_nhan_year = THIEN_AT_QUY_NHAN.get(bt.year_stem, ())

    return {
        "bat_tu": {
            "year": f"{bt.year_stem} {bt.year_branch}",
            "month": f"{bt.month_stem} {bt.month_branch}",
            "day": f"{bt.day_stem} {bt.day_branch}",
            "hour": f"{bt.hour_stem} {bt.hour_branch}",
            "nhat_chu": bt.day_stem,
            "nhat_chu_hanh": bt.nhat_chu_hanh,
            "year_branch": bt.year_branch,
            "all_hanh": bt.all_hanh,
            "thieu_hanh": bt.thieu_hanh,
            "quy_nhan_day": list(quy_nhan),
            "quy_nhan_year": list(quy_nhan_year),
        },
        "intent": {
            "key": intent,
            "label": INTENT_WEIGHTS.get(intent, {}).get("label", intent),
        },
        "direction": direction,
        "location_zone": location_zone,
        "target": f"{target_month:02d}/{target_year}",
        "all_days": [d.__dict__ for d in days],
        "top_days": [d.__dict__ for d in top],
        "taboos": [d.__dict__ for d in taboos],
    }


if __name__ == "__main__":
    # Demo: tính cho bạn anh
    result = analyze_full(
        birth_iso="1988-05-02T08:00:00",
        target_year=2026,
        target_month=6,
        intent="chuyen_nha",
        direction="đông",
        location_zone="bac",
    )
    import json
    print(json.dumps(result["bat_tu"], indent=2, ensure_ascii=False))
    print()
    print("🌟 TOP 5 NGÀY:")
    for d in result["top_days"][:5]:
        print(f"  📅 {d['day_num']:2}/{d['date'][:7]} ({d['weekday']}) — "
              f"{d['stem']} {d['branch']} — Score {d['score']:+} — {d['flag']}")
        for n in d['notes'][:3]:
            print(f"     · {n}")
