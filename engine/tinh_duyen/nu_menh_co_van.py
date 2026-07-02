"""Nữ mệnh cổ thư + biện chính — 女命骨髓賦 (Toàn Thư) × 王亭之 深造讲义.

Anh giao 2026-06-24/07-02: chuyên sâu hôn nhân NỮ MỆNH trong gieo duyên, wire nguồn
thật. Kho: `knowledge/nu_menh_co_van.json` — mỗi entry có NGUYÊN VĂN + nguồn đích danh
(quote-or-silence); câu HUNG cổ bắt buộc kèm BIỆN CHÍNH của Vương Đình Chi (王亭之) —
không đổ định kiến cổ (quả tú/hạ tiện/dâm dật...) lên user (Iron #4/#6/#8: đọc đồng
dạng, mệnh là động từ; "女命反易奋发" — thời nay nữ mệnh dễ phấn phát).

Matcher DETERMINISTIC: match điều kiện sao/cung/tứ hóa của LÁ THẬT → chỉ trả entry
khớp. Không match → danh sách RỖNG (hệ không suy đoán thêm).
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import json

_KB_PATH = Path(__file__).parent / "knowledge" / "nu_menh_co_van.json"

# Lục sát thật (Lộc Tồn nằm trong map sat_tinh của an_sao nhưng KHÔNG phải sát tinh)
_LUC_SAT = {"Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp"}

# 夜生人 (sinh đêm) theo giờ chi: Dậu→Dần (≈17h-5h). Mão→Thân = ngày (日生人).
_GIO_DEM = {"Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần"}


@lru_cache(maxsize=1)
def _kb() -> dict:
    return json.loads(_KB_PATH.read_text(encoding="utf-8"))


def _palace_idx(la_so: dict, name: str) -> Optional[int]:
    for p in (la_so or {}).get("palaces") or []:
        if isinstance(p, dict) and p.get("name") == name:
            return p.get("branch_index")
    return None


def _stars_at(la_so: dict, idx: Optional[int], key: str) -> list[str]:
    if idx is None:
        return []
    m = (la_so or {}).get(key)
    return [s for s, i in m.items() if i == idx] if isinstance(m, dict) else []


def _branch_of(la_so: dict, idx: Optional[int]) -> Optional[str]:
    for p in (la_so or {}).get("palaces") or []:
        if isinstance(p, dict) and p.get("branch_index") == idx:
            return p.get("branch")
    return None


def _cung_ctx(la_so: dict, cung: str) -> dict:
    """Gom sao + branch của 1 cung chức năng (Mệnh / Phu Thê)."""
    idx = _palace_idx(la_so, cung)
    chinh = _stars_at(la_so, idx, "chinh_tinh")
    phu = _stars_at(la_so, idx, "phu_tinh")
    sat_raw = _stars_at(la_so, idx, "sat_tinh")
    return {
        "idx": idx,
        "branch": _branch_of(la_so, idx),
        "chinh": chinh,
        "phu": phu,
        "sat": [s for s in sat_raw if s in _LUC_SAT],
        "loc_ton": "Lộc Tồn" in sat_raw,
        "all": chinh + phu + sat_raw,
    }


def _is_nu(gender: Optional[str]) -> bool:
    return str(gender or "").strip().lower() in ("nữ", "nu", "female", "f")


def _match_ctp(dk: dict, menh: dict, phu_the: dict, tu_hoa: dict) -> bool:
    """Điều kiện 1 khối 女命骨髓賦 với lá thật."""
    ctx = menh if dk.get("cung") == "Mệnh" else phu_the
    if dk.get("vo_chinh_dieu"):
        return not ctx["chinh"]
    if dk.get("hoa_tai_menh"):
        # Hóa (Lộc...) tại Mệnh: sao mang hóa đó phải đóng ở cung Mệnh
        star = (tu_hoa or {}).get(dk["hoa_tai_menh"])
        if not star or star not in ctx["all"]:
            return False
    if dk.get("sao_bat_ky") and not any(s in ctx["all"] for s in dk["sao_bat_ky"]):
        return False
    if dk.get("branch_in") and ctx.get("branch") not in dk["branch_in"]:
        return False
    if dk.get("can_them_sao") and not any(s in ctx["all"] for s in dk["can_them_sao"]):
        return False
    if dk.get("min_sat_tinh") and len(ctx["sat"]) < dk["min_sat_tinh"]:
        return False
    return True


def _match_wang(ap: dict, gender: str, phu_the: dict, tu_hoa: dict,
                hour_branch: Optional[str] = None) -> bool:
    """Điều kiện áp dụng 1 rule 王亭之 (xét trên cung Phu Thê + tứ hóa + giới + giờ)."""
    if ap.get("gender") and _is_nu(gender) != _is_nu(ap["gender"]):
        return False
    if ap.get("sinh_dem") and hour_branch not in _GIO_DEM:
        return False  # rule 夜生人 CHỈ áp cho sinh đêm — thiếu giờ cũng không áp
    if ap.get("hoa_ky_in"):
        ky_star = (tu_hoa or {}).get("Kỵ")
        if ky_star not in ap["hoa_ky_in"]:
            return False
    if ap.get("hoa_quyen_in"):
        q_star = (tu_hoa or {}).get("Quyền")
        if q_star not in ap["hoa_quyen_in"]:
            return False
    if ap.get("sat_in_cung") and not any(s in phu_the["all"] for s in ap["sat_in_cung"]):
        return False
    if ap.get("phu_in_cung") and not any(s in phu_the["phu"] for s in ap["phu_in_cung"]):
        return False
    if ap.get("min_sat_in_cung") and len(phu_the["sat"]) < ap["min_sat_in_cung"]:
        return False
    return True


def doc_nu_menh_co_van(la_so: dict, gender: str = "nữ") -> dict[str, Any]:
    """Đọc lá theo kho nữ-mệnh cổ thư. Trả matches CÓ NGUỒN; rỗng nếu không khớp.

    Chạy cả 2 giới (rule gender-specific tự lọc); tối ưu cho nữ mệnh.
    """
    kb = _kb()
    menh = _cung_ctx(la_so, "Mệnh")
    phu_the = _cung_ctx(la_so, "Phu Thê")
    tu_hoa = (la_so or {}).get("tu_hoa") or {}

    # Phu Thê vô chính diệu → mượn đối cung (phép chuẩn) cho matching rule per-sao
    phu_the_doc = dict(phu_the)
    muon_doi_cung = False
    if not phu_the["chinh"] and phu_the["idx"] is not None:
        doi_idx = (phu_the["idx"] + 6) % 12
        chinh_doi = _stars_at(la_so, doi_idx, "chinh_tinh")
        if chinh_doi:
            muon_doi_cung = True
            phu_the_doc["chinh"] = chinh_doi
            phu_the_doc["all"] = chinh_doi + phu_the["phu"] + phu_the["sat"] \
                + (["Lộc Tồn"] if phu_the["loc_ton"] else [])

    # 1) 女命骨髓賦 — match theo Mệnh/Phu Thê
    phu_matches: list[dict] = []
    for e in kb.get("cot_tuy_phu") or []:
        if _match_ctp(e.get("dieu_kien") or {}, menh, phu_the, tu_hoa):
            m = {k: e[k] for k in
                 ("id", "tone", "nguyen_van", "han_viet", "dich") if k in e}
            if e.get("doc_dong_dang"):
                m["doc_dong_dang"] = e["doc_dong_dang"]
            if e.get("bien_chinh"):
                m["bien_chinh"] = e["bien_chinh"]
            if e.get("ghi_chu_ban_khac"):
                m["ghi_chu_ban_khac"] = e["ghi_chu_ban_khac"]
            # Câu HUNG cổ: PHIÊN ÂM xuất ra phải nằm trong KHUNG BIỆN-CHÍNH — chuỗi
            # trần kiểu "vi hạ tiện" là verdict kết án (guard _has_forbidden chặn
            # đúng). Nguyên văn HÁN trong JSON giữ thuần (Iron #5); chỉ đóng khung
            # bản phiên âm ở tầng OUTPUT.
            if e.get("tone") == "hung_co":
                khung = " — [nhãn cổ thư; biện chính kèm theo — không phải bản án]"
                if m.get("han_viet"):
                    m["han_viet"] = m["han_viet"] + khung
                if m.get("dich"):
                    m["dich"] = m["dich"] + khung
            phu_matches.append(m)

    # 2) 王亭之 per-sao Phu Thê — chọn nhóm sao chính đang tọa (kể cả mượn đối cung)
    wang_matches: list[dict] = []
    for grp in kb.get("wang_phu_the_14_sao") or []:
        if grp.get("sao") not in phu_the_doc["chinh"]:
            continue
        for r in grp.get("rules") or []:
            if _match_wang(r.get("ap_dung") or {}, gender, phu_the_doc, tu_hoa,
                           hour_branch=(la_so or {}).get("hour_branch")):
                wang_matches.append({"sao": grp["sao"], "id": r["id"],
                                     "nguyen_van": r["nguyen_van"], "dich_y": r["dich_y"],
                                     "muon_doi_cung": muon_doi_cung})

    # 3) Nguyên tắc đọc — chọn cái LIÊN QUAN lá này (không dump cả 5)
    nts = {n["id"]: n for n in kb.get("nguyen_tac_doc") or []}
    nguyen_tac: list[dict] = []
    if any(m.get("tone") == "hung_co" for m in phu_matches):
        for nid in ("nt-2", "nt-5"):          # biện chính thời nay + 3 van xả
            if nid in nts:
                nguyen_tac.append(nts[nid])
    if any(s in menh["all"] for s in ("Vũ Khúc", "Thất Sát", "Phá Quân", "Hỏa Tinh", "Linh Tinh")):
        if "nt-1" in nts:
            nguyen_tac.append(nts["nt-1"])    # cương liệt tuỳ cung
    if _is_nu(gender) and "Thiên Đồng" in menh["chinh"] and "nt-3" in nts:
        nguyen_tac.append(nts["nt-3"])        # gỡ nhãn Thiên Đồng
    if (phu_matches or wang_matches) and "nt-4" in nts:
        nguyen_tac.append(nts["nt-4"])        # xét kèm Nhật-Nguyệt
    # khử trùng giữ thứ tự
    seen: set = set()
    nguyen_tac = [n for n in nguyen_tac if not (n["id"] in seen or seen.add(n["id"]))]

    return {
        "method_id": "nu_menh_co_van_v1",
        "toi_uu_cho": "nữ",
        "ap_dung_cho_la_nay": _is_nu(gender),
        "menh_sao": menh["chinh"],
        "phu_the_sao": phu_the_doc["chinh"],
        "phu_the_muon_doi_cung": muon_doi_cung,
        "cot_tuy_phu": phu_matches,
        "wang_tingzhi": wang_matches,
        "nguyen_tac": nguyen_tac,
        "_nguon": kb.get("_nguon"),
        "_paradigm_note": ("Cổ văn giữ NGUYÊN VĂN (Iron #5); mọi câu hung cổ đọc qua "
                           "biện chính Vương Đình Chi — đọc đồng dạng, mệnh là động từ, "
                           "không phán bản án."),
    }
