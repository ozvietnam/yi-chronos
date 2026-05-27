"""Tài Vận (財運) — wealth analysis from Bát Tự chart.

Paradigm (Iron Rule #4+6): Phân tích Tài Vận KHÔNG dự đoán "anh sẽ giàu năm X".
Đọc **cấu trúc Tài tinh + Day Master balance + patterns kinh điển** → mô tả
XU HƯỚNG tài lộc + thời điểm thuận + cảnh báo phá tài.

Source: Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (Q. 4-6 về Tài + Lục Thân).

3 nguyên tắc cốt yếu (từ Chương 3-4 sách):

1. **Day Master vượng đủ gánh Tài** — DM weak + Tài vượng = "Tài đa thân nhược",
   có tài cũng khó giữ. Cần Tỷ/Kiếp hoặc Ấn cứu thân trước.

2. **Tài tinh cần được "sinh"** — Thực Thương sinh Tài là cấu hình PHÚ kinh điển.
   Tài đơn độc không nguồn → tài đến rồi đi.

3. **Tài + Kiếp + Tỷ** trong cùng lá số → cảnh báo "Kiếp Tài đoạt Tài":
   bạn bè/cộng sự cùng giới cướp tài, hoặc đầu tư mất.

Algorithm:
1. Map Tài tinh (Chính + Thiên) — visible + hidden positions
2. Đánh giá Tài strength
3. Đánh giá DM-Tài balance (4 trạng thái)
4. Detect 6 patterns: Thực Thương sinh Tài / Kiếp đoạt Tài / Quan-Tài hỗ trợ / Ấn-Tài xung đột / Tài đa thân nhược / Thân vượng Tài nhược
5. Đại Vận tài timing (rank cycles)
6. Lưu Niên tài (current year)
7. Sources interpretation (Chính vs Thiên Tài)
8. Strategy recommendations
"""

from __future__ import annotations

from .constants import BRANCH_ELEMENT, ELEMENT_CONTROLS, STEM_ELEMENT
from .thap_than import thap_than_of


# ─── Reference tables ───────────────────────────────────────────────────────

TAI_SOURCE_TRAITS: dict[str, dict[str, str]] = {
    "Chính Tài": {
        "essence": "Tài chính ỔN ĐỊNH — lương cứng, tích lũy bền vững, vợ chính (nam).",
        "favorable": "Day Master vượng + Tài vượng → đại phú. Cần Thực Thương sinh Tài.",
        "kỵ": "Kiếp Tài cướp đoạt. Day Master nhược không gánh nổi Tài.",
        "career": "tài chính/kế toán, kinh doanh truyền thống, bất động sản cho thuê",
    },
    "Thiên Tài": {
        "essence": "Tài lộc BẤT NGỜ + đào hoa + đầu cơ. Cha (nam) + tài phụ.",
        "favorable": "Day Master vượng → kinh doanh đa lĩnh vực, có sức hút thu hút khách.",
        "kỵ": "Tỉ Kiếp cướp Tài. Quá nhiều → tiền đến nhanh đi nhanh.",
        "career": "kinh doanh đa lĩnh vực, môi giới, đầu cơ, marketing có sức hút",
    },
}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _map_tai_positions(pillars: dict, day_master: str) -> dict:
    """Map all Tài tinh (Chính + Thiên) positions trong lá số."""
    chinh_tai = []
    thien_tai = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        # Visible stem (skip day pillar's own stem = Bản thân)
        if pos != "day":
            stem_tt = thap_than_of(day_master, p["stem"])
            if stem_tt == "Chính Tài":
                chinh_tai.append({"position": pos, "position_vi": p.get("position_vi"),
                                  "type": "visible_stem", "stem": p["stem"]})
            elif stem_tt == "Thiên Tài":
                thien_tai.append({"position": pos, "position_vi": p.get("position_vi"),
                                  "type": "visible_stem", "stem": p["stem"]})
        # Hidden stems in branches
        for hs in p["hidden_stems"]:
            if hs == day_master and pos == "day":
                continue
            tt = thap_than_of(day_master, hs)
            if tt == "Chính Tài":
                chinh_tai.append({"position": pos, "position_vi": p.get("position_vi"),
                                  "type": "hidden_stem", "stem": hs,
                                  "branch": p["branch"]})
            elif tt == "Thiên Tài":
                thien_tai.append({"position": pos, "position_vi": p.get("position_vi"),
                                  "type": "hidden_stem", "stem": hs,
                                  "branch": p["branch"]})
    return {
        "chinh_tai_positions": chinh_tai,
        "thien_tai_positions": thien_tai,
        "total_chinh_tai": len(chinh_tai),
        "total_thien_tai": len(thien_tai),
        "total_count": len(chinh_tai) + len(thien_tai),
    }


