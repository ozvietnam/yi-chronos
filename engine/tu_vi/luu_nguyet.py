"""NHỊP THÁNG (lưu nguyệt) đa-năm cho lá số Tử Vi — la bàn chú-ý.

Cho một lá số: qua nhiều năm liên tiếp, MỖI THÁNG âm lịch, Tứ Hóa của tháng rơi
vào cung CHỨC nào của đương số. Đây là "la bàn chú-ý" (cung nào được cấu trúc
rọi sáng mỗi tháng) — **KHÔNG phải bói** (Iron Rule #4/#6/#8: đọc đồng dạng,
mệnh là động từ). Output cho biết SÂN KHẤU từng tháng, KHÔNG tính kết cục.

Phép dịch (thuần hàm của lá số + lịch can-chi):
  1. Lá số gốc → map sao chính → địa chi cung nó đậu (star → branch).
  2. 12 cung chức an từ Mệnh (arrange_palaces) → branch → tên cung.
  3. Can năm theo chu kỳ 60 (mốc 1984 = Giáp Tý).
  4. Can tháng = NGŨ HỔ ĐỘN (can năm → can tháng Giêng tại Dần), tháng thuận +1.
  5. Tứ Hóa tháng = TU_HOA_TABLE[can tháng] → mỗi hóa: sao → branch → cung.
     Phụ tinh (Văn Xương/Văn Khúc/Tả Phù/Hữu Bật) không nằm trong 14 chính tinh
     natal → branch=None, palace="(phụ tinh)".

⚠️ GIỚI HẠN tháng nhuận (Đằng Sơn Tập 1 Ch.2, đọc 2026-06-23): engine hiện chỉ 12
   tháng âm/năm. Năm nhuận có 13 tháng; tháng nhuận nằm TRỌN trong 1 cung (chung với
   tháng kề), là hệ quả phép-gần-đúng → cổ pháp: tính CẢ HAI trường hợp (chung tháng
   trước / tháng sau) rồi dùng dữ kiện khác chọn. Chưa xử lý ở v1.
"""
from __future__ import annotations

from datetime import datetime

from engine import natal_universe as nu
from engine.tu_vi.an_sao import (
    BRANCHES_TVI,
    TU_HOA_TABLE,
    arrange_palaces,
)

# Thiên can theo chu kỳ 60: 1984 = Giáp Tý → 1984 ≡ Giáp.
CAN: tuple[str, ...] = (
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
)

# NGŨ HỔ ĐỘN: can năm → can tháng GIÊNG (tháng Dần).
#   Giáp/Kỷ→Bính · Ất/Canh→Mậu · Bính/Tân→Canh · Đinh/Nhâm→Nhâm · Mậu/Quý→Giáp
_NGU_HO_DON: dict[str, str] = {
    "Giáp": "Bính", "Kỷ": "Bính",
    "Ất": "Mậu", "Canh": "Mậu",
    "Bính": "Canh", "Tân": "Canh",
    "Đinh": "Nhâm", "Nhâm": "Nhâm",
    "Mậu": "Giáp", "Quý": "Giáp",
}

# Phụ tinh có thể hóa nhưng KHÔNG nằm trong 14 chính tinh natal → không có cung.
_PHU_TINH = {"Văn Xương", "Văn Khúc", "Tả Phù", "Hữu Bật"}

# Giêng = Dần = index 2 trong BRANCHES_TVI (Tý=0).
_GIENG_BRANCH_INDEX = 2

MAX_SPAN_YEARS = 30


def year_stem(year: int) -> str:
    """Thiên can của năm dương lịch (mốc 1984 = Giáp Tý).

    Kiểm: 1988 → Mậu, 2026 → Bính.
    """
    return CAN[(year - 1984) % 10]


