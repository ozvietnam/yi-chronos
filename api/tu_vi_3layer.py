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

import sqlite3
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from engine.atomization.output_filler_v2 import render_3_layer

router = APIRouter(prefix="/api/tu-vi", tags=["tu-vi-3layer"])

# Phản hồi độ khớp chân dung (cuối mỗi phần: khai vị + từng món chính) — lưu cạnh
# users. KHÔNG để chung wiki.sqlite3 (đó là content db, ngoài CI). Đây là dữ liệu
# vận hành theo user (X-User-Id = Firebase UID do AppChat xác thực).
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_DB = _PROJECT_ROOT / "data/yi_users/tuvi_feedback.sqlite3"

# verdict: mức độ khớp CHÂN DUNG (để soát dữ liệu sinh) — KHÔNG phải "bói đúng/sai".
VALID_VERDICTS = {"correct", "close", "wrong", "vague"}


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
    # Quét điểm nổi bật toàn lá (cho cả UI lẫn narrative dùng chung)
    try:
        from engine.tu_vi.highlights import quet_diem_noi_bat
        result["highlights"] = quet_diem_noi_bat(la_so_input, result, top_n=6)
    except Exception:
        result["highlights"] = []
    return result


def _load_feedback(request: Request) -> dict | None:
    """Nạp phản hồi user đã đăng nhập → feed ngược vào bài (khép vòng tự học).

    Guest (chưa login) → None → bài luận như cũ.
    """
    try:
        from api.auth import get_current_user
        from engine.tu_vi.feedback_store import validated_atoms, khau_vi
        user = get_current_user(request)
        if not user:
            return None
        uid = user["user_id"]
        val = validated_atoms(uid)
        kv = khau_vi(uid)
        if not val and not kv.get("trai_nghiem"):
            return None
        return {"validated": val, "trai_nghiem": kv.get("trai_nghiem") or []}
    except Exception:
        return None


class NarrativeBirthInput(BirthInput):
    force: bool = False  # force=true bỏ cache, sinh lại


@router.post("/3-layer/narrative")
async def narrative_from_birth(birth: NarrativeBirthInput, request: Request) -> dict:
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
    # Điểm nổi bật toàn lá — render_from_birth đã quét, dùng lại (top 5 cho khai vị)
    ls_in["highlights"] = (base.get("highlights") or [])[:5]
    result = generate_narrative(base, ls_in, force=birth.force, feedback=_load_feedback(request))
    return {
        "narrative": result["narrative"],
        "cached": result["cached"],
        "model": result["model"],
    }


@router.get("/3-layer/chu-de")
async def list_chu_de() -> dict:
    """Danh sách 5 món chính (chủ đề đời sống) cho UI render thẻ."""
    from engine.tu_vi.chu_de import CHU_DE
    return {"chu_de": [
        {"slug": k, "ten": v["ten"], "icon": v["icon"], "goc_nhin": v["goc_nhin"]}
        for k, v in CHU_DE.items()
    ]}


class ChuDeBirthInput(BirthInput):
    chu_de: str
    force: bool = False


@router.post("/3-layer/chu-de")
async def chu_de_from_birth(birth: ChuDeBirthInput, request: Request) -> dict:
    """Luận MÓN CHÍNH theo 1 chủ đề đời sống (gom tam hợp cung liên quan + LLM).

    Lazy: frontend gọi khi user bấm thẻ chủ đề.
    """
    from engine.tu_vi.chu_de import gom_chu_de
    from engine.atomization.narrative_gen import generate_chu_de_narrative

    base = await render_from_birth(BirthInput(
        birth_datetime_local=birth.birth_datetime_local,
        timezone=birth.timezone,
        gender=birth.gender,
    ))
    ls_in = base["la_so_input"]
    cd = gom_chu_de(birth.chu_de, ls_in, base)
    if not cd:
        return {"error": f"Chủ đề không hợp lệ: {birth.chu_de}"}
    result = generate_chu_de_narrative(cd, ls_in, force=birth.force, feedback=_load_feedback(request))
    return {
        "slug": cd["slug"], "ten": cd["ten"], "icon": cd["icon"],
        "narrative": result["narrative"],
        "cached": result["cached"], "model": result["model"],
    }


