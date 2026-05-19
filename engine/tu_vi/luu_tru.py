"""Lưu Trú Sao — transit stars for a target year, layered on top of natal chart.

For any target_year, compute:
- Lưu Tứ Hóa: the target year's stem produces a new Tứ Hóa overlay
- Lưu Lộc Tồn / Kình Dương / Đà La: from target year's stem
- Lưu Thiên Khôi / Thiên Việt: from target year's stem
- Đại Hạn position (which Đại Vận cycle this year falls in, by age)
- Tiểu Hạn position (year-by-year cung)

This gives a complete "year sky" overlay for any year of life, used for
yearly fortune readings.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .an_sao import (
    BRANCHES_TVI,
    _fix,
    da_la,
    dai_van_direction,
    dia_khong_kiep,
    hoa_linh_tinh,
    kinh_duong,
    loc_ton,
    thien_khoi_viet,
    tieu_han_for_age,
    tu_hoa_assignments,
    van_khuc,
    van_xuong,
)


@dataclass(frozen=True)
class LuuTruYear:
    """Transit data for one specific year."""

    target_year: int                   # e.g. 2026
    target_stem: str                   # Thiên Can of the year
    target_branch: str                 # Địa Chi of the year
    age_at_year: int                   # natal age in target year
    dai_han_cycle: dict                # current Đại Vận cycle data
    dai_han_intra_cung: int            # intra-cung position (0..9) within current 10-year span
    tieu_han_branch: str               # current year's Tiểu Hạn cung
    luu_tu_hoa: dict                   # {Lộc/Quyền/Khoa/Kỵ → star} for target year
    luu_loc_ton: str                   # Lộc Tồn position for target year
    luu_kinh_duong: str
    luu_da_la: str
    luu_thien_khoi: str
    luu_thien_viet: str

    def to_dict(self) -> dict:
        return asdict(self)


# Map (year - 1984) to 60-jiazi cycle to get year's stem+branch.
_STEMS = ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý")
_BRANCHES = BRANCHES_TVI   # same order


def year_to_ganzhi(year: int) -> tuple[str, str]:
    """Convert Gregorian year → (Thiên Can, Địa Chi).

    Anchor: 1984 = Giáp Tý. Year N → stem = (N-4) mod 10, branch = (N-4) mod 12.
    """
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    return _STEMS[stem_idx], _BRANCHES[branch_idx]


def luu_tru_for_year(
    *,
    la_so: dict,
    target_year: int,
    birth_year: int,
) -> dict:
    """Compute full transit data for `target_year` against the natal lá số.

    Args:
        la_so: output of cast_la_so()
        target_year: e.g. 2026 (Gregorian)
        birth_year: natal Gregorian year (needed to compute age)
    """
    age = target_year - birth_year + 1   # 1-based lunar age convention

    # Target year's ganzhi.
    target_stem, target_branch = year_to_ganzhi(target_year)

    # Find which Đại Vận cycle contains this age.
    dai_van = la_so["dai_van"]
    current_dv = None
    for c in dai_van:
        if c["start_age"] <= age <= c["end_age"]:
            current_dv = c
            break
    if current_dv is None:
        # Age beyond 12 cycles → use last cycle (or first if age < starting_age).
        if age < dai_van[0]["start_age"]:
            current_dv = dai_van[0]
        else:
            current_dv = dai_van[-1]
    intra_cung = age - current_dv["start_age"]   # 0..9

    # Tiểu Hạn for current age (uses natal year branch).
    tieu_han_idx = tieu_han_for_age(la_so["year_branch"], la_so["gender"], age)
    tieu_han_branch = _BRANCHES[tieu_han_idx]

    # Transit Tứ Hóa from target year's stem.
    luu_tu_hoa = tu_hoa_assignments(target_stem)

    # Transit sát tinh + phụ tinh from target stem.
    luu_loc_ton = _BRANCHES[loc_ton(target_stem)]
    luu_kinh = _BRANCHES[kinh_duong(target_stem)]
    luu_da = _BRANCHES[da_la(target_stem)]
    khoi_idx, viet_idx = thien_khoi_viet(target_stem)
    luu_khoi = _BRANCHES[khoi_idx]
    luu_viet = _BRANCHES[viet_idx]

    return LuuTruYear(
        target_year=target_year,
        target_stem=target_stem,
        target_branch=target_branch,
        age_at_year=age,
        dai_han_cycle=current_dv,
        dai_han_intra_cung=intra_cung,
        tieu_han_branch=tieu_han_branch,
        luu_tu_hoa=luu_tu_hoa,
        luu_loc_ton=luu_loc_ton,
        luu_kinh_duong=luu_kinh,
        luu_da_la=luu_da,
        luu_thien_khoi=luu_khoi,
        luu_thien_viet=luu_viet,
    ).to_dict()


def dai_han_intra_cung_per_year(
    *,
    la_so: dict,
    birth_year: int,
    cycle_index: int,
) -> list[dict]:
    """For a given Đại Vận cycle, compute per-year intra-cung breakdown.

    Each Đại Vận = 10 years. Within those 10 years, each year's "Tiểu Hạn"
    moves through 10 sub-positions.

    Returns list of 10 dicts: {age, year, tieu_han_branch}
    """
    dai_van = la_so["dai_van"]
    if cycle_index < 1 or cycle_index > len(dai_van):
        raise ValueError(f"cycle_index must be 1..{len(dai_van)}, got {cycle_index}")
    cycle = dai_van[cycle_index - 1]

    out = []
    for age_offset in range(10):
        age = cycle["start_age"] + age_offset
        year = birth_year + age - 1
        tieu_han_idx = tieu_han_for_age(la_so["year_branch"], la_so["gender"], age)
        out.append({
            "age": age,
            "year": year,
            "tieu_han_branch": _BRANCHES[tieu_han_idx],
            "tieu_han_branch_index": tieu_han_idx,
        })
    return out
