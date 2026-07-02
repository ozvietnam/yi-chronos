"""An Sao Tử Vi Đẩu Số — canonical Bắc Phái star-placement algorithm.

Reference spec: docs/upgrade-plan-from-kabalavn-research.md mục 2.1.
Cross-verified with: iztro (SylarLong/iztro MIT), Renhuai123/ziwei-doushu,
tuvisaigon.vn, xemtuong.net, ncc.com.tw 安星訣.

Indexing: Tý=0, Sửu=1, ..., Hợi=11. All positions are integers in this space.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache


# ─── Constants ────────────────────────────────────────────────────────────────

BRANCHES_TVI: tuple[str, ...] = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)

STEMS_TVI: tuple[str, ...] = (
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
)

# Map for quick lookup
B = {name: i for i, name in enumerate(BRANCHES_TVI)}
S = {name: i for i, name in enumerate(STEMS_TVI)}


def _fix(x: int) -> int:
    """Python-safe modulo to [0, 12)."""
    return ((x % 12) + 12) % 12


# 12 palace names in canonical Bắc Phái order (Trần Đoàn — Phú Thái Vi Q1 p20 #511).
# Order: starting from Mệnh, going counter-clockwise on chart layout (= decreasing chi index).
# Kinh điển: "Cự đáo nhị cung, tất thị huynh đệ vô nghĩa" → cung 2 = Huynh Đệ (not Phụ Mẫu).
# Standard library: iztro (MIT, SylarLong) uses same order: 命兄夫子財疾遷奴官田福父.
#
# BUG-FIX 2026-05-20: Previous order had Phụ Mẫu at index 1 (Vietnamese popular listing
# order). When combined with `menh_index - k` traversal, this placed Phụ Mẫu at the chi
# where canonical Bắc Phái places Huynh Đệ, etc. — entire chart rotated wrong.
PALACE_NAMES: tuple[str, ...] = (
    "Mệnh",        # 0
    "Huynh Đệ",    # 1  (Cự đáo NHỊ CUNG = Huynh Đệ — Phú Thái Vi)
    "Phu Thê",     # 2
    "Tử Tức",      # 3
    "Tài Bạch",    # 4
    "Tật Ách",     # 5
    "Thiên Di",    # 6  (đối với Mệnh)
    "Nô Bộc",      # 7
    "Quan Lộc",    # 8
    "Điền Trạch",  # 9
    "Phúc Đức",    # 10
    "Phụ Mẫu",     # 11 (đối với Tật Ách)
)


# ─── 1. Cung Mệnh + Cung Thân ─────────────────────────────────────────────────


def cung_menh_index(lunar_month: int, hour_index: int) -> int:
    """Cung Mệnh = fix(2 + M - H) where H is 1-based hour (Tý=1)."""
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"lunar_month must be 1..12, got {lunar_month}")
    if not 1 <= hour_index <= 12:
        raise ValueError(f"hour_index must be 1..12 (Tý=1, Hợi=12), got {hour_index}")
    return _fix(2 + lunar_month - hour_index)


def cung_than_index(lunar_month: int, hour_index: int) -> int:
    """Cung Thân = fix(M + H)."""
    return _fix(lunar_month + hour_index)


def hour_index_from_branch(hour_branch: str) -> int:
    """Convert Tý..Hợi to 1..12 for the formulas above."""
    return B[hour_branch] + 1


# ─── 2. 12 Palaces arrangement ────────────────────────────────────────────────


def arrange_palaces(menh_index: int) -> list[dict]:
    """Place all 12 palaces counter-clockwise from Cung Mệnh.

    Returns list of 12 dicts: [{'name': 'Mệnh', 'branch_index': 2, 'branch': 'Dần'}, ...]
    """
    out: list[dict] = []
    for k, name in enumerate(PALACE_NAMES):
        idx = _fix(menh_index - k)
        out.append({
            "name": name,
            "branch_index": idx,
            "branch": BRANCHES_TVI[idx],
        })
    return out


# ─── 3. Cục Số (五行局) ───────────────────────────────────────────────────────
#
# Lookup table from §4a of spec.
# Index: (stem_pair, branch_pair) where:
#   stem_pair ∈ {"Giap-Ky", "At-Canh", "Binh-Tan", "Dinh-Nham", "Mau-Quy"}
#   branch_pair = lục-hợp pair of cung Mệnh branch.

_STEM_PAIR: dict[str, str] = {
    "Giáp": "Giap-Ky",   "Kỷ":   "Giap-Ky",
    "Ất":   "At-Canh",   "Canh": "At-Canh",
    "Bính": "Binh-Tan",  "Tân":  "Binh-Tan",
    "Đinh": "Dinh-Nham", "Nhâm": "Dinh-Nham",
    "Mậu":  "Mau-Quy",   "Quý":  "Mau-Quy",
}

_BRANCH_PAIR: dict[str, str] = {
    "Tý": "Ty-Suu",   "Sửu": "Ty-Suu",
    "Dần": "Dan-Mao", "Mão": "Dan-Mao",
    "Thìn": "Thin-Ty", "Tỵ": "Thin-Ty",
    "Ngọ": "Ngo-Mui", "Mùi": "Ngo-Mui",
    "Thân": "Than-Dau", "Dậu": "Than-Dau",
    "Tuất": "Tuat-Hoi", "Hợi": "Tuat-Hoi",
}

# (stem_pair, branch_pair) → cục số {2, 3, 4, 5, 6}
_CUC_TABLE: dict[tuple[str, str], int] = {
    ("Giap-Ky",   "Ty-Suu"):   2,  ("Giap-Ky",   "Dan-Mao"):  6,
    ("Giap-Ky",   "Thin-Ty"):  3,  ("Giap-Ky",   "Ngo-Mui"):  5,
    ("Giap-Ky",   "Than-Dau"): 4,  ("Giap-Ky",   "Tuat-Hoi"): 6,

    ("At-Canh",   "Ty-Suu"):   6,  ("At-Canh",   "Dan-Mao"):  5,
    ("At-Canh",   "Thin-Ty"):  4,  ("At-Canh",   "Ngo-Mui"):  3,
    ("At-Canh",   "Than-Dau"): 2,  ("At-Canh",   "Tuat-Hoi"): 5,

    ("Binh-Tan",  "Ty-Suu"):   5,  ("Binh-Tan",  "Dan-Mao"):  3,
    ("Binh-Tan",  "Thin-Ty"):  2,  ("Binh-Tan",  "Ngo-Mui"):  4,
    ("Binh-Tan",  "Than-Dau"): 6,  ("Binh-Tan",  "Tuat-Hoi"): 3,

    ("Dinh-Nham", "Ty-Suu"):   3,  ("Dinh-Nham", "Dan-Mao"):  4,
    ("Dinh-Nham", "Thin-Ty"):  6,  ("Dinh-Nham", "Ngo-Mui"):  2,
    ("Dinh-Nham", "Than-Dau"): 5,  ("Dinh-Nham", "Tuat-Hoi"): 4,

    ("Mau-Quy",   "Ty-Suu"):   4,  ("Mau-Quy",   "Dan-Mao"):  2,
    ("Mau-Quy",   "Thin-Ty"):  5,  ("Mau-Quy",   "Ngo-Mui"):  6,
    ("Mau-Quy",   "Than-Dau"): 3,  ("Mau-Quy",   "Tuat-Hoi"): 2,
}

CUC_NAMES: dict[int, str] = {
    2: "Thủy Nhị Cục",
    3: "Mộc Tam Cục",
    4: "Kim Tứ Cục",
    5: "Thổ Ngũ Cục",
    6: "Hỏa Lục Cục",
}


def cuc_so(year_stem: str, menh_branch: str) -> int:
    """Return Cục số (2/3/4/5/6) for given year stem + Mệnh branch."""
    sp = _STEM_PAIR.get(year_stem)
    bp = _BRANCH_PAIR.get(menh_branch)
    if sp is None or bp is None:
        raise ValueError(f"Unknown stem {year_stem!r} or branch {menh_branch!r}")
    return _CUC_TABLE[(sp, bp)]


# ─── 4. Tử Vi Anchor (iztro algorithm) ────────────────────────────────────────


@lru_cache(maxsize=1)
def _build_ziwei_table() -> dict[tuple[int, int], int]:
    """Pre-compute Tử Vi position for all (cuc, day) pairs.

    Uses the classical 安紫微訣 iteration:
        for offset in 0,1,2,...
            divisor = D + offset
            quotient, remainder = divmod(divisor, C)
            if remainder == 0: stop
        position_dan_base = quotient - 1   # 0 = Dần (寅) in canonical counting
        position_dan_base += offset if (offset % 2 == 0) else -offset
        # Convert from Dần-base (0=Dần) to chi-base (0=Tý): +2 chi index
        ziwei_chi = (position_dan_base + 2) mod 12

    BUG-FIX 2026-05-20: Previously the formula returned `_fix(ziwei)` treating
    `quotient - 1` directly as chi index (Tý=0). Per Phú Thái Vi Q1 the canonical
    counting starts at Dần (chi 2). Verified 30/30 (Thủy) + 29/30 (Thổ) cục
    against kinh điển 紫微定位表.
    """
    table: dict[tuple[int, int], int] = {}
    for cuc in (2, 3, 4, 5, 6):
        for day in range(1, 31):
            offset = 0
            while True:
                divisor = day + offset
                quotient, remainder = divmod(divisor, cuc)
                if remainder == 0:
                    break
                offset += 1
                if offset > 100:   # safety bound
                    break
            q = quotient % 12
            position_dan_base = q - 1
            position_dan_base += (offset if offset % 2 == 0 else -offset)
            # +2 to convert from Dần-base (0=Dần) to chi-base (0=Tý)
            table[(cuc, day)] = _fix(position_dan_base + 2)
    return table


def tu_vi_position(cuc: int, lunar_day: int) -> int:
    """Return Tử Vi branch index for given cục + lunar day."""
    if cuc not in (2, 3, 4, 5, 6):
        raise ValueError(f"cuc must be 2..6, got {cuc}")
    if not 1 <= lunar_day <= 30:
        raise ValueError(f"lunar_day must be 1..30, got {lunar_day}")
    return _build_ziwei_table()[(cuc, lunar_day)]


# ─── 5. 14 Chính Tinh Placement ───────────────────────────────────────────────

def thien_phu_position(tu_vi_idx: int) -> int:
    """Return Thiên Phủ branch index given Tử Vi's branch index.

    Classical Bắc Phái rule: count k steps CW from Dần to Tử Vi,
    then count k steps CCW from Dần → Thiên Phủ.
    Formula: Thiên Phủ = _fix(4 - tu_vi_idx)  [Dần chi=2, axis at Dần-Thân].
    Verified: Tử Vi Mão(3) → Thiên Phủ Sửu(1) per tuvi.vn + Phú Thái Vi.
    BUG-FIX 2026-05-20: Previous table used _fix(10-x) = Tỵ-Hợi axis (wrong).
    """
    return _fix(4 - tu_vi_idx)


# 14 chính tinh names (matches engine/tu_vi/chinh_tinh.py)
CHINH_TINH_NAMES: tuple[str, ...] = (
    # Tử Vi system (6 stars)
    "Tử Vi", "Thiên Cơ", "Thái Dương", "Vũ Khúc", "Thiên Đồng", "Liêm Trinh",
    # Thiên Phủ system (8 stars)
    "Thiên Phủ", "Thái Âm", "Tham Lang", "Cự Môn",
    "Thiên Tướng", "Thiên Lương", "Thất Sát", "Phá Quân",
)


def place_14_chinh_tinh(tu_vi_idx: int) -> dict[str, int]:
    """Place all 14 chính tinh based on Tử Vi position.

    Returns {star_name_vi: branch_index 0..11}.
    """
    tianfu = thien_phu_position(tu_vi_idx)
    return {
        # Tử Vi chùm (counter-clockwise from Tử Vi)
        "Tử Vi":      tu_vi_idx,
        "Thiên Cơ":   _fix(tu_vi_idx - 1),
        "Thái Dương": _fix(tu_vi_idx - 3),
        "Vũ Khúc":    _fix(tu_vi_idx - 4),
        "Thiên Đồng": _fix(tu_vi_idx - 5),
        "Liêm Trinh": _fix(tu_vi_idx - 8),
        # Thiên Phủ chùm (clockwise from Thiên Phủ)
        "Thiên Phủ":   tianfu,
        "Thái Âm":     _fix(tianfu + 1),
        "Tham Lang":   _fix(tianfu + 2),
        "Cự Môn":      _fix(tianfu + 3),
        "Thiên Tướng": _fix(tianfu + 4),
        "Thiên Lương": _fix(tianfu + 5),
        "Thất Sát":    _fix(tianfu + 6),
        "Phá Quân":    _fix(tianfu + 10),
    }


# ─── 6. Tứ Hóa ────────────────────────────────────────────────────────────────
# Table indexed by year stem → (Lộc, Quyền, Khoa, Kỵ).

TU_HOA_TABLE: dict[str, dict[str, str]] = {
    "Giáp": {"Lộc": "Liêm Trinh", "Quyền": "Phá Quân",  "Khoa": "Vũ Khúc",  "Kỵ": "Thái Dương"},
    "Ất":   {"Lộc": "Thiên Cơ",   "Quyền": "Thiên Lương","Khoa": "Tử Vi",   "Kỵ": "Thái Âm"},
    "Bính": {"Lộc": "Thiên Đồng", "Quyền": "Thiên Cơ",  "Khoa": "Văn Xương","Kỵ": "Liêm Trinh"},
    "Đinh": {"Lộc": "Thái Âm",    "Quyền": "Thiên Đồng","Khoa": "Thiên Cơ", "Kỵ": "Cự Môn"},
    "Mậu":  {"Lộc": "Tham Lang",  "Quyền": "Thái Âm",   "Khoa": "Hữu Bật", "Kỵ": "Thiên Cơ"},
    "Kỷ":   {"Lộc": "Vũ Khúc",    "Quyền": "Tham Lang", "Khoa": "Thiên Lương","Kỵ": "Văn Khúc"},
    "Canh": {"Lộc": "Thái Dương", "Quyền": "Vũ Khúc",   "Khoa": "Thái Âm", "Kỵ": "Thiên Đồng"},
    "Tân":  {"Lộc": "Cự Môn",     "Quyền": "Thái Dương","Khoa": "Văn Khúc","Kỵ": "Văn Xương"},
    "Nhâm": {"Lộc": "Thiên Lương","Quyền": "Tử Vi",     "Khoa": "Tả Phù",  "Kỵ": "Vũ Khúc"},
    "Quý":  {"Lộc": "Phá Quân",   "Quyền": "Cự Môn",    "Khoa": "Thái Âm", "Kỵ": "Tham Lang"},
}


def tu_hoa_assignments(year_stem: str) -> dict[str, str]:
    """Return {hoa_name: star_name} for the given year stem."""
    if year_stem not in TU_HOA_TABLE:
        raise ValueError(f"Unknown year stem: {year_stem!r}")
    return TU_HOA_TABLE[year_stem]


# ─── 7. 6 Phụ Tinh ────────────────────────────────────────────────────────────


def ta_phu(lunar_month: int) -> int:
    """Tả Phù = fix(Thìn + M - 1) = fix(M + 3)."""
    return _fix(B["Thìn"] + (lunar_month - 1))


def huu_bat(lunar_month: int) -> int:
    """Hữu Bật = fix(Tuất - (M - 1)) = fix(11 - M)."""
    return _fix(B["Tuất"] - (lunar_month - 1))


def van_khuc(hour_index: int) -> int:
    """Văn Khúc = fix(Thìn + (H - 1))."""
    return _fix(B["Thìn"] + (hour_index - 1))


def van_xuong(hour_index: int) -> int:
    """Văn Xương = fix(Tuất - (H - 1))."""
    return _fix(B["Tuất"] - (hour_index - 1))


_KHOI_VIET: dict[str, tuple[str, str]] = {
    "Giáp": ("Sửu", "Mùi"),  "Mậu": ("Sửu", "Mùi"),  "Canh": ("Sửu", "Mùi"),
    "Ất":   ("Tý", "Thân"),  "Kỷ":  ("Tý", "Thân"),
    "Bính": ("Hợi", "Dậu"),  "Đinh":("Hợi", "Dậu"),
    "Tân":  ("Ngọ", "Dần"),
    "Nhâm": ("Mão", "Tỵ"),   "Quý": ("Mão", "Tỵ"),
}


def thien_khoi_viet(year_stem: str) -> tuple[int, int]:
    """Return (Thiên Khôi index, Thiên Việt index)."""
    if year_stem not in _KHOI_VIET:
        raise ValueError(f"Unknown year stem: {year_stem!r}")
    khoi_b, viet_b = _KHOI_VIET[year_stem]
    return B[khoi_b], B[viet_b]


# ─── 8. Sát Tinh ──────────────────────────────────────────────────────────────


_LOC_TON: dict[str, str] = {
    "Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Đinh": "Ngọ",
    "Mậu":  "Tỵ",  "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
    "Nhâm": "Hợi", "Quý": "Tý",
}


def loc_ton(year_stem: str) -> int:
    """Return Lộc Tồn branch index."""
    return B[_LOC_TON[year_stem]]


def kinh_duong(year_stem: str) -> int:
    """Kình Dương = Lộc Tồn + 1 (祿前)."""
    return _fix(loc_ton(year_stem) + 1)


def da_la(year_stem: str) -> int:
    """Đà La = Lộc Tồn - 1 (祿後)."""
    return _fix(loc_ton(year_stem) - 1)


# Hỏa Tinh / Linh Tinh anchors by year-branch tam-hợp group
_HOA_LINH_ANCHORS: dict[str, tuple[str, str]] = {
    # (Hỏa anchor, Linh anchor)
    # Dần-Ngọ-Tuất
    "Dần": ("Sửu", "Mão"), "Ngọ": ("Sửu", "Mão"), "Tuất": ("Sửu", "Mão"),
    # Thân-Tý-Thìn
    "Thân": ("Dần", "Tuất"), "Tý": ("Dần", "Tuất"), "Thìn": ("Dần", "Tuất"),
    # Tỵ-Dậu-Sửu
    "Tỵ": ("Mão", "Tuất"), "Dậu": ("Mão", "Tuất"), "Sửu": ("Mão", "Tuất"),
    # Hợi-Mão-Mùi
    "Hợi": ("Dậu", "Tuất"), "Mão": ("Dậu", "Tuất"), "Mùi": ("Dậu", "Tuất"),
}


def hoa_linh_tinh(year_branch: str, hour_index: int) -> tuple[int, int]:
    """Return (Hỏa Tinh idx, Linh Tinh idx)."""
    huo_anchor, linh_anchor = _HOA_LINH_ANCHORS[year_branch]
    h = hour_index - 1   # 0-based
    return _fix(B[huo_anchor] + h), _fix(B[linh_anchor] + h)


def dia_khong_kiep(hour_index: int) -> tuple[int, int]:
    """Return (Địa Không, Địa Kiếp) — both anchored at Hợi.

    Địa Kiếp = fix(Hợi + h);  Địa Không = fix(Hợi - h).
    """
    h = hour_index - 1
    kiep = _fix(B["Hợi"] + h)
    khong = _fix(B["Hợi"] - h)
    return khong, kiep


# ─── 9. Đại Vận ───────────────────────────────────────────────────────────────


def dai_van_direction(year_stem: str, gender: str) -> int:
    """+1 = thuận (Dương Nam / Âm Nữ); -1 = nghịch."""
    yang_year = year_stem in ("Giáp", "Bính", "Mậu", "Canh", "Nhâm")
    is_male = gender == "nam"
    if (yang_year and is_male) or (not yang_year and not is_male):
        return +1
    return -1


def dai_van_trajectory(
    *,
    menh_index: int,
    cuc: int,
    year_stem: str,
    gender: str,
    num_cycles: int = 12,
) -> list[dict]:
    """Build Đại Vận trajectory: list of N 10-year cycles."""
    direction = dai_van_direction(year_stem, gender)
    out: list[dict] = []
    for k in range(num_cycles):
        idx = _fix(menh_index + direction * k)
        start_age = cuc + 10 * k
        out.append({
            "cycle_index": k + 1,
            "branch_index": idx,
            "branch": BRANCHES_TVI[idx],
            "start_age": start_age,
            "end_age": start_age + 9,
        })
    return out


# ─── 10. Tiểu Hạn ─────────────────────────────────────────────────────────────


_TIEU_HAN_START: dict[str, str] = {
    "Dần": "Thìn", "Ngọ": "Thìn", "Tuất": "Thìn",
    "Thân": "Tuất", "Tý": "Tuất", "Thìn": "Tuất",
    "Tỵ": "Mùi", "Dậu": "Mùi", "Sửu": "Mùi",
    "Hợi": "Sửu", "Mão": "Sửu", "Mùi": "Sửu",
}


def tieu_han_for_age(year_branch: str, gender: str, age: int) -> int:
    """Return Tiểu Hạn branch index for given age (lunar age, 1-based)."""
    start = B[_TIEU_HAN_START[year_branch]]
    direction = +1 if gender == "nam" else -1
    return _fix(start + direction * (age - 1))


# ─── 10b. Mệnh chủ, Thân chủ, Đẩu Quân ──────────────────────────────────────
# Source: Tử Vi Đẩu Số Toàn Thư (Trần Đoàn), Quyển 2:
#   "An Mệnh chủ · An Thân chủ · An Đẩu Quân quyết"
# Đây là 3 sao bổ sung thuộc nền móng kinh điển Bắc Phái mà engine
# hiện chỉ có 14 chính tinh + phụ + sát chưa cover.

# Mệnh chủ: chọn theo địa chi cung Mệnh
# Source: TVDSTT Q.2 - An Mệnh chủ quyết
_MENH_CHU_BY_BRANCH: dict[int, str] = {
    B["Tý"]:   "Tham Lang",
    B["Sửu"]:  "Cự Môn",
    B["Dần"]:  "Lộc Tồn",
    B["Mão"]:  "Văn Khúc",
    B["Thìn"]: "Liêm Trinh",
    B["Tỵ"]:   "Vũ Khúc",
    B["Ngọ"]:  "Phá Quân",
    B["Mùi"]:  "Vũ Khúc",
    B["Thân"]: "Liêm Trinh",
    B["Dậu"]:  "Văn Khúc",
    B["Tuất"]: "Lộc Tồn",
    B["Hợi"]:  "Cự Môn",
}


def menh_chu(menh_branch_idx: int) -> str:
    """Mệnh chủ — sao chủ của Mệnh cung, an theo địa chi Mệnh cung.

    Reference: Tử Vi Đẩu Số Toàn Thư Q.2 — An Mệnh chủ quyết.
    Đại diện cho căn cốt tiên thiên của đương sự.
    """
    return _MENH_CHU_BY_BRANCH[_fix(menh_branch_idx)]


# Thân chủ: chọn theo địa chi năm sinh
# Source: TVDSTT Q.2 - An Thân chủ quyết
_THAN_CHU_BY_YEAR_BRANCH: dict[int, str] = {
    B["Tý"]:   "Hỏa Tinh",
    B["Sửu"]:  "Thiên Tướng",
    B["Dần"]:  "Thiên Lương",
    B["Mão"]:  "Thiên Đồng",
    B["Thìn"]: "Văn Xương",
    B["Tỵ"]:   "Thiên Cơ",
    B["Ngọ"]:  "Hỏa Tinh",
    B["Mùi"]:  "Thiên Tướng",
    B["Thân"]: "Thiên Lương",
    B["Dậu"]:  "Thiên Đồng",
    B["Tuất"]: "Văn Xương",
    B["Hợi"]:  "Thiên Cơ",
}


def than_chu(year_branch: str) -> str:
    """Thân chủ — sao chủ của Thân cung, an theo năm sinh (địa chi).

    Reference: Tử Vi Đẩu Số Toàn Thư Q.2 — An Thân chủ quyết.
    Đại diện cho hướng phát triển hậu thiên (đối xứng với Mệnh chủ tiên thiên).
    """
    return _THAN_CHU_BY_YEAR_BRANCH[B[year_branch]]


def dau_quan(lunar_month: int, hour_index: int) -> int:
    """Đẩu Quân — sao tháng sinh trong lá số.

    Quyết: từ cung Dần đếm THUẬN tháng sinh (Giêng=Dần, ..., Chạp=Sửu),
    rồi từ cung đó đếm NGƯỢC giờ sinh (Tý=0).

    Reference: Tử Vi Đẩu Số Toàn Thư Q.2 — An Đẩu Quân quyết.
    Dùng để: định cung tháng đi hạn trong Đại Vận và Tiểu Hạn.

    Args:
        lunar_month: 1..12 (Giêng = 1)
        hour_index: 0..11 (Tý = 0)

    Returns: branch index 0..11
    """
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"lunar_month must be 1..12, got {lunar_month}")
    if not 0 <= hour_index <= 11:
        raise ValueError(f"hour_index must be 0..11, got {hour_index}")
    # Bước 1: từ Dần đếm thuận đến tháng sinh
    pos = _fix(B["Dần"] + (lunar_month - 1))
    # Bước 2: từ pos đếm ngược giờ sinh
    pos = _fix(pos - hour_index)
    return pos


# ─── 11.5 Q2 sao bộ — bổ sung sau thâm nhuần Quyển 2 (2026-05-19) ────────────
#
# Reference: Tử Vi Đẩu Số Toàn Thư — Quyển 2 (p0080-p0141 OCR)
# Detail audit: docs/design/engine-gaps-q2-thamnhuan.md
#
# Implemented:
#   - 12 sao Thái Tuế bộ (theo địa chi năm sinh)
#   - Cặp đào hoa: Hồng Loan + Thiên Hỉ
#   - Cặp cô đơn: Cô Thần + Quả Tú
#   - Cặp Tam Thai + Bát Tọa (theo ngày sinh + Tả Hữu)
#   - Cặp Thiên Khốc + Thiên Hư (theo năm)
#   - Cặp Long Trì + Phượng Các (theo năm)

# Thứ tự 12 sao Thái Tuế theo chu trình +1 cung từ vị trí năm sinh
THAI_TUE_BELT = (
    "Thái Tuế",     # +0 (tại địa chi năm sinh)
    "Thiếu Dương",  # +1
    "Tang Môn",     # +2
    "Thiếu Âm",     # +3
    "Quan Phù",     # +4
    "Tử Phù",       # +5
    "Tuế Phá",      # +6 (đối xung Thái Tuế)
    "Long Đức",     # +7
    "Bạch Hổ",      # +8
    "Phúc Đức",     # +9
    "Điếu Khách",   # +10
    "Trực Phù",     # +11 — chuẩn TQ + anlasotuvi (engine cũ ghi sai "Bệnh Phù")
)
# LƯU Ý: "Bệnh Phù" thuộc vòng Bác Sĩ (sao_q3.BAC_SI_BELT), không phải Tuế Tiền.


def thai_tue_belt(year_branch: str) -> dict[str, int]:
    """An 12 sao Thái Tuế theo địa chi năm sinh.

    Quyết: Thái Tuế tọa tại địa chi năm sinh; 11 sao còn lại đếm THUẬN +1 cung mỗi sao.
    Reference: TVDSTT Q.2 p85 — "An Thập Nhị Cung Thái Tuế Sát Lộc Thần ca quyết".

    Returns: {sao_name: branch_index, ...} — dict 12 sao.
    """
    base = B[year_branch]
    return {name: _fix(base + offset) for offset, name in enumerate(THAI_TUE_BELT)}


def hong_loan(year_branch: str) -> int:
    """Hồng Loan — sao đào hoa, hỉ sự.

    Quyết: từ cung Mão, NGHỊCH đếm theo địa chi năm sinh.
    Reference: TVDSTT Q.2 p93 (Hồng Loan Thiên Hỷ thuộc Thủy).

    Sinh năm Tý → Mão (Tý=0 → -0 = Mão)
    Sinh năm Sửu → Dần
    Sinh năm Dần → Sửu
    ...
    """
    return _fix(B["Mão"] - B[year_branch])


def thien_hi(year_branch: str) -> int:
    """Thiên Hỉ — đối xung Hồng Loan (+6 cung)."""
    return _fix(hong_loan(year_branch) + 6)


def thien_khong(year_branch: str) -> int:
    """Thiên Không (天空) — an SAU Thái Tuế 1 cung theo chiều thuận địa chi.

    Thái Tuế tọa cung có địa chi = chi năm sinh → Thiên Không = chi năm + 1.
    Kiểm chứng lá số founder (Mậu Thìn 2026-06-13): Thái Tuế Thìn → Thiên Không Tỵ.
    Sao riêng (nằm trong 1 cung), khác Địa Không (sát tinh an theo giờ tại Hợi).
    """
    return _fix(B[year_branch] + 1)


def ham_tri(year_branch: str) -> int:
    """Hàm Trì — sao đào hoa chính, an theo tam hợp địa chi năm.

    Quyết chuẩn (TVĐS Toàn Thư + Trung Châu Bắc phái):
      - Năm Dần/Ngọ/Tuất (tam hợp Hỏa) → Hàm Trì ở MÃO
      - Năm Tỵ/Dậu/Sửu  (tam hợp Kim) → Hàm Trì ở NGỌ
      - Năm Thân/Tý/Thìn (tam hợp Thủy) → Hàm Trì ở DẬU
      - Năm Hợi/Mão/Mùi  (tam hợp Mộc) → Hàm Trì ở TÝ

    Ý nghĩa Trung Châu: cặp Hàm Trì-Đại Hao là cặp đào hoa cốt — khi đồng cung
    với Tử-Tham hoặc Liêm-Tham → "Đào hoa phạm chủ" (sách 5.3 + 3.x).
    """
    yb = B[year_branch]
    if yb in (B["Dần"], B["Ngọ"], B["Tuất"]):
        return B["Mão"]
    if yb in (B["Tỵ"], B["Dậu"], B["Sửu"]):
        return B["Ngọ"]
    if yb in (B["Thân"], B["Tý"], B["Thìn"]):
        return B["Dậu"]
    return B["Tý"]  # Hợi/Mão/Mùi


def dai_hao_dao_hoa(year_branch: str) -> int:
    """Đại Hao (cặp đào hoa) — đối xung Hàm Trì (+6 cung).

    LƯU Ý: Đây là Đại Hao trong cặp đào hoa Hàm Trì-Đại Hao (sách Trung Châu).
    Khác với "Đại Hao" trong vòng Bác Sĩ/Lộc Tồn (an theo Lộc Tồn).
    Cả 2 hệ đều có trong Trung Châu, nhưng cặp đào hoa dùng cho luận Phu Thê.
    """
    return _fix(ham_tri(year_branch) + 6)


def thien_dieu(lunar_month: int) -> int:
    """Thiên Diêu — sao đào hoa phụ, an theo tháng âm lịch.

    Quyết chuẩn: tháng 1 tại SỬU, sau đó thuận theo tháng:
      - Tháng 1 → Sửu (index 1)
      - Tháng 2 → Dần
      - Tháng 12 → Tý (index 0)

    Ý nghĩa: làm mạnh thêm bệnh hiếu sắc, trùng hôn, tính dục.
    Gặp Hồng Loan/Thiên Hỉ thì có thể giảm nhẹ.
    """
    return _fix(lunar_month)


def co_than(year_branch: str) -> int:
    """Cô Thần — sao cô đơn (đặc biệt cho nam mệnh).

    Quyết (TVDSTT Q.2): an theo tam hợp địa chi năm:
      - Năm Dần/Mão/Thìn  → Cô Thần ở Tỵ
      - Năm Tỵ/Ngọ/Mùi    → Cô Thần ở Thân
      - Năm Thân/Dậu/Tuất → Cô Thần ở Hợi
      - Năm Hợi/Tý/Sửu    → Cô Thần ở Dần
    """
    yb = B[year_branch]
    if yb in (B["Dần"], B["Mão"], B["Thìn"]):
        return B["Tỵ"]
    if yb in (B["Tỵ"], B["Ngọ"], B["Mùi"]):
        return B["Thân"]
    if yb in (B["Thân"], B["Dậu"], B["Tuất"]):
        return B["Hợi"]
    return B["Dần"]  # Hợi/Tý/Sửu


def qua_tu(year_branch: str) -> int:
    """Quả Tú — sao cô đơn (đặc biệt cho nữ mệnh). Đối ngược Cô Thần.

    Quyết:
      - Năm Dần/Mão/Thìn  → Quả Tú ở Sửu
      - Năm Tỵ/Ngọ/Mùi    → Quả Tú ở Thìn
      - Năm Thân/Dậu/Tuất → Quả Tú ở Mùi
      - Năm Hợi/Tý/Sửu    → Quả Tú ở Tuất
    """
    yb = B[year_branch]
    if yb in (B["Dần"], B["Mão"], B["Thìn"]):
        return B["Sửu"]
    if yb in (B["Tỵ"], B["Ngọ"], B["Mùi"]):
        return B["Thìn"]
    if yb in (B["Thân"], B["Dậu"], B["Tuất"]):
        return B["Mùi"]
    return B["Tuất"]  # Hợi/Tý/Sửu


def tam_thai(ta_phu_idx: int, lunar_day: int) -> int:
    """Tam Thai — sao quý nhân, an theo Tả Phụ + ngày sinh.

    Quyết: "Tam Thai tầm Tả Phụ, tương sơ nhất gia tại Tả Phụ cung,
    thuận số chí bản sinh nhật an chi"
    → Từ Tả Phụ cộng (ngày sinh - 1), thuận đếm.

    Reference: TVDSTT Q.2 p86.
    """
    return _fix(ta_phu_idx + (lunar_day - 1))


def bat_toa(huu_bat_idx: int, lunar_day: int) -> int:
    """Bát Tọa — sao quý nhân, an theo Hữu Bật + ngày sinh, NGHỊCH.

    Quyết: từ Hữu Bật cộng (ngày sinh - 1), nghịch đếm.
    Reference: TVDSTT Q.2 p86.
    """
    return _fix(huu_bat_idx - (lunar_day - 1))


def thien_khoc(year_branch: str) -> int:
    """Thiên Khốc — bi thương, mất mát.

    Quyết: "Thiên Khốc khởi Ngọ, NGHỊCH đếm theo năm sinh"
    Reference: TVDSTT Q.2 p86 — "Khốc nghịch Tỵ hề Hư thuận Vị".

    Sinh năm Tý → Ngọ (Tý=0, không lùi)
    Sinh năm Sửu → Tỵ (lùi 1)
    Sinh năm Dần → Thìn (lùi 2)
    ...
    """
    return _fix(B["Ngọ"] - B[year_branch])


def thien_hu(year_branch: str) -> int:
    """Thiên Hư — hư hao, suy yếu.

    Quyết: "Thiên Hư khởi Ngọ, THUẬN đếm theo năm sinh"
    Reference: TVDSTT Q.2 p86.
    """
    return _fix(B["Ngọ"] + B[year_branch])


def long_tri(year_branch: str) -> int:
    """Long Trì — quý, long trọng.

    Quyết "Long Trì Tý (an tại) Thìn, thuận": NĂM TÝ → Long Trì ở Thìn, đếm
    thuận theo chi năm. Tức khởi điểm = Thìn (không phải Tý).
    Verify lá số founder (Mậu Thìn 2026-06-13): năm Thìn → Thìn+4 = Thân (khớp tuvi.vn).
    """
    return _fix(B["Thìn"] + B[year_branch])


def phuong_cac(year_branch: str) -> int:
    """Phượng Các — quý, trang nhã.

    Quyết: "Phượng Các Tý Tuất nghịch" — khởi Tuất, NGHỊCH đếm đến năm sinh.
    Reference: TVDSTT Q.2 p86.
    """
    return _fix(B["Tuất"] - B[year_branch])


# ─── 11. Top-level orchestrator ───────────────────────────────────────────────


@dataclass(frozen=True)
class LaSoTuVi:
    """Complete Tử Vi chart."""

    method_id: str
    source_ref: str
    lunar_month: int
    lunar_day: int
    hour_branch: str
    hour_index: int
    year_stem: str
    year_branch: str
    gender: str

    menh_index: int
    menh_branch: str
    than_index: int
    than_branch: str
    cuc: int
    cuc_name: str
    palaces: list[dict]                # 12 palaces with name + branch
    chinh_tinh: dict[str, int]         # 14 stars
    phu_tinh: dict[str, int]           # 6 auxiliary
    sat_tinh: dict[str, int]           # 6 sát
    tu_hoa: dict[str, str]             # {Lộc: star, Quyền: star, Khoa: star, Kỵ: star}
    dai_van: list[dict]                # 12 cycles
    tieu_han_anchor: int               # start branch for current year's Tiểu Hạn

    # Phase 1 upgrade (TVDSTT Q.2): Mệnh chủ, Thân chủ, Đẩu Quân
    menh_chu: str = ""                 # sao chủ theo địa chi Mệnh cung
    than_chu: str = ""                 # sao chủ theo địa chi năm sinh
    dau_quan_index: int = -1           # branch index của Đẩu Quân
    dau_quan_branch: str = ""          # tên branch

    def to_dict(self) -> dict:
        return asdict(self)


METHOD_ID = "tu_vi_an_sao_bac_phai_v1"
SOURCE_REF = (
    "Bắc Phái 紫微斗數 — iztro (MIT) algorithm + Vietnamese mainstream "
    "(tuvisaigon.vn, xemtuong.net) + 安星訣 canonical formulas"
)


def cast_la_so(
    *,
    lunar_month: int,
    lunar_day: int,
    hour_branch: str,
    year_stem: str,
    year_branch: str,
    gender: str,
) -> dict:
    """Top-level orchestrator: build complete Tử Vi lá số."""
    if gender not in ("nam", "nữ"):
        raise ValueError(f"gender must be 'nam' or 'nữ', got {gender!r}")

    H = hour_index_from_branch(hour_branch)

    menh_idx = cung_menh_index(lunar_month, H)
    than_idx = cung_than_index(lunar_month, H)
    menh_branch = BRANCHES_TVI[menh_idx]
    than_branch = BRANCHES_TVI[than_idx]

    cuc = cuc_so(year_stem, menh_branch)
    palaces = arrange_palaces(menh_idx)

    tuvi_idx = tu_vi_position(cuc, lunar_day)
    chinh_tinh = place_14_chinh_tinh(tuvi_idx)

    phu_tinh = {
        "Tả Phù":     ta_phu(lunar_month),
        "Hữu Bật":    huu_bat(lunar_month),
        "Văn Xương":  van_xuong(H),
        "Văn Khúc":   van_khuc(H),
        "Thiên Khôi": thien_khoi_viet(year_stem)[0],
        "Thiên Việt": thien_khoi_viet(year_stem)[1],
    }

    hoa_t, linh_t = hoa_linh_tinh(year_branch, H)
    khong_t, kiep_t = dia_khong_kiep(H)
    sat_tinh = {
        "Kình Dương": kinh_duong(year_stem),
        "Đà La":      da_la(year_stem),
        "Hỏa Tinh":   hoa_t,
        "Linh Tinh":  linh_t,
        "Địa Không":  khong_t,
        "Địa Kiếp":   kiep_t,
        "Lộc Tồn":    loc_ton(year_stem),
    }

    tu_hoa = tu_hoa_assignments(year_stem)
    dai_van = dai_van_trajectory(
        menh_index=menh_idx, cuc=cuc, year_stem=year_stem, gender=gender,
    )
    tieu_han_anchor_idx = B[_TIEU_HAN_START[year_branch]]

    # Phase 1 upgrade — TVDSTT Q.2
    menh_chu_star = menh_chu(menh_idx)
    than_chu_star = than_chu(year_branch)
    # H uses 1..12 convention (Tý=1). dau_quan() expects 0..11 (Tý=0).
    dau_quan_idx = dau_quan(lunar_month, H - 1)

    la_so = LaSoTuVi(
        method_id=METHOD_ID,
        source_ref=SOURCE_REF,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        hour_branch=hour_branch,
        hour_index=H,
        year_stem=year_stem,
        year_branch=year_branch,
        gender=gender,
        menh_index=menh_idx,
        menh_branch=menh_branch,
        than_index=than_idx,
        than_branch=than_branch,
        cuc=cuc,
        cuc_name=CUC_NAMES[cuc],
        palaces=palaces,
        chinh_tinh=chinh_tinh,
        phu_tinh=phu_tinh,
        sat_tinh=sat_tinh,
        tu_hoa=tu_hoa,
        dai_van=dai_van,
        tieu_han_anchor=tieu_han_anchor_idx,
        menh_chu=menh_chu_star,
        than_chu=than_chu_star,
        dau_quan_index=dau_quan_idx,
        dau_quan_branch=BRANCHES_TVI[dau_quan_idx],
    )
    out = la_so.to_dict()

    # Q2 sao bộ — thâm nhuần 2026-05-19 (Iron Rule #6)
    # An 12 sao Thái Tuế + cặp đào hoa/cô đơn + Tam Thai Bát Tọa + Thiên Khốc Hư + Long Trì Phượng Các
    out["thai_tue_belt"] = thai_tue_belt(year_branch)
    out["sao_q2"] = {
        "Hồng Loan": hong_loan(year_branch),
        "Thiên Hỉ":  thien_hi(year_branch),
        "Cô Thần":   co_than(year_branch),
        "Quả Tú":    qua_tu(year_branch),
        "Tam Thai":  tam_thai(phu_tinh["Tả Phù"], lunar_day),
        "Bát Tọa":   bat_toa(phu_tinh["Hữu Bật"], lunar_day),
        "Thiên Khốc": thien_khoc(year_branch),
        "Thiên Hư":   thien_hu(year_branch),
        "Long Trì":  long_tri(year_branch),
        "Phượng Các": phuong_cac(year_branch),
        # Hàm Trì (đào hoa) đã có trong vòng Tướng Tinh (q3) — KHÔNG an lại ở đây
        # tránh trùng 2 lần cùng cung (bug phát hiện 2026-06-13 đối chiếu ảnh).
        # LƯU Ý: "Đại Hao" engine wire vòng Bác Sĩ (chuẩn anlasotuvi); cặp đào hoa
        # giữ tên "Đại Hao đào hoa" để phân biệt
        "Đại Hao đào hoa": dai_hao_dao_hoa(year_branch),
        "Thiên Diêu": thien_dieu(lunar_month),
    }

    # Q3 sao bộ — thâm nhuần 2026-06-08 (đối chiếu anlasotuvi.com)
    # Thiên Mã + vòng Bác Sĩ + vòng Tướng Tinh + Triệt-Tuần + sao thần sát
    from .sao_q3 import build_sao_q3
    q3 = build_sao_q3(
        year_stem=year_stem,
        year_branch=year_branch,
        gender=gender,
        lunar_month=lunar_month,
        lunar_day=lunar_day,
        loc_ton_idx=sat_tinh["Lộc Tồn"],
        van_xuong_idx=phu_tinh["Văn Xương"],
        van_khuc_idx=phu_tinh["Văn Khúc"],
        menh_idx=menh_idx,
    )
    out["sao_q2"]["Thiên Mã"] = q3["thien_ma"]
    out["bac_si_belt"] = q3["bac_si_belt"]
    out["tuong_tinh_belt"] = q3["tuong_tinh_belt"]
    out["triet"] = list(q3["triet"])      # tuple → list cho JSON
    out["tuan"] = list(q3["tuan"])
    out["sao_le"] = q3["sao_le"]
    # ── Sao thêm/sửa 2026-06-13 sau khi đối chiếu ảnh lá số founder (tuvi.vn) ──
    out["sao_le"]["Thiên Không"] = thien_khong(year_branch)  # = chi năm +1 (sau Thái Tuế)
    out["sao_le"]["Thiên La"] = B["Thìn"]   # cố định Thìn (mọi phái)
    out["sao_le"]["Địa Võng"] = B["Tuất"]   # cố định Tuất
    out["sao_le"]["Thiên Sứ"] = _fix(menh_idx + 7)   # cung Tật Ách
    # Thai Phụ + Phong Cáo — phái VN phổ thông an theo GIỜ (khởi Ngọ/Dần tại giờ
    # Tý, thuận), khớp tuvi.vn. (Engine cũ an theo Văn Khúc+ngày = phái khác → lệch.)
    out["sao_le"]["Thai Phụ"] = _fix(B["Ngọ"] + (H - 1))
    out["sao_le"]["Phong Cáo"] = _fix(B["Dần"] + (H - 1))
    # Thiên Tài (từ Mệnh) + Thiên Thọ (từ Thân), khởi Tý thuận đến chi năm
    out["sao_le"]["Thiên Tài"] = _fix(menh_idx + B[year_branch])
    out["sao_le"]["Thiên Thọ"] = _fix(than_idx + B[year_branch])

    # ── Đợt 2 (research 2026-06-13, verify khớp ảnh founder) ──
    # Đường Phù = Lộc Tồn + 5 cung thuận (engine cũ dùng bảng can = phái khác → lệch)
    out["sao_le"]["Đường Phù"] = _fix(sat_tinh["Lộc Tồn"] + 5)
    # Thiên Y = khởi Sửu (tháng 1) thuận đến tháng sinh (engine cũ khởi Mệnh → lệch)
    out["sao_le"]["Thiên Y"] = _fix(B["Sửu"] + (lunar_month - 1))
    # Thiên Quý = Văn Khúc (mùng 1) nghịch theo ngày, tiến 1 cung
    out["sao_le"]["Thiên Quý"] = _fix(phu_tinh["Văn Khúc"] - (lunar_day - 1) + 1)
    # Đầu Quân (投軍, sao lẻ — KHÁC Đẩu Quân 斗君 khởi hạn): khởi Thái Tuế (chi năm)
    # kể tháng 1 nghịch tới tháng sinh, rồi kể giờ Tý thuận tới giờ sinh
    out["sao_le"]["Đầu Quân"] = _fix(B[year_branch] - (lunar_month - 1) + (H - 1))
    # Lưu Niên Văn Tinh (sao chuẩn, theo can năm — khác Văn Xương/Khúc)
    _VAN_TINH = {"Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Thân", "Đinh": "Dậu",
                 "Mậu": "Thân", "Kỷ": "Dậu", "Canh": "Hợi", "Tân": "Tý",
                 "Nhâm": "Dần", "Quý": "Mão"}
    out["sao_le"]["Văn Tinh"] = B[_VAN_TINH[year_stem]]
    # Thiên Thương (天傷) = cung Nô Bộc (đối Thiên Sứ ở Tật Ách)
    out["sao_le"]["Thiên Thương"] = _fix(menh_idx - 7)
    # Địa Giải = khởi Mùi tháng 1 thuận (đi cặp Thiên Giải khởi Thân) → verify Tuất
    out["sao_le"]["Địa Giải"] = _fix(B["Mùi"] + (lunar_month - 1))
    # GHI CHÚ đa phái (chưa sửa, 1 data-point chưa pin được công thức tuvi.vn):
    #   Giải Thần: engine khởi Tuất nghịch tháng (→Mùi); tuvi.vn để Ngọ (khởi Dậu?)
    #   Thiên Hỉ: engine đối xung Hồng Loan (→Tỵ); tuvi.vn để Tý

    # ── GIẢI MÃ ĐỊA BÀN: độ sáng chính tinh (Miếu/Vượng/Đắc/Bình/Lạc/Hãm) ──────────
    # Bảng mieu_vuong_ham chuẩn (14 chính tinh). Gắn vào output để UI/PDF hiện badge
    # (H)/(Đ)… ngay trên tên sao (trước chỉ tính được, chưa hiển thị trên lá số).
    from . import mieu_vuong_ham as _mvh
    _DS_ABBREV = {"miếu": "M", "vượng": "V", "đắc": "Đ", "bình": "B", "lạc": "L", "hãm": "H"}
    do_sang: dict = {}
    for _name, _idx in out["chinh_tinh"].items():
        _lv = _mvh.level_at(_name, BRANCHES_TVI[_idx])
        if _lv:
            do_sang[_name] = {"level": _lv, "abbrev": _DS_ABBREV.get(_lv, _lv[:1].upper()),
                              "label": _mvh.level_label(_lv), "color": _mvh.level_color(_lv)}
    out["do_sang"] = do_sang

    # ── GIẢI MÃ ĐỊA BÀN: thiên can mỗi cung (Ngũ Hổ Độn) → "Đinh Tỵ" ──────────────
    # Khởi can tại cung Dần theo can năm (五虎遁), thuận theo địa chi. Cho "vị trí cung"
    # đầy đủ can-chi thay vì chỉ địa chi.
    _CAN10 = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    from .luu_nguyet import _NGU_HO_DON
    _dan_can = _CAN10.index(_NGU_HO_DON[year_stem])   # can tại cung Dần (địa chi index 2)
    for _p in out["palaces"]:
        _can = _CAN10[(_dan_can + ((_p["branch_index"] - 2) % 12)) % 10]
        _p["can"] = _can
        _p["can_chi"] = f"{_can} {_p['branch']}"

    return out
