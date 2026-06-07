"""Chiêm Cung Phu Thê v2 — Bắc Phái Trung Châu (Vương Đình Chỉ).

Engine v2 thêm 6 quy luật chưa có trong v1:

1. Tứ Hóa tại chính tinh Phu Thê → bias paradigm (vd Tham Lang Hóa Lộc → vật chất)
2. Detect "Đào hoa phạm chủ" Tử-Tham (yêu cầu sao đào hoa khác đồng cung)
3. Xương-Khúc trong cung Phu Thê HOẶC tam phương (rule riêng Tử-Tham)
4. Tả-Hữu / Khôi-Việt hội chiếu từ tam phương tứ chính
5. Đối cung Phu Thê (= Quan Lộc) — đặc biệt vô chính diệu
6. Mệnh chủ effect lên hôn nhân

Source: Trung Châu Tử Vi Đẩu Số 2 — Vương Đình Chỉ, section 5.3 + 3.x (luận hệ)
Doc: docs/design/cung-phu-the-anh-doi-chieu-trung-chau.md
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from .chiem_phu_the import (
    _STAR_KEY_MAP, _PAIR_KEY_BY_BRANCH, _PAIR_COMBO_MAP,
    _find_palace, _stars_at_branch_idx, _detect_luc_sat, _detect_hoa_ki,
    _load_seed,
)

# Sao đào hoa hệ chính (rule paradigm Bắc phái)
_DAO_HOA_STARS = {"Hồng Loan", "Thiên Hỉ", "Hàm Trì", "Đại Hao", "Thiên Diêu", "Mộc Dục"}

# Sao đôi cát (sách: cần có cặp; lẻ = tái hôn / người thứ ba)
_SAO_DOI_CAT = {"Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt"}

# Sao Hóa
_HOA_KEYS = ["Lộc", "Quyền", "Khoa", "Kỵ"]

# Mệnh chủ → tinh thần đặc thù (rút từ luận hệ 14 chính tinh Trung Châu)
_MENH_CHU_PARADIGM = {
    "Tham Lang": "đào hoa + ham muốn — cần đối tác có chí + tiết chế",
    "Cự Môn": "khẩu thiệt — vợ chồng dễ tranh cãi, cần ĐỐI THOẠI rõ",
    "Lộc Tồn": "ích kỷ + thu nhập cố định — vợ chồng cần chia sẻ tài chính",
    "Văn Khúc": "đa tài đa cảm — cần đối tác hiểu sâu",
    "Liêm Trinh": "máu lửa + tình cảm — dễ rối ren tình ái",
    "Vũ Khúc": "cứng rắn, cô độc, HÌNH KHẮC — cần vợ MỀM để cân bằng",
    "Phá Quân": "phá cũ lập mới — vợ chồng chia sẻ tinh thần đột phá",
}


def _tam_phuong_tu_chinh(branch_idx: int) -> dict[str, int]:
    """Tam phương tứ chính của 1 cung.

    Returns: {"doi": idx, "tam_hop_1": idx, "tam_hop_2": idx}
    """
    return {
        "doi": (branch_idx + 6) % 12,
        "tam_hop_1": (branch_idx + 4) % 12,
        "tam_hop_2": (branch_idx + 8) % 12,
    }


def _giap_cung(branch_idx: int) -> list[int]:
    """2 cung giáp 2 bên cung này."""
    return [(branch_idx - 1) % 12, (branch_idx + 1) % 12]


def _stars_at_indices(la_so: dict, indices: list[int]) -> dict[int, dict[str, list[str]]]:
    """Lấy stars tại 1 list branch indices."""
    return {i: _stars_at_branch_idx(la_so, i) for i in indices}


def _flatten_stars(stars_by_idx: dict[int, dict[str, list[str]]]) -> set[str]:
    """Tất cả sao trong các cung."""
    s = set()
    for d in stars_by_idx.values():
        s.update(d["chinh_tinh"])
        s.update(d["phu_tinh"])
        s.update(d["sat_tinh"])
    return s


def _detect_dao_hoa_pham_chu(stars_in_palace: dict[str, list[str]]) -> dict[str, Any]:
    """Detect 'Đào hoa phạm chủ' = Tử-Tham + sao đào hoa khác đồng cung.

    Sách Trung Châu (section 3.x): điều kiện tiên quyết là có Hồng Loan / Thiên Hỉ /
    Hàm Trì / Đại Hao / Thiên Diêu đồng cung với Tử-Tham.

    Phải đọc cả sao_q2 (Hồng Loan, Hàm Trì, Đại Hao, Thiên Diêu, Thiên Hỉ) — chứ
    không chỉ phu_tinh/sat_tinh.
    """
    chinh = set(stars_in_palace["chinh_tinh"])
    is_tu_tham = {"Tử Vi", "Tham Lang"}.issubset(chinh)
    if not is_tu_tham:
        return {"detected": False}

    all_stars = set(
        stars_in_palace["phu_tinh"]
        + stars_in_palace["sat_tinh"]
        + stars_in_palace.get("sao_q2", [])
    )
    dao_hoa_in = all_stars & _DAO_HOA_STARS
    return {
        "detected": bool(dao_hoa_in),
        "is_tu_tham": True,
        "sao_dao_hoa_kem": sorted(dao_hoa_in),
        "paradigm": (
            f"⚠ ĐÀO HOA PHẠM CHỦ — phóng đãng, tửu sắc "
            f"(có {', '.join(sorted(dao_hoa_in))} đồng cung)"
            if dao_hoa_in
            else "KHÔNG đào hoa phạm chủ → cách cục đặc thù: đa tài đa nghệ, giỏi giao tế, có chủ kiến"
        ),
    }


def _detect_hoa_at_chinh_tinh(la_so: dict, chinh_tinh: list[str]) -> dict[str, str]:
    """Detect Tứ Hóa nào rơi vào chính tinh Phu Thê."""
    tu_hoa = la_so.get("tu_hoa", {})
    detected = {}
    if isinstance(tu_hoa, dict):
        for hoa_key in _HOA_KEYS:
            star = tu_hoa.get(hoa_key) or tu_hoa.get(f"Hóa {hoa_key}")
            if star and star in chinh_tinh:
                detected[hoa_key] = star
    return detected


def _classify_tu_tham_bias(
    hoa_at_chinh: dict[str, str],
    dao_hoa_pham_chu: bool,
    xuong_khuc_in_palace_or_tam_phuong: bool,
    has_ta_huu_doi_hoi_chieu: bool,
    luc_sat_count: int,
) -> dict[str, Any]:
    """Phân loại Tử-Tham: VẬT CHẤT vs DỤC TÌNH (rule riêng Bắc phái).

    Returns: {"bias": "vat_chat"/"duc_tinh"/"trung_hoa", "ly_do": [...]}
    """
    ly_do = []
    score_vc = 0  # vật chất
    score_dt = 0  # dục tình

    # Rule 1: Tham Lang Hóa Lộc / Quyền → vật chất
    if hoa_at_chinh.get("Lộc") == "Tham Lang":
        score_vc += 3
        ly_do.append("Tham Lang Hóa Lộc → ham muốn vật chất nặng (sách 3.x)")
    if hoa_at_chinh.get("Quyền") == "Tham Lang":
        score_vc += 2
        ly_do.append("Tham Lang Hóa Quyền → tính vật chất tăng")
    if hoa_at_chinh.get("Lộc") == "Vũ Khúc":
        score_vc += 1
    if hoa_at_chinh.get("Khoa") == "Thiên Phủ":
        score_vc += 1

    # Rule 2: Đào hoa phạm chủ → dục tình
    if dao_hoa_pham_chu:
        score_dt += 4
        ly_do.append("Đào hoa phạm chủ detected → DỤC TÌNH (cảnh báo)")

    # Rule 3: Xương-Khúc đồng cung HOẶC tam phương → tăng đào hoa (rule riêng Tử-Tham)
    if xuong_khuc_in_palace_or_tam_phuong:
        score_dt += 2
        ly_do.append("Xương-Khúc gặp Tử-Tham → tăng sắc thái đào hoa (rule riêng)")

    # Rule 4: Tả-Hữu cát đôi hội chiếu → đa tài (giảm sắc thái dục tình)
    if has_ta_huu_doi_hoi_chieu:
        score_vc += 2
        ly_do.append("Tả-Hữu đôi hội chiếu → đa tài đa nghệ (cát thắng)")

    # Rule 5: Lục sát nặng (3+) → có khả năng dục tình
    if luc_sat_count >= 3:
        score_dt += 2
        ly_do.append(f"Lục sát có {luc_sat_count} sao → áp lực tăng (có thể dục tình)")

    # Decision
    if score_vc > score_dt + 1:
        bias = "vat_chat"
        ket_luan = "🎯 THIÊN VẬT CHẤT — bạn đời có CHÍ TIẾN THỦ"
    elif score_dt > score_vc + 1:
        bias = "duc_tinh"
        ket_luan = "⚠ THIÊN DỤC TÌNH — trước hôn nhân nhiều sóng gió, sau dễ ngoại tình"
    else:
        bias = "trung_hoa"
        ket_luan = "⚖ TRUNG HÒA — chưa nghiêng rõ; cần xem kèm đại vận"

    return {
        "bias": bias,
        "score_vat_chat": score_vc,
        "score_duc_tinh": score_dt,
        "ket_luan": ket_luan,
        "ly_do": ly_do,
    }


def _detect_sao_doi_hoi_chieu(
    la_so: dict, phu_the_idx: int, star_name: str
) -> dict[str, Any]:
    """Detect sao có ĐÔI (cùng cặp) hội chiếu vào Phu Thê (cung + tam phương).

    Ví dụ: 'Tả Phù' + 'Hữu Bật' đều xuất hiện ở Phu Thê + tam phương → đôi.
    """
    PAIR_MAP = {
        "Tả Phù": "Hữu Bật",
        "Hữu Bật": "Tả Phù",
        "Văn Xương": "Văn Khúc",
        "Văn Khúc": "Văn Xương",
        "Thiên Khôi": "Thiên Việt",
        "Thiên Việt": "Thiên Khôi",
    }
    if star_name not in PAIR_MAP:
        return {"is_pair": False}

    tptc = _tam_phuong_tu_chinh(phu_the_idx)
    target_indices = [phu_the_idx] + list(tptc.values())
    all_stars = _flatten_stars(_stars_at_indices(la_so, target_indices))

    pair_partner = PAIR_MAP[star_name]
    is_pair = star_name in all_stars and pair_partner in all_stars
    return {
        "is_pair": is_pair,
        "this_star": star_name,
        "partner": pair_partner,
        "where": [
            i for i in target_indices
            if _stars_at_branch_idx(la_so, i)
            and (star_name in _flatten_stars({i: _stars_at_branch_idx(la_so, i)})
                 or pair_partner in _flatten_stars({i: _stars_at_branch_idx(la_so, i)}))
        ],
    }


def _check_xuong_khuc_in_palace_or_tam_phuong(la_so: dict, phu_the_idx: int) -> bool:
    """Có Văn Xương hoặc Văn Khúc trong Phu Thê HOẶC tam phương không?"""
    tptc = _tam_phuong_tu_chinh(phu_the_idx)
    indices = [phu_the_idx] + list(tptc.values())
    all_stars = _flatten_stars(_stars_at_indices(la_so, indices))
    return bool({"Văn Xương", "Văn Khúc"} & all_stars)


def _check_ta_huu_doi_hoi_chieu(la_so: dict, phu_the_idx: int) -> bool:
    """Có Tả Phù + Hữu Bật ĐÔI hội chiếu (cung + tam phương) không?"""
    tptc = _tam_phuong_tu_chinh(phu_the_idx)
    indices = [phu_the_idx] + list(tptc.values())
    all_stars = _flatten_stars(_stars_at_indices(la_so, indices))
    return "Tả Phù" in all_stars and "Hữu Bật" in all_stars


def _detect_doi_cung_vo_chinh_dieu(la_so: dict, phu_the_idx: int) -> dict[str, Any]:
    """Đối cung Phu Thê (= Quan Lộc) có vô chính diệu không?"""
    doi_idx = (phu_the_idx + 6) % 12
    stars = _stars_at_branch_idx(la_so, doi_idx)
    is_void = len(stars["chinh_tinh"]) == 0
    BRANCHES = ['Tý','Sửu','Dần','Mão','Thìn','Tỵ','Ngọ','Mùi','Thân','Dậu','Tuất','Hợi']
    return {
        "doi_cung_index": doi_idx,
        "doi_cung_branch": BRANCHES[doi_idx],
        "is_void": is_void,
        "stars_in_doi_cung": stars["chinh_tinh"],
        "paradigm": (
            "Đối cung (Quan Lộc) VÔ CHÍNH DIỆU → mượn sao Phu Thê. "
            "Sự nghiệp và hôn nhân chia sẻ cùng tinh hệ — vợ vừa là người yêu vừa là cộng sự."
            if is_void
            else f"Đối cung có chính tinh: {', '.join(stars['chinh_tinh'])}"
        ),
    }


def chiem_phu_the_v2(la_so: dict) -> dict[str, Any]:
    """Engine v2 — paradigm Bắc Phái Trung Châu, 6 quy luật mới."""
    seed = _load_seed()

    pal = _find_palace(la_so, "Phu Thê")
    if not pal:
        return {"error": "Không tìm thấy cung Phu Thê"}

    branch = pal["branch"]
    branch_idx = pal["branch_index"]
    stars_at = _stars_at_branch_idx(la_so, branch_idx)
    luc_sat = _detect_luc_sat(stars_at)
    hoa_ki = _detect_hoa_ki(la_so, branch_idx)

    # Quy luật 1: Tứ Hóa tại chính tinh Phu Thê
    hoa_at_chinh = _detect_hoa_at_chinh_tinh(la_so, stars_at["chinh_tinh"])

    # Quy luật 2: Đào hoa phạm chủ (chỉ áp dụng Tử-Tham)
    dao_hoa_check = _detect_dao_hoa_pham_chu(stars_at)

    # Quy luật 3: Xương-Khúc rule (chỉ áp dụng Tử-Tham)
    xuong_khuc = _check_xuong_khuc_in_palace_or_tam_phuong(la_so, branch_idx)

    # Quy luật 4: Tả-Hữu hội chiếu tam phương
    ta_huu_hoi = _check_ta_huu_doi_hoi_chieu(la_so, branch_idx)

    # Quy luật 5: Đối cung vô chính diệu
    doi_cung = _detect_doi_cung_vo_chinh_dieu(la_so, branch_idx)

    # Quy luật 6: Mệnh chủ effect
    menh_chu = la_so.get("menh_chu", "")
    menh_chu_paradigm = _MENH_CHU_PARADIGM.get(menh_chu, "")

    # Phân loại Tử-Tham bias (nếu là Tử-Tham)
    bias_result = None
    chinh_set = set(stars_at["chinh_tinh"])
    if {"Tử Vi", "Tham Lang"}.issubset(chinh_set):
        bias_result = _classify_tu_tham_bias(
            hoa_at_chinh=hoa_at_chinh,
            dao_hoa_pham_chu=dao_hoa_check["detected"],
            xuong_khuc_in_palace_or_tam_phuong=xuong_khuc,
            has_ta_huu_doi_hoi_chieu=ta_huu_hoi,
            luc_sat_count=len(luc_sat),
        )

    # Tổ hợp đôi
    to_hop_key = None
    if len(chinh_set) == 2:
        to_hop_key = _PAIR_COMBO_MAP.get(frozenset(chinh_set))

    return {
        "version": "v2",
        "cung_phu_the": {"branch": branch, "branch_index": branch_idx},
        "chinh_tinh": stars_at["chinh_tinh"],
        "phu_tinh": stars_at["phu_tinh"],
        "sat_tinh": stars_at["sat_tinh"],
        "luc_sat_trong_cung": luc_sat,
        "hoa_ki_trong_cung": hoa_ki,
        "to_hop_doi": to_hop_key,
        "quy_luat_v2": {
            "1_tu_hoa_at_chinh_tinh": hoa_at_chinh,
            "2_dao_hoa_pham_chu": dao_hoa_check,
            "3_xuong_khuc_anh_huong": {
                "detected": xuong_khuc,
                "note": "Tử-Tham + Xương/Khúc → tăng đào hoa (rule riêng Bắc phái)" if xuong_khuc else "Không tăng đào hoa từ Xương-Khúc",
            },
            "4_ta_huu_doi_hoi_chieu": {
                "detected": ta_huu_hoi,
                "note": "Tả-Hữu đôi hội chiếu (cung + tam phương) → đa tài đa nghệ, giỏi giao tế" if ta_huu_hoi else "Thiếu Tả-Hữu đôi",
            },
            "5_doi_cung_vo_chinh_dieu": doi_cung,
            "6_menh_chu_anh_huong": {
                "menh_chu": menh_chu,
                "paradigm": menh_chu_paradigm or "(không có rule cụ thể trong sách)",
            },
        },
        "tu_tham_bias": bias_result,
        "iron_rule": (
            "Paradigm Bắc Phái Trung Châu (Vương Đình Chỉ) — đọc ĐỒNG DẠNG, "
            "KHÔNG predict tuyệt đối. 6 quy luật v2 tổng hợp từ section 5.3 + 3.x."
        ),
        "school": "bac_phai_trung_chau",
        "thay_to_su": seed.get("_meta", {}).get("thay_to_su", []),
    }
