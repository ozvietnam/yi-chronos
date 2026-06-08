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


# ─── Q22-Q24: từ thâm nhuần vòng 2 Trung Châu Q2 (Anh confirm 2026-06-08) ──

# 6 cặp sao đôi cát (Trung Châu Q2 p30 — Vương Đình Chỉ)
_PAIRS_CAT = [
    ("Tả Phù", "Hữu Bật"),
    ("Văn Xương", "Văn Khúc"),
    ("Thiên Khôi", "Thiên Việt"),
    ("Tam Thai", "Bát Tọa"),
    ("Ân Quang", "Thiên Quý"),
    ("Long Trì", "Phượng Các"),
]


def _scan_pairs_in_palace(la_so: dict, palace_name: str) -> dict[str, Any]:
    """Scan 6 cặp sao đôi cát trong 1 cung. Trả về danh sách cặp đôi + sao lẻ."""
    pal = _stars_at_named_palace(la_so, palace_name)
    pool = set(pal["phu_tinh"]) | set(pal["sao_q2"])
    # Cũng include sao_le (Ân Quang, Thiên Quý nếu có)
    sao_le = la_so.get("sao_le", {}) or {}
    pal_idx = _palace_index(la_so, palace_name)
    for star, idx in sao_le.items():
        if idx == pal_idx:
            pool.add(star)

    pairs_full = []   # cặp ĐÔI đủ
    stars_le = []     # sao lẻ
    for a, b in _PAIRS_CAT:
        a_in = a in pool
        b_in = b in pool
        if a_in and b_in:
            pairs_full.append(f"{a}-{b}")
        elif a_in:
            stars_le.append(a)
        elif b_in:
            stars_le.append(b)
    return {
        "pairs_full": pairs_full,
        "stars_le": stars_le,
        "n_pairs": len(pairs_full),
        "n_le": len(stars_le),
    }


def _Q22_sao_doi_cap_3_cung(la_so: dict) -> dict[str, Any]:
    """Q22: Quy tắc "Sao đôi đủ cặp > sao lẻ" — scan Mệnh + Phúc Đức + Phu Thê.

    Sách Trung Châu Q2 p30: 'Sao đôi đủ cặp đồng cung, sức mạnh lớn hơn 3-4
    sao lẻ trong lục cát phân tán.'

    Anh: Phúc Đức Mùi có Tả-Hữu ĐÔI ✓ + Thiên Việt LẺ ⚠ — đã verify.
    """
    results = {}
    for palace in ("Mệnh", "Phúc Đức", "Phu Thê"):
        results[palace] = _scan_pairs_in_palace(la_so, palace)

    total_pairs = sum(r["n_pairs"] for r in results.values())
    total_le = sum(r["n_le"] for r in results.values())

    notes = []
    for palace, r in results.items():
        if r["n_pairs"] > 0:
            notes.append(f"✅ {palace}: {r['n_pairs']} cặp ĐÔI ({', '.join(r['pairs_full'])})")
        if r["n_le"] > 0:
            notes.append(f"⚠ {palace}: {r['n_le']} sao LẺ ({', '.join(r['stars_le'])})")

    if not notes:
        return {
            "detected": False,
            "paradigm": "Mệnh / Phúc Đức / Phu Thê không có sao đôi cát nào",
        }

    summary_short = f"{total_pairs} cặp ĐÔI + {total_le} sao LẺ (Mệnh + Phúc Đức + Phu Thê)"
    # Sách Trung Châu p30: '1 cặp ĐÔI > 3-4 sao LẺ' → CÓ cặp là CÁT;
    # NHƯNG le cũng có cảnh báo riêng (tái hôn / người thứ ba). Em verdict:
    #  - is_cat = True nếu có ít nhất 1 pair (giữ trọng tâm vào cát của cặp đôi)
    #  - Trong paradigm message vẫn liệt kê warning của sao LẺ để user thấy
    is_cat_overall = total_pairs > 0
    return {
        "detected": True,
        "is_cat": is_cat_overall,
        "total_pairs": total_pairs,
        "total_le": total_le,
        "by_palace": results,
        "paradigm": (
            f"📊 Sao đôi (sách Trung Châu p30): {summary_short}. "
            + " · ".join(notes)
            + f" → Quy tắc: 1 cặp ĐÔI mạnh hơn 3-4 sao LẺ. "
            + (f"Có {total_pairs} cặp ĐÔI = trợ lực + đoàn tụ. "
               if total_pairs > 0 else "")
            + (f"Có {total_le} sao LẺ = cảnh báo nhẹ tái hôn / người thứ ba / cô độc."
               if total_le > 0 else "")
        ),
    }


def _Q23_vu_pha_ty_hoi_nong_nay(la_so: dict) -> dict[str, Any]:
    """Q23: Vũ Khúc + Phá Quân đồng cung tại Tỵ/Hợi → 'biến cương thành nóng
    nảy, quyết định xung động nhất thời → thất bại'.

    Sách Trung Châu Q2 p34: 'Vũ Khúc gặp Phá Quân càng biến tính cứng rắn của
    Vũ Khúc thành nóng nảy, quyết đoán, thường dễ vì thiếu suy nghĩ hoặc
    không có kế hoạch dài lâu, hay vì xung động nhất thời mà dẫn đến thất
    bại. Cổ nhân nói: Vũ-Phá khó quý hiển.'

    Anh confirm 2026-06-08: 'hay nóng nảy ra quyết định lớn'.
    """
    # Tìm Vũ Khúc + Phá Quân đồng cung
    chinh = la_so.get("chinh_tinh", {}) or {}
    vu_idx = chinh.get("Vũ Khúc")
    pq_idx = chinh.get("Phá Quân")
    if vu_idx is None or pq_idx is None or vu_idx != pq_idx:
        return {"detected": False, "paradigm": "Lá số không có Vũ-Phá đồng cung"}

    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    branch = BR[vu_idx]
    if branch not in ("Tỵ", "Hợi"):
        return {
            "detected": False,
            "paradigm": f"Vũ-Phá đồng cung tại {branch} (không phải Tỵ/Hợi)"
        }

    # Tìm cung của Vũ-Phá
    palace_name = ""
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == vu_idx:
            palace_name = p.get("name", "")
            break

    return {
        "detected": True,
        "is_cat": False,
        "branch": branch,
        "palace": palace_name,
        "paradigm": (
            f"⚠ Vũ Khúc + Phá Quân đồng cung tại {branch} ({palace_name}) — "
            f"sách Trung Châu Q2 p34: 'biến tính cương thành nóng nảy, quyết "
            f"định xung động nhất thời → thất bại'. Lời khuyên: trước quyết "
            f"định lớn (mua bán, đổi nghề, lời nói) → dừng 24h, hỏi 1 người "
            f"tin cẩn. Anh có Hữu Bật Hóa Khoa Phúc Đức = trợ lực tâm — dùng "
            f"để cân bằng tính nóng."
        ),
    }