@router.post("/3-layer/chu-de-sau")
async def chu_de_sau_from_birth(birth: ChuDeBirthInput, request: Request) -> dict:
    """MÓN SÂU: luận 2 trụ (Trung Châu + Trần Đoàn) + xuất xứ + hội tụ/dị biệt.

    User bấm 'Đào sâu' sau khi đã nghe món chính tổng quan.
    """
    from engine.tu_vi.chu_de import gom_chu_de_sau
    from engine.atomization.narrative_gen import generate_chu_de_sau_narrative

    base = await render_from_birth(BirthInput(
        birth_datetime_local=birth.birth_datetime_local,
        timezone=birth.timezone, gender=birth.gender))
    ls_in = base["la_so_input"]
    cd = gom_chu_de_sau(birth.chu_de, ls_in, base)
    if not cd:
        return {"error": f"Chủ đề không hợp lệ: {birth.chu_de}"}
    result = generate_chu_de_sau_narrative(cd, ls_in, force=birth.force, feedback=_load_feedback(request))
    return {
        "slug": cd["slug"], "ten": cd["ten"], "icon": cd["icon"],
        "narrative": result["narrative"], "cached": result["cached"], "model": result["model"],
        # nguyên liệu xuất xứ cho UI hiển thị (minh bạch nguồn)
        "nguyen_lieu": [
            {"sao_vi": b["sao_vi"], "cung_vi": b["cung_vi"], "hoi_tu": b["hoi_tu"],
             "nguon": sorted({v["xuat_xu"] for v in b["views"] if v["xuat_xu"]})}
            for b in cd["sao_blocks"]
        ],
    }


@router.post("/3-layer/gia-vi")
async def gia_vi_from_birth(birth: ChuDeBirthInput) -> dict:
    """Phái mỏng → câu hỏi gợi ý (Đúng/Chưa/Không) để user tự soi + ta học khẩu vị."""
    from engine.tu_vi.chu_de import gom_gia_vi
    from engine.atomization.narrative_gen import generate_gia_vi_questions

    base = await render_from_birth(BirthInput(
        birth_datetime_local=birth.birth_datetime_local,
        timezone=birth.timezone, gender=birth.gender))
    atoms = gom_gia_vi(birth.chu_de, base["la_so_input"], base)
    questions = generate_gia_vi_questions(atoms)
    return {"chu_de": birth.chu_de, "cau_hoi": questions}


class FeedbackInput(BaseModel):
    chu_de: str | None = None
    atom_id: int | None = None
    sao: str | None = None
    cau_hoi: str | None = None
    answer: str | None = None       # dung | chua | khong
    free_text: str | None = None    # kể thêm trải nghiệm


@router.post("/3-layer/feedback")
async def save_user_feedback(fb: FeedbackInput, request: Request) -> dict:
    """Lưu phản hồi user (gated: tự lưu của mình). Vòng tự học — biết đúng/sai + khẩu vị."""
    from api.auth import require_user
    from engine.tu_vi.feedback_store import save_feedback
    user = require_user(request)  # 401 nếu chưa đăng nhập
    fid = save_feedback(user["user_id"], fb.chu_de, fb.atom_id, fb.sao,
                        fb.cau_hoi, fb.answer, fb.free_text)
    return {"ok": True, "id": fid}


@router.get("/3-layer/khau-vi")
async def get_khau_vi(request: Request) -> dict:
    """Khẩu vị + phản hồi của CHÍNH user (gated self)."""
    from api.auth import require_user
    from engine.tu_vi.feedback_store import khau_vi
    user = require_user(request)
    return khau_vi(user["user_id"])


class HopHonInput(BaseModel):
    birth1: str = Field(..., description="Ngày giờ sinh người 1 (ISO local, vd 1988-06-05T23:30)")
    gender1: str = Field("nam", description="nam | nữ")
    ten1: str = Field("Người 1")
    birth2: str = Field(..., description="Ngày giờ sinh người 2")
    gender2: str = Field("nữ")
    ten2: str = Field("Người 2")
    timezone: str = Field("Asia/Ho_Chi_Minh")


