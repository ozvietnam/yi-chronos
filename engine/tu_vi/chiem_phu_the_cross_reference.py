"""Chiêm cung Phu Thê — CROSS-REFERENCE panel.

Thay thế disclaimer chung chung "Cần xem kèm: Mệnh, Phúc Đức, đại vận hiện
tại, Thái Dương/Thái Âm miếu hãm" bằng panel RENDER THỰC với data của lá số.

4 cross-references generated per chart:

1. cung_menh — sao + Hóa + ý nghĩa cross-Phu Thê
2. cung_phuc_duc — sao + Hóa + cảnh báo cross-bind (sách Trung Châu §5.3.6)
3. dai_van_hien_tai — đại vận đang trong + cung Phu Thê đại vận đang ở đâu
4. thai_duong_thai_am — miếu/hãm + ý nghĩa (nam mệnh: Thái Âm = vợ;
                          nữ mệnh: Thái Dương = chồng)

Source: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ) §5.3 + Quyển 4 phụ lục
"""
from __future__ import annotations
from datetime import date
from typing import Any

from .chiem_phu_the import _find_palace, _stars_at_branch_idx

_BRANCHES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
             "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]


# ─── Mệnh × Phu Thê paradigm ──────────────────────────────────
_MENH_X_PHU_THE = {
    "Tử Vi": "Mệnh Tử Vi → cần vợ/chồng có địa vị tương xứng — nếu Phu Thê yếu sẽ áp đảo",
    "Thiên Cơ": "Mệnh Thiên Cơ → tính suy nghĩ nhiều, vợ chồng dễ 'bằng mặt không bằng lòng' — Phu Thê cần sao đôi để đoàn tụ",
    "Thái Dương": "Mệnh Thái Dương (nam) → chủ động trong hôn nhân; (nữ) → có chồng nhiều tham vọng. Miếu = tốt, Hãm = áp lực",
    "Vũ Khúc": "Mệnh Vũ Khúc → 'cô độc + hình khắc' (sách) — cần vợ/chồng mềm, kết hôn muộn hoặc lệch tuổi để giảm xung",
    "Thiên Đồng": "Mệnh Thiên Đồng → cảm tính cao, vợ chồng dễ thân mật nhưng cũng dễ ủy mị nếu Phu Thê có sát",
    "Liêm Trinh": "Mệnh Liêm Trinh → đào hoa + lý trí; Phu Thê có Liêm Trinh Hóa Kỵ → cực kỳ bất lợi",
    "Thiên Phủ": "Mệnh Thiên Phủ → ổn định gia đạo; cần Phu Thê có cát hóa để duy trì",
    "Thái Âm": "Mệnh Thái Âm (nam) → tình cảm phong phú; (nữ) → ngôi nữ chủ. Miếu = đẹp, Hãm = ẩn ức",
    "Tham Lang": "Mệnh Tham Lang → đào hoa mạnh — Phu Thê cần Xương-Khúc / Tả-Hữu để giữ chân",
    "Cự Môn": "Mệnh Cự Môn → 'một đời chuốc điều tiếng' (sách) — tiếng thị phi ảnh hưởng quan hệ vợ chồng",
    "Thiên Tướng": "Mệnh Thiên Tướng → công minh, trợ giúp tha nhân; Phu Thê cần cát tinh hỗ trợ vì Tướng kỵ cô độc",
    "Thiên Lương": "Mệnh Thiên Lương → trưởng thượng, cần vợ/chồng nhỏ hơn (5-10 tuổi) để cân bằng",
    "Thất Sát": "Mệnh Thất Sát → bạo liệt; Phu Thê thường gặp sóng gió, kết hôn muộn tốt hơn",
    "Phá Quân": "Mệnh Phá Quân → thay đổi nhiều; Phu Thê dễ tái hôn — cần Hóa Lộc/Quyền hỗ trợ",
}


