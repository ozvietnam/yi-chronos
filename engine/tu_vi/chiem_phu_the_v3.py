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


# ─── Q14-Q18: cross-bind sao đôi/Hóa/combo Phúc Đức (mở rộng 2026-06-08) ──

# Map combo chính tinh Phúc Đức → cảnh báo cross-bind Phu Thê
_PHUC_DUC_COMBO_WARN = {
    frozenset({"Liêm Trinh", "Thất Sát"}): (
        "⚠ Phúc Đức = Liêm-Thất + Phu Thê tổ hợp Tử-Tham/Vũ-Tham → "
        "sách Trung Châu §5.3.6: 'mệnh xướng kĩ' (cổ, cảnh báo). "
        "HIỆN ĐẠI: tâm lý dễ thiên ham muốn vật chất + tình dục lẫn lộn, "
        "cần kỷ luật bản thân trong hôn nhân"
    ),
    frozenset({"Tử Vi", "Phá Quân"}): (
        "⚠ Phúc Đức = Tử-Phá → tâm bất an, dễ thay đổi quyết định hôn nhân, "
        "ảnh hưởng ổn định cung Phu Thê"
    ),
    frozenset({"Thiên Cơ", "Cự Môn"}): (
        "⚠ Phúc Đức = Cơ-Cự → suy nghĩ nhiều + tiếng thị phi → "
        "ảnh hưởng hoà thuận vợ chồng cross-Phu Thê"
    ),
    frozenset({"Vũ Khúc", "Phá Quân"}): (
        "⚠ Phúc Đức = Vũ-Phá → cô độc + thay đổi → "
        "cần Phu Thê có sao đôi + Hóa Lộc để bù"
    ),
}


def _Q14_phuc_duc_combo_canh_bao(la_so: dict) -> dict[str, Any]:
    """Q14: combo chính tinh Phúc Đức (Liêm-Thất, Tử-Phá, Cơ-Cự, Vũ-Phá)
    → cảnh báo paradigm cross-Phu Thê (sách §5.3.6 + diễn giải)."""
    phuc = _stars_at_named_palace(la_so, "Phúc Đức")
    chinh = frozenset(phuc["chinh_tinh"])
    for combo, paradigm in _PHUC_DUC_COMBO_WARN.items():
        if combo.issubset(chinh):
            return {
                "detected": True,
                "combo": list(combo),
                "paradigm": paradigm,
            }
    return {
        "detected": False,
        "paradigm": "Phúc Đức không thuộc combo cảnh báo (Liêm-Thất / Tử-Phá / Cơ-Cự / Vũ-Phá)",
    }


def _Q15_ta_huu_at_phuc_duc(la_so: dict) -> dict[str, Any]:
    """Q15: Tả Phù + Hữu Bật tại Phúc Đức — đôi = cát đoàn tụ, lẻ = cảnh báo."""
    phuc = _stars_at_named_palace(la_so, "Phúc Đức")
    pt = set(phuc["phu_tinh"])
    pair = {"Tả Phù", "Hữu Bật"} & pt
    n = len(pair)
    if n == 2:
        return {
            "detected": True,
            "is_cat": True,
            "stars": sorted(pair),
            "paradigm": "✅ Tả-Hữu ĐÔI tại Phúc Đức → sách Trung Châu: vợ chồng đoàn tụ, có trợ lực hai bên",
        }
    if n == 1:
        return {
            "detected": True,
            "is_cat": False,
            "stars": sorted(pair),
            "paradigm": f"⚠ {next(iter(pair))} LẺ tại Phúc Đức → sách: cảnh báo tái hôn / người thứ ba xen vào",
        }
    return {"detected": False, "paradigm": "Không có Tả-Hữu tại Phúc Đức"}


def _Q16_khoi_viet_at_phuc_duc(la_so: dict) -> dict[str, Any]:
    """Q16: Thiên Khôi + Thiên Việt tại Phúc Đức — đôi cát, lẻ cảnh báo."""
    phuc = _stars_at_named_palace(la_so, "Phúc Đức")
    pool = set(phuc["phu_tinh"]) | set(phuc["sao_q2"])
    pair = {"Thiên Khôi", "Thiên Việt"} & pool
    n = len(pair)
    if n == 2:
        return {
            "detected": True,
            "is_cat": True,
            "stars": sorted(pair),
            "paradigm": "✅ Khôi-Việt ĐÔI tại Phúc Đức → quý nhân phù trợ hôn nhân",
        }
    if n == 1:
        return {
            "detected": True,
            "is_cat": False,
            "stars": sorted(pair),
            "paradigm": f"⚠ {next(iter(pair))} LẺ tại Phúc Đức → cảnh báo: quý nhân lệch, tái hôn / người thứ ba xen",
        }
    return {"detected": False, "paradigm": "Không có Khôi-Việt tại Phúc Đức"}


