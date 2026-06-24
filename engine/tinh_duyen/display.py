"""Lớp TRÌNH BÀY dùng chung web + AppChat cho read_tinh_duyen.

`build_display(reading_output, gender)` map output thô của
`engine.tinh_duyen.reading.read_tinh_duyen` → một cấu trúc {meta, sections}
SẠCH, CÓ THỨ TỰ, ĐÃ ẨN internal — render được trực tiếp ở cả 2 nơi:

- Web YI-Chronos (Vue): mỗi section.kind → 1 widget (dùng --read-* tokens).
- AppChat (prvchat): sections là JSON THUẦN (kind→widget), KHÔNG HTML.

ĐÂY LÀ PRESENTATION — KHÔNG đổi mệnh-lý, KHÔNG bịa: chỉ map cái có thật trong
reading_output. Giữ paradigm (Iron Rule #4/#6/#8): disclaimer ở meta + phác hoạ
mang nghĩa biểu tượng.

Quy tắc chính:
- Cấp độ thử thách (cap_do) là KILLER → LÊN ĐẦU sections.
- ẨN khỏi sections: base_12_khia_canh, scrub_caution_count, method_id nội bộ,
  các _nguon rải rác (GOM vào section 'nguon').
- Section RỖNG (không có data/items) → BỎ khỏi list.
- Title + meta.phoi_ngau gender-aware: NỮ → 'chồng', NAM → 'vợ'.
"""
from __future__ import annotations

from typing import Any, Optional

# Token giới NỮ: mặc định engine cho nữ mệnh.
_FEMALE_TOKENS = ("nữ", "nu", "female", "f", "")


def _is_female(gender: str) -> bool:
    return (gender or "").strip().lower() in _FEMALE_TOKENS


def _nonempty(obj: Any) -> bool:
    """True nếu obj có nội dung đáng hiển thị (str non-rỗng / list non-rỗng /
    dict non-rỗng / số). None / '' / [] / {} → False."""
    if obj is None:
        return False
    if isinstance(obj, str):
        return obj.strip() != ""
    if isinstance(obj, (list, tuple, dict)):
        return len(obj) > 0
    return True


def _refs_from(*blocks: Any) -> list[str]:
    """Gom mọi _nguon (str / list) từ các block lại thành list refs duy nhất,
    giữ thứ tự. Dùng cho refs cấp-section (vd cung_phu_the, cap_do)."""
    out: list[str] = []

    def _add(src: Any) -> None:
        if isinstance(src, str) and src.strip():
            if src not in out:
                out.append(src)
        elif isinstance(src, (list, tuple)):
            for x in src:
                _add(x)

    for b in blocks:
        _add(b)
    return out


# --------------------------------------------------------------------------- #
# Section builders — mỗi hàm trả 1 section dict hoặc None (None = bỏ).
# --------------------------------------------------------------------------- #
def _sec_cap_do(cd: dict) -> Optional[dict]:
    """KILLER section: chẩn đoán CẤP ĐỘ thử thách (1-5). LÊN ĐẦU."""
    if not _nonempty(cd):
        return None
    cap = cd.get("cap_do")
    if cap is None:
        return None
    nguyen_tac = cd.get("nguyen_tac_vang") or {}
    data = {
        "cap_do": cap,
        "max": 5,
        "ten_cap": cd.get("ten_cap"),
        "do_thay_doi_duoc": cd.get("do_thay_doi_duoc"),
        "phan_loai": cd.get("phan_loai"),
        "muc_do_thu_thach": cd.get("muc_do_thu_thach"),
        "tin_hieu": cd.get("tin_hieu_kich_hoat") or [],
        "lo_trinh": cd.get("lo_trinh") or [],
        "nguyen_tac": nguyen_tac.get("tuyen_bo"),
    }
    return {
        "id": "cap_do", "icon": "gauge", "title": "Mức độ thử thách",
        "kind": "cap_do", "data": data,
        "refs": _refs_from(cd.get("_nguon"), nguyen_tac.get("_nguon")),
    }


def _sec_hoi_dap(cau_hoi: list[dict]) -> Optional[dict]:
    """Câu hỏi của tuổi (Q&A) + cờ gieo quẻ Mai Hoa cho câu quyết định."""
    if not _nonempty(cau_hoi):
        return None
    items = []
    for q in cau_hoi:
        if not _nonempty(q.get("cau_hoi")):
            continue
        items.append({
            "hoi": q.get("cau_hoi"),
            "dap": q.get("tra_loi"),
            "he": q.get("he_tra_loi"),
            "cta_gieo_que": bool(q.get("can_gieo_que")),
        })
    if not items:
        return None
    return {
        "id": "hoi_dap", "icon": "messages", "title": "Câu hỏi của tuổi",
        "kind": "qa", "items": items,
    }


