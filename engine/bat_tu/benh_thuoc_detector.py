"""Bệnh-Thuốc Detector — phát hiện bệnh + tìm thần thuốc (TTT chương 18).

Paradigm CỐT (Nhậm Thiết Tiều, TTT chương 18 dòng 2511):
> "Hữu bệnh phương vi quý, vô thương bát thị kỳ."
>  (Có bệnh có thuốc chữa mới là quý; không bệnh không thuốc thì kỳ.)

> "Có bệnh có thuốc chữa, cát hung dễ dàng nghiệm đúng,
>  không bệnh không thuốc, hoạ phúc khó đoán."

Bệnh trong Bát Tự = khuyết tật cấu trúc lá số:
- Tài nhiều khắc Ấn (DM nhược không cứu được)
- Quan Sát vượng khắc DM (không có Ấn hóa)
- Tỷ Kiếp đoạt Tài (DM vượng tranh tài)
- Thực Thương kiến Quan (vô thuốc → hung)
- Nguyên Lưu tắc mạch (dòng không thông)
- Hư phù (DM lộ mà không có gốc)

Thuốc = thần CHẾ được bệnh:
- Tài nhiều → thuốc là Tỷ Kiếp (chế Tài) hoặc Quan (chế Tỷ Kiếp đoạt Tài lại)
- Quan vượng → thuốc là Ấn (hóa Quan) hoặc Thực Thương (chế Quan)
- Thực Thương kiến Quan → thuốc là Ấn (chế Thực Thương cứu Quan)
- Mạch tắc → thuốc là element dẫn mạch
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class BenhThuoc:
    """1 cặp Bệnh + Thuốc."""

    benh_name: str           # vd "Tài nhiều khắc Ấn"
    benh_severity: str       # "nhẹ" / "vừa" / "nặng"
    benh_evidence: str       # paradigm cụ thể trong lá số
    thuoc_thần: str          # vd "Tỷ Kiếp"
    thuoc_element: str       # vd "mộc"
    thuoc_present: bool      # đã có trong lá số chưa?
    thuoc_position: str      # vị trí (nếu có)
    fix_suggestion: str      # hướng hành động
    trich_sach: str          # citation

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BenhThuocResult:
    """Kết quả tổng."""

    benh_list: list[BenhThuoc]
    benh_count: int
    co_thuoc_count: int           # bệnh đã có thuốc
    vo_thuoc_count: int           # bệnh chưa có thuốc
    overall_grade: str            # "quý" / "trung bình" / "khó đoán" / "rất hung"
    narrative: str
    trich_dan: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "benh_list": [b.to_dict() for b in self.benh_list],
            "benh_count": self.benh_count,
            "co_thuoc_count": self.co_thuoc_count,
            "vo_thuoc_count": self.vo_thuoc_count,
            "overall_grade": self.overall_grade,
            "narrative": self.narrative,
            "trich_dan": self.trich_dan,
        }


def detect_benh_thuoc(tu_tru: dict) -> BenhThuocResult:
    """Engine chính — phát hiện bệnh + thuốc."""
    from .phu_uc_route import STEM_ELEMENT, _count_pressure, ELEMENT_RELATION
    from .thong_can import summarize_day_master_thong_can

    pillars = tu_tru["pillars"]
    day_master_stem = pillars["day"]["stem"]
    dm_element = STEM_ELEMENT.get(day_master_stem, "")

    # Diagnostics
    tc = summarize_day_master_thong_can(pillars)
    tc_score = tc.get("score", 0)
    pressure = _count_pressure(pillars, dm_element)
    rel = ELEMENT_RELATION.get(dm_element, {})

    benh_list: list[BenhThuoc] = []

    # ─── Bệnh 1: Tài nhiều khắc Ấn ──────────────────────────────────────
    if pressure.get("tài", 0) >= 3.0 and pressure.get("ấn", 0) < 1.5 and tc_score < 2.0:
        thuoc_el = rel.get("tỷ", "")
        thuoc_present = pressure.get("tỷ", 0) >= 1.0
        benh_list.append(BenhThuoc(
            benh_name="Tài nhiều khắc Ấn",
            benh_severity="nặng" if pressure["tài"] >= 4.0 else "vừa",
            benh_evidence=(
                f"Tài áp lực {pressure['tài']:.1f} >= 3.0 + Ấn yếu {pressure.get('ấn', 0):.1f} < 1.5 "
                f"+ Day Master thông căn {tc_score} < 2.0. Ấn không cứu được DM."
            ),
            thuoc_thần="Tỷ Kiếp",
            thuoc_element=thuoc_el,
            thuoc_present=thuoc_present,
            thuoc_position=("có" if thuoc_present else "chưa lộ rõ — cần vận bù"),
            fix_suggestion=(
                f"Tìm đồng đạo cùng hành {thuoc_el.title()} để chế bớt Tài "
                f"+ bảo vệ học vấn (Ấn) khỏi bị tiền của kéo đi."
            ),
            trich_sach="Trích Thiên Tủy TH1 (dòng 1682)",
        ))

    # ─── Bệnh 2: Quan Sát vượng không có Ấn hóa ─────────────────────────
    if pressure.get("quan_sát", 0) >= 3.0 and pressure.get("ấn", 0) < 1.5 and tc_score < 2.0:
        thuoc_el = rel.get("ấn", "")
        thuoc_present = False
        benh_list.append(BenhThuoc(
            benh_name="Quan Sát vượng + Ấn vô lực",
            benh_severity="nặng" if pressure["quan_sát"] >= 4.0 else "vừa",
            benh_evidence=(
                f"Quan Sát áp lực {pressure['quan_sát']:.1f} + Ấn {pressure.get('ấn', 0):.1f} < 1.5. "
                "Áp lực ngoài lớn không có thần hóa."
            ),
            thuoc_thần="Chính Ấn (ưu tiên hơn Kiêu Thần)",
            thuoc_element=thuoc_el,
            thuoc_present=thuoc_present,
            thuoc_position="cần vận Ấn (Thủy cho Mộc, Mộc cho Hỏa, ...)",
            fix_suggestion=(
                f"Học vấn / mentor có {thuoc_el.title()} để hóa áp lực Quan Sát. "
                "KHÔNG đối đầu trực diện."
            ),
            trich_sach="Trích Thiên Tủy TH2 (dòng 1683)",
        ))

    # ─── Bệnh 3: Tỷ Kiếp đoạt Tài (DM vượng) ──────────────────────────
    if pressure.get("tỷ", 0) >= 3.0 and pressure.get("tài", 0) >= 1.0 and tc_score >= 4.0:
        thuoc_el = rel.get("quan_sát", "")
        thuoc_present = pressure.get("quan_sát", 0) >= 1.0
        benh_list.append(BenhThuoc(
            benh_name="Tỷ Kiếp đoạt Tài",
            benh_severity="nặng" if pressure["tỷ"] >= 4.0 else "vừa",
            benh_evidence=(
                f"Tỷ Kiếp áp lực {pressure['tỷ']:.1f} >= 3.0 + có Tài {pressure['tài']:.1f}. "
                "Anh em tranh ăn của mình."
            ),
            thuoc_thần="Quan Sát (chế Tỷ Kiếp)",
            thuoc_element=thuoc_el,
            thuoc_present=thuoc_present,
            thuoc_position=("có" if thuoc_present else "chưa lộ"),
            fix_suggestion=(
                "Cần kỷ luật / cấp trên / luật pháp để bảo vệ tài. "
                "Tránh hợp tác đồng đạo trong việc liên quan tiền."
            ),
            trich_sach="Dự đoán Tứ Trụ Thiệu Vĩ Hoa",
        ))

    # ─── Bệnh 4: Hư Phù (DM lộ mà không có gốc) ────────────────────────
    if tc_score == 0 and pressure.get("ấn", 0) + pressure.get("tỷ", 0) < 2.0:
        thuoc_el_an = rel.get("ấn", "")
        thuoc_el_ty = rel.get("tỷ", "")
        benh_list.append(BenhThuoc(
            benh_name="Hư Phù (DM không có gốc)",
            benh_severity="nặng",
            benh_evidence=(
                f"Thông căn score = 0, Ấn+Tỷ tổng {pressure.get('ấn', 0) + pressure.get('tỷ', 0):.1f} < 2.0. "
                "Day Master rỗng, gặp khắc dễ vỡ."
            ),
            thuoc_thần=f"Ấn ({thuoc_el_an}) + Tỷ Kiếp ({thuoc_el_ty})",
            thuoc_element=f"{thuoc_el_an} + {thuoc_el_ty}",
            thuoc_present=False,
            thuoc_position="cần vận Ấn-Tỷ bù lại",
            fix_suggestion=(
                "Bồi gốc tinh thần (học vấn) + tìm đồng đạo. "
                "Không gồng làm việc lớn lúc gốc còn yếu."
            ),
            trich_sach="Trích Thiên Tủy về Hư Phù",
        ))

    # ─── Bệnh 5: Nguyên Lưu tắc mạch ────────────────────────────────────
    try:
        from .nguyen_luu_trace import trace_nguyen_luu
        nl = trace_nguyen_luu(tu_tru)
        if nl.chan_tro_element and len(nl.luu_chain) <= 2:
            benh_list.append(BenhThuoc(
                benh_name="Nguyên Lưu tắc mạch",
                benh_severity="vừa",
                benh_evidence=(
                    f"Dòng chảy chỉ đi {len(nl.luu_chain)} bước (từ {nl.nguyen_element.title()}). "
                    f"Mạch đứt tại {nl.chan_tro_element.title()} ({nl.chan_tro_position})."
                ),
                thuoc_thần=f"Element dẫn mạch: {nl.chan_tro_element.title()}",
                thuoc_element=nl.chan_tro_element,
                thuoc_present=False,
                thuoc_position="cần vận bù",
                fix_suggestion=(
                    f"Tìm môi trường/cơ hội có {nl.chan_tro_element.title()} để dẫn dòng khí "
                    "vượng đi tiếp. Đại vận có thể bù."
                ),
                trich_sach="Trích Thiên Tủy chương 19 (Nguyên Lưu)",
            ))
    except Exception:
        pass

    # ─── Tổng hợp ────────────────────────────────────────────────────────
    benh_count = len(benh_list)
    co_thuoc = sum(1 for b in benh_list if b.thuoc_present)
    vo_thuoc = benh_count - co_thuoc

    if benh_count == 0:
        grade = "khó_đoán"  # vô bệnh vô thuốc — TTT chương 18: hoạ phúc khó đoán
        grade_text = "Vô bệnh vô thuốc — hoạ phúc khó đoán (TTT chương 18)"
    elif co_thuoc == benh_count:
        grade = "quý"
        grade_text = "Hữu bệnh + đủ thuốc = QUÝ (đúng paradigm TTT chương 18)"
    elif co_thuoc > vo_thuoc:
        grade = "trung_bình"
        grade_text = f"Có {co_thuoc}/{benh_count} bệnh đã có thuốc, còn {vo_thuoc} cần vận bù"
    else:
        grade = "rất_hung"
        grade_text = f"Có {vo_thuoc}/{benh_count} bệnh chưa có thuốc — cần đại vận hỗ trợ"

    narrative_parts = [
        f"**Tổng số bệnh phát hiện:** {benh_count}",
        f"**Đã có thuốc:** {co_thuoc} bệnh",
        f"**Chưa có thuốc:** {vo_thuoc} bệnh",
        f"**Đánh giá:** {grade_text}",
    ]
    for i, b in enumerate(benh_list, 1):
        status = "✅ có thuốc" if b.thuoc_present else "⚠️ chưa thuốc"
        narrative_parts.append(
            f"\n**Bệnh {i}** ({b.benh_severity}): {b.benh_name} — {status}\n"
            f"- Bằng chứng: {b.benh_evidence}\n"
            f"- Thuốc: {b.thuoc_thần} ({b.thuoc_element})\n"
            f"- Vị trí thuốc: {b.thuoc_position}\n"
            f"- Hành động: {b.fix_suggestion}"
        )

    return BenhThuocResult(
        benh_list=benh_list,
        benh_count=benh_count,
        co_thuoc_count=co_thuoc,
        vo_thuoc_count=vo_thuoc,
        overall_grade=grade,
        narrative="\n\n".join(narrative_parts),
        trich_dan=[
            {
                "sach": "Trích Thiên Tủy chương 18 (Trung Hòa)",
                "dong": 2511,
                "noi_dung": (
                    "Hữu bệnh phương vi quý, vô thương bát thị kỳ. "
                    "Có bệnh có thuốc chữa, cát hung dễ dàng nghiệm đúng, "
                    "không bệnh không thuốc, hoạ phúc khó đoán."
                ),
            },
        ],
    )


def render_benh_thuoc_markdown(result: BenhThuocResult) -> str:
    """Render markdown."""
    grade_emoji = {
        "quý": "✨",
        "trung_bình": "🟡",
        "rất_hung": "🔴",
        "khó_đoán": "⚪",
    }
    emoji = grade_emoji.get(result.overall_grade, "?")
    lines = [
        f"## 💊 Bệnh-Thuốc Detector (TTT chương 18) {emoji}\n",
        result.narrative,
        f"\n### 📖 Trích Trích Thiên Tủy",
    ]
    for td in result.trich_dan:
        dong_str = f" (dòng {td['dong']})" if td.get("dong") else ""
        lines.append(f"\n> _{td['noi_dung']}_  ")
        lines.append(f"> — **{td['sach']}**{dong_str}")
    lines.append(
        "\n🪷 _Iron Rule #4+6 + Đức năng thắng số: Bệnh có thuốc rồi — hành động vẫn của anh._"
    )
    return "\n".join(lines)