def _Q17_cat_hoa_at_phuc_duc(la_so: dict) -> dict[str, Any]:
    """Q17: Hóa Lộc/Quyền/Khoa của sao trong Phúc Đức → cát cross-Phu Thê."""
    phuc = _stars_at_named_palace(la_so, "Phúc Đức")
    all_stars = set(phuc["chinh_tinh"]) | set(phuc["phu_tinh"]) | set(phuc["sao_q2"])
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    matches = []
    for hoa in ("Lộc", "Quyền", "Khoa"):
        star = tu_hoa.get(hoa) or tu_hoa.get(f"Hóa {hoa}")
        if star and star in all_stars:
            matches.append(f"{star} Hóa {hoa}")
    if matches:
        return {
            "detected": True,
            "is_cat": True,
            "hoa_list": matches,
            "paradigm": (
                f"✅ Tại Phúc Đức có cát Hóa: {', '.join(matches)} → "
                f"sách Trung Châu: phước báu hôn nhân được trợ, "
                f"tâm an + đạo lý gia đạo vững"
            ),
        }
    return {"detected": False, "paradigm": "Không có Hóa Lộc/Quyền/Khoa tại Phúc Đức"}


def _Q18_menh_thien_tuong_co_doc(la_so: dict) -> dict[str, Any]:
    """Q18: Mệnh Thiên Tướng + không có sao đôi tại Mệnh → kỵ cô độc → ảnh hưởng Phu Thê."""
    menh = _stars_at_named_palace(la_so, "Mệnh")
    chinh = set(menh["chinh_tinh"])
    if "Thiên Tướng" not in chinh:
        return {"detected": False, "paradigm": "Mệnh không có Thiên Tướng"}
    # Check sao đôi tại Mệnh
    phu = set(menh["phu_tinh"])
    sao_doi = (
        {"Tả Phù", "Hữu Bật"} & phu,
        {"Văn Xương", "Văn Khúc"} & phu,
        {"Thiên Khôi", "Thiên Việt"} & (phu | set(menh["sao_q2"])),
    )
    pair_count = sum(1 for p in sao_doi if len(p) == 2)
    if pair_count == 0:
        return {
            "detected": True,
            "is_cat": False,
            "paradigm": (
                "⚠ Mệnh Thiên Tướng KHÔNG có sao đôi → 'Tướng kỵ cô độc' (sách §5.3): "
                "Phu Thê cần cát tinh hỗ trợ + duy trì kết nối tâm tình, "
                "không để bản thân đi vào trạng thái cô lập"
            ),
        }
    return {
        "detected": True,
        "is_cat": True,
        "pair_count": pair_count,
        "paradigm": (
            f"✅ Mệnh Thiên Tướng có {pair_count} cặp sao đôi → "
            f"không rơi vào trạng thái cô độc, Phu Thê được bù đắp"
        ),
    }


# ─── Q19-Q21: từ thâm nhuần vòng 1 Trung Châu Q2 (Anh confirm ứng nghiệm 2026-06-08) ──