def _sec_cung_phu_the(cpt: dict, phoi_ngau: str) -> Optional[dict]:
    """Cung Phu Thê Tử Vi — prose_list (chính tinh / đào hoa / sát / tứ hoá)."""
    if not _nonempty(cpt):
        return None
    items = []
    refs = []
    groups = (
        ("chinh_tinh_luan", "tinh_chat_phoi_ngau"),
        ("dao_hoa_luan", "y_nghia_duyen"),
        ("sat_tinh_luan", "y_nghia"),
        ("tu_hoa_luan", "y_nghia"),
    )
    for key, body_field in groups:
        for entry in cpt.get(key) or []:
            ten = entry.get("sao") or entry.get("hoa")
            noi_dung = entry.get(body_field) or entry.get("y_nghia")
            if not _nonempty(noi_dung):
                continue
            items.append({"ten": ten, "noi_dung": noi_dung})
            refs.append(entry.get("_nguon"))
    if not items:
        return None
    return {
        "id": "cung_phu_the", "icon": "users",
        "title": f"Cung Phu Thê ({phoi_ngau})",
        "kind": "prose_list", "items": items, "refs": _refs_from(*refs),
    }


def _sec_song_phai(rec: list[dict]) -> Optional[dict]:
    """Tử Vi ⇄ Bát Tự — pairs (hội tụ / dị biệt theo chủ đề)."""
    if not _nonempty(rec):
        return None
    items = []
    for cd in rec:
        chu_de = cd.get("chu_de")
        tu_vi = cd.get("tuvi_doc_bang")
        bat_tu = cd.get("batu_doc_bang")
        if not (_nonempty(tu_vi) or _nonempty(bat_tu)):
            continue
        hoi_tu = cd.get("khi_HOI_TU")
        di_biet = cd.get("khi_DI_BIET")
        trang_thai = "hội tụ" if _nonempty(hoi_tu) else (
            "dị biệt" if _nonempty(di_biet) else "hội tụ")
        items.append({
            "chu_de": chu_de, "tu_vi": tu_vi, "bat_tu": bat_tu,
            "trang_thai": trang_thai,
        })
    if not items:
        return None
    return {
        "id": "song_phai", "icon": "arrows-shuffle",
        "title": "Tử Vi ⇄ Bát Tự", "kind": "pairs", "items": items,
    }


def _sec_dinh_thoi(dt: dict) -> Optional[dict]:
    """Định thời — timeline (năm kích hoạt / năm cần giữ gìn)."""
    if not _nonempty(dt):
        return None
    items = []
    for kh in dt.get("nam_kich_hoat") or []:
        items.append({
            "loai": "kích hoạt",
            "mo_ta": kh.get("dien_dat") or "đại vận có khí hỉ sự / duyên được kích hoạt",
            "start_age": kh.get("start_age"), "end_age": kh.get("end_age"),
            "branch": kh.get("branch"),
        })
    for gg in dt.get("nam_can_giu_gin") or []:
        items.append({
            "loai": "giữ gìn",
            "mo_ta": gg.get("dien_dat") or "năm cần giữ gìn / chăm sóc quan hệ",
            "start_age": gg.get("start_age"), "end_age": gg.get("end_age"),
            "branch": gg.get("branch"),
        })
    if not items:
        return None
    return {
        "id": "dinh_thoi", "icon": "clock", "title": "Định thời",
        "kind": "timeline", "items": items,
    }


# Map cat_hung engine → tone hiển thị.
_TONE_MAP = {
    "the_manh": "the_manh",
    "diem_can_chu_y": "can_chu_y",
    "trung_tinh": "trung_tinh",
}


def _sec_cach_cuc(cc: list[dict]) -> Optional[dict]:
    """Cách cục — list (đã reframe đọc-đồng-dạng qua field bien_chinh)."""
    if not _nonempty(cc):
        return None
    items = []
    for c in cc:
        noi_dung = c.get("bien_chinh") or c.get("van_hanh")
        if not _nonempty(noi_dung):
            continue
        items.append({
            "ten": c.get("ten_cach"),
            "noi_dung": noi_dung,
            "tone": _TONE_MAP.get(c.get("cat_hung"), "trung_tinh"),
        })
    if not items:
        return None
    return {
        "id": "cach_cuc", "icon": "recycle", "title": "Cách cục",
        "kind": "list", "items": items,
    }


def _sec_luan_chi_tiet(qt: dict) -> Optional[dict]:
    """Luận chi tiết 12+10 bước — collapsible (kim tự tháp + xếp hạng + bước)."""
    if not _nonempty(qt):
        return None
    tuvi = qt.get("tu_vi_12_buoc") or {}
    batu = qt.get("bat_tu_10_buoc") or {}
    xh = qt.get("xep_hang_yeu_to") or {}

    def _buoc(block: dict) -> list[dict]:
        out = []
        for b in block.get("buoc") or []:
            luan = b.get("luan")
            if not _nonempty(luan):
                continue
            out.append({"ten_buoc": b.get("ten_buoc"), "luan": luan})
        return out

    buoc_tu_vi = _buoc(tuvi)
    buoc_bat_tu = _buoc(batu)
    if not (buoc_tu_vi or buoc_bat_tu):
        return None

    def _rank(items: Any) -> list[dict]:
        out = []
        for it in items or []:
            out.append({"ten_buoc": it.get("ten_buoc"),
                        "luan_tom": it.get("luan_tom")})
        return out

    data = {
        "kim_tu_thap": qt.get("tong_hop_kim_tu_thap"),
        "xep_hang": {
            "truc_tiep": _rank(xh.get("truc_tiep")),
            "gian_tiep": _rank(xh.get("gian_tiep")),
            "tiem_an": _rank(xh.get("tiem_an")),
        },
        "buoc_tu_vi": buoc_tu_vi,
        "buoc_bat_tu": buoc_bat_tu,
    }
    return {
        "id": "luan_chi_tiet", "icon": "stack-2",
        "title": "Luận chi tiết 12+10 bước", "kind": "collapsible", "data": data,
    }


