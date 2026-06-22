"""Chiếu Đởm Kinh — An Sao 18 Phi Tinh.

Engine PARALLEL với engine.tu_vi.an_sao chính thống (14 chính tinh).

Theo Q4 p0272-p0273 (Phase A Batch 4 thâm nhuần 2026-05-20):

**Khởi Tử Vi lệ** (p0272 r017):
> "Phàm khởi Tử Vi, Hư, Quý, Ấn, Thọ, Không, Loan, Khố, Quán, Văn, Phúc, Lộc,
>  tịnh tòng Mùi thượng khởi Tý, thuận sổ chí bản nhân sinh niên, an Tử nghịch
>  sổ nhất cung, an nhất tinh."

**Khởi Thiên Trượng lệ** (p0272 r019):
> "Phàm khởi Thiên Trượng, Dị, Mao, Nhận, tịnh tòng Tý thượng khởi chính nguyệt,
>  nghịch sổ chí bản nhân sinh nguyệt, an Trượng. Nghịch bố Dị, Mao, Nhận."

**Khởi Thiên Hình lệ** (p0273 r002):
> "Phàm khởi Thiên Hình, tòng Dậu thượng khởi chánh nguyệt, thuận sổ chí bổn
>  nhân sanh nguyệt an Thiên Hình."

**Khởi Thiên Khốc lệ** (p0273 r004):
> "Phàm khởi Thiên Khốc, dữ bổn nhân sanh niên tương hợp, an Khốc, Tý dữ Sửu
>  hợp, như Tý niên sanh nhân Sửu thượng an Khốc."

**An Mệnh lệ** (p0273 r006):
> "Phàm tòng Trượng tinh thuận sổ bổn nhân sanh thì... phùng (chi giờ sinh)
>  tiện thị Mệnh cung."

**Khởi Đại Hạn / Tiểu Vận lệ** (p0273 r010-r012):
> Dương nam Âm nữ thuận, Âm nam Dương nữ nghịch.

Iron Rule: KHÔNG conflict với main an_sao.py — engine namespace riêng.
Convention âm-dương ĐẢO của Chiếu Đởm Kinh (Q4 p0273): Giáp Bính Mậu Canh Nhâm = ÂM.
"""
from __future__ import annotations

from typing import Optional

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

# Chiếu Đởm Kinh ÂM-DƯƠNG convention (Q4 p0273 r015) — ĐẢO so với chính thống
STEM_POLARITY_CDK = {
    "Giáp": "âm", "Bính": "âm", "Mậu": "âm", "Canh": "âm", "Nhâm": "âm",
    "Ất": "dương", "Đinh": "dương", "Kỷ": "dương", "Tân": "dương", "Quý": "dương",
}

# Lục hợp (Tý-Sửu hợp, Dần-Hợi hợp, ...) cho khởi Thiên Khốc
LUC_HOP = {
    "Tý": "Sửu", "Sửu": "Tý",
    "Dần": "Hợi", "Hợi": "Dần",
    "Mão": "Tuất", "Tuất": "Mão",
    "Thìn": "Dậu", "Dậu": "Thìn",
    "Tỵ": "Thân", "Thân": "Tỵ",
    "Ngọ": "Mùi", "Mùi": "Ngọ",
}

# Sao Group A — Khởi từ Mùi, theo năm sinh (Tử Vi group)
GROUP_A_STARS = ["Tử", "Hư", "Quý", "Ấn", "Thọ", "Không", "Loan", "Khố", "Quán", "Văn", "Phúc", "Lộc"]

# Sao Group B — Khởi từ Tý, theo tháng sinh (Thiên Trượng group)
GROUP_B_STARS = ["Trượng", "Dị", "Mao", "Nhận"]


def _add_branches(start_branch: str, n: int, direction: str = "thuận") -> str:
    """Add n steps from start_branch, direction = 'thuận' (forward) or 'nghịch' (backward)."""
    start_idx = BRANCHES.index(start_branch)
    if direction == "thuận":
        new_idx = (start_idx + n) % 12
    else:
        new_idx = (start_idx - n) % 12
    return BRANCHES[new_idx]