def _Q19_tu_vi_phu_the_tai_da_co_quan(la_so: dict) -> dict[str, Any]:
    """Q19: Tử Vi tọa Phu Thê + KHÔNG có Phủ-Tướng / Tả-Hữu / Khôi-Việt / Xương-Khúc
    → "Tại dã cô quân Phu Thê" — bạn đời độc đoán, thiếu trợ lực.

    Sách Trung Châu Q2 p10 — Vương Đình Chỉ:
    'Tử Vi nhập miếu không có Bách Quan Triều Củng thì còn khá, nếu lạc hãm mà
    còn không có Bách Quan Triều Củng, là Tại Dã Cô Quân'.

    Anh confirm 2026-06-08: Phu Thê Mão = Tử Vi + Tham Lang, không phụ tinh
    nào → ứng paradigm này.
    """
    pal = _stars_at_named_palace(la_so, "Phu Thê")
    chinh = set(pal["chinh_tinh"])
    if "Tử Vi" not in chinh:
        return {"detected": False, "paradigm": "Phu Thê không có Tử Vi"}

    # Check Bách Quan Triều Củng tại Phu Thê
    phu = set(pal["phu_tinh"])
    q2 = set(pal["sao_q2"])
    pool = phu | q2

    LUC_CAT = {"Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"}
    luc_cat_present = LUC_CAT & pool
    phu_tuong = {"Thiên Phủ", "Thiên Tướng"} & chinh

    if not luc_cat_present and not phu_tuong:
        return {
            "detected": True,
            "is_cat": False,
            "paradigm": (
                "⚠ Tử Vi tọa Phu Thê KHÔNG có Bách Quan Triều Củng (thiếu cả "
                "Phủ-Tướng + lục cát) → 'TẠI DÃ CÔ QUÂN Phu Thê' (sách Trung "
                "Châu Q2 p10): bạn đời tính độc đoán, thiếu trợ lực, dễ cô độc "
                "trong quan hệ. Cần phát triển con đường chính + lấy 'lòng "
                "chung thuỷ' bù 'sao đôi tâm linh'."
            ),
        }
    if luc_cat_present:
        return {
            "detected": True,
            "is_cat": True,
            "paradigm": (
                f"✅ Tử Vi tọa Phu Thê có lục cát ({', '.join(luc_cat_present)}) "
                "→ KHÔNG rơi vào 'Tại dã cô quân' — có trợ lực hôn nhân"
            ),
        }
    return {"detected": False, "paradigm": "Tử Vi Phu Thê có Phủ-Tướng (Bách Quan)"}


def _Q20_thai_duong_ham_sinh_dem(la_so: dict) -> dict[str, Any]:
    """Q20: Thái Dương HÃM + sinh ban đêm → cảnh báo bệnh mắt + tim mạch + thần kinh.

    Sách Trung Châu Q2 p26:
    'Người sinh ban đêm (giờ Thân-Dậu-Tuất-Hợi-Tý-Sửu) không nên có Thái Dương
    tọa Mệnh, Thái Dương lạc hãm càng không nên... bản thân dễ bị nạn tai,
    bệnh tật, nhất là chủ về bệnh hệ tuần hoàn, hệ thần kinh. Nếu ánh sáng
    của Thái Dương quá thịnh hoặc quá yếu, thì dễ mắc bệnh tật ở mắt'.

    Anh confirm 2026-06-08: anh sinh giờ Tý + Thái Dương ở Tật Ách Tý HÃM →
    paradigm ứng nghiệm bệnh mắt/tim mạch (anh xác nhận thực tế).

    Mở rộng paradigm sách: KHÔNG chỉ Thái Dương tọa Mệnh, mà Thái Dương HÃM ở
    bất kỳ cung nào + sinh đêm cũng có khả năng ứng.
    """
    NIGHT_HOURS = {"Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"}
    hour_branch = la_so.get("hour_branch", "")
    if hour_branch not in NIGHT_HOURS:
        return {"detected": False, "paradigm": "Sinh ban ngày — paradigm không ứng"}

    # Thái Dương position + miếu hãm
    chinh = la_so.get("chinh_tinh", {}) or {}
    td_idx = chinh.get("Thái Dương")
    if td_idx is None:
        return {"detected": False, "paradigm": "Lá số không có vị trí Thái Dương rõ"}

    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    td_branch = BR[td_idx]
    # Check miếu hãm
    try:
        from .mieu_vuong_ham import level_at
        level = (level_at("Thái Dương", td_branch) or "").lower()
    except Exception:
        level = ""

    if level not in ("hãm", "lạc", "lạc hãm"):
        return {
            "detected": False,
            "paradigm": f"Thái Dương tại {td_branch} không hãm (mức: {level}) — paradigm chưa ứng"
        }

    # Check Thái Dương tại cung nào (theo palaces)
    td_palace = None
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == td_idx:
            td_palace = p.get("name")
            break

    # Mức độ cảnh báo: tại Mệnh = mạnh nhất; Tật Ách = cảnh báo sức khoẻ; cung khác = nhẹ
    if td_palace == "Mệnh":
        msg = (
            "⚠ NẶNG — Thái Dương HÃM tọa MỆNH + sinh ban đêm (sách Trung Châu Q2 p26): "
            "bất lợi lục thân phái nam (cha/trưởng tử) + bệnh hệ tuần hoàn + thần "
            "kinh + bệnh mắt (loạn thị, lòa)"
        )
    elif td_palace == "Tật Ách":
        msg = (
            f"⚠ Thái Dương HÃM tại {td_palace} + sinh giờ {hour_branch} (ban đêm) "
            "→ cảnh báo SỨC KHOẺ: bệnh mắt, hệ tuần hoàn (tim mạch), hệ thần kinh. "
            "Sách Trung Châu Q2 p26: 'ánh sáng Thái Dương quá yếu dễ mắc bệnh mắt'"
        )
    else:
        msg = (
            f"⚠ Thái Dương HÃM tại {td_palace} + sinh ban đêm — cảnh báo nhẹ về "
            f"bệnh mắt / tim mạch (Trung Châu Q2 p26)"
        )

    return {
        "detected": True,
        "is_cat": False,
        "thai_duong_branch": td_branch,
        "thai_duong_palace": td_palace,
        "hour_branch": hour_branch,
        "level": level,
        "paradigm": msg,
    }


