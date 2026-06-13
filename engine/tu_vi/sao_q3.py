"""Sao Q3 — Thần sát + vòng Bác Sĩ + vòng Tướng Tinh + Triệt-Tuần + Thiên Mã.

Bổ sung 2026-06-08 cho ngang anlasotuvi.com:

1. Thiên Mã                — tam hợp chi năm
2. Vòng Bác Sĩ 12          — theo Lộc Tồn + chiều Dương Nam/Âm Nữ thuận, Âm Nam/Dương Nữ nghịch
3. Vòng Tướng Tinh 12      — tam hợp chi năm
4. Triệt Lộ Không Vong     — can năm
5. Tuần Trung Không Vong   — lục thập hoa giáp (an theo cặp can-chi năm)
6. Quốc Ấn, Đường Phù      — can năm
7. Phá Toái                — chi năm
8. Lưu Hà                  — can năm
9. Thiên Trù               — can năm
10. Thiên Y, Thiên Hình    — tháng sinh
11. Thiên Đức, Nguyệt Đức  — chi năm
12. Thiên Giải, Giải Thần  — tháng sinh
13. Ân Quang, Thai Phụ     — Văn Xương + ngày
14. Phong Cáo              — Văn Khúc + ngày
15. Thiên Quan, Thiên Phúc — can năm (sao quý nhân)

Reference: TVDSTT Q.2 + Tử Vi Đẩu Số Toàn Thư + Trung Châu Q.2
"""
from __future__ import annotations
from typing import Any

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
            "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
B = {b: i for i, b in enumerate(BRANCHES)}

STEMS = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]


def _fix(x: int) -> int:
    return x % 12


# ─── 1. Thiên Mã ──────────────────────────────────────────────
_THIEN_MA_BY_GROUP = {
    # Thân-Tý-Thìn (tam hợp Thủy) → Dần
    "Thân-Tý-Thìn": "Dần",
    # Dần-Ngọ-Tuất (tam hợp Hỏa) → Thân
    "Dần-Ngọ-Tuất": "Thân",
    # Tỵ-Dậu-Sửu (tam hợp Kim) → Hợi
    "Tỵ-Dậu-Sửu": "Hợi",
    # Hợi-Mão-Mùi (tam hợp Mộc) → Tỵ
    "Hợi-Mão-Mùi": "Tỵ",
}


def thien_ma(year_branch: str) -> int:
    """Thiên Mã — sao động, di chuyển. An theo tam hợp chi năm."""
    yb = B[year_branch]
    if yb in (B["Thân"], B["Tý"], B["Thìn"]):
        return B["Dần"]
    if yb in (B["Dần"], B["Ngọ"], B["Tuất"]):
        return B["Thân"]
    if yb in (B["Tỵ"], B["Dậu"], B["Sửu"]):
        return B["Hợi"]
    return B["Tỵ"]  # Hợi/Mão/Mùi


# ─── 2. Vòng Bác Sĩ 12 ────────────────────────────────────────
BAC_SI_BELT = (
    "Bác Sĩ",       # +0 tại Lộc Tồn
    "Lực Sĩ",       # +1
    "Thanh Long",   # +2
    "Tiểu Hao",     # +3
    "Tướng Quân",   # +4
    "Tấu Thư",      # +5
    "Phi Liêm",     # +6
    "Hỷ Thần",      # +7
    "Bệnh Phù",     # +8 — KHÁC Bệnh Phù vòng Tuế Tiền
    "Đại Hao",      # +9 — KHÁC Đại Hao đào hoa (Hàm Trì + 6)
    "Phục Binh",    # +10
    "Quan Phù",     # +11 — KHÁC Quan Phù vòng Tuế Tiền
)


def bac_si_belt(loc_ton_idx: int, year_stem: str, gender: str) -> dict[str, int]:
    """An vòng Bác Sĩ 12 sao.

    Quy tắc:
    - Khởi tại Lộc Tồn (Bác Sĩ +0)
    - Chiều: Dương Nam / Âm Nữ → THUẬN
             Âm Nam / Dương Nữ → NGHỊCH

    Can Dương = Giáp, Bính, Mậu, Canh, Nhâm (index 0,2,4,6,8)
    Can Âm = Ất, Đinh, Kỷ, Tân, Quý (index 1,3,5,7,9)
    """
    stem_idx = STEMS.index(year_stem)
    is_yang_stem = stem_idx % 2 == 0
    is_male = gender == "nam"

    # Dương Nam + Âm Nữ → THUẬN; ngược lại → NGHỊCH
    is_forward = (is_yang_stem and is_male) or (not is_yang_stem and not is_male)

    out = {}
    for offset, name in enumerate(BAC_SI_BELT):
        if is_forward:
            out[name] = _fix(loc_ton_idx + offset)
        else:
            out[name] = _fix(loc_ton_idx - offset)
    return out


