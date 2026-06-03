"""Ngũ Vận Lục Khí — paradigm Hoàng Đế Nội Kinh (Lê Văn Sửu lý luận).

Source: "Học Thuyết Âm Dương Ngũ Hành" — Lê Văn Sửu, chương 3 (Ngũ hành).
Verified dòng 2931-3346 sau OCR Tesseract VN 100 trang đầu (2026-06-03).

Paradigm CỐT (Hoàng Đế Nội Kinh):
- NGŨ VẬN — vận khí năm theo can: hợp hóa thành 1 trong 5 hành chủ năm
- LỤC KHÍ — khí trời 6 mùa nhỏ theo chi năm
- LỤC DÂM — 6 tà khí ngoài gây bệnh (Phong, Hàn, Thử, Thấp, Táo, Hỏa)

LÊ VĂN SỬU định lượng (chương 3, bảng 3-3):
| Phương | Tên khí | Hành | % nhiệt | % ẩm | Triệu chứng khi quá |
|---|---|---|---|---|---|
| Bắc | Hàn | Thủy | 0% | 50% | Tê buốt, co mạch, hàn phạm Phế |
| Nam | Hỏa/Thử | Hỏa | 100% | 50% | Sốt, say nóng, tổn huyết mạch |
| Đông | Phong | Mộc | 50% | 100% | Đau đầu di chuyển, chóng mặt |
| Tây | Táo | Kim | 50% | 0% | Da khô, ho khan, mũi họng khô |
| Trung | Thấp | Thổ | 50% | 50% | Đau khớp, tê mỏi, tiêu hóa kém |
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# ─── NGŨ VẬN — hợp hóa theo can năm ──────────────────────────────────────────
# (cốt: 2 can hợp lại tạo 1 hành chủ năm — đây là "Trung vận")
NGU_VAN: dict[str, str] = {
    "Giáp": "Thổ", "Kỷ": "Thổ",
    "Ất": "Kim", "Canh": "Kim",
    "Bính": "Thủy", "Tân": "Thủy",
    "Đinh": "Mộc", "Nhâm": "Mộc",
    "Mậu": "Hỏa", "Quý": "Hỏa",
}


# ─── LỤC KHÍ — Khí trời theo chi năm ────────────────────────────────────────
# (cốt: 6 cặp chi → 6 khí trời chủ năm)
LUC_KHI: dict[str, dict] = {
    "Tý": {"name": "Thiếu Âm Quân Hỏa", "tinh_chat": "hỏa", "tom_tat": "Nóng trong (quân hỏa)"},
    "Ngọ": {"name": "Thiếu Âm Quân Hỏa", "tinh_chat": "hỏa", "tom_tat": "Nóng trong (quân hỏa)"},
    "Sửu": {"name": "Thái Âm Thấp Thổ", "tinh_chat": "thấp", "tom_tat": "Ẩm thấp (thái âm)"},
    "Mùi": {"name": "Thái Âm Thấp Thổ", "tinh_chat": "thấp", "tom_tat": "Ẩm thấp (thái âm)"},
    "Dần": {"name": "Thiếu Dương Tướng Hỏa", "tinh_chat": "hỏa", "tom_tat": "Nóng ngoài (tướng hỏa)"},
    "Thân": {"name": "Thiếu Dương Tướng Hỏa", "tinh_chat": "hỏa", "tom_tat": "Nóng ngoài (tướng hỏa)"},
    "Mão": {"name": "Dương Minh Táo Kim", "tinh_chat": "táo", "tom_tat": "Khô (táo)"},
    "Dậu": {"name": "Dương Minh Táo Kim", "tinh_chat": "táo", "tom_tat": "Khô (táo)"},
    "Thìn": {"name": "Thái Dương Hàn Thủy", "tinh_chat": "hàn", "tom_tat": "Lạnh (hàn)"},
    "Tuất": {"name": "Thái Dương Hàn Thủy", "tinh_chat": "hàn", "tom_tat": "Lạnh (hàn)"},
    "Tỵ": {"name": "Quyết Âm Phong Mộc", "tinh_chat": "phong", "tom_tat": "Gió (phong)"},
    "Hợi": {"name": "Quyết Âm Phong Mộc", "tinh_chat": "phong", "tom_tat": "Gió (phong)"},
}


# ─── LỤC DÂM — 6 tà khí ngoài (paradigm Hoàng Đế Nội Kinh) ───────────────────
LUC_DAM: dict[str, dict] = {
    "phong": {
        "ten": "Phong (gió)",
        "hanh": "Mộc",
        "tang_dich_chu_yeu": "Can",
        "mua": "Xuân",
        "trieu_chung": [
            "Đau đầu di chuyển (chỗ đau thay đổi)",
            "Chóng mặt, hoa mắt",
            "Tê chân tay nhẹ thoáng qua",
            "Đau khớp nay chỗ này mai chỗ khác",
            "Cứng cổ vai gáy đột ngột sau gió lùa",
        ],
        "phong_ngua": [
            "Tránh gió lùa (đặc biệt vùng cổ vai gáy)",
            "Quàng khăn mỏng khi ra ngoài / điều hòa lạnh",
            "Massage huyệt Phong Trì sau tai khi cứng cổ",
        ],
        "thuc_an_chong": ["Gừng tươi", "Hành lá", "Tía tô (sơ phong)"],
    },
    "hàn": {
        "ten": "Hàn (lạnh)",
        "hanh": "Thủy",
        "tang_dich_chu_yeu": "Thận + Phế",
        "mua": "Đông",
        "trieu_chung": [
            "Co mạch máu, máu chảy chậm — TÊ BUỐT chân tay",
            "Sợ lạnh, chân tay lạnh",
            "Đau khớp xương cố định (1 chỗ) tăng khi trời lạnh",
            "Hàn phạm Phế: ho khan, hắt hơi, sổ mũi",
            "Hàn thương trường vị: tiêu chảy, đau bụng",
        ],
        "phong_ngua": [
            "Giữ ấm, đặc biệt vùng lưng (Thận) + bụng (Tỳ Vị)",
            "Tránh đồ lạnh sống, uống đá",
            "Tắm nắng buổi sáng",
        ],
        "thuc_an_chong": ["Quế chi", "Gừng khô", "Đại táo", "Thịt dê (mùa đông)"],
    },
    "thử": {
        "ten": "Thử (nóng mùa hè)",
        "hanh": "Hỏa",
        "tang_dich_chu_yeu": "Tâm + Tiểu trường",
        "mua": "Hè",
        "trieu_chung": [
            "Say nóng, choáng ngất",
            "Sốt cao, ra mồ hôi nhiều",
            "Khát nước, miệng khô",
            "Tim đập nhanh hồi hộp",
            "Thử thương khí: mệt mỏi cực độ giữa trưa nắng",
        ],
        "phong_ngua": [
            "Tránh ra nắng giữa trưa (giờ Ngọ 11h-13h)",
            "Bù điện giải khi ra mồ hôi nhiều",
            "Nghỉ trưa 15-30 phút",
        ],
        "thuc_an_chong": ["Mướp đắng", "Dưa hấu", "Đậu xanh", "Trà sen"],
    },
    "thấp": {
        "ten": "Thấp (ẩm)",
        "hanh": "Thổ",
        "tang_dich_chu_yeu": "Tỳ + Vị",
        "mua": "Cuối hạ (giao mùa)",
        "trieu_chung": [
            "Đau khớp nặng nề, nhức mỏi cố định",
            "Tiêu hóa kém, tiêu chảy",
            "Người nặng nề, lười vận động",
            "Da nhờn, viêm da tiết bã",
            "Thấp thương Tỳ Vị: đầy bụng, phân lỏng",
        ],
        "phong_ngua": [
            "Giữ khô ráo (đặc biệt mùa nồm)",
            "Tránh ngủ trên đất ẩm",
            "Vận động nhẹ để khí huyết lưu thông",
        ],
        "thuc_an_chong": ["Ý dĩ (bo bo)", "Bí đỏ", "Gừng + tỏi (táo thấp)"],
    },
    "táo": {
        "ten": "Táo (khô)",
        "hanh": "Kim",
        "tang_dich_chu_yeu": "Phế + Đại trường",
        "mua": "Thu",
        "trieu_chung": [
            "Da khô nứt, môi nứt",
            "Mũi họng khô, ho khan",
            "Táo bón",
            "Tóc khô, móng giòn",
            "Táo khí thương Phế: ho hen mùa thu",
        ],
        "phong_ngua": [
            "Uống đủ nước (đặc biệt mùa thu)",
            "Dưỡng ẩm da",
            "Tránh đồ cay nóng kéo dài",
        ],
        "thuc_an_chong": ["Lê", "Củ cải trắng", "Mộc nhĩ trắng", "Hạnh nhân", "Mật ong"],
    },
    "hỏa": {
        "ten": "Hỏa (nội nhiệt)",
        "hanh": "Hỏa",
        "tang_dich_chu_yeu": "Tâm + Can",
        "mua": "Bất kỳ (do nội thương)",
        "trieu_chung": [
            "Mắt đỏ, miệng lở loét",
            "Mất ngủ, tâm phiền",
            "Huyết áp cao, đau đầu",
            "Cáu gắt, dễ giận",
            "Hỏa thương âm: khát, gầy nhanh",
        ],
        "phong_ngua": [
            "Không thức khuya quá 23h",
            "Tránh tranh luận đốt khí",
            "Thiền, giảm stress",
        ],
        "thuc_an_chong": ["Khổ qua", "Trà hoa cúc", "Đậu xanh", "Sen (hạt + tâm)"],
    },
}


@dataclass
class NguVanLucKhiResult:
    """Kết quả Vận Khí năm."""

    year: int
    can_nam: str
    chi_nam: str
    trung_van_hanh: str          # Hành chủ năm (từ Ngũ Vận)
    luc_khi_name: str            # Tên khí chủ năm (vd "Thiếu Âm Quân Hỏa")
    luc_khi_tinh_chat: str       # phong / hàn / thử / thấp / táo / hỏa
    luc_khi_tom_tat: str
    luc_dam_canh_bao: list[dict] # 6 tà khí cảnh báo theo năm + chân dung sức khỏe
    paradigm_y_nghia: str
    cross_dm_element: str        # Quan hệ Vận-Khí năm với Day Master

    def to_dict(self) -> dict:
        return asdict(self)


def compute_ngu_van_luc_khi(can_nam: str, chi_nam: str, year: int,
                             day_master_element: str = "") -> NguVanLucKhiResult:
    """Engine chính — tính Vận Khí năm + cross với DM."""
    trung_van = NGU_VAN.get(can_nam, "?")
    luc_khi_info = LUC_KHI.get(chi_nam, {})
    luc_khi_name = luc_khi_info.get("name", "")
    luc_khi_tc = luc_khi_info.get("tinh_chat", "")
    luc_khi_tom = luc_khi_info.get("tom_tat", "")

    # Cảnh báo Lục Dâm — ưu tiên khí năm + khí đối ứng với DM yếu
    canh_bao = []
    # 1. Khí chủ năm
    if luc_khi_tc:
        cb = LUC_DAM.get(luc_khi_tc, {})
        if cb:
            canh_bao.append({
                "tinh_chat": luc_khi_tc,
                "loai": "khí chủ năm",
                "info": cb,
                "muc_do": "CAO — đây là khí ngoại chủ đạo năm nay",
            })

    # 2. Khí từ Trung Vận
    van_hanh_lower = trung_van.lower()
    tc_map = {"thủy": "hàn", "mộc": "phong", "hỏa": "hỏa", "thổ": "thấp", "kim": "táo"}
    van_tc = tc_map.get(van_hanh_lower)
    if van_tc and van_tc != luc_khi_tc:
        cb = LUC_DAM.get(van_tc, {})
        if cb:
            canh_bao.append({
                "tinh_chat": van_tc,
                "loai": "khí trung vận",
                "info": cb,
                "muc_do": "VỪA — khí ngầm năm nay",
            })

    # Cross DM
    cross = ""
    if day_master_element:
        if day_master_element == "mộc":
            if luc_khi_tc == "phong":
                cross = "Khí Phong (gió) năm nay đồng với Mộc Day Master — KHÍ THÔNG, dễ chịu. Nhưng cẩn trọng: PHONG cũng dễ thổi vào cổ vai gáy."
            elif luc_khi_tc == "hỏa":
                cross = "Khí Hỏa năm nay TIẾT khí Mộc của Anh — cần giảm suy nghĩ căng (đau nửa đầu trái) + tránh tranh luận."
            elif luc_khi_tc == "thấp":
                cross = "Khí Thấp năm nay làm Mộc Anh khắc Thổ NẶNG HƠN — Tỳ Vị dễ kém, đau khớp nặng nề."
            elif luc_khi_tc == "táo":
                cross = "Khí Táo (Kim) năm nay KHẮC Mộc — cẩn trọng cổ vai gáy + nửa đầu trái + đau khớp gối tăng."
            elif luc_khi_tc == "hàn":
                cross = "Khí Hàn năm nay sinh Mộc (Thủy → Mộc) — TỐT cho Anh. Nhưng máu chảy chậm có thể tăng nếu giữ ấm không kỹ."

    paradigm = (
        f"Năm {year} = {can_nam} {chi_nam}. "
        f"NGŨ VẬN: 2 can {can_nam} + (can hợp) → Trung Vận = **{trung_van}**. "
        f"LỤC KHÍ: chi năm {chi_nam} → khí trời = **{luc_khi_name}**."
    )

    return NguVanLucKhiResult(
        year=year,
        can_nam=can_nam,
        chi_nam=chi_nam,
        trung_van_hanh=trung_van,
        luc_khi_name=luc_khi_name,
        luc_khi_tinh_chat=luc_khi_tc,
        luc_khi_tom_tat=luc_khi_tom,
        luc_dam_canh_bao=canh_bao,
        paradigm_y_nghia=paradigm,
        cross_dm_element=cross,
    )


def render_ngu_van_luc_khi_markdown(result: NguVanLucKhiResult) -> str:
    """Render markdown."""
    lines = [
        f"## 🌀 Ngũ Vận Lục Khí — Năm {result.year}\n",
        f"_(Paradigm Hoàng Đế Nội Kinh — verified Lê Văn Sửu chương 3)_\n",
        f"### Vận Khí năm\n",
        f"- **Năm:** {result.can_nam} {result.chi_nam}",
        f"- **Trung Vận (Ngũ Vận):** hành {result.trung_van_hanh}",
        f"- **Khí trời (Lục Khí):** {result.luc_khi_name} — {result.luc_khi_tom_tat}",
        f"\n{result.paradigm_y_nghia}\n",
    ]
    if result.cross_dm_element:
        lines.append(f"### 🎯 Cross với Day Master\n{result.cross_dm_element}\n")

    lines.append("### ⚠️ Lục Dâm cảnh báo")
    for cb in result.luc_dam_canh_bao:
        info = cb["info"]
        lines.append(f"\n**{info['ten']}** ({cb['loai']} — {cb['muc_do']})")
        lines.append(f"- Tạng dễ tổn: **{info['tang_dich_chu_yeu']}**")
        lines.append(f"- Triệu chứng:")
        for t in info["trieu_chung"]:
            lines.append(f"  - {t}")
        lines.append(f"- Phòng ngừa: {' · '.join(info['phong_ngua'])}")
        lines.append(f"- Thực phẩm chống: {' · '.join(info['thuc_an_chong'])}")

    lines.append(
        "\n🪷 _Iron Rule #4+6: Vận khí năm là CẤU TRÚC KHÍ TRỜI tổng quát. "
        "KHÔNG predict ngày bệnh cụ thể. Giúp Anh chủ động phòng theo MÙA._"
    )
    return "\n".join(lines)