def _Q21_thien_co_thai_am_tu_tuc(la_so: dict) -> dict[str, Any]:
    """Q21: Thiên Cơ + Thái Âm cùng tại Tử Tức → paradigm con cái.

    Sách Trung Châu Q2 p18-21 — Thiên Cơ + Thái Âm là sao linh động + nhạy cảm.
    Tử Tức = con cái. Cặp đôi này tại Tử Tức:
    - Con linh động, đầu óc nhanh
    - Nhạy cảm tâm lý (Thái Âm)
    - Thiên về nghiên cứu / phân tích (Thiên Cơ nhập miếu)
    - Tâm trạng dễ buồn man mác (Thái Âm + Thiên Cơ hao phí trong tình ái nếu ở Dần/Thân)
    - Tị/Hợi: Thiên Cơ bình + Thái Âm đối — hao phí trong chuyện theo đuổi
      người khác giới (sách p21)

    Anh confirm 2026-06-08: con anh đúng paradigm.
    """
    pal = _stars_at_named_palace(la_so, "Tử Tức") or _stars_at_named_palace(la_so, "Tử Nữ")
    if not pal:
        return {"detected": False, "paradigm": "Không tìm thấy cung Tử Tức"}
    chinh = set(pal["chinh_tinh"])
    if not ({"Thiên Cơ", "Thái Âm"}.issubset(chinh)):
        return {
            "detected": False,
            "paradigm": "Tử Tức không có Thiên Cơ + Thái Âm đồng cung"
        }

    # Check vị trí (Dần-Thân vs Tị-Hợi)
    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    branch_idx = la_so.get("chinh_tinh", {}).get("Thiên Cơ")
    branch = BR[branch_idx] if branch_idx is not None else ""

    if branch in ("Dần", "Thân"):
        loc_note = (
            "đồng cung tại " + branch + " — con linh động + nhạy cảm, đầu óc "
            "nhanh, thiên về nghiên cứu/phân tích. Tâm lý dễ buồn man mác"
        )
    elif branch in ("Tị", "Hợi"):
        loc_note = (
            "đối cung tại " + branch + " — sách Trung Châu Q2 p21: 'hao phí "
            "tính linh động trong chuyện theo đuổi người khác giới', năng lực "
            "phân tích dùng để phân tích tâm lý đối tượng"
        )
    else:
        loc_note = "tại " + branch + " — linh động + nhạy cảm + nghiên cứu"

    return {
        "detected": True,
        "is_cat": True,
        "branch": branch,
        "paradigm": (
            f"✅ Tử Tức có Thiên Cơ + Thái Âm {loc_note}. Sách Trung Châu Q2: "
            "Thiên Cơ = mưu sĩ (đầu óc linh động) + Thái Âm = tâm hồn nhạy cảm "
            "→ con cái thông minh nhạy bén, có thiên hướng nghiên cứu / nghệ "
            "thuật, nhưng dễ thiên cảm xúc — cần định hướng kỷ luật để phát "
            "triển con đường chính"
        ),
    }


