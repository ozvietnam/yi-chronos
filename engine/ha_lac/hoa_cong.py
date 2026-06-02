"""Hóa Công + Thiên/Địa Nguyên Khí — Xuân Cang p.37-38.

Paradigm Xuân Cang:
> "Hóa Công, Thiên Nguyên khí, và Địa Nguyên khí là sự gặp gỡ giữa Năm sinh,
>  Mùa sinh và Môi trường — những điều của Trời Đất dành cho Con Người."

3 dạng ưu tiên:

1. **HÓA CÔNG** (化功) — năng lượng theo MÙA SINH
   - Sinh sau Đông Chí, trước Xuân Phân → có **Khảm** (thủy đông tàng)
   - Sinh sau Xuân Phân, trước Hạ Chí → có **Chấn** (mộc sinh phát)
   - Sinh sau Hạ Chí, trước Thu Phân → có **Ly** (hỏa hè nóng)
   - Sinh sau Thu Phân, trước Đông Chí → có **Đoài** (kim thu thâu)

2. **THIÊN NGUYÊN KHÍ** (天元氣) — khí gốc TRỜI từ CAN NĂM SINH
   - Nếu cấu trúc Hà Lạc có quẻ trùng với Can Năm sinh → có TNK
   - TNK chủ về SANG TRỌNG (hiển đạt, vinh dự, danh giá)

3. **ĐỊA NGUYÊN KHÍ** (地元氣) — khí gốc ĐẤT từ CHI NĂM SINH
   - Nếu cấu trúc Hà Lạc có quẻ trùng với Chi Năm sinh → có ĐNK
   - ĐNK chủ về GIÀU CÓ (tài lộc, ổn định)

Có cả TNK + ĐNK = **Phú Quý song toàn**.

⚠️ Iron Rule #4+6: Đây là tín hiệu cấu trúc, KHÔNG predict tĩnh.
Hóa Công + Nguyên Khí = ưu tiên — vẫn cần hành động tự thân.
"""

from __future__ import annotations


# Mùa sinh → quẻ Hóa Công (theo Tiết khí, Xuân Cang p.37)
# Convention: 4 mùa chính chia theo 4 tiết "Chí" + 4 tiết "Phân"
HOA_CONG_BY_SEASON: dict[str, dict] = {
    "dong": {
        "trigram": "Khảm",
        "tuong": "Thủy",
        "tiet_khi": "Đông Chí → Xuân Phân",
        "narrative": "Đông Chí → Xuân Phân: Trời ban Khảm (Thủy) — khí ẩn tàng nuôi dưỡng tiềm năng.",
    },
    "xuan": {
        "trigram": "Chấn",
        "tuong": "Lôi (Sấm Mộc)",
        "tiet_khi": "Xuân Phân → Hạ Chí",
        "narrative": "Xuân Phân → Hạ Chí: Trời ban Chấn (Lôi) — khí phát sinh, năng lượng bùng phát.",
    },
    "ha": {
        "trigram": "Ly",
        "tuong": "Hỏa",
        "tiet_khi": "Hạ Chí → Thu Phân",
        "narrative": "Hạ Chí → Thu Phân: Trời ban Ly (Hỏa) — khí sáng tỏ, vinh hiển bộc lộ.",
    },
    "thu": {
        "trigram": "Đoài",
        "tuong": "Trạch (Kim)",
        "tiet_khi": "Thu Phân → Đông Chí",
        "narrative": "Thu Phân → Đông Chí: Trời ban Đoài (Trạch) — khí thâu hoạch, kết quả thành đạt.",
    },
}


# Can → quẻ TNK (Thiên Nguyên Khí)
# Convention: Can ↔ trigram theo Lạc Thư (Học Năng)
CAN_TO_TRIGRAM: dict[str, str] = {
    "Giáp": "Càn",   # Mộc dương — Càn (trời)
    "Ất":   "Khôn",  # Mộc âm — Khôn (đất)
    "Bính": "Cấn",   # Hỏa dương — Cấn (núi)
    "Đinh": "Đoài",  # Hỏa âm — Đoài (đầm)
    "Mậu":  "Khảm",  # Thổ dương — Khảm (nước)
    "Kỷ":   "Ly",    # Thổ âm — Ly (lửa)
    "Canh": "Chấn",  # Kim dương — Chấn (sấm)
    "Tân":  "Tốn",   # Kim âm — Tốn (gió)
    "Nhâm": "Càn",   # Thủy dương — Càn (bổ sung)
    "Quý":  "Khôn",  # Thủy âm — Khôn (bổ sung)
}


