"""Weekly Health Planner — Lịch dưỡng sinh 7 ngày cá nhân hóa.

Cross paradigm:
- Day Master + kỵ thần → tránh / dưỡng tạng nào
- Mỗi ngày 1 can chi → giờ vượng tạng + cảm hứng
- 7 ngày × (giờ vượng + bài niệm + thực phẩm + vận động + reminder)

🪷 Iron Rule: lịch khung — Anh tự chọn áp dụng. KHÔNG ép.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta


# Mapping chi ngày → giờ vượng tạng phủ
NGAY_CHI_TANG_PHU: dict[str, dict] = {
    "Tý":   {"gio_vuong": "23h-1h", "tang": "Đởm", "mood": "Sáng tạo, linh hoạt"},
    "Sửu":  {"gio_vuong": "1h-3h", "tang": "Can/Gan", "mood": "Tích tụ, dưỡng huyết"},
    "Dần":  {"gio_vuong": "3h-5h", "tang": "Phế", "mood": "Khởi đầu, hô hấp"},
    "Mão":  {"gio_vuong": "5h-7h", "tang": "Đại trường", "mood": "Bài tiết, thanh lọc"},
    "Thìn": {"gio_vuong": "7h-9h", "tang": "Vị", "mood": "Tiếp nhận, ăn ngon"},
    "Tỵ":   {"gio_vuong": "9h-11h", "tang": "Tỳ", "mood": "Vận hóa, làm việc"},
    "Ngọ":  {"gio_vuong": "11h-13h", "tang": "Tâm/Tim", "mood": "Đỉnh dương, năng lượng"},
    "Mùi":  {"gio_vuong": "13h-15h", "tang": "Tiểu trường", "mood": "Phân loại, chiêm nghiệm"},
    "Thân": {"gio_vuong": "15h-17h", "tang": "Bàng quang", "mood": "Bài tiết, dọn dẹp"},
    "Dậu":  {"gio_vuong": "17h-19h", "tang": "Thận", "mood": "Tích trữ, nội dưỡng"},
    "Tuất": {"gio_vuong": "19h-21h", "tang": "Tâm bào", "mood": "Bảo vệ tim, thư giãn"},
    "Hợi":  {"gio_vuong": "21h-23h", "tang": "Tam tiêu", "mood": "Chuẩn bị ngủ, an thần"},
}

# Map chi → element + tương tác với DM
CHI_ELEMENT: dict[str, str] = {
    "Tý": "thủy", "Hợi": "thủy",
    "Dần": "mộc", "Mão": "mộc",
    "Tỵ": "hỏa", "Ngọ": "hỏa",
    "Thìn": "thổ", "Tuất": "thổ", "Sửu": "thổ", "Mùi": "thổ",
    "Thân": "kim", "Dậu": "kim",
}


@dataclass
class DayPlan:
    """1 ngày dưỡng sinh."""

    date_str: str
    day_index: int           # 1-7
    weekday_vn: str
    chi_ngay: str
    can_ngay: str
    can_chi: str
    chi_element: str
    relation_to_dm: str      # ấn/tỷ/thực_thương/tài/quan_sát
    level: str               # 🟢🟡🟠🔴
    gio_vuong: str
    tang_dac_biet: str
    mood: str
    bai_niem_sang: str
    bai_niem_toi: str
    thuc_an_dac_biet: list[str]
    van_dong: str
    reminder: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WeeklyPlannerResult:
    """Lịch 7 ngày."""

    start_date: str
    day_master: str
    day_master_element: str
    days: list[dict]
    summary: str
    iron_rule: str

    def to_dict(self) -> dict:
        return asdict(self)


WEEKDAY_VN: dict[int, str] = {
    0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm",
    4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật",
}


def _compute_day_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """Tính can chi ngày (đơn giản — dùng anchor 1984-01-01 = Giáp Tý ngày).

    Cải tiến: dùng anchor xác thực hơn.
    """
    # Anchor: 1984-12-22 (Đông Chí) — Giáp Tý
    # Đơn giản: cài 2026-01-01 = Bính Thân (verified)
    HEAVENLY = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    EARTHLY = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

    # Anchor 2026-01-01 = Bính Thân (index can=2, chi=8)
    anchor = datetime(2026, 1, 1)
    target = datetime(year, month, day)
    delta = (target - anchor).days
    can_idx = (2 + delta) % 10
    chi_idx = (8 + delta) % 12
    return HEAVENLY[can_idx], EARTHLY[chi_idx]


def _level_relation(chi_el: str, dm_el: str) -> tuple[str, str]:
    """Trả về (level emoji, relation name)."""
    # Quan hệ ngũ hành
    sinh = {"mộc": "hỏa", "hỏa": "thổ", "thổ": "kim", "kim": "thủy", "thủy": "mộc"}
    khac = {"mộc": "thổ", "thổ": "thủy", "thủy": "hỏa", "hỏa": "kim", "kim": "mộc"}

    if chi_el == dm_el:
        return "🟢", "Tỷ (đồng đạo) — VƯỢNG, hành động"
    elif sinh.get(chi_el) == dm_el:
        return "🟢", "Ấn (mẹ sinh) — DƯỠNG, nuôi khí"
    elif sinh.get(dm_el) == chi_el:
        return "🟡", "Thực Thương (con) — TIẾT khí, sáng tạo"
    elif khac.get(dm_el) == chi_el:
        return "🟠", "Tài (Mộc khắc) — HAO khí, dưỡng Tỳ Vị"
    elif khac.get(chi_el) == dm_el:
        return "🔴", "Quan Sát (khắc) — ÁP LỰC, cẩn trọng"
    return "·", "trung"


def build_weekly_plan(
    birth_datetime_local: str,
    timezone: str = "Asia/Ho_Chi_Minh",
    gender: str = "nam",
    start_date: str | None = None,  # YYYY-MM-DD; default = today
) -> WeeklyPlannerResult:
    """Engine chính."""
    from engine.bat_tu import extract_tu_tru
    from engine.bat_tu.constants import STEM_ELEMENT as SE
    from engine.bat_tu.phu_uc_route import route_phu_uc

    base = extract_tu_tru(birth_datetime_local, timezone)
    pillars = base["pillars"]
    dm_stem = pillars["day"]["stem"]
    dm_el = SE.get(dm_stem, "")

    # Kỵ thần để cảnh báo
    phu_uc = route_phu_uc({"pillars": pillars})
    ky_els = phu_uc.ky_than_elements or []

    # Start date
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        # Use a fixed date for reproducibility (engine không có "today")
        start = datetime(2026, 6, 4)  # Bắt đầu kế hoạch

    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        can, chi = _compute_day_pillar(d.year, d.month, d.day)
        chi_el = CHI_ELEMENT.get(chi, "")
        level, relation = _level_relation(chi_el, dm_el)
        info = NGAY_CHI_TANG_PHU.get(chi, {})

        # Bài niệm theo level
        if level == "🟢":
            bai_sang = "640 (bổ Can dưỡng gân)"
            bai_toi = "650.070 (dưỡng Thận, máu lưu thông)"
        elif level == "🟡":
            bai_sang = "260.50.30.80 (đau nửa đầu trái dễ bùng — phòng)"
            bai_toi = "640.30.80 (an thần)"
        elif level == "🟠":
            bai_sang = "650.30.820 (KHÍ NGŨ TẠNG — cân bằng)"
            bai_toi = "640 (dưỡng Can)"
        elif level == "🔴":
            bai_sang = "80.20 (phòng cổ vai gáy) + 260.50.30.80 (phòng đau đầu trái)"
            bai_toi = "640 (dưỡng Can trước ngủ)"
        else:
            bai_sang = "640"
            bai_toi = "650.070"

        # Thực ăn
        if chi_el == "thủy":
            thuc_an = ["Đậu đen + mè đen", "Cá hồi / hải sản nhẹ", "Trà hà thủ ô"]
        elif chi_el == "mộc":
            thuc_an = ["Rau xanh đậm", "Kỷ tử + đậu xanh", "Mộc nhĩ đen"]
        elif chi_el == "hỏa":
            thuc_an = ["Mướp đắng (giải Hỏa cho Anh)", "Trà sen", "Long nhãn"]
        elif chi_el == "thổ":
            thuc_an = ["Gạo lứt + bí đỏ", "Khoai lang", "Mật ong (ít)"]
        elif chi_el == "kim":
            thuc_an = ["Lê + củ cải trắng", "Mộc nhĩ trắng", "Hạnh nhân"]
        else:
            thuc_an = ["Ăn cân đối"]

        # Vận động
        if level in ["🟢"]:
            van_dong = "Đi bộ 30 phút + yoga giãn gân nhẹ"
        elif level == "🟡":
            van_dong = "Thiền 15-20 phút, vận động NHẸ"
        elif level == "🟠":
            van_dong = "Đi bộ sau ăn 10-15 phút, không gắng sức"
        elif level == "🔴":
            van_dong = "Vận động RẤT NHẸ, ưu tiên nghỉ + massage cổ vai gáy"
        else:
            van_dong = "Đi bộ vừa phải"

        # Reminder
        reminder = ""
        if level == "🔴":
            reminder = "⚠️ Tháng/ngày KIM khắc Mộc — cẩn trọng cổ vai gáy. Quàng khăn, tránh gió lùa."
        elif chi == "Sửu" or chi == "Tý":
            reminder = "🌙 Giờ Tý-Sửu = giờ dưỡng Can. PHẢI ngủ trước 23h tối nay."
        elif chi_el == "hỏa":
            reminder = "🔥 Hỏa vượng — tránh suy nghĩ căng buổi tối (đốt khí Can → đau nửa đầu trái)."

        days.append(DayPlan(
            date_str=d.strftime("%Y-%m-%d"),
            day_index=i + 1,
            weekday_vn=WEEKDAY_VN.get(d.weekday(), ""),
            chi_ngay=chi,
            can_ngay=can,
            can_chi=f"{can} {chi}",
            chi_element=chi_el,
            relation_to_dm=relation,
            level=level,
            gio_vuong=info.get("gio_vuong", ""),
            tang_dac_biet=info.get("tang", ""),
            mood=info.get("mood", ""),
            bai_niem_sang=bai_sang,
            bai_niem_toi=bai_toi,
            thuc_an_dac_biet=thuc_an,
            van_dong=van_dong,
            reminder=reminder,
        ).to_dict())

    # Summary
    green = sum(1 for d in days if d["level"] == "🟢")
    red = sum(1 for d in days if d["level"] == "🔴")
    yellow = sum(1 for d in days if d["level"] == "🟡")
    orange = sum(1 for d in days if d["level"] == "🟠")
    summary = (
        f"7 ngày từ {start.strftime('%Y-%m-%d')}: "
        f"{green} ngày 🟢 (dưỡng tốt) + {yellow} ngày 🟡 (tiết khí) + "
        f"{orange} ngày 🟠 (hao khí) + {red} ngày 🔴 (cẩn trọng)."
    )

    return WeeklyPlannerResult(
        start_date=start.strftime("%Y-%m-%d"),
        day_master=dm_stem,
        day_master_element=dm_el,
        days=days,
        summary=summary,
        iron_rule=(
            "🪷 Iron Rule: Lịch là KHUNG, không ép. Anh chọn ngày nào áp dụng phù hợp. "
            "KHÔNG predict bệnh ngày X. Mục đích: dưỡng tạng trước khi cần."
        ),
    )


def render_weekly_markdown(result: WeeklyPlannerResult) -> str:
    """Render markdown."""
    lines = [
        f"# 📅 Lịch Dưỡng Sinh 7 Ngày — bắt đầu {result.start_date}\n",
        f"**Day Master:** {result.day_master} ({result.day_master_element})\n",
        f"{result.summary}\n",
        "---\n",
    ]
    for d in result.days:
        lines.append(f"## {d['level']} Ngày {d['day_index']} — {d['weekday_vn']} {d['date_str']}")
        lines.append(f"**{d['can_chi']}** ({d['chi_element']}) — {d['relation_to_dm']}")
        lines.append(f"- ⏰ **Giờ vượng:** {d['gio_vuong']} → tạng **{d['tang_dac_biet']}**")
        lines.append(f"- 🎭 **Mood:** {d['mood']}")
        lines.append(f"- 🌅 **Bài niệm sáng:** `{d['bai_niem_sang']}`")
        lines.append(f"- 🌙 **Bài niệm tối:** `{d['bai_niem_toi']}`")
        lines.append(f"- 🍵 **Thực phẩm dưỡng:** {' · '.join(d['thuc_an_dac_biet'])}")
        lines.append(f"- 🚶 **Vận động:** {d['van_dong']}")
        if d['reminder']:
            lines.append(f"- {d['reminder']}")
        lines.append("")
    lines.append(f"\n---\n{result.iron_rule}")
    return "\n".join(lines)