def _Q24_vu_pha_sat_thien_di_tai_nan(la_so: dict) -> dict[str, Any]:
    """Q24: Vũ Khúc + Phá Quân + sát (Đà La/Hỏa-Linh/Không-Kiếp) tại Thiên Di
    → cảnh báo tai nạn xa nhà.

    Sách Trung Châu Q2 p36 case Vương Đình Chỉ: ngã vực Úc Châu 3 tháng bệnh
    viện + phá tướng, do Thiên Di lưu niên Vũ Khúc + Đà La. May có Thiên
    Tướng đồng cung + đại vận tốt → không chết.

    Mở rộng paradigm: KHÔNG chỉ lưu niên, mà Thiên Di gốc có Vũ-Phá + sát
    cũng có cảnh báo.

    Anh confirm 2026-06-08: 'tai nạn thì có, cũng gọi là cách xa nhà'.
    """
    # Tìm cung Thiên Di
    thien_di_pal = _stars_at_named_palace(la_so, "Thiên Di")
    if not thien_di_pal:
        return {"detected": False, "paradigm": "Không tìm thấy cung Thiên Di"}

    chinh = set(thien_di_pal["chinh_tinh"])
    sat = set(thien_di_pal["sat_tinh"])
    phu = set(thien_di_pal["phu_tinh"])

    has_vu_pha = {"Vũ Khúc", "Phá Quân"}.issubset(chinh)
    if not has_vu_pha:
        return {"detected": False, "paradigm": "Thiên Di không có Vũ-Phá đồng cung"}

    LUC_SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}
    sat_in_pal = LUC_SAT & (sat | phu)
    if not sat_in_pal:
        return {
            "detected": False,
            "paradigm": "Thiên Di có Vũ-Phá nhưng không có lục sát đi kèm"
        }

    return {
        "detected": True,
        "is_cat": False,
        "sat_stars": sorted(sat_in_pal),
        "paradigm": (
            f"⚠ Thiên Di có Vũ Khúc + Phá Quân + sát ({', '.join(sorted(sat_in_pal))}) "
            f"— sách Trung Châu Q2 p36 case Vương Đình Chỉ ngã vực Úc Châu vì "
            f"Vũ-Đà Thiên Di lưu niên. Cảnh báo TAI NẠN khi đi xa nhà (công "
            f"tác, du lịch, di chuyển dài). Lời khuyên: khi đại vận / lưu "
            f"niên đi qua cung này, đặc biệt cẩn trọng giao thông + sức khoẻ; "
            f"chọn bạn đồng hành đáng tin; tránh quyết định mạo hiểm tại "
            f"nước ngoài / xa nhà."
        ),
    }


# ─── Q29 + Q35 + Q40: từ thâm nhuần vòng 3-5 Trung Châu Q2 (2026-06-08) ──

# Bảng tam hợp chi năm → cung Mệnh (Vương Đình Chỉ p64)
_TAM_HOP_CUNG_MENH = {
    "Mão": {"Hợi", "Mão", "Mùi"},   # tam hợp Mộc
    "Ngọ": {"Dần", "Ngọ", "Tuất"},  # tam hợp Hỏa
    "Dậu": {"Tỵ", "Dậu", "Sửu"},    # tam hợp Kim
    "Tý":  {"Thân", "Tý", "Thìn"},  # tam hợp Thủy
}


def _Q29_tham_lang_vuong_chi_nam_tam_hop(la_so: dict) -> dict[str, Any]:
    """Q29: Tham Lang ở 4 cung VƯỢNG (Tý/Ngọ/Mão/Dậu) — phân biệt 'ham muốn
    vật chất' vs 'đào hoa phạm chủ dục tình' theo CHI NĂM tam hợp.

    Sách Trung Châu Q2 p64 — Vương Đình Chỉ:
    'Tham Lang ở 4 cung vượng... PHẢI là người sinh năm tam hợp với cung
    Mệnh, mới chủ về ham muốn vật chất. NẾU KHÔNG, là Đào hoa phạm chủ —
    chủ về DỤC TÌNH.'

    Mở rộng: paradigm gốc nói về Tham Lang tại Mệnh. Engine em mở rộng cho
    Phu Thê: nếu bạn đời có Tham Lang vượng + sinh chi năm KHÔNG tam hợp
    với cung Phu Thê → bạn đời chủ dục tình.

    Anh confirm 2026-06-08: 'có phần đúng' — Tham Lang Phu Thê Mão + Mậu
    Thìn (tam hợp Thủy = Tý) → KHÔNG tam hợp với Mão (tam hợp Mộc).
    """
    chinh = la_so.get("chinh_tinh", {}) or {}
    tham_idx = chinh.get("Tham Lang")
    if tham_idx is None:
        return {"detected": False, "paradigm": "Lá số không có Tham Lang"}

    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    tham_branch = BR[tham_idx]
    if tham_branch not in ("Tý", "Ngọ", "Mão", "Dậu"):
        return {
            "detected": False,
            "paradigm": f"Tham Lang tại {tham_branch} (không phải 4 cung vượng Tý/Ngọ/Mão/Dậu)"
        }

    # Tìm cung Tham Lang đang ở
    tham_palace = None
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == tham_idx:
            tham_palace = p.get("name", "")
            break

    # Check chi năm sinh có tam hợp với cung này không
    year_branch = la_so.get("year_branch", "")
    tam_hop_set = _TAM_HOP_CUNG_MENH.get(tham_branch, set())
    in_tam_hop = year_branch in tam_hop_set

    if in_tam_hop:
        return {
            "detected": True,
            "is_cat": True,
            "tham_branch": tham_branch,
            "tham_palace": tham_palace,
            "year_branch": year_branch,
            "tam_hop_set": sorted(tam_hop_set),
            "paradigm": (
                f"✅ Tham Lang vượng tại {tham_branch} ({tham_palace}) + chi năm "
                f"sinh {year_branch} ∈ tam hợp ({', '.join(sorted(tam_hop_set))}) "
                f"→ chủ về 'HAM MUỐN VẬT CHẤT' (chí tiến thủ, theo đuổi tài lộc) "
                f"— sách Trung Châu Q2 p64"
            ),
        }
    return {
        "detected": True,
        "is_cat": False,
        "tham_branch": tham_branch,
        "tham_palace": tham_palace,
        "year_branch": year_branch,
        "tam_hop_set": sorted(tam_hop_set),
        "paradigm": (
            f"⚠ Tham Lang vượng tại {tham_branch} ({tham_palace}) + chi năm "
            f"sinh {year_branch} ∉ tam hợp ({', '.join(sorted(tam_hop_set))}) "
            f"→ 'ĐÀO HOA PHẠM CHỦ' dục tình (sách Trung Châu Q2 p64). "
            f"Lời khuyên: phát triển 'con đường chính' (Văn Xương Khúc / "
            f"Thiên Hình / Hóa Kỵ kỷ luật) → biến thành 'phong lưu mà không "
            f"hạ lưu' (văn học gia, nghệ thuật gia)."
        ),
    }


