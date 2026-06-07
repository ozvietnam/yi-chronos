"""Đại Vận + Lưu Niên Phu Thê — Bắc Phái Trung Châu.

Trả lời:
- Cung Phu Thê tại mỗi đại vận có chính tinh gì?
- Năm lưu niên nào có Hồng Loan/Thiên Hỉ bay đến Phu Thê (= năm cát cho hôn nhân)?
- Năm lưu niên nào cung Phu Thê có Hóa Kỵ trùng điệp (= cảnh báo)?

Source paradigm: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ, section 5.3 + 3.x)
"""
from __future__ import annotations
from typing import Any

from .an_sao import hong_loan as _hong_loan, thien_hi as _thien_hi

BRANCHES = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
_B2I = {b: i for i, b in enumerate(BRANCHES)}


def _fix(x: int) -> int:
    return x % 12


def cung_phu_the_dai_van(la_so: dict) -> list[dict[str, Any]]:
    """Tính cung Phu Thê tại từng đại vận.

    Nguyên tắc:
    - Mỗi đại vận có cung Mệnh (đã có trong la_so['dai_van'])
    - Cung Phu Thê = cung Mệnh đại vận - 2 (đếm ngược, vì thứ tự 12 cung
      sau Mệnh: Phụ Mẫu → Phúc Đức → Điền Trạch → Quan Lộc → Nô Bộc → Thiên Di
      → Tật Ách → Tài Bạch → Tử Tức → Phu Thê → Huynh Đệ → Mệnh)
      Tức là Mệnh +10 = Phu Thê → cung Phu Thê = Mệnh - 2 (mod 12)

    Returns: list 8 dict, mỗi dict có:
        - start_age, end_age
        - menh_branch (đại vận)
        - phu_the_branch
        - phu_the_chinh_tinh (chính tinh nguyên cục tại cung đó)
        - canh_bao (nếu có Hóa Kỵ trùng điệp)
    """
    chinh_tinh = la_so.get("chinh_tinh", {})
    tu_hoa = la_so.get("tu_hoa", {})
    dai_van_list = la_so.get("dai_van", [])

    # Build lookup: branch_idx → list chính tinh
    by_branch: dict[int, list[str]] = {i: [] for i in range(12)}
    for star, idx in chinh_tinh.items():
        by_branch[idx].append(star)

    result = []
    for dv in dai_van_list:
        # Đại vận có thể có 'branch' hoặc 'menh_branch'
        menh_dv_branch = dv.get("branch") or dv.get("menh_branch") or ""
        if menh_dv_branch not in _B2I:
            continue
        menh_dv_idx = _B2I[menh_dv_branch]
        phu_the_dv_idx = _fix(menh_dv_idx - 2)
        phu_the_dv_branch = BRANCHES[phu_the_dv_idx]
        phu_the_stars = by_branch.get(phu_the_dv_idx, [])

        # Cảnh báo: nếu chính tinh Phu Thê đại vận = sao đang Hóa Kỵ → BÁO ĐỘNG
        canh_bao = []
        hoa_ki_star = tu_hoa.get("Kỵ") or tu_hoa.get("hoa_ki") or tu_hoa.get("ki")
        if hoa_ki_star and hoa_ki_star in phu_the_stars:
            canh_bao.append(f"{hoa_ki_star} Hóa Kỵ tại cung Phu Thê đại vận — cảnh báo")
        # Đặc biệt: Vũ Khúc Hóa Kỵ / Thái Dương Hóa Kỵ / Liêm Trinh Hóa Kỵ
        if hoa_ki_star in {"Vũ Khúc", "Thái Dương", "Liêm Trinh"} and hoa_ki_star in phu_the_stars:
            canh_bao.append(
                f"⚠ {hoa_ki_star} Hóa Kỵ tại Phu Thê đại vận — sách Trung Châu: CỰC KỲ BẤT LỢI"
            )

        result.append({
            "start_age": dv.get("start_age"),
            "end_age": dv.get("end_age"),
            "menh_branch": menh_dv_branch,
            "phu_the_branch": phu_the_dv_branch,
            "phu_the_chinh_tinh": phu_the_stars,
            "canh_bao": canh_bao,
        })

    return result


def luu_nien_phu_the_markers(
    la_so: dict,
    year_range: tuple[int, int] = (2024, 2034),
) -> list[dict[str, Any]]:
    """Tìm các năm lưu niên có Hồng Loan / Thiên Hỉ bay đến CUNG MỆNH hoặc CUNG PHU THÊ.

    Quy luật Trung Châu (3.1.x):
    > 'Có thể lấy cung Mệnh hoặc cung Phu Thê của lưu niên có Hồng Loan, Thiên Hỉ
    > bay đến làm ứng kỳ kết hôn / mang thai — NHƯNG cần tinh hệ chính diệu cát lợi
    > ổn định mới đúng.'

    Args:
        la_so: dict từ TuViAnalyzer.la_so
        year_range: (start_year, end_year) inclusive

    Returns: list dict:
        {
          "year": 2026,
          "year_branch": "Ngọ",
          "lưu_hong_loan_branch": "...",
          "lưu_thien_hi_branch": "...",
          "trigger_phu_the_menh": "hồng loan" | "thiên hỉ" | "cả 2",
          "trigger_type": "menh" | "phu_the" | "menh+phu_the",
          "note": "..."
        }
    """
    # Cung Mệnh + Cung Phu Thê NGUYÊN CỤC
    menh_idx = la_so.get("menh_index")
    if menh_idx is None:
        return []
    phu_the_idx = _fix(menh_idx - 2)

    # 60 năm Giáp Tý — map year → year_branch (Tý=1924, 1936, ...)
    # year_branch_index = (year - 4) % 12
    # 1924 = Giáp Tý → (1924-4)%12 = 0 = Tý ✓
    def year_to_branch(y: int) -> str:
        return BRANCHES[(y - 4) % 12]

    out = []
    for y in range(year_range[0], year_range[1] + 1):
        yb = year_to_branch(y)
        hl_idx = _hong_loan(yb)
        th_idx = _thien_hi(yb)

        trigger_hl_menh = hl_idx == menh_idx
        trigger_hl_phu = hl_idx == phu_the_idx
        trigger_th_menh = th_idx == menh_idx
        trigger_th_phu = th_idx == phu_the_idx

        # Chỉ ghi nhận năm có trigger
        if not (trigger_hl_menh or trigger_hl_phu or trigger_th_menh or trigger_th_phu):
            continue

        triggers = []
        if trigger_hl_menh: triggers.append("Hồng Loan bay đến Mệnh")
        if trigger_hl_phu:  triggers.append("Hồng Loan bay đến Phu Thê")
        if trigger_th_menh: triggers.append("Thiên Hỉ bay đến Mệnh")
        if trigger_th_phu:  triggers.append("Thiên Hỉ bay đến Phu Thê")

        out.append({
            "year": y,
            "year_branch": yb,
            "luu_hong_loan_branch": BRANCHES[hl_idx],
            "luu_thien_hi_branch": BRANCHES[th_idx],
            "triggers": triggers,
            "note": (
                f"Năm {y} ({yb}): {', '.join(triggers)}. "
                f"Theo Trung Châu, có thể là ứng kỳ HÔN NHÂN/THAI nếu các sao chính cát lợi."
            ),
        })

    return out
