"""Luận giải tổng hợp Bát Tự (Comprehensive interpretation engine).

Synthesize the multi-layer output of `cast_bat_tu` into a structured narrative
that respects the paradigm taught by Thiệu Vĩ Hoa & Trần Viên in
_Dự đoán theo Tứ trụ_ (NXB Văn hóa Thông tin, 1994):

- Tử Bình KHÔNG predict-tool ("anh sẽ giàu/nghèo").
- Tử Bình = đọc cấu trúc khí bẩm sinh + lưu biến → tri mệnh → BỔ cân bằng.
- "Mệnh cố kết, vận lưu biến" (cùng paradigm Tử Vi Iron Rule #6 — CƠ + BIẾN).

10 patterns encoded (from Chương 3 sách Thiệu Vĩ Hoa, tr. 50-100):
1. 5 quy tắc Vượng Thân — verify day_master.strength_tag
2. Sinh-Khắc 10 Thần dynamic — detect favorable combinations
3. "Vật đến cực tất quay trở lại" — warn excess (count > 4)
4. Công năng 4 cánh của mỗi Thần — encode as narrative
5. Tâm tính positive + negative — from dominant Thập Thần
6. "Tài bị Kiếp đoạt" — warn Tài + Kiếp Tài combination
7. "Thương Quan kiến Quan" — major warning
8. "Thực Thần chế Sát" / "Ấn hóa Sát" — favorable combinations
9. Thông quan — detect 2 opposing elements + suggest mediator
10. "Có thuốc" — Day Master vs Dụng Thần alignment with current Đại Vận

Output: dict ready for JSON serialization to /api/bat-tu/luan-giai endpoint.

Reference: docs/design/bat-tu-thieu-vi-hoa-tham-nhuan.md (Phần C).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import FIVE_ELEMENTS, PILLAR_DOMAIN, STEM_ELEMENT, THAP_THAN_MEANING


# ─── Reference tables for narrative composition ──────────────────────────────

# Element → 5 đức tính (from Chương 2 tr. 25-26)
ELEMENT_DUC_TINH: dict[str, dict[str, str]] = {
    "mộc": {
        "duc": "NHÂN",
        "vuong": "thẳng thắn, ôn hòa, bác ái, thanh cao, không giả dối",
        "suy": "hẹp hòi, đố kị, không quyết đoán",
    },
    "hỏa": {
        "duc": "LỄ",
        "vuong": "lễ độ, hoạt bát, cung kính, sáng tỏ, năng động",
        "suy": "dối trá, cay độc, làm việc không đầu đuôi",
    },
    "thổ": {
        "duc": "TÍN",
        "vuong": "trung hậu, chân thành, độ lượng, giữ lời hứa",
        "suy": "cứng nhắc, ác độc, bất tín, vô tình",
    },
    "kim": {
        "duc": "NGHĨA",
        "vuong": "cương trực, mãnh liệt, quyết đoán, trọng nghĩa khinh tài",
        "suy": "nham hiểm, ham dâm, biến lận, tham lam",
    },
    "thủy": {
        "duc": "TRÍ",
        "vuong": "thông minh, hiền lành, túc trí đa mưu, lưu động",
        "suy": "vô mưu, hành động không thứ tự, tính linh tinh",
    },
}

# Element → "Bổ" recommendations (from Chương 2 tr. 26)
ELEMENT_BO_HUONG: dict[str, dict[str, list[str]]] = {
    "mộc": {
        "nghe_nghiep": ["mộc", "giấy", "trồng cây/hoa", "chăm sóc cây non", "hương liệu", "phẩm vật tế lễ"],
        "mau_sac": ["xanh lá", "xanh ngọc"],
        "phuong_vi": ["Đông"],
        "am_thuc": ["chua", "rau xanh", "trái cây tươi"],
    },
    "hỏa": {
        "nghe_nghiep": ["chiếu sáng/quang học", "nhiệt độ cao", "dầu/rượu", "thực phẩm nóng",
                       "cắt tóc/trang điểm", "văn nghệ/văn học", "giáo viên/thư ký",
                       "xuất bản/sáng tác", "công vụ"],
        "mau_sac": ["đỏ", "tím", "cam"],
        "phuong_vi": ["Nam"],
        "am_thuc": ["đắng", "cay nóng", "thực phẩm nướng"],
    },
    "thổ": {
        "nghe_nghiep": ["thổ sản/đất đai/nông thôn", "chăn nuôi", "vải vóc/thêu dệt",
                       "đá/than/xi măng/kiến trúc", "mua bán nhà ở", "trung gian/môi giới",
                       "luật sư", "quản lí", "thiết kế", "cố vấn"],
        "mau_sac": ["vàng đất", "nâu"],
        "phuong_vi": ["Trung (giữa)", "Tây Nam", "Đông Bắc"],
        "am_thuc": ["ngọt vừa", "thực phẩm tinh bột", "ngũ cốc"],
    },
    "thủy": {
        "nghe_nghiep": ["hàng hải/thủy sản", "dung dịch không cháy", "nước đá",
                       "thủy lợi", "đồ ướp lạnh", "câu cá", "y tá/dược liệu",
                       "ảo thuật/du lịch", "trinh sát/kí giả", "chiêm bốc"],
        "mau_sac": ["đen", "xanh nước biển sâu"],
        "phuong_vi": ["Bắc"],
        "am_thuc": ["mặn", "thủy sản", "canh", "đồ uống"],
    },
    "kim": {
        "nghe_nghiep": ["kim loại/cơ khí", "võ thuật/giám định",
                       "quan thanh liêm/tổng quản", "ô tô/giao thông", "kim hoàn",
                       "công trình", "khai thác mỏ/gỗ"],
        "mau_sac": ["trắng", "bạc", "xám sáng"],
        "phuong_vi": ["Tây"],
        "am_thuc": ["cay nhẹ", "thực phẩm sắc gọn", "gia vị khô"],
    },
}

# Công năng 4 cánh mỗi Thần (from Chương 3 tr. 83-87)
THAP_THAN_FUNCTION: dict[str, str] = {
    "Chính Quan": (
        "**Bảo vệ Tài + sinh Ấn + áp chế thân + khắc chế Kiếp.** "
        "Khi Day Master vượng, Tài nhược → Chính Quan bảo vệ Tài. "
        "Khi Day Master vượng, Ấn nhược → Chính Quan sinh Ấn. "
        "Khi Day Master quá vượng → Chính Quan hạn chế. "
        "Khi Kiếp nhiều → Chính Quan khắc chế Kiếp."
    ),
    "Thất Sát": (
        "**Tổn Tài + sinh Ấn + công phá thân + khắc Kiếp.** "
        "Cần CHẾ HÓA: có Thực Thần CHẾ Sát hoặc Ấn HÓA Sát → quý hiển. "
        "Không chế hóa → tai họa, kiện tụng."
    ),
    "Chính Tài": (
        "**Sinh Quan + hao Ấn + bị Kiếp đoạt.** "
        "Day Master vượng + Chính Tài vượng + có Thực Thương sinh Tài → đại phú. "
        "Day Master nhược không gánh nổi Tài, hoặc Kiếp Tài nhiều → tài tan."
    ),
    "Thiên Tài": (
        "**Sinh Sát + hao Ấn + bị Kiếp đoạt.** "
        "Day Master vượng → phát tài bất ngờ, kinh doanh đa lĩnh vực. "
        "Day Master nhược + Kiếp nhiều → tài đến rồi đi nhanh."
    ),
    "Chính Ấn": (
        "**Sinh Day Master + áp Thương Quan + hao Tài.** "
        "Sao mẹ + học vấn. Khi Day Master nhược → Ấn cứu thân, đại quý. "
        "Khi Day Master vượng + Ấn nhiều → ỷ lại, lười suy nghĩ. "
        "Kỵ Chính Tài đoạt Ấn."
    ),
    "Thiên Ấn": (
        "**Sinh Day Master + ĐOẠT Thực Thần + hao Tài.** "
        "Kiêu Thần = trí tuệ phi truyền thống. "
        "Kỵ: khi có Thực Thần thì Thiên Ấn đoạt mất → mất nguồn lộc."
    ),
    "Thực Thần": (
        "**Sinh Tài + CHẾ Thất Sát + xì hơi Day Master.** "
        "Hợp sáng tạo, ẩm thực, giáo dục. "
        "Khi gặp Thất Sát → 'Thực Thần chế Sát' → quý hiển. "
        "Kỵ Thiên Ấn (Kiêu Thần) đoạt Thực."
    ),
    "Thương Quan": (
        "**Sinh Tài + đối địch Chính Quan + xì hơi Day Master.** "
        "Tài năng vượt khuôn khổ. Cần Chính Ấn để 'Thương Quan phối Ấn'. "
        "Kỵ 'Thương Quan kiến Quan' khi Day Master nhược → đại hung."
    ),
    "Tỷ Kiên": (
        "**Trợ Day Master + đoạt Tài + đối lập Quan Sát.** "
        "Day Master nhược → Tỷ Kiên cứu thân. "
        "Day Master vượng → Tỷ Kiên đoạt Tài, cô độc tăng."
    ),
    "Kiếp Tài": (
        "**Đoạt Tài mạnh + hợp Quan + đối lập Tài.** "
        "Cẩn trọng: tổn tài bất ngờ, cướp Tài, đối thủ ngầm. "
        "Vị trí Trụ Tháng → Dương Nhận cách (cách đặc biệt)."
    ),
}

# Tâm tính 2 mặt của 10 Thần (from Chương 3 tr. 88)
THAP_THAN_TAM_TINH: dict[str, dict[str, str]] = {
    "Tỷ Kiên": {
        "tich_cuc": "cương nghị, mạo hiểm, dũng cảm, chí tiến thủ, độc lập",
        "tieu_cuc": "dễ cô độc, ít hòa nhập, đôi khi đơn côi",
    },
    "Kiếp Tài": {
        "tich_cuc": "nhiệt thành, thẳng thắn, ý chí kiên nhẫn, phấn đấu bất khuất",
        "tieu_cuc": "dễ thiên về mù quáng, thiếu lí trí, đôi khi manh động liều lĩnh",
    },
    "Thực Thần": {
        "tich_cuc": "ôn hòa, rộng rãi với mọi người, hiền lành, thân mật",
        "tieu_cuc": "dễ bề ngoài không thật bụng, nhút nhát, đôi khi giả tạo",
    },
    "Thương Quan": {
        "tich_cuc": "thông minh, hoạt bát, tài hoa dồi dào, hiếu thắng",
        "tieu_cuc": "dễ tùy tiện, thiếu kiểm chế ràng buộc, đôi khi tự do vô chính phủ",
    },
    "Chính Tài": {
        "tich_cuc": "cần cù, tiết kiệm, chắc chắn, thật thà",
        "tieu_cuc": "dễ thiên về cẩu thả, thiếu tính tiến thủ, đôi khi nhu nhược",
    },
    "Thiên Tài": {
        "tich_cuc": "khẳng khái, trọng tình, thông minh, nhạy bén, lạc quan, phóng khoáng",
        "tieu_cuc": "dễ thiên về ba hoa, bề ngoài, thiếu kiểm chế, đôi khi phù phiếm",
    },
    "Chính Quan": {
        "tich_cuc": "trung chính, công bằng, kỷ luật, có danh tiếng",
        "tieu_cuc": "dễ cứng nhắc, gò bó, áp lực kỷ luật",
    },
    "Thất Sát": {
        "tich_cuc": "quyết đoán, dũng mãnh, có leadership, dám chịu trách nhiệm",
        "tieu_cuc": "khi không có Thực Thần CHẾ Sát hoặc Ấn HÓA Sát → tai họa, kẻ thù",
    },
    "Chính Ấn": {
        "tich_cuc": "trí tuệ, nhân từ, học vấn chính quy, từ thiện",
        "tieu_cuc": "dễ ỷ lại, lười suy nghĩ độc lập, có khi thiếu hành động",
    },
    "Thiên Ấn": {
        "tich_cuc": "sáng tạo, trực giác sâu, độc lập tư duy",
        "tieu_cuc": "dễ cô độc, đoạt Thực Thần → mất nguồn lộc, phi truyền thống",
    },
}

# Strength tags from engine
STRENGTH_NARRATIVE: dict[str, str] = {
    "strong": "**Vượng** — Day Master mạnh, có khí gốc và được trợ giúp. "
              "Cần khí làm hao/tiết (Thực/Thương, Tài, Quan/Sát) → Dụng Thần.",
    "weak": "**Nhược** — Day Master yếu, ít gốc, ít trợ giúp. "
            "Cần khí hỗ trợ (Ấn, Tỷ/Kiếp) → Dụng Thần. Đại Vận sinh thân là 'thuốc'.",
    "balanced": "**Trung hòa** — Day Master cân bằng, không quá vượng không quá nhược. "
                "Dụng Thần dựa vào khí thiếu nhất hoặc khí điều hậu (mùa sinh).",
}


# ─── Composer functions ─────────────────────────────────────────────────────


def _compose_overview(state: dict) -> str:
    """Lead paragraph — paradigm intro, never predict."""
    dm_stem = state["tu_tru"]["day_master"]["stem"]
    dm_el = state["tu_tru"]["day_master"]["element"]
    duc = ELEMENT_DUC_TINH[dm_el]["duc"]
    pillars = state["tu_tru"]["pillars"]
    year_gz = f"{pillars['year']['stem']} {pillars['year']['branch']}"
    month_gz = f"{pillars['month']['stem']} {pillars['month']['branch']}"
    day_gz = f"{pillars['day']['stem']} {pillars['day']['branch']}"
    hour_gz = f"{pillars['hour']['stem']} {pillars['hour']['branch']}"
    return (
        f"Tứ Trụ của Anh: **{year_gz} / {month_gz} / {day_gz} / {hour_gz}**. "
        f"Nhật Chủ = **{dm_stem} ({dm_el.title()})** — đại biểu cho bản thân Anh. "
        f"Hành Mộc-Hỏa-Thổ-Kim-Thủy của Day Master quy chiếu đức {duc} trong ngũ thường. "
        f"Lá số này KHÔNG dự đoán kết quả cuộc đời — nó phản chiếu **cấu trúc khí bẩm sinh** "
        f"tại điểm sinh + **lưu biến** theo Đại Vận. Mục đích: tri mệnh (biết mình ở đâu "
        f"trong tổng thể) → cân bằng (BỔ) → thuận tự nhiên."
    )


def _luan_cuong_do(state: dict) -> dict:
    """Phân tích Cường độ Nhật Chủ — Vượng / Nhược / Trung hòa."""
    dm_assess = state["ngu_hanh"]["day_master_assessment"]
    tag = dm_assess["strength_tag"]
    label = dm_assess["strength_label"]
    support = dm_assess.get("support_score", 0)
    drain = dm_assess.get("drain_score", 0)
    diff = support - drain
    narrative_base = STRENGTH_NARRATIVE.get(tag, "")
    if tag == "strong":
        if diff >= 4:
            extra = "Mức độ **quá vượng** — cần hao/tiết mạnh để tránh phản tác dụng."
        elif diff >= 2:
            extra = "Mức độ **rất vượng** — có khí gốc đầy đủ."
        else:
            extra = "Mức độ **vượng vừa phải** — đắc lệnh nhưng không quá."
    elif tag == "weak":
        if diff <= -4:
            extra = "Mức độ **quá nhược** — cần Ấn/Tỷ cứu thân khẩn thiết."
        elif diff <= -2:
            extra = "Mức độ **rất nhược** — nguồn sinh trợ thiếu."
        else:
            extra = "Mức độ **nhược nhẹ** — gần trung hòa."
    else:
        extra = "Trạng thái này thuận để Dụng Thần phát huy theo khí thiếu/điều hậu."
    return {
        "tag": tag,
        "label": label,
        "support_score": support,
        "drain_score": drain,
        "diff": diff,
        "narrative": f"{narrative_base} {extra}",
    }


def _luan_ngu_hanh(state: dict) -> dict:
    """Phân tích cân bằng ngũ hành + đề xuất hành cần BỔ."""
    counts = state["ngu_hanh"]["counts"]
    total = sum(counts.values()) or 1
    sorted_counts = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    thua = [el for el, c in sorted_counts if c >= max(3, total / 2)]
    thieu = [el for el, c in counts.items() if c == 0]
    can_bo = thieu if thieu else [el for el, c in sorted_counts[-2:] if c <= 1]

    parts = []
    if thua:
        thua_str = " · ".join(f"{el.title()} ({counts[el]})" for el in thua)
        parts.append(f"Khí **THỪA**: {thua_str}.")
    if thieu:
        thieu_str = " · ".join(f"{el.title()}" for el in thieu)
        parts.append(f"Khí **THIẾU** (vắng mặt): {thieu_str}.")
    else:
        weakest = [el for el, c in sorted_counts if c <= 1]
        if weakest:
            parts.append(f"Khí mỏng: {' · '.join(el.title() for el in weakest)}.")

    # "Vật đến cực tất quay trở lại" — warn when count > 4
    overflow = [el for el, c in counts.items() if c > 4]
    if overflow:
        parts.append(
            f"⚠ **Cảnh báo cực** (vật đến cực tất quay trở lại): "
            f"{' · '.join(el.title() for el in overflow)} quá vượng — "
            f"sinh thái quá hóa hại."
        )

    return {
        "counts": counts,
        "thua": thua,
        "thieu": thieu,
        "can_bo": can_bo,
        "narrative": " ".join(parts) if parts else "Ngũ hành tương đối cân bằng.",
    }


def _luan_cach_cuc(state: dict) -> dict:
    """Phân tích Cách Cục — pattern recognition + reading.

    If extreme_pattern detected, mention it overrides normal cách cục.
    """
    cc = state.get("cach_cuc")
    extreme = state.get("extreme_pattern")
    if not cc:
        return {"present": False, "narrative": "Cách cục chưa xác định được."}
    name = cc.get("cach_name", "")
    polarity = cc.get("polarity", "")
    essence = cc.get("essence", "")
    favorable = cc.get("favorable", "")
    ky = cc.get("ky", "")
    based_on = cc.get("based_on", "")
    narrative = (
        f"Lá số rơi vào **{name}** ({polarity}), xác định dựa trên {based_on}. "
        f"**Bản chất**: {essence} "
        f"**Hợp**: {favorable} "
        f"**Kỵ**: {ky}"
    )
    if extreme:
        narrative += (
            f"\n\n⚠ **OVERRIDE** — Lá số CŨNG phát hiện cách đặc biệt: "
            f"**{extreme['name']}** ({extreme['pattern_type']}, confidence={extreme['confidence']}). "
            f"Paradigm đặc biệt này ĐẢO NGƯỢC heuristic vượng/nhược thường — "
            f"Dụng Thần thực sự là {extreme['dung_than_element'].title()} (chứ không phải theo Day Master support thường)."
        )
    return {
        "present": True,
        "name": name,
        "polarity": polarity,
        "essence": essence,
        "favorable": favorable,
        "ky": ky,
        "narrative": narrative,
        "has_extreme_override": bool(extreme),
    }


def _luan_extreme_pattern(state: dict) -> dict | None:
    """Dedicated section for extreme cách cục (Five Special / Hóa Khí / Tòng).

    Returns None if no extreme pattern detected (chart is "normal").
    """
    extreme = state.get("extreme_pattern")
    if not extreme:
        return None
    type_labels = {
        "special": "🌟 Ngũ Khí Triều Nguyên (Five Special)",
        "hoa": "🔄 Hóa Khí cách (Transform pattern)",
        "tong": "↗ Tòng cách (Follow pattern)",
    }
    return {
        "type": extreme["pattern_type"],
        "type_label": type_labels.get(extreme["pattern_type"], extreme["pattern_type"]),
        "name": extreme["name"],
        "essence": extreme["essence"],
        "dung_than_element": extreme["dung_than_element"],
        "hy_than_element": extreme["hy_than_element"],
        "ky_than_element": extreme["ky_than_element"],
        "confidence": extreme["confidence"],
        "notes": extreme["notes"],
        "narrative": (
            f"Lá số phát hiện **{extreme['name']}** "
            f"(confidence={extreme['confidence']}). {extreme['essence']} "
            f"**LƯU Ý**: Đây là paradigm ĐẢO NGƯỢC heuristic vượng/nhược thông thường — "
            f"Dụng Thần thực sự = {extreme['dung_than_element'].title()}, "
            f"Hỷ Thần = {extreme['hy_than_element'].title()}, "
            f"Kỵ Thần = {extreme['ky_than_element'].title()}. "
            f"Đại Vận đi vào {extreme['dung_than_element'].title()}/{extreme['hy_than_element'].title()} → thuận."
        ),
    }


def _luan_dung_than(state: dict) -> dict:
    """Phân tích Dụng-Hỷ-Kỵ Thần — 'thuốc' cứu mệnh."""
    dt = state.get("dung_than", {})
    dung = dt.get("dung_than_element", "")
    hy = dt.get("hy_than_element", "")
    ky = dt.get("ky_than_element", "")
    reason = dt.get("dung_than_reason", "")
    note = dt.get("note", "")
    role = dt.get("dung_than_role_vi", "")
    return {
        "dung": dung,
        "hy": hy,
        "ky": ky,
        "role": role,
        "narrative": (
            f"**Dụng Thần** = **{dung.title()}** ({role}) — đây là 'thuốc' cho lá số. "
            f"**Hỷ Thần** = **{hy.title()}** (sinh ra Dụng Thần). "
            f"**Kỵ Thần** = **{ky.title()}** (khắc Dụng Thần, cản trở mệnh). "
            f"Lý do: {reason} {note}"
        ).strip(),
    }


def _luan_thap_than_pattern(state: dict) -> dict:
    """Tìm Thập Thần NỔI BẬT (visible + hidden) → tâm tính + công năng."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    # Combined weighted (visible = 2x, hidden = 1x)
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0
    # Top 3 dominant
    sorted_tt = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    top = [tt for tt, _ in sorted_tt[:3] if combined[tt] >= 2.0]
    profiles = []
    for tt in top:
        tt_data = THAP_THAN_TAM_TINH.get(tt)
        if not tt_data:
            continue
        profiles.append({
            "name": tt,
            "weight": combined[tt],
            "tich_cuc": tt_data["tich_cuc"],
            "tieu_cuc": tt_data["tieu_cuc"],
            "cong_nang": THAP_THAN_FUNCTION.get(tt, ""),
            "meaning_short": THAP_THAN_MEANING.get(tt, ""),
        })
    return {
        "dominant": top,
        "profiles": profiles,
    }


