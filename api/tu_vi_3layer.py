"""API endpoint render 3-Layer cho lá số bất kỳ.

POST /api/tu-vi/3-layer
Body: {
  "can": "mau", "chi": "thin",
  "menh_palace": "ty", "than_palace": "than",
  "cuc": "thuy_nhi_cuc", "gender": "M",
  "chinh_tinh_per_palace": {"ty": ["thien_dong"], ...}
}

Returns: {
  "lop_1_chuyen_ve_anh": str,
  "lop_2_vi_sao": str,
  "lop_3_sach_co": dict,
  "warnings": list,
  "metadata": dict
}

Built 2026-06-10 Phase C.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from engine.atomization.output_filler_v2 import render_3_layer

router = APIRouter(prefix="/api/tu-vi", tags=["tu-vi-3layer"])


class LaSoInput(BaseModel):
    can: str = Field(..., description="Can năm sinh canonical lowercase (vd: mau, giap)")
    chi: str = Field(..., description="Chi năm sinh canonical (vd: thin, ngo)")
    menh_palace: str = Field(..., description="Cung Mệnh (chi canonical, vd: ty)")
    than_palace: str = Field(..., description="Cung Thân (chi canonical)")
    cuc: str = Field("thuy_nhi_cuc", description="Cục Mệnh canonical")
    gender: str = Field("M", description="M or F")
    chinh_tinh_per_palace: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map cung chi → list chính tinh canonical (snake_case)"
    )


@router.post("/3-layer")
async def render_3_layer_api(la_so: LaSoInput) -> dict:
    """Render 3-Layer output cho 1 lá số bất kỳ."""
    return render_3_layer(la_so.dict())


class BirthInput(BaseModel):
    birth_datetime_local: str = Field(..., description="vd 1988-06-05T23:30")
    timezone: str = Field("Asia/Ho_Chi_Minh")
    gender: str = Field("nam", description="nam | nu")


# Index 0-11 → chi canonical
IDX_TO_CHI = ["ty", "suu", "dan", "mao", "thin", "ti", "ngo", "mui", "than", "dau", "tuat", "hoi"]

# Tên sao tiếng Việt → canonical
STAR_VI_TO_CANON = {
    "Tử Vi": "tu_vi", "Thiên Cơ": "thien_co", "Thái Dương": "thai_duong",
    "Vũ Khúc": "vu_khuc", "Thiên Đồng": "thien_dong", "Liêm Trinh": "liem_trinh",
    "Thiên Phủ": "thien_phu", "Thái Âm": "thai_am", "Tham Lang": "tham_lang",
    "Cự Môn": "cu_mon", "Thiên Tướng": "thien_tuong", "Thiên Lương": "thien_luong",
    "Thất Sát": "that_sat", "Phá Quân": "pha_quan",
}

# Phụ tinh + sát tinh (an_sao trả {tên_vi: idx}) → canonical
PHU_SAT_VI_TO_CANON = {
    "Tả Phù": "ta_phu", "Tả Phụ": "ta_phu", "Hữu Bật": "huu_bat",
    "Văn Xương": "van_xuong", "Văn Khúc": "van_khuc",
    "Thiên Khôi": "thien_khoi", "Thiên Việt": "thien_viet",
    "Kình Dương": "kinh_duong", "Đà La": "da_la",
    "Hỏa Tinh": "hoa_tinh", "Linh Tinh": "linh_tinh",
    "Địa Không": "dia_khong", "Địa Kiếp": "dia_kiep",
    "Lộc Tồn": "loc_ton",
}

# Tứ Hóa: key an_sao → sao hóa canonical
TU_HOA_TO_CANON = {
    "Lộc": "hoa_loc", "Quyền": "hoa_quyen", "Khoa": "hoa_khoa", "Kỵ": "hoa_ky",
}

# Vòng sao phụ (Thái Tuế / Tướng Tinh / Bác Sĩ / sao Q2 / sao lẻ) → canonical.
# Mở khóa match cách cục cần sao vòng (Hổ cư hổ vị, Tứ Linh, Tuấn mã...).
VONG_VI_TO_CANON = {
    # Vòng Thái Tuế
    "Thái Tuế": "thai_tue", "Thiếu Dương": "thieu_duong", "Tang Môn": "tang_mon",
    "Thiếu Âm": "thieu_am", "Quan Phù": "quan_phu", "Tử Phù": "tu_phu",
    "Tuế Phá": "tue_pha", "Long Đức": "long_duc", "Bạch Hổ": "bach_ho",
    "Phúc Đức": "phuc_duc_sao", "Điếu Khách": "dieu_khach", "Trực Phù": "truc_phu",
    # Vòng Tướng Tinh
    "Tướng Tinh": "tuong_tinh", "Phan An": "phan_an", "Tuế Dịch": "tue_dich",
    "Tức Thần": "tuc_than", "Hoa Cái": "hoa_cai", "Kiếp Sát": "kiep_sat",
    "Tai Sát": "tai_sat", "Thiên Sát": "thien_sat", "Chỉ Bối": "chi_boi",
    "Hàm Trì": "ham_tri", "Nguyệt Sát": "nguyet_sat", "Vong Thần": "vong_than",
    # Vòng Bác Sĩ
    "Bác Sĩ": "bac_si", "Lực Sĩ": "luc_si", "Thanh Long": "thanh_long",
    "Tiểu Hao": "tieu_hao", "Tướng Quân": "tuong_quan", "Tấu Thư": "tau_thu",
    "Phi Liêm": "phi_liem", "Hỷ Thần": "hy_than", "Bệnh Phù": "benh_phu",
    "Đại Hao": "dai_hao", "Phục Binh": "phuc_binh",
    # Sao Q2 + sao lẻ
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

CAN_VI_TO_CANON = {
    "Giáp": "giap", "Ất": "at", "Bính": "binh", "Đinh": "dinh", "Mậu": "mau",
    "Kỷ": "ky", "Canh": "canh", "Tân": "tan", "Nhâm": "nham", "Quý": "quy",
}

CHI_VI_TO_CANON = {
    "Tý": "ty", "Sửu": "suu", "Dần": "dan", "Mão": "mao", "Thìn": "thin",
    "Tỵ": "ti", "Ngọ": "ngo", "Mùi": "mui", "Thân": "than", "Dậu": "dau",
    "Tuất": "tuat", "Hợi": "hoi",
}

CUC_NAME_TO_CANON = {
    "Thủy Nhị Cục": "thuy_nhi_cuc", "Mộc Tam Cục": "moc_tam_cuc",
    "Kim Tứ Cục": "kim_tu_cuc", "Thổ Ngũ Cục": "tho_ngu_cuc",
    "Hỏa Lục Cục": "hoa_luc_cuc",
}


@router.post("/3-layer/from-birth")
async def render_from_birth(birth: BirthInput) -> dict:
    """Nhập ngày sinh → tự an sao (re-use /api/tu-vi/cast logic) → render 3-Layer."""
    # Re-use route handler có sẵn solar→lunar conversion (engine an_sao = source of truth)
    from api.main import tu_vi_cast
    from api.schemas import TuViCastRequest

    cast = tu_vi_cast(TuViCastRequest(
        birth_datetime_local=birth.birth_datetime_local,
        timezone=birth.timezone,
        gender=birth.gender,
    ))
    ls = cast["la_so"]

    # Map chi index → cung CHỨC NĂNG (Mệnh/Tài Bạch/...) từ la_so palaces
    # để lookup được CẢ atoms tagged theo chi (mao, ti) VÀ theo chức năng (menh, tai_bach)
    PALACE_NAME_TO_CANON = {
        "Mệnh": "menh", "Huynh Đệ": "huynh_de", "Phu Thê": "phu_the",
        "Tử Tức": "tu_tuc", "Tài Bạch": "tai_bach", "Tật Ách": "tat_ach",
        "Thiên Di": "thien_di", "Nô Bộc": "no_boc", "Quan Lộc": "quan_loc",
        "Điền Trạch": "dien_trach", "Phúc Đức": "phuc_duc", "Phụ Mẫu": "phu_mau",
    }
    idx_to_function: dict[int, str] = {}
    for p in (ls.get("palaces") or []):
        fn = PALACE_NAME_TO_CANON.get(p.get("name", ""))
        if fn is not None and p.get("branch_index") is not None:
            idx_to_function[p["branch_index"] % 12] = fn

    # Map chinh_tinh {tên_vi: idx} → {palace_key: [star_canonical]}
    # palace_key gồm CẢ chi (ti, mao...) lẫn chức năng (menh, tai_bach...) — atoms
    # các sách tag theo 2 kiểu khác nhau, lookup cả 2 để không sót.
    chinh_tinh_per_palace: dict[str, list[str]] = {}
    for star_vi, idx in (ls.get("chinh_tinh") or {}).items():
        star = STAR_VI_TO_CANON.get(star_vi)
        if not star:
            continue
        chi = IDX_TO_CHI[idx % 12]
        chinh_tinh_per_palace.setdefault(chi, []).append(star)
        fn = idx_to_function.get(idx % 12)
        if fn:
            chinh_tinh_per_palace.setdefault(fn, []).append(star)

    # Phụ tinh + sát tinh ({tên_vi: idx}) — dual-lookup chi + chức năng như chính tinh
    phu_tinh_per_palace: dict[str, list[str]] = {}
    star_idx: dict[str, int] = {}  # canonical star → idx (để định vị Tứ Hóa)
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
    for star_vi, idx in (ls.get("chinh_tinh") or {}).items():
        star = STAR_VI_TO_CANON.get(star_vi)
        if star:
            star_idx[star] = idx % 12

    # Tứ Hóa: an_sao trả {"Lộc": "Tham Lang", ...} — hóa tinh đặt tại cung của sao gốc.
    # Đưa hoa_loc/hoa_quyen/... vào palace map để retrieval pull atoms 768+ tag hoa_ky...
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

    # Vòng sao phụ (4 vòng + sao lẻ) → chi map; KHÔNG vào phu_tinh retrieval
    # (giữ scope) — chỉ phục vụ match cách cục có tên.
    vong_sao_per_palace: dict[str, list[str]] = {}
    for src_key in ("thai_tue_belt", "tuong_tinh_belt", "bac_si_belt", "sao_q2", "sao_le"):
        for star_vi, idx in (ls.get(src_key) or {}).items():
            star = VONG_VI_TO_CANON.get(star_vi)
            if star is None:
                continue
            chi = IDX_TO_CHI[idx % 12]
            if star not in vong_sao_per_palace.setdefault(chi, []):
                vong_sao_per_palace[chi].append(star)
    tuan_chi = [IDX_TO_CHI[i % 12] for i in (ls.get("tuan") or [])]
    triet_chi = [IDX_TO_CHI[i % 12] for i in (ls.get("triet") or [])]

    # Vòng Tràng Sinh 12 sao (ts_*) — an theo cục + can + giới tính
    from engine.tu_vi.paradigm.trang_sinh import an_trang_sinh
    _cuc_canon = CUC_NAME_TO_CANON.get(ls.get("cuc_name", ""), "thuy_nhi_cuc")
    _can_canon = CAN_VI_TO_CANON.get(ls["year_stem"], ls["year_stem"].lower())
    for sao, chi in an_trang_sinh(_cuc_canon, _can_canon, "M" if birth.gender == "nam" else "F").items():
        if sao not in vong_sao_per_palace.setdefault(chi, []):
            vong_sao_per_palace[chi].append(sao)

    # Việc 3 — đại vận hiện tại (BIẾN): tuổi mụ → cycle đang đi, cung vận = "Mệnh 10 năm"
    from datetime import datetime
    birth_year = int(birth.birth_datetime_local[:4])
    age_mu = datetime.now().year - birth_year + 1
    dai_van_hien_tai = None
    cur = next((dv for dv in (ls.get("dai_van") or [])
                if dv["start_age"] <= age_mu <= dv["end_age"]), None)
    if cur:
        idx = cur["branch_index"] % 12
        van_chi = IDX_TO_CHI[idx]
        dai_van_hien_tai = {
            "cycle_index": cur["cycle_index"],
            "chi": van_chi,
            "fn": idx_to_function.get(idx),
            "start_age": cur["start_age"],
            "end_age": cur["end_age"],
            "age_mu": age_mu,
            "stars": [s for s in chinh_tinh_per_palace.get(van_chi, [])],
            "phu_tinh": [s for s in phu_tinh_per_palace.get(van_chi, [])],
        }

    la_so_input = {
        "can": CAN_VI_TO_CANON.get(ls["year_stem"], ls["year_stem"].lower()),
        "chi": CHI_VI_TO_CANON.get(ls["year_branch"], ls["year_branch"].lower()),
        "menh_palace": CHI_VI_TO_CANON.get(ls["menh_branch"], ls["menh_branch"].lower()),
        "than_palace": CHI_VI_TO_CANON.get(ls["than_branch"], ls["than_branch"].lower()),
        "cuc": CUC_NAME_TO_CANON.get(ls.get("cuc_name", ""), "thuy_nhi_cuc"),
        "gender": "M" if birth.gender == "nam" else "F",
        "birth_year": birth_year,  # năm dương lịch — LLM KHÔNG được tự suy (vá bịa 1976)
        "chinh_tinh_per_palace": chinh_tinh_per_palace,
        "phu_tinh_per_palace": phu_tinh_per_palace,
        "tu_hoa": tu_hoa_summary,
        "dai_van_hien_tai": dai_van_hien_tai,
        "vong_sao_per_palace": vong_sao_per_palace,
        "tuan_chi": tuan_chi,
        "triet_chi": triet_chi,
        # cung chức năng → chi thật: cho output_filler đối chiếu miếu-hãm +
        # lọc atom "mệnh ở chi khác" (lỗ #4 precision 2026-06-13)
        "fn_to_chi": {fn: IDX_TO_CHI[idx] for idx, fn in idx_to_function.items()},
    }
    result = render_3_layer(la_so_input)
    result["la_so_input"] = la_so_input
    return result


class NarrativeBirthInput(BirthInput):
    force: bool = False  # force=true bỏ cache, sinh lại


@router.post("/3-layer/narrative")
async def narrative_from_birth(birth: NarrativeBirthInput) -> dict:
    """Sinh narrative Lớp 1 'Chuyện về anh' bằng LLM (DeepSeek + cache theo lá số).

    Tách endpoint riêng vì LLM call 5-15s — frontend gọi sau khi đã render 3-layer.
    """
    from engine.atomization.narrative_gen import generate_narrative

    base = await render_from_birth(BirthInput(
        birth_datetime_local=birth.birth_datetime_local,
        timezone=birth.timezone,
        gender=birth.gender,
    ))
    # Vòng đời: tuổi mụ (năm xem − năm sinh + 1) → giai đoạn × giới → chủ đề + cung nhấn
    from datetime import datetime
    from engine.tu_vi.vong_doi import giai_doan_song, buoc_ngoat_dai_van, tin_hieu_nam_xem
    ls_in = base["la_so_input"]
    by = ls_in.get("birth_year") or int(birth.birth_datetime_local[:4])
    nam_xem = datetime.now().year
    tuoi_mu = nam_xem - by + 1
    gender_c = ls_in.get("gender", "M")
    ls_in["vong_doi"] = giai_doan_song(tuoi_mu, gender_c)
    ls_in["buoc_ngoat_nhac"] = buoc_ngoat_dai_van(ls_in.get("dai_van_hien_tai"))
    # Cung trọng tâm giai đoạn × giới → tên Việt để LLM nhấn
    _CUNG_NHAN = {
        ("thanh_nien", "nam"): ["Mệnh", "Quan Lộc", "Thiên Di"],
        ("thanh_nien", "nu"): ["Mệnh", "Phu Thê", "Quan Lộc"],
        ("lap_than", "nam"): ["Quan Lộc", "Tài Bạch", "Phu Thê"],
        ("lap_than", "nu"): ["Phu Thê", "Tử Tức", "Quan Lộc"],
        ("tam_thap", "nam"): ["Quan Lộc", "Tài Bạch", "Tử Tức", "Phu Thê"],
        ("tam_thap", "nu"): ["Tử Tức", "Phu Thê", "Phúc Đức"],
        ("tu_thap", "nam"): ["Quan Lộc", "Điền Trạch", "Tật Ách"],
        ("tu_thap", "nu"): ["Tử Tức", "Tật Ách", "Phu Thê", "Phúc Đức"],
        ("ngu_thap", "nam"): ["Quan Lộc", "Điền Trạch", "Tật Ách", "Phúc Đức"],
        ("ngu_thap", "nu"): ["Tử Tức", "Tật Ách", "Phúc Đức"],
        ("luc_thap", "nam"): ["Phúc Đức", "Tật Ách", "Tử Tức"],
        ("luc_thap", "nu"): ["Phúc Đức", "Tật Ách", "Tử Tức"],
    }
    vd = ls_in["vong_doi"]
    ls_in["cung_nhan"] = _CUNG_NHAN.get((vd.get("slug"), vd.get("gioi")), [])
    from engine.tu_vi.vong_doi import CHI as _VD_CHI
    _chi_vi = _VD_CHI[IDX_TO_CHI.index(ls_in["chi"])] if ls_in.get("chi") in IDX_TO_CHI else None
    ls_in["tin_hieu_nam"] = tin_hieu_nam_xem(_chi_vi, nam_xem, tuoi_mu, gender_c) if _chi_vi else []
    result = generate_narrative(base, ls_in, force=birth.force)
    return {
        "narrative": result["narrative"],
        "cached": result["cached"],
        "model": result["model"],
    }


@router.get("/3-layer/founder-demo")
async def founder_demo() -> dict:
    """Demo lá số founder Mậu Thìn (1988-06-05 23:30 Nam)."""
    la_so = {
        "can": "mau",
        "chi": "thin",
        "menh_palace": "ty",
        "than_palace": "than",
        "cuc": "thuy_nhi_cuc",
        "gender": "M",
        "chinh_tinh_per_palace": {
            "ty": ["thien_dong"],
            "than": ["vu_khuc"],
            "thin": ["tu_vi"],
            "hoi": ["thien_co"],
            "dau": ["thai_am"],
            "mao": ["thai_duong"],
            "ngo": ["lien_trinh"],
            "tuat": ["that_sat"],
            "dan": ["thien_phu"],
            "mui": ["thien_luong"],
            "suu": ["thien_tuong"],
            "ti": ["pha_quan"],
        }
    }
    return render_3_layer(la_so)
