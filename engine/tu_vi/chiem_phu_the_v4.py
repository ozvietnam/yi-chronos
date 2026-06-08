"""Chiêm cung Phu Thê v4 — Phase 2-5: Full cross-bind paradigm Bắc phái.

Mở rộng từ v3 (13 quy luật) thêm 14 quy luật cross-bind:

PHASE 2 — Quan Lộc × Phu Thê (đối cung):
  Q14: Vũ Khúc Hóa Kỵ ở cả Sự Nghiệp + Phu Thê → "tiền + tình cùng phá"
  Q15: Tham Lang Hóa Lộc ở Sự Nghiệp + Phu Thê có Tử-Tham → "vợ chồng cùng sáng lập"

PHASE 3 — Thiên Di × Phu Thê (tam phương +8):
  Q16: Thiên Mã hội Tử Vi ở Phu Thê = "loan dư" — vợ chồng quý hiển
  Q17: Lộc Tồn + Hóa Lộc ở Phu Thê = "Lộc hợp uyên ương" — chung giàu có
  Q18: Thiên Mã + Đà La + sát + Phu Thê (nữ) → cảnh báo chọn lầm

PHASE 4 — Mệnh + Tài Bạch + Tử Tức × Phu Thê:
  Q19: Cự Môn tọa Mệnh + Phu Thê → "tiếng thị phi" ảnh hưởng quan hệ
  Q20: Vũ Khúc + Hỏa-Linh tọa Mệnh + Phu Thê không tốt → "giao tiền cho vợ" rule
  Q21: Tham Lang + đào hoa ở Tử Tức + Phu Thê → cảnh báo
  Q22: Vũ Khúc Hóa Kỵ ở Tài Bạch + Phu Thê → tiền + tình cùng phá

PHASE 5 — Lục thân (Huynh/Phụ/Tật/Điền):
  Q23: Liêm Trinh Hóa Kỵ ở Huynh Đệ + Phá Quân ở Phu Thê → bất hòa anh em
  Q24: Cự Môn ở Phụ Mẫu + Phu Thê → bất hòa thân gia
  Q25: Vũ Khúc Hóa Kỵ ở Điền Trạch + Phu Thê → tổ ấm + hôn nhân cùng phá
  Q26: Sát tinh nặng ở Tật Ách (Bạch Hổ + Phi Xà + Đà La...) → cảnh báo sức khỏe bạn đời
  Q27: Meta — đếm tổng số cảnh báo + điểm cát toàn bộ 27 quy luật

Source: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ) — section 5.x + 3.x
Doc: docs/design/PLAN-CUNG-PHU-THE-FULL-CROSS.md
"""
from __future__ import annotations
from typing import Any

from .chiem_phu_the_v3 import (
    chiem_phu_the_v3,
    _stars_at_named_palace,
    _palace_index,
    _fix,
)
from .chiem_phu_the_v2 import BRANCHES
from .chiem_phu_the import _stars_at_branch_idx


# ─── Helpers ───────────────────────────────────────────────────────────────

def _has_star_at_palace(la_so: dict, star_name: str, palace_name: str) -> bool:
    """Star có tại cung palace_name không (tìm trong mọi nhóm sao)?"""
    pal_idx = _palace_index(la_so, palace_name)
    if pal_idx is None:
        return False
    for source in ("chinh_tinh", "phu_tinh", "sat_tinh", "sao_q2"):
        d = la_so.get(source, {})
        if isinstance(d, dict) and d.get(star_name) == pal_idx:
            return True
    return False


def _has_hoa_at_palace(la_so: dict, star: str, palace_name: str, hoa_key: str) -> bool:
    """Star có Hóa <hoa_key> NẰM ở cung palace_name không?"""
    tu_hoa = la_so.get("tu_hoa", {})
    hoa_star = tu_hoa.get(hoa_key) or tu_hoa.get(f"Hóa {hoa_key}")
    if hoa_star != star:
        return False
    return _has_star_at_palace(la_so, star, palace_name)