def _detect_favorable_combinations(state: dict) -> list[dict]:
    """Detect classical combinations: Thực Thần chế Sát, Ấn hóa Sát, Thương Quan phối Ấn, etc."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    out = []
    if has("Thất Sát") and has("Thực Thần"):
        out.append({
            "name": "Thực Thần chế Sát",
            "polarity": "lành",
            "narrative": "Thực Thần khắc chế Thất Sát → Sát biến thành QUYỀN, không thành tai họa. "
                         "Cấu hình quý hiển (Chương 3 tr. 86).",
        })
    if has("Thất Sát") and (has("Chính Ấn") or has("Thiên Ấn")):
        out.append({
            "name": "Ấn hóa Sát",
            "polarity": "lành",
            "narrative": "Ấn sinh thân + hóa Sát thành sinh khí → áp lực biến thành học vấn/quý nhân. "
                         "Cấu hình bảo hộ.",
        })
    if has("Thương Quan") and has("Chính Ấn"):
        out.append({
            "name": "Thương Quan phối Ấn",
            "polarity": "lành",
            "narrative": "Thương Quan có Ấn dạy bảo → tài năng có khuôn, không phá. "
                         "Cấu hình của nghệ sĩ + học giả độc đáo.",
        })
    if has("Chính Tài") and (has("Thực Thần") or has("Thương Quan")):
        out.append({
            "name": "Thực Thương sinh Tài",
            "polarity": "lành",
            "narrative": "Thực Thần / Thương Quan sinh ra Tài → tài lộc bền vững có sáng tạo. "
                         "Cần Day Master vượng để gánh.",
        })
    return out


def _detect_warnings(state: dict) -> list[dict]:
    """Detect classical warnings: Thương Quan kiến Quan, Tài bị Kiếp đoạt, etc."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    dm_tag = state["ngu_hanh"]["day_master_assessment"]["strength_tag"]
    out = []
    # "Thương Quan kiến Quan" — đại hung khi Day Master nhược
    if has("Thương Quan") and has("Chính Quan") and dm_tag == "weak":
        out.append({
            "name": "Thương Quan kiến Quan",
            "polarity": "hung",
            "narrative": "Thương Quan + Chính Quan đồng hiện + Day Master nhược → đại hung. "
                         "Cần cẩn trọng quan hệ với cấp trên / pháp luật (Chương 3 tr. 86).",
        })
    # "Tài bị Kiếp đoạt" — khi có Tài + Kiếp Tài
    if (has("Chính Tài") or has("Thiên Tài")) and has("Kiếp Tài"):
        out.append({
            "name": "Tài bị Kiếp đoạt",
            "polarity": "cẩn trọng",
            "narrative": "Có Tài + có Kiếp Tài → cần đề phòng tổn tài bất ngờ, "
                         "bạn bè / đồng nghiệp tranh đoạt.",
        })
    # "Kiêu đoạt Thực" — khi có Thực Thần + Thiên Ấn
    if has("Thực Thần") and has("Thiên Ấn"):
        out.append({
            "name": "Kiêu đoạt Thực",
            "polarity": "cẩn trọng",
            "narrative": "Thiên Ấn (Kiêu Thần) đoạt mất Thực Thần → có thể giảm phúc lộc, "
                         "ăn uống / hưởng thụ. Cần cân nhắc lựa chọn nghề nghiệp.",
        })
    # Day Master nhược + Tài nhiều
    if dm_tag == "weak" and (visible.get("Chính Tài", 0) + visible.get("Thiên Tài", 0)
                              + hidden.get("Chính Tài", 0) + hidden.get("Thiên Tài", 0)) >= 2:
        out.append({
            "name": "Thân nhược không gánh nổi Tài",
            "polarity": "cẩn trọng",
            "narrative": "Day Master yếu mà Tài tinh nhiều → có Tài cũng khó giữ. "
                         "Cần Tỷ/Kiếp hoặc Ấn cứu thân trước.",
        })
    return out


