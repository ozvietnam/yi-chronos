"""Nhị Khí Thành Tượng (二氣成象) — 2 hành chiếm dominantly tạo thành "tượng".

Paradigm Trích Thiên Tủy bình chú (Nhậm Thiết Tiều) Chương 11 Phương Cục:

> "Hai khí thành tượng, cần phải Nhật chủ không được sinh, dụng thân hoặc thực
>  hoặc thương quan. Gọi là tinh anh tú khí, thông tuệ phú quý đều có."

5 cặp "hai khí" theo Ngũ Hành Sinh:
- **Mộc-Hỏa**: Mộc sinh Hỏa (sinh khí)
- **Hỏa-Thổ**: Hỏa sinh Thổ
- **Thổ-Kim**: Thổ sinh Kim
- **Kim-Thủy**: Kim sinh Thủy
- **Thủy-Mộc**: Thủy sinh Mộc

Đặc trưng:
- 2 hành chiếm ≥75% Tứ Trụ (6/8 element units, hoặc 4/4 chi)
- Quan hệ giữa 2 hành là sinh (không phải khắc)
- Nhật Chủ thuộc 1 trong 2 hành dominant
- Tinh anh tú khí lưu hành theo chiều sinh

Khác Tòng Cách (chỉ 1 hành chiếm) và Cách Độc Vượng (1 hành chiếm hoàn toàn).

⚠️ Iron Rule #4+6: Output = pattern paradigm, không predict tốt/xấu tĩnh.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


# Cặp Ngũ Hành tương sinh
SINH_PAIRS: list[tuple[str, str]] = [
    ("mộc", "hỏa"),
    ("hỏa", "thổ"),
    ("thổ", "kim"),
    ("kim", "thủy"),
    ("thủy", "mộc"),
]


# Tên Việt + Hán cho mỗi cặp
NHI_KHI_NAMES: dict[tuple[str, str], dict] = {
    ("mộc", "hỏa"): {
        "name_vi": "Mộc-Hỏa Thành Tượng",
        "name_hv": "Mộc Hỏa Thông Minh",
        "essence": "Mộc sinh Hỏa — tú khí lưu hành. Văn chương, sáng tạo, nghệ thuật.",
        "ideal_career": "học thuật, sáng tạo, văn chương, nghệ thuật, công nghệ",
    },
    ("hỏa", "thổ"): {
        "name_vi": "Hỏa-Thổ Thành Tượng",
        "name_hv": "Hỏa Thổ Từ Tường",
        "essence": "Hỏa sinh Thổ — đôn hậu, từ thiện. Sinh dưỡng vạn vật.",
        "ideal_career": "giáo dục, y tế, dịch vụ xã hội, công vụ, làm chủ ổn định",
    },
    ("thổ", "kim"): {
        "name_vi": "Thổ-Kim Thành Tượng",
        "name_hv": "Thổ Kim Dục Tú",
        "essence": "Thổ sinh Kim — cương trực, có nguyên tắc. Kim được Thổ nuôi sáng.",
        "ideal_career": "luật, tài chính, kỷ luật, quản lý, kỹ thuật chính xác",
    },
    ("kim", "thủy"): {
        "name_vi": "Kim-Thủy Thành Tượng",
        "name_hv": "Kim Thủy Tương Hàm",
        "essence": "Kim sinh Thủy — thanh thoát, trí tuệ. Lưu chảy không ngừng.",
        "ideal_career": "khoa học, nghiên cứu, công nghệ thông tin, ngoại giao, truyền thông",
    },
    ("thủy", "mộc"): {
        "name_vi": "Thủy-Mộc Thành Tượng",
        "name_hv": "Thủy Mộc Thanh Hoa",
        "essence": "Thủy sinh Mộc — sinh sôi, phát triển. Khí cách tinh anh.",
        "ideal_career": "giáo dục, viết lách, tư vấn, y học, nông nghiệp hữu cơ",
    },
}


@dataclass(frozen=True)
class NhiKhiResult:
    """Kết quả phát hiện Nhị Khí Thành Tượng."""

    detected: bool
    sheng_element: str         # element sinh (parent)
    receive_element: str       # element nhận sinh (child)
    name_vi: str
    name_hv: str
    essence: str
    ideal_career: str
    sheng_count: float
    receive_count: float
    total_share: float          # tổng % 2 hành / tổng 5 hành
    day_master_in_pair: bool
    day_master_role: str        # "sheng" / "receive" / "outsider"
    quality_tag: str            # "loaded" (mạnh) / "moderate" (vừa) / "weak"
    narrative: str
    yong_than_suggestion: str   # dụng thần đề xuất theo paradigm Trích Thiên Tủy

    def to_dict(self) -> dict:
        return asdict(self)


def detect_nhi_khi_thanh_tuong(element_counts: dict[str, float], day_element: str) -> dict | None:
    """Detect Nhị Khí Thành Tượng pattern.

    Args:
        element_counts: {element: count} cho 5 hành
        day_element: ngũ hành Nhật Chủ (lowercase)

    Returns:
        Dict result nếu detect được, None nếu không.

    Criteria:
        - 2 hành liên tiếp trong vòng sinh chiếm ≥70% tổng
        - Day Master thuộc 1 trong 2 hành
        - Chiếm dominantly so với 3 hành còn lại
    """
    total = sum(element_counts.values()) or 1
    day_element = (day_element or "").lower()

    best: tuple[float, str, str] | None = None  # (share, sheng, receive)
    for sheng, receive in SINH_PAIRS:
        s = element_counts.get(sheng, 0)
        r = element_counts.get(receive, 0)
        if s <= 0 or r <= 0:
            continue
        share = (s + r) / total
        if share >= 0.70:
            # Khác hành thứ 3 trở lên không được dominant
            other_max = max(
                (v for k, v in element_counts.items() if k not in (sheng, receive)),
                default=0,
            )
            # 2 hành phải mạnh hơn hành lớn nhất còn lại đáng kể
            if min(s, r) > other_max:
                if best is None or share > best[0]:
                    best = (share, sheng, receive)

    if not best:
        return None

    share, sheng, receive = best
    s_count = element_counts.get(sheng, 0)
    r_count = element_counts.get(receive, 0)
    meta = NHI_KHI_NAMES.get((sheng, receive), {})

    # Day Master role
    if day_element == sheng:
        dm_role = "sheng"  # DM là parent
        dm_in_pair = True
    elif day_element == receive:
        dm_role = "receive"  # DM là child
        dm_in_pair = True
    else:
        dm_role = "outsider"
        dm_in_pair = False

    # Quality
    if share >= 0.85:
        quality = "loaded"
        qual_vi = "rất mạnh"
    elif share >= 0.78:
        quality = "moderate"
        qual_vi = "vừa phải"
    else:
        quality = "weak"
        qual_vi = "yếu cận biên"

    # Dụng Thần suggestion theo Nhậm Thiết Tiều:
    # "Dụng thực hoặc thương quan, tú khí lưu hành"
    # Sheng → DM → tiết khí qua Thực/Thương (= con của child)
    # Receive → DM → đã là child, cần tiết khí qua hành sau (child of child)
    if dm_role == "sheng":
        # DM tiết khí qua child (= "receive")
        yong_than = (
            f"Theo Trích Thiên Tủy: Nhật Chủ ({sheng}) là sheng — TIẾT khí qua "
            f"{receive} (Thực/Thương Quan). Tú khí lưu hành theo chiều sinh."
        )
    elif dm_role == "receive":
        # DM đã là child, tiếp tục tiết qua child-of-child
        next_idx = SINH_PAIRS.index((sheng, receive)) + 1
        next_el = SINH_PAIRS[next_idx % len(SINH_PAIRS)][1] if next_idx < len(SINH_PAIRS) else None
        yong_than = (
            f"Theo Trích Thiên Tủy: Nhật Chủ ({receive}) là receive — đã được sinh đủ. "
            f"Tiếp tục tiết khí qua hành sinh tiếp ({next_el or 'hành kế tiếp'})."
            if next_el else
            f"Theo Trích Thiên Tủy: Nhật Chủ ({receive}) là receive — đã được sinh đủ. "
            "Tiếp tục tiết khí qua Thực/Thương."
        )
    else:
        yong_than = (
            f"Day Master ({day_element}) KHÔNG nằm trong cặp Nhị Khí. "
            "Cấu trúc bất hài hòa — cần Ấn hoặc Tỉ Kiếp trợ thân, hoặc khắc bớt 2 hành dominant."
        )

    narrative = (
        f"**{meta.get('name_vi', f'{sheng.title()}-{receive.title()} Thành Tượng')}** "
        f"({meta.get('name_hv', '')}) — {share*100:.0f}% Tứ Trụ chiếm bởi "
        f"{sheng.title()} ({s_count:.1f}) + {receive.title()} ({r_count:.1f}). "
        f"Chất lượng {qual_vi}. {meta.get('essence', '')}\n\n"
        f"Nghề phù hợp paradigm: {meta.get('ideal_career', 'tùy hỉ kỵ Tứ Trụ')}."
    )

    return NhiKhiResult(
        detected=True,
        sheng_element=sheng,
        receive_element=receive,
        name_vi=meta.get("name_vi", f"{sheng.title()}-{receive.title()} Thành Tượng"),
        name_hv=meta.get("name_hv", ""),
        essence=meta.get("essence", ""),
        ideal_career=meta.get("ideal_career", ""),
        sheng_count=round(s_count, 1),
        receive_count=round(r_count, 1),
        total_share=round(share, 3),
        day_master_in_pair=dm_in_pair,
        day_master_role=dm_role,
        quality_tag=quality,
        narrative=narrative,
        yong_than_suggestion=yong_than,
    ).to_dict()