def _Q35_thien_tuong_menh_giap_cuc(la_so: dict) -> dict[str, Any]:
    """Q35: Thiên Tướng tọa Mệnh + giáp cục — Tài Ấm Giáp Ấn vs Hình Kỵ Giáp Ấn.

    Sách Trung Châu Q2 p77-p78 — Vương Đình Chỉ:
    'Thiên Tướng = ấn tinh, không có tính chất riêng, HOÀN TOÀN bị hoàn cảnh
    chi phối. Phải xem HAI CUNG GIÁP TRƯỚC, rồi mới xem tam phương tứ chính.'

    2 cách giáp:
    - Tài Ấm Giáp Ấn (CÁT): Cự Hóa Lộc + Thiên Lương giáp → tài+ấm phủ ấn
    - Hình Kỵ Giáp Ấn (HUNG): 1 cung Kình Dương + 1 cung Hóa Kỵ giáp

    Anh confirm 2026-06-08: 'gia đình luôn che chở anh' — đúng Tài Ấm.
    """
    pal_menh = _stars_at_named_palace(la_so, "Mệnh")
    if "Thiên Tướng" not in pal_menh["chinh_tinh"]:
        return {"detected": False, "paradigm": "Mệnh không có Thiên Tướng"}

    menh_idx = _palace_index(la_so, "Mệnh")
    if menh_idx is None:
        return {"detected": False, "paradigm": "Không tìm thấy cung Mệnh"}

    # 2 cung giáp Mệnh (idx-1 và idx+1)
    giap_pre_idx = _fix(menh_idx - 1)
    giap_post_idx = _fix(menh_idx + 1)

    # Tìm tên 2 cung giáp
    palace_by_idx = {p.get("branch_index"): p.get("name", "") for p in la_so.get("palaces", [])}
    pre_palace = palace_by_idx.get(giap_pre_idx, "")
    post_palace = palace_by_idx.get(giap_post_idx, "")

    pre_stars = _stars_at_branch_idx(la_so, giap_pre_idx)
    post_stars = _stars_at_branch_idx(la_so, giap_post_idx)

    # Check Cự Môn + Thiên Lương giáp (cấu trúc Tài Ấm)
    has_cu_giap = "Cự Môn" in (pre_stars["chinh_tinh"] + post_stars["chinh_tinh"])
    has_luong_giap = "Thiên Lương" in (pre_stars["chinh_tinh"] + post_stars["chinh_tinh"])

    if not (has_cu_giap and has_luong_giap):
        return {
            "detected": False,
            "paradigm": "Mệnh Thiên Tướng không có Cự Môn + Thiên Lương giáp"
        }

    # Check Hóa Lộc trong cung Cự Môn (hoặc sao đồng độ)
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    has_hoa_loc_giap = False
    hoa_loc_star = tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")
    pre_all = set(pre_stars["chinh_tinh"]) | set(pre_stars["phu_tinh"]) | set(pre_stars["sao_q2"])
    post_all = set(post_stars["chinh_tinh"]) | set(post_stars["phu_tinh"]) | set(post_stars["sao_q2"])
    if hoa_loc_star and (hoa_loc_star in pre_all or hoa_loc_star in post_all):
        has_hoa_loc_giap = True

    # Check Kình Dương + Hóa Kỵ giáp (Hình Kỵ)
    has_kinh_duong_giap = (
        "Kình Dương" in pre_stars["sat_tinh"] or
        "Kình Dương" in post_stars["sat_tinh"]
    )
    hoa_ki_star = tu_hoa.get("Kỵ") or tu_hoa.get("Hóa Kỵ")
    has_hoa_ki_giap = bool(hoa_ki_star) and (hoa_ki_star in pre_all or hoa_ki_star in post_all)

    # Verdict
    if has_hoa_loc_giap and not (has_kinh_duong_giap and has_hoa_ki_giap):
        return {
            "detected": True,
            "is_cat": True,
            "is_tai_am": True,
            "paradigm": (
                f"✅ Thiên Tướng Mệnh + 'TÀI ẤM GIÁP ẤN' đầy đủ — Cự Môn "
                f"({pre_palace if 'Cự Môn' in pre_stars['chinh_tinh'] else post_palace}) "
                f"có Hóa Lộc + Thiên Lương "
                f"({pre_palace if 'Thiên Lương' in pre_stars['chinh_tinh'] else post_palace}) "
                f"giáp Mệnh → sách Trung Châu Q2 p78: gia đình + anh chị em "
                f"che chở mạnh, tài lộc + ấm tinh đầy đủ."
            ),
        }
    if has_kinh_duong_giap and has_hoa_ki_giap:
        return {
            "detected": True,
            "is_cat": False,
            "is_hinh_ki": True,
            "paradigm": (
                "⚠ Thiên Tướng Mệnh + 'HÌNH KỴ GIÁP ẤN' đầy đủ — Kình Dương "
                "+ Hóa Kỵ giáp Mệnh → sách Trung Châu Q2 p78: Tướng bị hoàn "
                "cảnh kéo xấu, dễ tai họa kéo dài."
            ),
        }

    # Tổ hợp lai (anh ứng — Tài Ấm thiếu Hóa Lộc + Kình Dương 1 cung)
    parts = []
    if has_cu_giap and has_luong_giap:
        parts.append("Cự Môn + Thiên Lương giáp Mệnh (cấu trúc TÀI ẤM)")
    if not has_hoa_loc_giap:
        parts.append("THIẾU Hóa Lộc Cự Môn (Tài Ấm chưa đầy đủ)")
    if has_kinh_duong_giap:
        parts.append("CÓ Kình Dương 1 cung giáp (1/2 yếu tố Hình)")
    if not has_hoa_ki_giap:
        parts.append("KHÔNG Hóa Kỵ giáp (Hình Kỵ KHÔNG đầy đủ)")

    return {
        "detected": True,
        "is_cat": True,  # gia đình che chở là cát
        "is_lai": True,
        "paradigm": (
            "🌓 Thiên Tướng Mệnh + GIÁP CỤC LAI: " + " · ".join(parts) +
            ". Sách Trung Châu Q2 p78: có lực 'ấm' che chở từ Phụ Mẫu "
            "(Thiên Lương) + Huynh Đệ (Cự Môn) — gia đình hỗ trợ. Tuy "
            "thiếu Hóa Lộc Cự Môn nên tài lộc KHÔNG tự nhiên đầy đủ, cần "
            "phấn đấu hậu thiên. Kình Dương 1 cung giáp = ý chí cương "
            "quyết của Phụ Mẫu, không phải 'Hình Kỵ' đầy đủ."
        ),
    }