def _luan_truong_sinh(state: dict) -> dict:
    """Vòng Trường Sinh — sức sống Day Master qua 4 trụ."""
    ts = state.get("truong_sinh", {})
    total = ts.get("total_strength_score", 0)
    pillars = ts.get("pillars", {})
    phases = []
    for pos, p in pillars.items():
        phases.append({
            "pillar": p.get("pillar_position_vi", pos),
            "branch": p.get("branch", ""),
            "phase": p.get("phase", ""),
            "score": p.get("strength_score", 0),
        })
    if total >= 4:
        verdict = "sức sống tổng thể MẠNH — có gốc dày, năng lượng tự nhiên cao."
    elif total >= 0:
        verdict = "sức sống TRUNG BÌNH — đủ dùng, không quá thiếu."
    else:
        verdict = "sức sống MỎNG — cần dưỡng tinh khí, bồi bổ Dụng Thần qua môi trường."
    return {
        "total_score": total,
        "phases": phases,
        "narrative": f"Tổng điểm sức sống = {total}. {verdict}",
    }


def _luan_than_sat(state: dict) -> dict:
    """Thần Sát — chọn 3-5 sao quan trọng nhất."""
    stars = state.get("than_sat", [])
    if not stars:
        return {"present": False, "highlights": [], "narrative": "Lá số không có sao Thần Sát đặc biệt trong 15 sao đang sàng."}
    # Priority: Thiên Ất Quý Nhân > Văn Xương > Lộc Thần > Dịch Mã > Đào Hoa > others
    priority = {
        "Thiên Ất Quý Nhân": 10, "Văn Xương": 9, "Lộc Thần": 8,
        "Dịch Mã": 7, "Đào Hoa": 6, "Hồng Diễm": 5,
        "Dương Nhận": 4, "Kiếp Sát": 3, "Vong Thần": 3,
        "Cô Thần": 2, "Quả Tú": 2,
    }
    sorted_stars = sorted(stars, key=lambda s: priority.get(s.get("name", ""), 1), reverse=True)
    highlights = sorted_stars[:5]
    return {
        "present": True,
        "highlights": [
            {
                "name": s.get("name"),
                "polarity": s.get("polarity"),
                "pillar": s.get("found_at_pillar"),
                "description": s.get("description"),
            }
            for s in highlights
        ],
        "narrative": (
            f"Lá số có **{len(stars)} sao Thần Sát** đáng chú ý. "
            f"Top {len(highlights)}: " + ", ".join(s.get("name", "") for s in highlights) + "."
        ),
    }