# ─── 3. Vòng Tướng Tinh 12 ────────────────────────────────────
TUONG_TINH_BELT = (
    "Tướng Tinh",   # +0
    "Phan An",      # +1
    "Tuế Dịch",     # +2
    "Tức Thần",     # +3
    "Hoa Cái",      # +4 — sao quý (cũng hoa hư danh)
    "Kiếp Sát",     # +5 — sao hung
    "Tai Sát",      # +6
    "Thiên Sát",    # +7
    "Chỉ Bối",      # +8
    "Hàm Trì",      # +9 — đào hoa (engine đã có hàm riêng)
    "Nguyệt Sát",   # +10
    "Vong Thần",    # +11
)


def tuong_tinh_anchor(year_branch: str) -> int:
    """Khởi cung Tướng Tinh theo tam hợp chi năm."""
    yb = B[year_branch]
    if yb in (B["Thân"], B["Tý"], B["Thìn"]):
        return B["Tý"]
    if yb in (B["Dần"], B["Ngọ"], B["Tuất"]):
        return B["Ngọ"]
    if yb in (B["Tỵ"], B["Dậu"], B["Sửu"]):
        return B["Dậu"]
    return B["Mão"]  # Hợi/Mão/Mùi


def tuong_tinh_belt(year_branch: str) -> dict[str, int]:
    """An vòng Tướng Tinh 12 sao — thuận theo tam hợp chi năm."""
    base = tuong_tinh_anchor(year_branch)
    return {name: _fix(base + offset) for offset, name in enumerate(TUONG_TINH_BELT)}


# ─── 4. Triệt Lộ Không Vong ────────────────────────────────────
_TRIET_BY_STEM = {
    "Giáp": ("Thân", "Dậu"),
    "Kỷ":   ("Thân", "Dậu"),
    "Ất":   ("Ngọ", "Mùi"),
    "Canh": ("Ngọ", "Mùi"),
    "Bính": ("Thìn", "Tỵ"),
    "Tân":  ("Thìn", "Tỵ"),
    "Đinh": ("Dần", "Mão"),
    "Nhâm": ("Dần", "Mão"),
    "Mậu":  ("Tý", "Sửu"),
    "Quý":  ("Tý", "Sửu"),
}


def triet(year_stem: str) -> tuple[int, int]:
    """Triệt Lộ Không Vong — 2 chi cấm theo can năm."""
    b1, b2 = _TRIET_BY_STEM[year_stem]
    return (B[b1], B[b2])


# ─── 5. Tuần Trung Không Vong (Lục thập hoa giáp) ─────────────
# 6 tuần × 10 năm:
#   Giáp Tý  tuần: Tý-Sửu-Dần-Mão-Thìn-Tỵ-Ngọ-Mùi-Thân-Dậu → Tuần KV = Tuất-Hợi
#   Giáp Tuất tuần: Tuất-Hợi-Tý-Sửu-Dần-Mão-Thìn-Tỵ-Ngọ-Mùi → Tuần KV = Thân-Dậu
#   Giáp Thân tuần: Thân-Dậu-Tuất-Hợi-Tý-Sửu-Dần-Mão-Thìn-Tỵ → Tuần KV = Ngọ-Mùi
#   Giáp Ngọ  tuần: Ngọ-Mùi-Thân-Dậu-Tuất-Hợi-Tý-Sửu-Dần-Mão → Tuần KV = Thìn-Tỵ
#   Giáp Thìn tuần: Thìn-Tỵ-Ngọ-Mùi-Thân-Dậu-Tuất-Hợi-Tý-Sửu → Tuần KV = Dần-Mão
#   Giáp Dần  tuần: Dần-Mão-Thìn-Tỵ-Ngọ-Mùi-Thân-Dậu-Tuất-Hợi → Tuần KV = Tý-Sửu

