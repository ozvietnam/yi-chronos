"""Build `la_so_input` (per-palace canonical) từ lá số thô cast_la_so → cho match cách cục +
đại vận hiện tại + render 3-layer. Tách từ api/tu_vi_3layer.render_from_birth để engine (Chân Dung)
dùng chung mà KHÔNG gọi API. (Dedup debt: api/tu_vi_3layer còn bản inline — gom về đây sau.)
"""
from __future__ import annotations

IDX_TO_CHI = ["ty", "suu", "dan", "mao", "thin", "ti", "ngo", "mui", "than", "dau", "tuat", "hoi"]

STAR_VI_TO_CANON = {
    "Tử Vi": "tu_vi", "Thiên Cơ": "thien_co", "Thái Dương": "thai_duong",
    "Vũ Khúc": "vu_khuc", "Thiên Đồng": "thien_dong", "Liêm Trinh": "liem_trinh",
    "Thiên Phủ": "thien_phu", "Thái Âm": "thai_am", "Tham Lang": "tham_lang",
    "Cự Môn": "cu_mon", "Thiên Tướng": "thien_tuong", "Thiên Lương": "thien_luong",
    "Thất Sát": "that_sat", "Phá Quân": "pha_quan",
}
PHU_SAT_VI_TO_CANON = {
    "Tả Phù": "ta_phu", "Tả Phụ": "ta_phu", "Hữu Bật": "huu_bat",
    "Văn Xương": "van_xuong", "Văn Khúc": "van_khuc",
    "Thiên Khôi": "thien_khoi", "Thiên Việt": "thien_viet",
    "Kình Dương": "kinh_duong", "Đà La": "da_la",
    "Hỏa Tinh": "hoa_tinh", "Linh Tinh": "linh_tinh",
    "Địa Không": "dia_khong", "Địa Kiếp": "dia_kiep", "Lộc Tồn": "loc_ton",
}
TU_HOA_TO_CANON = {"Lộc": "hoa_loc", "Quyền": "hoa_quyen", "Khoa": "hoa_khoa", "Kỵ": "hoa_ky"}
CHI_VI_TO_CANON = {
    "Tý": "ty", "Sửu": "suu", "Dần": "dan", "Mão": "mao", "Thìn": "thin",
    "Tỵ": "ti", "Ngọ": "ngo", "Mùi": "mui", "Thân": "than", "Dậu": "dau",
    "Tuất": "tuat", "Hợi": "hoi",
}
CAN_VI_TO_CANON = {
    "Giáp": "giap", "Ất": "at", "Bính": "binh", "Đinh": "dinh", "Mậu": "mau",
    "Kỷ": "ky", "Canh": "canh", "Tân": "tan", "Nhâm": "nham", "Quý": "quy",
}
CUC_NAME_TO_CANON = {
    "Thủy Nhị Cục": "thuy_nhi_cuc", "Mộc Tam Cục": "moc_tam_cuc",
    "Kim Tứ Cục": "kim_tu_cuc", "Thổ Ngũ Cục": "tho_ngu_cuc", "Hỏa Lục Cục": "hoa_luc_cuc",
}
VONG_VI_TO_CANON = {
    "Thái Tuế": "thai_tue", "Thiếu Dương": "thieu_duong", "Tang Môn": "tang_mon",
    "Thiếu Âm": "thieu_am", "Quan Phù": "quan_phu", "Tử Phù": "tu_phu",
    "Tuế Phá": "tue_pha", "Long Đức": "long_duc", "Bạch Hổ": "bach_ho",
    "Phúc Đức": "phuc_duc_sao", "Điếu Khách": "dieu_khach", "Trực Phù": "truc_phu",
    "Tướng Tinh": "tuong_tinh", "Phan An": "phan_an", "Tuế Dịch": "tue_dich",
    "Tức Thần": "tuc_than", "Hoa Cái": "hoa_cai", "Kiếp Sát": "kiep_sat",
    "Tai Sát": "tai_sat", "Thiên Sát": "thien_sat", "Chỉ Bối": "chi_boi",
    "Hàm Trì": "ham_tri", "Nguyệt Sát": "nguyet_sat", "Vong Thần": "vong_than",
    "Bác Sĩ": "bac_si", "Lực Sĩ": "luc_si", "Thanh Long": "thanh_long",
    "Tiểu Hao": "tieu_hao", "Tướng Quân": "tuong_quan", "Tấu Thư": "tau_thu",
    "Phi Liêm": "phi_liem", "Hỷ Thần": "hy_than", "Bệnh Phù": "benh_phu",
    "Đại Hao": "dai_hao", "Phục Binh": "phuc_binh",
    "Hồng Loan": "hong_loan", "Thiên Hỉ": "thien_hy", "Cô Thần": "co_than",
    "Quả Tú": "qua_tu", "Tam Thai": "tam_thai", "Bát Tọa": "bat_toa",
    "Thiên Khốc": "thien_khoc", "Thiên Hư": "thien_hu", "Long Trì": "long_tri",
    "Phượng Các": "phuong_cac", "Thiên Diêu": "thien_rieu",
    "Quốc Ấn": "quoc_an", "Đường Phù": "duong_phu", "Phá Toái": "pha_toai",
    "Lưu Hà": "luu_ha", "Thiên Y": "thien_y", "Thiên Hình": "thien_hinh",
    "Thiên Đức": "thien_duc", "Nguyệt Đức": "nguyet_duc", "Thiên Giải": "thien_giai",
    "Giải Thần": "giai_than", "Ân Quang": "an_quang", "Thai Phụ": "thai_phu",
    "Phong Cáo": "phong_cao", "Thiên Quan": "thien_quan", "Thiên Phúc": "thien_phuc",
    "Thiên Trù": "thien_tru", "Thiên Không": "thien_khong",
}
_PALACE_NAME_TO_CANON = {
    "Mệnh": "menh", "Huynh Đệ": "huynh_de", "Phu Thê": "phu_the", "Tử Tức": "tu_tuc",
    "Tài Bạch": "tai_bach", "Tật Ách": "tat_ach", "Thiên Di": "thien_di", "Nô Bộc": "no_boc",
    "Quan Lộc": "quan_loc", "Điền Trạch": "dien_trach", "Phúc Đức": "phuc_duc", "Phụ Mẫu": "phu_mau",
}