# ─── Phúc Đức × Phu Thê paradigm ──────────────────────────────
# Một số paradigm gender-conditional (xem mặc định kế bên).
_PHUC_X_PHU_THE = {
    # Liêm-Thất Phúc Đức + Tử-Tham Phu Thê — phân biệt nam/nữ theo Trung Châu Q2 §5.3.6 + V17
    ("Liêm Trinh", "Thất Sát"): {
        "nữ": (
            "⚠ Phúc Đức = Liêm-Thất → sách Trung Châu Q2 §5.3.6 (NỮ MỆNH cổ): "
            "'Liêm-Thất ở Phúc Đức + Tử-Tham ở Phu Thê → mệnh xướng kĩ'. "
            "HIỆN ĐẠI cho nữ: tâm lý dễ thiên ham muốn vật chất + tình dục lẫn lộn, "
            "cần kỷ luật bản thân + chọn chồng có nguyên tắc"
        ),
        "nam": (
            "⚖ Phúc Đức = Liêm-Thất + Tử-Tham Phu Thê (NAM MỆNH, Trung Châu Q2 V17 p358): "
            "phấn biệt 'PHẤN CHẤN' (Xương-Khúc + Lộc, không sát) vs 'CƯƠNG BẠO'. "
            "Tinh thần đa chiều — lý tưởng tinh thần + thực tế kiếm tiền song song. "
            "KHÔNG phải 'xướng kĩ' (paradigm đó chỉ nữ cổ)"
        ),
    },
    ("Tử Vi", "Phá Quân"): "Phúc Đức Tử-Phá → tâm bất an, dễ thay đổi quyết định hôn nhân",
    ("Thiên Cơ", "Cự Môn"): "Phúc Đức Cơ-Cự → suy nghĩ nhiều + tiếng thị phi → ảnh hưởng hoà thuận vợ chồng",
    ("Tham Lang",): "Phúc Đức có Tham Lang → đào hoa nội tâm → Phu Thê dễ có người thứ ba xen",
    ("Thái Âm",): "Phúc Đức có Thái Âm → tình cảm phong phú; Miếu = phúc đức tốt, Hãm = ẩn ức tâm lý",
    ("Vũ Khúc",): "Phúc Đức có Vũ Khúc → 'cô độc' (sách) → cần Phu Thê có sao đôi để bù",
}


# ─── Thái Dương / Thái Âm paradigm ─────────────────────────────
def _td_ta_paradigm(level: str, star: str, role: str) -> str:
    """role: 'spouse' (vợ/chồng) hoặc 'self' (bản thân)."""
    LABELS = {
        "miếu": "đắc thế",
        "vượng": "vượng",
        "đắc": "có lực",
        "bình": "bình thường",
        "lạc": "yếu",
        "hãm": "thấp/ẩn ức",
    }
    label = LABELS.get(level.lower() if level else "", "")
    if star == "Thái Âm":
        # Nam mệnh → Thái Âm chỉ vợ
        if role == "spouse":
            if level and level.lower() in ("miếu", "vượng", "đắc"):
                return f"Thái Âm {label} → VỢ có nét đẹp + tâm hồn phong phú, được trợ lực"
            return f"Thái Âm {label} → vợ có thể ẩn ức tình cảm, cần Anh chủ động lắng nghe"
    if star == "Thái Dương":
        if role == "spouse":
            if level and level.lower() in ("miếu", "vượng", "đắc"):
                return f"Thái Dương {label} → CHỒNG có sự nghiệp + danh vọng"
            return f"Thái Dương {label} → chồng vất vả + ít danh, cần kiên nhẫn"
        else:
            if level and level.lower() in ("miếu", "vượng", "đắc"):
                return f"Thái Dương {label} → Anh có khí dương đầy đủ → vợ chồng cân bằng"
            return f"Thái Dương {label} → khí dương của Anh yếu → cần vợ chủ động hỗ trợ"
    return f"{star} {label}"


def _compute_current_age(la_so: dict, birth_year: int | None = None) -> int | None:
    """Tính tuổi hiện tại (tuổi mụ) từ year sinh."""
    try:
        if not birth_year:
            birth_year = la_so.get("birth", {}).get("year") or la_so.get("birth_year")
        if birth_year:
            return date.today().year - int(birth_year) + 1
    except Exception:
        pass
    return None


def _find_current_dai_van(dv_list: list[dict], current_age: int | None) -> dict | None:
    if current_age is None:
        return None
    for dv in dv_list:
        if dv.get("start_age", 0) <= current_age <= dv.get("end_age", 999):
            return dv
    return None


def _has_hoa(la_so: dict, star: str, hoa: str) -> bool:
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    return tu_hoa.get(hoa) == star or tu_hoa.get(f"Hóa {hoa}") == star