_TUAN_KV_BY_GIAP = {
    "Giáp Tý":   ("Tuất", "Hợi"),
    "Giáp Tuất": ("Thân", "Dậu"),
    "Giáp Thân": ("Ngọ", "Mùi"),
    "Giáp Ngọ":  ("Thìn", "Tỵ"),
    "Giáp Thìn": ("Dần", "Mão"),
    "Giáp Dần":  ("Tý", "Sửu"),
}


def _stem_chi_index(stem_idx: int, branch_idx: int) -> int:
    """Tính index trong 60 hoa giáp.
    Giáp Tý = 0, Ất Sửu = 1, ..., Quý Hợi = 59
    """
    # Pattern: stem_idx và branch_idx must align — stem cycle 10, branch cycle 12
    # Tìm n sao cho n % 10 == stem_idx và n % 12 == branch_idx
    for n in range(60):
        if n % 10 == stem_idx and n % 12 == branch_idx:
            return n
    raise ValueError(f"Invalid stem-chi combo: stem={stem_idx}, branch={branch_idx}")


def tuan(year_stem: str, year_branch: str) -> tuple[int, int]:
    """Tuần Trung Không Vong — 2 chi cuối của giáp tuần chứa năm sinh."""
    stem_idx = STEMS.index(year_stem)
    branch_idx = B[year_branch]
    n = _stem_chi_index(stem_idx, branch_idx)
    # Tuần index = floor(n / 10) → 0..5
    tuan_idx = n // 10
    # Mỗi tuần khởi từ Giáp Tý, Giáp Tuất, Giáp Thân, Giáp Ngọ, Giáp Thìn, Giáp Dần
    giap_branch_start = [B["Tý"], B["Tuất"], B["Thân"], B["Ngọ"], B["Thìn"], B["Dần"]][tuan_idx]
    giap_name = "Giáp " + BRANCHES[giap_branch_start]
    b1, b2 = _TUAN_KV_BY_GIAP[giap_name]
    return (B[b1], B[b2])


# ─── 6. Quốc Ấn + Đường Phù (theo can năm) ────────────────────
_QUOC_AN_BY_STEM = {
    "Giáp": "Tuất", "Ất": "Hợi",
    "Bính": "Sửu", "Mậu": "Sửu",
    "Đinh": "Dần", "Kỷ": "Dần",
    "Canh": "Thìn", "Tân": "Tỵ",
    "Nhâm": "Mùi", "Quý": "Thân",
}


def quoc_an(year_stem: str) -> int:
    """Quốc Ấn — sao quý nhân, công danh."""
    return B[_QUOC_AN_BY_STEM[year_stem]]


_DUONG_PHU_BY_STEM = {
    "Giáp": "Sửu", "Ất": "Dần",
    "Bính": "Thìn", "Mậu": "Thìn",
    "Đinh": "Tỵ", "Kỷ": "Tỵ",
    "Canh": "Mùi", "Tân": "Thân",
    "Nhâm": "Tuất", "Quý": "Hợi",
}


def duong_phu(year_stem: str) -> int:
    """Đường Phù — sao quý nhân (đối Quốc Ấn về luận giải)."""
    return B[_DUONG_PHU_BY_STEM[year_stem]]


# ─── 7. Phá Toái (chi năm) ────────────────────────────────────
def pha_toai(year_branch: str) -> int:
    """Phá Toái — sao tiêu hao, đổ vỡ. An theo tứ chính/tứ sinh/tứ mộ.

    Tý Ngọ Mão Dậu (tứ chính) → Tỵ
    Dần Thân Tỵ Hợi (tứ sinh) → Dậu
    Thìn Tuất Sửu Mùi (tứ mộ) → Sửu
    Pin 2 lá số tuvi.vn (2026-06-13): năm Mão→Tỵ, năm Thìn→Sửu. (Cũ dùng tam hợp → sai.)
    """
    yb = B[year_branch]
    if yb in (B["Tý"], B["Ngọ"], B["Mão"], B["Dậu"]):
        return B["Tỵ"]
    if yb in (B["Dần"], B["Thân"], B["Tỵ"], B["Hợi"]):
        return B["Dậu"]
    return B["Sửu"]  # Thìn Tuất Sửu Mùi (tứ mộ)


