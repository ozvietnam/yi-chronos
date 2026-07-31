"""Nhân Cung paradigm — Trần Đoàn Toàn Thư (Vũ Tài Lục p63-64).

> "Nhân cung là nơi đất đắc địa cho một số sao. Vào nhân cung khả năng tốt
> sẽ bị giảm đến 80% hoặc nó sẽ gây thành tính kỳ quặc mà hỏng việc;
> nhân cung nghĩa bóng của thất vị thất nghiệp."

8 trường hợp được Toàn Thư liệt kê (atoms tdts.S4.Q25-Q33).
6 chính tinh khác (Thiên Đồng, Thiên Phủ, Thái Âm, Thái Dương, Liêm Trinh,
Cự Môn) thất lạc trong sách gốc — KHÔNG có dữ liệu.
"""
from __future__ import annotations

# Mapping: star_canonical → list of cung trở thành Nhân Cung
# Cung dùng canonical lowercase chi: ty, suu, dan, mao, thin, ty, ngo, mui, than, dau, tuat, hoi
# (Tý = ty; Tỵ = tÿ — em phân biệt qua chu kỳ encoding nếu cần)
NHAN_CUNG: dict[str, list[str]] = {
    "tu_vi":        ["ty", "thin", "hoi"],       # Tử Vi ở Tí, Thìn, Hợi
    "tham_lang":    ["dan", "than"],             # Tham Lang ở Dần, Thân
    "thien_tuong":  ["thin", "tuat"],            # Thiên Tướng ở Thìn, Tuất
    "that_sat":     ["thin", "hoi"],             # Thất Sát ở Thìn, Hợi
    "thien_luong":  ["ti"],                       # Thiên Lương ở Tỵ
    "thien_co":     ["ti"],                       # Thiên Cơ ở Tỵ
    "pha_quan":     ["ti", "than"],              # Phá Quân ở Tỵ, Thân
    "vu_khuc":      ["than"],                     # Vũ Khúc ở Thân
}
# Quy ước canonical chi TOÀN HỆ THỐNG (khớp la_so_input_builder.CHI_VI_TO_CANON,
# thien_luong.CHI_VI, to_hop_cung.CHI_RING): "ty" = Tý (子), "ti" = Tỵ (巳) —
# 2 chi KHÁC NHAU. Fix 2026-07-17: 3 dòng trên trước đây dùng "ty" cho vị trí
# Tỵ (đụng độ với "ty"=Tý của Tử Vi) — engine sẽ báo Nhân Cung SAI cung.

CITATION = "Trần Đoàn Toàn Thư p63-64 (atoms tdts.S4.Q25-Q33)"


def is_nhan_cung(sao: str, cung: str) -> tuple[bool, str]:
    """Check if (sao, cung) là Nhân Cung paradigm Trần Đoàn.

    Args:
        sao: canonical star name (vd "tu_vi", "tham_lang")
        cung: canonical chi (vd "ty", "thin")

    Returns:
        (is_nhan_cung, citation_or_reason)
    """
    sao_norm = sao.lower().strip().replace(" ", "_")
    cung_norm = cung.lower().strip()
    cungs = NHAN_CUNG.get(sao_norm, [])
    if cung_norm in cungs:
        return True, (
            f"⚠ NHÂN CUNG: {sao} ở {cung} là 'đất đắc địa nghịch lý' — "
            f"khả năng tốt giảm 80% hoặc thành tính kỳ quặc. "
            f"Nguồn: {CITATION}"
        )
    return False, "không phải Nhân Cung"
