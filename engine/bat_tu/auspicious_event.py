"""Auspicious Event Picker — chọn ngày/giờ thuận cho event cụ thể dựa trên Bát Tự.

Paradigm (Iron Rule #4+6): KHÔNG dự đoán "ngày X chắc chắn tốt". Đọc cấu trúc khí
của ngày candidate vs lá số user + nature of event → rank thuận hay nghịch.

Event types support:
- 'wedding' (hôn lễ): cần Tài/Quan hợp + tránh xung Trụ Ngày
- 'business_opening' (khai trương): cần Tài hợp + Dụng Thần
- 'moving_house' (di chuyển/chuyển nhà): cần Dịch Mã + tránh xung
- 'signing_contract' (ký hợp đồng): cần Quan Tinh hợp + tránh Thương Quan
- 'travel' (đi xa): cần Dịch Mã + tránh Lục Hại

Algorithm:
1. Convert candidate date range → Bát Tự day pillars (mỗi ngày)
2. For each candidate day:
   - Element of day stem + branch
   - Compare with user's Dụng Thần / Hỷ Thần / Kỵ Thần
   - Compare with user's Trụ Ngày (cung phối) — tránh xung
   - Event-specific scoring
3. Rank candidates, return top N
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .constants import BRANCH_ELEMENT, STEM_ELEMENT
from .luu_nien import LUC_HAI, LUC_HOP, LUC_XUNG, TAM_HINH_GROUPS


# ─── Event type rules ────────────────────────────────────────────────────────

EVENT_RULES: dict[str, dict] = {
    "wedding": {
        "label": "Hôn lễ / Cưới hỏi",
        "favorable_factors": ["Dụng Thần", "Hỷ Thần", "lục hợp Trụ Ngày", "Hồng Loan", "Thiên Hỷ"],
        "avoid_factors": ["lục xung Trụ Ngày", "Cô Thần", "Quả Tú",
                          "Kỵ Thần mạnh", "Tam Hình"],
        "polarity_weights": {
            "dung_match": 3, "hy_match": 2,
            "luc_hop": 3, "luc_xung": -5,
            "luc_hai": -3, "tam_hinh": -3,
        },
        "narrative": (
            "Hôn lễ cần khí HỢP (lục hợp) + Tài/Quan thuận + tránh xung Trụ Ngày "
            "(chi vợ/chồng). Ngày Đạo hoa nhẹ cũng tốt."
        ),
    },
    "business_opening": {
        "label": "Khai trương / Khởi nghiệp",
        "favorable_factors": ["Dụng Thần", "Tài tinh ngày", "Lộc Thần", "Quan tinh"],
        "avoid_factors": ["Kiếp Tài ngày", "Kỵ Thần", "Tang Môn", "lục xung"],
        "polarity_weights": {
            "dung_match": 4, "hy_match": 2,
            "luc_hop": 2, "luc_xung": -4,
            "luc_hai": -2, "tam_hinh": -2,
        },
        "narrative": (
            "Khai trương cần khí Tài + Dụng Thần kích hoạt. Tránh ngày Kiếp Tài "
            "(cướp tài) + ngày xung Trụ Ngày (gặp trở ngại đối tác)."
        ),
    },
    "moving_house": {
        "label": "Chuyển nhà / Di chuyển",
        "favorable_factors": ["Dịch Mã", "Lục hợp", "Dụng Thần"],
        "avoid_factors": ["Sát chính", "lục xung", "Tang Môn", "Bệnh Phù"],
        "polarity_weights": {
            "dung_match": 2, "hy_match": 1,
            "luc_hop": 3, "luc_xung": -4,
            "luc_hai": -3, "tam_hinh": -2,
        },
        "narrative": (
            "Chuyển nhà cần khí ổn định (lục hợp), tránh xung phá (lục xung). "
            "Dịch Mã ngày tốt cho di chuyển xa."
        ),
    },
    "signing_contract": {
        "label": "Ký hợp đồng / Hợp tác",
        "favorable_factors": ["Quan tinh ngày", "Chính Ấn", "Dụng Thần", "Thiên Đức"],
        "avoid_factors": ["Thương Quan ngày", "Kiếp Tài", "lục xung", "Tam Hình"],
        "polarity_weights": {
            "dung_match": 3, "hy_match": 2,
            "luc_hop": 3, "luc_xung": -4,
            "luc_hai": -3, "tam_hinh": -3,
        },
        "narrative": (
            "Ký hợp đồng cần khí Quan + Ấn (tin tưởng, chính danh). Tránh Thương Quan "
            "(phá Quan, đổ vỡ thỏa thuận) + lục xung (lật kèo)."
        ),
    },
    "travel": {
        "label": "Đi xa / Du lịch",
        "favorable_factors": ["Dịch Mã", "Thiên Hỷ", "lục hợp"],
        "avoid_factors": ["lục xung", "Kiếp Sát", "Vong Thần", "Tang Môn"],
        "polarity_weights": {
            "dung_match": 1, "hy_match": 1,
            "luc_hop": 2, "luc_xung": -3,
            "luc_hai": -3, "tam_hinh": -2,
        },
        "narrative": "Đi xa cần Dịch Mã + tránh Lục Xung. An toàn = ưu tiên hàng đầu.",
    },
    "general": {
        "label": "Việc tổng quát",
        "favorable_factors": ["Dụng Thần", "Hỷ Thần", "Lục Hợp"],
        "avoid_factors": ["Kỵ Thần", "lục xung", "Tam Hình"],
        "polarity_weights": {
            "dung_match": 2, "hy_match": 1,
            "luc_hop": 2, "luc_xung": -3,
            "luc_hai": -2, "tam_hinh": -2,
        },
        "narrative": "Việc tổng quát: ưu tiên ngày hợp Dụng Thần + tránh ngày xung Trụ Ngày.",
    },
}


# ─── Day pillar computation ──────────────────────────────────────────────────


def _get_day_pillar(target_date_iso: str, timezone: str = "Asia/Ho_Chi_Minh") -> dict:
    """Compute Trụ Ngày (day pillar) cho 1 ngày dương lịch."""
    from core.chronos import calculate_chronos_state
    # Sử dụng 12:00 trưa làm reference
    dt_str = f"{target_date_iso}T12:00"
    chronos = calculate_chronos_state(dt_str, timezone)
    parts = chronos.ganzhi.day.split()
    if len(parts) != 2:
        return {}
    stem, branch = parts
    return {
        "date": target_date_iso,
        "stem": stem,
        "branch": branch,
        "stem_element": STEM_ELEMENT.get(stem, ""),
        "branch_element": BRANCH_ELEMENT.get(branch, ""),
    }


def _score_candidate(day_pillar: dict, user_chart: dict, event_rules: dict) -> dict:
    """Score 1 candidate day against user chart + event rules."""
    if not day_pillar:
        return {"score": -99, "reasons": ["invalid day pillar"]}

    user_pillars = user_chart["tu_tru"]["pillars"]
    user_day_branch = user_pillars["day"]["branch"]
    dung_than = user_chart.get("dung_than", {})
    dung_el = dung_than.get("dung_than_element", "")
    hy_el = dung_than.get("hy_than_element", "")
    ky_el = dung_than.get("ky_than_element", "")
    weights = event_rules["polarity_weights"]

    score = 0
    reasons = []
    day_stem_el = day_pillar["stem_element"]
    day_branch_el = day_pillar["branch_element"]
    day_branch = day_pillar["branch"]
    day_elements = {day_stem_el, day_branch_el}

    # Dụng / Hỷ / Kỵ Thần matching
    if dung_el in day_elements:
        score += weights["dung_match"]
        reasons.append(f"+{weights['dung_match']} có khí Dụng Thần ({dung_el})")
    if hy_el in day_elements:
        score += weights["hy_match"]
        reasons.append(f"+{weights['hy_match']} có khí Hỷ Thần ({hy_el})")
    if ky_el in day_elements:
        score += -2
        reasons.append(f"-2 có khí Kỵ Thần ({ky_el})")

    # Chi day vs Trụ Ngày (user)
    pair = frozenset([day_branch, user_day_branch])
    if day_branch == user_day_branch:
        # đồng chi: neutral
        reasons.append("đồng chi với Trụ Ngày (trung tính)")
    if pair in LUC_HOP:
        score += weights["luc_hop"]
        reasons.append(f"+{weights['luc_hop']} lục hợp Trụ Ngày ({day_branch}+{user_day_branch})")
    if pair in LUC_XUNG:
        score += weights["luc_xung"]
        reasons.append(f"{weights['luc_xung']} lục xung Trụ Ngày ({day_branch}⚔{user_day_branch})")
    if pair in LUC_HAI:
        score += weights["luc_hai"]
        reasons.append(f"{weights['luc_hai']} lục hại Trụ Ngày")
    for group in TAM_HINH_GROUPS:
        if day_branch in group and user_day_branch in group and day_branch != user_day_branch:
            score += weights["tam_hinh"]
            reasons.append(f"{weights['tam_hinh']} tương hình Trụ Ngày")
            break

    # Optional: check against Trụ Năm (xung Thái Tuế = chocking)
    user_year_branch = user_pillars["year"]["branch"]
    pair_year = frozenset([day_branch, user_year_branch])
    if pair_year in LUC_XUNG:
        score -= 1
        reasons.append("-1 xung Trụ Năm (Thái Tuế nhẹ)")

    return {
        "score": score,
        "reasons": reasons,
        "day_pillar": day_pillar,
    }


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_auspicious_event_v1"
SOURCE_REF = "Tử Bình + tradition chọn ngày (黃道). Match Dụng Thần + tránh xung Trụ Ngày."


def pick_auspicious_dates(
    user_chart: dict,
    *,
    event_type: str = "general",
    start_date: str,
    end_date: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    top_n: int = 10,
) -> dict:
    """Pick auspicious dates in a range for a specific event.

    Args:
        user_chart: Output of `cast_bat_tu(...)`
        event_type: 'wedding' / 'business_opening' / 'moving_house' / 'signing_contract' / 'travel' / 'general'
        start_date: ISO date 'YYYY-MM-DD'
        end_date: ISO date 'YYYY-MM-DD'
        timezone: TZ for day pillar computation
        top_n: top N candidates to return

    Returns:
        Dict with ranked candidates + paradigm narrative.
    """
    if "tu_tru" not in user_chart:
        raise ValueError("user_chart must contain 'tu_tru' key")
    event_rules = EVENT_RULES.get(event_type, EVENT_RULES["general"])

    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {e}")
    if (end_dt - start_dt).days > 90:
        raise ValueError("Date range too large (max 90 days)")
    if end_dt < start_dt:
        raise ValueError("end_date must be after start_date")

    # Scan every day in range
    candidates = []
    current = start_dt
    while current <= end_dt:
        day_pillar = _get_day_pillar(current.isoformat(), timezone)
        scored = _score_candidate(day_pillar, user_chart, event_rules)
        scored["date"] = current.isoformat()
        scored["weekday"] = current.strftime("%A")
        candidates.append(scored)
        current += timedelta(days=1)

    # Sort by score desc
    candidates.sort(key=lambda c: -c["score"])
    top = candidates[:top_n]
    bottom = sorted(candidates, key=lambda c: c["score"])[:5]  # worst 5

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Pick auspicious dates KHÔNG đảm bảo việc sẽ thành công. "
            "Đọc cấu hình khí ngày vs lá số + event nature → rank thuận-nghịch. "
            "Lựa chọn ngày + thực hành có ý thức = chìa khóa, không phải ngày tốt tự dưng cho kết quả."
        ),
        "event_type": event_type,
        "event_label": event_rules["label"],
        "event_narrative": event_rules["narrative"],
        "date_range": {"start": start_date, "end": end_date},
        "user_day_pillar": {
            "stem": user_chart["tu_tru"]["pillars"]["day"]["stem"],
            "branch": user_chart["tu_tru"]["pillars"]["day"]["branch"],
        },
        "dung_than_element": user_chart.get("dung_than", {}).get("dung_than_element"),
        "top_candidates": top,
        "avoid_dates": bottom,
        "total_scanned": len(candidates),
        "closing": (
            "Ngày tốt = ngày có khí thuận. Nhưng làm việc lớn cần CHUẨN BỊ + Ý THỨC + "
            "ĐỘI NGŨ + LOGIC. Bát Tự chỉ là 1 lớp lựa chọn. Không phụ thuộc 100%."
        ),
    }
