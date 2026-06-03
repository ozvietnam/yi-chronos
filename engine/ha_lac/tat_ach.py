"""Hà Lạc Tật Ách — đọc sức khỏe qua 2 quẻ Tiên Thiên + Hậu Thiên + hào Nguyên Đường.

Paradigm CỐT (kết hợp Hà Lạc Xuân Cang + Đông Y bát quái):
- Tiên Thiên Quái = THỂ (cấu trúc bẩm sinh) → tạng phủ bẩm sinh
- Hậu Thiên Quái = DỤNG (cấu trúc vận hành) → tạng phủ hiện hành
- Hào Nguyên Đường = vị trí khí huyết tập trung mạnh nhất
- Cross 8 quẻ → 8 tạng phủ (Bát Quái ↔ Tạng phủ)

Source paradigm:
- "Chữa bệnh theo Chu Dịch" chương I: Bát Quái ↔ Tạng phủ ↔ Cơ thể
- "Bát Tự Hà Lạc và Quỹ Đạo Đời Người" (Xuân Cang): paradigm Hà Lạc
- TTT chương 25: kỳ thần nhập ngũ tạng

🪷 Iron Rule #4+6: KHÔNG predict bệnh — đọc cấu trúc khí Hà Lạc đối ứng tạng phủ.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# ─── Mapping 8 trigram → tạng phủ + cơ thể ────────────────────────────────
TRIGRAM_TANG_PHU: dict[str, dict] = {
    "Càn": {
        "hieu": "☰", "hanh": "kim",
        "tang": "Đại trường", "co_the": "Đầu, não",
        "bieu_hien_khoe": "Đầu sáng, suy nghĩ minh mẫn, đại tiện đều",
        "bieu_hien_yeu": "Đau đầu, mệt não, táo bón",
        "y_nghia_hà_lạc": "Càn = cha, dương cương — bẩm sinh lãnh đạo, chịu áp lực đầu",
    },
    "Đoài": {
        "hieu": "☱", "hanh": "kim",
        "tang": "Phế (phổi)", "co_the": "Miệng, mũi, da",
        "bieu_hien_khoe": "Hơi thở đều, da mịn, mũi thông",
        "bieu_hien_yeu": "Ho khan, viêm họng, da khô, dị ứng",
        "y_nghia_hà_lạc": "Đoài = duyệt (vui vẻ), thiếu nữ — bẩm sinh giao tiếp, ngôn ngữ",
    },
    "Ly": {
        "hieu": "☲", "hanh": "hỏa",
        "tang": "Tâm + Tâm bào", "co_the": "Mắt, mạch, huyết",
        "bieu_hien_khoe": "Tim đập đều, mắt sáng, tinh thần tỉnh",
        "bieu_hien_yeu": "Hồi hộp, mất ngủ, mắt đỏ/khô",
        "y_nghia_hà_lạc": "Ly = lệ (đẹp/sáng), trung nữ — bẩm sinh trí tuệ + nhiệt huyết",
    },
    "Chấn": {
        "hieu": "☳", "hanh": "mộc",
        "tang": "Can (gan)", "co_the": "Chân + gân + móng",
        "bieu_hien_khoe": "Gân chắc, chân khỏe, móng cứng",
        "bieu_hien_yeu": "GÂN YẾU, chuột rút, đứt gân, đầu gối yếu, dễ giận",
        "y_nghia_hà_lạc": "Chấn = động (sấm), trưởng nam — bẩm sinh hành động, ra quyết định",
    },
    "Tốn": {
        "hieu": "☴", "hanh": "mộc",
        "tang": "Đởm (mật)", "co_the": "Đùi, hông, gân khớp",
        "bieu_hien_khoe": "Đùi chắc, ăn ngon, mật bài tiết đều",
        "bieu_hien_yeu": "Đắng miệng, đau hông, sỏi mật",
        "y_nghia_hà_lạc": "Tốn = nhập (gió thổi vào), trưởng nữ — bẩm sinh thấm nhuần, linh hoạt",
    },
    "Khảm": {
        "hieu": "☵", "hanh": "thủy",
        "tang": "Thận", "co_the": "Tai, xương, tủy, răng, tóc, sinh khí",
        "bieu_hien_khoe": "Tai thính, xương cứng, tóc đen, sinh khí mạnh",
        "bieu_hien_yeu": "Đau lưng, gối yếu, ù tai, tóc bạc, sinh khí giảm",
        "y_nghia_hà_lạc": "Khảm = hãm (sâu, hiểm), trung nam — bẩm sinh trí sâu, dụng tâm",
    },
    "Cấn": {
        "hieu": "☶", "hanh": "thổ",
        "tang": "Vị (dạ dày)", "co_the": "Tay, khớp",
        "bieu_hien_khoe": "Ăn ngon, tay khỏe",
        "bieu_hien_yeu": "Đau dạ dày, đầy hơi, tay tê",
        "y_nghia_hà_lạc": "Cấn = chỉ (dừng, an định), thiếu nam — bẩm sinh kiên định, dừng đúng lúc",
    },
    "Khôn": {
        "hieu": "☷", "hanh": "thổ",
        "tang": "Tỳ (lá lách)", "co_the": "Bụng, cơ thịt",
        "bieu_hien_khoe": "Bụng êm, tiêu hóa tốt, da thịt săn",
        "bieu_hien_yeu": "Đầy bụng, phân lỏng, cơ nhão, suy tư nhiều",
        "y_nghia_hà_lạc": "Khôn = thuận (đất hòa), mẹ — bẩm sinh dung nạp, kiên nhẫn",
    },
}


# ─── Hào Nguyên Đường — paradigm 6 hào (sức khỏe) ────────────────────────────
HAO_NGUYEN_DUONG_HEALTH: dict[int, dict] = {
    1: {
        "vi_tri": "Hào 1 (dưới cùng)",
        "co_the_vi_tri": "Chân, gót, bàn chân",
        "khi_huyet": "Khí huyết bắt đầu đi từ chân lên — nguồn",
        "loi_khuyen": "Dưỡng chân: đi bộ chậm, ngâm chân nước ấm, massage gan bàn chân",
    },
    2: {
        "vi_tri": "Hào 2 (thứ hai)",
        "co_the_vi_tri": "Bụng dưới, đùi, gan, mật",
        "khi_huyet": "Khí huyết tích tụ ở vùng bụng dưới + Đan điền",
        "loi_khuyen": "Dưỡng Đan điền: thở bụng, ngồi yên, ăn ấm bụng",
    },
    3: {
        "vi_tri": "Hào 3 (giữa dưới)",
        "co_the_vi_tri": "Tỳ vị, eo, lưng dưới",
        "khi_huyet": "Khí huyết qua giữa thân — cầu nối",
        "loi_khuyen": "Dưỡng eo lưng: massage 2 bên cột sống, không ngồi lâu",
    },
    4: {
        "vi_tri": "Hào 4 (giữa trên)",
        "co_the_vi_tri": "Tim, phổi, vai, lồng ngực",
        "khi_huyet": "Khí huyết tới vùng ngực — trao đổi",
        "loi_khuyen": "Dưỡng tim phổi: thở sâu, cười nhiều, tránh u sầu",
    },
    5: {
        "vi_tri": "Hào 5 (gần đỉnh)",
        "co_the_vi_tri": "Cổ, vai gáy, họng",  # ⭐ Founder
        "khi_huyet": "Khí huyết qua cổ vai — cửa ngõ lên đầu",
        "loi_khuyen": "⭐ DƯỠNG CỔ VAI GÁY: quàng khăn khi gió lùa, massage sau gáy mỗi tối, tránh điều hòa thổi trực tiếp",
    },
    6: {
        "vi_tri": "Hào 6 (đỉnh)",
        "co_the_vi_tri": "Đầu, não, đỉnh đầu",
        "khi_huyet": "Khí huyết tới đỉnh — hoàn thành chu trình",
        "loi_khuyen": "Dưỡng đầu não: ngủ đúng giờ Tý 23h-1h, tránh suy nghĩ căng buổi tối",
    },
}


@dataclass
class HaLacTatAchResult:
    """Kết quả Hà Lạc Tật Ách."""

    tien_thien_quai: str
    tien_thien_upper: str
    tien_thien_lower: str
    tien_thien_nd: int          # Hào nguyên đường
    hau_thien_quai: str
    hau_thien_upper: str
    hau_thien_lower: str
    hau_thien_nd: int
    bam_sinh_tang_phu: list[dict]    # Từ Tiên Thiên
    van_hanh_tang_phu: list[dict]    # Từ Hậu Thiên
    hao_nd_tien_loi_khuyen: dict     # ND Tiên Thiên
    hao_nd_hau_loi_khuyen: dict      # ND Hậu Thiên
    paradigm_tong_quat: str
    cross_chan_thuong: str           # Cross với chân dung Anh

    def to_dict(self) -> dict:
        return asdict(self)


def analyze_ha_lac_tat_ach(ha_lac_result: dict, day_master_element: str = "") -> HaLacTatAchResult:
    """Engine chính — phân tích Hà Lạc Tật Ách.

    Args:
        ha_lac_result: output từ engine.ha_lac.cast_ha_lac()
        day_master_element: hành Day Master để cross (vd "mộc")
    """
    tien = ha_lac_result["tien_thien_quai"]
    hau = ha_lac_result["hau_thien_quai"]

    tien_upper = tien["upper_trigram"]
    tien_lower = tien["lower_trigram"]
    hau_upper = hau["upper_trigram"]
    hau_lower = hau["lower_trigram"]

    # Bẩm sinh tạng phủ (từ Tiên Thiên)
    bam_sinh = []
    for trigram, role in [(tien_upper, "thượng (trên)"), (tien_lower, "hạ (dưới)")]:
        info = TRIGRAM_TANG_PHU.get(trigram, {})
        if info:
            bam_sinh.append({
                "trigram": trigram,
                "vai_tro": role,
                "hieu": info["hieu"],
                "hanh": info["hanh"],
                "tang": info["tang"],
                "co_the": info["co_the"],
                "khoe": info["bieu_hien_khoe"],
                "yeu": info["bieu_hien_yeu"],
                "y_nghia": info["y_nghia_hà_lạc"],
            })

    # Vận hành tạng phủ (từ Hậu Thiên)
    van_hanh = []
    for trigram, role in [(hau_upper, "thượng (trên)"), (hau_lower, "hạ (dưới)")]:
        info = TRIGRAM_TANG_PHU.get(trigram, {})
        if info:
            van_hanh.append({
                "trigram": trigram,
                "vai_tro": role,
                "hieu": info["hieu"],
                "hanh": info["hanh"],
                "tang": info["tang"],
                "co_the": info["co_the"],
                "khoe": info["bieu_hien_khoe"],
                "yeu": info["bieu_hien_yeu"],
                "y_nghia": info["y_nghia_hà_lạc"],
            })

    # Hào ND loại khuyên
    nd_tien = tien["nguyen_duong_line"]
    nd_hau = hau["nguyen_duong_line"]
    hao_tien_loi = HAO_NGUYEN_DUONG_HEALTH.get(nd_tien, {})
    hao_hau_loi = HAO_NGUYEN_DUONG_HEALTH.get(nd_hau, {})

    # Paradigm tổng quát
    tien_name = tien.get("name_vi", "")
    hau_name = hau.get("name_vi", "")
    paradigm = (
        f"Tiên Thiên **{tien_name}** ({tien_upper}/{tien_lower}) = cấu trúc bẩm sinh tạng phủ. "
        f"Hậu Thiên **{hau_name}** ({hau_upper}/{hau_lower}) = cấu trúc vận hành. "
        f"Hào ND Tiên hào {nd_tien}, Hậu hào {nd_hau}."
    )

    # Cross chân thương
    cross = ""
    if day_master_element == "mộc":
        # Check Khảm (Thủy)
        has_kham = "Khảm" in [tien_upper, tien_lower, hau_upper, hau_lower]
        has_chan_ton = any(t in [tien_upper, tien_lower, hau_upper, hau_lower] for t in ["Chấn", "Tốn"])
        if has_kham:
            cross += (
                "✨ Có quẻ KHẢM (Thủy/Thận) trong Hà Lạc — bẩm sinh có Thủy nuôi Mộc cho Anh. "
                "Đây là cơ chế tự dưỡng Can-Thận của lá số. "
            )
            # Nếu 2 quẻ Khảm
            count_kham = [tien_upper, tien_lower, hau_upper, hau_lower].count("Khảm")
            if count_kham >= 2:
                cross += (
                    f"⚠️ NHƯNG có {count_kham} quẻ Khảm — Thủy QUÁ VƯỢNG có thể NGẬP Mộc "
                    "(paradigm TTT chương 17 'vượng cực không thể tốn'). "
                    "Cần điều hòa: Thủy vừa đủ nuôi Mộc, không quá đà → tránh ngồi ngâm chân nước lâu, "
                    "không uống quá nhiều nước lạnh."
                )
        if not has_chan_ton:
            cross += (
                "\n⚠️ KHÔNG có quẻ Chấn (Can) hay Tốn (Đởm) trong Hà Lạc → "
                "Can-Đởm KHÔNG có hỗ trợ trực tiếp từ Hà Lạc — phụ thuộc vận khí và đại vận. "
                "Đây có thể là gốc của 3 triệu chứng: gân yếu + đau nửa đầu trái + cổ vai gáy."
            )

    return HaLacTatAchResult(
        tien_thien_quai=tien_name,
        tien_thien_upper=tien_upper,
        tien_thien_lower=tien_lower,
        tien_thien_nd=nd_tien,
        hau_thien_quai=hau_name,
        hau_thien_upper=hau_upper,
        hau_thien_lower=hau_lower,
        hau_thien_nd=nd_hau,
        bam_sinh_tang_phu=bam_sinh,
        van_hanh_tang_phu=van_hanh,
        hao_nd_tien_loi_khuyen=hao_tien_loi,
        hao_nd_hau_loi_khuyen=hao_hau_loi,
        paradigm_tong_quat=paradigm,
        cross_chan_thuong=cross,
    )


def render_ha_lac_tat_ach_markdown(result: HaLacTatAchResult) -> str:
    """Render markdown."""
    lines = [
        f"## ⭐ Hà Lạc Tật Ách\n",
        f"{result.paradigm_tong_quat}\n",
        f"### 🌱 Cấu trúc tạng phủ bẩm sinh (Tiên Thiên {result.tien_thien_quai})",
    ]
    for b in result.bam_sinh_tang_phu:
        lines.append(f"\n**{b['hieu']} {b['trigram']}** ({b['vai_tro']}, hành {b['hanh']}) → **{b['tang']}** (chủ {b['co_the']})")
        lines.append(f"- Khỏe: {b['khoe']}")
        lines.append(f"- Yếu: {b['yeu']}")
        lines.append(f"- _{b['y_nghia']}_")

    lines.append(f"\n### ☀ Cấu trúc tạng phủ vận hành (Hậu Thiên {result.hau_thien_quai})")
    for b in result.van_hanh_tang_phu:
        lines.append(f"\n**{b['hieu']} {b['trigram']}** ({b['vai_tro']}, hành {b['hanh']}) → **{b['tang']}**")
        lines.append(f"- Khỏe: {b['khoe']}")
        lines.append(f"- Yếu: {b['yeu']}")

    if result.hao_nd_tien_loi_khuyen:
        h = result.hao_nd_tien_loi_khuyen
        lines.append(f"\n### 🌟 Hào Nguyên Đường Tiên Thiên (hào {result.tien_thien_nd})")
        lines.append(f"- **Vị trí cơ thể:** {h['co_the_vi_tri']}")
        lines.append(f"- **Khí huyết:** {h['khi_huyet']}")
        lines.append(f"- **Lời khuyên:** {h['loi_khuyen']}")

    if result.hao_nd_hau_loi_khuyen:
        h = result.hao_nd_hau_loi_khuyen
        lines.append(f"\n### 🌟 Hào Nguyên Đường Hậu Thiên (hào {result.hau_thien_nd})")
        lines.append(f"- **Vị trí cơ thể:** {h['co_the_vi_tri']}")
        lines.append(f"- **Khí huyết:** {h['khi_huyet']}")
        lines.append(f"- **Lời khuyên:** {h['loi_khuyen']}")

    if result.cross_chan_thuong:
        lines.append(f"\n### 🎯 Cross với chân dung sức khỏe\n{result.cross_chan_thuong}")

    lines.append("\n🪷 _Iron Rule #4+6: Hà Lạc đọc cấu trúc khí — KHÔNG predict bệnh._")
    return "\n".join(lines)
