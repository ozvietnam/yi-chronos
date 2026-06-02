"""Kinh Lạc Overview — 12 kinh chính + giờ khí huyết (paradigm Đông Y cổ).

Source: Hoàng Đế Nội Kinh + giáo trình Đông y truyền thống.

12 kinh chính (Thập Nhị Chính Kinh) — 6 dương + 6 âm:
- 3 kinh dương tay: Đại trường, Tiểu trường, Tam tiêu
- 3 kinh âm tay: Phế, Tâm, Tâm bào
- 3 kinh dương chân: Vị, Bàng quang, Đởm
- 3 kinh âm chân: Tỳ, Thận, Can

Mỗi kinh hoạt động cao điểm 2 giờ trong ngày (12 thời thần × 2h = 24h).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


KINH_LAC_12: dict[str, dict] = {
    "Phế": {
        "type": "âm tay",
        "tang_phu": "Phế (Phổi)",
        "hanh": "kim",
        "que": "Đoài",
        "gio_vuong": "3h-5h (giờ Dần)",
        "function": "Chủ khí, hô hấp, da",
        "trieu_chung_benh": ["ho", "hen", "ngạt mũi", "da khô"],
    },
    "Đại trường": {
        "type": "dương tay",
        "tang_phu": "Đại trường",
        "hanh": "kim",
        "que": "Càn",
        "gio_vuong": "5h-7h (giờ Mão)",
        "function": "Thải độc, bài tiết",
        "trieu_chung_benh": ["táo bón", "tiêu chảy", "đầy hơi"],
    },
    "Vị": {
        "type": "dương chân",
        "tang_phu": "Vị (Dạ dày)",
        "hanh": "thổ",
        "que": "Cấn",
        "gio_vuong": "7h-9h (giờ Thìn)",
        "function": "Tiếp nhận thức ăn, tiêu hóa",
        "trieu_chung_benh": ["đau dạ dày", "nôn", "kén ăn"],
    },
    "Tỳ": {
        "type": "âm chân",
        "tang_phu": "Tỳ (Lá lách)",
        "hanh": "thổ",
        "que": "Khôn",
        "gio_vuong": "9h-11h (giờ Tỵ)",
        "function": "Vận hóa thủy cốc, sinh huyết",
        "trieu_chung_benh": ["mệt mỏi", "đầy bụng", "phân lỏng", "phù"],
    },
    "Tâm": {
        "type": "âm tay",
        "tang_phu": "Tâm (Tim)",
        "hanh": "hỏa",
        "que": "Ly",
        "gio_vuong": "11h-13h (giờ Ngọ)",
        "function": "Chủ huyết mạch, thần chí",
        "trieu_chung_benh": ["hồi hộp", "mất ngủ", "tâm phiền"],
    },
    "Tiểu trường": {
        "type": "dương tay",
        "tang_phu": "Tiểu trường",
        "hanh": "hỏa",
        "que": "Ly",
        "gio_vuong": "13h-15h (giờ Mùi)",
        "function": "Phân thanh trọc, hấp thu dinh dưỡng",
        "trieu_chung_benh": ["đau bụng", "tiêu hóa kém"],
    },
    "Bàng quang": {
        "type": "dương chân",
        "tang_phu": "Bàng quang",
        "hanh": "thủy",
        "que": "Khảm",
        "gio_vuong": "15h-17h (giờ Thân)",
        "function": "Chứa và bài tiết nước tiểu",
        "trieu_chung_benh": ["tiểu khó", "đau lưng dưới"],
    },
    "Thận": {
        "type": "âm chân",
        "tang_phu": "Thận",
        "hanh": "thủy",
        "que": "Khảm",
        "gio_vuong": "17h-19h (giờ Dậu)",
        "function": "Tàng tinh, chủ cốt tủy, sinh khí",
        "trieu_chung_benh": ["đau lưng", "gối yếu", "ù tai", "tóc bạc sớm"],
    },
    "Tâm bào": {
        "type": "âm tay",
        "tang_phu": "Tâm bào",
        "hanh": "hỏa",
        "que": "Ly",
        "gio_vuong": "19h-21h (giờ Tuất)",
        "function": "Bảo vệ Tâm",
        "trieu_chung_benh": ["lo lắng", "đánh trống ngực nhẹ"],
    },
    "Tam tiêu": {
        "type": "dương tay",
        "tang_phu": "Tam tiêu (thượng-trung-hạ)",
        "hanh": "hỏa",
        "que": "Ly",
        "gio_vuong": "21h-23h (giờ Hợi)",
        "function": "Đường dẫn khí và thủy dịch",
        "trieu_chung_benh": ["mất cân bằng nóng-lạnh", "phù"],
    },
    "Đởm": {
        "type": "dương chân",
        "tang_phu": "Đởm (Mật)",
        "hanh": "mộc",
        "que": "Tốn",
        "gio_vuong": "23h-1h (giờ Tý)",
        "function": "Tích trữ và bài tiết dịch mật, quyết đoán",
        "trieu_chung_benh": ["đắng miệng", "sỏi mật", "do dự"],
    },
    "Can": {
        "type": "âm chân",
        "tang_phu": "Can (Gan)",
        "hanh": "mộc",
        "que": "Chấn",
        "gio_vuong": "1h-3h (giờ Sửu)",
        "function": "Tàng huyết, chủ gân, sơ tiết",
        "trieu_chung_benh": ["gân yếu", "đau hông sườn", "dễ giận", "mắt khô"],
    },
}


@dataclass
class KinhLacResult:
    """Kết quả tra cứu Kinh Lạc."""

    target_tang: str
    kinh_chinh: str
    kinh_info: dict
    gio_duong: str
    cap_doi_bieu_ly: str  # Tạng (âm) + Phủ (dương) cùng hành
    cap_doi_info: dict
    narrative: str

    def to_dict(self) -> dict:
        return asdict(self)


# Mapping tạng phủ → kinh tương ứng
TANG_TO_KINH: dict[str, str] = {
    "phế": "Phế", "phổi": "Phế",
    "đại trường": "Đại trường",
    "vị": "Vị", "dạ dày": "Vị",
    "tỳ": "Tỳ", "lá lách": "Tỳ",
    "tâm": "Tâm", "tim": "Tâm",
    "tiểu trường": "Tiểu trường",
    "bàng quang": "Bàng quang",
    "thận": "Thận",
    "tâm bào": "Tâm bào",
    "tam tiêu": "Tam tiêu",
    "đởm": "Đởm", "mật": "Đởm",
    "can": "Can", "gan": "Can",
}

# Cặp đôi biểu-lý (tạng âm + phủ dương cùng hành)
CAP_DOI: dict[str, str] = {
    "Phế": "Đại trường", "Đại trường": "Phế",
    "Tỳ": "Vị", "Vị": "Tỳ",
    "Tâm": "Tiểu trường", "Tiểu trường": "Tâm",
    "Thận": "Bàng quang", "Bàng quang": "Thận",
    "Tâm bào": "Tam tiêu", "Tam tiêu": "Tâm bào",
    "Can": "Đởm", "Đởm": "Can",
}


def tra_kinh_lac(tang_name: str) -> KinhLacResult | None:
    """Tra kinh lạc theo tên tạng phủ.

    Args: tang_name (vd "Can", "Thận")
    Returns: KinhLacResult hoặc None
    """
    tang_lower = tang_name.lower()
    kinh = None
    for key, k in TANG_TO_KINH.items():
        if key in tang_lower:
            kinh = k
            break
    if not kinh:
        return None

    info = KINH_LAC_12[kinh]
    cap_kinh = CAP_DOI.get(kinh, "")
    cap_info = KINH_LAC_12.get(cap_kinh, {})

    narrative = (
        f"Kinh **{kinh}** ({info['type']}) — hành {info['hanh'].title()}, "
        f"quẻ {info['que']}.\n\n"
        f"**Giờ vượng:** {info['gio_vuong']} — đây là giờ khí huyết chảy mạnh nhất qua kinh này, "
        f"nên dưỡng / châm cứu / bổ sung trong giờ này.\n\n"
        f"**Chức năng:** {info['function']}\n\n"
        f"**Triệu chứng khi bệnh:** {', '.join(info['trieu_chung_benh'])}\n\n"
        f"**Cặp đôi biểu-lý:** {kinh} ↔ {cap_kinh} — "
        f"cùng hành {info['hanh'].title()}, "
        + (f"giờ vượng cặp: {cap_info.get('gio_vuong', '')}" if cap_info else "")
    )

    return KinhLacResult(
        target_tang=tang_name,
        kinh_chinh=kinh,
        kinh_info=info,
        gio_duong=info["gio_vuong"],
        cap_doi_bieu_ly=cap_kinh,
        cap_doi_info=cap_info,
        narrative=narrative,
    )


def render_kinh_lac_markdown(result: KinhLacResult) -> str:
    """Render markdown."""
    return f"## 🌐 Kinh Lạc — {result.kinh_chinh}\n\n{result.narrative}"