def _dm_tai_balance(dm_tag: str, total_tai: int, dm_diff: float) -> dict:
    """Đánh giá Day Master vs Tài balance — 4 trạng thái cốt yếu."""
    if dm_tag in ("strong", "balanced") and total_tai >= 2:
        return {
            "status": "ưu — Thân vượng Tài vượng",
            "polarity": "lành",
            "narrative": (
                "Day Master VƯỢNG + Tài tinh VƯỢNG → cấu hình PHÚ. "
                "Có khả năng 'gánh' Tài tốt. Cần Thực Thương sinh Tài để tài lộc bền vững."
            ),
            "recommend": "Khởi nghiệp / kinh doanh / tích lũy. Day Master đủ sức chịu áp lực tài.",
        }
    if dm_tag in ("strong", "balanced") and total_tai < 2:
        return {
            "status": "trung — Thân vượng Tài nhược",
            "polarity": "trung tính",
            "narrative": (
                "Day Master vượng + Tài tinh nhược → có sức nhưng thiếu nguồn tài. "
                "Cần Thực Thương sinh Tài hoặc Đại Vận tài vượng để kích hoạt."
            ),
            "recommend": "Bồi dưỡng kỹ năng tạo Tài (Thực Thương — sáng tạo + lao động). "
                         "Đợi Đại Vận đi vào Tài.",
        }
    if dm_tag == "weak" and total_tai >= 3:
        return {
            "status": "hung — Tài đa thân nhược",
            "polarity": "cảnh báo cao",
            "narrative": (
                "Day Master nhược + Tài tinh quá vượng → 'Tài đa thân nhược', "
                "có tài cũng không gánh nổi. Khó giữ, dễ phá."
            ),
            "recommend": "Ưu tiên BỒI THÂN trước (Ấn + Tỷ/Kiếp). KHÔNG vội khởi nghiệp + "
                         "kinh doanh áp lực cao. Ưu tiên lương cứng + tích nội lực.",
        }
    if dm_tag == "weak":
        return {
            "status": "nhược — Cần cứu thân trước",
            "polarity": "trung tính",
            "narrative": (
                "Day Master nhược + Tài tinh không nhiều → trước tiên bồi thân. "
                "Đại Vận đi vào Ấn / Tỷ Kiếp → tích nội lực."
            ),
            "recommend": "Ưu tiên học vấn (Chính Ấn) + đối tác (Tỷ/Kiếp). "
                         "Đợi đời thứ 2 Đại Vận tài để khởi nghiệp.",
        }
    return {
        "status": "không xác định",
        "polarity": "trung tính",
        "narrative": f"Không xác định rõ DM vs Tài (dm_tag={dm_tag}, total_tai={total_tai}).",
        "recommend": "",
    }