def _palace_has_chinh_tinh(la_so: dict, palace_name: str, target_stars: set[str]) -> set[str]:
    """Cung có chính tinh nào trong target_stars (intersection)?"""
    pal_stars = _stars_at_named_palace(la_so, palace_name)
    return set(pal_stars["chinh_tinh"]) & target_stars


# ─── PHASE 2 ───────────────────────────────────────────────────────────────

def _Q14_vu_khuc_hoa_ki_sn_phuthe(la_so: dict) -> dict[str, Any]:
    """Q14: Vũ Khúc Hóa Kỵ ở cả Sự Nghiệp + Phu Thê → tiền + tình cùng phá.

    Sách: "Vũ Khúc Hóa Kỵ rơi vào Mệnh/Điền Trạch/Phu Thê/Tài Bạch/Sự Nghiệp đều
    không hay. Nếu cung Phu Thê cũng không được tốt, thế thì khá phức tạp rồi."
    """
    at_sn = _has_hoa_at_palace(la_so, "Vũ Khúc", "Sự Nghiệp", "Kỵ") or \
            _has_hoa_at_palace(la_so, "Vũ Khúc", "Quan Lộc", "Kỵ")
    at_phu = _has_hoa_at_palace(la_so, "Vũ Khúc", "Phu Thê", "Kỵ")

    detected = at_sn and at_phu
    return {
        "detected": detected,
        "at_su_nghiep": at_sn,
        "at_phu_the": at_phu,
        "paradigm": (
            "⚠ Vũ Khúc Hóa Kỵ ở CẢ Sự Nghiệp + Phu Thê → tiền tài + tình cảm cùng phá tán"
            if detected
            else "Vũ Khúc Hóa Kỵ không trùng điệp Sự Nghiệp-Phu Thê"
        ),
    }


def _Q15_tham_lang_loc_cung_sang_lap(la_so: dict) -> dict[str, Any]:
    """Q15: Tham Lang Hóa Lộc ở Sự Nghiệp + Tử-Tham/Vũ-Tham ở Phu Thê → cùng sáng lập.

    Sách: "Vào đại vận có Vũ Khúc, Tham Lang → vợ chồng cùng nhau sáng lập sự nghiệp."
    """
    sn_name = "Sự Nghiệp" if _palace_index(la_so, "Sự Nghiệp") is not None else "Quan Lộc"
    tham_lang_loc_at_sn = _has_hoa_at_palace(la_so, "Tham Lang", sn_name, "Lộc")

    # Phu Thê có Tử-Tham hoặc Vũ-Tham
    phu_stars = set(_stars_at_named_palace(la_so, "Phu Thê")["chinh_tinh"])
    tu_tham = {"Tử Vi", "Tham Lang"}.issubset(phu_stars)
    vu_tham = {"Vũ Khúc", "Tham Lang"}.issubset(phu_stars)
    has_tham_combo = tu_tham or vu_tham

    detected = tham_lang_loc_at_sn and has_tham_combo
    return {
        "detected": detected,
        "tham_lang_hoa_loc_at_su_nghiep": tham_lang_loc_at_sn,
        "phu_the_tham_combo": "Tử-Tham" if tu_tham else ("Vũ-Tham" if vu_tham else None),
        "paradigm": (
            "✅ Tham Lang Hóa Lộc ở Sự Nghiệp + Phu Thê có Tử-Tham/Vũ-Tham → "
            "vợ chồng cùng nhau SÁNG LẬP sự nghiệp"
            if detected
            else "Không có pattern Tham Lang Lộc-Sự Nghiệp + Tham combo Phu Thê"
        ),
    }


# ─── PHASE 3 ───────────────────────────────────────────────────────────────