def _luan_dai_van_current(state: dict, current_age: int | None = None) -> dict:
    """Đại Vận hiện tại — đang ở cycle nào, đi đúng/sai Dụng Thần."""
    dv = state.get("dai_van", {})
    cycles = dv.get("cycles", [])
    dt = state.get("dung_than", {})
    dung_el = dt.get("dung_than_element", "")
    ky_el = dt.get("ky_than_element", "")

    if not cycles or current_age is None:
        return {
            "current_cycle": None,
            "narrative": (
                "Đại Vận đầy đủ ở phần 'Đại Vận' bên trên. "
                "Mỗi cycle 10 năm — vận đi vào Dụng Thần (= "
                f"{dung_el.title()}) → 10 năm thuận. "
                f"Vận đi vào Kỵ Thần ({ky_el.title()}) → cần đề phòng."
            ),
        }

    current = None
    for c in cycles:
        if c.get("start_age", 0) <= current_age <= c.get("end_age", 999):
            current = c
            break
    if not current:
        return {
            "current_cycle": None,
            "narrative": f"Tuổi {current_age} chưa vào Đại Vận đầu tiên hoặc đã qua hết chu kỳ.",
        }

    stem_el = STEM_ELEMENT.get(current.get("stem", ""), "")
    branch_el = state["tu_tru"]["pillars"]["year"].get("branch_element", "")  # fallback
    from .constants import BRANCH_ELEMENT
    branch_el = BRANCH_ELEMENT.get(current.get("branch", ""), "")

    matches_dung = stem_el == dung_el or branch_el == dung_el
    matches_ky = stem_el == ky_el or branch_el == ky_el

    if matches_dung:
        verdict = "✦ Đại Vận đi vào **Dụng Thần** → 10 năm THUẬN, là thời cơ để Anh phát huy + cân bằng khí thiếu."
    elif matches_ky:
        verdict = "⚠ Đại Vận đi vào **Kỵ Thần** → 10 năm THỬ THÁCH, cần đề phòng + dùng các phương tiện 'Bổ' tích cực hơn."
    else:
        verdict = "Đại Vận khí trung tính — không hỗ trợ mạnh nhưng cũng không cản."
    return {
        "current_cycle": current,
        "stem_element": stem_el,
        "branch_element": branch_el,
        "matches_dung_than": matches_dung,
        "matches_ky_than": matches_ky,
        "narrative": (
            f"Tuổi {current_age} → Đại Vận **{current.get('stem')} {current.get('branch')}** "
            f"({current.get('start_age')}-{current.get('end_age')} tuổi). "
            f"{verdict}"
        ),
    }


