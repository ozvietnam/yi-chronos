"""Tử Vi — Đẩu Quân (斗君) compute + interpret.

Theo Q2 p0088 (thâm nhuần 2026-05-20):

> _"Thái Tuế cung trung tiện khởi chính, nghịch tầm sinh nguyệt tức lưu đình."_
> _"Hựu tùng sinh nguyệt cung luân tử, thuận đáo sinh thời trấn Đẩu tinh."_

Công thức:
1. Cung Thái Tuế của lưu niên khởi tháng 1 (chính)
2. NGHỊCH đếm đến tháng sinh → cung tháng sinh
3. Từ cung tháng sinh, THUẬN đếm đến giờ sinh → đó là Đẩu Quân

Diễn giải (Q3 p0157):
> _"Đẩu Quân ngộ cát, kỳ niên nguyệt tài quan vượng;_
> _phùng hung kỵ, tài quan bất hiển đạt, hữu lao lục bôn ba."_

Đẩu Quân đi qua cung nào → quyết định cát/hung của tháng/năm đó.
Đặc biệt (Q3 p0148):
> _"Đẩu quân tại Tử Nữ cung quá độ, phùng cát, tử nữ xương thịnh,_
> _phùng hung, hình khắc, hoặc tử phá gia."_
"""
from __future__ import annotations

BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


def compute_dau_quan(
    luu_nien_branch: str,
    lunar_month: int,
    hour_branch: str,
) -> dict:
    """Đẩu Quân vị trí cho 1 lưu niên cụ thể.

    Args:
        luu_nien_branch: chi của năm lưu niên (vd "Ngọ" cho 2026 Bính Ngọ)
        lunar_month: tháng sinh âm lịch (1-12)
        hour_branch: chi giờ sinh (vd "Tý")

    Returns:
        {
          "dau_quan_branch": "Mão",
          "dau_quan_branch_index": 3,
          "trace": [
            "Khởi Ngọ (lưu niên) = tháng 1",
            "Nghịch đến tháng 4 → Mão",
            "Từ Mão, thuận đến giờ Tý → Mão",
          ],
        }
    """
    if luu_nien_branch not in BRANCHES:
        raise ValueError(f"Invalid luu_nien_branch: {luu_nien_branch}")
    if hour_branch not in BRANCHES:
        raise ValueError(f"Invalid hour_branch: {hour_branch}")
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"Invalid lunar_month: {lunar_month}")

    start_idx = BRANCHES.index(luu_nien_branch)
    # Step 1: start_idx is month 1
    # Step 2: nghịch (decrement) by (lunar_month - 1) to reach lunar_month
    month_idx = (start_idx - (lunar_month - 1)) % 12
    month_branch = BRANCHES[month_idx]
    # Step 3: thuận (increment) by hour_branch index
    hour_idx = BRANCHES.index(hour_branch)
    final_idx = (month_idx + hour_idx) % 12
    final_branch = BRANCHES[final_idx]

    trace = [
        f"Khởi {luu_nien_branch} (lưu niên Thái Tuế) = tháng 1",
        f"Nghịch đến tháng {lunar_month} → {month_branch}",
        f"Từ {month_branch}, thuận đến giờ {hour_branch} → {final_branch}",
    ]
    return {
        "dau_quan_branch": final_branch,
        "dau_quan_branch_index": final_idx,
        "month_branch": month_branch,
        "trace": trace,
    }


def compute_dau_quan_for_months(
    luu_nien_branch: str,
    lunar_month_birth: int,
    hour_branch: str,
) -> list[dict]:
    """Đẩu Quân đi qua các tháng trong lưu niên — Lưu Nguyệt mode.

    Đẩu Quân năm gốc (start) → mỗi tháng lưu nguyệt thuận 1 cung.

    Returns:
        12-element list, mỗi item:
        {month: 1, dau_quan_branch: "Mão", ...}
    """
    base = compute_dau_quan(luu_nien_branch, lunar_month_birth, hour_branch)
    base_idx = base["dau_quan_branch_index"]
    out = []
    for m in range(1, 13):
        idx = (base_idx + (m - 1)) % 12
        out.append({
            "luu_nguyet_month": m,
            "dau_quan_branch": BRANCHES[idx],
            "dau_quan_branch_index": idx,
        })
    return out


