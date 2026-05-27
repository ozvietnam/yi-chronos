"""Wrapper class an cục Kỳ Môn Độn Giáp.

Sử dụng `engine.ky_mon.vendored.kinqimen` (vendored từ kentang2017/kinqimen, MIT)
để tính bàn cơ bản, sau đó dịch TQ → Việt và format JSON contract cho UI.

Paradigm: ĐỌC ĐỒNG DẠNG (theo Iron Rule #4 + #6).
Bàn Kỳ Môn là bản đồ năng lượng thời-không tại thời điểm hỏi, không phải predict.
Người đọc trace ngược: Khí (bàn) → Tính (bản chất khoảnh khắc) → Đối ứng tâm cảnh.
"""

from datetime import datetime
from typing import Literal

from .vendored.kinqimen import Qimen
from .constants import (
    CACH_CUC_CANON,
    CAN_NGU_HANH,
    CAN_VN,
    CHI_VN,
    CUNG_DIRECTION,
    CUNG_NGU_HANH,
    CUNG_VN,
    LUC_NGHI,
    MON_CAT_HUNG,
    MON_NGU_HANH,
    MON_VN,
    TAM_KY,
    THAN_CAT_HUNG,
    THAN_VN,
    TIET_KHI_VN,
    TINH_CAT_HUNG,
    TINH_NGU_HANH,
    TINH_VN,
)

Method = Literal["chabu", "zhirun", "minute", "gpan"]
_METHOD_MAP = {"chabu": 1, "zhirun": 2}


def _vn_can(ch: str) -> dict:
    if ch in CAN_VN:
        return {"zh": ch, "vn": CAN_VN[ch], "ngu_hanh": CAN_NGU_HANH[ch]}
    if ch in TAM_KY:
        return {"zh": ch, "vn": CAN_VN[ch], "kind": "tam_ky", "label": TAM_KY[ch]}
    if ch in LUC_NGHI:
        return {"zh": ch, "vn": CAN_VN[ch], "kind": "luc_nghi", "label": LUC_NGHI[ch]}
    return {"zh": ch, "vn": ch}


def _translate_cung_map(raw: dict, value_kind: str) -> list[dict]:
    """Translate dict {cung_zh: value_zh} → list of structured cung cells."""
    out = []
    for cung_zh, val in raw.items():
        cell = {
            "cung_zh": cung_zh,
            "cung_vn": CUNG_VN.get(cung_zh, cung_zh),
            "direction": CUNG_DIRECTION.get(cung_zh, ""),
            "cung_ngu_hanh": CUNG_NGU_HANH.get(cung_zh, ""),
        }
        if value_kind == "can":
            cell.update({
                "can_zh": val,
                "can_vn": CAN_VN.get(val, val),
                "ngu_hanh": CAN_NGU_HANH.get(val, ""),
                "is_tam_ky": val in TAM_KY,
                "is_luc_nghi": val in LUC_NGHI,
            })
        elif value_kind == "mon":
            cell.update({
                "mon_zh": val,
                "mon_vn": MON_VN.get(val, val),
                "ngu_hanh": MON_NGU_HANH.get(val, ""),
                "cat_hung": MON_CAT_HUNG.get(val, ""),
            })
        elif value_kind == "tinh":
            cell.update({
                "tinh_zh": val,
                "tinh_vn": TINH_VN.get(val, val),
                "ngu_hanh": TINH_NGU_HANH.get(val, ""),
                "cat_hung": TINH_CAT_HUNG.get(val, ""),
            })
        elif value_kind == "than":
            cell.update({
                "than_zh": val,
                "than_vn": THAN_VN.get(val, val),
                "cat_hung": THAN_CAT_HUNG.get(val, ""),
            })
        out.append(cell)
    return out


def _parse_can_chi_string(s: str) -> dict:
    """Parse '戊辰年戊午月壬辰日庚子時' → 4 pillars dict."""
    pillars = {}
    pairs = [("年", "year"), ("月", "month"), ("日", "day"), ("時", "hour")]
    cursor = 0
    for marker, key in pairs:
        idx = s.find(marker, cursor)
        if idx == -1:
            continue
        can_chi = s[cursor:idx]
        if len(can_chi) >= 2:
            can_ch, chi_ch = can_chi[0], can_chi[1]
            pillars[key] = {
                "zh": can_chi,
                "can": {"zh": can_ch, "vn": CAN_VN.get(can_ch, can_ch),
                        "ngu_hanh": CAN_NGU_HANH.get(can_ch, "")},
                "chi": {"zh": chi_ch, "vn": CHI_VN.get(chi_ch, chi_ch)},
            }
        cursor = idx + 1
    return pillars