def _Q40_phung_phu_khan_tuong(la_so: dict) -> dict[str, Any]:
    """Q40: 'Phùng Phủ khán Tướng' / 'Phùng Tướng khán Phủ' — bí mật Trung Châu.

    Sách Trung Châu Q2 p81 — Vương Đình Chỉ:
    'Thiên Phủ-Thiên Tướng luôn tương hội tam phương. Khi Phủ XẤU (gặp tứ
    sát, hình kỵ, ác tinh), DÙ Tướng bản thân không gặp sát, Tướng vẫn bị
    KÉO XẤU → tham lam ti tiện, không chủ kiến, phản ứng sai lầm.'

    Logic ngược lại: Tướng tốt + Phủ tốt → cả hai cộng hưởng cát.

    Anh confirm 2026-06-08: 'có ý đúng' — Tướng Mệnh Tỵ + Phủ Tài Bạch Sửu
    cả 2 đều KHÔNG xấu.
    """
    pal_menh = _stars_at_named_palace(la_so, "Mệnh")
    chinh_menh = set(pal_menh["chinh_tinh"])

    has_tuong = "Thiên Tướng" in chinh_menh
    has_phu = "Thiên Phủ" in chinh_menh

    if not (has_tuong or has_phu):
        return {"detected": False, "paradigm": "Mệnh không có Thiên Tướng và Thiên Phủ"}

    # Tìm sao kia (Phủ nếu Tướng ở Mệnh, ngược lại)
    target_star = "Thiên Phủ" if has_tuong else "Thiên Tướng"
    target_idx = la_so.get("chinh_tinh", {}).get(target_star)
    if target_idx is None:
        return {"detected": False, "paradigm": f"Lá số không có {target_star}"}

    target_stars = _stars_at_branch_idx(la_so, target_idx)

    # Tìm cung chứa sao kia
    target_palace = None
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == target_idx:
            target_palace = p.get("name", "")
            break

    # Đánh giá xấu/tốt của target
    LUC_SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}
    sat_in_target = LUC_SAT & (set(target_stars["sat_tinh"]) | set(target_stars["phu_tinh"]))

    tu_hoa = la_so.get("tu_hoa", {}) or {}
    ki_star = tu_hoa.get("Kỵ") or tu_hoa.get("Hóa Kỵ")
    target_pool = (set(target_stars["chinh_tinh"]) | set(target_stars["phu_tinh"]) |
                   set(target_stars["sao_q2"]))
    has_ki_in_target = bool(ki_star) and ki_star in target_pool

    # Sao quý nhân CÁT
    LUC_CAT = {"Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"}
    cat_in_target = LUC_CAT & target_pool

    # Verdict
    is_target_xau = bool(sat_in_target) or has_ki_in_target
    is_target_tot = bool(cat_in_target) and not is_target_xau

    menh_star = "Thiên Tướng" if has_tuong else "Thiên Phủ"
    quy_tac = "Phùng Tướng khán Phủ" if has_tuong else "Phùng Phủ khán Tướng"

    if is_target_xau:
        return {
            "detected": True,
            "is_cat": False,
            "menh_star": menh_star,
            "target_star": target_star,
            "target_palace": target_palace,
            "sat_in_target": sorted(sat_in_target),
            "has_ki": has_ki_in_target,
            "paradigm": (
                f"⚠ '{quy_tac}' — {menh_star} tọa Mệnh + {target_star} "
                f"({target_palace}) XẤU (có {', '.join(sat_in_target) or 'Hóa Kỵ'}). "
                f"Sách Trung Châu Q2 p81: dù {menh_star} bản thân không gặp "
                f"sát, vẫn bị {target_star} kéo xấu → tham lam ti tiện, "
                f"không chủ kiến, phản ứng sai lầm."
            ),
        }
    if is_target_tot:
        return {
            "detected": True,
            "is_cat": True,
            "menh_star": menh_star,
            "target_star": target_star,
            "target_palace": target_palace,
            "cat_in_target": sorted(cat_in_target),
            "paradigm": (
                f"✅ '{quy_tac}' — {menh_star} tọa Mệnh + {target_star} "
                f"({target_palace}) TỐT (có cát: {', '.join(cat_in_target)}). "
                f"Sách Trung Châu Q2 p81: hai sao cộng hưởng → quản lý tài "
                f"chính tốt + công minh trợ giúp tha nhân + uy lực phát huy."
            ),
        }

    return {
        "detected": True,
        "is_cat": True,
        "is_neutral": True,
        "menh_star": menh_star,
        "target_star": target_star,
        "target_palace": target_palace,
        "paradigm": (
            f"🌓 '{quy_tac}' — {menh_star} Mệnh + {target_star} "
            f"({target_palace}) KHÔNG xấu cũng KHÔNG đặc biệt cát. Không "
            f"kéo {menh_star} vào trạng thái xấu."
        ),
    }


# ─── Q54 + Q57: từ thâm nhuần vòng 6-8 Trung Châu Q2 (2026-06-08) ──

def _Q54_khong_kiep_doi_xung_menh(la_so: dict) -> dict[str, Any]:
    """Q54: Địa Không + Địa Kiếp đối xung Mệnh (Thiên Di) HOẶC đồng cung Mệnh
    → lúc nhỏ tuổi bất lợi, không được cha mẹ che chở, đau yếu/nghèo khó.

    Sách Trung Châu Q2 p133 — Vương Đình Chỉ:
    'Địa Không, Địa Kiếp đồng độ thủ Mệnh, hoặc ĐỐI XUNG, phần nhiều chủ về
    lúc còn nhỏ tuổi bất lợi, không được cha mẹ che chở, hay đau yếu, nghèo
    khó, hoặc nhiều tai ách.'

    Anh confirm 2026-06-08: 'lúc nhỏ nhà nghèo, xa cha mẹ từ 10 tuổi,
    không có khó khăn lớn' → ỨNG phần nghèo + xa cha mẹ.
    """
    menh_idx = _palace_index(la_so, "Mệnh")
    if menh_idx is None:
        return {"detected": False, "paradigm": "Không tìm thấy cung Mệnh"}

    sat_tinh = la_so.get("sat_tinh", {}) or {}
    khong_idx = sat_tinh.get("Địa Không")
    kiep_idx = sat_tinh.get("Địa Kiếp")
    if khong_idx is None or kiep_idx is None:
        return {"detected": False, "paradigm": "Lá số không có Địa Không/Địa Kiếp"}

    # Trường hợp 1: đồng cung Mệnh
    if khong_idx == menh_idx and kiep_idx == menh_idx:
        return {
            "detected": True,
            "is_cat": False,
            "configuration": "đồng cung Mệnh",
            "paradigm": (
                "⚠ Địa Không + Địa Kiếp ĐỒNG CUNG MỆNH — sách Trung Châu Q2 p133: "
                "lúc nhỏ tuổi bất lợi nặng — không cha mẹ che chở + đau yếu + "
                "nghèo khó. Hậu thiên cần phấn đấu để vượt qua."
            ),
        }

    # Trường hợp 2: đối xung Mệnh (cùng cung Thiên Di)
    doi_idx = _fix(menh_idx + 6)
    if khong_idx == doi_idx and kiep_idx == doi_idx:
        return {
            "detected": True,
            "is_cat": False,
            "configuration": "đối xung Mệnh (Thiên Di)",
            "paradigm": (
                "⚠ Địa Không + Địa Kiếp đồng cung Thiên Di ĐỐI XUNG Mệnh — "
                "sách Trung Châu Q2 p133: lúc nhỏ tuổi bất lợi — phần nhiều "
                "nhà nghèo / xa cha mẹ sớm / hay đau yếu. Paradigm ứng đặc "
                "biệt với chuyển cung lúc bé (làm con nuôi, học nội trú, "
                "xa nhà). Hậu thiên có thể vượt qua nhờ nỗ lực."
            ),
        }

    return {
        "detected": False,
        "paradigm": "Địa Không + Địa Kiếp không đồng cung Mệnh và không đối xung"
    }


def _Q57_da_la_cung_luc_than(la_so: dict) -> dict[str, Any]:
    """Q57: Đà La tại cung lục thân → tính chất ÂM Ỉ KÉO DÀI của Đà La.

    Sách Trung Châu Q2 p126-p127 — Vương Đình Chỉ:
    - Đà La thủ cung Phu Thê → kết hôn MUỘN
    - Đà La thủ cung Tử Tức → CHẬM CÓ CON
    - Đà La (mở rộng) thủ Huynh Đệ → bất hòa hoặc xa cách anh chị em
      (Đà La âm ỉ kéo dài → quan hệ dây dưa, không công khai xung đột)

    Anh confirm 2026-06-08: 'chị em ở xa, ít qua lại' — ỨNG Đà La Huynh Đệ.
    """
    sat_tinh = la_so.get("sat_tinh", {}) or {}
    da_la_idx = sat_tinh.get("Đà La")
    if da_la_idx is None:
        return {"detected": False, "paradigm": "Lá số không có Đà La"}

    # Tìm cung Đà La đang ở
    da_la_palace = None
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == da_la_idx:
            da_la_palace = p.get("name", "")
            break

    paradigms_by_palace = {
        "Phu Thê": "⚠ Đà La tại Phu Thê → kết hôn MUỘN (Trung Châu Q2 p127)",
        "Tử Tức": "⚠ Đà La tại Tử Tức → CHẬM CÓ CON (Trung Châu Q2 p127)",
        "Huynh Đệ": (
            "⚠ Đà La tại Huynh Đệ → anh chị em xa cách / ít qua lại / âm ỉ "
            "không công khai bất hòa (mở rộng paradigm Trung Châu Q2 p127: "
            "Đà La 'dây dưa kéo dài' áp dụng cho cung lục thân)"
        ),
        "Phụ Mẫu": (
            "⚠ Đà La tại Phụ Mẫu → quan hệ với cha mẹ dây dưa, có khoảng "
            "cách tâm lý kéo dài"
        ),
        "Nô Bộc": (
            "⚠ Đà La tại Nô Bộc → người dưới quyền hoặc bạn bè dây dưa, "
            "khó dứt khoát"
        ),
        "Giao Hữu": (
            "⚠ Đà La tại Giao Hữu → bạn bè dây dưa, khó dứt khoát"
        ),
    }

    if da_la_palace in paradigms_by_palace:
        return {
            "detected": True,
            "is_cat": False,
            "palace": da_la_palace,
            "paradigm": paradigms_by_palace[da_la_palace],
        }
    return {
        "detected": False,
        "palace": da_la_palace,
        "paradigm": f"Đà La tại {da_la_palace} (không phải cung lục thân)",
    }


