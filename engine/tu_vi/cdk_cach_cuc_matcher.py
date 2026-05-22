"""CDK Cách Cục Matcher — đánh giá 6 cách cục Chiếu Đởm Kinh cho lá số cụ thể.

Mỗi cách cục có pattern điều kiện. Engine eval xem lá số có trúng không + reason.

Source: data/tu_vi/chieu_dom_kinh_cach_cuc.json (Q4 p0275)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

CACH_CUC_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data/tu_vi/chieu_dom_kinh_cach_cuc.json"


def _load_cach_cuc_dict() -> dict:
    with CACH_CUC_DATA_PATH.open() as f:
        return json.load(f)


def _is_star_in_mieu(star: str, branch: str) -> bool:
    """Kiểm tra sao này có đắc miếu/hỷ tại branch không.
    Đơn giản hóa: dùng Nhập Cốt hy_cung mapping.
    """
    p = Path(__file__).resolve().parent.parent.parent / "data/tu_vi/nhap_cot_tien_kinh_tong_doan.json"
    if not p.exists():
        return False
    with p.open() as f:
        nc = json.load(f)
    # Map sao short → full name
    NAME_MAP = {
        "Tử": "Tử Vi", "Hư": "Thiên Hư", "Quý": "Thiên Quý", "Ấn": "Thiên Ấn",
        "Thọ": "Thiên Thọ", "Không": "Thiên Hư", "Loan": "Hồng Loan", "Hồng": "Hồng Loan",
        "Khố": "Thiên Khố", "Quán": "Thiên Quán", "Văn": "Văn Xương",
        "Phúc": "Phúc Lộc", "Lộc": "Phúc Lộc", "Trượng": "Thiên Trượng",
        "Dị": "Thiên Dị", "Mao": "Mao Đầu", "Nhận": "Thiên Nhận (Kình Dương)",
        "Hình": "Thiên Hình", "Khốc": "Thiên Khốc", "Diêu": "Thiên Diêu",
    }
    full = NAME_MAP.get(star, star)
    for item in nc.get("per_star_tong_doan", []):
        if item.get("star") == full:
            return branch in (item.get("hy_cung") or [])
    return False


def _eval_pattern(cach_cuc: dict, cdk_chart: dict, birth_hour_branch: str) -> dict:
    """Eval 1 cách cục. Return {matched: bool, reason: str, details: dict}.

    Args:
        cach_cuc: 1 entry từ data['cach_cuc']
        cdk_chart: kết quả cast_chieu_dom_kinh (có menh_branch, than_branch, stars{star→branch})
        birth_hour_branch: giờ sinh (chi)
    """
    pid = cach_cuc.get("id")
    pattern = cach_cuc.get("pattern", {})
    menh = cdk_chart.get("menh_branch")
    # CDK chart không có than_branch sẵn — dùng menh làm fallback (CDK không tách Thân riêng như TVĐS)
    than = cdk_chart.get("than_branch", menh)
    stars = cdk_chart.get("stars", {}) or {}

    result = {"matched": False, "reason": "", "details": {}}

    if pid == "than_nich_giang_ho":
        # Mệnh hoặc Thân tại Hợi/Tý + sao thất miếu
        target_branches = pattern.get("menh_than_branch", ["Hợi", "Tý"])
        loc_match = menh in target_branches or than in target_branches
        if not loc_match:
            result["reason"] = f"Mệnh ({menh}) và Thân ({than}) không tại {target_branches}."
        else:
            # Check stars at those branches — có sao nào đó thất hãm không
            check_branch = menh if menh in target_branches else than
            stars_at = [s for s, b in stars.items() if b == check_branch]
            not_in_mieu = [s for s in stars_at if not _is_star_in_mieu(s, check_branch)]
            if not_in_mieu:
                result["matched"] = True
                result["reason"] = f"Mệnh/Thân tại {check_branch}, sao thất hãm: {', '.join(not_in_mieu)}."
                result["details"]["unmieu_stars"] = not_in_mieu
            else:
                result["reason"] = f"Mệnh/Thân tại {check_branch} nhưng các sao đều đắc miếu — không trúng."

    elif pid == "tu_dau_la_vong":
        target = pattern.get("menh_branch_any", ["Tuất", "Hợi", "Thìn", "Tỵ"])
        if menh in target:
            result["matched"] = True
            zone = "Thiên La" if menh in ["Thìn", "Tỵ"] else "Địa Võng"
            result["reason"] = f"Mệnh tại {menh} thuộc {zone}."
            result["details"]["zone"] = zone
        else:
            result["reason"] = f"Mệnh ({menh}) không nằm trong Thiên La (Thìn-Tỵ) hoặc Địa Võng (Tuất-Hợi)."

    elif pid == "than_nhap_ban_dan":
        target_branch = pattern.get("than_quan_at_branch", "Tỵ")
        # CDK không có cung Quan rõ — em map Thân tại target_branch
        if than == target_branch:
            result["matched"] = True
            result["reason"] = f"Thân quan tại {target_branch}."
        else:
            result["reason"] = f"Thân ({than}) không tại {target_branch}."

    elif pid == "ma_chuc_vi_menh":
        # Mệnh có Thiên Nhận (Kình Dương)
        nhan_branch = stars.get("Nhận")
        if nhan_branch == menh:
            result["matched"] = True
            result["reason"] = f"Sao Nhận (Kình Dương) tọa Mệnh tại {menh}."
        else:
            result["reason"] = f"Sao Nhận đóng tại {nhan_branch}, không tại Mệnh ({menh})."

    elif pid == "menh_toa_phu_mon":
        # Mệnh Mão + có Thiên Nhận + Thiên Hư tại Mão
        if menh != "Mão":
            result["reason"] = f"Mệnh tại {menh}, không phải Mão."
        else:
            stars_at_mao = [s for s, b in stars.items() if b == "Mão"]
            has_nhan = "Nhận" in stars_at_mao
            has_hu = "Hư" in stars_at_mao or "Không" in stars_at_mao
            if has_nhan and has_hu:
                result["matched"] = True
                result["reason"] = "Mệnh Mão + có cả Nhận (Kình Dương) và Hư tại đây — KỲ CÁCH (hung-mà-không-hung)."
                result["details"]["ky_cach"] = True
            else:
                missing = []
                if not has_nhan: missing.append("Nhận")
                if not has_hu: missing.append("Hư")
                result["reason"] = f"Mệnh Mão nhưng thiếu sao: {missing}."

    elif pid == "xa_nhap_long_cung":
        # Mệnh Mão + giờ sinh Mão
        if menh == "Mão" and birth_hour_branch == "Mão":
            result["matched"] = True
            result["reason"] = "Mệnh Mão + giờ sinh Mão — rule mạnh, tốt mọi mặt không cần xét sao."
        else:
            parts = []
            if menh != "Mão": parts.append(f"Mệnh={menh} (cần Mão)")
            if birth_hour_branch != "Mão": parts.append(f"giờ sinh={birth_hour_branch} (cần Mão)")
            result["reason"] = ", ".join(parts) + "."

    else:
        result["reason"] = f"Chưa hỗ trợ eval cho cách cục id={pid}."

    return result


def evaluate_cdk_cach_cuc(cdk_chart: dict, birth_hour_branch: str) -> dict:
    """Eval cả 6 cách cục Chiếu Đởm Kinh cho lá số.

    Args:
        cdk_chart: output của cast_chieu_dom_kinh()
        birth_hour_branch: giờ sinh chi (Tý/Sửu/.../Hợi)

    Returns:
        {
          status: 'ok',
          total: 6,
          matched_count: int,
          matched: [{...full cach cuc data + match result}],
          not_matched: [{...same shape}],
          paradigm_note: str,
        }
    """
    data = _load_cach_cuc_dict()
    cach_list = data.get("cach_cuc", [])
    matched = []
    not_matched = []
    for cc in cach_list:
        eval_result = _eval_pattern(cc, cdk_chart, birth_hour_branch)
        entry = {**cc, **eval_result}
        if eval_result["matched"]:
            matched.append(entry)
        else:
            not_matched.append(entry)
    return {
        "status": "ok",
        "menh_branch": cdk_chart.get("menh_branch"),
        "than_branch": cdk_chart.get("than_branch") or cdk_chart.get("menh_branch"),
        "birth_hour_branch": birth_hour_branch,
        "total": len(cach_list),
        "matched_count": len(matched),
        "matched": matched,
        "not_matched": not_matched,
        "paradigm_note": data.get("paradigm_note", ""),
        "source": data.get("source", ""),
    }