def cast(
    year: int, month: int, day: int, hour: int, minute: int = 0,
    method: Method = "chabu",
) -> dict:
    """An cục Kỳ Môn Độn Giáp tại thời điểm cụ thể.

    Args:
        year, month, day, hour, minute: Solar datetime (dương lịch)
        method: 'chabu' (拆補) | 'zhirun' (置閏) | 'minute' (分家) | 'gpan' (金函玉鏡 daily)

    Returns:
        dict với keys: phuong_phap, tu_tru, tuan, cuc, tiet_khi, tri_phu_tri_su,
        thien_ban (9 cung), dia_ban (9 cung), mon (8 cung), tinh (9 cung), than (8 cung),
        ma_tinh, truong_sinh_van, paradigm_note
    """
    qm = Qimen(year, month, day, hour, minute)

    if method == "gpan":
        raw = qm.gpan()
        return _format_gpan(raw, year, month, day, hour, minute)
    if method == "minute":
        raw = qm.pan_minute(2)
    else:
        raw = qm.pan(_METHOD_MAP[method])

    thien_ban_raw = raw.get("天盤", {})
    dia_ban_raw = raw.get("地盤", {})
    mon_raw = raw.get("門", {})
    cach_cuc_detected = detect_cach_cuc(thien_ban_raw, dia_ban_raw, mon_raw)

    return {
        "method": method,
        "phuong_phap_zh": raw.get("排盤方式", ""),
        "input": {"year": year, "month": month, "day": day, "hour": hour, "minute": minute},
        "tu_tru": _parse_can_chi_string(raw.get("干支", "")),
        "tu_tru_zh": raw.get("干支", ""),
        "tuan_thu": raw.get("旬首", ""),
        "tuan_khong": raw.get("旬空", {}),
        "cuc_nhat": raw.get("局日", ""),
        "bai_cuc_zh": raw.get("排局", ""),
        "bai_cuc": _parse_cuc(raw.get("排局", "")),
        "tiet_khi_zh": raw.get("節氣", ""),
        "tiet_khi_vn": TIET_KHI_VN.get(raw.get("節氣", ""), ""),
        "tri_phu_tri_su": _format_tri_phu_tri_su(raw.get("值符值使", {})),
        "thien_at": raw.get("天乙", ""),
        "thien_ban": _translate_cung_map(thien_ban_raw, "can"),
        "dia_ban": _translate_cung_map(dia_ban_raw, "can"),
        "mon": _translate_cung_map(mon_raw, "mon"),
        "tinh": _translate_cung_map(raw.get("星", {}), "tinh"),
        "than": _translate_cung_map(raw.get("神", {}), "than"),
        "ma_tinh": raw.get("馬星", ""),
        "truong_sinh_van": raw.get("長生運", ""),
        "cach_cuc_detected": cach_cuc_detected,
        "paradigm_note": (
            "Bàn này là bản đồ năng lượng thời-không tại thời điểm hỏi, "
            "phản chiếu cấu trúc vũ trụ — KHÔNG phải predict cát hung tuyệt đối. "
            "Đọc đồng dạng: Khí (bàn) → Tính (bản chất khoảnh khắc) → Đối ứng tâm cảnh."
        ),
    }


def _format_gpan(raw: dict, year: int, month: int, day: int, hour: int, minute: int) -> dict:
    """Format Golden Mirror daily chart output."""
    return {
        "method": "gpan",
        "phuong_phap_zh": "金函玉鏡 (Kim Hàm Ngọc Kính)",
        "input": {"year": year, "month": month, "day": day, "hour": hour, "minute": minute},
        "bai_cuc_zh": raw.get("局", ""),
        "bai_cuc": _parse_cuc(raw.get("局", "")),
        "hac_than": raw.get("鶴神", ""),
        "tinh": _translate_cung_map(raw.get("星", {}), "tinh"),
        "mon": _translate_cung_map(raw.get("門", {}), "mon"),
        "than": _translate_cung_map(raw.get("神", {}), "than"),
        "paradigm_note": (
            "Kim Hàm Ngọc Kính = bàn theo ngày (không phải theo giờ). "
            "Phù hợp luận đại hướng trong ngày, không chi tiết khoảnh khắc."
        ),
    }


def _format_tri_phu_tri_su(raw: dict) -> dict:
    """Translate 值符值使 dict."""
    return {
        "tri_phu_can": raw.get("值符天干", []),
        "tri_phu_tinh_cung": raw.get("值符星宮", []),
        "tri_su_mon_cung": raw.get("值使門宮", []),
    }