def _bo_huong_recommendations(state: dict) -> dict:
    """'Bổ' actionable: nghề, màu, phương, ẩm thực dựa trên Dụng Thần + Hỷ Thần."""
    dt = state.get("dung_than", {})
    dung = dt.get("dung_than_element", "")
    hy = dt.get("hy_than_element", "")
    ky = dt.get("ky_than_element", "")
    rec = {}
    for el_key, el_name in [("dung", dung), ("hy", hy)]:
        if not el_name:
            continue
        bo = ELEMENT_BO_HUONG.get(el_name)
        if not bo:
            continue
        rec[el_key] = {
            "element": el_name,
            "nghe_nghiep": bo["nghe_nghiep"],
            "mau_sac": bo["mau_sac"],
            "phuong_vi": bo["phuong_vi"],
            "am_thuc": bo["am_thuc"],
        }
    tranh = ELEMENT_BO_HUONG.get(ky, {})
    narrative = (
        f"BỔ theo Dụng Thần ({dung.title()}) — chìa khóa vàng của Tử Bình (Thiệu Vĩ Hoa Q1 ch.2). "
        f"Ưu tiên hoạt động trong môi trường + hành nghề thuộc {dung.title()} và {hy.title()}. "
        f"Hạn chế tiếp xúc lâu dài với khí {ky.title()} (Kỵ Thần) — không phải tránh hoàn toàn, "
        f"mà giữ liều lượng vừa phải."
    )
    return {
        "recommend": rec,
        "tranh": {
            "element": ky,
            "nghe_nghiep": tranh.get("nghe_nghiep", []),
            "mau_sac": tranh.get("mau_sac", []),
            "phuong_vi": tranh.get("phuong_vi", []),
        } if tranh else None,
        "narrative": narrative,
    }