def _detect_tai_patterns(thap_than_dist: dict, dm_tag: str) -> list[dict]:
    """Detect 6 patterns kinh điển về Tài."""
    visible = thap_than_dist.get("visible", {})
    hidden = thap_than_dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    count = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0)
    patterns = []

    # Pattern 1: Thực Thương sinh Tài (kinh điển PHÚ)
    if (has("Chính Tài") or has("Thiên Tài")) and (has("Thực Thần") or has("Thương Quan")):
        patterns.append({
            "name": "Thực Thương sinh Tài",
            "polarity": "lành — kinh điển PHÚ",
            "narrative": (
                "Thực Thần / Thương Quan SINH Tài → cấu hình tài lộc bền vững. "
                "Sáng tạo + lao động + kinh doanh = tài lộc đến qua chính sức mình. "
                "Đây là 1 trong 3 cấu hình PHÚ kinh điển của Tử Bình."
            ),
            "actionable": "Chọn nghề liên quan đến sáng tạo + thương mại. "
                          "Đầu tư vào kỹ năng tạo sản phẩm/dịch vụ.",
        })

    # Pattern 2: Kiếp Tài đoạt Tài
    if (has("Chính Tài") or has("Thiên Tài")) and has("Kiếp Tài"):
        patterns.append({
            "name": "Kiếp Tài đoạt Tài",
            "polarity": "cảnh báo — phá tài",
            "narrative": (
                "Tài tinh + Kiếp Tài đồng lộ → đề phòng TỔN TÀI từ bạn bè/cộng sự, "
                "đầu tư rủi ro cao, hoặc cạnh tranh trực diện cướp khách. "
                "Đặc biệt nguy hiểm khi Đại Vận Kiếp Tài vào."
            ),
            "actionable": "Cẩn trọng partnership tài chính. Tránh cho mượn tiền nhóm bạn. "
                          "Diversify, không bỏ trứng vào 1 giỏ.",
        })

    # Pattern 3: Quan-Tài hỗ trợ
    if (has("Chính Tài") or has("Thiên Tài")) and (has("Chính Quan") or has("Thất Sát")):
        patterns.append({
            "name": "Tài-Quan tương sinh",
            "polarity": "lành — quý + phú",
            "narrative": (
                "Tài sinh Quan → Tài lộc đi cùng danh tiếng / chức vụ. "
                "Quan bảo vệ Tài → không bị Kiếp đoạt. Cấu hình QUÝ + PHÚ kép."
            ),
            "actionable": "Hợp công chức + kinh doanh side, hoặc kinh doanh + đầu tư chức vụ.",
        })

    # Pattern 4: Tài đoạt Ấn (Chính Tài phá Chính Ấn)
    if has("Chính Tài") and has("Chính Ấn"):
        patterns.append({
            "name": "Tài đoạt Ấn",
            "polarity": "cảnh báo — học vấn vs tài",
            "narrative": (
                "Chính Tài + Chính Ấn xung đột (Tài khắc Ấn). "
                "Có thể giữa học vấn/từ thiện và tài lộc khó cân bằng — "
                "chọn 1 hướng phát triển sâu thay vì cả 2."
            ),
            "actionable": "Quyết định: học thuật-từ thiện sâu HOẶC kinh doanh-tài lộc. "
                          "Khó dung hòa cả 2 ở mức cao.",
        })

    # Pattern 5: Tài đa thân nhược (DM weak + nhiều Tài)
    if dm_tag == "weak" and (count("Chính Tài") + count("Thiên Tài")) >= 3:
        patterns.append({
            "name": "Tài đa thân nhược",
            "polarity": "cảnh báo cao — có tài không giữ được",
            "narrative": (
                "Day Master yếu mà Tài tinh quá nhiều → có tiền cũng khó giữ, "
                "dễ vướng nợ, đầu tư mất. Cần Tỷ/Kiếp hoặc Ấn cứu thân TRƯỚC."
            ),
            "actionable": "Hạn chế áp lực tài chính. Ưu tiên xây sức khỏe + đối tác + học vấn. "
                          "Đợi vận Ấn / Tỷ.",
        })

    # Pattern 6: Thân vượng Tài cô đơn (DM vượng nhưng Tài quá nhược)
    if dm_tag == "strong" and (count("Chính Tài") + count("Thiên Tài")) <= 1:
        patterns.append({
            "name": "Thân vượng Tài nhược",
            "polarity": "trung tính — thiếu kích hoạt",
            "narrative": (
                "Day Master vượng nhưng Tài tinh quá nhược → có sức nhưng thiếu nguồn tài. "
                "Cần Đại Vận / Lưu Niên đi vào Tài + Thực Thương để kích hoạt."
            ),
            "actionable": "Bồi dưỡng Thực/Thương (sáng tạo, kỹ năng) để 'sinh' Tài. "
                          "Đợi Đại Vận tài vận đến.",
        })

    return patterns


