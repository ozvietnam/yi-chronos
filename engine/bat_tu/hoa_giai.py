"""Hóa Giải (化解) — chuyển hóa cấu trúc bất lợi qua hành động.

Paradigm Thiệu Vĩ Hoa Tập 2 Chương 24:
- KHÔNG predict tĩnh — KHÔNG nói "anh sẽ X năm Y, không thay đổi được"
- Mọi cấu hình "xấu" đều có CÁCH HÓA GIẢI qua:
  1. **Phương vị**: tránh Tam Sát / Thái Tuế / Tuế Phá theo Lưu Niên
  2. **Bù hành**: thêm hành thiếu qua môi trường (màu sắc / hướng / vật phẩm)
  3. **Dưỡng sinh**: ăn uống + tập luyện theo Dụng Thần
  4. **Phóng sinh**: làm việc thiện = tích đức = chuyển hóa nghiệp

⚠️ Iron Rule #4+6: Đây là PARADIGM, KHÔNG phải superstition predict-tool.
Hóa Giải = chuyển hóa qua hành động chứ KHÔNG phải bùa phép.
"""

from __future__ import annotations


# Tam Sát theo Tam Hợp Cục của Lưu Niên (3 hướng XẤU mỗi năm)
# Tam Sát = 3 chi đối lập với Tam Hợp Cục
TAM_SAT_BY_LUU_NIEN_GROUP: dict[str, tuple[str, ...]] = {
    # Tam hợp cục Thân-Tý-Thìn (Thủy cục) → Tam Sát ở Tỵ-Ngọ-Mùi (phương Nam)
    "thuy_cuc": ("Tỵ", "Ngọ", "Mùi"),
    # Dần-Ngọ-Tuất (Hỏa cục) → Tam Sát Hợi-Tý-Sửu (phương Bắc)
    "hoa_cuc": ("Hợi", "Tý", "Sửu"),
    # Tỵ-Dậu-Sửu (Kim cục) → Tam Sát Dần-Mão-Thìn (phương Đông)
    "kim_cuc": ("Dần", "Mão", "Thìn"),
    # Hợi-Mão-Mùi (Mộc cục) → Tam Sát Thân-Dậu-Tuất (phương Tây)
    "moc_cuc": ("Thân", "Dậu", "Tuất"),
}

LUU_NIEN_TO_GROUP: dict[str, str] = {
    "Thân": "thuy_cuc", "Tý": "thuy_cuc", "Thìn": "thuy_cuc",
    "Dần": "hoa_cuc", "Ngọ": "hoa_cuc", "Tuất": "hoa_cuc",
    "Tỵ": "kim_cuc", "Dậu": "kim_cuc", "Sửu": "kim_cuc",
    "Hợi": "moc_cuc", "Mão": "moc_cuc", "Mùi": "moc_cuc",
}


# Bù hành thiếu — màu sắc / hướng / vật phẩm
HANH_BU_CUU: dict[str, dict] = {
    "mộc": {
        "colors": ["xanh lá", "xanh dương"],
        "directions": ["Đông", "Đông Nam"],
        "items": ["cây cảnh", "tranh phong cảnh xanh", "đồ gỗ tự nhiên"],
        "foods": ["rau xanh", "trái cây chua nhẹ", "đậu"],
        "actions": ["đọc sách", "đi bộ rừng", "trồng cây", "viết lách sáng tạo"],
    },
    "hỏa": {
        "colors": ["đỏ", "hồng", "tím", "cam"],
        "directions": ["Nam"],
        "items": ["đèn ấm", "tranh mặt trời", "lò sưởi"],
        "foods": ["thực phẩm đắng / cay nhẹ", "cà phê", "trà"],
        "actions": ["thiền nhìn nến", "thuyết trình", "biểu diễn nghệ thuật"],
    },
    "thổ": {
        "colors": ["vàng", "nâu đất"],
        "directions": ["Trung tâm", "Tây Nam", "Đông Bắc"],
        "items": ["đồ gốm sứ", "đá pha lê", "tinh thể muối"],
        "foods": ["lương thực", "khoai", "ngũ cốc"],
        "actions": ["làm vườn", "thiền tĩnh", "chăm sóc người khác"],
    },
    "kim": {
        "colors": ["trắng", "bạc", "vàng kim"],
        "directions": ["Tây", "Tây Bắc"],
        "items": ["đồ kim loại", "đồng hồ", "kiếm trang trí"],
        "foods": ["thực phẩm cay", "gừng", "hành"],
        "actions": ["lập kế hoạch chi tiết", "đầu tư kỷ luật", "võ thuật"],
    },
    "thủy": {
        "colors": ["đen", "xanh đậm", "xanh dương"],
        "directions": ["Bắc"],
        "items": ["bể cá", "đài phun nước", "tranh sông biển"],
        "foods": ["thực phẩm mặn vừa phải", "hải sản", "trà"],
        "actions": ["bơi lội", "thiền nước", "du lịch nước"],
    },
}


