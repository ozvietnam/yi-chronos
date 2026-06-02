"""Âm Dương Cân Bằng — đánh giá thân thể qua lá số Bát Tự + chấn thương.

Paradigm Hoàng Đế Nội Kinh:
> "Âm thắng tắc dương bệnh, dương thắng tắc âm bệnh.
>  Dương thắng tắc nhiệt, âm thắng tắc hàn."
>  (Âm thịnh thì dương yếu, dương thịnh thì âm yếu.
>   Dương thịnh sinh nhiệt, âm thịnh sinh hàn.)

Engine evaluate:
- Tỷ lệ Âm/Dương trong tứ trụ (qua Thiên Can + Địa Chi)
- Tỷ lệ Hỏa/Thủy (cặp đối nhau cốt)
- Đề xuất thuần thuốc / vận động để cân bằng
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# Âm/Dương của Thiên Can + Địa Chi
STEM_YIN_YANG: dict[str, str] = {
    "Giáp": "dương", "Bính": "dương", "Mậu": "dương", "Canh": "dương", "Nhâm": "dương",
    "Ất": "âm", "Đinh": "âm", "Kỷ": "âm", "Tân": "âm", "Quý": "âm",
}
BRANCH_YIN_YANG: dict[str, str] = {
    "Tý": "dương", "Dần": "dương", "Thìn": "dương", "Ngọ": "dương", "Thân": "dương", "Tuất": "dương",
    "Sửu": "âm", "Mão": "âm", "Tỵ": "âm", "Mùi": "âm", "Dậu": "âm", "Hợi": "âm",
}

# Element thuộc nóng/lạnh
ELEMENT_NHIET_HAN: dict[str, str] = {
    "hỏa": "nhiệt",   # Nóng
    "thổ": "ôn",      # Ấm
    "mộc": "ôn",      # Ấm hơi
    "kim": "lương",   # Mát
    "thủy": "hàn",    # Lạnh
}


@dataclass
class AmDuongResult:
    """Kết quả đánh giá âm dương."""

    am_count: int
    duong_count: int
    am_duong_ratio: str          # "cân bằng" / "thiên âm" / "thiên dương"
    nhiet_count: int             # Số element nhiệt (hỏa + thổ)
    han_count: int               # Số element hàn (thủy + kim)
    nhiet_han_balance: str       # "cân bằng" / "thiên nhiệt" / "thiên hàn"
    nguyen_am_vs_nguyen_duong: str  # paradigm Thận âm vs Thận dương
    advice_thuc_pham: list[str]
    advice_van_dong: list[str]
    advice_giac_ngu: list[str]
    iron_rule_note: str

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_am_duong_can_bang(tu_tru: dict, chan_thuong: str = "") -> AmDuongResult:
    """Đánh giá cân bằng âm dương qua tứ trụ + chấn thương."""
    from engine.bat_tu.constants import BRANCH_ELEMENT
    pillars = tu_tru["pillars"]

    # Đếm âm dương
    am_c, duong_c = 0, 0
    nhiet_c, han_c = 0, 0
    for pos in ("year", "month", "day", "hour"):
        p = pillars.get(pos, {})
        stem = p.get("stem")
        branch = p.get("branch")
        if stem:
            yy = STEM_YIN_YANG.get(stem)
            if yy == "âm": am_c += 1
            elif yy == "dương": duong_c += 1
        if branch:
            yy = BRANCH_YIN_YANG.get(branch)
            if yy == "âm": am_c += 1
            elif yy == "dương": duong_c += 1

            br_el = BRANCH_ELEMENT.get(branch, "").lower()
            nh = ELEMENT_NHIET_HAN.get(br_el)
            if nh in ("nhiệt", "ôn"): nhiet_c += 1
            elif nh in ("hàn", "lương"): han_c += 1

    # Phân loại
    diff = abs(am_c - duong_c)
    if diff <= 2:
        am_duong_ratio = "cân bằng"
    elif am_c > duong_c:
        am_duong_ratio = "thiên âm (âm thắng)"
    else:
        am_duong_ratio = "thiên dương (dương thắng)"

    if abs(nhiet_c - han_c) <= 2:
        nhiet_han = "cân bằng"
    elif nhiet_c > han_c:
        nhiet_han = "thiên nhiệt (nóng)"
    else:
        nhiet_han = "thiên hàn (lạnh)"

    # Chấn thương → infer nguyên âm/nguyên dương
    nguyen_text = "Cân đối — chưa phát hiện thiên lệch rõ"
    ct = chan_thuong.lower()
    if any(k in ct for k in ["gân", "đầu gối", "xương", "khớp", "lưng"]):
        nguyen_text = (
            "Triệu chứng GÂN-XƯƠNG chỉ NGUYÊN ÂM (thận âm) hư — "
            "âm dịch nuôi gân cốt không đủ. Cần TƯ ÂM (bổ nguyên âm)."
        )
    elif any(k in ct for k in ["lạnh", "tay chân lạnh", "liệt", "không sinh khí"]):
        nguyen_text = (
            "Triệu chứng HÀN LẠNH chỉ NGUYÊN DƯƠNG (thận dương) hư — "
            "khí dương không đủ làm ấm. Cần ÔN DƯƠNG (bổ nguyên dương)."
        )

    # Advice
    advice_thuc, advice_vd, advice_ngu = [], [], []

    if nhiet_han == "thiên hàn (lạnh)":
        advice_thuc += ["Gừng tươi, quế chi, đại táo (tăng dương)",
                        "Thịt dê, thịt bò (mùa lạnh)",
                        "Tránh đồ lạnh, sinh-sống, đá"]
        advice_vd += ["Vận động nhẹ buổi sáng để khởi dương",
                      "Tắm nắng 15-20 phút"]
    elif nhiet_han == "thiên nhiệt (nóng)":
        advice_thuc += ["Mướp đắng, dưa hấu, đậu xanh (giải nhiệt)",
                        "Trà sen, trà hoa cúc",
                        "Tránh đồ cay nóng, rượu, ớt"]
        advice_vd += ["Tập sáng sớm hoặc tối mát",
                      "Tránh tập giữa trưa nắng gắt"]
    else:
        advice_thuc += ["Ăn cân đối ngũ vị: chua + đắng + ngọt + cay + mặn"]
        advice_vd += ["Vận động đều, sáng hoặc tối"]

    if am_duong_ratio == "thiên âm (âm thắng)":
        advice_thuc.append("Bổ dương: hà thủ ô, nhân sâm, ích trí nhân")
        advice_ngu.append("Dậy sớm hơn để đón dương khí")
    elif am_duong_ratio == "thiên dương (dương thắng)":
        advice_thuc.append("Tư âm: thục địa, mạch môn, kỷ tử")
        advice_ngu.append("Ngủ đủ + ngủ sớm để dưỡng âm")

    # Giờ ngủ chung
    advice_ngu.append("Giờ Tý 23h-1h: PHẢI ngủ (dưỡng Đởm-Can)")
    advice_ngu.append("Giờ Sửu 1h-3h: ngủ sâu (dưỡng Can-Gan, tàng huyết)")

    return AmDuongResult(
        am_count=am_c,
        duong_count=duong_c,
        am_duong_ratio=am_duong_ratio,
        nhiet_count=nhiet_c,
        han_count=han_c,
        nhiet_han_balance=nhiet_han,
        nguyen_am_vs_nguyen_duong=nguyen_text,
        advice_thuc_pham=advice_thuc,
        advice_van_dong=advice_vd,
        advice_giac_ngu=advice_ngu,
        iron_rule_note=(
            "🪷 Iron Rule #4+6: Đánh giá Âm-Dương theo cấu trúc khí. "
            "KHÔNG predict bệnh — chỉ điều chỉnh sinh hoạt theo paradigm Hoàng Đế Nội Kinh."
        ),
    )


def render_am_duong_markdown(result: AmDuongResult) -> str:
    lines = [
        "## ☯ Âm Dương Cân Bằng\n",
        f"**Âm:** {result.am_count} · **Dương:** {result.duong_count} → **{result.am_duong_ratio.upper()}**",
        f"**Nhiệt:** {result.nhiet_count} · **Hàn:** {result.han_count} → **{result.nhiet_han_balance.upper()}**\n",
        f"### Nguyên Âm vs Nguyên Dương\n{result.nguyen_am_vs_nguyen_duong}\n",
        "### Lời khuyên\n",
        "**🍵 Thực phẩm:**",
    ]
    for a in result.advice_thuc_pham: lines.append(f"- {a}")
    lines.append("\n**🚶 Vận động:**")
    for a in result.advice_van_dong: lines.append(f"- {a}")
    lines.append("\n**🌙 Giấc ngủ:**")
    for a in result.advice_giac_ngu: lines.append(f"- {a}")
    lines.append(f"\n---\n\n{result.iron_rule_note}")
    return "\n".join(lines)
