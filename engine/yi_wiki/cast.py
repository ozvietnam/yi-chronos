"""Mai Hoa Dịch Số — Niên-Nguyệt-Nhật-Thời Khởi Lệ.

Implementation từ trang 43-45 Mai Hoa. Trans-historical tool — anh
có thể gọi để gieo quẻ thật và lưu vào Prediction table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Bảng số quẻ Tiên Thiên (Phục Hy)
QUE_NUMBER_TO_NAME = {
    1: ("Càn", "乾", "☰"),
    2: ("Đoài", "兌", "☱"),
    3: ("Ly", "離", "☲"),
    4: ("Chấn", "震", "☳"),
    5: ("Tốn", "巽", "☴"),
    6: ("Khảm", "坎", "☵"),
    7: ("Cấn", "艮", "☶"),
    8: ("Khôn", "坤", "☷"),
}

QUE_TO_LINES = {
    "Càn": (1, 1, 1),    # ☰
    "Đoài": (1, 1, 0),   # ☱ (hào trên âm)
    "Ly": (1, 0, 1),     # ☲ (hào giữa âm)
    "Chấn": (0, 0, 1),   # ☳ (hào dưới dương)
    "Tốn": (1, 1, 0),    # ☴ — wait, correct: Tốn = (0, 1, 1) hào dưới âm
    "Khảm": (0, 1, 0),   # ☵
    "Cấn": (1, 0, 0),    # ☶
    "Khôn": (0, 0, 0),   # ☷
}
# Lines convention: (bottom, middle, top)
# Càn = 3 dương = (1,1,1)
# Đoài = thượng khuyết (trên âm) = (1,1,0)
# Ly = trung hư (giữa âm) = (1,0,1)
# Chấn = ngưỡng vu (1 dương dưới) = (1,0,0) — wait
# Theo bài thơ Mnemonic:
# Càn tam liên ☰ → 1,1,1
# Đoài thượng khuyết ☱ → top=0, mid=1, bot=1 → (1,1,0)
# Ly trung hư ☲ → top=1, mid=0, bot=1 → (1,0,1)
# Chấn ngưỡng vu ☳ (1 dương dưới) → top=0, mid=0, bot=1 → (1,0,0)
# Tốn hạ đoạn ☴ (1 âm dưới) → top=1, mid=1, bot=0 → (0,1,1)
# Khảm trung mãn ☵ (1 dương giữa) → top=0, mid=1, bot=0 → (0,1,0)
# Cấn phúc uyển ☶ (1 dương trên) → top=1, mid=0, bot=0 → (0,0,1)
# Khôn lục đoạn ☷ → (0,0,0)
QUE_TO_LINES = {
    "Càn": (1, 1, 1),
    "Đoài": (1, 1, 0),
    "Ly": (1, 0, 1),
    "Chấn": (1, 0, 0),
    "Tốn": (0, 1, 1),
    "Khảm": (0, 1, 0),
    "Cấn": (0, 0, 1),
    "Khôn": (0, 0, 0),
}
# (bottom, middle, top) — convention từ dưới lên

LINES_TO_QUE = {v: k for k, v in QUE_TO_LINES.items()}

# Chi → số
CHI_NUMBER = {
    "Tý": 1, "Sửu": 2, "Dần": 3, "Mão": 4,
    "Thìn": 5, "Tỵ": 6, "Ngọ": 7, "Mùi": 8,
    "Thân": 9, "Dậu": 10, "Tuất": 11, "Hợi": 12,
}


@dataclass
class Hexagram:
    """1 quẻ 6 vạch (trùng quái)."""
    upper_que: str   # quẻ trên (ngoại quái)
    lower_que: str   # quẻ dưới (nội quái)
    upper_num: int
    lower_num: int

    @property
    def lines(self) -> tuple[int, int, int, int, int, int]:
        """6 hào từ dưới lên: lower(bot,mid,top) + upper(bot,mid,top)."""
        return QUE_TO_LINES[self.lower_que] + QUE_TO_LINES[self.upper_que]

    @property
    def name(self) -> str:
        return f"{self.upper_que} / {self.lower_que}"

    def __str__(self) -> str:
        # Render từ trên xuống
        top_lines = QUE_TO_LINES[self.upper_que]
        bot_lines = QUE_TO_LINES[self.lower_que]
        out = [self.name]
        for ln in reversed(top_lines):
            out.append("━━━━━" if ln else "━━ ━━")
        out.append("- - - - -")
        for ln in reversed(bot_lines):
            out.append("━━━━━" if ln else "━━ ━━")
        return "\n".join(out)


@dataclass
class CastResult:
    """Kết quả gieo quẻ Mai Hoa — full schema."""
    timestamp: int
    inputs: dict                  # năm/tháng/ngày/giờ
    upper_num: int
    lower_num: int
    moving_line: int              # 1-6 từ dưới lên
    chinh_quai: Hexagram          # quẻ chính
    bien_quai: Hexagram           # quẻ biến
    ho_quai: Hexagram             # quẻ hỗ
    formula_trace: list[str] = field(default_factory=list)
    # ⭐ Cải tiến (Thầy Quyển 3 tr.82): khi Chính là Thuần Càn/Khôn,
    # hỗ quẻ trùng chính nó → dùng biến quẻ làm gốc tính hỗ thay
    ho_used_bien: bool = False
    ho_warning: str = ""


def _mod_or_max(n: int, divisor: int) -> int:
    """Mod, nhưng 0 → divisor (theo Mai Hoa)."""
    r = n % divisor
    return r if r != 0 else divisor


def _build_bien_quai(chinh: Hexagram, moving_line: int) -> Hexagram:
    """Đổi 1 hào ở vị trí moving_line (1-6 từ dưới)."""
    lines = list(chinh.lines)
    lines[moving_line - 1] = 1 - lines[moving_line - 1]
    bot = tuple(lines[:3])
    top = tuple(lines[3:])
    lower = LINES_TO_QUE[bot]
    upper = LINES_TO_QUE[top]
    return Hexagram(
        upper_que=upper, lower_que=lower,
        upper_num=next(k for k, v in QUE_NUMBER_TO_NAME.items() if v[0] == upper),
        lower_num=next(k for k, v in QUE_NUMBER_TO_NAME.items() if v[0] == lower),
    )


def _build_ho_quai(chinh: Hexagram) -> Hexagram:
    """Hỗ quái: hào 2-3-4 = lower mới, hào 3-4-5 = upper mới."""
    L = chinh.lines  # 0=hào 1, 5=hào 6
    bot = (L[1], L[2], L[3])   # hào 2, 3, 4
    top = (L[2], L[3], L[4])   # hào 3, 4, 5
    lower = LINES_TO_QUE[bot]
    upper = LINES_TO_QUE[top]
    return Hexagram(
        upper_que=upper, lower_que=lower,
        upper_num=next(k for k, v in QUE_NUMBER_TO_NAME.items() if v[0] == upper),
        lower_num=next(k for k, v in QUE_NUMBER_TO_NAME.items() if v[0] == lower),
    )


def cast_by_time(
    year_chi: str,
    month: int,
    day: int,
    hour_chi: str,
    *,
    timestamp: Optional[int] = None,
) -> CastResult:
    """Niên-Nguyệt-Nhật-Thời Khởi Lệ — pp bốc Mai Hoa theo thời gian.

    Args:
        year_chi: chi của năm — vd "Mão"
        month:    tháng 1-12
        day:      ngày trong tháng 1-30
        hour_chi: chi của giờ — vd "Ngọ"

    Returns: CastResult với chính + biến + hỗ quái + động hào.
    """
    y = CHI_NUMBER[year_chi]
    m = month
    d = day
    h = CHI_NUMBER[hour_chi]

    trace = [
        f"Năm {year_chi} = {y}",
        f"Tháng {m} = {m}",
        f"Ngày {d} = {d}",
        f"Giờ {hour_chi} = {h}",
    ]

    # Quẻ trên = (y+m+d) mod 8
    upper_sum = y + m + d
    upper_num = _mod_or_max(upper_sum, 8)
    upper_que = QUE_NUMBER_TO_NAME[upper_num][0]
    trace.append(f"Quẻ trên = ({y}+{m}+{d}) mod 8 = {upper_sum} mod 8 = {upper_num} → {upper_que}")

    # Quẻ dưới = (y+m+d+h) mod 8
    lower_sum = y + m + d + h
    lower_num = _mod_or_max(lower_sum, 8)
    lower_que = QUE_NUMBER_TO_NAME[lower_num][0]
    trace.append(f"Quẻ dưới = ({y}+{m}+{d}+{h}) mod 8 = {lower_sum} mod 8 = {lower_num} → {lower_que}")

    # Động hào = (y+m+d+h) mod 6
    moving = _mod_or_max(lower_sum, 6)
    trace.append(f"Động hào = ({y}+{m}+{d}+{h}) mod 6 = {lower_sum} mod 6 = {moving}")

    chinh = Hexagram(
        upper_que=upper_que, lower_que=lower_que,
        upper_num=upper_num, lower_num=lower_num,
    )
    bien = _build_bien_quai(chinh, moving)
    ho = _build_ho_quai(chinh)

    # ⭐ Thầy Quyển 3 tr.82: "Hỗ quẻ của Càn/Khôn trùng chính nó → dùng biến quẻ
    # để lấy hỗ quẻ thay thế."
    ho_used_bien = False
    ho_warning = ""
    ho_same_as_chinh = (ho.upper_que == chinh.upper_que and ho.lower_que == chinh.lower_que)
    if ho_same_as_chinh:
        # Hỗ trùng Chính → đây là Thuần Càn/Khôn (hoặc gần thuần) case
        ho_alt = _build_ho_quai(bien)
        ho_alt_same_as_chinh = (
            ho_alt.upper_que == chinh.upper_que and ho_alt.lower_que == chinh.lower_que
        )
        if not ho_alt_same_as_chinh:
            # ho_alt khác chính → dùng ho_alt thay
            ho = ho_alt
            ho_used_bien = True
            ho_warning = (
                f"⭐ Hỗ quẻ {chinh.name} trùng chính nó (Thuần {chinh.upper_que}). "
                f"Theo Thầy Q3 tr.82, lấy hỗ từ Biến quẻ thay → {ho.name}"
            )
            trace.append(ho_warning)
        else:
            # ho_alt cũng trùng chính → trường hợp "khoá Thuần Càn/Khôn"
            # Thầy Q3 tr.82 không xử lý case này. Em fall-back: dùng BIẾN làm
            # reference cho "hỗ" trong phân tích (biến = chỉ động lực duy nhất)
            ho = bien
            ho_used_bien = True
            ho_warning = (
                f"⚠️⚠️ Cả Hỗ gốc và Hỗ-từ-Biến đều trùng Chính ({chinh.name}). "
                f"Quẻ này thuộc Thuần Càn/Khôn khoá kín — KHÔNG có 'giữa kỳ' khắc ứng. "
                f"Em DÙNG BIẾN QUẺ ({bien.name}) thay HỖ để có động lực biến hoá phân tích."
            )
            trace.append(ho_warning)

    return CastResult(
        timestamp=timestamp or int(datetime.now().timestamp()),
        inputs={"year_chi": year_chi, "month": month, "day": day, "hour_chi": hour_chi},
        upper_num=upper_num, lower_num=lower_num, moving_line=moving,
        chinh_quai=chinh,
        bien_quai=bien,
        ho_quai=ho,
        formula_trace=trace,
        ho_used_bien=ho_used_bien,
        ho_warning=ho_warning,
    )


def demo():
    """Demo gieo quẻ hôm nay (2026-05-15, giờ Mùi giả định)."""
    # 2026 = năm Bính Ngọ. Năm Ngọ.
    # 2026-05-15 — tháng 5, ngày 15
    # Giờ Mùi (13:00-15:00)
    r = cast_by_time("Ngọ", 5, 15, "Mùi")
    print("═" * 50)
    print("🌌 GIEO QUẺ MAI HOA")
    print("═" * 50)
    print("\n".join(r.formula_trace))
    print()
    print(f"CHÍNH QUÁI: {r.chinh_quai.name}")
    print(r.chinh_quai)
    print(f"\nQUẺ BIẾN (hào {r.moving_line} động): {r.bien_quai.name}")
    print(r.bien_quai)
    print(f"\nQUẺ HỖ: {r.ho_quai.name}")
    print(r.ho_quai)


if __name__ == "__main__":
    demo()