# ─── Q71 + Q72: từ vòng 10 Trung Châu Q2 (2026-06-08, Anh confirm 2/2) ──

def _Q71_pha_toai_tai_tinh(la_so: dict) -> dict[str, Any]:
    """Q71: Phá Toái đồng cung với tài tinh (Vũ Khúc / Thiên Phủ / Thái Âm
    / Lộc Tồn / chính tinh Hóa Lộc) → làm yếu tài khí.

    Sách Trung Châu Q2 p150: 'Phá Toái đồng độ với các sao tiền tài chủ về
    làm yếu tài khí, có chút tiền ắt cũng phải hao tốn một phần.'

    Anh confirm 2026-06-08: 'đúng' — Phá Toái + Thiên Phủ Tài Bạch Sửu.
    """
    sao_le = la_so.get("sao_le", {}) or {}
    pha_toai_idx = sao_le.get("Phá Toái")
    if pha_toai_idx is None:
        return {"detected": False, "paradigm": "Lá số không có Phá Toái"}

    # Stars at Phá Toái cung
    stars = _stars_at_branch_idx(la_so, pha_toai_idx)
    chinh = set(stars["chinh_tinh"])
    sat = set(stars["sat_tinh"])

    # Tài tinh: Vũ Khúc, Thiên Phủ, Thái Âm (chính tinh) + Lộc Tồn (sat_tinh)
    TAI_CHINH = {"Vũ Khúc", "Thiên Phủ", "Thái Âm"}
    has_tai_chinh = TAI_CHINH & chinh
    has_loc_ton = "Lộc Tồn" in sat

    # Chính tinh Hóa Lộc
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    loc_star = tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")
    has_hoa_loc_chinh = bool(loc_star) and loc_star in chinh

    detected = bool(has_tai_chinh or has_loc_ton or has_hoa_loc_chinh)
    if not detected:
        return {
            "detected": False,
            "paradigm": "Phá Toái không đồng cung tài tinh"
        }

    # Tìm cung của Phá Toái
    pha_palace = None
    for p in la_so.get("palaces", []):
        if p.get("branch_index") == pha_toai_idx:
            pha_palace = p.get("name", "")
            break

    parts = []
    if has_tai_chinh: parts.append(f"tài tinh {', '.join(sorted(has_tai_chinh))}")
    if has_loc_ton: parts.append("Lộc Tồn")
    if has_hoa_loc_chinh: parts.append(f"{loc_star} Hóa Lộc")

    return {
        "detected": True,
        "is_cat": False,
        "palace": pha_palace,
        "paradigm": (
            f"⚠ Phá Toái đồng cung tại {pha_palace} với {', '.join(parts)} — "
            f"sách Trung Châu Q2 p150: 'làm yếu tài khí, có chút tiền ắt "
            f"cũng phải hao tốn một phần'. Cần kỷ luật tài chính + đầu tư "
            f"dài hạn để giữ tài lộc, tránh tiêu vặt + đầu cơ rủi ro."
        ),
    }


def _Q72_phuong_cac_menh(la_so: dict) -> dict[str, Any]:
    """Q72: Long Trì + Phượng Các tại các CUNG TRỌNG YẾU (Mệnh / Phụ Mẫu /
    Phúc Đức / Sự Nghiệp / Tài Bạch) → phong thái + tài nghệ.

    Sách Trung Châu Q2 p147: 'Long Trì-Phượng Các chủ về thanh quý (sang
    quý thanh cao) mà KHÔNG phải phú quý, cũng chủ về nghệ thuật, kiến
    trúc, xây dựng.' Đôi mạnh nhất; lẻ vẫn có ý nghĩa.

    Mỗi cung có paradigm khác nhau:
    - Mệnh: phong thái cá nhân
    - Phụ Mẫu: cha mẹ có phong thái nghệ thuật
    - Phúc Đức: thiên hướng nghệ thuật
    - Sự Nghiệp / Tài Bạch: thu hoạch nhờ tài nghệ

    Anh: Phượng Các Phụ Mẫu Ngọ (LẺ, Long Trì Huynh Đệ Thìn).
    """
    sao_q2 = la_so.get("sao_q2", {}) or {}
    pc_idx = sao_q2.get("Phượng Các")
    lt_idx = sao_q2.get("Long Trì")
    if pc_idx is None and lt_idx is None:
        return {"detected": False, "paradigm": "Lá số không có Long Trì/Phượng Các"}

    # Map cung index → tên
    palace_by_idx = {p.get("branch_index"): p.get("name", "") for p in la_so.get("palaces", [])}

    TRONG_YEU = {"Mệnh", "Phụ Mẫu", "Phúc Đức", "Sự Nghiệp", "Quan Lộc", "Tài Bạch"}

    pc_palace = palace_by_idx.get(pc_idx, "") if pc_idx is not None else ""
    lt_palace = palace_by_idx.get(lt_idx, "") if lt_idx is not None else ""

    notes = []
    is_doi = False
    if pc_idx == lt_idx and pc_palace in TRONG_YEU:
        is_doi = True
        notes.append(
            f"✅ Long Trì + Phượng Các ĐÔI tại {pc_palace} — thanh quý + "
            "tài nghệ MẠNH (Trung Châu Q2 p147)"
        )
    else:
        if pc_palace in TRONG_YEU:
            paradigm_map = {
                "Mệnh": "phong thái văn nhã + thiên hướng nghệ thuật / khéo léo (cá nhân)",
                "Phụ Mẫu": "cha mẹ có phong thái nghệ thuật + thẩm mỹ",
                "Phúc Đức": "tâm hồn thiên về nghệ thuật + nét tinh tế",
                "Sự Nghiệp": "sự nghiệp liên quan nghệ thuật / kiến trúc / thẩm mỹ",
                "Quan Lộc": "sự nghiệp liên quan nghệ thuật / kiến trúc / thẩm mỹ",
                "Tài Bạch": "tài lộc nhờ tài nghệ / nghệ thuật",
            }
            notes.append(f"✅ Phượng Các LẺ tại {pc_palace} → {paradigm_map[pc_palace]}")
        if lt_palace in TRONG_YEU and lt_palace != pc_palace:
            paradigm_map_lt = {
                "Mệnh": "phong thái long trọng + thanh quý",
                "Phụ Mẫu": "cha mẹ phong thái long trọng",
                "Phúc Đức": "tâm hồn long trọng, thanh quý",
                "Sự Nghiệp": "sự nghiệp được quý nhân biểu dương",
                "Quan Lộc": "sự nghiệp được quý nhân biểu dương",
                "Tài Bạch": "tài lộc nhờ vinh dự",
            }
            notes.append(f"✅ Long Trì LẺ tại {lt_palace} → {paradigm_map_lt[lt_palace]}")

    if not notes:
        return {
            "detected": False,
            "paradigm": (
                f"Long Trì ({lt_palace}) + Phượng Các ({pc_palace}) "
                "không ở cung trọng yếu (Mệnh / Phụ Mẫu / Phúc Đức / "
                "Sự Nghiệp / Tài Bạch)"
            ),
        }
    return {
        "detected": True,
        "is_cat": True,
        "doi_cap": is_doi,
        "pc_palace": pc_palace,
        "lt_palace": lt_palace,
        "paradigm": " · ".join(notes) + (
            ". Sách Trung Châu Q2 p147: 'thanh quý chứ KHÔNG phú quý' — "
            "thiên về nghệ thuật, kiến trúc, xây dựng."
        ),
    }