def _detect_thong_quan(state: dict) -> dict | None:
    """Thông quan — detect 2 opposing elements with ~equal force → suggest mediator."""
    counts = state["ngu_hanh"]["counts"]
    # Pairs of opposing elements (controls relation)
    opposites = [
        ("kim", "mộc"),  # Kim khắc Mộc
        ("mộc", "thổ"),  # Mộc khắc Thổ
        ("thổ", "thủy"), # Thổ khắc Thủy
        ("thủy", "hỏa"), # Thủy khắc Hỏa
        ("hỏa", "kim"),  # Hỏa khắc Kim
    ]
    # Mediators: A→B opposite uses C such that A→C→B
    mediator = {
        ("kim", "mộc"): "thủy",   # Kim→Thủy→Mộc
        ("mộc", "thổ"): "hỏa",    # Mộc→Hỏa→Thổ
        ("thổ", "thủy"): "kim",   # Thổ→Kim→Thủy
        ("thủy", "hỏa"): "mộc",   # Thủy→Mộc→Hỏa
        ("hỏa", "kim"): "thổ",    # Hỏa→Thổ→Kim
    }
    for a, b in opposites:
        ca, cb = counts.get(a, 0), counts.get(b, 0)
        if ca >= 2 and cb >= 2 and abs(ca - cb) <= 1:
            med = mediator[(a, b)]
            return {
                "a": a, "b": b,
                "mediator": med,
                "a_count": ca, "b_count": cb,
                "mediator_count": counts.get(med, 0),
                "narrative": (
                    f"**Thông quan**: {a.title()} và {b.title()} đối lập ngang nhau "
                    f"({ca}-{cb}) → mệnh có bệnh. Thuốc = **{med.title()}** "
                    f"(làm trung gian: {a}→{med}→{b}). "
                    f"Hiện trong lá số {med.title()} có {counts.get(med, 0)} đơn vị."
                ),
            }
    return None


