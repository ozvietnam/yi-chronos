"""Chiêm cung Phu Thê v3 — Phase 1: Cross-bind Phúc Đức + Mệnh.

Mở rộng từ v2 (9 quy luật) thêm 4 quy luật cross-bind chính (Q10-Q13):

Q10: Văn Khúc Hóa Kỵ ở Phúc Đức/Phu Thê → rắc rối tình cảm
Q11: Văn Xương-Văn Khúc giáp Phu Thê → quấy rối
Q12: Xương-Khúc CHIA RA (Mệnh+Phu Thê hoặc Phúc Đức+Phu Thê) → vợ chồng HỢP Ý
Q13: Địa Không ở Phúc Đức → đả kích tinh thần cross Phu Thê

Source: Trung Châu Tử Vi Đẩu Số 2 — Vương Đình Chỉ, section 5.3 + 3.x
Doc: docs/design/PLAN-CUNG-PHU-THE-FULL-CROSS.md
"""
from __future__ import annotations
from typing import Any

from .chiem_phu_the_v2 import chiem_phu_the_v2, BRANCHES
from .chiem_phu_the import _find_palace, _stars_at_branch_idx


def _fix(x: int) -> int:
    return x % 12


def _stars_at_named_palace(la_so: dict, palace_name: str) -> dict[str, list[str]]:
    """Helper: lấy stars tại cung có tên cụ thể."""
    pal = _find_palace(la_so, palace_name)
    if not pal:
        return {"chinh_tinh": [], "phu_tinh": [], "sat_tinh": [], "sao_q2": []}
    return _stars_at_branch_idx(la_so, pal["branch_index"])


def _palace_index(la_so: dict, palace_name: str) -> int | None:
    pal = _find_palace(la_so, palace_name)
    return pal["branch_index"] if pal else None


def _giap_indices(branch_idx: int) -> tuple[int, int]:
    """2 cung giáp cung này (trước + sau)."""
    return (_fix(branch_idx - 1), _fix(branch_idx + 1))


def _detect_hoa_at_star_in_palace(
    la_so: dict, target_star: str, palace_name: str, hoa_key: str
) -> bool:
    """Star có Hóa <key> nào đó NẰM ở cung palace_name không?"""
    tu_hoa = la_so.get("tu_hoa", {})
    star = tu_hoa.get(hoa_key) or tu_hoa.get(f"Hóa {hoa_key}")
    if star != target_star:
        return False
    # Find target star position
    pal_idx = _palace_index(la_so, palace_name)
    if pal_idx is None:
        return False
    # Star có thể là chính tinh hoặc phụ tinh
    for source in ("chinh_tinh", "phu_tinh", "sat_tinh", "sao_q2"):
        d = la_so.get(source, {})
        if isinstance(d, dict) and d.get(target_star) == pal_idx:
            return True
    return False


def _Q10_van_khuc_hoa_ki_at_phuc_or_phuthe(la_so: dict) -> dict[str, Any]:
    """Q10: Văn Khúc Hóa Kỵ ở Phúc Đức HOẶC Phu Thê → rắc rối tình cảm.

    Sách: "nữ mệnh có Văn Khúc Hóa Kỵ ở Mệnh, Phu Thê hoặc Phúc Đức..."
    """
    at_phuc = _detect_hoa_at_star_in_palace(la_so, "Văn Khúc", "Phúc Đức", "Kỵ")
    at_phu_the = _detect_hoa_at_star_in_palace(la_so, "Văn Khúc", "Phu Thê", "Kỵ")
    at_menh = _detect_hoa_at_star_in_palace(la_so, "Văn Khúc", "Mệnh", "Kỵ")
    detected = at_phuc or at_phu_the or at_menh

    where = []
    if at_phuc: where.append("Phúc Đức")
    if at_phu_the: where.append("Phu Thê")
    if at_menh: where.append("Mệnh")

    return {
        "detected": detected,
        "where": where,
        "paradigm": (
            f"⚠ Văn Khúc Hóa Kỵ tại {', '.join(where)} → "
            f"sách Trung Châu: rắc rối tình cảm, đặc biệt nữ mệnh"
            if detected
            else "Không có Văn Khúc Hóa Kỵ ở các cung Mệnh/Phu Thê/Phúc Đức"
        ),
    }


def _Q11_xuong_khuc_giap_phu_the(la_so: dict) -> dict[str, Any]:
    """Q11: Văn Xương + Văn Khúc giáp cung Phu Thê → quấy rối tình cảm.

    Sách 3.x: "Văn Xương, Văn Khúc giáp cung Phu Thê, thì dễ bị quấy rối về tình cảm."
    """
    phu_the_idx = _palace_index(la_so, "Phu Thê")
    if phu_the_idx is None:
        return {"detected": False}
    giap1, giap2 = _giap_indices(phu_the_idx)

    phu_tinh = la_so.get("phu_tinh", {})
    xuong = phu_tinh.get("Văn Xương")
    khuc = phu_tinh.get("Văn Khúc")

    detected = (
        xuong is not None and khuc is not None
        and {xuong, khuc} == {giap1, giap2}
    )
    return {
        "detected": detected,
        "phu_the_branch": BRANCHES[phu_the_idx],
        "giap_branches": [BRANCHES[giap1], BRANCHES[giap2]],
        "paradigm": (
            "⚠ Văn Xương + Văn Khúc GIÁP cung Phu Thê — sách: dễ bị quấy rối tình cảm"
            if detected
            else "Xương-Khúc không giáp Phu Thê"
        ),
    }