def _dai_van_tai_timing(dai_van_cycles: list[dict],
                         day_master_el: str,
                         dung_than_el: str) -> list[dict]:
    """Rank Đại Vận cycles theo Tài tinh activation."""
    # Tài element = element bị day_master khắc
    tai_el = ELEMENT_CONTROLS.get(day_master_el)
    if not tai_el:
        return []
    out = []
    for c in dai_van_cycles:
        stem_el = STEM_ELEMENT.get(c.get("stem", ""))
        branch_el = BRANCH_ELEMENT.get(c.get("branch", ""))
        elements = {stem_el, branch_el}
        score = 0
        reasons = []
        if tai_el in elements:
            score += 2
            reasons.append(f"có khí Tài ({tai_el})")
        if dung_than_el in elements:
            score += 1
            reasons.append(f"hợp Dụng Thần ({dung_than_el})")
        # Element generating tai (Thực/Thương) cũng tốt
        for el, target in [("mộc", "hỏa"), ("hỏa", "thổ"), ("thổ", "kim"),
                          ("kim", "thủy"), ("thủy", "mộc")]:
            if target == tai_el and el in elements:
                score += 1
                reasons.append(f"sinh Tài qua khí {el}")
                break

        if score >= 2:
            verdict = "tài lộc kích hoạt"
            mark = "✦"
        elif score == 1:
            verdict = "tài lộc bình"
            mark = "·"
        else:
            verdict = "tài lộc yên"
            mark = "○"
        out.append({
            **c,
            "stem_element": stem_el,
            "branch_element": branch_el,
            "score": score,
            "reasons": reasons,
            "verdict": verdict,
            "mark": mark,
        })
    return out


def _suggest_strategy(dm_tag: str, balance: dict, patterns: list[dict]) -> list[str]:
    """Compose strategic recommendations dựa trên DM-Tài balance + patterns."""
    out = []
    pattern_names = {p["name"] for p in patterns}

    if balance["status"].startswith("ưu"):
        out.append("✦ Cấu hình PHÚ — có thể khởi nghiệp, kinh doanh, tích lũy.")
    elif balance["status"].startswith("hung"):
        out.append("⚠ HẠN CHẾ áp lực tài lớn. Bồi thân trước, đợi vận thuận.")
    elif balance["status"].startswith("trung"):
        out.append("· Cần kích hoạt Tài — đợi Đại Vận Tài hoặc rèn Thực Thương.")
    elif balance["status"].startswith("nhược"):
        out.append("· Ưu tiên học vấn + đối tác. Đời 1 (Tỷ/Ấn) bồi thân, đời 2 (Tài) phát.")

    if "Thực Thương sinh Tài" in pattern_names:
        out.append("✦ Khai thác cấu hình Thực Thương sinh Tài: chọn nghề sáng tạo + thương mại.")
    if "Kiếp Tài đoạt Tài" in pattern_names:
        out.append("⚠ Cẩn trọng partnership tài chính, tránh đầu tư nhóm bạn cùng giới.")
    if "Tài-Quan tương sinh" in pattern_names:
        out.append("✦ Quý + Phú kép — kết hợp công chức + side hustle, hoặc kinh doanh + danh tiếng.")
    if "Tài đoạt Ấn" in pattern_names:
        out.append("⚖ Quyết định: học thuật/từ thiện HOẶC kinh doanh. Không dung hòa cả 2.")
    if "Tài đa thân nhược" in pattern_names:
        out.append("⚠ Khẩn cấp bồi thân. Ưu tiên sức khỏe + đối tác + học vấn trước tiền.")

    if not out:
        out.append("Cấu trúc tài trung tính — duy trì + chờ tín hiệu Đại Vận / Lưu Niên.")
    return out


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_tai_van_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ. "
    "Tài tinh + DM-Tài balance + 6 patterns kinh điển (Q. 4-6)."
)