def _Q16_thien_ma_tu_vi_loan_du(la_so: dict) -> dict[str, Any]:
    """Q16: Thiên Mã đồng cung hoặc hội Tử Vi ở Phu Thê = "loan dư".

    Sách 3.x: "Thiên Mã ưa đồng cung hoặc hội chiếu với Tử Vi, cổ nhân gọi là
    'loan dư' (xe vua đi), có thể làm tăng khí thế của Tử Vi."
    """
    # Thiên Mã thường có trong sao_q2 hoặc phu_tinh
    thien_ma_idx = None
    for source in ("phu_tinh", "sat_tinh", "sao_q2"):
        d = la_so.get(source, {})
        if isinstance(d, dict) and "Thiên Mã" in d:
            thien_ma_idx = d["Thiên Mã"]
            break

    if thien_ma_idx is None:
        return {"detected": False, "note": "Engine an_sao chưa có Thiên Mã"}

    phu_the_idx = _palace_index(la_so, "Phu Thê")
    if phu_the_idx is None:
        return {"detected": False}

    # Tử Vi tại cung nào
    tu_vi_idx = la_so.get("chinh_tinh", {}).get("Tử Vi")
    if tu_vi_idx is None:
        return {"detected": False}

    # "Loan dư": Thiên Mã đồng cung Tử Vi HOẶC đối cung HOẶC tam hợp với Tử Vi
    # Đồng cung
    dong_cung = thien_ma_idx == tu_vi_idx
    # Đối cung
    doi_cung = thien_ma_idx == _fix(tu_vi_idx + 6)
    # Tam hợp
    tam_hop = thien_ma_idx in (_fix(tu_vi_idx + 4), _fix(tu_vi_idx + 8))

    loan_du = dong_cung or doi_cung or tam_hop

    # Check Tử Vi có trong tam phương Phu Thê không (để biết có liên quan Phu Thê)
    phu_the_tam_phuong = {
        phu_the_idx,
        _fix(phu_the_idx + 6),
        _fix(phu_the_idx + 4),
        _fix(phu_the_idx + 8),
    }
    tu_vi_in_phu_the_area = tu_vi_idx in phu_the_tam_phuong

    detected = loan_du and tu_vi_in_phu_the_area
    return {
        "detected": detected,
        "loan_du_hinh_thanh": loan_du,
        "tu_vi_in_phu_the_area": tu_vi_in_phu_the_area,
        "paradigm": (
            "✅ Thiên Mã + Tử Vi = 'loan dư' (xe vua đi) ảnh hưởng Phu Thê → "
            "vợ chồng quý hiển, khí thế cát"
            if detected
            else "Không hình thành 'loan dư' liên quan Phu Thê"
        ),
    }


def _Q17_loc_hop_uyen_uong(la_so: dict) -> dict[str, Any]:
    """Q17: Lộc Tồn + Hóa Lộc ở Phu Thê = "Lộc hợp uyên ương" — chung giàu có.

    Sách 3.x: "Cung Phu Thê gặp Lộc Tồn, có Hóa Lộc đến hội, gọi là cách
    'Lộc hợp uyên ương', chủ về có chung giàu có. Nam mệnh chủ về được vợ vượng phu."
    """
    phu_the_idx = _palace_index(la_so, "Phu Thê")
    if phu_the_idx is None:
        return {"detected": False}

    # Lộc Tồn ở Phu Thê?
    sat = la_so.get("sat_tinh", {})
    loc_ton_idx = sat.get("Lộc Tồn") if isinstance(sat, dict) else None
    loc_ton_at_phu = loc_ton_idx == phu_the_idx

    # Hóa Lộc đến hội (cùng cung HOẶC tam phương)
    tu_hoa = la_so.get("tu_hoa", {})
    hoa_loc_star = tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")
    hoa_loc_idx = None
    if hoa_loc_star:
        hoa_loc_idx = la_so.get("chinh_tinh", {}).get(hoa_loc_star)

    phu_the_tam_phuong = {
        phu_the_idx,
        _fix(phu_the_idx + 6),
        _fix(phu_the_idx + 4),
        _fix(phu_the_idx + 8),
    }
    hoa_loc_to_hoi = hoa_loc_idx is not None and hoa_loc_idx in phu_the_tam_phuong

    detected = loc_ton_at_phu and hoa_loc_to_hoi
    return {
        "detected": detected,
        "loc_ton_at_phu_the": loc_ton_at_phu,
        "hoa_loc_to_hoi": hoa_loc_to_hoi,
        "hoa_loc_star": hoa_loc_star,
        "paradigm": (
            f"✅ 'Lộc hợp uyên ương' — Lộc Tồn ở Phu Thê + {hoa_loc_star} Hóa Lộc đến hội → "
            "vợ chồng chung GIÀU CÓ; nam được vợ vượng phu"
            if detected
            else "Không hình thành 'Lộc hợp uyên ương'"
        ),
    }


