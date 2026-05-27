"""Mai Hoa Lưu Vận — 7 vòng quẻ paradigm Khang Tiết + giao thoa.

Theo Mai Hoa Q1 "Niên-Nguyệt-Nhật-Thời khởi lệ":
  Thượng = (Năm + Tháng + Ngày) mod 8
  Hạ     = (Năm + Tháng + Ngày + Giờ) mod 8
  Động   = (Năm + Tháng + Ngày + Giờ) mod 6

Số: Tý=1, Sửu=2, ..., Hợi=12 (chi-năm và chi-giờ)
    Tháng/Ngày = số nguyên 1-12 / 1-30 (âm lịch)

Tổ sư KHÔNG có khái niệm "7 vòng cố định" — em (Claude) sáng tạo
paradigm này dựa trên Tam Tài (Anh × Vũ trụ × Thời gian).

⚠️ Iron Rule #4 — Mai Hoa = đọc đồng dạng, KHÔNG predict cát/hung tĩnh.
   File này KHÔNG được thêm logic "tốt/xấu" — chỉ tính quẻ + Ngũ hành.

📚 Reference: docs/design/MAI-HOA-LUU-VAN-GOAL.md — GOAL dài hạn KHÔNG QUÊN.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from engine.yi_wiki.cast import (
    CHI_NUMBER,
    CastResult,
    Hexagram,
    QUE_NUMBER_TO_NAME,
    cast_by_time,
)


# ============================================================================
# Birth + DateTime input dataclasses
# ============================================================================

@dataclass
class BirthInfo:
    """Sinh thần — input cho các vòng cá nhân."""
    year_chi: str       # Chi năm sinh (vd "Thìn" cho 1988 Mậu Thìn)
    lunar_month: int    # 1-12 tháng âm
    lunar_day: int      # 1-30 ngày âm
    hour_chi: str       # Chi giờ sinh (vd "Tý")


@dataclass
class NowInfo:
    """Thời điểm hiện tại — input cho các vòng vận hành."""
    year_chi: str       # Chi năm hiện tại (vd "Bính Ngọ" 2026 → "Ngọ")
    lunar_month: int    # tháng âm hiện tại
    lunar_day: int      # ngày âm hiện tại
    hour_chi: str       # chi giờ hiện tại


# ============================================================================
# 7 vòng quẻ — paradigm Tam Tài (Anh × Vũ trụ × Thời)
# ============================================================================

VONG_PARADIGM = {
    "khoi_sinh": {
        "ten": "Quẻ Khởi Sinh",
        "doi_moi_khi": "Không bao giờ (cố định cả đời)",
        "phan_anh": "Tượng khoảnh khắc Anh sinh ra — cấu trúc gốc",
        "paradigm": "KHÔNG dùng để predict đời. Chỉ là tham chiếu cấu trúc.",
    },
    "luu_nien": {
        "ten": "Lưu Niên",
        "doi_moi_khi": "Đầu năm âm",
        "phan_anh": "Tượng năm hiện tại Anh đi qua",
        "paradigm": "Năm này Anh đi qua paradigm gì — không phải 'năm tốt/xấu'.",
    },
    "luu_nguyet": {
        "ten": "Lưu Nguyệt",
        "doi_moi_khi": "Đầu tháng âm",
        "phan_anh": "Tượng tháng — chu kỳ ngắn hơn năm",
        "paradigm": "Tháng này Anh đi qua paradigm gì.",
    },
    "luu_nhat": {
        "ten": "Lưu Nhật",
        "doi_moi_khi": "23:00 (giờ Tý) — ngày Mai Hoa bắt đầu giờ Tý",
        "phan_anh": "Tượng ngày — paradigm 24 tiếng",
        "paradigm": "Ngày này Anh đi qua paradigm gì.",
    },
    "luu_thoi": {
        "ten": "Lưu Thời",
        "doi_moi_khi": "Mỗi 2 tiếng (12 chi giờ)",
        "phan_anh": "Tượng thời điểm vũ trụ chiếu vào Anh",
        "paradigm": "Khoảnh khắc này Anh phản chiếu cái gì.",
    },
    "vu_tru": {
        "ten": "Quẻ Vũ trụ",
        "doi_moi_khi": "Mỗi 2 tiếng",
        "phan_anh": "Tượng vũ trụ thuần — không cá nhân hóa",
        "paradigm": "Chung cho mọi người gieo cùng giờ. KHÔNG dành riêng Anh.",
    },
    "cong_huong": {
        "ten": "Quẻ Cộng hưởng Tam Tài",
        "doi_moi_khi": "Mỗi 2 tiếng",
        "phan_anh": "Giao thoa Anh × Vũ trụ",
        "paradigm": "Tổng số khởi sinh + số hiện tại → quẻ thứ 3.",
    },
}


def cast_que_khoi_sinh(birth: BirthInfo) -> CastResult:
    """Vòng 1 — Quẻ Khởi Sinh (cố định cả đời Anh)."""
    return cast_by_time(
        year_chi=birth.year_chi,
        month=birth.lunar_month,
        day=birth.lunar_day,
        hour_chi=birth.hour_chi,
    )


def cast_luu_nien(birth: BirthInfo, now_year_chi: str) -> CastResult:
    """Vòng 2 — Lưu Niên: năm hiện tại + tháng/ngày/giờ sinh."""
    return cast_by_time(
        year_chi=now_year_chi,
        month=birth.lunar_month,
        day=birth.lunar_day,
        hour_chi=birth.hour_chi,
    )


def cast_luu_nguyet(birth: BirthInfo, now: NowInfo) -> CastResult:
    """Vòng 3 — Lưu Nguyệt: năm+tháng hiện tại, ngày+giờ sinh."""
    return cast_by_time(
        year_chi=now.year_chi,
        month=now.lunar_month,
        day=birth.lunar_day,
        hour_chi=birth.hour_chi,
    )


def cast_luu_nhat(birth: BirthInfo, now: NowInfo) -> CastResult:
    """Vòng 4 — Lưu Nhật: năm+tháng+ngày hiện tại, giờ sinh."""
    return cast_by_time(
        year_chi=now.year_chi,
        month=now.lunar_month,
        day=now.lunar_day,
        hour_chi=birth.hour_chi,
    )


def cast_luu_thoi(now: NowInfo) -> CastResult:
    """Vòng 5 — Lưu Thời: tất cả hiện tại (cá nhân nhìn vào vũ trụ).

    Note: cùng công thức Vòng 6 (Vũ trụ) — khác ở paradigm explain.
    Vòng 5: Anh đứng ở khoảnh khắc này → đọc qua mắt Anh.
    Vòng 6: vũ trụ rung — chung cho mọi người.
    """
    return cast_by_time(
        year_chi=now.year_chi,
        month=now.lunar_month,
        day=now.lunar_day,
        hour_chi=now.hour_chi,
    )


def cast_que_vu_tru(now: NowInfo) -> CastResult:
    """Vòng 6 — Quẻ Vũ trụ thuần (chung cho mọi người)."""
    return cast_by_time(
        year_chi=now.year_chi,
        month=now.lunar_month,
        day=now.lunar_day,
        hour_chi=now.hour_chi,
    )


def cast_que_cong_huong(birth: BirthInfo, now: NowInfo) -> CastResult:
    """Vòng 7 — Quẻ Cộng hưởng Tam Tài.

    Paradigm: tổng số GIEO sinh + tổng số GIEO hiện tại → quẻ thứ 3.
    Đây là "giao thoa số" giữa Anh và Vũ trụ — không phải thật quẻ
    nào trong vòng 1-6, mà là kết quả phép cộng paradigm.
    """
    b_y = CHI_NUMBER[birth.year_chi]
    b_h = CHI_NUMBER[birth.hour_chi]
    n_y = CHI_NUMBER[now.year_chi]
    n_h = CHI_NUMBER[now.hour_chi]

    # Tổng số cộng hưởng
    sum_birth = b_y + birth.lunar_month + birth.lunar_day
    sum_now = n_y + now.lunar_month + now.lunar_day

    upper_total = sum_birth + sum_now
    lower_total = upper_total + b_h + n_h

    upper_num = (upper_total % 8) or 8
    lower_num = (lower_total % 8) or 8
    moving = (lower_total % 6) or 6

    upper_que = QUE_NUMBER_TO_NAME[upper_num][0]
    lower_que = QUE_NUMBER_TO_NAME[lower_num][0]

    chinh = Hexagram(
        upper_que=upper_que, lower_que=lower_que,
        upper_num=upper_num, lower_num=lower_num,
    )

    # Reuse cast_by_time logic for bien + ho
    from engine.yi_wiki.cast import _build_bien_quai, _build_ho_quai
    bien = _build_bien_quai(chinh, moving)
    ho = _build_ho_quai(chinh)

    trace = [
        f"Cộng hưởng paradigm Tam Tài (Anh × Vũ trụ)",
        f"Sinh: {birth.year_chi}({b_y}) + {birth.lunar_month}T + {birth.lunar_day}D + {birth.hour_chi}({b_h}) = {sum_birth + b_h}",
        f"Hiện tại: {now.year_chi}({n_y}) + {now.lunar_month}T + {now.lunar_day}D + {now.hour_chi}({n_h}) = {sum_now + n_h}",
        f"Upper = ({sum_birth} + {sum_now}) mod 8 = {upper_total} mod 8 = {upper_num} → {upper_que}",
        f"Lower = ({upper_total} + {b_h} + {n_h}) mod 8 = {lower_total} mod 8 = {lower_num} → {lower_que}",
        f"Động hào = {lower_total} mod 6 = {moving}",
    ]

    return CastResult(
        timestamp=0,
        inputs={
            "paradigm": "tam_tai_cong_huong",
            "birth": birth.__dict__,
            "now": now.__dict__,
        },
        upper_num=upper_num,
        lower_num=lower_num,
        moving_line=moving,
        chinh_quai=chinh,
        bien_quai=bien,
        ho_quai=ho,
        formula_trace=trace,
    )


# ============================================================================
# Snapshot — 7 vòng cùng lúc + giao thoa
# ============================================================================

def quan_sat_luu_van(birth: BirthInfo, now: NowInfo) -> dict:
    """Snapshot 7 vòng + giao thoa giữa các vòng.

    Returns:
        {
            "vong_1_khoi_sinh": CastResult dict,
            ...
            "vong_7_cong_huong": ...,
            "giao_thoa": {
                "khoi_sinh_vs_luu_nien": dict,
                "khoi_sinh_vs_luu_nguyet": dict,
                "khoi_sinh_vs_vu_tru": dict,
                "luu_nien_vs_luu_nguyet": dict,
            },
        }
    """
    from engine.yi_wiki.giao_thoa import giao_thoa_2_quẻ

    vong_1 = cast_que_khoi_sinh(birth)
    vong_2 = cast_luu_nien(birth, now.year_chi)
    vong_3 = cast_luu_nguyet(birth, now)
    vong_4 = cast_luu_nhat(birth, now)
    vong_5 = cast_luu_thoi(now)
    vong_6 = cast_que_vu_tru(now)
    vong_7 = cast_que_cong_huong(birth, now)

    def _serialize(c: CastResult, paradigm_key: str) -> dict:
        return {
            "paradigm_key": paradigm_key,
            "paradigm_meta": VONG_PARADIGM[paradigm_key],
            "chinh": {"upper": c.chinh_quai.upper_que, "lower": c.chinh_quai.lower_que,
                      "name": c.chinh_quai.name, "upper_num": c.chinh_quai.upper_num,
                      "lower_num": c.chinh_quai.lower_num},
            "bien": {"upper": c.bien_quai.upper_que, "lower": c.bien_quai.lower_que,
                     "name": c.bien_quai.name},
            "ho": {"upper": c.ho_quai.upper_que, "lower": c.ho_quai.lower_que,
                   "name": c.ho_quai.name},
            "moving_line": c.moving_line,
            "formula_trace": c.formula_trace,
        }

    return {
        "input": {
            "birth": birth.__dict__,
            "now": now.__dict__,
        },
        "vong_1_khoi_sinh": _serialize(vong_1, "khoi_sinh"),
        "vong_2_luu_nien": _serialize(vong_2, "luu_nien"),
        "vong_3_luu_nguyet": _serialize(vong_3, "luu_nguyet"),
        "vong_4_luu_nhat": _serialize(vong_4, "luu_nhat"),
        "vong_5_luu_thoi": _serialize(vong_5, "luu_thoi"),
        "vong_6_vu_tru": _serialize(vong_6, "vu_tru"),
        "vong_7_cong_huong": _serialize(vong_7, "cong_huong"),
        "giao_thoa": {
            "khoi_sinh_vs_luu_nien": giao_thoa_2_quẻ(vong_1.chinh_quai, vong_2.chinh_quai),
            "khoi_sinh_vs_luu_nguyet": giao_thoa_2_quẻ(vong_1.chinh_quai, vong_3.chinh_quai),
            "khoi_sinh_vs_luu_nhat": giao_thoa_2_quẻ(vong_1.chinh_quai, vong_4.chinh_quai),
            "khoi_sinh_vs_vu_tru": giao_thoa_2_quẻ(vong_1.chinh_quai, vong_6.chinh_quai),
            "luu_nien_vs_luu_nguyet": giao_thoa_2_quẻ(vong_2.chinh_quai, vong_3.chinh_quai),
            "luu_nhat_vs_vu_tru": giao_thoa_2_quẻ(vong_4.chinh_quai, vong_6.chinh_quai),
        },
        "_paradigm_note": (
            "⚠️ Iron Rule #4: Mai Hoa = đọc đồng dạng, KHÔNG predict cát/hung tĩnh. "
            "7 vòng quẻ là TƯỢNG CẤU TRÚC tại thời điểm — Anh là người đọc + quyết định, "
            "không phải vũ trụ ra lệnh."
        ),
    }
