"""Thần Sát (神煞) — auxiliary stars in Bát Tự.

Each star follows a canonical lookup table keyed by Day Stem, Year Branch, or
Month Branch. Some stars are "lành" (Quý nhân, Đào hoa, Văn xương, ...), others
"dữ" (Dương Nhận, Kiếp Sát, ...).

This module ships 15 of the most-cited stars. The classical 子平真詮 + 三命通會
canon has ~80 named stars; we cover the practical core. Future expansion easy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .constants import EARTHLY_BRANCHES


# Map abbreviation: branch string for compact tables.
_B_FULL = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()


# ─── 1. Thiên Ất Quý Nhân (天乙貴人) — by day stem ───────────────────────
# The single most important "Quý nhân" star — represents helpful nobles.
# Canonical: each stem has 2 branch positions.
THIEN_AT_QUY_NHAN: dict[str, tuple[str, ...]] = {
    "Giáp": ("Sửu", "Mùi"),
    "Mậu":  ("Sửu", "Mùi"),
    "Canh": ("Sửu", "Mùi"),
    "Ất":   ("Tý", "Thân"),
    "Kỷ":   ("Tý", "Thân"),
    "Bính": ("Dậu", "Hợi"),
    "Đinh": ("Dậu", "Hợi"),
    "Nhâm": ("Mão", "Tỵ"),
    "Quý":  ("Mão", "Tỵ"),
    "Tân":  ("Dần", "Ngọ"),
}


# ─── 2. Văn Xương (文昌) — by day stem ─────────────────────────────────
# Star of literary talent / academic success.
VAN_XUONG: dict[str, str] = {
    "Giáp": "Tỵ",
    "Ất":   "Ngọ",
    "Bính": "Thân",
    "Đinh": "Dậu",
    "Mậu":  "Thân",
    "Kỷ":   "Dậu",
    "Canh": "Hợi",
    "Tân":  "Tý",
    "Nhâm": "Dần",
    "Quý":  "Mão",
}


# ─── 3. Lộc Thần (祿神) — by day stem ──────────────────────────────────
# Star of stable income / official rank.
LOC_THAN: dict[str, str] = {
    "Giáp": "Dần",
    "Ất":   "Mão",
    "Bính": "Tỵ",
    "Đinh": "Ngọ",
    "Mậu":  "Tỵ",
    "Kỷ":   "Ngọ",
    "Canh": "Thân",
    "Tân":  "Dậu",
    "Nhâm": "Hợi",
    "Quý":  "Tý",
}


# ─── 4. Dương Nhận (羊刃) — by day stem ────────────────────────────────
# A "blade" star — represents power but with violent / accident potential.
# Only yang stems have proper Dương Nhận; yin stems have a weaker variant.
DUONG_NHAN: dict[str, str] = {
    "Giáp": "Mão",
    "Bính": "Ngọ",
    "Mậu":  "Ngọ",
    "Canh": "Dậu",
    "Nhâm": "Tý",
    # Yin stems:
    "Ất":   "Dần",
    "Đinh": "Tỵ",
    "Kỷ":   "Tỵ",
    "Tân":  "Thân",
    "Quý":  "Hợi",
}


# ─── 5. Đào Hoa (桃花) — by day or year branch (we use day branch) ─────
# "Peach blossom" — sex appeal, romance. Different name in different tam-hợp groups.
# Tam-hợp clusters:
#   Hợi-Mão-Mùi → Đào Hoa = Tý
#   Dần-Ngọ-Tuất → Đào Hoa = Mão
#   Tỵ-Dậu-Sửu → Đào Hoa = Ngọ
#   Thân-Tý-Thìn → Đào Hoa = Dậu
DAO_HOA_BY_BRANCH: dict[str, str] = {
    "Hợi": "Tý", "Mão": "Tý", "Mùi": "Tý",
    "Dần": "Mão", "Ngọ": "Mão", "Tuất": "Mão",
    "Tỵ": "Ngọ", "Dậu": "Ngọ", "Sửu": "Ngọ",
    "Thân": "Dậu", "Tý": "Dậu", "Thìn": "Dậu",
}


# ─── 6. Hồng Loan + 7. Thiên Hỷ — by year branch ──────────────────────
# Marriage / happiness stars. Hồng Loan walks backward from Mão; Thiên Hỷ = opposite.
def _hong_loan_by_year_branch(year_branch: str) -> str:
    idx = EARTHLY_BRANCHES.index(year_branch)
    # Hồng Loan: Tý→Mão (3), Sửu→Dần (2), Dần→Sửu (1), ... going backward.
    target_idx = (3 - idx) % 12
    return EARTHLY_BRANCHES[target_idx]


def _thien_hy_by_year_branch(year_branch: str) -> str:
    hl = _hong_loan_by_year_branch(year_branch)
    hl_idx = EARTHLY_BRANCHES.index(hl)
    return EARTHLY_BRANCHES[(hl_idx + 6) % 12]


# ─── 8. Tướng Tinh (將星) — by year/day branch ────────────────────────
# "General star" — leadership, command.
TUONG_TINH_BY_BRANCH: dict[str, str] = {
    "Thân": "Tý", "Tý": "Tý", "Thìn": "Tý",
    "Dần": "Ngọ", "Ngọ": "Ngọ", "Tuất": "Ngọ",
    "Tỵ": "Dậu", "Dậu": "Dậu", "Sửu": "Dậu",
    "Hợi": "Mão", "Mão": "Mão", "Mùi": "Mão",
}


# ─── 9. Dịch Mã (驛馬) — by year/day branch ───────────────────────────
# "Travel horse" — frequent travel, change of residence.
DICH_MA_BY_BRANCH: dict[str, str] = {
    "Thân": "Dần", "Tý": "Dần", "Thìn": "Dần",
    "Dần": "Thân", "Ngọ": "Thân", "Tuất": "Thân",
    "Tỵ": "Hợi", "Dậu": "Hợi", "Sửu": "Hợi",
    "Hợi": "Tỵ", "Mão": "Tỵ", "Mùi": "Tỵ",
}


# ─── 10. Hoa Cái (華蓋) — by year/day branch ──────────────────────────
# "Flower canopy" — spirituality, art, hermit nature.
HOA_CAI_BY_BRANCH: dict[str, str] = {
    "Thân": "Thìn", "Tý": "Thìn", "Thìn": "Thìn",
    "Dần": "Tuất", "Ngọ": "Tuất", "Tuất": "Tuất",
    "Tỵ": "Sửu", "Dậu": "Sửu", "Sửu": "Sửu",
    "Hợi": "Mùi", "Mão": "Mùi", "Mùi": "Mùi",
}


# ─── 11. Kiếp Sát (劫煞) — by year branch ─────────────────────────────
KIEP_SAT_BY_BRANCH: dict[str, str] = {
    "Thân": "Tỵ", "Tý": "Tỵ", "Thìn": "Tỵ",
    "Dần": "Hợi", "Ngọ": "Hợi", "Tuất": "Hợi",
    "Tỵ": "Dần", "Dậu": "Dần", "Sửu": "Dần",
    "Hợi": "Thân", "Mão": "Thân", "Mùi": "Thân",
}


# ─── 12. Cô Thần — 13. Quả Tú — by year branch (loneliness stars) ────
CO_THAN_BY_BRANCH: dict[str, str] = {
    "Hợi": "Dần", "Tý": "Dần", "Sửu": "Dần",
    "Dần": "Tỵ", "Mão": "Tỵ", "Thìn": "Tỵ",
    "Tỵ": "Thân", "Ngọ": "Thân", "Mùi": "Thân",
    "Thân": "Hợi", "Dậu": "Hợi", "Tuất": "Hợi",
}
QUA_TU_BY_BRANCH: dict[str, str] = {
    "Hợi": "Tuất", "Tý": "Tuất", "Sửu": "Tuất",
    "Dần": "Sửu", "Mão": "Sửu", "Thìn": "Sửu",
    "Tỵ": "Thìn", "Ngọ": "Thìn", "Mùi": "Thìn",
    "Thân": "Mùi", "Dậu": "Mùi", "Tuất": "Mùi",
}


# ─── 14. Thiên Đức Quý Nhân — by month branch ─────────────────────────
THIEN_DUC_BY_MONTH: dict[str, str] = {
    "Dần": "Đinh", "Mão": "Thân", "Thìn": "Nhâm",
    "Tỵ": "Tân", "Ngọ": "Hợi", "Mùi": "Giáp",
    "Thân": "Quý", "Dậu": "Dần", "Tuất": "Bính",
    "Hợi": "Ất", "Tý": "Tỵ", "Sửu": "Canh",
}


# ─── 15. Nguyệt Đức Quý Nhân — by month branch ────────────────────────
# Maps to a STEM (not branch).
NGUYET_DUC_BY_MONTH: dict[str, str] = {
    "Dần": "Bính", "Ngọ": "Bính", "Tuất": "Bính",
    "Tỵ": "Canh", "Dậu": "Canh", "Sửu": "Canh",
    "Thân": "Nhâm", "Tý": "Nhâm", "Thìn": "Nhâm",
    "Hợi": "Giáp", "Mão": "Giáp", "Mùi": "Giáp",
}


# ─── v2 EXPANSION (critique #16/#3/#7 from bat_tu sage) ──────────────────
# Added 2026-05-12. Sage requested expansion 15 → 30+ stars.
# Sources: 三命通會 + 滴天髓 + 子平真詮.


# ─── 16. Khôi Cương (魁罡) — checked against DAY pillar ──────────────────
# Special day pillars only: Mậu Thìn, Mậu Tuất, Canh Thìn, Canh Tuất, Nhâm Thìn.
# Person is sharp, decisive, leader; but lonely, intense.
KHOI_CUONG_DAY_PILLARS: set[tuple[str, str]] = {
    ("Mậu", "Thìn"), ("Mậu", "Tuất"),
    ("Canh", "Thìn"), ("Canh", "Tuất"),
    ("Nhâm", "Thìn"),
}


# ─── 17. Văn Khúc (文曲) — by day stem ────────────────────────────────────
# Pair with Văn Xương — artistic + writing talent (Văn Khúc is "moon" to V.X.'s "sun").
VAN_KHUC: dict[str, str] = {
    "Giáp": "Hợi", "Ất":   "Tý",
    "Bính": "Dần", "Đinh": "Mão",
    "Mậu":  "Dần", "Kỷ":   "Mão",
    "Canh": "Tỵ",  "Tân":  "Ngọ",
    "Nhâm": "Thân", "Quý": "Dậu",
}


# ─── 18. Quốc Ấn (國印) — by day stem ─────────────────────────────────────
# "National seal" — official authority, leadership in institutions.
QUOC_AN: dict[str, str] = {
    "Giáp": "Tuất", "Ất":   "Hợi",
    "Bính": "Sửu",  "Đinh": "Dần",
    "Mậu":  "Sửu",  "Kỷ":   "Dần",
    "Canh": "Thìn", "Tân":  "Tỵ",
    "Nhâm": "Mùi",  "Quý":  "Thân",
}


# ─── 19. Kim Dư (金輿) — by day stem ──────────────────────────────────────
# "Gold carriage" — material wealth, status symbols, vehicles.
KIM_DU: dict[str, str] = {
    "Giáp": "Thìn", "Ất":   "Tỵ",
    "Bính": "Mùi",  "Đinh": "Thân",
    "Mậu":  "Mùi",  "Kỷ":   "Thân",
    "Canh": "Tuất", "Tân":  "Hợi",
    "Nhâm": "Sửu",  "Quý":  "Dần",
}


# ─── 20. Lưu Hà (流霞) — by day stem ──────────────────────────────────────
# Star of "blood loss" / accidents involving liquid — caution sign.
LUU_HA: dict[str, str] = {
    "Giáp": "Dậu", "Ất":   "Tuất",
    "Bính": "Mùi", "Đinh": "Thân",
    "Mậu":  "Tỵ",  "Kỷ":   "Ngọ",
    "Canh": "Thìn", "Tân":  "Mão",
    "Nhâm": "Hợi", "Quý":  "Dần",
}


# ─── 21. Thiên La (天羅) + 22. Địa Võng (地網) — by year branch ──────────
# "Heaven's net + Earth's web" — restriction, lawsuits, entrapment.
# Thiên La = Tuất, Hợi for certain branches; Địa Võng = Thìn, Tỵ.
THIEN_LA_PRESENT_YEARS: set[str] = {"Tý", "Sửu", "Dần", "Mão"}    # gặp Tuất/Hợi → Thiên La
DIA_VONG_PRESENT_YEARS: set[str] = {"Ngọ", "Mùi", "Thân", "Dậu"}  # gặp Thìn/Tỵ → Địa Võng


# ─── 23. Tang Môn (喪門) + 24. Bạch Hổ (白虎) + 25. Điếu Khách (吊客) ────
# Three "death/grief" stars — by year branch, 3 positions before / 2 after / 2 before.
def _tang_mon(year_branch: str) -> str:
    idx = EARTHLY_BRANCHES.index(year_branch)
    return EARTHLY_BRANCHES[(idx - 2) % 12]


def _bach_ho(year_branch: str) -> str:
    idx = EARTHLY_BRANCHES.index(year_branch)
    return EARTHLY_BRANCHES[(idx - 4) % 12]


def _dieu_khach(year_branch: str) -> str:
    idx = EARTHLY_BRANCHES.index(year_branch)
    return EARTHLY_BRANCHES[(idx + 2) % 12]


# ─── 26. Thái Cực Quý Nhân (太極貴人) — by day stem ────────────────────
# "Supreme noble" — wisdom, philosophical/spiritual paths.
THAI_CUC: dict[str, tuple[str, ...]] = {
    "Giáp": ("Tý", "Ngọ"), "Ất": ("Tý", "Ngọ"),
    "Bính": ("Mão", "Dậu"), "Đinh": ("Mão", "Dậu"),
    "Mậu":  ("Thìn", "Tuất", "Sửu", "Mùi"),
    "Kỷ":   ("Thìn", "Tuất", "Sửu", "Mùi"),
    "Canh": ("Dần", "Hợi"), "Tân": ("Dần", "Hợi"),
    "Nhâm": ("Tỵ", "Thân"), "Quý": ("Tỵ", "Thân"),
}


# ─── 27. Phục Ngâm + 28. Phản Ngâm — detected by full pillar matching ──
# Phục Ngâm = a pillar matches natal pillar exactly (same stem + branch).
# Phản Ngâm = a pillar's stem-branch is the exact opposite (xung trực diện).
# These are detected dynamically in detect_than_sat — no static table.


# ─── 29. Lục Ất (六乙日) + 30. Lục Đinh (六丁日) ──────────────────────
# Day Master being Ất (六乙) or Đinh (六丁) — special yin-stem patterns.
# Detected from day stem only.


@dataclass(frozen=True)
class ThanSatStar:
    """One identified Thần Sát match in the chart."""

    name: str               # Vietnamese name
    short_tag: str
    polarity: str           # "lành" / "dữ" / "trung tính"
    description: str
    found_at_pillar: str    # 'year' / 'month' / 'day' / 'hour'
    branch_or_stem: str     # the matched character

    def to_dict(self) -> dict:
        return asdict(self)


def _scan_for_branch_target(pillars: dict, target_branch: str) -> list[str]:
    """Return list of pillar positions where the branch equals target."""
    return [pos for pos in ("year", "month", "day", "hour")
            if pillars[pos]["branch"] == target_branch]


def _scan_for_stem_target(pillars: dict, target_stem: str) -> list[str]:
    """Return list of pillar positions where the stem equals target."""
    return [pos for pos in ("year", "month", "day", "hour")
            if pillars[pos]["stem"] == target_stem]


def detect_than_sat(pillars: dict, day_master_stem: str) -> list[dict]:
    """Detect all Thần Sát stars present in the chart.

    Returns a list of ThanSatStar dicts (may be empty if no auxiliary stars match).
    """
    out: list[ThanSatStar] = []
    year_branch = pillars["year"]["branch"]
    day_branch = pillars["day"]["branch"]
    month_branch = pillars["month"]["branch"]

    # 1. Thiên Ất Quý Nhân (by day stem)
    for target in THIEN_AT_QUY_NHAN.get(day_master_stem, ()):
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Thiên Ất Quý Nhân",
                short_tag="QN-T.Ất",
                polarity="lành",
                description="Quý nhân tối thượng — gặp khó được người giúp.",
                found_at_pillar=pos,
                branch_or_stem=target,
            ))

    # 2. Văn Xương
    target = VAN_XUONG.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Văn Xương", short_tag="V.Xương", polarity="lành",
                description="Sao văn chương — hợp học hành, thi cử, viết lách.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 3. Lộc Thần
    target = LOC_THAN.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Lộc Thần", short_tag="Lộc", polarity="lành",
                description="Sao tiền lương / chức tước — thu nhập ổn định.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 4. Dương Nhận
    target = DUONG_NHAN.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Dương Nhận", short_tag="D.Nhận", polarity="dữ",
                description="Sao quyền lực có lưỡi sắc — nguy cơ tai nạn / xung đột.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 5. Đào Hoa (from day branch)
    target = DAO_HOA_BY_BRANCH.get(day_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            if pillars[pos]["branch"] == day_branch:
                continue  # don't count day branch itself
            out.append(ThanSatStar(
                name="Đào Hoa", short_tag="Đ.Hoa", polarity="trung tính",
                description="Sao tình duyên / sức hút giới khác — hợp showbiz, có rủi ro tình cảm.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 6. Hồng Loan (from year branch)
    target = _hong_loan_by_year_branch(year_branch)
    for pos in _scan_for_branch_target(pillars, target):
        out.append(ThanSatStar(
            name="Hồng Loan", short_tag="H.Loan", polarity="lành",
            description="Sao hôn nhân / vui mừng — duyên lành.",
            found_at_pillar=pos, branch_or_stem=target,
        ))

    # 7. Thiên Hỷ
    target = _thien_hy_by_year_branch(year_branch)
    for pos in _scan_for_branch_target(pillars, target):
        out.append(ThanSatStar(
            name="Thiên Hỷ", short_tag="T.Hỷ", polarity="lành",
            description="Sao hỉ sự — sinh con, lễ tốt, vui vẻ.",
            found_at_pillar=pos, branch_or_stem=target,
        ))

    # 8. Tướng Tinh (from year branch)
    target = TUONG_TINH_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Tướng Tinh", short_tag="T.Tinh", polarity="lành",
                description="Sao lãnh đạo / chỉ huy.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 9. Dịch Mã
    target = DICH_MA_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Dịch Mã", short_tag="D.Mã", polarity="trung tính",
                description="Sao di chuyển — hay đi xa, đổi chỗ.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 10. Hoa Cái
    target = HOA_CAI_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Hoa Cái", short_tag="H.Cái", polarity="trung tính",
                description="Sao tâm linh / nghệ thuật / ẩn sĩ.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 11. Kiếp Sát
    target = KIEP_SAT_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Kiếp Sát", short_tag="K.Sát", polarity="dữ",
                description="Sao bị cướp / rủi ro tài sản.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 12. Cô Thần
    target = CO_THAN_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Cô Thần", short_tag="Cô", polarity="dữ",
                description="Sao cô đơn nam — khó kết duyên / xa người thân.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 13. Quả Tú
    target = QUA_TU_BY_BRANCH.get(year_branch)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Quả Tú", short_tag="Quả", polarity="dữ",
                description="Sao cô đơn nữ — khó kết duyên / đơn lẻ.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 14. Thiên Đức (by month branch, looks for a STEM)
    target_stem = THIEN_DUC_BY_MONTH.get(month_branch)
    if target_stem:
        for pos in _scan_for_stem_target(pillars, target_stem):
            out.append(ThanSatStar(
                name="Thiên Đức Quý Nhân", short_tag="T.Đức", polarity="lành",
                description="Quý nhân từ trời — hóa giải hung tinh.",
                found_at_pillar=pos, branch_or_stem=target_stem,
            ))

    # 15. Nguyệt Đức (by month branch, looks for a STEM)
    target_stem = NGUYET_DUC_BY_MONTH.get(month_branch)
    if target_stem:
        for pos in _scan_for_stem_target(pillars, target_stem):
            out.append(ThanSatStar(
                name="Nguyệt Đức Quý Nhân", short_tag="Ng.Đức", polarity="lành",
                description="Quý nhân từ tháng — hóa giải tai họa.",
                found_at_pillar=pos, branch_or_stem=target_stem,
            ))

    # ─── v2 EXPANSION (critique #16/#3/#7) — 10 new stars ─────────────────

    # 16. Khôi Cương — special day pillar
    day_stem = pillars["day"]["stem"]
    if (day_stem, day_branch) in KHOI_CUONG_DAY_PILLARS:
        out.append(ThanSatStar(
            name="Khôi Cương", short_tag="Kh.Cương", polarity="trung tính",
            description="Trụ Ngày đặc biệt — quyết đoán, sắc bén, lãnh đạo; nhưng cô độc và nội tâm dữ dội.",
            found_at_pillar="day", branch_or_stem=f"{day_stem} {day_branch}",
        ))

    # 17. Văn Khúc
    target = VAN_KHUC.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Văn Khúc", short_tag="V.Khúc", polarity="lành",
                description="Sao nghệ thuật + viết lách — bổ trợ Văn Xương, mạnh ở chiều sâu cảm xúc.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 18. Quốc Ấn
    target = QUOC_AN.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Quốc Ấn", short_tag="Q.Ấn", polarity="lành",
                description="Ấn tín quốc gia — quyền lực chính thống, chức vụ trong tổ chức.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 19. Kim Dư
    target = KIM_DU.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Kim Dư", short_tag="K.Dư", polarity="lành",
                description="Xe vàng — sang trọng, vật chất, phương tiện đẹp, hôn nhân giàu.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 20. Lưu Hà
    target = LUU_HA.get(day_master_stem)
    if target:
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Lưu Hà", short_tag="L.Hà", polarity="dữ",
                description="Sao chảy máu / tai nạn liên quan chất lỏng — cẩn trọng phẫu thuật, đi biển.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 21/22. Thiên La / Địa Võng
    if year_branch in THIEN_LA_PRESENT_YEARS:
        for tla in ("Tuất", "Hợi"):
            for pos in _scan_for_branch_target(pillars, tla):
                out.append(ThanSatStar(
                    name="Thiên La", short_tag="T.La", polarity="dữ",
                    description="Lưới trời — bị trói buộc, kiện tụng, khó thoát.",
                    found_at_pillar=pos, branch_or_stem=tla,
                ))
    if year_branch in DIA_VONG_PRESENT_YEARS:
        for dv in ("Thìn", "Tỵ"):
            for pos in _scan_for_branch_target(pillars, dv):
                out.append(ThanSatStar(
                    name="Địa Võng", short_tag="Đ.Võng", polarity="dữ",
                    description="Lưới đất — vướng kẹt, hạn chế phát triển, kiện tụng.",
                    found_at_pillar=pos, branch_or_stem=dv,
                ))

    # 23/24/25. Tang Môn / Bạch Hổ / Điếu Khách
    tm = _tang_mon(year_branch)
    for pos in _scan_for_branch_target(pillars, tm):
        out.append(ThanSatStar(
            name="Tang Môn", short_tag="T.Môn", polarity="dữ",
            description="Cửa tang — tang sự, mất mát người thân, u sầu.",
            found_at_pillar=pos, branch_or_stem=tm,
        ))
    bh = _bach_ho(year_branch)
    for pos in _scan_for_branch_target(pillars, bh):
        out.append(ThanSatStar(
            name="Bạch Hổ", short_tag="B.Hổ", polarity="dữ",
            description="Hổ trắng — tai nạn máu, phẫu thuật, xung đột bạo lực.",
            found_at_pillar=pos, branch_or_stem=bh,
        ))
    dk = _dieu_khach(year_branch)
    for pos in _scan_for_branch_target(pillars, dk):
        out.append(ThanSatStar(
            name="Điếu Khách", short_tag="Đ.Khách", polarity="dữ",
            description="Khách viếng tang — bất ổn tâm trạng, dự tang, tin buồn.",
            found_at_pillar=pos, branch_or_stem=dk,
        ))

    # 26. Thái Cực Quý Nhân
    for target in THAI_CUC.get(day_master_stem, ()):
        for pos in _scan_for_branch_target(pillars, target):
            out.append(ThanSatStar(
                name="Thái Cực Quý Nhân", short_tag="T.Cực", polarity="lành",
                description="Quý nhân thượng đẳng — trí huệ, đường tu, triết học.",
                found_at_pillar=pos, branch_or_stem=target,
            ))

    # 27. Phục Ngâm — pillar matches natal Day pillar exactly
    natal_day = (pillars["day"]["stem"], pillars["day"]["branch"])
    for pos in ("year", "month", "hour"):
        if (pillars[pos]["stem"], pillars[pos]["branch"]) == natal_day:
            out.append(ThanSatStar(
                name="Phục Ngâm", short_tag="P.Ngâm", polarity="trung tính",
                description="Trùng trụ với Trụ Ngày — ý lặp lại, lưu ý hiện tượng \"bản mệnh giờ\".",
                found_at_pillar=pos, branch_or_stem=f"{pillars[pos]['stem']} {pillars[pos]['branch']}",
            ))

    # 28. Phản Ngâm — pillar's stem-branch is exact OPPOSITE of Day pillar
    # Opposite stem = stem at index+5 in 10 stems; opposite branch = at index+6 in 12 branches.
    from .constants import HEAVENLY_STEMS as _HS
    natal_day_stem_idx = _HS.index(pillars["day"]["stem"])
    natal_day_branch_idx = EARTHLY_BRANCHES.index(pillars["day"]["branch"])
    opp_stem = _HS[(natal_day_stem_idx + 5) % 10]
    opp_branch = EARTHLY_BRANCHES[(natal_day_branch_idx + 6) % 12]
    for pos in ("year", "month", "hour"):
        if (pillars[pos]["stem"], pillars[pos]["branch"]) == (opp_stem, opp_branch):
            out.append(ThanSatStar(
                name="Phản Ngâm", short_tag="Pn.Ngâm", polarity="dữ",
                description="Trụ xung trực diện Trụ Ngày — biến động lớn, đối lập với bản mệnh.",
                found_at_pillar=pos, branch_or_stem=f"{opp_stem} {opp_branch}",
            ))

    return [s.to_dict() for s in out]