# ─── 8. Lưu Hà (can năm) ──────────────────────────────────────
_LUU_HA_BY_STEM = {
    "Giáp": "Dậu", "Ất": "Tuất",
    "Bính": "Mùi", "Đinh": "Thân",
    "Mậu": "Tỵ", "Kỷ": "Ngọ",
    "Canh": "Thìn", "Tân": "Mão",
    "Nhâm": "Hợi", "Quý": "Tý",
}


def luu_ha(year_stem: str) -> int:
    """Lưu Hà — sao tai ách (đặc biệt hung khi gặp Hỏa-Linh)."""
    return B[_LUU_HA_BY_STEM[year_stem]]


# ─── 9. Thiên Trù (can năm) ───────────────────────────────────
_THIEN_TRU_BY_STEM = {
    # Pin từ ảnh tuvi.vn: Mậu→Ngọ, Kỷ→Thân (2026-06-13).
    "Giáp": "Tỵ", "Đinh": "Tỵ",
    "Ất": "Ngọ", "Mậu": "Ngọ",
    "Kỷ": "Thân",   # verify lá số 2 (Kỷ Mão, tuvi.vn) → Thân
    "Bính": "Tý",   # verify lá số 3 (Bính Dần, anlasotuvi.com) → Tý
    "Canh": "Thân", "Tân": "Dần",
    "Nhâm": "Dậu", "Quý": "Hợi",
}


def thien_tru(year_stem: str) -> int | None:
    """Thiên Trù — sao ăn lộc trời. (Bính cần verify công thức)"""
    val = _THIEN_TRU_BY_STEM.get(year_stem)
    if val and val in B:
        return B[val]
    return None


# ─── 10. Thiên Y + Thiên Hình (tháng sinh) ────────────────────
def thien_y(menh_idx: int, lunar_month: int) -> int:
    """Thiên Y — sao y dược, tài năng chữa trị.
    Khởi từ Mệnh, thuận đếm theo tháng sinh.
    """
    return _fix(menh_idx + (lunar_month - 1))


def thien_hinh(lunar_month: int) -> int:
    """Thiên Hình — sao hình khắc, tai ách.
    Khởi Dậu tháng 1, thuận đếm.
    """
    return _fix(B["Dậu"] + (lunar_month - 1))


# ─── 11. Thiên Đức + Nguyệt Đức (chi năm — phái phổ thông VN) ──
def thien_duc(year_branch: str) -> int:
    """Thiên Đức — sao cát giải hung.
    An tại chi đối xung +0 (cùng năm sinh).
    Một số phái: khởi Dậu, thuận đếm theo năm.
    """
    return _fix(B["Dậu"] + B[year_branch])


def nguyet_duc(year_branch: str) -> int:
    """Nguyệt Đức — sao cát giải hung phụ.
    Một phái: khởi Tỵ, thuận đếm theo năm.
    """
    return _fix(B["Tỵ"] + B[year_branch])


# ─── 12. Thiên Giải + Giải Thần (tháng sinh) ──────────────────
def thien_giai(lunar_month: int) -> int:
    """Thiên Giải — giải tai ách.
    Khởi Thân tháng 1, thuận đếm.
    """
    return _fix(B["Thân"] + (lunar_month - 1))


def giai_than(lunar_month: int) -> int:
    """Giải Thần — giải hung (gặp Tang Môn, Bạch Hổ tốt).
    Khởi DẬU tháng 1, NGHỊCH đếm tới tháng sinh.
    Pin bằng 2 lá số tuvi.vn (2026-06-13): tháng4→Ngọ, tháng3→Mùi. (Cũ khởi Tuất → lệch 1 cung.)
    """
    return _fix(B["Dậu"] - (lunar_month - 1))


# ─── 13. Ân Quang + Thai Phụ (Văn Xương + ngày) ───────────────
def an_quang(van_xuong_idx: int, lunar_day: int) -> int:
    """Ân Quang — quý nhân.
    Từ Văn Xương, thuận đếm (ngày - 1) cung, rồi lùi 1.
    """
    return _fix(van_xuong_idx + (lunar_day - 1) - 1)


def thai_phu(van_khuc_idx: int, lunar_day: int) -> int:
    """Thai Phụ — quý nhân, học vấn.
    Từ Văn Khúc, thuận đếm (ngày - 1) cung, rồi tới 2.
    """
    return _fix(van_khuc_idx + (lunar_day - 1) + 2)