# ─── Q101-Q103: CHƯƠNG CỐT cho lá số anh — §4.4 Tử Vi Mão/Dậu ──

def _Q101_thien_tuong_ty_hoi_menh(la_so: dict) -> dict[str, Any]:
    """Q101 ⭐⭐⭐: Thiên Tướng độc tọa Mệnh Tỵ HOẶC Hợi = "ỔN NHẤT trong 12 cung".

    Sách Trung Châu Q2 p347 — Vương Đình Chỉ:
    'Thiên Tướng độc tọa ở hai cung Tỵ hoặc Hợi, là ỔN NHẤT trong 12 cung.
    Có tính rất kiên nhẫn, lại giàu sức khai sáng; chỉ cần Thiên Tướng
    KHÔNG thuộc Hình Kỵ Giáp Ấn, thông thường đều có tính chất tốt lành.'

    Đặc tính khác: thiếu tính độc lập, khó tự làm chủ.
    Phân biệt 2 loại:
    - "Có sức khai sáng": có sao Lộc đồng cung HOẶC Liêm Hóa Lộc Sửu/Mùi
    - "Nhờ người khác thành việc": không có sao Lộc khai sáng
    """
    pal_menh = _stars_at_named_palace(la_so, "Mệnh")
    chinh_menh = set(pal_menh["chinh_tinh"])
    if "Thiên Tướng" not in chinh_menh or len(chinh_menh) != 1:
        return {"detected": False, "paradigm": "Mệnh không phải Thiên Tướng độc tọa"}

    menh_idx = _palace_index(la_so, "Mệnh")
    if menh_idx is None:
        return {"detected": False, "paradigm": "Không tìm thấy cung Mệnh"}

    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    menh_branch = BR[menh_idx]
    if menh_branch not in ("Tỵ", "Hợi"):
        return {
            "detected": False,
            "paradigm": f"Thiên Tướng Mệnh ở {menh_branch} (không phải Tỵ/Hợi)"
        }

    # Check sao Lộc đồng cung Thiên Tướng (Lộc Tồn hoặc Hóa Lộc của chính tinh khác)
    sat = set(pal_menh["sat_tinh"])
    phu = set(pal_menh["phu_tinh"])
    has_loc_ton = "Lộc Tồn" in sat
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    loc_star = tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")
    has_chinh_hoa_loc = bool(loc_star) and loc_star in chinh_menh

    has_khai_sang = has_loc_ton or has_chinh_hoa_loc

    # Check Liêm Hóa Lộc tại Sửu/Mùi (Phúc Đức) — paradigm cao nhất
    pal_phuc = _stars_at_named_palace(la_so, "Phúc Đức")
    liem_hoa_loc_phuc = (
        "Liêm Trinh" in pal_phuc["chinh_tinh"] and
        loc_star == "Liêm Trinh"
    )

    parts = [
        f"✅ **Thiên Tướng độc tọa Mệnh {menh_branch}** — sách Trung Châu Q2 "
        f"p347: 'ỔN NHẤT trong 12 cung', có TÍNH KIÊN NHẪN + GIÀU SỨC KHAI "
        f"SÁNG."
    ]
    if has_loc_ton:
        parts.append("✅ Có Lộc Tồn đồng cung → CÓ SỨC KHAI SÁNG (sao Lộc hỗ trợ Tướng).")
    if has_chinh_hoa_loc:
        parts.append(f"✅ {loc_star} Hóa Lộc đồng cung Mệnh → CÓ SỨC KHAI SÁNG.")
    if liem_hoa_loc_phuc:
        parts.append("✅ Liêm Trinh Hóa Lộc tại Phúc Đức (Sửu/Mùi) → cách KHAI SÁNG TỐI ĐA.")
    if not (has_khai_sang or liem_hoa_loc_phuc):
        parts.append(
            "⚠ KHÔNG có sao Lộc khai sáng (Lộc Tồn đồng cung HOẶC Liêm "
            "Hóa Lộc Sửu/Mùi) → thuộc loại 'NHỜ NGƯỜI KHÁC thành việc'. "
            "Cần dựa vào trợ lực để thành công."
        )

    parts.append(
        "Lưu ý: Thiên Tướng = 'ấn tinh' → thiếu tính độc lập, dễ phải nhờ "
        "trợ lực để tự chủ. Q40 'Phùng Tướng khán Phủ' đã xét Phủ tốt → "
        "không kéo Tướng vào xấu."
    )

    return {
        "detected": True,
        "is_cat": True,
        "menh_branch": menh_branch,
        "has_loc_ton": has_loc_ton,
        "has_chinh_hoa_loc": has_chinh_hoa_loc,
        "has_khai_sang": has_khai_sang or liem_hoa_loc_phuc,
        "paradigm": " · ".join(parts),
    }


