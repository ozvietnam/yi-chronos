"""Bệnh Tật theo Trích Thiên Tủy chương 25 (Nhậm Thiết Tiều).

Source: Trích Thiên Tủy bình chú chương 25 "Bệnh Tật" (dòng 6819-7006).

PARADIGM CỐT:
1. "Ngũ hành hòa thuận, cả đời không họa" — Bát Tự + tạng phủ đều hòa
2. "Khí huyết loạn, cả đời nhiều bệnh tật" — ngũ hành đảo điên
3. KỲ THẦN nhập ngũ tạng = bệnh HUNG (sâu, khó chế)
4. KHÁCH THẦN du lục kinh = bệnh NHẸ (ngoài, dễ chế)
5. Ngũ vị hại tạng nếu ăn QUÁ ĐÀ

⭐ Paradigm số 1 cho Anh:
"Tâm đức là số 1, phong thủy là số 2, mệnh cách là thứ 3"
(TTT chương 26, dòng 7019)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# ─── 1. KỲ THẦN nhập ngũ tạng (bệnh HUNG) ────────────────────────────────────
# Verified TTT dòng 6914-6919
KY_THAN_NGU_TANG: dict[str, dict] = {
    "mộc_nhập_thổ": {
        "kỵ_thần": "Mộc",
        "tạng_bệnh": "Tỳ (lá lách)",
        "ý_nghĩa": "Kỵ Mộc nhập Thổ — Tỳ bệnh do Mộc khắc Thổ ngầm",
        "phát_ở_mùa": "Đông Xuân (khi Thổ hư thấp)",
        "biểu_hiện": [
            "Tiêu hóa kém, đầy bụng",
            "Mệt mỏi, lười vận động",
            "Phân lỏng, ăn không ngon",
            "Suy tư quá độ ↔ Tỳ bệnh",
        ],
        "phong_ngừa": "Khi Day Master KỴ Mộc → tránh stress + dưỡng Tỳ Vị (gạo lứt, bí đỏ, mật ong)",
    },
    "hỏa_nhập_kim": {
        "kỵ_thần": "Hỏa",
        "tạng_bệnh": "Phế (phổi)",
        "ý_nghĩa": "Kỵ Hỏa nhập Kim — Phế bệnh do Hỏa khắc Kim",
        "phát_ở_mùa": "Hè (Hỏa vượng)",
        "biểu_hiện": [
            "Ho khan, hơi ngắn",
            "Đại trường không thông (táo bón)",
            "Da khô, viêm họng",
            "Hỏa lên → khí Phế nghịch lên",
        ],
        "phong_ngừa": "Khi Day Master KỴ Hỏa → tránh đồ cay nóng, dưỡng Phế (lê, mộc nhĩ trắng)",
    },
    "thổ_nhập_thủy": {
        "kỵ_thần": "Thổ",
        "tạng_bệnh": "Thận + Bàng Quang",
        "ý_nghĩa": "Kỵ Thổ nhập Thủy — Thận bệnh do Thổ khắc Thủy (chặn nước)",
        "phát_ở_mùa": "Cuối hạ giao mùa",
        "biểu_hiện": [
            "Đau lưng, gối yếu",
            "Tiểu khó, tiểu không thông",
            "Bàng quang táo, khô",
            "Sinh khí giảm",
        ],
        "phong_ngừa": "Khi Day Master KỴ Thổ → tránh đồ mặn ngọt quá, dưỡng Thận (đậu đen, mè đen)",
    },
    "kim_nhập_mộc": {
        "kỵ_thần": "Kim",
        "tạng_bệnh": "Gan (Can) + Mật (Đởm)",  # ⭐ FOUNDER
        "ý_nghĩa": "Kỵ Kim nhập Mộc — GAN bệnh do Kim khắc Mộc (chính paradigm founder!)",
        "phát_ở_mùa": "Thu (Kim vượng)",
        "biểu_hiện": [
            "GÂN YẾU, dễ chuột rút, đứt gân",  # Founder!
            "Cáu gắt, dễ giận",
            "Mắt khô, kém sáng",
            "Đau nửa đầu (Đảm kinh chạy 2 bên đầu)",  # Founder!
            "Đau cổ vai gáy (3 kinh dương)",  # Founder!
            "Gan nóng sinh Hỏa, Mật hàn mà bệnh",
        ],
        "phong_ngừa": "⭐ KHI DAY MASTER MỘC YẾU + KỴ KIM (paradigm Anh) → tránh đồ cay nóng quá, dưỡng Can (đậu xanh, kỷ tử) + né gió lùa cổ vai gáy mùa thu",
    },
    "thủy_nhập_hỏa": {
        "kỵ_thần": "Thủy",
        "tạng_bệnh": "Tim (Tâm) + Tiểu Tràng",
        "ý_nghĩa": "Kỵ Thủy nhập Hỏa — Tim bệnh do Thủy khắc Hỏa",
        "phát_ở_mùa": "Đông (Thủy vượng)",
        "biểu_hiện": [
            "Hồi hộp, đánh trống ngực",
            "Mất ngủ, mộng mị",
            "Tim không mở rộng",
            "Tiểu tràng kéo dài",
        ],
        "phong_ngừa": "Khi Day Master KỴ Thủy → tránh đồ lạnh, dưỡng Tâm (long nhãn, hạt sen, đậu đỏ)",
    },
}


# ─── 2. NGŨ VỊ HẠI TẠNG (TTT dòng 6827) ──────────────────────────────────────
NGU_VI_HAI_TANG: dict[str, dict] = {
    "chua": {
        "hành": "Mộc", "tạng_vào": "Can/Gan",
        "ăn_vừa": "Bổ Can dưỡng huyết",
        "ăn_quá_đà": "HẠI GAN — uất khí, dễ giận, đau hông sườn",
        "ví_dụ": "Chanh, dấm, mơ, dâu, quả mọng chua",
    },
    "đắng": {
        "hành": "Hỏa", "tạng_vào": "Tâm/Tim",
        "ăn_vừa": "Giáng hỏa, thanh nhiệt",
        "ăn_quá_đà": "HẠI XƯƠNG — khô tủy, hại Thận âm",
        "ví_dụ": "Mướp đắng, cà phê, ca cao, trà đậm",
    },
    "ngọt": {
        "hành": "Thổ", "tạng_vào": "Tỳ/Lá lách",
        "ăn_vừa": "Bổ Tỳ ích khí",
        "ăn_quá_đà": "HẠI THỊT (cơ bắp) — cơ nhão, mỡ tích",
        "ví_dụ": "Đường tinh, bánh kẹo, mật ong (vừa thì tốt)",
    },
    "cay": {
        "hành": "Kim", "tạng_vào": "Phế/Phổi",
        "ăn_vừa": "Tuyên Phế, sơ phong",
        "ăn_quá_đà": "HẠI KHÍ — phế khí tiêu tan, ho khan",
        "ví_dụ": "Ớt, tiêu, gừng (quá nhiều)",
    },
    "mặn": {
        "hành": "Thủy", "tạng_vào": "Thận",
        "ăn_vừa": "Bổ Thận khí",
        "ăn_quá_đà": "HẠI MÁU — máu cô đặc, cao huyết áp",
        "ví_dụ": "Muối, nước mắm, đồ kho mặn",
    },
}


# ─── 3. KHÁCH THẦN du lục kinh (bệnh NHẸ) ────────────────────────────────────
KHACH_THAN_LUC_KINH: dict[str, str] = {
    "mộc_du_thổ": "Mộc du hành đất Thổ → DẠ DÀY không may (đau bụng nhẹ, ăn không ngon)",
    "hỏa_du_kim": "Hỏa du hành đất Kim → ĐẠI TRÀNG không may (đại tiện thất thường)",
    "thổ_du_thủy": "Thổ du hành đất Thủy → BÀNG QUANG có họa (tiểu không thông)",
    "kim_du_mộc": "Kim du hành đất Mộc → MẬT không may (đắng miệng)",
    "thủy_du_hỏa": "Thủy du hành đất Hỏa → ĐƯỜNG RUỘT gặp họa (rối loạn tiêu hóa)",
}


# ─── 4. PARADIGM TÂM ĐỨC > PHONG THỦY > MỆNH (TTT chương 26) ─────────────────
PARADIGM_TAM_DUC: dict = {
    "trich_dan": (
        "Tâm đức là số một, phong thủy là số hai, mệnh cách là thứ ba."
    ),
    "y_nghia": (
        "Nhân Thiết Tiều dạy: Quan trọng nhất là TÂM ĐỨC + hành động đạo đức. "
        "Phong thủy môi trường sống đứng hàng 2. Lá số mệnh cách chỉ là yếu tố 3. "
        "→ Đức năng thắng số — paradigm cốt cho Anh nuôi tâm trước, dưỡng thân thứ hai."
    ),
    "trich_sach": "TTT chương 26 (dòng 7019)",
}


@dataclass
class BenhTatTTTResult:
    """Kết quả phân tích bệnh tật theo TTT."""

    day_master_element: str
    ky_than_elements: list[str]
    benh_hung_canh_bao: list[dict]   # KỲ THẦN nhập ngũ tạng
    benh_nhe_canh_bao: list[dict]    # KHÁCH THẦN du lục kinh
    ngu_vi_advice: list[dict]        # Cảnh báo ngũ vị
    paradigm_tam_duc: dict
    tong_quat: str

    def to_dict(self) -> dict:
        return asdict(self)


# Map element → 5 kỳ thần patterns
KY_THAN_MAP: dict[str, str] = {
    "mộc_khắc_thổ": "mộc_nhập_thổ",
    "hỏa_khắc_kim": "hỏa_nhập_kim",
    "thổ_khắc_thủy": "thổ_nhập_thủy",
    "kim_khắc_mộc": "kim_nhập_mộc",
    "thủy_khắc_hỏa": "thủy_nhập_hỏa",
}

# Khắc map
HANH_KHAC: dict[str, str] = {
    "mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"
}


def analyze_benh_tat_ttt(day_master_element: str,
                         ky_than_elements: list[str]) -> BenhTatTTTResult:
    """Engine chính — phân tích bệnh tật theo TTT chương 25.

    Args:
        day_master_element: hành Day Master (vd "mộc")
        ky_than_elements: list các kỵ thần (vd ["kim", "thổ"])
    """
    # 1. Bệnh HUNG: kỳ thần nhập ngũ tạng
    benh_hung = []
    for ky_el in ky_than_elements:
        if ky_el in HANH_KHAC:
            target = HANH_KHAC[ky_el]
            key = f"{ky_el}_nhập_{target}"
            info = KY_THAN_NGU_TANG.get(key)
            if info:
                benh_hung.append({
                    "key": key,
                    "info": info,
                })

    # 2. Bệnh NHẸ: khách thần du lục kinh
    # Tất cả kỳ thần đều có thể du hành
    benh_nhe = []
    for ky_el in ky_than_elements:
        if ky_el in HANH_KHAC:
            target = HANH_KHAC[ky_el]
            key = f"{ky_el}_du_{target}"
            msg = KHACH_THAN_LUC_KINH.get(key)
            if msg:
                benh_nhe.append({
                    "key": key,
                    "y_nghia": msg,
                })

    # 3. Ngũ vị advice
    ngu_vi_advice = []
    # Map element → vị tương ứng cần tránh
    el_to_vi = {"mộc": "chua", "hỏa": "đắng", "thổ": "ngọt", "kim": "cay", "thủy": "mặn"}
    # Tránh vị của kỵ thần (vì sẽ làm kỵ thần mạnh hơn)
    for ky_el in ky_than_elements:
        vi_key = el_to_vi.get(ky_el)
        if vi_key:
            info = NGU_VI_HAI_TANG.get(vi_key)
            if info:
                ngu_vi_advice.append({
                    "vị_cần_giảm": vi_key,
                    "info": info,
                    "ly_do": f"Vị {vi_key.upper()} sinh khí cho hành {ky_el.title()} (kỵ thần), giảm bớt."
                })

    tong_quat = (
        f"Day Master {day_master_element.title()}, kỵ thần: {' + '.join([k.title() for k in ky_than_elements])}. "
        f"Phát hiện {len(benh_hung)} cảnh báo bệnh HUNG (kỳ thần nhập ngũ tạng) + "
        f"{len(benh_nhe)} cảnh báo bệnh NHẸ (khách thần du lục kinh)."
    )

    return BenhTatTTTResult(
        day_master_element=day_master_element,
        ky_than_elements=ky_than_elements,
        benh_hung_canh_bao=benh_hung,
        benh_nhe_canh_bao=benh_nhe,
        ngu_vi_advice=ngu_vi_advice,
        paradigm_tam_duc=PARADIGM_TAM_DUC,
        tong_quat=tong_quat,
    )


def render_benh_tat_ttt_markdown(result: BenhTatTTTResult) -> str:
    """Render markdown."""
    lines = [
        "## ⚕️ Bệnh Tật theo Trích Thiên Tủy chương 25\n",
        f"{result.tong_quat}\n",
        "### ⚠️ Bệnh HUNG (kỳ thần nhập ngũ tạng — sâu, khó chế)",
    ]
    for b in result.benh_hung_canh_bao:
        info = b["info"]
        lines.append(f"\n**{info['ý_nghĩa']}**")
        lines.append(f"- Tạng bệnh: **{info['tạng_bệnh']}**")
        lines.append(f"- Phát ở mùa: {info['phát_ở_mùa']}")
        lines.append(f"- Biểu hiện:")
        for b_ in info['biểu_hiện']:
            lines.append(f"  - {b_}")
        lines.append(f"- 🛡 Phòng ngừa: _{info['phong_ngừa']}_")

    if result.benh_nhe_canh_bao:
        lines.append("\n### 🟡 Bệnh NHẸ (khách thần du lục kinh)")
        for b in result.benh_nhe_canh_bao:
            lines.append(f"- {b['y_nghia']}")

    if result.ngu_vi_advice:
        lines.append("\n### 🍵 Ngũ vị cần GIẢM")
        for adv in result.ngu_vi_advice:
            info = adv["info"]
            lines.append(f"\n**Vị {adv['vị_cần_giảm'].upper()}** ({info['hành']}/{info['tạng_vào']})")
            lines.append(f"- Ăn quá đà: {info['ăn_quá_đà']}")
            lines.append(f"- Ví dụ tránh: {info['ví_dụ']}")
            lines.append(f"- Lý do: {adv['ly_do']}")

    lines.append("\n### 🪷 Paradigm CỐT — Tâm Đức")
    lines.append(f"> _{result.paradigm_tam_duc['trich_dan']}_")
    lines.append(f"> — {result.paradigm_tam_duc['trich_sach']}")
    lines.append(f"\n{result.paradigm_tam_duc['y_nghia']}")
    return "\n".join(lines)