def _Q18_thien_ma_da_la_sat_phu(la_so: dict, gender: str) -> dict[str, Any]:
    """Q18: Thiên Mã + Đà La + sát tinh ở Mệnh hoặc Phu Thê (nữ mệnh) → chọn lầm.

    Sách 3.x: "Thiên Mã có Đà La hội chiếu, lại gặp sát tinh chính diệu không
    cát tường, sẽ chủ về con đường lầm lạc. Cung Mệnh hoặc Phu Thê của nữ mệnh
    mà gặp tổ hợp này, dễ chọn lầm."
    """
    if not gender.startswith("nữ") and not gender.startswith("nu"):
        return {"detected": False, "note": "Chỉ áp dụng cho nữ mệnh"}

    # Tìm Thiên Mã
    thien_ma_idx = None
    for source in ("phu_tinh", "sat_tinh", "sao_q2"):
        d = la_so.get(source, {})
        if isinstance(d, dict) and "Thiên Mã" in d:
            thien_ma_idx = d["Thiên Mã"]
            break
    if thien_ma_idx is None:
        return {"detected": False}

    da_la_idx = la_so.get("sat_tinh", {}).get("Đà La")
    if da_la_idx is None:
        return {"detected": False}

    # Đà La hội chiếu Thiên Mã (cùng cung HOẶC tam phương)
    thien_ma_tam_phuong = {
        thien_ma_idx,
        _fix(thien_ma_idx + 6),
        _fix(thien_ma_idx + 4),
        _fix(thien_ma_idx + 8),
    }
    da_la_hoi = da_la_idx in thien_ma_tam_phuong
    if not da_la_hoi:
        return {"detected": False}

    # Có sát tinh nặng (Hỏa/Linh/Kình) ở cung Mệnh hoặc Phu Thê
    menh_idx = _palace_index(la_so, "Mệnh")
    phu_the_idx = _palace_index(la_so, "Phu Thê")
    sat = la_so.get("sat_tinh", {})
    sat_stars = {
        s: sat.get(s) for s in ("Hỏa Tinh", "Linh Tinh", "Kình Dương")
        if isinstance(sat, dict) and sat.get(s) is not None
    }
    sat_at_menh_or_phu = any(
        idx in (menh_idx, phu_the_idx) for idx in sat_stars.values()
    )

    detected = da_la_hoi and sat_at_menh_or_phu
    return {
        "detected": detected,
        "da_la_hoi_thien_ma": da_la_hoi,
        "sat_at_menh_phu": sat_at_menh_or_phu,
        "paradigm": (
            "⚠ Thiên Mã + Đà La + sát tinh ở Mệnh hoặc Phu Thê (nữ mệnh) → "
            "sách: dễ chọn lầm người, cần cẩn trọng"
            if detected
            else "Không có pattern lầm lạc"
        ),
    }


# ─── PHASE 4 ───────────────────────────────────────────────────────────────

def _Q19_cu_mon_menh_thi_phi(la_so: dict) -> dict[str, Any]:
    """Q19: Cự Môn tọa Mệnh + ảnh hưởng Phu Thê → "tiếng thị phi".

    Sách: "Cự Môn thủ cung Mệnh và Thân, một đời chuốc điều tiếng thị phi" —
    ảnh hưởng lan sang quan hệ Phu Thê.
    """
    menh_has_cu_mon = "Cự Môn" in _stars_at_named_palace(la_so, "Mệnh")["chinh_tinh"]

    # Phu Thê có sát tinh + Cự Môn Mệnh → mạnh hơn
    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")
    sat_in_phu = bool(set(phu_stars["phu_tinh"] + phu_stars["sat_tinh"]) &
                      {"Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La"})

    detected = menh_has_cu_mon
    severity = "nặng" if (detected and sat_in_phu) else "nhẹ" if detected else None

    return {
        "detected": detected,
        "menh_has_cu_mon": menh_has_cu_mon,
        "sat_in_phu_the": sat_in_phu,
        "severity": severity,
        "paradigm": (
            f"⚠ Cự Môn tọa Mệnh → 'tiếng thị phi' suốt đời, "
            f"cross Phu Thê mức độ {severity}"
            if detected
            else "Không có Cự Môn Mệnh"
        ),
    }


