"""Chiêm cung Phu Thê — PERSONALIZE filter cho từng dòng paradigm.

Mỗi dòng paradigm trong seed JSON (data/seeds/tuvi_cung_phu_the_trung_chau.json)
có thể là:
- ALWAYS_APPLY: luôn áp dụng cho cặp Sao×Vị_trí (vd `to_hop`, `phan_loai`, `co_ban`)
- CONDITIONAL: chỉ áp dụng nếu lá số có điều kiện phụ thoả (vd `voi_xuong_khuc`,
  `voi_liem_trinh_hoa_ki`, `voi_phu_ta`, `voi_sat`, `voi_dao_hoa`...)
- GENDER-CONDITIONAL: chỉ áp dụng theo giới tính (`nam_*`, `nu_*`)

Module này provide `personalize_paradigm()` trả về `matched` + `unmatched`:
- matched: list dòng đã pass điều kiện + reason + sách citation
- unmatched: list dòng KHÔNG pass (giữ lại để UI show "paradigm chung")

Source paradigm: Trung Châu Tử Vi Đẩu Số 2 (Vương Đình Chỉ), section 5.3
"""
from __future__ import annotations
from typing import Any

# ─── Star groups ──────────────────────────────────────────────
LUC_CAT = {"Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"}
TA_HUU = {"Tả Phù", "Hữu Bật"}
# Engine an_sao output dùng "Tả Phù" — KHÔNG phải "Tả Phụ"
XUONG_KHUC = {"Văn Xương", "Văn Khúc"}
KHOI_VIET = {"Thiên Khôi", "Thiên Việt"}

LUC_SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}
KINH_DA = {"Kình Dương", "Đà La"}
HOA_LINH = {"Hỏa Tinh", "Linh Tinh"}
KHONG_KIEP = {"Địa Không", "Địa Kiếp"}

DAO_HOA = {"Hồng Loan", "Thiên Hỉ", "Hàm Trì", "Đại Hao", "Thiên Diêu", "Mộc Dục"}

LOC_TON = "Lộc Tồn"
THIEN_MA = "Thiên Mã"
THIEN_HINH = "Thiên Hình"

CAT_HOA = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"}  # 3 hoá cát
TU_HOA_ALL = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"}

# ─── Keys luôn áp dụng (không phụ thuộc sao phụ) ──────────────
ALWAYS_APPLY: set[str] = {
    "to_hop", "phan_loai", "tinh_chat", "co_ban", "y_nghia",
    "cung_menh", "cung_han_ung_nghiem", "tuoi_tac",
    "khuyen", "khuyen_tuoi", "case_founder",
    "ham_muon_vat_chat", "duc_tinh",
    "doc_toa", "doi_cung", "diem_chot",
    "tai_hon", "khong_nen_tai_hon",
    "nghe_nghiep_giai_quyet", "tinh_chat",
    "luu_y", "luu_y_nam",
    "thuong_thuong", "tam_trang_hoa_nang",
    "hach_dia", "thien_la_dia_vong",
    "qua_cuong", "qua_nhu", "vo_tinh", "huu_tinh",
    "mao_de_sinh_ly", "mao_doi_thien_dong", "mao_uu_dau",
    "tai_hoi", "tai_hoi_vo_xau",
    "ty_tot_ngo", "ty_uu_hoi", "ty_kem_hoi",
    "ngo", "suu_tot", "mui_xau", "tuat_uu_thin", "tuat_cat_+_khong_sat",
    "dau_xau_mao", "nam_lay_vo_dep",
    "khong_kho_lo_kho_trong",
    "tai_ty_vo_dep",  # vị trí-specific
    "can_co", "can_co_loc", "can_cuong_nhu_tuong_te",
    "can_loc_quyen_khoa_du", "can_sao_loc",
    "cat", "hung", "hung_nang", "cat_canh_bao", "canh_bao",
    "ki",
    "cat_hoa", "cat_hoa_phu_ta", "cat_hoa_phu_duc_khong_cat",  # treat as conditional? see below
    "hoa_quyen_+_khong_xuong_khuc_dao_hoa",
    "ban_dem_sinh_nu_menh_hoa_ki",  # gender + time specific — coarse always
    "voi_bach_quan_trieu_cung",  # cấu trúc tổng quát
    "ưu_tinh",
}

# ─── Gender-conditional keys ──────────────────────────────────
GENDER_MALE_KEYS = {
    "nam_menh_cat", "nam_menh_sat_ki", "nam_uu", "nam_uu_nu",
    "nam_30+",
    "vu_khuc_hoa_ki_nam", "vu_khuc_hoa_loc_nam",
    "hoi_voi_sat_hoa_ki_nam",
    "voi_sao_le_phu_ta_+_dao_hoa_nam",
}
GENDER_FEMALE_KEYS = {
    "nu_menh_cat", "nu_menh_sat_ki", "nu_menh_cam", "nu_uu",
    "nu_bat_hoa_gia_dinh_chong",
    "vu_khuc_hoa_ki_nu",
    "ty_voi_sat_hoa_ki_nu_menh_dai_han_tu_vi_thien_phu",
}