def build_cross_reference(
    la_so: dict,
    gender: str = "nam",
    birth_year: int | None = None,
) -> dict[str, Any]:
    """Build personalized cross-reference panel for cung Phu Thê.

    Returns:
        {
            "cung_menh": {chinh_tinh, sat_tinh, phu_tinh, paradigm, hoa_in_menh, ...},
            "cung_phuc_duc": {...},
            "dai_van_hien_tai": {...},
            "thai_duong_thai_am": {td: {...}, ta: {...}, paradigm},
        }
    """
    from .mieu_vuong_ham import level_at, level_label

    out: dict[str, Any] = {}

    # ─── 1. Cung Mệnh ───────────────────────────────────────
    menh = _find_palace(la_so, "Mệnh")
    if menh:
        ms = _stars_at_branch_idx(la_so, menh["branch_index"])
        chinh = ms["chinh_tinh"]
        paradigms = [_MENH_X_PHU_THE[s] for s in chinh if s in _MENH_X_PHU_THE]
        # Hóa tại Mệnh
        hoa_in_menh = []
        tu_hoa = la_so.get("tu_hoa", {}) or {}
        for hoa_key in ("Lộc", "Quyền", "Khoa", "Kỵ"):
            star = tu_hoa.get(hoa_key) or tu_hoa.get(f"Hóa {hoa_key}")
            if star and (star in chinh or star in ms["phu_tinh"] or star in ms["sao_q2"]):
                hoa_in_menh.append(f"{star} Hóa {hoa_key}")
        out["cung_menh"] = {
            "branch": menh["branch"],
            "chinh_tinh": chinh,
            "phu_tinh": ms["phu_tinh"],
            "sat_tinh": ms["sat_tinh"],
            "sao_q2": ms["sao_q2"],
            "hoa_in_palace": hoa_in_menh,
            "paradigms": paradigms,
            "note": (
                f"Cung Mệnh = bản thân Anh. Tâm tính + cách xử của Anh ảnh hưởng "
                f"trực tiếp đến cung Phu Thê (tam hợp +4)."
            ),
        }

    # ─── 2. Cung Phúc Đức ───────────────────────────────────
    phuc = _find_palace(la_so, "Phúc Đức")
    if phuc:
        ps = _stars_at_branch_idx(la_so, phuc["branch_index"])
        chinh = ps["chinh_tinh"]
        paradigms = []
        # Match cặp đôi trước
        chinh_set = frozenset(chinh)
        gender_norm = "nữ" if gender in ("nu", "nữ") else "nam"
        for key_tuple, txt in _PHUC_X_PHU_THE.items():
            if set(key_tuple).issubset(chinh_set):
                # Gender-conditional: txt có thể là dict {"nam":..., "nữ":...} hoặc str
                if isinstance(txt, dict):
                    txt = txt.get(gender_norm) or txt.get("nam") or ""
                if txt:
                    paradigms.append(txt)
                break
        # Nếu không match cặp → match đơn
        if not paradigms:
            for s in chinh:
                if (s,) in _PHUC_X_PHU_THE:
                    val = _PHUC_X_PHU_THE[(s,)]
                    if isinstance(val, dict):
                        val = val.get(gender_norm) or val.get("nam") or ""
                    if val:
                        paradigms.append(val)

        # Sao đôi vs lẻ ở Phúc Đức → quan trọng cho Phu Thê (sách)
        TA_HUU = {"Tả Phù", "Hữu Bật"} & set(ps["phu_tinh"])
        XK = {"Văn Xương", "Văn Khúc"} & set(ps["phu_tinh"])
        KV = {"Thiên Khôi", "Thiên Việt"} & set(ps["phu_tinh"]) | (
            {"Thiên Khôi", "Thiên Việt"} & set(ps["sao_q2"]))
        sao_doi_notes = []
        for pair_name, pair in [("Tả-Hữu", TA_HUU), ("Xương-Khúc", XK), ("Khôi-Việt", KV)]:
            if len(pair) == 2:
                sao_doi_notes.append(f"✓ Có {pair_name} ĐÔI ở Phúc Đức → vợ chồng đoàn tụ")
            elif len(pair) == 1:
                sao_doi_notes.append(f"⚠ Có {pair_name} LẺ ở Phúc Đức → tái hôn / người thứ ba xen")

        hoa_in_phuc = []
        tu_hoa = la_so.get("tu_hoa", {}) or {}
        for hoa_key in ("Lộc", "Quyền", "Khoa", "Kỵ"):
            star = tu_hoa.get(hoa_key) or tu_hoa.get(f"Hóa {hoa_key}")
            if star and (star in chinh or star in ps["phu_tinh"] or star in ps["sao_q2"]):
                hoa_in_phuc.append(f"{star} Hóa {hoa_key}")

        # Cross-bind cảnh báo nặng: Văn Khúc Hóa Kỵ tại Phúc Đức
        canh_bao_cross = []
        if "Văn Khúc" in (ps["phu_tinh"] or []) and _has_hoa(la_so, "Văn Khúc", "Kỵ"):
            canh_bao_cross.append(
                "⚠ Văn Khúc Hóa Kỵ tại Phúc Đức → sách Trung Châu §5.3: "
                "rắc rối tình cảm cross-bind Phu Thê (đặc biệt nữ mệnh)"
            )
        if {"Địa Không", "Địa Kiếp"} & set(ps["sat_tinh"]):
            canh_bao_cross.append(
                "⚠ Có Địa Không/Kiếp tại Phúc Đức → sách: đả kích tinh thần, "
                "tâm lý hôn nhân bị ảnh hưởng (cross-bind Phu Thê)"
            )

        out["cung_phuc_duc"] = {
            "branch": phuc["branch"],
            "chinh_tinh": chinh,
            "phu_tinh": ps["phu_tinh"],
            "sat_tinh": ps["sat_tinh"],
            "sao_q2": ps["sao_q2"],
            "hoa_in_palace": hoa_in_phuc,
            "paradigms": paradigms,
            "sao_doi_notes": sao_doi_notes,
            "canh_bao_cross": canh_bao_cross,
            "note": (
                "Phúc Đức = đạo lý hôn nhân + tâm lý + phước báu vợ chồng. "
                "Sách Trung Châu §5.3.6 nói: 'Phúc Đức × Phu Thê là cặp cross-bind "
                "QUAN TRỌNG NHẤT' — phải xem kèm KHÔNG được bỏ."
            ),
        }

    # ─── 3. Đại vận hiện tại ─────────────────────────────────
    try:
        from .dai_van_luu_nien_phu_the import cung_phu_the_dai_van
        dv_list = cung_phu_the_dai_van(la_so)
        current_age = _compute_current_age(la_so, birth_year=birth_year)
        current_dv = _find_current_dai_van(dv_list, current_age)
        out["dai_van_hien_tai"] = {
            "current_age": current_age,
            "current_dai_van": current_dv,
            "all_dai_van": dv_list,
            "note": (
                f"Đại vận đại Phu Thê = cung Phu Thê DI ĐỘNG theo từng 10 năm. "
                f"Đại vận hiện tại của Anh (tuổi {current_age}) cho biết Phu Thê "
                f"đang chịu ảnh hưởng tinh hệ ở đâu — quyết định 'thời điểm' "
                f"ứng nghiệm cát/hung của cung Phu Thê gốc."
            ),
        }
    except Exception as e:
        out["dai_van_hien_tai"] = {"_error": str(e)}

    # ─── 4. Thái Dương / Thái Âm miếu hãm ────────────────────
    ct = la_so.get("chinh_tinh", {}) or {}
    td_idx = ct.get("Thái Dương")
    ta_idx = ct.get("Thái Âm")

    td_info = ta_info = None
    if td_idx is not None:
        td_branch = _BRANCHES[td_idx]
        td_level = level_at("Thái Dương", td_branch) or ""
        td_role = "spouse" if gender in ("nu", "nữ") else "self"
        td_info = {
            "branch": td_branch,
            "level": td_level,
            "level_label": level_label(td_level) if td_level else "",
            "paradigm": _td_ta_paradigm(td_level, "Thái Dương", td_role),
        }
    if ta_idx is not None:
        ta_branch = _BRANCHES[ta_idx]
        ta_level = level_at("Thái Âm", ta_branch) or ""
        ta_role = "spouse" if gender == "nam" else "self"
        ta_info = {
            "branch": ta_branch,
            "level": ta_level,
            "level_label": level_label(ta_level) if ta_level else "",
            "paradigm": _td_ta_paradigm(ta_level, "Thái Âm", ta_role),
        }
    out["thai_duong_thai_am"] = {
        "thai_duong": td_info,
        "thai_am": ta_info,
        "gender": gender,
        "note": (
            f"Sách Trung Châu §5.3: 'vợ chồng cần khí Dương-Âm hài hòa'. "
            f"{'Nam mệnh: Thái Âm chỉ vợ (xem miếu hãm Thái Âm)' if gender=='nam' else 'Nữ mệnh: Thái Dương chỉ chồng (xem miếu hãm Thái Dương)'}. "
            f"Sao kia đại diện khí cân bằng âm-dương của bản thân Anh."
        ),
    }

    return out