def _Q12_xuong_khuc_split_menh_phu_or_phuc_phu(la_so: dict) -> dict[str, Any]:
    """Q12: Xương-Khúc CHIA RA ở (Mệnh+Phu Thê) HOẶC (Phúc Đức+Phu Thê) → vợ chồng HỢP Ý.

    Sách 3.x: "Văn Xương, Văn Khúc chia ra ở cung Mệnh và Phu Thê, hoặc Phúc Đức
    và Phu Thê, tinh hệ chính diệu cát, chủ về vợ chồng hợp ý nhau."
    """
    phu_tinh = la_so.get("phu_tinh", {})
    xuong = phu_tinh.get("Văn Xương")
    khuc = phu_tinh.get("Văn Khúc")
    if xuong is None or khuc is None:
        return {"detected": False}

    menh_idx = _palace_index(la_so, "Mệnh")
    phu_the_idx = _palace_index(la_so, "Phu Thê")
    phuc_duc_idx = _palace_index(la_so, "Phúc Đức")

    # Detect 1 sao ở Mệnh + 1 sao ở Phu Thê (chia ra)
    split_menh_phu = (
        (xuong == menh_idx and khuc == phu_the_idx)
        or (khuc == menh_idx and xuong == phu_the_idx)
    )
    split_phuc_phu = (
        (xuong == phuc_duc_idx and khuc == phu_the_idx)
        or (khuc == phuc_duc_idx and xuong == phu_the_idx)
    )

    pattern = None
    if split_menh_phu:
        pattern = "Mệnh + Phu Thê"
    elif split_phuc_phu:
        pattern = "Phúc Đức + Phu Thê"

    return {
        "detected": bool(pattern),
        "pattern": pattern,
        "paradigm": (
            f"✅ Xương-Khúc CHIA RA ở {pattern} → "
            f"sách: 'vợ chồng hợp ý nhau' (cát — nếu tinh hệ chính diệu cát)"
            if pattern
            else "Xương-Khúc không chia ra theo cách cát"
        ),
    }


def _Q13_dia_khong_at_phuc_or_phu_or_tu(la_so: dict) -> dict[str, Any]:
    """Q13: Địa Không ở Phúc Đức HOẶC Phu Thê HOẶC Tử Tức → đả kích tinh thần.

    Sách 3.x: "Địa Không không nên ở Phúc Đức, Phu Thê, Tử Nữ."
    """
    sat = la_so.get("sat_tinh", {})
    if not isinstance(sat, dict):
        return {"detected": False}
    dia_khong_idx = sat.get("Địa Không")
    if dia_khong_idx is None:
        return {"detected": False}

    phuc_idx = _palace_index(la_so, "Phúc Đức")
    phu_idx = _palace_index(la_so, "Phu Thê")
    tu_idx = _palace_index(la_so, "Tử Tức") or _palace_index(la_so, "Tử Nữ")

    where = []
    if dia_khong_idx == phuc_idx: where.append("Phúc Đức")
    if dia_khong_idx == phu_idx: where.append("Phu Thê")
    if dia_khong_idx == tu_idx: where.append("Tử Tức")

    detected = bool(where)
    return {
        "detected": detected,
        "where": where,
        "paradigm": (
            f"⚠ Địa Không tại {', '.join(where)} → "
            f"sách: đả kích tinh thần, ảnh hưởng cross Phu Thê"
            if detected
            else "Địa Không không nằm ở các cung tinh thần (Phúc/Phu/Tử)"
        ),
    }


def chiem_phu_the_v3(la_so: dict) -> dict[str, Any]:
    """Engine v3 — v2 (9 quy luật) + Q10-Q13 cross-bind Phúc Đức + Mệnh.

    Output structure: backward-compat với v2, thêm field `quy_luat_v3`.
    """
    result = chiem_phu_the_v2(la_so)

    # Cross-bind Phúc Đức + Mệnh
    cross = {
        "10_van_khuc_hoa_ki_cross": _Q10_van_khuc_hoa_ki_at_phuc_or_phuthe(la_so),
        "11_xuong_khuc_giap_phu_the": _Q11_xuong_khuc_giap_phu_the(la_so),
        "12_xuong_khuc_chia_re_cat": _Q12_xuong_khuc_split_menh_phu_or_phuc_phu(la_so),
        "13_dia_khong_cross_tam_phuc": _Q13_dia_khong_at_phuc_or_phu_or_tu(la_so),
    }

    # Aggregate cảnh báo cát/hung cross-bind
    canh_bao = []
    if cross["10_van_khuc_hoa_ki_cross"].get("detected"):
        canh_bao.append(cross["10_van_khuc_hoa_ki_cross"]["paradigm"])
    if cross["11_xuong_khuc_giap_phu_the"].get("detected"):
        canh_bao.append(cross["11_xuong_khuc_giap_phu_the"]["paradigm"])
    if cross["13_dia_khong_cross_tam_phuc"].get("detected"):
        canh_bao.append(cross["13_dia_khong_cross_tam_phuc"]["paradigm"])

    diem_cat = []
    if cross["12_xuong_khuc_chia_re_cat"].get("detected"):
        diem_cat.append(cross["12_xuong_khuc_chia_re_cat"]["paradigm"])

    # Lookup chính tinh Phúc Đức để cung cấp paradigm
    phuc_duc_stars = _stars_at_named_palace(la_so, "Phúc Đức")

    result["version"] = "v3"
    result["quy_luat_v3"] = cross
    result["cross_bind_phuc_duc"] = {
        "phuc_duc_chinh_tinh": phuc_duc_stars["chinh_tinh"],
        "phuc_duc_branch_index": _palace_index(la_so, "Phúc Đức"),
        "canh_bao_cross": canh_bao,
        "diem_cat_cross": diem_cat,
    }

    return result