def _stars_in(la_so: dict, palace_name: str) -> dict[str, set[str]]:
    """Lookup tất cả sao trong 1 cung tên — return dict các set."""
    from .chiem_phu_the import _find_palace, _stars_at_branch_idx
    pal = _find_palace(la_so, palace_name)
    if not pal:
        return {"chinh_tinh": set(), "phu_tinh": set(), "sat_tinh": set(), "sao_q2": set()}
    s = _stars_at_branch_idx(la_so, pal["branch_index"])
    return {k: set(s.get(k, [])) for k in ("chinh_tinh", "phu_tinh", "sat_tinh", "sao_q2")}


def _all_stars_in_palace(la_so: dict, palace_name: str) -> set[str]:
    s = _stars_in(la_so, palace_name)
    return s["chinh_tinh"] | s["phu_tinh"] | s["sat_tinh"] | s["sao_q2"]


def _star_at_palace(la_so: dict, star: str, palace_name: str) -> bool:
    """1 sao có ở 1 cung không?"""
    return star in _all_stars_in_palace(la_so, palace_name)


def _hoa_of_star_in_palace(la_so: dict, star: str, palace_name: str, hoa: str) -> bool:
    """Sao X có Hóa Y NẰM TẠI cung palace_name?"""
    tu_hoa = la_so.get("tu_hoa", {}) or {}
    if (tu_hoa.get(hoa) or tu_hoa.get(f"Hóa {hoa}")) != star:
        return False
    return _star_at_palace(la_so, star, palace_name)


def _doi_cung_name(palace_name: str) -> str:
    """Tên đối cung."""
    pairs = {
        "Mệnh": "Thiên Di", "Thiên Di": "Mệnh",
        "Phụ Mẫu": "Tật Ách", "Tật Ách": "Phụ Mẫu",
        "Phúc Đức": "Tài Bạch", "Tài Bạch": "Phúc Đức",
        "Điền Trạch": "Tử Tức", "Tử Tức": "Điền Trạch",
        "Sự Nghiệp": "Phu Thê", "Quan Lộc": "Phu Thê",
        "Phu Thê": "Sự Nghiệp",
        "Huynh Đệ": "Nô Bộc", "Nô Bộc": "Huynh Đệ", "Giao Hữu": "Huynh Đệ",
    }
    return pairs.get(palace_name, "")


