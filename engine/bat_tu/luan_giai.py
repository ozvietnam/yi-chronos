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
    """Phân tích Cường độ Nhật Chủ — Vượng / Nhược / Trung hòa.

    Inject lá số data: month branch (đắc lệnh?), positions của Ấn + Tỷ/Kiếp + Tài + Quan + Thực Thương.
    """
    dm_assess = state["ngu_hanh"]["day_master_assessment"]
    tag = dm_assess["strength_tag"]
    label = dm_assess["strength_label"]
    support = dm_assess.get("support_score", 0)
    drain = dm_assess.get("drain_score", 0)
    diff = support - drain
    pillars = state["tu_tru"]["pillars"]
    dm_stem = state["tu_tru"]["day_master"]["stem"]
    dm_el = state["tu_tru"]["day_master"]["element"]
    month_branch = pillars["month"]["branch"]
    month_branch_el = pillars["month"]["branch_element"]
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    count = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0)
    narrative_base = STRENGTH_NARRATIVE.get(tag, "")

    # 1. Đắc lệnh check
    from .constants import ELEMENT_GENERATES
    if month_branch_el == dm_el:
        loi_label = "ĐẮC LỆNH (chi tháng cùng hành)"
    elif ELEMENT_GENERATES.get(month_branch_el) == dm_el:
        loi_label = "ĐẮC LỆNH (chi tháng sinh Day Master)"
    elif ELEMENT_GENERATES.get(dm_el) == month_branch_el:
        loi_label = "TIẾT KHÍ (Day Master sinh chi tháng → mất khí)"
    else:
        from .constants import ELEMENT_CONTROLS
        if ELEMENT_CONTROLS.get(month_branch_el) == dm_el:
            loi_label = "BỊ KHẮC (chi tháng khắc Day Master)"
        elif ELEMENT_CONTROLS.get(dm_el) == month_branch_el:
            loi_label = "HAO KHẮC (Day Master khắc chi tháng → hao sức)"
        else:
            loi_label = "không đắc lệnh"

    # 2. Support breakdown
    an_count = count("Chính Ấn") + count("Thiên Ấn")
    ty_count = count("Tỷ Kiên") + count("Kiếp Tài")
    # 3. Drain breakdown
    tai_count = count("Chính Tài") + count("Thiên Tài")
    quan_count = count("Chính Quan") + count("Thất Sát")
    thuc_count = count("Thực Thần") + count("Thương Quan")

    # 4. Mức độ extra
    if tag == "strong":
        if diff >= 4:
            extra = "Mức độ **quá vượng** — cần hao/tiết mạnh, tránh tự đại thái quá."
        elif diff >= 2:
            extra = "Mức độ **rất vượng** — gốc đầy đủ, sức mạnh ổn."
        else:
            extra = "Mức độ **vượng vừa phải** — đắc lệnh nhưng không quá."
    elif tag == "weak":
        if diff <= -4:
            extra = "Mức độ **quá nhược** — Ấn/Tỷ phải cấp cứu, không thì áp lực thân lớn."
        elif diff <= -2:
            extra = "Mức độ **rất nhược** — sinh trợ thiếu, dễ mệt, sức bền hạn chế."
        else:
            extra = "Mức độ **nhược nhẹ** — gần trung hòa, không quá khắc nghiệt."
    else:
        extra = "Trạng thái này thuận để Dụng Thần phát huy theo khí thiếu/điều hậu."

    # 5. Detailed narrative
    detail_lines = [
        f"Nhật Chủ **{dm_stem} ({dm_el})** sinh tháng **{month_branch} ({month_branch_el})** → **{loi_label}**.",
        f"📊 **Support** (sinh-trợ Day Master): Ấn = {an_count} vị trí, Tỷ/Kiếp = {ty_count} vị trí → "
        f"tổng support score = **{support:.1f}**.",
        f"📉 **Drain** (hao-tiết Day Master): Tài = {tai_count}, Quan/Sát = {quan_count}, "
        f"Thực/Thương = {thuc_count} → tổng drain score = **{drain:.1f}**.",
        f"⚖ Δ (support − drain) = **{diff:+.1f}** → kết luận: {extra}",
    ]
    return {
        "tag": tag,
        "label": label,
        "support_score": support,
        "drain_score": drain,
        "diff": diff,
        "loi_label": loi_label,
        "an_count": an_count,
        "ty_count": ty_count,
        "tai_count": tai_count,
        "quan_count": quan_count,
        "thuc_count": thuc_count,
        "narrative": f"{narrative_base}\n\n" + "\n".join(detail_lines),
    }