# ─── 14. Phong Cáo (Văn Khúc + ngày) ──────────────────────────
def phong_cao(van_khuc_idx: int, lunar_day: int) -> int:
    """Phong Cáo — quý nhân, danh tiếng.
    Từ Văn Khúc, thuận đếm (ngày - 1) cung, rồi +4 (1 số phái).
    """
    return _fix(van_khuc_idx + (lunar_day - 1) + 4)


# ─── 15. Thiên Quan + Thiên Phúc (can năm, quý nhân) ──────────
_THIEN_QUAN_BY_STEM = {
    "Giáp": "Mùi", "Ất": "Thìn",
    "Bính": "Tỵ", "Đinh": "Dần",
    "Mậu": "Mão", "Kỷ": "Dậu",
    "Canh": "Hợi", "Tân": "Dậu",
    "Nhâm": "Tuất", "Quý": "Ngọ",
}


def thien_quan(year_stem: str) -> int:
    """Thiên Quan — quý nhân, công danh."""
    return B[_THIEN_QUAN_BY_STEM[year_stem]]


_THIEN_PHUC_BY_STEM = {
    "Giáp": "Dậu", "Ất": "Thân",
    "Bính": "Tý", "Đinh": "Hợi",
    "Mậu": "Mão", "Kỷ": "Dần",
    "Canh": "Ngọ", "Tân": "Tỵ",
    "Nhâm": "Mão", "Quý": "Dần",
}


def thien_phuc(year_stem: str) -> int:
    """Thiên Phúc — phúc đức, lộc."""
    return B[_THIEN_PHUC_BY_STEM[year_stem]]


# ─── Top-level wiring ──────────────────────────────────────────
def build_sao_q3(
    *,
    year_stem: str,
    year_branch: str,
    gender: str,
    lunar_month: int,
    lunar_day: int,
    loc_ton_idx: int,
    van_xuong_idx: int,
    van_khuc_idx: int,
    menh_idx: int,
) -> dict[str, Any]:
    """Build complete sao Q3 dict.

    Returns:
        {
            "thien_ma": idx,
            "bac_si_belt": {sao: idx, ...},
            "tuong_tinh_belt": {sao: idx, ...},
            "triet": (idx1, idx2),
            "tuan": (idx1, idx2),
            "sao_le": {
                "Quốc Ấn": idx, "Đường Phù": idx,
                "Phá Toái": idx, "Lưu Hà": idx,
                "Thiên Y": idx, "Thiên Hình": idx,
                "Thiên Đức": idx, "Nguyệt Đức": idx,
                "Thiên Giải": idx, "Giải Thần": idx,
                "Ân Quang": idx, "Thai Phụ": idx,
                "Phong Cáo": idx,
                "Thiên Quan": idx, "Thiên Phúc": idx,
                ...
            },
        }
    """
    sao_le: dict[str, int] = {
        "Quốc Ấn":    quoc_an(year_stem),
        "Đường Phù":  duong_phu(year_stem),
        "Phá Toái":   pha_toai(year_branch),
        "Lưu Hà":     luu_ha(year_stem),
        "Thiên Y":    thien_y(menh_idx, lunar_month),
        "Thiên Hình": thien_hinh(lunar_month),
        "Thiên Đức":  thien_duc(year_branch),
        "Nguyệt Đức": nguyet_duc(year_branch),
        "Thiên Giải": thien_giai(lunar_month),
        "Giải Thần":  giai_than(lunar_month),
        "Ân Quang":   an_quang(van_xuong_idx, lunar_day),
        "Thai Phụ":   thai_phu(van_khuc_idx, lunar_day),
        "Phong Cáo":  phong_cao(van_khuc_idx, lunar_day),
        "Thiên Quan": thien_quan(year_stem),
        "Thiên Phúc": thien_phuc(year_stem),
    }
    tr = thien_tru(year_stem)
    if tr is not None:
        sao_le["Thiên Trù"] = tr

    return {
        "thien_ma": thien_ma(year_branch),
        "bac_si_belt": bac_si_belt(loc_ton_idx, year_stem, gender),
        "tuong_tinh_belt": tuong_tinh_belt(year_branch),
        "triet": triet(year_stem),
        "tuan": tuan(year_stem, year_branch),
        "sao_le": sao_le,
    }