def luan_hoa_giai(state: dict, current_luu_nien_chi: str | None = None) -> dict:
    """Tổng hợp đề xuất hóa giải dựa trên Tứ Trụ + Lưu Niên hiện tại.

    Args:
        state: bat_tu state from cast_bat_tu()
        current_luu_nien_chi: Vietnamese branch of current year (vd "Bính Ngọ" → "Ngọ")

    Returns:
        {
            "phuong_vi_tranh": list of bad directions for this year,
            "bu_hanh": dict with colors/directions/foods/actions to support Dụng Thần,
            "duong_sinh": list of lifestyle recommendations,
            "phong_sinh": paradigm tu thân tích đức,
            "paradigm_guard": notice
        }
    """
    counts = state.get("ngu_hanh", {}).get("counts", {})
    dung_than = state.get("dung_than", {})
    dung_el = dung_than.get("dung_than_element", "") if dung_than else ""

    # 1. Phương vị tránh — Tam Sát của Lưu Niên
    phuong_vi_tranh = []
    if current_luu_nien_chi:
        group = LUU_NIEN_TO_GROUP.get(current_luu_nien_chi)
        if group:
            sat_branches = TAM_SAT_BY_LUU_NIEN_GROUP[group]
            phuong_vi_tranh.append({
                "type": "tam_sat",
                "branches": list(sat_branches),
                "narrative": (
                    f"Năm {current_luu_nien_chi} ({group}): Tam Sát ở 3 chi "
                    f"{', '.join(sat_branches)}. Tránh các phương hướng tương ứng "
                    "khi xây dựng / di chuyển lớn. Không cấm tuyệt đối — cẩn trọng."
                ),
            })
        # Thái Tuế = chính chi của Lưu Niên (xung trụ năm bản mệnh = "xung Thái Tuế")
        phuong_vi_tranh.append({
            "type": "thai_tue",
            "branch": current_luu_nien_chi,
            "narrative": (
                f"Năm {current_luu_nien_chi} là Thái Tuế của bản thân năm đó. "
                "Tránh đối đầu trực diện, làm việc lớn ngược chiều. "
                "Hỏi xem có trong Tứ Trụ chi xung với {current_luu_nien_chi} không — "
                "nếu có là 'xung Thái Tuế', cần điều chỉnh."
            ),
        })

    # 2. Bù hành thiếu — ưu tiên Dụng Thần, sau là hành count thấp nhất
    target_hanh = dung_el.lower() if dung_el else None
    if not target_hanh:
        # Fallback: hành có count thấp nhất
        if counts:
            target_hanh = min(counts.items(), key=lambda kv: kv[1])[0]
    bu_hanh = HANH_BU_CUU.get(target_hanh, {}) if target_hanh else {}

    # 3. Dưỡng sinh — tập luyện + nghỉ ngơi phù hợp Dụng Thần
    duong_sinh = []
    if target_hanh == "mộc":
        duong_sinh = ["Đi bộ trong rừng / công viên xanh", "Yoga giãn cơ", "Ngủ sớm (10pm)"]
    elif target_hanh == "hỏa":
        duong_sinh = ["Thiền sáng nắng", "Tập cardio nhẹ", "Tránh đồ lạnh"]
    elif target_hanh == "thổ":
        duong_sinh = ["Làm vườn / chăm cây", "Ăn đúng giờ", "Tránh stress"]
    elif target_hanh == "kim":
        duong_sinh = ["Tập võ thuật / kỷ luật", "Hít thở sâu", "Sleep 7-8h"]
    elif target_hanh == "thủy":
        duong_sinh = ["Bơi lội / tắm nước", "Uống đủ nước", "Du lịch biển/hồ"]

    # 4. Phóng sinh = paradigm tu thân
    phong_sinh = (
        "**Phóng sinh** không chỉ là thả cá. Theo Thiệu Vĩ Hoa Tập 2 Ch.24, "
        "phóng sinh = TÍCH ĐỨC qua việc thiện hàng ngày: giúp người yếu hơn, "
        "tha thứ kẻ làm sai, không tham đoạt cái không phải của mình. "
        "Tích đức = chuyển hóa nghiệp = mở vận. Đây là CỐT của paradigm 'tu mệnh'."
    )

    paradigm_guard = (
        "⚠️ Hóa Giải KHÔNG phải bùa phép. Là CHUYỂN HÓA qua hành động cụ thể: "
        "phương vị cẩn trọng, môi trường bù hành thiếu, dưỡng sinh kỷ luật, "
        "tích đức qua việc thiện. Tử Bình paradigm: 'Mệnh cố kết, vận lưu biến — "
        "BỔ qua hành động là quyền của chính Anh.'"
    )

    return {
        "phuong_vi_tranh": phuong_vi_tranh,
        "bu_hanh": {
            "target_element": target_hanh,
            **bu_hanh,
        } if target_hanh else {},
        "duong_sinh": duong_sinh,
        "phong_sinh": phong_sinh,
        "paradigm_guard": paradigm_guard,
    }