def month_can_chi(year_stem_: str, month: int) -> tuple[str, str]:
    """(can tháng, chi tháng) cho tháng âm m (1..12) theo NGŨ HỔ ĐỘN.

    Giêng (m=1) = Dần; can Giêng theo can năm; tháng thuận +1 can, +1 chi.
    """
    if not 1 <= month <= 12:
        raise ValueError(f"month must be 1..12, got {month}")
    gieng_stem = _NGU_HO_DON[year_stem_]
    chi = BRANCHES_TVI[(_GIENG_BRANCH_INDEX + (month - 1)) % 12]
    can = CAN[(CAN.index(gieng_stem) + (month - 1)) % 10]
    return can, chi


def _build_star_to_branch(chart: dict) -> dict[str, str]:
    """Map {tên sao chính → địa chi cung nó đậu} từ dia_ban của build_natal."""
    star_to_branch: dict[str, str] = {}
    for cung in chart["dia_ban"]["cung"]:
        for star in cung["chinh_tinh"]:
            star_to_branch[star["name"]] = cung["chi"]
    return star_to_branch


def _month_hoa(
    month_stem: str,
    star_to_branch: dict[str, str],
    branch_to_palace: dict[str, str],
) -> dict[str, dict]:
    """Tứ Hóa của một tháng → {Lộc/Quyền/Khoa/Kỵ: {star, branch, palace}}."""
    out: dict[str, dict] = {}
    for hoa_name, star in TU_HOA_TABLE[month_stem].items():
        if star in _PHU_TINH and star not in star_to_branch:
            branch: str | None = None
            palace = "(phụ tinh)"
        else:
            branch = star_to_branch.get(star)
            palace = branch_to_palace.get(branch) if branch is not None else None
        out[hoa_name] = {"star": star, "branch": branch, "palace": palace}
    return out


def luu_nguyet_rhythm(
    birth_local: datetime,
    lat: float,
    lon: float,
    year_start: int,
    year_end: int,
) -> dict:
    """Nhịp tháng đa-năm: mỗi tháng âm, Tứ Hóa tháng rọi vào cung chức nào.

    Args:
        birth_local: giờ sinh địa phương — PHẢI có tzinfo (raise nếu không).
        lat, lon: toạ độ nơi sinh (độ).
        year_start, year_end: khoảng năm dương (bao gồm 2 đầu). Chênh ≤ 30 năm.

    Returns: dict gồm natal / palace_to_branch / years (mỗi năm 12 tháng).
    """
    if birth_local.tzinfo is None:
        raise ValueError("birth_local phải có tzinfo (giờ địa phương nơi sinh)")
    if year_end < year_start:
        raise ValueError(f"year_end ({year_end}) < year_start ({year_start})")
    if year_end - year_start > MAX_SPAN_YEARS:
        raise ValueError(
            f"span {year_end - year_start} năm vượt giới hạn {MAX_SPAN_YEARS}"
        )

    chart = nu.build_natal(birth_local, lat=lat, lon=lon)
    menh_chi = chart["dia_ban"]["menh_chi"]
    year_can_chi = chart["dia_ban"]["year_can_chi"]

    star_to_branch = _build_star_to_branch(chart)

    # 12 cung chức an từ Mệnh.
    menh_index = BRANCHES_TVI.index(menh_chi)
    palaces = arrange_palaces(menh_index)
    branch_to_palace = {p["branch"]: p["name"] for p in palaces}
    palace_to_branch = {p["name"]: p["branch"] for p in palaces}

    years: list[dict] = []
    for y in range(year_start, year_end + 1):
        ys = year_stem(y)
        months: list[dict] = []
        for m in range(1, 13):
            m_can, m_chi = month_can_chi(ys, m)
            months.append({
                "month": m,
                "month_can_chi": f"{m_can} {m_chi}",
                "hoa": _month_hoa(m_can, star_to_branch, branch_to_palace),
            })
        years.append({"year": y, "year_stem": ys, "months": months})

    return {
        "natal": {"menh_chi": menh_chi, "year_can_chi": year_can_chi},
        "palace_to_branch": palace_to_branch,
        "years": years,
    }