@router.post("/hop-hon")
async def hop_hon(inp: HopHonInput) -> dict:
    """Hợp Hôn Tam Hệ — chấm độ tương ứng 2 lá số (Tử Vi + Bát Tự + Kinh Dịch).

    User nhập lá số mình + 1 lá số khác → kết quả + gia quy + hướng dẫn đọc.
    Paradigm: đọc đồng dạng, KHÔNG predict.
    """
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.ha_lac.cast import cast_ha_lac
    from engine.tu_vi.hop_hon import phan_tich_hop_hon

    def _gc(g):
        return "nữ" if g in ("nữ", "nu", "F", "f") else "nam"

    g1, g2 = _gc(inp.gender1), _gc(inp.gender2)
    try:
        base1 = await render_from_birth(BirthInput(
            birth_datetime_local=inp.birth1, timezone=inp.timezone, gender=g1))
        base2 = await render_from_birth(BirthInput(
            birth_datetime_local=inp.birth2, timezone=inp.timezone, gender=g2))
        ls1, ls2 = base1["la_so_input"], base2["la_so_input"]
        p1 = extract_tu_tru(inp.birth1, inp.timezone)
        p2 = extract_tu_tru(inp.birth2, inp.timezone)
        q1 = cast_ha_lac(birth_datetime_local=inp.birth1, timezone=inp.timezone, gender=g1).get("tien_thien_quai")
        q2 = cast_ha_lac(birth_datetime_local=inp.birth2, timezone=inp.timezone, gender=g2).get("tien_thien_quai")
    except Exception as e:
        return {"error": f"Lỗi lập lá số: {e}"}

    kq = phan_tich_hop_hon(ls1, p1, q1, ls2, p2, q2, ten1=inp.ten1, ten2=inp.ten2)
    # Món: năm hợp cưới (đào hoa vận cặp)
    try:
        from datetime import datetime as _dt
        from engine.tu_vi.hop_hon import nam_hop_cuoi
        by1 = ls1.get("birth_year") or int(inp.birth1[:4])
        by2 = ls2.get("birth_year") or int(inp.birth2[:4])
        kq["nam_hop_cuoi"] = nam_hop_cuoi(ls1, by1, ls2, by2, _dt.now().year, 10)
    except Exception:
        kq["nam_hop_cuoi"] = None
    return kq


class DuyenInput(BaseModel):
    birth: str = Field(..., description="Ngày giờ sinh (ISO local)")
    gender: str = Field("nam")
    timezone: str = Field("Asia/Ho_Chi_Minh")


@router.post("/duyen")
async def duyen_ca_nhan_endpoint(inp: DuyenInput) -> dict:
    """Duyên của tôi — bộ 4 tính năng cho người ĐANG TÌM:
    chân dung nửa kia · đường tình duyên · năm có duyên · tuổi hợp.
    """
    from datetime import datetime
    from engine.tu_vi.duyen import (chan_dung_nua_kia, duyen_ca_nhan, dao_hoa_van, tuoi_hop)

    g = "nữ" if inp.gender in ("nữ", "nu", "F", "f") else "nam"
    try:
        base = await render_from_birth(BirthInput(
            birth_datetime_local=inp.birth, timezone=inp.timezone, gender=g))
    except Exception as e:
        return {"error": f"Lỗi lập lá số: {e}"}
    ls = base["la_so_input"]
    by = ls.get("birth_year") or int(inp.birth[:4])
    nam_xem = datetime.now().year
    tuoi = nam_xem - by + 1
    return {
        "tuoi_mu": tuoi, "gioi": g,
        "chan_dung_nua_kia": chan_dung_nua_kia(ls),
        "duyen_ca_nhan": duyen_ca_nhan(ls, tuoi, g),
        "nam_co_duyen": dao_hoa_van(ls, by, nam_xem, n_nam=12),
        "tuoi_hop": tuoi_hop(ls.get("chi")),
        "paradigm": "Đọc đồng dạng, không bói. Lá số chỉ thiên hướng — duyên là việc bạn vận hành.",
    }


