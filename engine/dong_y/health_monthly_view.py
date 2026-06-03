"""Health Monthly View — Lịch sức khỏe cá nhân theo Lưu Nguyệt.

Anh chỉ 2026-06-03: "kết hợp với chu kỳ tháng bên Tử Vi và Bát Tự.
Cho anh tầm nhìn cả tháng."

Engine kết hợp 3 paradigm:
1. **Bát Tự Lưu Nguyệt** — 12 can chi tháng + ngũ hành vs Day Master
2. **Tử Vi Lưu Nguyệt** — sao chiếu cung Mệnh / Tật Ách / Thân
3. **Chân dung sức khỏe** — 3 cụm triệu chứng + chấn thương cá nhân

→ Output: lịch 12 tháng âm (theo tiết khí), mỗi tháng có:
  - Cường độ khí (🟢🟡🟠🔴)
  - Tạng cần dưỡng cho tháng đó
  - Tượng số ưu tiên niệm
  - Việc nên làm + tránh

🪷 Iron Rule #4+6: lịch là CẤU TRÚC KHÍ tháng, KHÔNG predict ngày cụ thể
"Anh sẽ bệnh ngày X". Cấu trúc giúp Anh CHỦ ĐỘNG dưỡng tạng yếu trước
khi tháng vào áp lực.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict


# ─── Element relations cho DM Mộc (founder) ─────────────────────────────────

# Cho Day Master Mộc (Giáp):
# - Thủy SINH Mộc → tháng Hợi/Tý = Ấn (dưỡng) 🟢
# - Mộc CÙNG Mộc → tháng Dần/Mão = Tỷ (vượng) 🟢
# - Mộc SINH Hỏa → tháng Tỵ/Ngọ = Thực Thương (tiết) 🟡
# - Mộc KHẮC Thổ → tháng Thìn/Tuất/Sửu/Mùi = Tài (hao) 🟠
# - Kim KHẮC Mộc → tháng Thân/Dậu = Quan Sát (áp) 🔴

DM_MONTH_PARADIGM: dict[str, dict] = {
    "mộc": {
        "thuy_lvl": "🟢", "thuy_meaning": "Ấn (mẹ sinh) — DƯỠNG tốt",
        "moc_lvl": "🟢", "moc_meaning": "Tỷ (đồng đạo) — VƯỢNG, hành động",
        "hoa_lvl": "🟡", "hoa_meaning": "Thực Thương (con) — TIẾT khí, tránh đốt sức",
        "tho_lvl": "🟠", "tho_meaning": "Tài (Mộc khắc) — HAO khí, dưỡng Tỳ Vị",
        "kim_lvl": "🔴", "kim_meaning": "Quan Sát (khắc) — ÁP LỰC, cẩn trọng cổ vai gáy + đau đầu",
    },
    "hỏa": {
        "moc_lvl": "🟢", "moc_meaning": "Ấn (mẹ sinh) — DƯỠNG tốt",
        "hoa_lvl": "🟢", "hoa_meaning": "Tỷ (đồng đạo) — VƯỢNG",
        "tho_lvl": "🟡", "tho_meaning": "Thực Thương — TIẾT khí",
        "kim_lvl": "🟠", "kim_meaning": "Tài — HAO",
        "thuy_lvl": "🔴", "thuy_meaning": "Quan Sát — ÁP LỰC, cẩn trọng",
    },
    "thổ": {
        "hoa_lvl": "🟢", "hoa_meaning": "Ấn — DƯỠNG",
        "tho_lvl": "🟢", "tho_meaning": "Tỷ — VƯỢNG",
        "kim_lvl": "🟡", "kim_meaning": "Thực Thương — TIẾT",
        "thuy_lvl": "🟠", "thuy_meaning": "Tài — HAO",
        "moc_lvl": "🔴", "moc_meaning": "Quan Sát — ÁP LỰC",
    },
    "kim": {
        "tho_lvl": "🟢", "tho_meaning": "Ấn — DƯỠNG",
        "kim_lvl": "🟢", "kim_meaning": "Tỷ — VƯỢNG",
        "thuy_lvl": "🟡", "thuy_meaning": "Thực Thương — TIẾT",
        "moc_lvl": "🟠", "moc_meaning": "Tài — HAO",
        "hoa_lvl": "🔴", "hoa_meaning": "Quan Sát — ÁP LỰC",
    },
    "thủy": {
        "kim_lvl": "🟢", "kim_meaning": "Ấn — DƯỠNG",
        "thuy_lvl": "🟢", "thuy_meaning": "Tỷ — VƯỢNG",
        "moc_lvl": "🟡", "moc_meaning": "Thực Thương — TIẾT",
        "hoa_lvl": "🟠", "hoa_meaning": "Tài — HAO",
        "tho_lvl": "🔴", "tho_meaning": "Quan Sát — ÁP LỰC",
    },
}

# Mapping element → tạng cần dưỡng + tượng số gợi ý
LEVEL_HEALTH_GUIDE: dict[str, dict] = {
    "🟢_thuy": {
        "tang_dac_biet": "Thận + Bàng quang",
        "tuong_so_goi_y": "650.070 (dưỡng Thận thông kinh)",
        "hanh_dong": [
            "Đậu đen + mè đen + óc chó tăng cường",
            "Ngủ đúng giờ Tý (23h-1h) dưỡng Đởm-Can",
            "Đi bộ chậm, hít thở sâu",
        ],
        "tranh": ["Đồ mặn quá", "Ngồi lâu không vận động"],
    },
    "🟢_moc": {
        "tang_dac_biet": "Can + Đởm + Gân",
        "tuong_so_goi_y": "640 (bổ Can dưỡng gân)",
        "hanh_dong": [
            "Đậu xanh + rau lá xanh đậm + kỷ tử",
            "Hành động: ra quyết định, mở rộng đồng đạo",
            "Đi bộ chậm trên đất phẳng (TRÁNH chạy nhảy mạnh — gân vẫn yếu)",
        ],
        "tranh": ["Rượu mạnh", "Cà phê đậm chiều/tối", "Stress đốt khí"],
    },
    "🟡_hoa": {
        "tang_dac_biet": "Tâm + Tiểu trường (chú ý tiết khí)",
        "tuong_so_goi_y": "640.30.80 (an thần + tránh đốt Mộc)",
        "hanh_dong": [
            "Đậu đỏ + long nhãn + táo tàu",
            "Thiền 15-20 phút mỗi tối",
            "TRÁNH suy nghĩ căng (đốt khí huyết Can — đau nửa đầu trái nặng lên)",
        ],
        "tranh": ["Show off + tranh luận căng", "Thức khuya sáng tạo", "Cà phê + đồ kích thích"],
    },
    "🟠_tho": {
        "tang_dac_biet": "Tỳ + Vị (chú ý ăn uống)",
        "tuong_so_goi_y": "650.30.820 (KHÍ NGŨ TẠNG, cân bằng cả 5 tạng)",
        "hanh_dong": [
            "Gạo lứt + bí đỏ + khoai lang + mật ong",
            "Ăn đúng giờ — đặc biệt sáng (giờ Tỳ-Vị 7h-11h)",
            "Massage bụng theo chiều kim đồng hồ sau ăn",
            "Tránh ép kinh doanh / mở rộng quy mô (hao Tỳ)",
        ],
        "tranh": ["Ăn lạnh sống", "Bỏ bữa", "Đu trend tiền nhanh"],
    },
    "🔴_kim": {
        "tang_dac_biet": "Phế + Đại trường + KHÍ HÔ HẤP (Mộc Anh sẽ bị Kim khắc)",
        "tuong_so_goi_y": "80.20 (cổ vai gáy) + 260.50.30.80 (nửa đầu trái)",
        "hanh_dong": [
            "🚨 THẬN TRỌNG: tháng này dễ tái phát đau cổ vai gáy + nửa đầu trái",
            "TRÁNH gió lùa cổ vai (khăn mỏng khi đi xe máy + điều hòa)",
            "TRÁNH nhận thêm trách nhiệm vượt sức (Quan Sát = áp lực)",
            "Ngủ sớm hơn bình thường — dưỡng Can-Thận trước",
            "Lê + củ cải trắng + hạnh nhân + mộc nhĩ trắng",
            "Thở bụng sâu sáng sớm",
        ],
        "tranh": ["Đối đầu trực diện người quyền lực", "Khoe trí tranh luận", "Thay đổi lớn"],
    },
}


# 12 tháng Đông y — giờ vượng kinh + tạng tương ứng
THANG_TANG_PHU: dict[str, str] = {
    "Dần": "Phế (3h-5h)",        # tháng 1 âm
    "Mão": "Đại trường (5h-7h)",  # tháng 2
    "Thìn": "Vị (7h-9h)",         # tháng 3
    "Tỵ": "Tỳ (9h-11h)",          # tháng 4
    "Ngọ": "Tâm (11h-13h)",       # tháng 5
    "Mùi": "Tiểu trường (13h-15h)", # tháng 6
    "Thân": "Bàng quang (15h-17h)", # tháng 7
    "Dậu": "Thận (17h-19h)",      # tháng 8
    "Tuất": "Tâm bào (19h-21h)",  # tháng 9
    "Hợi": "Tam tiêu (21h-23h)",  # tháng 10
    "Tý": "Đởm (23h-1h)",         # tháng 11
    "Sửu": "Can (1h-3h)",         # tháng 12
}


@dataclass
class MonthHealthForecast:
    """1 tháng — health forecast."""

    month_index: int             # 1-12 (theo tiết khí, 1=Dần)
    month_solar_approx: int      # tháng dương lịch xấp xỉ
    tiet_khi: str
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    level: str                   # 🟢 / 🟡 / 🟠 / 🔴
    level_meaning: str           # Ấn / Tỷ / Thực Thương / Tài / Quan Sát
    tang_dac_biet: str
    gio_vuong: str               # giờ vượng kinh tháng đó
    tuong_so_goi_y: str
    hanh_dong: list[str]
    tranh: list[str]
    cross_chan_thuong: str       # Liên kết với chấn thương cố định Anh

    def to_dict(self) -> dict:
        return asdict(self)


def _level_for_element(dm_element: str, target_element: str) -> tuple[str, str]:
    """Trả về (level, meaning) cho element vs DM."""
    # ASCII keys (mộc → moc, hỏa → hoa, thủy → thuy, etc.)
    ASCII_MAP = {"mộc": "moc", "hỏa": "hoa", "thổ": "tho", "kim": "kim", "thủy": "thuy"}
    target_key = ASCII_MAP.get(target_element, target_element)
    paradigm = DM_MONTH_PARADIGM.get(dm_element, {})
    key_lvl = f"{target_key}_lvl"
    key_meaning = f"{target_key}_meaning"
    return paradigm.get(key_lvl, "·"), paradigm.get(key_meaning, "trung")


def _guide_for_level(level: str, element: str) -> dict:
    """Lookup health guide."""
    # Try {level}_{element} first
    map_key = {
        ("🟢", "thủy"): "🟢_thuy",
        ("🟢", "mộc"): "🟢_moc",
        ("🟢", "kim"): "🟢_thuy",  # fallback
        ("🟡", "hỏa"): "🟡_hoa",
        ("🟠", "thổ"): "🟠_tho",
        ("🔴", "kim"): "🔴_kim",
    }.get((level, element))
    if map_key:
        return LEVEL_HEALTH_GUIDE[map_key]
    # Default for other combos
    return {
        "tang_dac_biet": "Tổng quát",
        "tuong_so_goi_y": "650.30.820 (KHÍ NGŨ TẠNG)",
        "hanh_dong": ["Ăn cân đối ngũ vị", "Vận động đều"],
        "tranh": ["Thái quá ngũ tạng nào"],
    }


def _cross_chan_thuong_for_month(level: str, element: str, dm_element: str) -> str:
    """Cross với chân dung 3 triệu chứng cố định của Anh."""
    if dm_element == "mộc":
        if element == "kim" and level == "🔴":
            return (
                "⚠️ Tháng KIM khắc MỘC — cảnh báo CAO cho 3 triệu chứng của Anh: "
                "đau cổ vai gáy + nửa đầu trái có thể tái phát mạnh. "
                "Niệm 80.20 + 260.50.30.80 mỗi sáng để phòng."
            )
        elif element == "thổ" and level == "🟠":
            return (
                "Tháng THỔ (Tài) — Mộc Anh hao khí khắc Thổ. "
                "Tiêu hóa có thể kém + máu lưu thông chậm. Niệm 650.070 buổi tối."
            )
        elif element == "thủy" and level == "🟢":
            return (
                "✨ Tháng THỦY (Ấn) — mẹ nuôi Mộc cho Anh. ĐÂY LÀ THÁNG TỐT NHẤT "
                "để dưỡng Can-Thận. Niệm 640 hàng ngày + đậu đen + ngủ sớm."
            )
        elif element == "mộc" and level == "🟢":
            return (
                "✨ Tháng MỘC (Tỷ Kiếp) — đồng đạo. Khí Mộc vượng dễ chịu, "
                "nhưng đừng gắng sức. Hành động vừa phải."
            )
        elif element == "hỏa" and level == "🟡":
            return (
                "Tháng HỎA — Mộc tiết khí ra Hỏa. Đau nửa đầu trái dễ bùng (suy nghĩ "
                "căng đốt Can). Tránh stress, niệm 640.30.80 trước khi ngủ."
            )
    return ""


def build_monthly_health_view(tu_tru: dict, current_year: int = 2026) -> dict:
    """Engine chính — sinh lịch 12 tháng sức khỏe cá nhân.

    Args:
        tu_tru: pillars
        current_year: năm cần xem (default 2026)

    Returns: dict với 12 months + summary
    """
    from engine.bat_tu.luu_nien import _compute_luu_nguyet
    from engine.bat_tu.constants import STEM_ELEMENT as SE

    year_pillar_stem = tu_tru.get("luu_nien_year_stem")
    if not year_pillar_stem:
        # Tính year stem từ current_year
        from engine.bat_tu.luu_nien import compute_luu_nien_pillar_by_year
        ly = compute_luu_nien_pillar_by_year(current_year)
        year_pillar_stem = ly["stem"]

    pillars = tu_tru["pillars"]
    dm_stem = pillars["day"]["stem"]
    dm_element = SE.get(dm_stem, "")

    # Sinh 12 tháng Lưu Nguyệt
    months_raw = _compute_luu_nguyet(year_pillar_stem, current_year)

    # Đánh giá từng tháng
    forecasts = []
    for m in months_raw:
        # Lấy hành CHÍNH của tháng (chi tháng → element)
        primary_element = m["branch_element"].lower()
        level, meaning = _level_for_element(dm_element, primary_element)
        guide = _guide_for_level(level, primary_element)
        cross = _cross_chan_thuong_for_month(level, primary_element, dm_element)

        forecasts.append(MonthHealthForecast(
            month_index=m["month_index"],
            month_solar_approx=m.get("month_solar", m["month_index"] + 1),
            tiet_khi=m["tiet_khi"],
            stem=m["stem"],
            branch=m["branch"],
            stem_element=m["stem_element"],
            branch_element=m["branch_element"],
            level=level,
            level_meaning=meaning,
            tang_dac_biet=guide["tang_dac_biet"],
            gio_vuong=THANG_TANG_PHU.get(m["branch"], ""),
            tuong_so_goi_y=guide["tuong_so_goi_y"],
            hanh_dong=guide["hanh_dong"],
            tranh=guide["tranh"],
            cross_chan_thuong=cross,
        ))

    # Summary: phân loại tháng tốt / tránh
    green = [f for f in forecasts if f.level == "🟢"]
    yellow = [f for f in forecasts if f.level == "🟡"]
    orange = [f for f in forecasts if f.level == "🟠"]
    red = [f for f in forecasts if f.level == "🔴"]

    summary = {
        "tong_quat": (
            f"Năm {current_year} — Day Master {dm_stem} ({dm_element}). "
            f"Có {len(green)} tháng 🟢, {len(yellow)} tháng 🟡, "
            f"{len(orange)} tháng 🟠, {len(red)} tháng 🔴."
        ),
        "thang_tot_nhat": [f"Tháng {f.month_index} ({f.tiet_khi}) — {f.level_meaning}" for f in green],
        "thang_can_trong": [f"Tháng {f.month_index} ({f.tiet_khi}) — {f.level_meaning}" for f in red],
        "loi_khuyen_chien_luoc": _build_strategy(dm_element, green, red),
    }

    return {
        "current_year": current_year,
        "day_master": dm_stem,
        "day_master_element": dm_element,
        "months": [f.to_dict() for f in forecasts],
        "summary": summary,
        "paradigm_note": (
            "🪷 Lịch là CẤU TRÚC KHÍ tháng — KHÔNG predict ngày cụ thể bệnh. "
            "Mục đích: Anh CHỦ ĐỘNG dưỡng tạng yếu TRƯỚC khi tháng vào áp lực. "
            "Engine kết hợp Bát Tự Lưu Nguyệt + paradigm Đông y."
        ),
        "sources": [
            "Bát Tự Lưu Nguyệt (Thiệu Vĩ Hoa + Trần Viên — Dự đoán Tứ Trụ)",
            "Đông y Tạng phủ ↔ Giờ vượng kinh (Hoàng Đế Nội Kinh)",
            "Liệu pháp Tượng Số (Chữa bệnh theo Chu Dịch — Lý Ngọc Sơn + Lý Kiện Dân)",
        ],
    }


def _build_strategy(dm_element: str, green_months: list, red_months: list) -> list[str]:
    """Lời khuyên chiến lược cả năm."""
    strategy = []
    if dm_element == "mộc":
        strategy.append(
            f"Ưu tiên hành động trong {len(green_months)} tháng 🟢 (Thủy + Mộc): "
            "ra quyết định, mở rộng đồng đạo, học sâu."
        )
        if red_months:
            months_str = ", ".join(str(f.month_index) for f in red_months)
            strategy.append(
                f"Cẩn trọng tháng {months_str} (Kim khắc Mộc): "
                "GIỮ THẾ THỦ. Tránh nhận trách nhiệm lớn. Dưỡng cổ vai gáy + đầu trái."
            )
        strategy.append(
            "Tháng 🟡 (Hỏa) tiết khí: thiền nhiều, tránh suy nghĩ căng — "
            "đau nửa đầu trái dễ tái phát."
        )
        strategy.append(
            "Tháng 🟠 (Thổ) Tài: tránh đu trend tiền nhanh, dưỡng Tỳ Vị."
        )
    return strategy


def render_monthly_view_markdown(view: dict) -> str:
    """Render markdown lịch 12 tháng."""
    lines = [
        f"# 📅 Lịch Sức Khỏe 12 Tháng — Năm {view['current_year']}\n",
        f"**Day Master:** {view['day_master']} ({view['day_master_element']})\n",
        f"## 🎯 Tổng quát\n{view['summary']['tong_quat']}\n",
        "## 📌 Chiến lược cả năm\n",
    ]
    for s in view['summary']['loi_khuyen_chien_luoc']:
        lines.append(f"- {s}")

    lines.append("\n## 🗓 12 Tháng (theo Tiết khí)\n")
    for m in view['months']:
        lines.append(f"### {m['level']} Tháng {m['month_index']} — {m['tiet_khi']} "
                     f"({m['stem']} {m['branch']}, hành {m['branch_element']})")
        lines.append(f"- **{m['level_meaning']}**")
        lines.append(f"- Tạng dưỡng: **{m['tang_dac_biet']}** ({m['gio_vuong']})")
        lines.append(f"- Tượng số gợi ý: `{m['tuong_so_goi_y']}`")
        if m['cross_chan_thuong']:
            lines.append(f"- 🩺 _{m['cross_chan_thuong']}_")
        lines.append("- **Nên:**")
        for h in m['hanh_dong']:
            lines.append(f"  - {h}")
        lines.append("- **Tránh:**")
        for t in m['tranh']:
            lines.append(f"  - {t}")
        lines.append("")

    lines.append(f"\n---\n\n{view['paradigm_note']}")
    return "\n".join(lines)