def _Q20_vu_khuc_hoa_linh_giao_tien_vo(la_so: dict, gender: str) -> dict[str, Any]:
    """Q20: Vũ Khúc + Hỏa-Linh tọa Mệnh + Phu Thê không tốt → "giao tiền cho vợ".

    Sách: "Nếu Vũ Khúc và Hỏa Tinh tọa Mệnh, có lúc sẽ bị phá tài, phép hóa giải
    là giao quyền tài chính cho người phối ngẫu. Nhưng nếu cung Phu Thê cũng
    không được tốt, thế thì khá phức tạp rồi."
    """
    menh_stars = _stars_at_named_palace(la_so, "Mệnh")
    menh_has_vu = "Vũ Khúc" in menh_stars["chinh_tinh"]
    menh_has_hoa_or_linh = bool(
        set(menh_stars["phu_tinh"] + menh_stars["sat_tinh"]) & {"Hỏa Tinh", "Linh Tinh"}
    )

    if not (menh_has_vu and menh_has_hoa_or_linh):
        return {"detected": False}

    # Phu Thê có vấn đề?
    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")
    phu_has_sat = bool(
        set(phu_stars["phu_tinh"] + phu_stars["sat_tinh"]) &
        {"Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La", "Địa Không", "Địa Kiếp"}
    )
    # Hóa Kỵ ở Phu Thê
    tu_hoa = la_so.get("tu_hoa", {})
    ki_star = tu_hoa.get("Kỵ") or tu_hoa.get("Hóa Kỵ")
    phu_has_ki = ki_star and ki_star in phu_stars["chinh_tinh"]
    phu_not_good = phu_has_sat or phu_has_ki

    return {
        "detected": True,
        "phu_the_not_good": phu_not_good,
        "paradigm": (
            "⚠⚠ Vũ Khúc + Hỏa/Linh tọa Mệnh + Phu Thê CŨNG không tốt → "
            "phức tạp; cần giao tài chính cho người phối ngẫu nhưng e ngại"
            if phu_not_good
            else "Vũ Khúc + Hỏa/Linh Mệnh → giao tài chính cho vợ là phép hóa giải tốt (vì Phu Thê ổn)"
        ),
    }


def _Q21_tham_lang_dao_hoa_tu_tuc(la_so: dict) -> dict[str, Any]:
    """Q21: Tham Lang + sao đào hoa ở Tử Tức + Tử-Tham/Vũ-Tham ở Phu Thê → cảnh báo.

    Sách: cung Tử Tức (Tử Nữ) cùng tam hợp Mệnh — Tham Lang đào hoa tại đây
    + Phu Thê có Tham → tăng nguy cơ tình ái rối ren.
    """
    tu_tuc_name = "Tử Tức" if _palace_index(la_so, "Tử Tức") is not None else "Tử Nữ"
    tu_stars = _stars_at_named_palace(la_so, tu_tuc_name)
    tu_has_tham = "Tham Lang" in tu_stars["chinh_tinh"]
    if not tu_has_tham:
        return {"detected": False}

    DAO_HOA = {"Hồng Loan", "Thiên Hỉ", "Hàm Trì", "Đại Hao", "Thiên Diêu"}
    dao_hoa_at_tu = bool(set(tu_stars.get("sao_q2", [])) & DAO_HOA)

    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")["chinh_tinh"]
    phu_has_tham = "Tham Lang" in phu_stars

    detected = tu_has_tham and dao_hoa_at_tu and phu_has_tham
    return {
        "detected": detected,
        "paradigm": (
            "⚠ Tham Lang + sao đào hoa tại Tử Tức + Tham Lang ở Phu Thê → "
            "cross-bind: tình ái rối ren có thể lan sang con cái"
            if detected
            else "Không có pattern Tham Lang đào hoa Tử Tức-Phu Thê"
        ),
    }