def an_group_a_stars(year_branch: str) -> dict:
    """An 12 sao Group A (Tử Vi, Hư, Quý, Ấn, Thọ, Không, Loan, Khố, Quán, Văn, Phúc, Lộc).

    Per Q4 p0272 r017: "Tịnh tòng Mùi thượng khởi Tý, thuận sổ chí bản nhân sinh niên,
    an Tử nghịch sổ nhất cung, an nhất tinh."

    Args:
        year_branch: chi năm sinh ("Tý", "Sửu", ...)

    Returns:
        dict {star_name: branch_name} cho 12 sao Group A
    """
    # Step 1: Từ cung Mùi khởi Tý, thuận đếm đến năm sinh
    year_idx = BRANCHES.index(year_branch)
    # Mùi index = 7. Mùi = Tý → so Tử Vi at Mùi+year_idx
    tu_vi_idx = (BRANCHES.index("Mùi") + year_idx) % 12

    # Step 2: An Tử Vi tại đó, nghịch bố 11 sao còn lại (mỗi cung 1 sao)
    result = {}
    for i, star in enumerate(GROUP_A_STARS):
        idx = (tu_vi_idx - i) % 12
        result[star] = BRANCHES[idx]
    return result


def an_group_b_stars(lunar_month: int) -> dict:
    """An 4 sao Group B (Trượng, Dị, Mao, Nhận).

    Per Q4 p0272 r019: "Tịnh tòng Tý thượng khởi chính nguyệt, nghịch sổ chí bản nhân
    sinh nguyệt, an Trượng. Nghịch bố Dị, Mao, Nhận."

    Args:
        lunar_month: tháng sinh âm lịch (1-12)

    Returns:
        dict {star_name: branch_name} cho 4 sao Group B
    """
    # Từ Tý khởi tháng 1, nghịch đếm đến tháng sinh
    truong_idx = (BRANCHES.index("Tý") - (lunar_month - 1)) % 12
    result = {}
    for i, star in enumerate(GROUP_B_STARS):
        idx = (truong_idx - i) % 12
        result[star] = BRANCHES[idx]
    return result


def an_thien_hinh(lunar_month: int) -> str:
    """An Thiên Hình per Q4 p0273 r002.

    "Tòng Dậu thượng khởi chánh nguyệt, thuận sổ chí bổn nhân sanh nguyệt an Thiên Hình."
    """
    return _add_branches("Dậu", lunar_month - 1, "thuận")


def an_thien_khoc(year_branch: str) -> str:
    """An Thiên Khốc per Q4 p0273 r004 — lục hợp năm sinh."""
    return LUC_HOP.get(year_branch, year_branch)


def an_thien_dieu(lunar_month: int) -> str:
    """An Thiên Diêu — GỐC Q4 p0272 r002 "Thiên Diêu (tại Sửu thuận hành)" + r014
    "Hình [Dậu] Diêu [Sửu] giai thuận hành, sổ chí sinh nguyệt". KHÔNG phải heuristic —
    từ Sửu, thuận, đếm tới tháng sinh (xác nhận sách gốc 2026-06-23)."""
    return _add_branches("Sửu", lunar_month - 1, "thuận")


def an_menh_chieu_dom(truong_branch: str, hour_branch: str) -> str:
    """An Mệnh cung CDK per Q4 p0273 r006.

    "Phàm từ Trượng tinh thuận sổ bản nhân sinh thì... gặp giờ sinh tiện thị Mệnh cung."

    NHƯNG dùng cách khác: "tắc tòng Tý thượng khởi Thân, thuận sổ chí Mùi, phùng Mão
    tiện thị Mệnh cung" cho ví dụ giờ Mão.

    Args:
        truong_branch: vị trí Thiên Trượng đã an
        hour_branch: chi giờ sinh
    """
    # Heuristic: từ Trượng thuận đếm theo hour offset
    hour_idx = BRANCHES.index(hour_branch)
    return _add_branches(truong_branch, hour_idx, "thuận")