def _sec_loi_thay() -> dict:
    """Lời thầy — narration (sage narrate qua endpoint, fetch riêng)."""
    return {
        "id": "loi_thay", "icon": "quote", "title": "Lời thầy",
        "kind": "narration", "content": None,
        "fetch_action": "/api/cross-paradigm/tinh-duyen/narrate",
    }


def _sec_phac_hoa(phoi_ngau: str, disclaimer: Optional[str]) -> dict:
    """Phác hoạ chân dung BIỂU TƯỢNG người phối ngẫu — cta (paradigm)."""
    return {
        "id": "phac_hoa", "icon": "palette",
        "title": f"Phác họa người {phoi_ngau}", "kind": "cta",
        "action": "/api/cross-paradigm/tinh-duyen/phac-hoa",
        "note": disclaimer,
    }


def _sec_gieo_que() -> dict:
    """Gieo quẻ Mai Hoa cho câu quyết định — cta_gieo_que."""
    return {
        "id": "gieo_que", "icon": "yin-yang", "title": "Gieo quẻ quyết định",
        "kind": "cta_gieo_que",
        "action": "/api/cross-paradigm/tinh-duyen/gieo-que",
    }


def _sec_nguon(sources: list[str]) -> Optional[dict]:
    """Nguồn — refs (gom _nguon rải rác về 1 chỗ)."""
    if not _nonempty(sources):
        return None
    return {
        "id": "nguon", "icon": "book", "title": "Nguồn",
        "kind": "refs", "items": list(sources),
    }


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def build_display(reading_output: dict, gender: str = "nữ") -> dict:
    """Map read_tinh_duyen output → {meta, sections} trình bày dùng chung.

    Args:
        reading_output: dict trả từ read_tinh_duyen (hoặc service.run_tinh_duyen,
            có merge thêm charged_xu/cached — vẫn chứa đủ key engine).
        gender: 'nữ' (mặc định) / 'nam'. Nếu rỗng/không rõ, suy từ
            reading_output['input']['gender'].

    Returns:
        {meta: {...}, sections: [...]} — sections SẠCH, CÓ THỨ TỰ, ẨN internal,
        section rỗng đã bị bỏ. KHÔNG còn base_12_khia_canh / scrub_caution_count.
    """
    ro = reading_output or {}
    inp = ro.get("input") or {}

    # Giới: ưu tiên tham số; nếu không rõ → lấy từ input đã chuẩn hoá của engine.
    g = gender if _nonempty(gender) else inp.get("gender")
    nu = _is_female(g)
    phoi_ngau = "chồng" if nu else "vợ"
    gender_token = "nữ" if nu else "nam"

    stage = ro.get("stage") or {}
    disclaimer = ro.get("_disclaimer")

    meta = {
        "title": f"Tình duyên — người {phoi_ngau}",
        "gender": gender_token,
        "phoi_ngau": phoi_ngau,
        "tuoi": inp.get("tuoi") if inp.get("tuoi") is not None else stage.get("tuoi"),
        "stage_id": stage.get("stage_id"),
        "moi_truong": stage.get("moi_truong"),
        "disclaimer": disclaimer,
        "method_id": ro.get("method_id"),
        "paradigm_ok": bool(ro.get("paradigm_ok", True)),
    }

    # THỨ TỰ hiển thị (cap_do KILLER lên đầu; nguon cuối). None / rỗng đã bị bỏ.
    candidates = [
        _sec_cap_do(ro.get("chan_doan_cap_do") or {}),
        _sec_hoi_dap(ro.get("cau_hoi_tuoi") or []),
        _sec_cung_phu_the(ro.get("cung_phu_the_tuvi") or {}, phoi_ngau),
        _sec_song_phai(ro.get("song_phai_reconcile") or []),
        _sec_dinh_thoi(ro.get("dinh_thoi") or {}),
        _sec_cach_cuc(ro.get("cach_cuc") or []),
        _sec_luan_chi_tiet(ro.get("quy_trinh_day_du") or {}),
        _sec_loi_thay(),
        _sec_phac_hoa(phoi_ngau, disclaimer),
        _sec_gieo_que(),
        _sec_nguon(ro.get("sources") or []),
    ]
    sections = [s for s in candidates if s is not None]

    return {"meta": meta, "sections": sections}


__all__ = ["build_display"]