class GiaDaoInput(BaseModel):
    birth1: str
    gender1: str = "nam"
    ten1: str = "Chồng"
    birth2: str
    gender2: str = "nữ"
    ten2: str = "Vợ"
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/gia-dao")
async def gia_dao(inp: GiaDaoInput) -> dict:
    """Gia Đạo (đã cưới): gia quy ăn ở hợp đạo + năm thuận đón con (tính cho người nữ/mẹ)."""
    from datetime import datetime
    from engine.tu_vi.gia_dao import gia_quy_an_o, nam_sinh_con

    def _gc(g):
        return "nữ" if g in ("nữ", "nu", "F", "f") else "nam"
    g1, g2 = _gc(inp.gender1), _gc(inp.gender2)
    try:
        b1 = await render_from_birth(BirthInput(birth_datetime_local=inp.birth1, timezone=inp.timezone, gender=g1))
        b2 = await render_from_birth(BirthInput(birth_datetime_local=inp.birth2, timezone=inp.timezone, gender=g2))
    except Exception as e:
        return {"error": f"Lỗi lập lá số: {e}"}
    ls1, ls2 = b1["la_so_input"], b2["la_so_input"]
    nam_xem = datetime.now().year
    # năm sinh con: tính cho người NỮ (mẹ); nếu không có nữ → người 1
    if g2 == "nữ":
        me_ls, me_birth = ls2, inp.birth2
    elif g1 == "nữ":
        me_ls, me_birth = ls1, inp.birth1
    else:
        me_ls, me_birth = ls1, inp.birth1
    by_me = me_ls.get("birth_year") or int(me_birth[:4])
    return {
        "gia_quy": gia_quy_an_o(ls1, ls2, inp.ten1, inp.ten2),
        "nam_sinh_con": nam_sinh_con(me_ls, by_me, nam_xem, 10),
        "paradigm": "Đọc đồng dạng, không bói. Nếp nhà là việc hai người vận hành mỗi ngày.",
    }