def _Q103_tu_tham_mao_dau_phu_the(la_so: dict) -> dict[str, Any]:
    """Q103 ⭐⭐⭐: Tử-Tham Phu Thê Mão/Dậu = TINH HỆ THUẦN DỤC VỌNG.

    Sách Trung Châu Q2 p336 — Vương Đình Chỉ:
    'Tử-Tham đồng độ Mão/Dậu thuộc loại THUẦN DỤC VỌNG. Bản thân Tử-Tham
    có dục vọng + Vũ-Phá hội (Thiên Di) cũng ham muốn vật chất mạnh, chỉ
    có Liêm-Thất hội (Phúc Đức) đôi khi thiên về tình cảm.'

    Phân biệt VẬT CHẤT vs DỤC TÌNH:
    - Tham Hóa Lộc + Vũ/Phá Hóa Lộc + phụ tinh = VẬT CHẤT
    - Thiên Diêu đồng cung + đào hoa hội = DỤC TÌNH
    - Xương-Khúc đồng cung = tăng DỤC TÌNH

    Anh: Tử-Tham Phu Thê Mão + Tham Hóa Lộc → VẬT CHẤT
    + Hàm Trì Dậu đối Mão (hội Tam Phương Tứ Chính) → có yếu tố DỤC TÌNH NHẸ
    """
    pal_phu = _stars_at_named_palace(la_so, "Phu Thê")
    chinh_phu = set(pal_phu["chinh_tinh"])

    if not ({"Tử Vi", "Tham Lang"}.issubset(chinh_phu)):
        return {"detected": False, "paradigm": "Phu Thê không có Tử-Tham đồng cung"}

    # Check vị trí Mão/Dậu
    phu_idx = _palace_index(la_so, "Phu Thê")
    if phu_idx is None:
        return {"detected": False, "paradigm": "Không tìm thấy cung Phu Thê"}
    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    phu_branch = BR[phu_idx]
    if phu_branch not in ("Mão", "Dậu"):
        return {"detected": False, "paradigm": f"Tử-Tham tại {phu_branch} (không phải Mão/Dậu)"}

    # Phân biệt vật chất vs dục tình
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    has_tham_hoa_loc = (tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")) == "Tham Lang"

    # Đào hoa đồng cung Phu Thê
    q2 = set(pal_phu["sao_q2"])
    DAO_HOA = {"Hồng Loan", "Thiên Hỉ", "Hàm Trì", "Đại Hao đào hoa", "Thiên Diêu", "Mộc Dục"}
    dao_hoa_dong = DAO_HOA & q2

    # Đào hoa TAM PHƯƠNG TỨ CHÍNH (đối cung)
    doi_idx = _fix(phu_idx + 6)
    doi_stars = _stars_at_branch_idx(la_so, doi_idx)
    doi_q2 = set(doi_stars["sao_q2"])
    dao_hoa_doi = DAO_HOA & doi_q2

    # Xương-Khúc đồng cung Phu Thê
    phu_tinh = set(pal_phu["phu_tinh"])
    xuong_khuc_dong = {"Văn Xương", "Văn Khúc"} & phu_tinh

    # Verdict
    vat_chat_factors = []
    duc_tinh_factors = []
    if has_tham_hoa_loc:
        vat_chat_factors.append("Tham Lang Hóa Lộc")
    if dao_hoa_dong:
        duc_tinh_factors.append(f"đào hoa đồng cung ({', '.join(dao_hoa_dong)})")
    if dao_hoa_doi:
        duc_tinh_factors.append(f"đào hoa đối cung Tam Phương hội ({', '.join(dao_hoa_doi)})")
    if xuong_khuc_dong:
        duc_tinh_factors.append(f"Xương-Khúc đồng cung ({', '.join(xuong_khuc_dong)})")

    # Mức độ
    score_vat_chat = len(vat_chat_factors)
    score_duc_tinh = len(duc_tinh_factors)

    if score_vat_chat > score_duc_tinh:
        nature = "nghiêng VẬT CHẤT"
        is_cat = True
    elif score_duc_tinh > score_vat_chat:
        nature = "nghiêng DỤC TÌNH"
        is_cat = False
    else:
        nature = "QUÂN BÌNH vật chất + dục tình"
        is_cat = None

    parts = [
        f"🌐 **Phu Thê {phu_branch} = Tử Vi + Tham Lang** — sách Trung Châu "
        f"Q2 p336: TINH HỆ THUẦN DỤC VỌNG (Tử-Tham + Vũ-Phá Thiên Di + "
        f"Liêm-Thất Phúc Đức đều có sắc thái dục)."
    ]
    if vat_chat_factors:
        parts.append(f"📊 Vật chất: {', '.join(vat_chat_factors)}")
    if duc_tinh_factors:
        parts.append(f"💃 Dục tình: {', '.join(duc_tinh_factors)}")
    parts.append(f"→ Bản chất: **{nature}**")
    parts.append(
        "Đặc tính bạn đời (Tử-Tham): CHỦ ĐỘNG, tích cực, có thể quyết liệt "
        "để đạt mục đích (sách: 'thậm chí vì mục đích mà không từ thủ đoạn')."
    )

    return {
        "detected": True,
        "is_cat": is_cat,
        "phu_branch": phu_branch,
        "nature": nature,
        "vat_chat_factors": vat_chat_factors,
        "duc_tinh_factors": duc_tinh_factors,
        "paradigm": " · ".join(parts),
    }


# ─── Q105 + Q106: từ vòng 17 §4.4.5 + §4.4.4 (Anh confirm 2/2 nuanced) ──

def _Q105_liem_that_phuc_duc_hung_tu(la_so: dict) -> dict[str, Any]:
    """Q105 ⭐⭐: Liêm-Thất tại Phúc Đức Mùi/Sửu → "Hùng Tú Kiển Nguyên Cách"
    phấn chấn vs cương bạo.

    Sách Trung Châu Q2 p358 — Vương Đình Chỉ:
    "Liêm-Thất ở MÙI + cát tinh (Văn Xương, Văn Khúc) + Lộc Tồn/Hóa Lộc +
    KHÔNG tứ sát (Tử/Phủ/Không/Kiếp) → 'PHẤN CHẤN' — trải qua gian khổ
    thành đại nghiệp. Ngược lại 'CƯƠNG BẠO' — lục thân lạnh nhạt, nạn tai,
    bôn ba vất vả."

    Anh confirm 2026-06-08: "đúng" — Liêm-Thất Phúc Đức Mùi + Tả-Hữu đôi
    + Hữu Bật Hóa Khoa, NHƯNG thiếu Xương-Khúc + Lộc Tồn → PHẤN CHẤN
    không đầy đủ (gian khổ thành quả nhưng không đại nghiệp tột bậc).
    """
    pal = _stars_at_named_palace(la_so, "Phúc Đức")
    chinh = set(pal["chinh_tinh"])
    if not {"Liêm Trinh", "Thất Sát"}.issubset(chinh):
        return {"detected": False, "paradigm": "Phúc Đức không có Liêm-Thất đồng cung"}

    phuc_idx = _palace_index(la_so, "Phúc Đức")
    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    phuc_branch = BR[phuc_idx] if phuc_idx is not None else ""

    if phuc_branch not in ("Sửu", "Mùi"):
        return {"detected": False, "paradigm": f"Liêm-Thất Phúc Đức tại {phuc_branch} (không Sửu/Mùi)"}

    # Check yếu tố PHẤN CHẤN (4 yếu tố)
    phu_tinh = set(pal["phu_tinh"])
    sat = set(pal["sat_tinh"])
    pos = []   # yếu tố tích cực
    neg = []   # yếu tố tiêu cực / thiếu

    # 1. Tại Mùi (anh có) → cách Mùi tốt hơn Sửu
    if phuc_branch == "Mùi":
        pos.append("Mùi (cách Hùng Tú Kiển Nguyên tại Mùi)")
    else:
        neg.append("Sửu (kém Mùi)")

    # 2. Xương-Khúc tại Phúc Đức
    has_xuong_khuc = bool({"Văn Xương", "Văn Khúc"} & phu_tinh)
    if has_xuong_khuc:
        pos.append(f"Văn Xương/Khúc tại Phúc Đức ({', '.join({'Văn Xương','Văn Khúc'} & phu_tinh)})")
    else:
        neg.append("THIẾU Văn Xương/Khúc")

    # 3. Lộc Tồn / Hóa Lộc tại Phúc Đức
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    loc_star = tu_hoa.get("Lộc") or tu_hoa.get("Hóa Lộc")
    has_loc_ton = "Lộc Tồn" in sat
    has_hoa_loc_phuc = bool(loc_star) and loc_star in (chinh | phu_tinh | set(pal["sao_q2"]))
    if has_loc_ton or has_hoa_loc_phuc:
        pos.append("Lộc Tồn/Hóa Lộc tại Phúc Đức")
    else:
        neg.append("THIẾU Lộc Tồn/Hóa Lộc tại Phúc Đức")

    # 4. KHÔNG Tử/Phủ/Không/Kiếp tại Phúc Đức
    has_tu_sat = bool({"Địa Không", "Địa Kiếp"} & sat) or bool({"Tử Vi", "Thiên Phủ"} & chinh)
    if not has_tu_sat:
        pos.append("KHÔNG Không/Kiếp tại Phúc Đức")
    else:
        neg.append("CÓ Không/Kiếp tại Phúc Đức")

    # Bonus: Tả-Hữu đôi (Hữu Bật Hóa Khoa)
    has_ta_huu_doi = {"Tả Phù", "Hữu Bật"}.issubset(phu_tinh)
    if has_ta_huu_doi:
        pos.append("Tả-Hữu ĐÔI")

    # Verdict
    score_pos = len(pos)
    score_neg = len(neg)
    n_neg_critical = sum(1 for n in neg if "THIẾU" in n or "CÓ Không/Kiếp" in n)

    if score_neg == 0:
        verdict = "✅ HÙNG TÚ KIỂN NGUYÊN ĐẦY ĐỦ"
        is_cat = True
        outcome = "trải qua gian khổ thành ĐẠI NGHIỆP TỘT BẬC"
    elif n_neg_critical >= 3:
        verdict = "⚠ CƯƠNG BẠO"
        is_cat = False
        outcome = "lục thân lạnh nhạt, nạn tai, bôn ba vất vả"
    else:
        verdict = "🌓 PHẤN CHẤN KHÔNG ĐẦY ĐỦ"
        is_cat = True
        outcome = "trải qua gian khổ thành quả, NHƯNG KHÔNG đại nghiệp tột bậc"

    parts = [
        f"{verdict} — Liêm-Thất Phúc Đức {phuc_branch} (sách Trung Châu Q2 p358)",
        f"✅ Có: {', '.join(pos)}" if pos else "",
        f"⚠ Thiếu: {', '.join(neg)}" if neg else "",
        f"→ Outcome: {outcome}",
    ]
    return {
        "detected": True,
        "is_cat": is_cat,
        "verdict": verdict,
        "pos": pos,
        "neg": neg,
        "paradigm": " · ".join(p for p in parts if p),
    }


def _Q106_thien_luong_ngo_phu_mau(la_so: dict) -> dict[str, Any]:
    """Q106 ⭐: Thiên Lương Phụ Mẫu Ngọ → "lục thân khắc nhẹ" (refined).

    Sách Trung Châu Q2 p352 — Vương Đình Chỉ:
    "Thiên Lương Ngọ tất sẽ mang tính 'cô độc và hình khắc' vì Thái Dương
    đối cung Tý lạc hãm. Quan hệ lục thân không cát tường."

    Anh confirm 2026-06-08: "chị cả rất quan tâm, chị 2 thì bình thường,
    ai cũng bận cả" → KHÔNG phải hình khắc tuyệt đối. Em REFINE paradigm:
    KHÔNG đoạn tuyệt, NHƯNG quan hệ thường ngày không gắn bó sâu sắc.
    """
    pal = _stars_at_named_palace(la_so, "Phụ Mẫu")
    chinh = set(pal["chinh_tinh"])
    if "Thiên Lương" not in chinh:
        return {"detected": False, "paradigm": "Phụ Mẫu không có Thiên Lương"}

    phu_mau_idx = _palace_index(la_so, "Phụ Mẫu")
    BR = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    pm_branch = BR[phu_mau_idx] if phu_mau_idx is not None else ""
    if pm_branch not in ("Tý", "Ngọ"):
        return {
            "detected": False,
            "paradigm": f"Thiên Lương Phụ Mẫu {pm_branch} (không Tý/Ngọ)"
        }

    if pm_branch == "Tý":
        return {
            "detected": True,
            "is_cat": True,
            "paradigm": (
                "✅ Thiên Lương Phụ Mẫu Tý — Thái Dương đối Ngọ nhập miếu "
                "→ DUNG HÒA. Quan hệ với cha mẹ + anh chị em ấm áp."
            ),
        }

    # Ngọ — "cô độc hình khắc"
    sat = set(pal["sat_tinh"])
    has_kinh = "Kình Dương" in sat
    return {
        "detected": True,
        "is_cat": False,
        "paradigm": (
            f"⚠ Thiên Lương Phụ Mẫu Ngọ"
            + (" + Kình Dương" if has_kinh else "")
            + " — sách Trung Châu Q2 p352: 'cô độc và hình khắc' vì Thái "
            "Dương đối cung Tý lạc hãm. **Refined cho anh** (confirm 2026-"
            "06-08): KHÔNG đoạn tuyệt — có thể có người quan tâm (chị cả "
            "của anh), nhưng quan hệ thường ngày KHÔNG gắn bó sâu sắc, "
            "'ai cũng bận'. Bổ sung Q54 'xa cha mẹ từ 10 tuổi'."
        ),
    }


def chiem_phu_the_v3(la_so: dict) -> dict[str, Any]:
    """Engine v3 — v2 (9 quy luật) + Q10-Q106 (15→26 quy luật).

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
        # Từ vòng 2 thâm nhuần Trung Châu Q2 (2026-06-08, Anh confirm)
        "22_sao_doi_cap_3_cung": _Q22_sao_doi_cap_3_cung(la_so),
        "23_vu_pha_ty_hoi_nong_nay": _Q23_vu_pha_ty_hoi_nong_nay(la_so),
        "24_vu_pha_sat_thien_di": _Q24_vu_pha_sat_thien_di_tai_nan(la_so),
        # Từ vòng 3+4+5 thâm nhuần Trung Châu Q2 (2026-06-08, Anh confirm 3/3)
        "29_tham_lang_chi_nam_tam_hop": _Q29_tham_lang_vuong_chi_nam_tam_hop(la_so),
        "35_thien_tuong_menh_giap_cuc": _Q35_thien_tuong_menh_giap_cuc(la_so),
        "40_phung_phu_khan_tuong": _Q40_phung_phu_khan_tuong(la_so),
        # Từ vòng 6+7+8 thâm nhuần Trung Châu Q2 (2026-06-08, Anh confirm 2/3)
        "54_khong_kiep_doi_xung_menh": _Q54_khong_kiep_doi_xung_menh(la_so),
        "57_da_la_cung_luc_than": _Q57_da_la_cung_luc_than(la_so),
        # Từ vòng 9+10+11 thâm nhuần Trung Châu Q2 (2026-06-08, Anh confirm 2/2)
        "71_pha_toai_tai_tinh": _Q71_pha_toai_tai_tinh(la_so),
        "72_phuong_cac_menh": _Q72_phuong_cac_menh(la_so),
        # Từ vòng 16 CHƯƠNG CỐT lá số anh — §4.4 Tử Vi Mão/Dậu (2026-06-08)
        "101_thien_tuong_ty_hoi_menh": _Q101_thien_tuong_ty_hoi_menh(la_so),
        "103_tu_tham_mao_dau_phu_the": _Q103_tu_tham_mao_dau_phu_the(la_so),
        # Từ vòng 17 CHƯƠNG CỐT (Anh confirm 2/2, Q106 refined)
        "105_liem_that_hung_tu_kien_nguyen": _Q105_liem_that_phuc_duc_hung_tu(la_so),
        "106_thien_luong_ngo_phu_mau": _Q106_thien_luong_ngo_phu_mau(la_so),
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

    # Q14-57 (mới): có is_cat flag → phân loại rõ
    for key in ("14_phuc_duc_combo_canh_bao", "15_ta_huu_phuc_duc",
                "16_khoi_viet_phuc_duc", "17_cat_hoa_phuc_duc",
                "18_menh_thien_tuong_co_doc",
                "19_tu_vi_phu_the_tai_da_co_quan",
                "20_thai_duong_ham_sinh_dem",
                "21_thien_co_thai_am_tu_tuc",
                "22_sao_doi_cap_3_cung",
                "23_vu_pha_ty_hoi_nong_nay",
                "24_vu_pha_sat_thien_di",
                "29_tham_lang_chi_nam_tam_hop",
                "35_thien_tuong_menh_giap_cuc",
                "40_phung_phu_khan_tuong",
                "54_khong_kiep_doi_xung_menh",
                "57_da_la_cung_luc_than",
                "71_pha_toai_tai_tinh",
                "72_phuong_cac_menh",
                "101_thien_tuong_ty_hoi_menh",
                "103_tu_tham_mao_dau_phu_the",
                "105_liem_that_hung_tu_kien_nguyen",
                "106_thien_luong_ngo_phu_mau"):
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
