"""Health Synthesis — Tích hợp 4 trường phái cho 1 chân dung sức khỏe.

4 paradigm:
1. BÁT TỰ — Day Master + Phù-Ức + Bệnh-Thuốc + Nguyên Lưu
2. HÀ LẠC — Tiên Thiên + Hậu Thiên + Hào Nguyên Đường
3. ĐÔNG Y — Tạng phủ + Kinh lạc + Âm dương + Liệu pháp tượng số
4. TỬ VI — (placeholder, cần engine tat_ach riêng — nay dùng kỵ thần từ Bát Tự thay thế)

Output: 1 báo cáo TỔNG HỢP 8 sections cho người dùng.

🪷 Iron Rule #4+6: KHÔNG predict, chỉ đọc cấu trúc khí tổng hợp.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


@dataclass
class HealthSynthesisResult:
    """Báo cáo tổng hợp 4 trường phái."""

    # Section 1: Snapshot
    day_master: str
    day_master_element: str
    tien_thien_quai: str
    hau_thien_quai: str

    # Section 2: Bát Tự
    bat_tu_strength: str
    bat_tu_path: str
    bat_tu_dung_than: list[str]
    bat_tu_ky_than: list[str]

    # Section 3: Hà Lạc
    ha_lac_bam_sinh: list[dict]   # Tạng phủ bẩm sinh
    ha_lac_van_hanh: list[dict]   # Tạng phủ vận hành
    ha_lac_cross: str             # Cross với chân dung

    # Section 4: Đông Y - Tạng phủ
    dong_y_primary_tang: str
    dong_y_constitution_strength: str

    # Section 5: Đông Y - Vận khí năm
    van_khi_year: int
    trung_van: str
    luc_khi: str
    luc_dam_canh_bao: list[dict]

    # Section 6: Bệnh tật TTT chương 25
    benh_hung_canh_bao: list[dict]
    ngu_vi_can_giam: list[dict]

    # Section 7: Tượng số ưu tiên
    tuong_so_uu_tien: list[str]   # 3-5 bài niệm phù hợp

    # Section 8: Synthesis
    overall_paradigm: str
    chien_luoc_3_thang: str
    chien_luoc_1_nam: str
    tam_duc_loi_khuyen: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_health_synthesis(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
    chan_thuong: str = "",
    current_year: int = 2026,
) -> HealthSynthesisResult:
    """Engine TÍCH HỢP — gọi tất cả engines + tổng hợp."""
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.cast import cast_bat_tu
    from engine.bat_tu.constants import STEM_ELEMENT as SE
    from engine.bat_tu.phu_uc_route import route_phu_uc
    from engine.ha_lac import cast_ha_lac
    from engine.ha_lac.tat_ach import analyze_ha_lac_tat_ach
    from engine.bat_tu.luu_nien import compute_luu_nien_pillar_by_year
    from engine.dong_y.tang_phu_chan_doan import chan_doan_tang_phu
    from engine.dong_y.ngu_van_luc_khi import compute_ngu_van_luc_khi
    from engine.dong_y.benh_tat_ttt import analyze_benh_tat_ttt
    from engine.dong_y.lieu_phap_tuong_so import tim_tuong_so

    # 1. Bát Tự
    base = extract_tu_tru(birth_datetime_local, timezone)
    pillars = base["pillars"]
    dm_stem = pillars["day"]["stem"]
    dm_el = SE.get(dm_stem, "")
    tu_tru = {"pillars": pillars}
    phu_uc = route_phu_uc(tu_tru)

    # 2. Hà Lạc
    ha_lac = cast_ha_lac(birth_datetime_local=birth_datetime_local, timezone=timezone, gender=gender)
    ha_lac_ta = analyze_ha_lac_tat_ach(ha_lac, day_master_element=dm_el)

    # 3. Đông Y tạng phủ
    tp = chan_doan_tang_phu(chan_thuong) if chan_thuong else None
    dong_y_tang = tp.primary_tang if tp and tp.primary_tang else "Chưa input chấn thương"
    dong_y_strength = "yếu" if dm_el == "mộc" and phu_uc.strength_tag == "nhược" else "trung bình"

    # 4. Vận khí năm
    year_pillar = compute_luu_nien_pillar_by_year(current_year)
    van_khi = compute_ngu_van_luc_khi(
        can_nam=year_pillar["stem"],
        chi_nam=year_pillar["branch"],
        year=current_year,
        day_master_element=dm_el,
    )

    # 5. Bệnh tật TTT
    benh_tat = analyze_benh_tat_ttt(dm_el, phu_uc.ky_than_elements or [])

    # 6. Tượng số ưu tiên (sort theo chấn thương + chân dung)
    tuong_so_list = []
    # 640 cho founder Mộc nhược (bổ Can dưỡng gân)
    if dm_el == "mộc" and phu_uc.strength_tag == "nhược":
        tuong_so_list.append("640 (bổ Can dưỡng gân — dùng hàng ngày)")
    # Theo chấn thương
    if chan_thuong:
        ts = tim_tuong_so(chan_thuong)
        if ts.primary_formula:
            tuong_so_list.append(f"{ts.primary_formula['tuong_so']} ({ts.primary_formula['y_nghia']})")
    # Bài tổng quát
    tuong_so_list.append("650.30.820 (KHÍ NGŨ TẠNG — khi thấy nhiều vấn đề kèm)")

    # 7. Synthesis paradigm tổng
    paradigm = (
        f"Day Master **{dm_stem} ({dm_el})** — {phu_uc.strength_tag}. "
        f"Hà Lạc: Tiên Thiên **{ha_lac_ta.tien_thien_quai}** + Hậu Thiên **{ha_lac_ta.hau_thien_quai}**. "
        f"Vận khí năm {current_year}: Trung Vận {van_khi.trung_van_hanh}, Khí trời {van_khi.luc_khi_name}."
    )

    # 8. Chiến lược 3 tháng + 1 năm
    chien_luoc_3 = (
        f"Tháng tới (gần Lập Hạ → Tiểu Thử): Mộc đang tiết khí ra Hỏa. "
        f"Tránh suy nghĩ căng (đốt Can → đau nửa đầu trái). "
        f"Niệm 640 + 260.50.30.80 mỗi sáng. "
        f"Ngủ trước 23h để dưỡng Đởm-Can."
    )
    chien_luoc_1y = (
        f"Năm {current_year}: TRỌNG ĐIỂM dưỡng tháng 7-8 âm (Kim khắc Mộc — paradigm Anh dễ tái phát). "
        f"Tháng 10-11 âm (Thủy nuôi Mộc) — MÙA HỒI PHỤC tốt nhất. "
        f"Tránh đồ CAY + NGỌT quá đà cả năm (sinh Kim + Thổ — kỵ thần)."
    )

    # 9. Tâm Đức (paradigm TTT chương 26)
    tam_duc = (
        "🪷 'Tâm đức là số một, phong thủy là số hai, mệnh cách là thứ ba' (TTT ch.26). "
        "Lá số chỉ là cấu trúc. Hành động đạo đức + thiền + nuôi tâm an = thuốc lớn nhất."
    )

    return HealthSynthesisResult(
        day_master=dm_stem,
        day_master_element=dm_el,
        tien_thien_quai=ha_lac_ta.tien_thien_quai,
        hau_thien_quai=ha_lac_ta.hau_thien_quai,
        bat_tu_strength=phu_uc.strength_tag,
        bat_tu_path=phu_uc.path_id,
        bat_tu_dung_than=phu_uc.dung_than or [],
        bat_tu_ky_than=phu_uc.ky_than or [],
        ha_lac_bam_sinh=ha_lac_ta.bam_sinh_tang_phu,
        ha_lac_van_hanh=ha_lac_ta.van_hanh_tang_phu,
        ha_lac_cross=ha_lac_ta.cross_chan_thuong,
        dong_y_primary_tang=dong_y_tang,
        dong_y_constitution_strength=dong_y_strength,
        van_khi_year=current_year,
        trung_van=van_khi.trung_van_hanh,
        luc_khi=van_khi.luc_khi_name,
        luc_dam_canh_bao=van_khi.luc_dam_canh_bao,
        benh_hung_canh_bao=benh_tat.benh_hung_canh_bao,
        ngu_vi_can_giam=benh_tat.ngu_vi_advice,
        tuong_so_uu_tien=tuong_so_list,
        overall_paradigm=paradigm,
        chien_luoc_3_thang=chien_luoc_3,
        chien_luoc_1_nam=chien_luoc_1y,
        tam_duc_loi_khuyen=tam_duc,
    )


def render_synthesis_markdown(result: HealthSynthesisResult) -> str:
    """Render báo cáo tổng hợp 8 sections."""
    lines = [
        "# 🌿 Chân Dung Sức Khỏe Tổng Hợp — 4 Trường Phái\n",
        "_(Bát Tự + Hà Lạc + Đông Y + Vận Khí)_\n",
        "---\n",
        "## 1. Snapshot\n",
        f"- **Day Master:** {result.day_master} ({result.day_master_element})",
        f"- **Hà Lạc Tiên Thiên:** {result.tien_thien_quai}",
        f"- **Hà Lạc Hậu Thiên:** {result.hau_thien_quai}",
        f"- **Năm vận khí:** {result.van_khi_year}",
        "\n## 2. Bát Tự — Phù Ức\n",
        f"- **Cường độ:** {result.bat_tu_strength.upper()}",
        f"- **Path:** {result.bat_tu_path}",
        f"- **Dụng thần:** {' + '.join(result.bat_tu_dung_than)}",
        f"- **Kỵ thần:** {' + '.join(result.bat_tu_ky_than)}",
        "\n## 3. Hà Lạc Tật Ách\n",
        "**Bẩm sinh tạng phủ:**",
    ]
    for b in result.ha_lac_bam_sinh:
        lines.append(f"- {b['hieu']} {b['trigram']} → {b['tang']} ({b['vai_tro']})")
    lines.append("\n**Vận hành tạng phủ:**")
    for b in result.ha_lac_van_hanh:
        lines.append(f"- {b['hieu']} {b['trigram']} → {b['tang']} ({b['vai_tro']})")
    if result.ha_lac_cross:
        lines.append(f"\n{result.ha_lac_cross}")

    lines.extend([
        f"\n## 4. Đông Y\n",
        f"- **Tạng chính:** {result.dong_y_primary_tang}",
        f"- **Cường độ thân thể:** {result.dong_y_constitution_strength.upper()}",
        f"\n## 5. Vận Khí Năm {result.van_khi_year}\n",
        f"- **Trung Vận:** {result.trung_van}",
        f"- **Khí trời:** {result.luc_khi}",
        f"\n**Lục Dâm cảnh báo:**",
    ])
    for cb in result.luc_dam_canh_bao:
        info = cb["info"]
        lines.append(f"- **{info['ten']}** ({cb['loai']}): tạng {info['tang_dich_chu_yeu']}")

    lines.append("\n## 6. Bệnh Tật theo TTT chương 25\n")
    lines.append("**Bệnh HUNG (kỳ thần nhập ngũ tạng):**")
    for b in result.benh_hung_canh_bao:
        info = b["info"]
        lines.append(f"- {info['ý_nghĩa']} → **{info['tạng_bệnh']}**")
    lines.append("\n**Ngũ vị cần GIẢM:**")
    for v in result.ngu_vi_can_giam:
        info = v["info"]
        lines.append(f"- Vị **{v['vị_cần_giảm'].upper()}** → {info['ăn_quá_đà']}")

    lines.append("\n## 7. Tượng Số Ưu Tiên\n")
    for ts in result.tuong_so_uu_tien:
        lines.append(f"- `{ts}`")

    lines.extend([
        "\n## 8. Synthesis + Chiến lược\n",
        f"### Tổng paradigm\n{result.overall_paradigm}\n",
        f"### Chiến lược 3 tháng tới\n{result.chien_luoc_3_thang}\n",
        f"### Chiến lược cả năm {result.van_khi_year}\n{result.chien_luoc_1_nam}\n",
        f"### Tâm Đức\n{result.tam_duc_loi_khuyen}\n",
        "\n---\n🪷 _Iron Rule #4+6: 4 paradigm đồng-dạng — KHÔNG predict, KHÔNG thay y học._",
    ])
    return "\n".join(lines)