def _luan_ngu_hanh(state: dict) -> dict:
    """Phân tích cân bằng ngũ hành + đề xuất hành cần BỔ.

    Inject: pct cụ thể từng hành, tạng phủ tương ứng (Trung y), Đại Vận hiện tại
    có bổ khí thiếu không.
    """
    counts = state["ngu_hanh"]["counts"]
    total = sum(counts.values()) or 1
    sorted_counts = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    thua = [el for el, c in sorted_counts if c >= max(3, total / 2)]
    thieu = [el for el, c in counts.items() if c == 0]
    can_bo = thieu if thieu else [el for el, c in sorted_counts[-2:] if c <= 1]

    # Trung y mapping cho hành thừa/thiếu
    TANG_PHU = {
        "mộc": ("Can/Đởm", "gan + mật, mắt, gân"),
        "hỏa": ("Tâm/Tiểu Trường", "tim, mạch + lưỡi"),
        "thổ": ("Tỳ/Vị", "lá lách + dạ dày, miệng + cơ"),
        "kim": ("Phế/Đại Trường", "phổi + ruột già, mũi + da"),
        "thủy": ("Thận/Bàng Quang", "thận, tai + xương"),
    }

    parts = []

    # 1. Full distribution
    pct_lines = []
    for el, c in sorted_counts:
        pct = c / total * 100
        marker = "🔴" if c >= 3 else ("🟢" if c >= 1.5 else ("🟡" if c >= 0.5 else "⚪"))
        pct_lines.append(f"  {marker} {el.title()}: {c:.1f} ({pct:.0f}%)")
    parts.append("📊 **Phân bố ngũ hành** (Tổng = {:.1f}):\n{}".format(
        total, "\n".join(pct_lines)
    ))

    # 2. Thừa with tạng phủ + symptoms
    if thua:
        thua_lines = []
        for el in thua:
            tang, body_part = TANG_PHU.get(el, ("", ""))
            thua_lines.append(
                f"  • **{el.title()} THỪA ({counts[el]:.1f} = {counts[el]/total*100:.0f}%)** → "
                f"Tạng/Phủ {tang} dễ quá vượng → cần ý thức {body_part}."
            )
        parts.append("🔥 **Khí THỪA**:\n" + "\n".join(thua_lines))

    # 3. Thiếu hoặc mỏng with tạng phủ
    if thieu:
        thieu_lines = []
        for el in thieu:
            tang, body_part = TANG_PHU.get(el, ("", ""))
            thieu_lines.append(
                f"  • **{el.title()} VẮNG MẶT (0%)** → "
                f"Tạng/Phủ {tang} thiếu sinh khí → cần BỔ qua {body_part}."
            )
        parts.append("❄ **Khí THIẾU (vắng mặt)**:\n" + "\n".join(thieu_lines))
    else:
        weakest = [el for el, c in sorted_counts if c <= 1]
        if weakest:
            mong_lines = []
            for el in weakest:
                tang, body_part = TANG_PHU.get(el, ("", ""))
                mong_lines.append(
                    f"  • **{el.title()} mỏng ({counts[el]:.1f} = {counts[el]/total*100:.0f}%)** → "
                    f"Tạng/Phủ {tang} cần bồi dưỡng nhẹ."
                )
            parts.append("🟡 **Khí mỏng**:\n" + "\n".join(mong_lines))

    # 4. Vật đến cực
    overflow = [el for el, c in counts.items() if c > 4]
    if overflow:
        parts.append(
            "⚠ **Cảnh báo cực** (vật đến cực tất quay trở lại): "
            + ", ".join(f"{el.title()}={counts[el]:.1f}" for el in overflow)
            + " — sinh thái quá hóa hại, cần tiết khí có ý thức (theo Thiệu Vĩ Hoa Chương 2 tr.22 và tr.81)."
        )

    # 5. Bổ hint
    if can_bo:
        bo_lines = []
        for el in can_bo:
            tang, _ = TANG_PHU.get(el, ("", ""))
            bo_lines.append(f"  • **{el.title()}** (bổ qua nghề/màu/phương → hỗ trợ {tang})")
        parts.append("🎯 **Cần BỔ** (theo Thiệu Vĩ Hoa Q1 ch.2 - chìa khóa vàng):\n" + "\n".join(bo_lines))

    return {
        "counts": counts,
        "thua": thua,
        "thieu": thieu,
        "can_bo": can_bo,
        "narrative": "\n\n".join(parts) if parts else "Ngũ hành tương đối cân bằng.",
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
    """Tìm Thập Thần NỔI BẬT (visible + hidden) → tâm tính + công năng + positions cụ thể."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    combined: dict[str, float] = {}
    for tt, n in visible.items():
        combined[tt] = combined.get(tt, 0) + n * 2.0
    for tt, n in hidden.items():
        combined[tt] = combined.get(tt, 0) + n * 1.0
    sorted_tt = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)
    top = [tt for tt, _ in sorted_tt[:3] if combined[tt] >= 2.0]
    profiles = []
    for tt in top:
        tt_data = THAP_THAN_TAM_TINH.get(tt)
        if not tt_data:
            continue
        positions = _find_thap_than_positions_in_state(state, tt)
        v_count = visible.get(tt, 0)
        h_count = hidden.get(tt, 0)
        narrative = (
            f"**Vị trí trong lá số Anh** ({v_count} visible + {h_count} hidden = "
            f"trọng số {combined[tt]:.0f}):\n"
            + "\n".join(f"  • {p}" for p in positions[:6])
            + f"\n\n**Tâm tính tích cực**: {tt_data['tich_cuc']}\n"
            + f"**Tâm tính tiêu cực**: {tt_data['tieu_cuc']}\n\n"
            + f"**Công năng** (Thiệu Vĩ Hoa Q1 ch.3): {THAP_THAN_FUNCTION.get(tt, '')}"
        )
        profiles.append({
            "name": tt,
            "weight": combined[tt],
            "visible_count": v_count,
            "hidden_count": h_count,
            "positions": positions,
            "tich_cuc": tt_data["tich_cuc"],
            "tieu_cuc": tt_data["tieu_cuc"],
            "cong_nang": THAP_THAN_FUNCTION.get(tt, ""),
            "meaning_short": THAP_THAN_MEANING.get(tt, ""),
            "narrative": narrative,
        })
    return {
        "dominant": top,
        "profiles": profiles,
    }


def _find_thap_than_positions_in_state(state: dict, target_tt: str) -> list[str]:
    """Find positions of a specific Thập Thần in the chart (visible + hidden), returning labels."""
    pillars = state["tu_tru"]["pillars"]
    day_master = state["tu_tru"]["day_master"]["stem"]
    positions = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        if pos != "day":
            stem_tt = p.get("stem_thap_than")
            if stem_tt == target_tt:
                positions.append(f"can {p['stem']} ở {p.get('position_vi', pos)} (visible)")
        for h in p.get("hidden_stems_with_thap_than", []):
            if h.get("thap_than") == target_tt:
                positions.append(f"tàng {h['stem']} trong {p.get('position_vi', pos)} ({p['branch']})")
    return positions


def _detect_favorable_combinations(state: dict) -> list[dict]:
    """Detect classical combinations: Thực Thần chế Sát, Ấn hóa Sát, ... with specific positions injected."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    out = []

    if has("Thất Sát") and has("Thực Thần"):
        sat_pos = _find_thap_than_positions_in_state(state, "Thất Sát")
        thuc_pos = _find_thap_than_positions_in_state(state, "Thực Thần")
        out.append({
            "name": "Thực Thần chế Sát",
            "polarity": "lành",
            "positions": {"Thất Sát": sat_pos, "Thực Thần": thuc_pos},
            "narrative": (
                f"**Trong lá số Anh**: Thất Sát ở [{', '.join(sat_pos) or 'không tìm thấy'}], "
                f"Thực Thần ở [{', '.join(thuc_pos) or 'không tìm thấy'}]. "
                f"Thực Thần khắc chế Thất Sát → Sát mất tính HUNG, biến thành QUYỀN "
                f"(quyền lực có kỷ luật, không thành tai họa). "
                f"Cấu hình quý hiển kinh điển — Thiệu Vĩ Hoa Q1 Chương 3 tr. 86. "
                f"💡 Actionable: Tận dụng cấu hình bằng nghề có áp lực + đòi sáng tạo "
                f"(quân đội + chiến lược, lãnh đạo + sáng tạo, kinh doanh mạo hiểm có kỷ luật)."
            ),
        })
    if has("Thất Sát") and (has("Chính Ấn") or has("Thiên Ấn")):
        sat_pos = _find_thap_than_positions_in_state(state, "Thất Sát")
        an_pos = (_find_thap_than_positions_in_state(state, "Chính Ấn")
                  + _find_thap_than_positions_in_state(state, "Thiên Ấn"))
        out.append({
            "name": "Ấn hóa Sát",
            "polarity": "lành",
            "positions": {"Thất Sát": sat_pos, "Ấn": an_pos},
            "narrative": (
                f"**Trong lá số Anh**: Thất Sát ở [{', '.join(sat_pos) or '∅'}], "
                f"Ấn ở [{', '.join(an_pos) or '∅'}]. "
                f"Ấn sinh thân + hóa Sát → Sát biến thành sinh khí. "
                f"Áp lực chuyển thành học vấn/quý nhân. Cấu hình bảo hộ kinh điển. "
                f"💡 Actionable: Đầu tư học vấn + tìm thầy/quý nhân → "
                f"áp lực bên ngoài sẽ chuyển thành cơ hội học hỏi."
            ),
        })
    if has("Thương Quan") and has("Chính Ấn"):
        thuong_pos = _find_thap_than_positions_in_state(state, "Thương Quan")
        an_pos = _find_thap_than_positions_in_state(state, "Chính Ấn")
        out.append({
            "name": "Thương Quan phối Ấn",
            "polarity": "lành",
            "positions": {"Thương Quan": thuong_pos, "Chính Ấn": an_pos},
            "narrative": (
                f"**Trong lá số Anh**: Thương Quan ở [{', '.join(thuong_pos) or '∅'}], "
                f"Chính Ấn ở [{', '.join(an_pos) or '∅'}]. "
                f"Thương Quan có Ấn dạy bảo → tài năng vượt khuôn khổ có 'phanh', "
                f"không phá vào Quan. Cấu hình của nghệ sĩ độc đáo + học giả + công nghệ. "
                f"💡 Actionable: Khi sáng tạo, luôn quay về Ấn (học vấn, từ thiện, "
                f"truyền thống) để 'phanh' tài năng — tránh nổi loạn phá hoại."
            ),
        })
    if (has("Chính Tài") or has("Thiên Tài")) and (has("Thực Thần") or has("Thương Quan")):
        tai_pos = (_find_thap_than_positions_in_state(state, "Chính Tài")
                   + _find_thap_than_positions_in_state(state, "Thiên Tài"))
        thuc_pos = (_find_thap_than_positions_in_state(state, "Thực Thần")
                    + _find_thap_than_positions_in_state(state, "Thương Quan"))
        out.append({
            "name": "Thực Thương sinh Tài",
            "polarity": "lành",
            "positions": {"Tài": tai_pos, "Thực/Thương": thuc_pos},
            "narrative": (
                f"**Trong lá số Anh**: Tài tinh ở [{', '.join(tai_pos) or '∅'}], "
                f"Thực/Thương ở [{', '.join(thuc_pos) or '∅'}]. "
                f"Thực/Thương SINH Tài → tài lộc đến qua sáng tạo + lao động bền vững. "
                f"Đây là 1 trong 3 cấu hình PHÚ kinh điển của Tử Bình. "
                f"💡 Actionable: Chọn nghề có sản phẩm/dịch vụ sáng tạo + thương mại "
                f"(không phải kinh doanh thuần). Cần Day Master vượng để 'gánh' Tài."
            ),
        })
    return out


def _detect_warnings(state: dict) -> list[dict]:
    """Detect classical warnings — with specific positions in lá số."""
    dist = state.get("thap_than_distribution", {})
    visible = dist.get("visible", {})
    hidden = dist.get("hidden", {})
    has = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0) > 0
    count = lambda tt: visible.get(tt, 0) + hidden.get(tt, 0)
    dm_tag = state["ngu_hanh"]["day_master_assessment"]["strength_tag"]
    out = []

    if has("Thương Quan") and has("Chính Quan") and dm_tag == "weak":
        thuong_pos = _find_thap_than_positions_in_state(state, "Thương Quan")
        quan_pos = _find_thap_than_positions_in_state(state, "Chính Quan")
        out.append({
            "name": "Thương Quan kiến Quan",
            "polarity": "hung",
            "positions": {"Thương Quan": thuong_pos, "Chính Quan": quan_pos},
            "narrative": (
                f"**Trong lá số Anh**: Thương Quan ở [{', '.join(thuong_pos) or '∅'}], "
                f"Chính Quan ở [{', '.join(quan_pos) or '∅'}], Day Master NHƯỢC. "
                f"⚠ 'Thương Quan kiến Quan vi họa bách đoan' (Thiệu Vĩ Hoa Q1 ch.3 tr.86): "
                f"Thương Quan PHÁ Chính Quan → đại hung cho danh tiếng + quan lộ. "
                f"💊 **Hóa giải**: Thêm Chính Ấn (học vấn) để 'Thương Quan phối Ấn'. "
                f"Tránh kích thích cấp trên/pháp luật, không nổi loạn vì cảm xúc."
            ),
        })

    if (has("Chính Tài") or has("Thiên Tài")) and has("Kiếp Tài"):
        tai_pos = (_find_thap_than_positions_in_state(state, "Chính Tài")
                   + _find_thap_than_positions_in_state(state, "Thiên Tài"))
        kiep_pos = _find_thap_than_positions_in_state(state, "Kiếp Tài")
        out.append({
            "name": "Tài bị Kiếp đoạt",
            "polarity": "cẩn trọng",
            "positions": {"Tài": tai_pos, "Kiếp Tài": kiep_pos},
            "narrative": (
                f"**Trong lá số Anh**: Tài tinh ở [{', '.join(tai_pos) or '∅'}], "
                f"Kiếp Tài ở [{', '.join(kiep_pos) or '∅'}]. "
                f"Kiếp Tài đoạt Tài → đề phòng TỔN TÀI từ bạn bè/cộng sự cùng giới "
                f"(tranh đoạt, lừa đảo, đầu tư chung mất). "
                f"Đặc biệt nguy hiểm khi Đại Vận hoặc Lưu Niên Kiếp Tài kích hoạt. "
                f"💊 **Hóa giải**: Tránh partnership tài chính không hợp đồng. "
                f"Diversify đầu tư. Không cho mượn tiền nhóm bạn."
            ),
        })

    if has("Thực Thần") and has("Thiên Ấn"):
        thuc_pos = _find_thap_than_positions_in_state(state, "Thực Thần")
        kieu_pos = _find_thap_than_positions_in_state(state, "Thiên Ấn")
        out.append({
            "name": "Kiêu đoạt Thực",
            "polarity": "cẩn trọng",
            "positions": {"Thực Thần": thuc_pos, "Thiên Ấn (Kiêu Thần)": kieu_pos},
            "narrative": (
                f"**Trong lá số Anh**: Thực Thần ở [{', '.join(thuc_pos) or '∅'}], "
                f"Thiên Ấn (Kiêu) ở [{', '.join(kieu_pos) or '∅'}]. "
                f"Kiêu Thần ĐOẠT Thực Thần → có thể giảm phúc lộc + hưởng thụ. "
                f"💊 **Hóa giải**: Có Chính Tài giúp khắc Kiêu để bảo vệ Thực Thần. "
                f"Hoặc chọn nghề sáng tạo có deadline/output cụ thể (không để Kiêu ngủ quên Thực)."
            ),
        })

    if dm_tag == "weak" and (count("Chính Tài") + count("Thiên Tài")) >= 2:
        tai_count = count("Chính Tài") + count("Thiên Tài")
        tai_pos = (_find_thap_than_positions_in_state(state, "Chính Tài")
                   + _find_thap_than_positions_in_state(state, "Thiên Tài"))
        out.append({
            "name": "Thân nhược không gánh nổi Tài",
            "polarity": "cẩn trọng",
            "positions": {"Tài tinh": tai_pos},
            "narrative": (
                f"**Trong lá số Anh**: Day Master NHƯỢC + có {tai_count} vị trí Tài tinh "
                f"({', '.join(tai_pos) or '∅'}). "
                f"⚠ 'Tài đa thân nhược' — có Tài cũng không giữ được. "
                f"Khởi nghiệp/kinh doanh áp lực cao = mất sức + dễ phá tài. "
                f"💊 **Hóa giải**: ĐỜI 1 BỒI THÂN trước (học vấn, kỹ năng, đối tác Tỷ/Kiếp), "
                f"ĐỜI 2 mới gánh Tài. Tránh áp lực tài chính lớn khi Đại Vận chưa thuận."
            ),
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
    """Đại Vận hiện tại — đi đúng/sai Dụng Thần + interaction với 4 trụ gốc."""
    dv = state.get("dai_van", {})
    cycles = dv.get("cycles", [])
    dt = state.get("dung_than", {})
    dung_el = dt.get("dung_than_element", "")
    hy_el = dt.get("hy_than_element", "")
    ky_el = dt.get("ky_than_element", "")
    pillars = state["tu_tru"]["pillars"]
    day_master = state["tu_tru"]["day_master"]["stem"]

    if not cycles or current_age is None:
        return {
            "current_cycle": None,
            "narrative": (
                f"Đại Vận đầy đủ ở phần 'Đại Vận' bên trên. "
                f"Mỗi cycle 10 năm — vận đi vào Dụng Thần ({dung_el.title()}) → 10 năm thuận. "
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

    from .constants import BRANCH_ELEMENT
    stem_el = STEM_ELEMENT.get(current.get("stem", ""), "")
    branch_el = BRANCH_ELEMENT.get(current.get("branch", ""), "")
    matches_dung = stem_el == dung_el or branch_el == dung_el
    matches_hy = stem_el == hy_el or branch_el == hy_el
    matches_ky = stem_el == ky_el or branch_el == ky_el

    # Interactions với 4 trụ gốc
    from .luu_nien import LUC_HAI, LUC_HOP, LUC_XUNG, TAM_HINH_GROUPS
    dv_branch = current.get("branch")
    interactions = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars[pos]
        pair = frozenset([dv_branch, p["branch"]])
        if pair in LUC_HOP:
            interactions.append(
                f"  ✓ Lục HỢP với {p.get('position_vi', pos)} ({p['branch']}) → "
                f"hành {LUC_HOP[pair].title()} kích hoạt"
            )
        if pair in LUC_XUNG:
            interactions.append(
                f"  ⚔ Lục XUNG với {p.get('position_vi', pos)} ({p['branch']}) → "
                f"biến động lĩnh vực {p.get('domain_vi', pos)}"
            )
        if pair in LUC_HAI:
            interactions.append(
                f"  ✗ Lục HẠI với {p.get('position_vi', pos)} ({p['branch']}) → "
                f"bất hòa ngầm"
            )
        for group in TAM_HINH_GROUPS:
            if dv_branch in group and p["branch"] in group and dv_branch != p["branch"]:
                interactions.append(
                    f"  ⚖ Tương HÌNH với {p.get('position_vi', pos)} → kiện tụng / va chạm"
                )
                break

    # Verdict
    if matches_dung:
        verdict = (
            f"✦ Đại Vận đi vào **Dụng Thần** ({dung_el.title()}) → 10 năm THUẬN. "
            f"Đây là thời cơ phát huy + cân bằng khí thiếu."
        )
    elif matches_ky:
        verdict = (
            f"⚠ Đại Vận đi vào **Kỵ Thần** ({ky_el.title()}) → 10 năm THỬ THÁCH. "
            f"Cần dùng phương tiện 'Bổ' Dụng Thần ({dung_el.title()}) + Hỷ Thần "
            f"({hy_el.title()}) tích cực hơn để hóa giải. "
            f"Hợp thời gian này: học hỏi + tích nội lực + chọn lọc cơ hội kỹ."
        )
    elif matches_hy:
        verdict = (
            f"✧ Đại Vận có khí Hỷ Thần ({hy_el.title()}) → vận tích lũy, "
            f"không bứt phá nhưng ổn định, chuẩn bị cho Đại Vận tiếp theo."
        )
    else:
        verdict = (
            f"Đại Vận khí trung tính ({stem_el.title()}/{branch_el.title()}) — "
            f"không hỗ trợ mạnh nhưng cũng không cản. Năm 'Bổ' tự thân."
        )

    inter_text = ""
    if interactions:
        inter_text = "\n\n📍 **Tương tác với 4 trụ gốc**:\n" + "\n".join(interactions)
    else:
        inter_text = "\n\n📍 Đại Vận không có tương tác đặc biệt với 4 trụ gốc."

    narrative = (
        f"Tuổi **{current_age}** → Đại Vận **{current.get('stem')} {current.get('branch')}** "
        f"({current.get('start_age')}-{current.get('end_age')} tuổi, "
        f"hành {stem_el.title()}/{branch_el.title()}).\n\n"
        f"{verdict}"
        f"{inter_text}"
    )

    return {
        "current_cycle": current,
        "stem_element": stem_el,
        "branch_element": branch_el,
        "matches_dung_than": matches_dung,
        "matches_hy_than": matches_hy,
        "matches_ky_than": matches_ky,
        "interactions_with_4_pillars": interactions,
        "narrative": narrative,
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


def _luan_hoa_giai_in_state(state: dict, current_age: int | None = None) -> dict:
    """Wrap hoa_giai.luan_hoa_giai — auto-resolve Lưu Niên chi from current_age + Dai Van."""
    from .hoa_giai import luan_hoa_giai
    # Try to get current Lưu Niên chi from dai_van (current_year branch)
    current_chi = None
    dai_van = state.get("dai_van", {})
    if isinstance(dai_van, dict):
        current_chi = dai_van.get("current_year_branch")
    try:
        return luan_hoa_giai(state, current_luu_nien_chi=current_chi)
    except Exception as e:
        return {"_error": str(e)[:200]}


def _luan_cha_me_in_state(state: dict) -> dict:
    """Luận cha mẹ from Tứ Trụ — paradigm Thiệu Vĩ Hoa Tập 2 Ch.12-13."""
    from .cha_me import luan_cha_me
    try:
        return luan_cha_me(state)
    except Exception as e:
        return {"patterns": [], "narrative": "", "paradigm_guard": "", "_error": str(e)[:200]}


def _detect_can_hoa_hop_in_state(state: dict) -> list[dict]:
    """Wrap luu_nien.detect_can_hoa_hop with state's pillars."""
    from .luu_nien import detect_can_hoa_hop
    pillars = state.get("tu_tru", {}).get("pillars", {})
    if not pillars:
        return []
    try:
        return detect_can_hoa_hop(pillars)
    except Exception:
        return []


def _detect_tai_lo_vs_tang(state: dict) -> dict | None:
    """Tài Tinh lộ vs tàng — paradigm Thiệu Vĩ Hoa tr. 123.

    - Tài lộ + vượng → khẳng khái, đại phóng (nhưng kị Tỉ Kiếp = bị cướp đoạt)
    - Tài tàng (có mộ kho) → giàu mà biển lận, nhỏ nhen
    - Vừa lộ vừa tàng → tích lũy + không mất đại phóng (ưu thế)
    """
    pillars = state.get("tu_tru", {}).get("pillars", {})
    if not pillars:
        return None
    # Find Tài Tinh positions
    tai_lo_pillars = []      # stems showing Chính Tài / Thiên Tài
    tai_tang_pillars = []    # hidden stems showing Tài
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        stem_tt = p.get("stem_thap_than", "")
        if "Tài" in stem_tt and "Kiếp" not in stem_tt:
            tai_lo_pillars.append(pos)
        for h in p.get("hidden_stems_thap_than", []) or []:
            tt = h.get("thap_than", "") if isinstance(h, dict) else str(h)
            if "Tài" in tt and "Kiếp" not in tt:
                tai_tang_pillars.append(pos)
                break

    has_lo = len(tai_lo_pillars) > 0
    has_tang = len(tai_tang_pillars) > 0
    if not (has_lo or has_tang):
        return None

    if has_lo and has_tang:
        pattern = "ca_lo_va_tang"
        narrative = (
            "**Tài lộ + Tàng kết hợp** ⭐ — vừa tích lũy được, vừa giữ được sự đại phóng. "
            "Thiệu Vĩ Hoa tr. 123: 'Vừa có can tàng, can lộ — có thể tích lũy lại không bị mất đại phóng.'"
        )
    elif has_lo:
        pattern = "chi_lo"
        narrative = (
            "**Tài lộ** trên thiên can — khẳng khái, đại phóng với tiền bạc. "
            "⚠️ Kị Tỉ Kiếp xung khắc — Đại Vận / Lưu Niên gặp Tỉ Kiếp = nguy cơ bị cướp đoạt / hợp tác đổ vỡ."
        )
    else:
        pattern = "chi_tang"
        narrative = (
            "**Tài tàng** trong địa chi (mộ kho) — của giấu kín, có xu hướng biển lận, dè sẻn. "
            "Thiệu Vĩ Hoa: 'càng giàu càng nhỏ nhen' nếu chỉ có tàng không lộ."
        )
    return {
        "pattern": pattern,
        "tai_lo_pillars": tai_lo_pillars,
        "tai_tang_pillars": list(set(tai_tang_pillars)),
        "narrative": narrative,
    }


def _detect_sat_tang_an_thau(state: dict) -> dict | None:
    """Sát tàng + Ấn thấu — paradigm Thiệu Vĩ Hoa tr. 123.

    'Người địa chi tàng Sát, thiên can thấu Ấn — bộ mặt hiền từ, tâm dạ độc ác.'
    """
    pillars = state.get("tu_tru", {}).get("pillars", {})
    if not pillars:
        return None
    sat_in_chi = []
    an_in_can = []
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        stem_tt = p.get("stem_thap_than", "")
        if "Ấn" in stem_tt:  # Chính Ấn / Thiên Ấn (Kiêu)
            an_in_can.append(pos)
        for h in p.get("hidden_stems_thap_than", []) or []:
            tt = h.get("thap_than", "") if isinstance(h, dict) else str(h)
            if "Thất Sát" in tt:
                sat_in_chi.append(pos)
                break
    if not (sat_in_chi and an_in_can):
        return None
    return {
        "sat_in_chi_pillars": sat_in_chi,
        "an_in_can_pillars": an_in_can,
        "narrative": (
            "**Sát tàng + Ấn thấu** ⚠️ — Thiệu Vĩ Hoa tr. 123: "
            "'bộ mặt hiền từ, tâm dạ độc ác'. "
            "Cấu trúc này KHÔNG predict tĩnh — chỉ cảnh báo xu hướng bề ngoài hoà nhã nhưng có thể "
            "ẩn giấu sát khí. Lưu ý khi đánh giá người bằng vẻ ngoài. "
            "Mặt tốt: tu dưỡng đúng cách → trí huệ sâu, có khả năng quyết đoán cứng rắn khi cần."
        ),
    }


def _build_dung_than_cascade(state: dict) -> list[dict]:
    """Build cascade 2-3 Dụng Thần theo Thiệu Vĩ Hoa tr. 101-109.

    Output structure cho UI hiển thị #1/#2/#3 priority.
    """
    from .dung_than import determine_dung_than_cascade
    ngu_hanh = state.get("ngu_hanh", {})
    counts = ngu_hanh.get("counts", {})
    assessment = ngu_hanh.get("day_master_assessment", {})
    day_element = (assessment.get("day_master_element") or "").lower()
    strength_tag = assessment.get("strength_tag", "balanced")
    if not day_element or not counts:
        return []
    try:
        return determine_dung_than_cascade(
            day_element=day_element,
            element_counts=counts,
            strength_tag=strength_tag,
        )
    except Exception:
        return []


def _detect_tu_tru_kho(state: dict) -> dict | None:
    """Tứ Trụ KHÔ — mệnh cục thiếu 2+ ngũ hành (Thiệu Vĩ Hoa tr. 108).

    Paradigm: "Tứ trụ rất khô, ngoài Tài Tinh ra không có gì có thể giải cứu."
    KHÔNG predict-tool — KHÔNG output "khó nuôi/chết yếu". Chỉ output WARNING
    + suggest điều hòa qua môi trường + hành động.
    """
    counts = state.get("ngu_hanh", {}).get("counts", {})
    if not counts:
        return None
    missing = [el for el in ("kim", "mộc", "thủy", "hỏa", "thổ") if counts.get(el, 0) == 0]
    if len(missing) < 2:
        return None
    # Severity by số hành thiếu
    sev = "critical" if len(missing) >= 3 else "high"
    return {
        "missing_elements": missing,
        "missing_count": len(missing),
        "severity": sev,
        "narrative": (
            f"**Tứ Trụ KHÔ** ⚠️ — mệnh cục thiếu {len(missing)} hành: "
            f"{', '.join(m.title() for m in missing)}. "
            f"Thiệu Vĩ Hoa tr. 108: _'Tứ trụ rất khô, ngoài Tài Tinh ra không có gì giải cứu.'_ "
            f"Paradigm KHÔNG predict tĩnh — đây là **TÍN HIỆU cân bằng** qua môi trường + hành động: "
            f"chọn nghề / nơi ở / quan hệ có nhiều {' + '.join(missing)} để bổ hành thiếu. "
            f"Đặc biệt chú ý sức khoẻ liên quan các hành missing (xem mục Sức Khoẻ)."
        ),
    }


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

    result = {
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
        "tu_tru_kho": _detect_tu_tru_kho(bat_tu_state),
        "dung_than_cascade": _build_dung_than_cascade(bat_tu_state),
        "tai_lo_vs_tang": _detect_tai_lo_vs_tang(bat_tu_state),
        "sat_tang_an_thau": _detect_sat_tang_an_thau(bat_tu_state),
        "can_hoa_hop": _detect_can_hoa_hop_in_state(bat_tu_state),
        "cha_me": _luan_cha_me_in_state(bat_tu_state),
        "hoa_giai": _luan_hoa_giai_in_state(bat_tu_state, current_age=current_age),
        "truong_sinh_luan": _luan_truong_sinh(bat_tu_state),
        "than_sat_highlights": _luan_than_sat(bat_tu_state),
        "dai_van_current": _luan_dai_van_current(bat_tu_state, current_age),
        "bo_huong": _bo_huong_recommendations(bat_tu_state),
        "closing": _compose_closing(bat_tu_state),
    }
    # Causal reasoning layer — "vì sao + liên kết" (v3)
    from .causal_reasoning import analyze_causal_reasoning
    result["causal_reasoning"] = analyze_causal_reasoning(
        bat_tu_state, luan_giai=result, current_age=current_age
    )
    return result