def _Q22_vu_khuc_ki_tai_bach(la_so: dict) -> dict[str, Any]:
    """Q22: Vũ Khúc Hóa Kỵ ở Tài Bạch + Phu Thê không tốt → tiền + tình cùng phá.

    Sách: "Người sinh năm Nhâm, Vũ Khúc Hóa Kỵ, nếu rơi vào Tài Bạch... đều có
    chỗ không hay. Nếu cung Phu Thê cũng không tốt thì phức tạp."
    """
    at_tb = _has_hoa_at_palace(la_so, "Vũ Khúc", "Tài Bạch", "Kỵ")
    if not at_tb:
        return {"detected": False}

    # Phu Thê không tốt?
    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")
    phu_has_sat = bool(
        set(phu_stars["phu_tinh"] + phu_stars["sat_tinh"]) &
        {"Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La"}
    )
    tu_hoa = la_so.get("tu_hoa", {})
    ki_star = tu_hoa.get("Kỵ") or tu_hoa.get("Hóa Kỵ")
    phu_has_ki = ki_star and ki_star in phu_stars["chinh_tinh"]
    phu_not_good = phu_has_sat or phu_has_ki

    return {
        "detected": True,
        "phu_the_not_good": phu_not_good,
        "paradigm": (
            "⚠⚠ Vũ Khúc Hóa Kỵ ở Tài Bạch + Phu Thê CŨNG không tốt → "
            "tiền + tình cùng phá tán"
            if phu_not_good
            else "Vũ Khúc Hóa Kỵ ở Tài Bạch (Phu Thê ổn) → chỉ tiền tài bị ảnh hưởng"
        ),
    }


# ─── PHASE 5 ───────────────────────────────────────────────────────────────

def _Q23_lien_trinh_ki_huynh_de_pha_phu(la_so: dict) -> dict[str, Any]:
    """Q23: Liêm Trinh Hóa Kỵ ở Huynh Đệ + Phá Quân ở Phu Thê → bất hòa anh em.

    Sách 5.3 Phá Quân: "Tổ hợp Phá Quân, Liêm Trinh, Thiên Tướng, nếu Liêm Trinh
    Hóa Kỵ, chủ về bạn đời bất hòa với anh chị em mệnh tạo."
    """
    at_hd = _has_hoa_at_palace(la_so, "Liêm Trinh", "Huynh Đệ", "Kỵ")
    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")["chinh_tinh"]
    phu_has_pha = "Phá Quân" in phu_stars

    detected = at_hd and phu_has_pha
    return {
        "detected": detected,
        "paradigm": (
            "⚠ Liêm Trinh Hóa Kỵ ở Huynh Đệ + Phá Quân ở Phu Thê → "
            "bạn đời bất hòa với anh chị em mệnh tạo"
            if detected
            else "Không có pattern Liêm Hóa Kỵ-Huynh × Phá Phu"
        ),
    }


def _Q24_cu_mon_phu_mau_phu_the(la_so: dict) -> dict[str, Any]:
    """Q24: Cự Môn ở Phụ Mẫu HOẶC Phu Thê → bất hòa thân gia / cãi vã.

    Sách: "Cự Môn ở các cung Phụ Mẫu/Phu Thê → bất hòa với gia đình bạn đời".
    """
    phu_mau_has_cu = "Cự Môn" in _stars_at_named_palace(la_so, "Phụ Mẫu")["chinh_tinh"]
    phu_the_has_cu = "Cự Môn" in _stars_at_named_palace(la_so, "Phu Thê")["chinh_tinh"]

    detected = phu_mau_has_cu and phu_the_has_cu
    return {
        "detected": detected,
        "phu_mau_has_cu_mon": phu_mau_has_cu,
        "phu_the_has_cu_mon": phu_the_has_cu,
        "paradigm": (
            "⚠ Cự Môn ở CẢ Phụ Mẫu + Phu Thê → "
            "bất hòa lớn giữa gia đình mình và gia đình bạn đời"
            if detected
            else "Không có pattern Cự Môn cross Phụ Mẫu-Phu Thê"
        ),
    }