def an_dai_han_cdk(menh_branch: str, year_stem: str, gender: str) -> list[dict]:
    """An Đại Hạn CDK — 10 năm/cung.

    Per Q4 p0273 r010: "Dương nam Âm nữ tòng Mệnh cung thuận sổ, thập niên hành nhất
    cung; Âm nam Dương nữ tòng Thân cung nghịch sổ".

    SỬA 2026-06-23 theo SÁCH GỐC (Q4 p0273 r014-r015 đặt NGAY SAU luật hạn r010):
    CDK dùng convention ĐẢO (Giáp Bính Mậu Canh Nhâm = ÂM) để định "Dương nam/Âm nữ"
    cho CHIỀU hạn. Trước đây engine dùng chuẩn (không-đảo) = NGƯỢC gốc → nay theo
    STEM_POLARITY_CDK. (Vd Mậu = âm → "âm nam" → nghịch, không còn thuận.)

    LƯU Ý còn tồn (chưa xử lý, cần cung Thân): gốc r010 nói "âm nam dương nữ tòng THÂN
    cung nghịch sổ" — khởi từ cung Thân, không phải Mệnh. Engine hiện luôn khởi từ
    menh_branch (đơn giản hóa). Chiều đã đúng gốc; điểm khởi Mệnh/Thân cần bổ sung sau.
    """
    polarity = STEM_POLARITY_CDK.get(year_stem, "âm")
    is_thuan = (polarity == "dương" and gender == "nam") or (polarity == "âm" and gender == "nữ")

    cycles = []
    for i in range(8):  # 8 cycles × 10 năm = 80 năm
        # FIX 2026-06-23: trước đây idx_offset=-i KÈM direction="nghịch" → triệt tiêu
        # (luôn thuận). Dùng i dương, để direction lo dấu mới đúng chiều nghịch.
        branch = _add_branches(menh_branch, i, "thuận" if is_thuan else "nghịch")
        cycles.append({
            "cycle_index": i + 1,
            "branch": branch,
            "start_age": i * 10 + 1,
            "end_age": (i + 1) * 10,
        })
    return cycles


def cast_chieu_dom_kinh(
    year_stem: str,
    year_branch: str,
    lunar_month: int,
    hour_branch: str,
    gender: str = "nam",
) -> dict:
    """Cast lá số Chiếu Đởm Kinh complete.

    Returns:
        {
          "stars": {17 stars → branch},
          "menh_branch": str,
          "dai_han_cycles": [...],
          "source_refs": [...]
        }
    """
    # Step 1: Group A (12 sao theo năm sinh)
    group_a = an_group_a_stars(year_branch)

    # Step 2: Group B (4 sao theo tháng sinh)
    group_b = an_group_b_stars(lunar_month)

    # Step 3: Thiên Hình theo tháng (Dậu start)
    hinh = an_thien_hinh(lunar_month)

    # Step 4: Thiên Khốc theo năm (lục hợp)
    khoc = an_thien_khoc(year_branch)

    # Step 5: Thiên Diêu theo tháng (Sửu start)
    dieu = an_thien_dieu(lunar_month)

    # Step 6: An Mệnh từ Trượng + giờ sinh
    menh = an_menh_chieu_dom(group_b["Trượng"], hour_branch)

    # Step 7: An Đại Hạn
    dai_han = an_dai_han_cdk(menh, year_stem, gender)

    # Combine all 17 stars (18 if include Tử Vi as Group A "Tử")
    all_stars = {**group_a, **group_b, "Hình": hinh, "Khốc": khoc, "Diêu": dieu}

    return {
        "stars": all_stars,
        "menh_branch": menh,
        "dai_han_cycles": dai_han,
        "year_stem": year_stem,
        "year_branch": year_branch,
        "lunar_month": lunar_month,
        "hour_branch": hour_branch,
        "gender": gender,
        "source_refs": [
            "Q4 p0272 r017 — Khởi Tử Vi lệ",
            "Q4 p0272 r019 — Khởi Thiên Trượng lệ",
            "Q4 p0273 r002 — Khởi Thiên Hình lệ",
            "Q4 p0273 r004 — Khởi Thiên Khốc lệ",
            "Q4 p0273 r006 — An Mệnh lệ",
            "Q4 p0273 r010 — Khởi Đại Hạn lệ",
        ],
        "paradigm_note": "Chiếu Đởm Kinh là PARALLEL paradigm với Tử Vi Đẩu Số chính thống (14 chính tinh). 18 Phi Tinh KHÁC. Iron Rule: KHÔNG merge với main an_sao engine.",
    }


if __name__ == "__main__":
    # Test với founder: 1988 Mậu Thìn, lunar tháng 4, giờ Tý
    result = cast_chieu_dom_kinh(
        year_stem="Mậu",
        year_branch="Thìn",
        lunar_month=4,
        hour_branch="Tý",
        gender="nam",
    )
    print("=== Chiếu Đởm Kinh chart — founder 1988-06-05 23:30 (lunar 4, Tý) ===")
    print(f"\nMệnh CDK: {result['menh_branch']}")
    print(f"\n18 sao positions:")
    for star, branch in result["stars"].items():
        print(f"  {star:10s} tại {branch}")
    print(f"\nĐại Hạn cycles ({len(result['dai_han_cycles'])}):")
    for c in result["dai_han_cycles"][:4]:
        print(f"  Cycle {c['cycle_index']}: {c['branch']} (tuổi {c['start_age']}-{c['end_age']})")