# Interpretation per palace (Q3 p0148 + p0157)
DAU_QUAN_PALACE_INTERP = {
    "Mệnh": {
        "if_cat": "Đẩu Quân quá Mệnh + cát → toàn cảnh năm/tháng tài quan vượng, hành sự thuận lợi.",
        "if_hung": "Đẩu Quân quá Mệnh + hung → bản thân nhiều áp lực, sức khỏe / tâm trạng cần giữ.",
        "source": "Q3 p0157",
    },
    "Huynh Đệ": {
        "if_cat": "Đẩu Quân quá Huynh Đệ + cát → anh em / cộng sự hỗ trợ tốt.",
        "if_hung": "Đẩu Quân quá Huynh Đệ + hung → đề phòng xung đột anh em / partner.",
        "source": "Q3 p0157",
    },
    "Phu Thê": {
        "if_cat": "Đẩu Quân quá Phu Thê + cát → tình cảm hài hòa, gặp người tốt.",
        "if_hung": "Đẩu Quân quá Phu Thê + hung → quan hệ căng thẳng, cần kiên nhẫn.",
        "source": "Q3 p0157",
    },
    "Tử Tức": {
        "if_cat": "Đẩu Quân quá Tử Tức + cát → con cái xương thịnh, hỉ sự sinh con.",
        "if_hung": "Đẩu Quân quá Tử Tức + hung → con cái hình khắc, hoặc tử phá gia. (Q3 p0148)",
        "source": "Q3 p0148",
    },
    "Tài Bạch": {
        "if_cat": "Đẩu Quân quá Tài Bạch + cát → tài lộc vượng, có ngoại tài.",
        "if_hung": "Đẩu Quân quá Tài Bạch + hung → hao tài, thận trọng đầu tư.",
        "source": "Q3 p0157",
    },
    "Tật Ách": {
        "if_cat": "Đẩu Quân quá Tật Ách + cát → sức khỏe vượng.",
        "if_hung": "Đẩu Quân quá Tật Ách + hung → đề phòng bệnh tật, kiểm tra y tế.",
        "source": "Q3 p0157",
    },
    "Thiên Di": {
        "if_cat": "Đẩu Quân quá Thiên Di + cát → đi xa có lợi, gặp quý nhân ngoại địa.",
        "if_hung": "Đẩu Quân quá Thiên Di + hung → đi xa không lợi, ở nhà tốt hơn.",
        "source": "Q3 p0157",
    },
    "Nô Bộc": {
        "if_cat": "Đẩu Quân quá Nô Bộc + cát → bạn bè / nhân viên hỗ trợ.",
        "if_hung": "Đẩu Quân quá Nô Bộc + hung → cảnh giác kẻ tiểu nhân.",
        "source": "Q3 p0157",
    },
    "Quan Lộc": {
        "if_cat": "Đẩu Quân quá Quan Lộc + cát → sự nghiệp thăng tiến, công danh hiển đạt.",
        "if_hung": "Đẩu Quân quá Quan Lộc + hung → việc làm trắc trở, áp lực công việc.",
        "source": "Q3 p0157",
    },
    "Điền Trạch": {
        "if_cat": "Đẩu Quân quá Điền Trạch + cát → mua nhà / đất / cố định tài sản thuận lợi.",
        "if_hung": "Đẩu Quân quá Điền Trạch + hung → hao tài nhà cửa, thận trọng giao dịch.",
        "source": "Q3 p0157",
    },
    "Phúc Đức": {
        "if_cat": "Đẩu Quân quá Phúc Đức + cát → tinh thần an lạc, phúc thọ vượng.",
        "if_hung": "Đẩu Quân quá Phúc Đức + hung → tâm trạng nặng, nên thiền tĩnh.",
        "source": "Q3 p0157",
    },
    "Phụ Mẫu": {
        "if_cat": "Đẩu Quân quá Phụ Mẫu + cát → cha mẹ / cấp trên hỗ trợ.",
        "if_hung": "Đẩu Quân quá Phụ Mẫu + hung → đề phòng sức khỏe cha mẹ.",
        "source": "Q3 p0157",
    },
}


def interpret_dau_quan(palace_name: str, has_cat: bool = True) -> dict:
    """Diễn giải Đẩu Quân quá cung X."""
    palace_data = DAU_QUAN_PALACE_INTERP.get(palace_name, {
        "if_cat": f"Đẩu Quân quá {palace_name} — xem cát/hung tinh tại cung này.",
        "if_hung": f"Đẩu Quân quá {palace_name} — xem cát/hung tinh tại cung này.",
        "source": "general",
    })
    return {
        "palace": palace_name,
        "interpretation": palace_data["if_cat"] if has_cat else palace_data["if_hung"],
        "source": palace_data["source"],
    }


if __name__ == "__main__":
    # Founder test
    print("=== Đẩu Quân test — founder 1988-06-05 23:30 (lunar tháng 4, giờ Tý) ===")
    print("\nLưu niên 2026 (Bính Ngọ):")
    r = compute_dau_quan("Ngọ", lunar_month=4, hour_branch="Tý")
    print(f"  {r['trace']}")
    print(f"  → Đẩu Quân tại {r['dau_quan_branch']}")

    print("\nLưu niên 2027 (Đinh Mùi):")
    r = compute_dau_quan("Mùi", lunar_month=4, hour_branch="Tý")
    print(f"  → Đẩu Quân tại {r['dau_quan_branch']}")

    print("\n12 tháng lưu nguyệt 2026 (Bính Ngọ):")
    months = compute_dau_quan_for_months("Ngọ", 4, "Tý")
    for m in months:
        print(f"  Tháng {m['luu_nguyet_month']}: Đẩu Quân tại {m['dau_quan_branch']}")