def analyze_tai_van(bat_tu_state: dict) -> dict:
    """Phân tích Tài Vận từ lá số Bát Tự.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)`.

    Returns:
        Structured dict 8 sections.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key")

    pillars = bat_tu_state["tu_tru"]["pillars"]
    day_master = bat_tu_state["tu_tru"]["day_master"]["stem"]
    day_master_el = bat_tu_state["tu_tru"]["day_master"]["element"]
    dm_tag = bat_tu_state["ngu_hanh"]["day_master_assessment"]["strength_tag"]
    dm_diff = (bat_tu_state["ngu_hanh"]["day_master_assessment"].get("support_score", 0)
               - bat_tu_state["ngu_hanh"]["day_master_assessment"].get("drain_score", 0))
    thap_than_dist = bat_tu_state.get("thap_than_distribution", {})
    dai_van = bat_tu_state.get("dai_van", {})
    dung_than = bat_tu_state.get("dung_than", {})

    tai_map = _map_tai_positions(pillars, day_master)
    balance = _dm_tai_balance(dm_tag, tai_map["total_count"], dm_diff)
    patterns = _detect_tai_patterns(thap_than_dist, dm_tag)
    timing = _dai_van_tai_timing(
        dai_van.get("cycles", []), day_master_el,
        dung_than.get("dung_than_element", "")
    )
    strategy = _suggest_strategy(dm_tag, balance, patterns)

    # Sources interpretation
    sources_narr = []
    if tai_map["total_chinh_tai"] > 0:
        sources_narr.append({
            "type": "Chính Tài",
            "count": tai_map["total_chinh_tai"],
            **TAI_SOURCE_TRAITS["Chính Tài"],
        })
    if tai_map["total_thien_tai"] > 0:
        sources_narr.append({
            "type": "Thiên Tài",
            "count": tai_map["total_thien_tai"],
            **TAI_SOURCE_TRAITS["Thiên Tài"],
        })
    if not sources_narr:
        sources_narr = [{
            "type": "Tài tinh vắng mặt",
            "count": 0,
            "essence": "Lá số không có Tài tinh visible hoặc hidden — "
                       "tài lộc đến qua Đại Vận / Lưu Niên khi khí Tài xuất hiện.",
            "favorable": "Cần đợi vận tài đến.",
            "kỵ": "Khi chưa có vận tài, tránh áp lực tài chính.",
            "career": "Bồi nội lực (Ấn / học vấn) hoặc Thực Thương (sáng tạo) trước.",
        }]

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Phân tích Tài Vận KHÔNG dự đoán anh sẽ giàu năm X. "
            "Đọc cấu trúc Tài tinh + DM balance + 6 patterns kinh điển → "
            "mô tả xu hướng tài lộc + thời điểm thuận + cảnh báo phá tài."
        ),
        "tai_map": tai_map,
        "dm_tai_balance": balance,
        "patterns": patterns,
        "sources": sources_narr,
        "dai_van_tai_timing": timing,
        "strategy": strategy,
        "closing": (
            "Tài lộc KHÔNG cố định bởi số mệnh. Lá số chỉ cho thấy CẤU HÌNH KHÍ tài "
            "(tài tinh + Day Master + patterns) → bản đồ thuận-nghịch. "
            "Tri mệnh để chọn cách đi: khi nào tích, khi nào phá, khi nào đợi."
        ),
    }