def _Q25_vu_khuc_ki_dien_trach(la_so: dict) -> dict[str, Any]:
    """Q25: Vũ Khúc Hóa Kỵ ở Điền Trạch + Phu Thê không tốt → tổ ấm + hôn nhân cùng phá."""
    at_dt = _has_hoa_at_palace(la_so, "Vũ Khúc", "Điền Trạch", "Kỵ")
    if not at_dt:
        return {"detected": False}

    phu_stars = _stars_at_named_palace(la_so, "Phu Thê")
    phu_has_sat = bool(
        set(phu_stars["phu_tinh"] + phu_stars["sat_tinh"]) &
        {"Hỏa Tinh", "Linh Tinh", "Kình Dương", "Đà La"}
    )

    return {
        "detected": True,
        "phu_the_not_good": phu_has_sat,
        "paradigm": (
            "⚠ Vũ Khúc Hóa Kỵ ở Điền Trạch + Phu Thê có sát → "
            "tổ ấm + hôn nhân cùng phá"
            if phu_has_sat
            else "Vũ Khúc Hóa Kỵ Điền Trạch — Phu Thê ổn, ảnh hưởng nhẹ"
        ),
    }


def _Q26_sat_tat_ach_phu_the(la_so: dict) -> dict[str, Any]:
    """Q26: Sát tinh nặng ở Tật Ách → cảnh báo sức khỏe bạn đời.

    Sách: Bạch Hổ + Phi Xà + Đà La cùng ở Tật Ách → bạn đời nhiều bệnh.
    """
    tat_stars = _stars_at_named_palace(la_so, "Tật Ách")
    all_tat = set(tat_stars["phu_tinh"] + tat_stars["sat_tinh"] + tat_stars["sao_q2"])
    BAD = {"Bạch Hổ", "Phi Xà", "Đà La", "Kình Dương", "Linh Tinh"}
    found = all_tat & BAD

    detected = len(found) >= 2
    return {
        "detected": detected,
        "sat_found_at_tat_ach": sorted(found),
        "paradigm": (
            f"⚠ Sát tinh ({len(found)} sao: {', '.join(sorted(found))}) ở Tật Ách → "
            f"cảnh báo sức khỏe bạn đời / mệnh tạo"
            if detected
            else "Tật Ách không có sát tinh đáng kể"
        ),
    }


def _Q27_meta_aggregate(v3_result: dict, v4_rules: dict) -> dict[str, Any]:
    """Q27 (Meta): tổng hợp QUY LUẬT KÍCH HOẠT → đếm cảnh báo + điểm cát + tổng quan.

    Tổng quy luật đã build (đếm động, không hardcode):
    - v2: Q1-Q9 (9 quy luật cơ bản)
    - v3 cross-bind: Q10-Q142 (~28 quy luật, mở rộng theo thâm nhuần Trung Châu Q2)
    - v4 phase 2-5: Q14-Q26 (13 quy luật cross-bind 12 cung)

    Đếm động dựa vào số rules thực sự được wire trong v3.quy_luat_v3 + v4_rules.
    """
    canh_bao = []
    diem_cat = []

    # Lấy cảnh báo + cát từ v2
    v2_warning = v3_result.get("canh_bao", [])
    canh_bao.extend(v2_warning)

    # Đào hoa phạm chủ (v2)
    q2 = v3_result.get("quy_luat_v2", {}).get("2_dao_hoa_pham_chu", {})
    if q2.get("detected"):
        canh_bao.append(f"Q2: {q2.get('paradigm')}")

    # Hóa Kỵ trong cung (v2)
    if v3_result.get("hoa_ki_trong_cung"):
        canh_bao.append(f"Hóa Kỵ trong Phu Thê: {v3_result['hoa_ki_trong_cung']}")

    # Tả-Hữu hội chiếu (v2 cát)
    q4 = v3_result.get("quy_luat_v2", {}).get("4_ta_huu_doi_hoi_chieu", {})
    if q4.get("detected"):
        diem_cat.append(f"Q4: {q4.get('note')}")

    # v3 cross-bind
    v3_cb = v3_result.get("cross_bind_phuc_duc", {})
    canh_bao.extend(v3_cb.get("canh_bao_cross", []))
    diem_cat.extend(v3_cb.get("diem_cat_cross", []))

    # v4 quy luật
    for key, rule in v4_rules.items():
        if not rule.get("detected"):
            continue
        paradigm = rule.get("paradigm", "")
        if paradigm.startswith("⚠") or "phá" in paradigm.lower() or "lầm" in paradigm.lower() \
            or "bất hòa" in paradigm.lower() or "thị phi" in paradigm.lower():
            canh_bao.append(f"{key}: {paradigm}")
        elif paradigm.startswith("✅"):
            diem_cat.append(f"{key}: {paradigm}")

    total = len(canh_bao) + len(diem_cat)
    score_cat = len(diem_cat)
    score_hung = len(canh_bao)
    net = score_cat - score_hung

    if net >= 2:
        overall = "CÁT THẮNG"
    elif net <= -2:
        overall = "HUNG THẮNG"
    else:
        overall = "TRUNG HÒA"

    # Đếm động: 9 (v2) + số rules v3 + số rules v4
    v3_rules_count = len(v3_result.get("quy_luat_v3", {}))
    v4_rules_count = len(v4_rules)
    total_rules_built = 9 + v3_rules_count + v4_rules_count

    return {
        "total_rules_evaluated": total_rules_built,  # đếm động — không hardcode
        "total_rules_detected": score_cat + score_hung,
        "score_cat": score_cat,
        "score_hung": score_hung,
        "net": net,
        "overall": overall,
        "all_canh_bao": canh_bao,
        "all_diem_cat": diem_cat,
        "summary": (
            f"Tổng quan cung Phu Thê × {total_rules_built} quy luật Bắc phái Trung Châu "
            f"(kích hoạt {score_cat + score_hung}): "
            f"{score_cat} điểm cát × {score_hung} cảnh báo → {overall}"
        ),
    }