def chiem_phu_the_v3(la_so: dict) -> dict[str, Any]:
    """Engine v3 — v2 (9 quy luật) + Q10-Q21 cross-bind Phúc Đức + Mệnh + Phu Thê + Tử Tức.

    Q10-Q13: detect Xương-Khúc + Văn Khúc Hóa Kỵ + Địa Không (cấu trúc giáp)
    Q14-Q18: detect combo Phúc Đức + sao đôi + Hóa cát + Mệnh Tướng cô độc
    Q19-Q21: từ thâm nhuần vòng 1 Trung Châu Q2 (2026-06-08, Anh confirm ứng nghiệm)

    Output structure: backward-compat với v2, thêm field `quy_luat_v3`.
    """
    result = chiem_phu_the_v2(la_so)

    # Cross-bind Phúc Đức + Mệnh + Phu Thê + Tử Tức — 12 quy luật
    cross = {
        "10_van_khuc_hoa_ki_cross": _Q10_van_khuc_hoa_ki_at_phuc_or_phuthe(la_so),
        "11_xuong_khuc_giap_phu_the": _Q11_xuong_khuc_giap_phu_the(la_so),
        "12_xuong_khuc_chia_re_cat": _Q12_xuong_khuc_split_menh_phu_or_phuc_phu(la_so),
        "13_dia_khong_cross_tam_phuc": _Q13_dia_khong_at_phuc_or_phu_or_tu(la_so),
        "14_phuc_duc_combo_canh_bao": _Q14_phuc_duc_combo_canh_bao(la_so),
        "15_ta_huu_phuc_duc": _Q15_ta_huu_at_phuc_duc(la_so),
        "16_khoi_viet_phuc_duc": _Q16_khoi_viet_at_phuc_duc(la_so),
        "17_cat_hoa_phuc_duc": _Q17_cat_hoa_at_phuc_duc(la_so),
        "18_menh_thien_tuong_co_doc": _Q18_menh_thien_tuong_co_doc(la_so),
        # Từ vòng 1 thâm nhuần Trung Châu Q2 (2026-06-08)
        "19_tu_vi_phu_the_tai_da_co_quan": _Q19_tu_vi_phu_the_tai_da_co_quan(la_so),
        "20_thai_duong_ham_sinh_dem": _Q20_thai_duong_ham_sinh_dem(la_so),
        "21_thien_co_thai_am_tu_tuc": _Q21_thien_co_thai_am_tu_tuc(la_so),
    }

    # Aggregate cảnh báo + điểm cát theo is_cat flag (cho rules có flag) hoặc semantic key
    canh_bao = []
    diem_cat = []

    # Q10-13 (legacy): paradigm có ⚠ hoặc ✅
    if cross["10_van_khuc_hoa_ki_cross"].get("detected"):
        canh_bao.append(cross["10_van_khuc_hoa_ki_cross"]["paradigm"])
    if cross["11_xuong_khuc_giap_phu_the"].get("detected"):
        canh_bao.append(cross["11_xuong_khuc_giap_phu_the"]["paradigm"])
    if cross["13_dia_khong_cross_tam_phuc"].get("detected"):
        canh_bao.append(cross["13_dia_khong_cross_tam_phuc"]["paradigm"])
    if cross["12_xuong_khuc_chia_re_cat"].get("detected"):
        diem_cat.append(cross["12_xuong_khuc_chia_re_cat"]["paradigm"])

    # Q14-21 (mới): có is_cat flag → phân loại rõ
    for key in ("14_phuc_duc_combo_canh_bao", "15_ta_huu_phuc_duc",
                "16_khoi_viet_phuc_duc", "17_cat_hoa_phuc_duc",
                "18_menh_thien_tuong_co_doc",
                "19_tu_vi_phu_the_tai_da_co_quan",
                "20_thai_duong_ham_sinh_dem",
                "21_thien_co_thai_am_tu_tuc"):
        rule = cross[key]
        if not rule.get("detected"):
            continue
        if rule.get("is_cat", False):
            diem_cat.append(rule["paradigm"])
        else:
            # Q14 không có is_cat field (luôn warn nếu detected)
            canh_bao.append(rule["paradigm"])

    # Lookup chính tinh Phúc Đức + Mệnh để cung cấp context
    phuc_duc_stars = _stars_at_named_palace(la_so, "Phúc Đức")
    menh_stars = _stars_at_named_palace(la_so, "Mệnh")

    result["version"] = "v3"
    result["quy_luat_v3"] = cross
    result["cross_bind_phuc_duc"] = {
        "phuc_duc_chinh_tinh": phuc_duc_stars["chinh_tinh"],
        "phuc_duc_phu_tinh": phuc_duc_stars["phu_tinh"],
        "phuc_duc_sat_tinh": phuc_duc_stars["sat_tinh"],
        "phuc_duc_branch_index": _palace_index(la_so, "Phúc Đức"),
        "menh_chinh_tinh": menh_stars["chinh_tinh"],
        "menh_phu_tinh": menh_stars["phu_tinh"],
        "menh_sat_tinh": menh_stars["sat_tinh"],
        "menh_branch_index": _palace_index(la_so, "Mệnh"),
        "canh_bao_cross": canh_bao,
        "diem_cat_cross": diem_cat,
        "summary": (
            f"{len(diem_cat)} điểm cát + {len(canh_bao)} cảnh báo cross-bind"
            if (diem_cat or canh_bao)
            else "Phúc Đức + Mệnh không có dấu hiệu cross-bind đặc biệt cho Phu Thê"
        ),
    }

    return result
