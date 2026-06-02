"""Tạng Phủ Chẩn Đoán — Bát Quái ↔ Tạng phủ ↔ Cơ thể (Đông Y paradigm).

Source: "Chữa bệnh theo Chu Dịch" (Lý Ngọc Sơn + Lý Kiện Dân) — chương I, dòng 314-565
+ Hoàng Đế Nội Kinh (Ngũ hành ↔ Tạng phủ).

Paradigm CỐT (trích sách, dòng 322-326):
> "Bát quái tượng số liệu pháp trong quan hệ lấy BÁT QUÁI VI THỂ, NGŨ HÀNH VI DỤNG —
>  chính là thể hiện nguyên lý vĩnh hằng của vũ trụ."

Mỗi tạng phủ map vào 1 quẻ + 1 hành + 1 bộ phận cơ thể:
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ─── Bảng Bát Quái ↔ Tạng Phủ ↔ Cơ thể ──────────────────────────────────────
# Extract từ "Chữa bệnh theo Chu Dịch" chương I dòng 314-565 (đã verified)

QUE_TANG_PHU: dict[str, dict] = {
    "Càn": {
        "hieu": "☰",
        "so_tien_thien": 1,
        "hanh": "kim",
        "tinh_chat": "Kiện (cương kiện, khỏe)",
        "tang": "Đại trường",
        "co_the": "Đầu",
        "tu_nhien": "Thiên (Trời)",
        "gia_toc": "Cha",
        "khai_khieu": "Đầu, não",
        "bieu_hien_khoe": "Đầu sáng, suy nghĩ minh mẫn, đại tiện đều",
        "bieu_hien_yeu": "Đau đầu kéo dài, mệt mỏi tinh thần, táo bón",
    },
    "Đoài": {
        "hieu": "☱",
        "so_tien_thien": 2,
        "hanh": "kim",
        "tinh_chat": "Duyệt (vui vẻ, hòa duyệt)",
        "tang": "Phế (Phổi)",
        "co_the": "Miệng",
        "tu_nhien": "Trạch (Đầm)",
        "gia_toc": "Thiếu nữ",
        "khai_khieu": "Mũi, da",
        "bieu_hien_khoe": "Hơi thở đều, da dẻ mịn, mũi thông",
        "bieu_hien_yeu": "Ho khan, viêm họng, da khô, mũi nghẹt, dị ứng",
    },
    "Ly": {
        "hieu": "☲",
        "so_tien_thien": 3,
        "hanh": "hỏa",
        "tinh_chat": "Lệ (đẹp, sáng)",
        "tang": "Tâm + Tâm bào",
        "co_the": "Mắt",
        "tu_nhien": "Hỏa (Lửa)",
        "gia_toc": "Trung nữ",
        "khai_khieu": "Lưỡi, mạch",
        "bieu_hien_khoe": "Tim đập đều, mắt sáng, tinh thần tỉnh táo",
        "bieu_hien_yeu": "Hồi hộp đánh trống ngực, mất ngủ, mắt khô đỏ, lưỡi lở loét",
    },
    "Chấn": {
        "hieu": "☳",
        "so_tien_thien": 4,
        "hanh": "mộc",
        "tinh_chat": "Động (chấn động, hoạt động)",
        "tang": "Can (Gan)",
        "co_the": "Chân + gân",  # ⭐ Founder
        "tu_nhien": "Lôi (Sấm)",
        "gia_toc": "Trưởng nam",
        "khai_khieu": "Mắt, gân, móng",
        "bieu_hien_khoe": "Gân chắc, chân khỏe, móng cứng, mắt nhanh",
        "bieu_hien_yeu": "Gân yếu, chuột rút, đứt gân, đầu gối yếu, móng giòn, dễ giận",
    },
    "Tốn": {
        "hieu": "☴",
        "so_tien_thien": 5,
        "hanh": "mộc",
        "tinh_chat": "Nhập (vào, hấp thụ)",
        "tang": "Đởm (Mật)",
        "co_the": "Đùi",
        "tu_nhien": "Phong (Gió)",
        "gia_toc": "Trưởng nữ",
        "khai_khieu": "Gân, khớp",
        "bieu_hien_khoe": "Đùi chắc, mật bài tiết đều, ăn ngon",
        "bieu_hien_yeu": "Đùi yếu, sỏi mật, đắng miệng, hay đau hông",
    },
    "Khảm": {
        "hieu": "☵",
        "so_tien_thien": 6,
        "hanh": "thủy",
        "tinh_chat": "Hãm (lún, sâu)",
        "tang": "Thận",
        "co_the": "Tai",
        "tu_nhien": "Thủy (Nước)",
        "gia_toc": "Trung nam",
        "khai_khieu": "Tai, xương, tủy, răng, tóc",
        "bieu_hien_khoe": "Tai thính, xương cứng, tóc đen, sinh khí mạnh, lưng vững",
        "bieu_hien_yeu": "Đau lưng, gối yếu, xương khớp lỏng, tóc bạc sớm, ù tai, sinh khí giảm",
    },
    "Cấn": {
        "hieu": "☶",
        "so_tien_thien": 7,
        "hanh": "thổ",
        "tinh_chat": "Chỉ (dừng, an định)",
        "tang": "Vị (Dạ dày)",
        "co_the": "Tay",
        "tu_nhien": "Sơn (Núi)",
        "gia_toc": "Thiếu nam",
        "khai_khieu": "Miệng, cơ",
        "bieu_hien_khoe": "Ăn ngon, tay khỏe, hấp thu tốt",
        "bieu_hien_yeu": "Đau dạ dày, đầy hơi, tay tê, kén ăn",
    },
    "Khôn": {
        "hieu": "☷",
        "so_tien_thien": 8,
        "hanh": "thổ",
        "tinh_chat": "Thuận (hòa thuận, dung nạp)",
        "tang": "Tỳ (Lá lách)",
        "co_the": "Bụng",
        "tu_nhien": "Địa (Đất)",
        "gia_toc": "Mẹ",
        "khai_khieu": "Miệng, môi, cơ thịt",
        "bieu_hien_khoe": "Bụng êm, tiêu hóa tốt, da thịt săn chắc",
        "bieu_hien_yeu": "Đầy bụng, phân lỏng, cơ nhão, mệt mỏi, suy tư nhiều",
    },
}


# Map element → list of (quẻ, tạng) — để lookup ngược
ELEMENT_TO_QUE: dict[str, list[str]] = {
    "kim": ["Càn", "Đoài"],
    "mộc": ["Chấn", "Tốn"],
    "hỏa": ["Ly"],
    "thổ": ["Cấn", "Khôn"],
    "thủy": ["Khảm"],
}


# Map cơ thể (keyword) → quẻ tương ứng
CO_THE_TO_QUE: dict[str, str] = {
    "đầu": "Càn",
    "não": "Càn",
    "miệng": "Đoài",
    "phổi": "Đoài",
    "phế": "Đoài",
    "họng": "Đoài",
    "da": "Đoài",
    "mũi": "Đoài",
    "mắt": "Ly",
    "tim": "Ly",
    "tâm": "Ly",
    "lưỡi": "Ly",
    "mạch": "Ly",
    "huyết": "Ly",
    "chân": "Chấn",
    "gân": "Chấn",
    "móng": "Chấn",
    "đầu gối": "Chấn",
    "khớp": "Chấn",  # primary, cũng có liên quan Khảm (xương)
    "gan": "Chấn",
    "can": "Chấn",
    "đùi": "Tốn",
    "mật": "Tốn",
    "đởm": "Tốn",
    "hông": "Tốn",
    "tai": "Khảm",
    "xương": "Khảm",
    "tủy": "Khảm",
    "răng": "Khảm",
    "tóc": "Khảm",
    "thận": "Khảm",
    "lưng": "Khảm",
    "sinh khí": "Khảm",
    "tay": "Cấn",
    "dạ dày": "Cấn",
    "vị": "Cấn",
    "bụng": "Khôn",
    "tỳ": "Khôn",
    "lá lách": "Khôn",
    "cơ": "Khôn",
}


@dataclass
class TangPhuChanDoanResult:
    """Kết quả chẩn đoán tạng phủ."""

    chan_thuong_input: str
    matched_que_list: list[dict]      # Các quẻ liên quan đến chấn thương
    primary_que: str                  # Quẻ chính
    primary_tang: str
    primary_hanh: str
    primary_bieu_hien_yeu: list[str]
    related_tang_via_sinh_khac: list[dict]  # Tạng liên đới qua sinh-khắc

    def to_dict(self) -> dict:
        return asdict(self)


# Ngũ hành sinh
HANH_SINH = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
HANH_KHAC = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}


def chan_doan_tang_phu(chan_thuong: str) -> TangPhuChanDoanResult:
    """Chẩn đoán tạng phủ liên quan đến chấn thương / triệu chứng input.

    Args:
        chan_thuong: text mô tả (vd "đứt gân đầu gối")

    Returns: TangPhuChanDoanResult
    """
    ct = chan_thuong.lower()
    matched = []
    seen_que = set()

    # Sort by keyword length desc — "đầu gối" match trước "đầu"
    sorted_keys = sorted(CO_THE_TO_QUE.items(), key=lambda x: -len(x[0]))
    for keyword, que in sorted_keys:
        if keyword in ct and que not in seen_que:
            info = QUE_TANG_PHU.get(que, {})
            matched.append({
                "keyword": keyword,
                "que": que,
                "hieu": info.get("hieu", ""),
                "so_tien_thien": info.get("so_tien_thien"),
                "tang": info.get("tang", ""),
                "hanh": info.get("hanh", ""),
                "co_the": info.get("co_the", ""),
            })
            seen_que.add(que)

    if not matched:
        return TangPhuChanDoanResult(
            chan_thuong_input=chan_thuong,
            matched_que_list=[],
            primary_que="", primary_tang="", primary_hanh="",
            primary_bieu_hien_yeu=[],
            related_tang_via_sinh_khac=[],
        )

    # Primary = quẻ đầu tiên match (thường là chính)
    primary = matched[0]
    primary_que = primary["que"]
    primary_info = QUE_TANG_PHU[primary_que]
    primary_hanh = primary_info["hanh"]
    primary_bieu_hien = primary_info["bieu_hien_yeu"].split(", ")

    # Tạng liên đới qua sinh-khắc
    related = []
    # Tạng SINH primary (mẹ) — nuôi dưỡng
    me_hanh = None
    for h, son in HANH_SINH.items():
        if son == primary_hanh:
            me_hanh = h
            break
    if me_hanh:
        for q in ELEMENT_TO_QUE.get(me_hanh, []):
            qinfo = QUE_TANG_PHU[q]
            related.append({
                "relation": "mẹ (sinh)",
                "que": q,
                "tang": qinfo["tang"],
                "hanh": me_hanh,
                "y_nghia": f"Tạng {qinfo['tang']} SINH ra {primary_info['tang']}. Cần bồi tạng mẹ trước.",
            })

    # Tạng primary SINH (con) — tiết khí ra
    con_hanh = HANH_SINH.get(primary_hanh)
    if con_hanh:
        for q in ELEMENT_TO_QUE.get(con_hanh, [])[:1]:  # chỉ 1
            qinfo = QUE_TANG_PHU[q]
            related.append({
                "relation": "con (sinh xuất)",
                "que": q,
                "tang": qinfo["tang"],
                "hanh": con_hanh,
                "y_nghia": f"Tạng {primary_info['tang']} SINH ra {qinfo['tang']}. Nếu mẹ yếu, con cũng yếu theo.",
            })

    # Tạng KHẮC primary — kẻ thù
    ke_thu_hanh = None
    for h, target in HANH_KHAC.items():
        if target == primary_hanh:
            ke_thu_hanh = h
            break
    if ke_thu_hanh:
        for q in ELEMENT_TO_QUE.get(ke_thu_hanh, [])[:1]:
            qinfo = QUE_TANG_PHU[q]
            related.append({
                "relation": "kẻ khắc",
                "que": q,
                "tang": qinfo["tang"],
                "hanh": ke_thu_hanh,
                "y_nghia": f"Tạng {qinfo['tang']} KHẮC {primary_info['tang']}. Khi yếu càng dễ bị áp.",
            })

    return TangPhuChanDoanResult(
        chan_thuong_input=chan_thuong,
        matched_que_list=matched,
        primary_que=primary_que,
        primary_tang=primary_info["tang"],
        primary_hanh=primary_hanh,
        primary_bieu_hien_yeu=primary_bieu_hien,
        related_tang_via_sinh_khac=related,
    )


def render_tang_phu_markdown(result: TangPhuChanDoanResult) -> str:
    """Render markdown."""
    if not result.matched_que_list:
        return f"_(Không khớp keyword nào cho: '{result.chan_thuong_input}')_"

    lines = [
        f"## 🩺 Tạng phủ liên quan\n",
        f"_Triệu chứng/chấn thương:_ **{result.chan_thuong_input}**\n",
        "### Quẻ + Tạng phủ map\n",
    ]
    for m in result.matched_que_list:
        lines.append(
            f"- **{m['hieu']} {m['que']}** (số {m['so_tien_thien']}, hành {m['hanh'].title()}) "
            f"→ Tạng **{m['tang']}** — chủ **{m['co_the']}**"
        )

    info = QUE_TANG_PHU[result.primary_que]
    lines.append(f"\n### 🎯 Tạng CHÍNH: {info['hieu']} {result.primary_que} → {result.primary_tang}\n")
    lines.append(f"**Khi yếu biểu hiện:** {info['bieu_hien_yeu']}\n")

    lines.append("### 🔄 Tạng liên đới qua sinh-khắc\n")
    for r in result.related_tang_via_sinh_khac:
        lines.append(f"- **{r['relation'].upper()}**: {r['tang']} (hành {r['hanh'].title()}) — {r['y_nghia']}")

    lines.append(
        "\n_Source: 'Chữa bệnh theo Chu Dịch' (Lý Ngọc Sơn + Lý Kiện Dân), "
        "chương I — Cơ sở lý luận Liệu pháp Tượng số Bát quái._"
    )
    return "\n".join(lines)