class DatTenInput(BaseModel):
    birth_con: str = Field(..., description="Ngày giờ sinh của bé (ISO local)")
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/dat-ten")
async def dat_ten(inp: DatTenInput) -> dict:
    """Đặt tên con bổ ngũ hành: Bát Tự bé → dụng thần → gợi ý hành + chữ/tên mẫu."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.tu_vi.gia_dao import dat_ten_con
    try:
        pillars = extract_tu_tru(inp.birth_con, inp.timezone)
    except Exception as e:
        return {"error": f"Lỗi lập Bát Tự bé: {e}"}
    return dat_ten_con(pillars)


class _PersonIn(BaseModel):
    birth: str
    gender: str = "nam"
    ten: str = ""


class SoSanhInput(BaseModel):
    me: _PersonIn
    others: list[_PersonIn] = Field(default_factory=list)
    timezone: str = "Asia/Ho_Chi_Minh"


@router.post("/duyen-tho")
async def duyen_tho(inp: DuyenInput) -> dict:
    """Lời văn ấm cho 'Duyên của tôi' (LLM) — gọi sau khi đã hiện kết quả cấu trúc."""
    from engine.atomization.narrative_gen import generate_duyen_narrative
    base = await duyen_ca_nhan_endpoint(inp)
    if base.get("error"):
        return base
    try:
        out = generate_duyen_narrative(base)
    except Exception as e:
        return {"error": f"Lỗi sinh lời: {e}"}
    return out


@router.post("/so-sanh-duyen")
async def so_sanh_duyen(inp: SoSanhInput) -> dict:
    """So nhiều người với mình → xếp hạng độ tương ứng (cho người đang phân vân giữa nhiều mối)."""
    from engine.bat_tu.tu_tru import extract_tu_tru
    from engine.ha_lac.cast import cast_ha_lac
    from engine.tu_vi.hop_hon import phan_tich_hop_hon

    def _gc(g):
        return "nữ" if g in ("nữ", "nu", "F", "f") else "nam"

    async def _prep(p):
        g = _gc(p.gender)
        base = await render_from_birth(BirthInput(
            birth_datetime_local=p.birth, timezone=inp.timezone, gender=g))
        return (base["la_so_input"], extract_tu_tru(p.birth, inp.timezone),
                cast_ha_lac(birth_datetime_local=p.birth, timezone=inp.timezone, gender=g).get("tien_thien_quai"))

    try:
        mls, mp, mq = await _prep(inp.me)
    except Exception as e:
        return {"error": f"Lỗi lá số của bạn: {e}"}

    ket_qua = []
    for i, o in enumerate(inp.others[:8]):
        try:
            ols, op, oq = await _prep(o)
            r = phan_tich_hop_hon(mls, mp, mq, ols, op, oq,
                                  ten1=inp.me.ten or "Bạn", ten2=o.ten or f"Người {i+1}")
            ket_qua.append({
                "ten": o.ten or f"Người {i+1}", "diem_tong": r["diem_tong"], "muc": r["muc"],
                "ung_nhau": r["truc_cuong_nhu"]["ung_nhau"],
                "diem_noi_bat": (r["khoa_duyen"][:1] or [""])[0],
                "luu_y": (r["cho_phai_giu"][:1] or [""])[0],
            })
        except Exception:
            continue
    ket_qua.sort(key=lambda x: -x["diem_tong"])
    return {"xep_hang": ket_qua,
            "ghi_chu": "Điểm là độ TƯƠNG ỨNG cấu trúc, không phải 'người tốt nhất'. "
                       "Con người thật quan trọng hơn con số — đây chỉ là gợi ý tham khảo."}


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


# ── Phản hồi độ khớp (cuối mỗi phần luận) ────────────────────────────────────

def _ensure_feedback_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tuvi_feedback (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT,                -- X-User-Id (Firebase UID), nullable
            person_key  TEXT,                -- hồ sơ mệnh lý (nếu app gửi)
            section     TEXT NOT NULL,       -- 'khai_vi' | slug món chính
            verdict     TEXT NOT NULL,       -- correct|close|wrong|vague
            note        TEXT,
            model       TEXT,                -- bài luận do model nào sinh (truy vết)
            created_at  INTEGER NOT NULL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_tuvi_feedback_user "
        "ON tuvi_feedback (user_id, section)"
    )


class FeedbackInput(BaseModel):
    section: str = Field(..., description="'khai_vi' hoặc slug món chính (vd 'su-nghiep')")
    verdict: str = Field(..., description="correct | close | wrong | vague")
    note: Optional[str] = Field(None, description="ghi chú tự do của user (tùy chọn)")
    person_key: Optional[str] = None
    model: Optional[str] = Field(None, description="model đã sinh bài (truy vết, tùy chọn)")


@router.post("/feedback")
async def submit_feedback(
    fb: FeedbackInput,
    x_user_id: Optional[str] = Header(default=None),
) -> dict:
    """Nhận phản hồi độ KHỚP CHÂN DUNG cuối mỗi phần luận (khai vị + món chính).

    Mục đích: (1) đo độ khớp để cải thiện luận giải; (2) cờ NGHI NGỜ DỮ LIỆU SINH
    khi verdict ∈ {wrong, vague} → AppChat mời user soát lại ngày/giờ sinh (lẫn
    âm-dương, không nhớ giờ) hoặc chạy quiz tìm giờ. KHÔNG phải "bói đúng/sai".
    """
    verdict = (fb.verdict or "").strip().lower()
    if verdict not in VALID_VERDICTS:
        raise HTTPException(422, f"verdict không hợp lệ: {fb.verdict!r} (cho phép: {sorted(VALID_VERDICTS)})")
    if not (fb.section or "").strip():
        raise HTTPException(422, "thiếu section")

    FEEDBACK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(FEEDBACK_DB)
    try:
        _ensure_feedback_table(conn)
        conn.execute(
            "INSERT INTO tuvi_feedback "
            "(user_id, person_key, section, verdict, note, model, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (x_user_id, fb.person_key, fb.section.strip(), verdict,
             fb.note, fb.model, int(time.time())),
        )
        conn.commit()
    finally:
        conn.close()

    # wrong/vague = tín hiệu dữ liệu sinh có thể sai → AppChat gợi ý soát lại.
    birth_doubt = verdict in ("wrong", "vague")
    return {"status": "ok", "stored": True, "section": fb.section.strip(),
            "verdict": verdict, "birth_doubt": birth_doubt}