def _compose_closing(state: dict) -> str:
    """Paradigm closing — tri mệnh."""
    return (
        "📿 **Đóng**: Tử Bình KHÔNG nói Anh sẽ thành công hay thất bại. "
        "Tử Bình chỉ cho Anh thấy cấu trúc khí bẩm sinh + đường đi của khí. "
        "Mệnh **cố kết** (Tứ Trụ) — không đổi được. "
        "Vận **lưu biến** (Đại Vận) — có thể chọn cách đi qua. "
        "Việc Anh làm bây giờ là **BỔ** (cân bằng khí thiếu) qua nghề nghiệp, môi trường, "
        "ẩm thực, quan hệ — như Thiệu Vĩ Hoa dạy ở Chương 2. "
        "Tri mệnh thì không lo. Cảm ơn Anh đã cho em đọc cùng."
    )


# ─── Public API ─────────────────────────────────────────────────────────────


METHOD_ID = "bat_tu_luan_giai_v1"
SOURCE_REF = (
    "Thiệu Vĩ Hoa & Trần Viên — Dự đoán theo Tứ trụ (NXB VHTT, dịch giả Nguyễn Văn Mậu, "
    "tái bản lần 4). Chương 1-3."
)


def compose_luan_giai(bat_tu_state: dict, current_age: int | None = None) -> dict:
    """Synthesize a comprehensive Bát Tự interpretation in paradigm tone.

    Args:
        bat_tu_state: Output of `cast_bat_tu(...)` — contains pillars, day_master,
            ngu_hanh, cach_cuc, dung_than, truong_sinh, than_sat, dai_van, etc.
        current_age: Optional. If provided, will identify current Đại Vận cycle.

    Returns:
        Dict with structured narrative sections, ready for JSON API response.
    """
    if "tu_tru" not in bat_tu_state:
        raise ValueError("bat_tu_state must contain 'tu_tru' key (from cast_bat_tu)")

    return {
        "method_id": METHOD_ID,
        "source_ref": SOURCE_REF,
        "paradigm_guard": (
            "Tử Bình KHÔNG predict — đọc đồng dạng. Mệnh cố kết, Vận lưu biến. "
            "Tri mệnh để cân bằng (Bổ), không để biết kết quả."
        ),
        "overview": _compose_overview(bat_tu_state),
        "cuong_do_nhat_chu": _luan_cuong_do(bat_tu_state),
        "ngu_hanh_balance": _luan_ngu_hanh(bat_tu_state),
        "cach_cuc_luan": _luan_cach_cuc(bat_tu_state),
        "extreme_pattern_luan": _luan_extreme_pattern(bat_tu_state),
        "dung_than_luan": _luan_dung_than(bat_tu_state),
        "thap_than_pattern": _luan_thap_than_pattern(bat_tu_state),
        "favorable_combinations": _detect_favorable_combinations(bat_tu_state),
        "warnings": _detect_warnings(bat_tu_state),
        "thong_quan": _detect_thong_quan(bat_tu_state),
        "truong_sinh_luan": _luan_truong_sinh(bat_tu_state),
        "than_sat_highlights": _luan_than_sat(bat_tu_state),
        "dai_van_current": _luan_dai_van_current(bat_tu_state, current_age),
        "bo_huong": _bo_huong_recommendations(bat_tu_state),
        "closing": _compose_closing(bat_tu_state),
    }