# Chi → quẻ ĐNK (Địa Nguyên Khí)
# Convention: Chi ↔ trigram theo Hà Đồ
CHI_TO_TRIGRAM: dict[str, str] = {
    "Tý":   "Khảm",   # Thủy
    "Sửu":  "Cấn",    # Thổ
    "Dần":  "Cấn",    # Mộc-Thổ
    "Mão":  "Chấn",   # Mộc
    "Thìn": "Tốn",    # Thổ-Mộc
    "Tỵ":   "Tốn",    # Hỏa
    "Ngọ":  "Ly",     # Hỏa
    "Mùi":  "Khôn",   # Thổ-Hỏa
    "Thân": "Đoài",   # Kim
    "Dậu":  "Đoài",   # Kim
    "Tuất": "Càn",    # Kim-Thổ
    "Hợi":  "Càn",    # Thủy
}


def determine_season_from_month(month: int) -> str:
    """Convert dương lịch month → season key.

    Approximation (chính xác hơn cần Tiết khí tra cứu):
    - Đông Chí ~ 22/12, Xuân Phân ~ 21/3, Hạ Chí ~ 21/6, Thu Phân ~ 23/9
    """
    if month in (12, 1, 2):
        return "dong"  # Đông Chí → Xuân Phân
    if month in (3, 4, 5):
        return "xuan"  # Xuân Phân → Hạ Chí
    if month in (6, 7, 8):
        return "ha"    # Hạ Chí → Thu Phân
    return "thu"       # Thu Phân → Đông Chí (9, 10, 11)


def analyze_hoa_cong_nguyen_khi(
    *,
    birth_month: int,
    year_stem: str,
    year_branch: str,
    structural_trigrams: list[str],
) -> dict:
    """Phân tích Hóa Công + TNK + ĐNK.

    Args:
        birth_month: tháng sinh dương lịch (1-12)
        year_stem: Can năm sinh (vd "Mậu")
        year_branch: Chi năm sinh (vd "Thìn")
        structural_trigrams: list 4 trigrams trong cấu trúc Hà Lạc
            (Tiên Thiên upper, Tiên Thiên lower, Hậu Thiên upper, Hậu Thiên lower,
             optionally Hỗ Tiên upper/lower, Hỗ Hậu upper/lower)

    Returns: dict result.
    """
    season = determine_season_from_month(birth_month)
    hoa_cong_meta = HOA_CONG_BY_SEASON[season]
    hoa_cong_trigram = hoa_cong_meta["trigram"]
    has_hoa_cong = hoa_cong_trigram in structural_trigrams

    # TNK
    tnk_trigram = CAN_TO_TRIGRAM.get(year_stem)
    has_tnk = bool(tnk_trigram and tnk_trigram in structural_trigrams)

    # ĐNK
    dnk_trigram = CHI_TO_TRIGRAM.get(year_branch)
    has_dnk = bool(dnk_trigram and dnk_trigram in structural_trigrams)

    # Composite verdict
    has_both = has_tnk and has_dnk
    has_any = has_hoa_cong or has_tnk or has_dnk

    verdict = (
        "Phú Quý song toàn" if has_both
        else "Có ưu tiên (1 trong 3)" if has_any
        else "Cấu trúc bình thường"
    )

    return {
        "hoa_cong": {
            "season": season,
            "trigram": hoa_cong_trigram,
            "tuong": hoa_cong_meta["tuong"],
            "tiet_khi": hoa_cong_meta["tiet_khi"],
            "present": has_hoa_cong,
            "narrative": hoa_cong_meta["narrative"],
        },
        "thien_nguyen_khi": {
            "year_stem": year_stem,
            "trigram": tnk_trigram,
            "present": has_tnk,
            "narrative": (
                f"Can năm {year_stem} → quẻ {tnk_trigram}. "
                + ("**Có TNK** trong cấu trúc — chủ về SANG TRỌNG (hiển đạt, danh giá, vinh dự)."
                   if has_tnk else "Không thấy trong cấu trúc.")
            ),
        },
        "dia_nguyen_khi": {
            "year_branch": year_branch,
            "trigram": dnk_trigram,
            "present": has_dnk,
            "narrative": (
                f"Chi năm {year_branch} → quẻ {dnk_trigram}. "
                + ("**Có ĐNK** trong cấu trúc — chủ về GIÀU CÓ (tài lộc, ổn định)."
                   if has_dnk else "Không thấy trong cấu trúc.")
            ),
        },
        "verdict": verdict,
        "has_phu_quy_song_toan": has_both,
        "paradigm_guard": (
            "⚠️ Hóa Công + Nguyên Khí = TÍN HIỆU ƯU TIÊN của Trời Đất, không phải định mệnh. "
            "Vẫn cần hành động tự thân để khai mở. Iron Rule #4+6."
        ),
        "source": "Xuân Cang — Bát Tự Hà Lạc và Quỹ Đạo Đời Người, p.37-38",
    }