def build_la_so_input(ls: dict, gender: str, birth_year: int | None = None,
                      now_year: int | None = None) -> dict:
    """ls = output cast_la_so(_from_birth); gender 'nam'|'nữ'. Trả la_so_input (per-palace canonical)
    + dai_van_hien_tai (cần birth_year + now_year). Dùng cho match_named_cach_cucs + render_3_layer."""
    idx_to_function: dict[int, str] = {}
    for p in (ls.get("palaces") or []):
        fn = _PALACE_NAME_TO_CANON.get(p.get("name", ""))
        if fn is not None and p.get("branch_index") is not None:
            idx_to_function[p["branch_index"] % 12] = fn

    chinh_tinh_per_palace: dict[str, list[str]] = {}
    star_idx: dict[str, int] = {}
    for star_vi, idx in (ls.get("chinh_tinh") or {}).items():
        star = STAR_VI_TO_CANON.get(star_vi)
        if not star:
            continue
        star_idx[star] = idx % 12
        chi = IDX_TO_CHI[idx % 12]
        chinh_tinh_per_palace.setdefault(chi, []).append(star)
        fn = idx_to_function.get(idx % 12)
        if fn:
            chinh_tinh_per_palace.setdefault(fn, []).append(star)

    phu_tinh_per_palace: dict[str, list[str]] = {}
    for src_key in ("phu_tinh", "sat_tinh"):
        for star_vi, idx in (ls.get(src_key) or {}).items():
            star = PHU_SAT_VI_TO_CANON.get(star_vi)
            if star is None:
                continue
            star_idx[star] = idx % 12
            chi = IDX_TO_CHI[idx % 12]
            phu_tinh_per_palace.setdefault(chi, []).append(star)
            fn = idx_to_function.get(idx % 12)
            if fn:
                phu_tinh_per_palace.setdefault(fn, []).append(star)

    tu_hoa_summary: list[dict] = []
    for hoa_key, star_vi in (ls.get("tu_hoa") or {}).items():
        hoa = TU_HOA_TO_CANON.get(hoa_key)
        base = STAR_VI_TO_CANON.get(star_vi) or PHU_SAT_VI_TO_CANON.get(star_vi)
        if not hoa or base is None or base not in star_idx:
            continue
        idx = star_idx[base]
        chi = IDX_TO_CHI[idx]
        phu_tinh_per_palace.setdefault(chi, []).append(hoa)
        fn = idx_to_function.get(idx)
        if fn:
            phu_tinh_per_palace.setdefault(fn, []).append(hoa)
        tu_hoa_summary.append({"hoa": hoa, "star": base, "palace_chi": chi, "palace_fn": fn})

    vong_sao_per_palace: dict[str, list[str]] = {}
    for src_key in ("thai_tue_belt", "tuong_tinh_belt", "bac_si_belt", "sao_q2", "sao_le"):
        for star_vi, idx in (ls.get(src_key) or {}).items():
            star = VONG_VI_TO_CANON.get(star_vi)
            if star is None:
                continue
            chi = IDX_TO_CHI[idx % 12]
            if star not in vong_sao_per_palace.setdefault(chi, []):
                vong_sao_per_palace[chi].append(star)
    try:
        from engine.tu_vi.paradigm.trang_sinh import an_trang_sinh
        _cuc = CUC_NAME_TO_CANON.get(ls.get("cuc_name", ""), "thuy_nhi_cuc")
        _can = CAN_VI_TO_CANON.get(ls.get("year_stem", ""), str(ls.get("year_stem", "")).lower())
        for sao, chi in an_trang_sinh(_cuc, _can, "M" if gender == "nam" else "F").items():
            if sao not in vong_sao_per_palace.setdefault(chi, []):
                vong_sao_per_palace[chi].append(sao)
    except Exception:
        pass

    tuan_chi = [IDX_TO_CHI[i % 12] for i in (ls.get("tuan") or [])]
    triet_chi = [IDX_TO_CHI[i % 12] for i in (ls.get("triet") or [])]

    dai_van_hien_tai = None
    if now_year is not None and birth_year is not None:
        age_mu = now_year - int(birth_year) + 1
        cur = next((dv for dv in (ls.get("dai_van") or [])
                    if dv.get("start_age", 0) <= age_mu <= dv.get("end_age", 0)), None)
        if cur:
            idx = cur["branch_index"] % 12
            van_chi = IDX_TO_CHI[idx]
            dai_van_hien_tai = {
                "cycle_index": cur.get("cycle_index"), "chi": van_chi,
                "fn": idx_to_function.get(idx), "start_age": cur.get("start_age"),
                "end_age": cur.get("end_age"), "age_mu": age_mu,
                "stars": list(chinh_tinh_per_palace.get(van_chi, [])),
                "phu_tinh": list(phu_tinh_per_palace.get(van_chi, [])),
            }

    return {
        "menh_palace": CHI_VI_TO_CANON.get(ls.get("menh_branch", ""), str(ls.get("menh_branch", "")).lower()),
        "than_palace": CHI_VI_TO_CANON.get(ls.get("than_branch", ""), str(ls.get("than_branch", "")).lower()),
        "chinh_tinh_per_palace": chinh_tinh_per_palace,
        "phu_tinh_per_palace": phu_tinh_per_palace,
        "vong_sao_per_palace": vong_sao_per_palace,
        "tu_hoa": tu_hoa_summary,
        "tuan_chi": tuan_chi,
        "triet_chi": triet_chi,
        "dai_van_hien_tai": dai_van_hien_tai,
        "fn_to_chi": {fn: IDX_TO_CHI[idx] for idx, fn in idx_to_function.items()},
    }