def detect_cach_cuc(thien_ban_raw: dict, dia_ban_raw: dict, mon_raw: dict | None = None) -> list[dict]:
    """Detect cách cục matching từ bàn KMDG (Đàm Liên Chương I phần V).

    Args:
        thien_ban_raw: dict {cung_zh: can_zh} from kinqimen output
        dia_ban_raw: dict {cung_zh: can_zh} from kinqimen output
        mon_raw: optional dict {cung_zh: mon_zh} for cách cục có môn

    Returns:
        List of matched cách cục dicts. Empty list nếu không match.
    """
    matched = []

    # Loop qua 9 cung, check conditions cho cách cục đơn giản
    for cung in thien_ban_raw:
        thien_can = thien_ban_raw.get(cung)
        dia_can = dia_ban_raw.get(cung)

        if not thien_can or not dia_can:
            continue

        # Phi Điểu Trật Huyệt: Thiên Bàn Bính, Địa Bàn Lục Giáp (=Mậu ẩn Giáp Tý)
        # Vì Giáp ẨN, mapping: Mậu=Giáp Tý, Kỷ=Giáp Tuất, etc. Bất kỳ Lục Nghi nào ở Địa Bàn = "Lục Giáp ẩn"
        if thien_can == "丙" and dia_can in {"戊", "己", "庚", "辛", "壬", "癸"}:
            cc = CACH_CUC_CANON["Phi Điểu Trật Huyệt"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên={thien_can} (Bính), Địa={dia_can} (ẩn Giáp)"
            matched.append({"name": "Phi Điểu Trật Huyệt", **cc})

        # Thanh Long Hồi Thủ: cần Trực Phù — skip auto-detect, vì cần state nhiều hơn

        # Thanh Long Đào Tẩu: Thiên Bàn Ất, Địa Bàn Tân
        if thien_can == "乙" and dia_can == "辛":
            cc = CACH_CUC_CANON["Thanh Long Đào Tẩu"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên Ất 乙, Địa Tân 辛"
            matched.append({"name": "Thanh Long Đào Tẩu", **cc})

        # Bạch Hổ Xương Cuồng: Thiên Bàn Tân, Địa Bàn Ất
        if thien_can == "辛" and dia_can == "乙":
            cc = CACH_CUC_CANON["Bạch Hổ Xương Cuồng"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên Tân 辛, Địa Ất 乙"
            matched.append({"name": "Bạch Hổ Xương Cuồng", **cc})

        # Đằng Xà Yêu Dược: Thiên Bàn Quý, Địa Bàn Đinh
        if thien_can == "癸" and dia_can == "丁":
            cc = CACH_CUC_CANON["Đằng Xà Yêu Dược"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên Quý 癸, Địa Đinh 丁"
            matched.append({"name": "Đằng Xà Yêu Dược", **cc})

        # Chu Tước Đầu Giang: Thiên Bàn Đinh, Địa Bàn Quý
        if thien_can == "丁" and dia_can == "癸":
            cc = CACH_CUC_CANON["Chu Tước Đầu Giang"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên Đinh 丁, Địa Quý 癸"
            matched.append({"name": "Chu Tước Đầu Giang", **cc})

        # Hình Cách: Thiên Bàn Canh, Địa Bàn Kỷ
        if thien_can == "庚" and dia_can == "己":
            cc = CACH_CUC_CANON["Hình Cách"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên Canh 庚, Địa Kỷ 己"
            matched.append({"name": "Hình Cách", **cc})

        # Giao Thái: Thiên Ất + Địa Đinh (HOẶC Thiên Đinh + Địa Bính)
        if (thien_can == "乙" and dia_can == "丁") or (thien_can == "丁" and dia_can == "丙"):
            cc = CACH_CUC_CANON["Giao Thái"].copy()
            cc["cung_phat_hien"] = cung
            cc["chi_tiet"] = f"Cung {cung}: Thiên={thien_can}, Địa={dia_can}"
            matched.append({"name": "Giao Thái", **cc})

    # Tam Cơ Thăng Điện: Ất→Chấn, Bính→Ly, Đinh→Đoài (3 cung concurrent)
    # Đại cát môn, kỵ Mộ bức (Đàm Liên page 47)
    if (thien_ban_raw.get("震") == "乙" and
        thien_ban_raw.get("離") == "丙" and
        thien_ban_raw.get("兌") == "丁"):
        cc = CACH_CUC_CANON["Tam Cơ Thăng Điện"].copy()
        cc["cung_phat_hien"] = "Chấn + Ly + Đoài"
        cc["chi_tiet"] = "Ất tại Chấn + Bính tại Ly + Đinh tại Đoài — VẠN SỰ"
        matched.append({"name": "Tam Cơ Thăng Điện", **cc})

    # Tam Kỳ đắc Lộc: Ất→Chấn, Bính→Tốn, Đinh→Ly
    if (thien_ban_raw.get("震") == "乙" and
        thien_ban_raw.get("巽") == "丙" and
        thien_ban_raw.get("離") == "丁"):
        cc = CACH_CUC_CANON["Tam Kỳ đắc Lộc"].copy()
        cc["cung_phat_hien"] = "Chấn + Tốn + Ly"
        cc["chi_tiet"] = "Ất tại Chấn + Bính tại Tốn + Đinh tại Ly"
        matched.append({"name": "Tam Kỳ đắc Lộc", **cc})

    return matched


def _parse_cuc(s: str) -> dict:
    """Parse '陽遁九局下元' → {duong_am, cuc_so, nguyen}."""
    if not s:
        return {}
    result = {"raw_zh": s}
    if s.startswith("陽遁"):
        result["duong_am"] = "Dương Cục"
    elif s.startswith("陰遁"):
        result["duong_am"] = "Âm Cục"
    cuc_so_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                  "六": 6, "七": 7, "八": 8, "九": 9}
    for zh, num in cuc_so_map.items():
        if zh + "局" in s:
            result["cuc_so"] = num
            break
    if "上元" in s:
        result["nguyen"] = "Thượng nguyên"
    elif "中元" in s:
        result["nguyen"] = "Trung nguyên"
    elif "下元" in s:
        result["nguyen"] = "Hạ nguyên"
    return result