# ─── MAIN v4 ENGINE ────────────────────────────────────────────────────────

def chiem_phu_the_v4(la_so: dict) -> dict[str, Any]:
    """Engine v4 — Full cross-bind paradigm Bắc phái (26 quy luật + meta)."""
    base = chiem_phu_the_v3(la_so)
    gender = la_so.get("gender", "nam")

    # Phase 2-5 rules
    v4_rules = {
        "Q14_vu_khuc_ki_sn_phu": _Q14_vu_khuc_hoa_ki_sn_phuthe(la_so),
        "Q15_tham_lang_loc_cung_sang_lap": _Q15_tham_lang_loc_cung_sang_lap(la_so),
        "Q16_thien_ma_tu_vi_loan_du": _Q16_thien_ma_tu_vi_loan_du(la_so),
        "Q17_loc_hop_uyen_uong": _Q17_loc_hop_uyen_uong(la_so),
        "Q18_thien_ma_da_la_sat_phu": _Q18_thien_ma_da_la_sat_phu(la_so, gender),
        "Q19_cu_mon_menh_thi_phi": _Q19_cu_mon_menh_thi_phi(la_so),
        "Q20_vu_khuc_hoa_linh_giao_tien": _Q20_vu_khuc_hoa_linh_giao_tien_vo(la_so, gender),
        "Q21_tham_lang_dao_hoa_tu_tuc": _Q21_tham_lang_dao_hoa_tu_tuc(la_so),
        "Q22_vu_khuc_ki_tai_bach": _Q22_vu_khuc_ki_tai_bach(la_so),
        "Q23_lien_trinh_ki_hd_pha_phu": _Q23_lien_trinh_ki_huynh_de_pha_phu(la_so),
        "Q24_cu_mon_phu_mau_phu_the": _Q24_cu_mon_phu_mau_phu_the(la_so),
        "Q25_vu_khuc_ki_dien_trach": _Q25_vu_khuc_ki_dien_trach(la_so),
        "Q26_sat_tat_ach": _Q26_sat_tat_ach_phu_the(la_so),
    }

    # Q27 Meta: aggregate
    meta = _Q27_meta_aggregate(base, v4_rules)

    base["version"] = "v4"
    base["quy_luat_v4"] = v4_rules
    base["panorama_hon_nhan"] = meta
    return base