# ─── Tâm condition resolver ────────────────────────────────────
def check_condition(
    key: str,
    la_so: dict,
    gender: str,
    palace_name: str = "Phu Thê",
) -> tuple[bool, str]:
    """Return (applies, reason).

    `applies`: True nếu paradigm áp dụng cho lá số này
    `reason`: lời giải thích để show UI
    """
    # ─── 1. Always-apply keys ───────────────────────────────
    if key in ALWAYS_APPLY:
        return True, "paradigm chung cho cặp Sao × Vị trí"

    # ─── 2. Gender-conditional ──────────────────────────────
    if key in GENDER_MALE_KEYS:
        if gender == "nam":
            return True, "áp dụng vì lá số nam"
        return False, "chỉ áp dụng cho lá số nam"
    if key in GENDER_FEMALE_KEYS:
        if gender in ("nữ", "nu"):
            return True, "áp dụng vì lá số nữ"
        return False, "chỉ áp dụng cho lá số nữ"

    # ─── 3. Stars in palace ────────────────────────────────
    stars = _stars_in(la_so, palace_name)
    in_pal = stars["chinh_tinh"] | stars["phu_tinh"] | stars["sat_tinh"] | stars["sao_q2"]
    tu_hoa = la_so.get("tu_hoa", {}) or {}

    def has_hoa(star: str, hoa: str) -> bool:
        return tu_hoa.get(hoa) == star or tu_hoa.get(f"Hóa {hoa}") == star

    # voi_xuong_khuc: cần Văn Xương HOẶC Văn Khúc trong cung
    if key in ("voi_xuong_khuc",):
        if XUONG_KHUC & in_pal:
            return True, f"cung {palace_name} có {', '.join(XUONG_KHUC & in_pal)}"
        return False, f"cung {palace_name} không có Văn Xương/Văn Khúc"

    if key == "voi_xuong_khuc_dao_hoa":
        if (XUONG_KHUC & in_pal) and (DAO_HOA & in_pal):
            return True, "có Xương-Khúc + đào hoa"
        return False, "thiếu Xương-Khúc hoặc đào hoa"

    if key == "voi_xuong_khuc_+_dao_hoa_+_lien_trinh_hoa_ki":
        cond = (XUONG_KHUC & in_pal) and (DAO_HOA & in_pal) and has_hoa("Liêm Trinh", "Kỵ")
        return cond, ("đủ 3: Xương-Khúc + đào hoa + Liêm Trinh Hóa Kỵ"
                      if cond else "thiếu ≥1 trong: Xương-Khúc / đào hoa / Liêm Trinh Hóa Kỵ")

    # voi_phu_ta: Tả-Hữu
    if key in ("voi_phu_ta",):
        if TA_HUU & in_pal:
            return True, f"cung có {', '.join(TA_HUU & in_pal)}"
        return False, "không có Tả Phù/Hữu Bật trong cung"

    if key == "voi_sao_le_phu_ta":
        # phu-ta nhưng LẺ (1 trong 2)
        n = len(TA_HUU & in_pal)
        return (n == 1, f"có {n} sao đôi Tả-Hữu (1 lẻ = ứng paradigm)" if n == 1
                else f"có {n} sao Tả-Hữu, không lẻ")

    if key == "voi_sao_le_phu_ta_+_dao_hoa_nam":
        n = len(TA_HUU & in_pal)
        cond = n == 1 and (DAO_HOA & in_pal) and gender == "nam"
        return cond, ("nam mệnh có sao đôi lẻ + đào hoa" if cond
                      else "thiếu điều kiện sao lẻ + đào hoa + nam mệnh")

    # voi_cat_tinh / voi_cat / cat_voi_cat_tinh: cát tinh trong cung
    if key in ("voi_cat_tinh", "voi_cat", "cat_voi_cat_tinh"):
        if LUC_CAT & in_pal:
            return True, f"có lục cát: {', '.join(LUC_CAT & in_pal)}"
        return False, "không có lục cát trong cung"

    # voi_cat_hoa: Hóa Lộc/Quyền/Khoa của sao chính
    if key in ("voi_cat_hoa", "voi_cat_hoa_+_cat_tinh"):
        # check có chính tinh trong cung được Hóa Lộc/Quyền/Khoa không
        chinh = stars["chinh_tinh"]
        for star in chinh:
            for hoa in ("Lộc", "Quyền", "Khoa"):
                if has_hoa(star, hoa):
                    extra_ok = True
                    if key == "voi_cat_hoa_+_cat_tinh":
                        extra_ok = bool(LUC_CAT & in_pal)
                    if extra_ok:
                        return True, f"{star} Hóa {hoa} tại cung" + (
                            " + cát tinh" if key.endswith("cat_tinh") else "")
        return False, "không có chính tinh được Hóa Lộc/Quyền/Khoa" + (
            " (hoặc thiếu cát tinh)" if key.endswith("cat_tinh") else "")

    # voi_sat: lục sát
    if key in ("voi_sat",):
        if LUC_SAT & in_pal:
            return True, f"có lục sát: {', '.join(LUC_SAT & in_pal)}"
        return False, "không có lục sát trong cung"

    if key == "voi_sat_HOAC_sao_le":
        sat = bool(LUC_SAT & in_pal)
        le = (len(TA_HUU & in_pal) == 1) or (len(XUONG_KHUC & in_pal) == 1) or (len(KHOI_VIET & in_pal) == 1)
        return (sat or le, "có lục sát hoặc sao lẻ" if (sat or le) else "không có sát + không lẻ")

    if key in ("voi_sat_ki", "voi_sat_ki_hinh", "voi_sat_ki_trung_trung"):
        sat = bool(LUC_SAT & in_pal)
        chinh = stars["chinh_tinh"]
        has_ki = any(has_hoa(s, "Kỵ") and s in chinh for s in chinh)
        if key == "voi_sat_ki_hinh":
            cond = sat and has_ki and (THIEN_HINH in in_pal)
            return cond, ("có sát + Hóa Kỵ chính tinh + Thiên Hình"
                          if cond else "thiếu trong: sát / Hóa Kỵ / Thiên Hình")
        if key == "voi_sat_ki_trung_trung":
            n_sat = len(LUC_SAT & in_pal)
            n_ki = sum(1 for s in chinh if has_hoa(s, "Kỵ"))
            cond = n_sat >= 2 and n_ki >= 1
            return cond, (f"có {n_sat} sát + {n_ki} Hóa Kỵ (trùng trùng)"
                          if cond else f"có {n_sat} sát, {n_ki} Hóa Kỵ — chưa đủ trùng trùng")
        cond = sat and has_ki
        return cond, ("có lục sát + Hóa Kỵ chính tinh"
                      if cond else "thiếu sát hoặc Hóa Kỵ chính tinh")

    # voi_kinh_da: Kình Dương + Đà La
    if key == "voi_kinh_da":
        if KINH_DA & in_pal:
            return True, f"có {', '.join(KINH_DA & in_pal)}"
        return False, "không có Kình Dương/Đà La"
    if key == "voi_da_la":
        return ("Đà La" in in_pal,
                "có Đà La" if "Đà La" in in_pal else "không có Đà La")
    if key == "voi_da_la_+_kho_lo":
        # kho_lo = sao Khô Lộ ~ khó verify, treat as Đà La + Lộc Tồn
        cond = ("Đà La" in in_pal) and (LOC_TON in in_pal)
        return cond, ("có Đà La + Lộc Tồn (Kho Lộ)" if cond else "thiếu Đà La hoặc Lộc Tồn")
    if key == "voi_hoa_da":
        cond = ("Hỏa Tinh" in in_pal) and ("Đà La" in in_pal)
        return cond, ("có Hỏa Tinh + Đà La" if cond else "thiếu 1 trong 2")
    if key == "voi_hoa_linh":
        if HOA_LINH & in_pal:
            return True, f"có {', '.join(HOA_LINH & in_pal)}"
        return False, "không có Hỏa Tinh/Linh Tinh"
    if key == "voi_khong_kiep":
        if KHONG_KIEP & in_pal:
            return True, f"có {', '.join(KHONG_KIEP & in_pal)}"
        return False, "không có Địa Không/Địa Kiếp"
    if key == "voi_kinh_duong_hoa_linh_khong_kiep":
        bad = LUC_SAT & in_pal
        # cần ≥1 trong tập (Kình Dương, Hỏa, Linh, Không, Kiếp)
        target = {"Kình Dương", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"} & in_pal
        if target:
            return True, f"có {', '.join(target)}"
        return False, "không có Kình/Hỏa/Linh/Không/Kiếp"

    # voi_dao_hoa
    if key in ("voi_dao_hoa",):
        if DAO_HOA & in_pal:
            return True, f"có đào hoa: {', '.join(DAO_HOA & in_pal)}"
        return False, "không có đào hoa trong cung"
    if key == "voi_dao_hoa_+_kho_lo":
        cond = bool(DAO_HOA & in_pal) and (LOC_TON in in_pal)
        return cond, ("đào hoa + Lộc Tồn (Kho Lộ)" if cond else "thiếu đào hoa hoặc Lộc Tồn")
    if key == "voi_dao_hoa_+_sao_le":
        n_le = (len(TA_HUU & in_pal) == 1) + (len(XUONG_KHUC & in_pal) == 1) + (len(KHOI_VIET & in_pal) == 1)
        cond = bool(DAO_HOA & in_pal) and n_le > 0
        return cond, (f"đào hoa + {n_le} cặp lẻ" if cond else "thiếu đào hoa hoặc sao lẻ")
    if key == "voi_thien_dieu":
        return ("Thiên Diêu" in in_pal,
                "có Thiên Diêu" if "Thiên Diêu" in in_pal else "không có Thiên Diêu")
    if key == "voi_phiem_thuy_dao_hoa" or key == "phiem_thuy_dao_hoa":
        # Phiếm thuỷ đào hoa = Tham Lang + Đào Hoa (đặc biệt ở Tý/Hợi)
        cond = ("Tham Lang" in in_pal) and bool(DAO_HOA & in_pal)
        return cond, ("Tham Lang + đào hoa (phiếm thuỷ)" if cond
                      else "không phải phiếm thuỷ đào hoa")

    # voi_sao_le: bất kỳ cặp lẻ
    if key == "voi_sao_le":
        le_pairs = []
        if len(TA_HUU & in_pal) == 1: le_pairs.append("Tả-Hữu lẻ")
        if len(XUONG_KHUC & in_pal) == 1: le_pairs.append("Xương-Khúc lẻ")
        if len(KHOI_VIET & in_pal) == 1: le_pairs.append("Khôi-Việt lẻ")
        if le_pairs:
            return True, ", ".join(le_pairs)
        return False, "không có cặp sao lẻ"
    if key == "voi_sao_le_+_dao_hoa":
        n_le = (len(TA_HUU & in_pal) == 1) + (len(XUONG_KHUC & in_pal) == 1) + (len(KHOI_VIET & in_pal) == 1)
        cond = n_le > 0 and bool(DAO_HOA & in_pal)
        return cond, (f"có {n_le} cặp lẻ + đào hoa" if cond else "thiếu lẻ hoặc đào hoa")

    # Lộc Tồn / Thiên Mã
    if key == "voi_loc_ton_hoa_loc":
        chinh = stars["chinh_tinh"]
        has_chinh_loc = any(has_hoa(s, "Lộc") for s in chinh)
        cond = (LOC_TON in in_pal) and has_chinh_loc
        return cond, ("có Lộc Tồn + chính tinh Hóa Lộc (Song Lộc)"
                      if cond else "thiếu Lộc Tồn hoặc Hóa Lộc chính tinh")
    if key == "voi_loc_ton_thien_ma":
        cond = (LOC_TON in in_pal) and (THIEN_MA in in_pal)
        return cond, ("có Lộc Tồn + Thiên Mã (Lộc Mã giao trì)"
                      if cond else "thiếu Lộc Tồn hoặc Thiên Mã")
    if key == "voi_loc_ton_+_hoa_linh_giap":
        # complicated giáp — skip detailed
        cond = LOC_TON in in_pal and bool(HOA_LINH & in_pal)
        return cond, ("Lộc Tồn + Hỏa/Linh" if cond else "thiếu Lộc Tồn hoặc Hỏa/Linh")

    # Liêm Trinh family
    if key in ("voi_liem_trinh_hoa_loc",):
        cond = _hoa_of_star_in_palace(la_so, "Liêm Trinh", palace_name, "Lộc")
        return cond, ("Liêm Trinh Hóa Lộc tại cung" if cond
                      else f"Liêm Trinh không Hóa Lộc tại {palace_name}")
    if key in ("voi_liem_trinh_hoa_ki", "voi_lien_trinh_hoa_ki"):
        cond = _hoa_of_star_in_palace(la_so, "Liêm Trinh", palace_name, "Kỵ")
        return cond, ("Liêm Trinh Hóa Kỵ tại cung" if cond
                      else f"Liêm Trinh không Hóa Kỵ tại {palace_name}")
    if key in ("voi_lien_trinh_hoa_ki_doi", "voi_lien_trinh_hoa_ki_doi_cung", "lien_trinh_hoa_ki_doi"):
        doi = _doi_cung_name(palace_name)
        cond = bool(doi) and _hoa_of_star_in_palace(la_so, "Liêm Trinh", doi, "Kỵ")
        return cond, ("Liêm Trinh Hóa Kỵ tại đối cung " + doi if cond
                      else "đối cung không có Liêm Trinh Hóa Kỵ")
    if key == "lien_trinh_hoa_loc_doi":
        doi = _doi_cung_name(palace_name)
        cond = bool(doi) and _hoa_of_star_in_palace(la_so, "Liêm Trinh", doi, "Lộc")
        return cond, ("Liêm Trinh Hóa Lộc tại đối cung " + doi if cond
                      else "đối cung không có Liêm Trinh Hóa Lộc")
    if key == "voi_vu_khuc_hoa_ki_+_lien_trinh_hoa_ki":
        cond = has_hoa("Vũ Khúc", "Kỵ") and has_hoa("Liêm Trinh", "Kỵ")
        return cond, ("năm sinh có cả Vũ-Liêm Hóa Kỵ" if cond
                      else "thiếu Vũ Khúc hoặc Liêm Trinh Hóa Kỵ")

    # Thiên Đồng / Thái Âm / Thái Dương / Thiên Cơ / Cự Môn / Vũ Khúc / Tham Lang Hóa
    for star_keyword, star_name in [
        ("thien_dong", "Thiên Đồng"),
        ("thai_am", "Thái Âm"),
        ("thai_duong", "Thái Dương"),
        ("thien_co", "Thiên Cơ"),
        ("cu_mon", "Cự Môn"),
        ("vu_khuc", "Vũ Khúc"),
        ("tham_lang", "Tham Lang"),
    ]:
        if key == f"voi_{star_keyword}_hoa_ki":
            cond = has_hoa(star_name, "Kỵ")
            return cond, (f"{star_name} Hóa Kỵ năm sinh" if cond
                          else f"{star_name} không Hóa Kỵ")
        if key == f"{star_keyword}_hoa_ki":
            cond = has_hoa(star_name, "Kỵ")
            return cond, (f"{star_name} Hóa Kỵ năm sinh" if cond
                          else f"{star_name} không Hóa Kỵ")
        if key == f"voi_{star_keyword}_hoa_loc":
            cond = has_hoa(star_name, "Lộc")
            return cond, (f"{star_name} Hóa Lộc năm sinh" if cond
                          else f"{star_name} không Hóa Lộc")

    if key == "voi_thai_am_hoa_ki":
        cond = has_hoa("Thái Âm", "Kỵ")
        return cond, ("Thái Âm Hóa Kỵ năm sinh" if cond else "Thái Âm không Hóa Kỵ")
    if key == "voi_thai_am_hoa_loc":
        cond = has_hoa("Thái Âm", "Lộc")
        return cond, ("Thái Âm Hóa Lộc năm sinh" if cond else "Thái Âm không Hóa Lộc")

    if key in ("voi_hoa_ki",):
        chinh = stars["chinh_tinh"]
        ki_star = next((s for s in chinh if has_hoa(s, "Kỵ")), None)
        if ki_star:
            return True, f"{ki_star} (chính tinh) Hóa Kỵ tại cung"
        return False, "không có chính tinh Hóa Kỵ tại cung"

    if key == "voi_hoa_loc_quyen_ki":
        chinh = stars["chinh_tinh"]
        for star in chinh:
            for hoa in ("Lộc", "Quyền", "Kỵ"):
                if has_hoa(star, hoa):
                    return True, f"{star} Hóa {hoa}"
        return False, "không chính tinh nào Hóa Lộc/Quyền/Kỵ"

    if key == "voi_hoa_ki_hoa_loc_deu":
        chinh = stars["chinh_tinh"]
        has_loc = any(has_hoa(s, "Lộc") for s in chinh)
        has_ki = any(has_hoa(s, "Kỵ") for s in chinh)
        cond = has_loc and has_ki
        return cond, ("có cả Hóa Lộc + Hóa Kỵ tại cung" if cond
                      else "thiếu Hóa Lộc hoặc Hóa Kỵ")

    if key == "voi_hoa_loc_thin":
        # specific to vị trí Thìn
        chinh = stars["chinh_tinh"]
        has_loc = any(has_hoa(s, "Lộc") for s in chinh)
        return has_loc, ("có Hóa Lộc (paradigm Thìn)" if has_loc else "không Hóa Lộc")

    # voi_vu_khuc_hoa_ki_+_sat
    if key == "voi_vu_khuc_hoa_ki_+_sat":
        cond = has_hoa("Vũ Khúc", "Kỵ") and bool(LUC_SAT & in_pal)
        return cond, ("Vũ Khúc Hóa Kỵ + lục sát" if cond else "thiếu Vũ-Kỵ hoặc lục sát")

    # voi_tham_lang_hoa_loc_+_xuong_khuc_HOAC_dao_hoa
    if key == "voi_tham_lang_hoa_loc_+_xuong_khuc_HOAC_dao_hoa":
        loc = has_hoa("Tham Lang", "Lộc")
        xk_or_dh = bool(XUONG_KHUC & in_pal) or bool(DAO_HOA & in_pal)
        cond = loc and xk_or_dh
        return cond, ("Tham Lang Hóa Lộc + Xương-Khúc/đào hoa" if cond
                      else "thiếu Tham-Lộc hoặc Xương-Khúc/đào hoa")

    # voi_pha_quan_hoa_loc_+_hoa_linh_HOAC_sao_le
    if key == "voi_pha_quan_hoa_loc_+_hoa_linh_HOAC_sao_le":
        loc = has_hoa("Phá Quân", "Lộc")
        n_le = (len(TA_HUU & in_pal) == 1) + (len(XUONG_KHUC & in_pal) == 1) + (len(KHOI_VIET & in_pal) == 1)
        cond = loc and (bool(HOA_LINH & in_pal) or n_le > 0)
        return cond, ("Phá Quân Hóa Lộc + Hỏa-Linh/sao lẻ" if cond else "thiếu điều kiện")

    # voi_hoa_tham_linh_tham (paradigm Tử Vi + Thất Sát Tỵ/Hợi)
    if key == "voi_hoa_tham_linh_tham":
        cond = (
            ("Tham Lang" in in_pal)
            and (("Hỏa Tinh" in in_pal) or ("Linh Tinh" in in_pal))
        )
        return cond, ("có Tham Lang + Hỏa/Linh (Hỏa Tham/Linh Tham)" if cond
                      else "không có Hỏa Tham/Linh Tham")

    # voi_tu_tham_+_dao_hoa
    if key == "voi_tu_tham_+_dao_hoa":
        cond = ("Tử Vi" in in_pal) and ("Tham Lang" in in_pal) and bool(DAO_HOA & in_pal)
        return cond, ("Tử-Tham + đào hoa" if cond else "không phải Tử-Tham + đào hoa")

    # voi_thien_hinh_sao_khong
    if key == "voi_thien_hinh_sao_khong":
        cond = (THIEN_HINH in in_pal) and bool(KHONG_KIEP & in_pal)
        return cond, ("Thiên Hình + Không/Kiếp" if cond else "thiếu Thiên Hình hoặc Không/Kiếp")

    # voi_thien_tuong_tai_an_giap_an
    if key in ("voi_thien_tuong_tai_an_giap_an", "voi_tai_an_giap_an",
               "voi_tai_an_giap_an_+_xuong_hoa_ki"):
        # Cấu trúc giáp khó verify mà không có engine giáp — treat conservative as conditional
        return False, "cấu trúc Tài Ấm giáp Ấn — cần kiểm tra giáp cung riêng"

    # voi_hinh_ki_giap_an: Hình + Kỵ giáp
    if key == "voi_hinh_ki_giap_an":
        return False, "cấu trúc Hình Kỵ giáp Ấn — cần kiểm tra giáp cung riêng"

    # voi_loc_ton_+_hoa_linh_giap: Lộc Tồn + Hỏa Linh giáp
    if key == "doi_voi_tu_vi_pha_quan_+_ta_huu_giap":
        # Tử Vi Phá Quân + Tả Hữu giáp cung
        return False, "cấu trúc giáp Tả Hữu — cần kiểm tra giáp cung riêng"

    # voi_voi_thien_dong_hoa_ki_doi_+_sat
    if key == "voi_thien_dong_hoa_ki_doi_+_sat":
        doi = _doi_cung_name(palace_name)
        cond = bool(doi) and _hoa_of_star_in_palace(la_so, "Thiên Đồng", doi, "Kỵ") and bool(LUC_SAT & in_pal)
        return cond, ("Thiên Đồng Hóa Kỵ đối cung + sát" if cond else "thiếu điều kiện đối")
    if key == "voi_thien_dong_hoa_loc_doi_+_cat":
        doi = _doi_cung_name(palace_name)
        cond = bool(doi) and _hoa_of_star_in_palace(la_so, "Thiên Đồng", doi, "Lộc") and bool(LUC_CAT & in_pal)
        return cond, ("Thiên Đồng Hóa Lộc đối + cát tinh" if cond else "thiếu điều kiện")

    # ta_huu_xuong_khuc_chia_ra_2_cung — cross palace
    if key == "ta_huu_xuong_khuc_chia_ra_2_cung":
        # 1 cặp ở Phu Thê + cặp khác ở cung khác — đã wire v3 Q12; coarse always show as paradigm chung
        return True, "paradigm cross-bind (xem chi tiết Engine v3)"

    # ─── tuoi-tac / khuyen — non-conditional ─────────────────
    if key in ("khuyen", "khuyen_tuoi", "tuoi_tac", "tinh_chat", "y_nghia",
               "case_founder", "cung_han_ung_nghiem"):
        return True, "luôn áp dụng"

    # ─── đặc thù vị trí ──────────────────────────────────────
    # vd ki_da_la, ki_nhat, vu_khuc_hoa_ki_nam,...
    if key == "ki_da_la":
        return ("Đà La" in in_pal,
                "có Đà La" if "Đà La" in in_pal else "không có Đà La")
    if key == "ki_nhat":
        return True, "luôn áp dụng (paradigm chung)"

    if key == "vu_khuc_hoa_ki":
        cond = has_hoa("Vũ Khúc", "Kỵ")
        return cond, ("Vũ Khúc Hóa Kỵ" if cond else "Vũ Khúc không Hóa Kỵ")
    if key == "vu_khuc_hoa_quyen_loc":
        cond = has_hoa("Vũ Khúc", "Quyền") or has_hoa("Vũ Khúc", "Lộc")
        return cond, ("Vũ Khúc Hóa Quyền/Lộc" if cond else "Vũ Khúc không Hóa Quyền/Lộc")
    if key == "cu_mon_hoa_ki":
        cond = has_hoa("Cự Môn", "Kỵ")
        return cond, ("Cự Môn Hóa Kỵ" if cond else "Cự Môn không Hóa Kỵ")
    if key == "tuat_voi_cu_mon_hoa_ki":
        cond = has_hoa("Cự Môn", "Kỵ")
        return cond, ("Cự Môn Hóa Kỵ (paradigm Tuất)" if cond else "không")
    if key == "thin_voi_cu_mon_hoa_ki":
        cond = has_hoa("Cự Môn", "Kỵ")
        return cond, ("Cự Môn Hóa Kỵ (paradigm Thìn)" if cond else "không")
    if key == "thin_voi_hoa_loc_quyen_khoa":
        chinh = stars["chinh_tinh"]
        for star in chinh:
            for hoa in ("Lộc", "Quyền", "Khoa"):
                if has_hoa(star, hoa):
                    return True, f"{star} Hóa {hoa}"
        return False, "không có chính tinh Hóa Lộc/Quyền/Khoa"
    if key == "voi_cu_mon_hoa_ki":
        cond = has_hoa("Cự Môn", "Kỵ")
        return cond, ("Cự Môn Hóa Kỵ" if cond else "Cự Môn không Hóa Kỵ")
    if key == "phu_ta_dong_do_+_vu_phu_doi_cung_co_phu_ta":
        # Tả Hữu đồng độ + đối cung có Tả Hữu
        cond = len(TA_HUU & in_pal) == 2
        return cond, ("Tả-Hữu đồng độ" if cond else "Tả-Hữu không đồng độ")

    if key == "hoi_+_thai_am_hoa_ki":
        return (has_hoa("Thái Âm", "Kỵ"),
                "Thái Âm Hóa Kỵ" if has_hoa("Thái Âm", "Kỵ") else "Thái Âm không Hóa Kỵ")
    if key == "hoi_+_sat_ki":
        chinh = stars["chinh_tinh"]
        has_ki = any(has_hoa(s, "Kỵ") for s in chinh)
        cond = bool(LUC_SAT & in_pal) and has_ki
        return cond, ("có sát + Hóa Kỵ" if cond else "thiếu sát hoặc Hóa Kỵ")
    if key == "dau_+_thien_dong_hoa_ki_+_dao_hoa_+_sao_le":
        cond = (
            has_hoa("Thiên Đồng", "Kỵ")
            and bool(DAO_HOA & in_pal)
            and ((len(TA_HUU & in_pal) == 1)
                 or (len(XUONG_KHUC & in_pal) == 1)
                 or (len(KHOI_VIET & in_pal) == 1))
        )
        return cond, ("đủ Đồng-Kỵ + đào hoa + sao lẻ" if cond else "thiếu điều kiện")

    if key == "khong_nen_thien_dong_lien_trinh_that_sat_dai_van":
        # đại vận specific — luôn show là cảnh báo
        return True, "cảnh báo đại vận (luôn áp dụng nếu có đại vận tương ứng)"

    # ─── fallback: nếu chứa "hoa_ki" → conditional; ngược lại always
    if "hoa_ki" in key:
        return False, f"key chưa map — coi như conditional (chưa pass)"

    # Fallback safe: nếu không match pattern → coi là paradigm chung
    return True, "paradigm chung (key chưa có condition riêng)"


def personalize_vi_tri_paradigm(
    vi_tri_data: dict[str, Any],
    la_so: dict,
    gender: str,
    palace_name: str = "Phu Thê",
) -> dict[str, list[dict[str, Any]]]:
    """Filter từng key trong vi_tri data → return matched + unmatched.

    Args:
        vi_tri_data: dict từ seed JSON, vd {"to_hop":"Tử-Tham","voi_xuong_khuc":"..."}
        la_so: full lá số dict
        gender: "nam" | "nữ"
        palace_name: cung đang luận (default Phu Thê)

    Returns:
        {
            "matched": [{key, label, text, reason}],
            "unmatched": [{key, label, text, reason}],
        }
    """
    matched, unmatched = [], []
    for key, text in vi_tri_data.items():
        if not isinstance(text, str):
            continue  # skip nested
        applies, reason = check_condition(key, la_so, gender, palace_name)
        entry = {
            "key": key,
            "label": _humanize_key(key),
            "text": text,
            "reason": reason,
        }
        (matched if applies else unmatched).append(entry)
    return {"matched": matched, "unmatched": unmatched}


_LABEL_MAP = {
    "to_hop": "Tổ hợp",
    "phan_loai": "Phân loại",
    "ham_muon_vat_chat": "Hướng vật chất",
    "duc_tinh": "Hướng dục tình",
    "voi_xuong_khuc": "Khi có Xương–Khúc",
    "voi_phu_ta": "Khi có Tả–Hữu",
    "voi_cat_tinh": "Khi có lục cát",
    "cat_voi_cat_tinh": "Khi gặp cát tinh",
    "voi_cat_hoa": "Khi có cát Hóa",
    "voi_cat_hoa_+_cat_tinh": "Khi cát Hóa + cát tinh",
    "voi_sat": "Khi gặp lục sát",
    "voi_sat_ki": "Khi gặp sát + Hóa Kỵ",
    "voi_hoa_linh": "Khi gặp Hỏa–Linh",
    "voi_kinh_da": "Khi gặp Kình–Đà",
    "voi_khong_kiep": "Khi gặp Không–Kiếp",
    "voi_dao_hoa": "Khi có đào hoa",
    "voi_thien_dieu": "Khi có Thiên Diêu",
    "voi_sao_le": "Khi có sao đôi LẺ",
    "voi_sao_le_phu_ta": "Khi Tả–Hữu LẺ",
    "voi_hoa_ki": "Khi chính tinh Hóa Kỵ",
    "voi_liem_trinh_hoa_loc": "Khi Liêm Trinh Hóa Lộc",
    "voi_liem_trinh_hoa_ki": "Khi Liêm Trinh Hóa Kỵ",
    "voi_lien_trinh_hoa_ki": "Khi Liêm Trinh Hóa Kỵ",
    "voi_thai_am_hoa_ki": "Khi Thái Âm Hóa Kỵ",
    "voi_thai_am_hoa_loc": "Khi Thái Âm Hóa Lộc",
    "voi_thien_co_hoa_ki": "Khi Thiên Cơ Hóa Kỵ",
    "voi_cu_mon_hoa_ki": "Khi Cự Môn Hóa Kỵ",
    "voi_vu_khuc_hoa_ki_+_lien_trinh_hoa_ki": "Vũ-Liêm cùng Hóa Kỵ",
    "voi_vu_khuc_hoa_ki_+_sat": "Vũ-Kỵ + sát",
    "voi_loc_ton_hoa_loc": "Lộc Tồn + Hóa Lộc (Song Lộc)",
    "voi_loc_ton_thien_ma": "Lộc Tồn + Thiên Mã",
    "voi_hoa_tham_linh_tham": "Hỏa Tham / Linh Tham",
    "voi_tu_tham_+_dao_hoa": "Tử-Tham + đào hoa",
    "voi_tham_lang_hoa_loc_+_xuong_khuc_HOAC_dao_hoa": "Tham-Lộc + Xương-Khúc/đào hoa",
    "voi_pha_quan_hoa_loc_+_hoa_linh_HOAC_sao_le": "Phá-Lộc + Hỏa-Linh/sao lẻ",
    "voi_xuong_khuc_dao_hoa": "Xương-Khúc + đào hoa",
    "voi_xuong_khuc_+_dao_hoa_+_lien_trinh_hoa_ki": "Xương-Khúc + đào hoa + Liêm-Kỵ",
    "voi_thien_hinh_sao_khong": "Thiên Hình + Không-Kiếp",
    "voi_thai_am_hoa_ki": "Thái Âm Hóa Kỵ",
    "voi_bach_quan_trieu_cung": "Khi có Bách Quan Triều Củng",
    "voi_sao_le_phu_ta_+_dao_hoa_nam": "Nam mệnh — Tả-Hữu lẻ + đào hoa",
    "co_ban": "Cơ bản",
    "tinh_chat": "Tính chất",
    "y_nghia": "Ý nghĩa",
    "cung_menh": "Liên quan cung Mệnh",
    "cung_han_ung_nghiem": "Cung hạn ứng nghiệm",
    "tuoi_tac": "Tuổi tác",
    "khuyen": "Lời khuyên",
    "khuyen_tuoi": "Khuyên tuổi tác",
    "case_founder": "Áp dụng riêng lá số",
    "doc_toa": "Độc tọa",
    "doi_cung": "Đối cung",
    "tai_hon": "Khi tái hôn",
    "khong_nen_tai_hon": "Không nên tái hôn khi",
    "nu_menh_cat": "Nữ mệnh cát",
    "nu_menh_sat_ki": "Nữ mệnh sát-kỵ",
    "nu_menh_cam": "Nữ mệnh cấm kỵ",
    "nu_uu": "Nữ mệnh ưu tiên",
    "nu_bat_hoa_gia_dinh_chong": "Nữ — bất hoà gia đình chồng",
    "nam_menh_cat": "Nam mệnh cát",
    "nam_menh_sat_ki": "Nam mệnh sát-kỵ",
    "nam_uu": "Nam mệnh ưu tiên",
    "nam_uu_nu": "Nam mệnh / nữ ưu tiên",
    "nam_lay_vo_dep": "Nam lấy vợ đẹp",
    "luu_y": "Lưu ý",
    "luu_y_nam": "Lưu ý nam mệnh",
    "vu_khuc_hoa_ki_nam": "Nam — Vũ Khúc Hóa Kỵ",
    "vu_khuc_hoa_ki_nu": "Nữ — Vũ Khúc Hóa Kỵ",
    "vu_khuc_hoa_loc_nam": "Nam — Vũ Khúc Hóa Lộc",
    "hoi_voi_sat_hoa_ki_nam": "Nam — vị trí Hợi + sát-Kỵ",
    "ty_voi_sat_hoa_ki_nu_menh_dai_han_tu_vi_thien_phu": "Nữ — vị trí Tỵ + sát-Kỵ đại hạn",
    "cat": "Cát", "hung": "Hung", "hung_nang": "Hung nặng",
    "cat_canh_bao": "Cát kèm cảnh báo",
    "canh_bao": "Cảnh báo",
    "ki": "Kỵ",
    "diem_chot": "Điểm chốt",
    "qua_cuong": "Quá cương",
    "qua_nhu": "Quá nhu",
    "vo_tinh": "Vô tình",
    "huu_tinh": "Hữu tình",
    "thuong_thuong": "Bình thường",
    "tam_trang_hoa_nang": "Tâm trạng (hóa nặng)",
    "tinh_chat": "Tính chất",
}


def _humanize_key(key: str) -> str:
    if key in _LABEL_MAP:
        return _LABEL_MAP[key]
    # snake_case → Title Case Vietnamese
    return key.replace("_", " ").replace("+", "+").title()
