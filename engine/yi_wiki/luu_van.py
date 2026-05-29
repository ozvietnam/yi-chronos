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

def timeline_luu_nguyet_nam(
    birth: BirthInfo,
    year_chi_list: list[str],
    months: list[int] | None = None,
) -> dict:
    """Timeline 12 Lưu Nguyệt qua N năm — so sánh cùng tháng các năm khác nhau.

    Args:
        birth: sinh thần
        year_chi_list: list chi năm (vd ["Giáp Ngọ", "Ất Mùi", ...] hoặc chỉ ["Ngọ","Mùi"])
        months: list tháng âm muốn xem (default: [1..12])

    Returns:
        {
            "rows": [{"month": 1, "by_year": {"Ngọ": {chinh, hao, ngu_hanh_vs_birth}, ...}}, ...],
            "birth_summary": {...}
        }
    """
    months = months or list(range(1, 13))
    rows = []
    for m in months:
        by_year = {}
        for yc in year_chi_list:
            # Chỉ lấy chi (last word nếu format "Bính Ngọ")
            chi_only = yc.split()[-1] if " " in yc else yc
            try:
                now = NowInfo(
                    year_chi=chi_only, lunar_month=m,
                    lunar_day=birth.lunar_day, hour_chi=birth.hour_chi,
                )
                cast = cast_luu_nguyet(birth, now)
                # Giao thoa với Khởi Sinh
                from engine.yi_wiki.giao_thoa import (
                    BAT_QUAI_NGU_HANH, ngu_hanh_relation,
                )
                khoi_sinh = cast_que_khoi_sinh(birth)
                hanh_birth = BAT_QUAI_NGU_HANH[khoi_sinh.chinh_quai.upper_que]
                hanh_now = BAT_QUAI_NGU_HANH[cast.chinh_quai.upper_que]
                relation = ngu_hanh_relation(hanh_birth, hanh_now)
                by_year[yc] = {
                    "chinh": cast.chinh_quai.name,
                    "chinh_upper": cast.chinh_quai.upper_que,
                    "chinh_lower": cast.chinh_quai.lower_que,
                    "moving_line": cast.moving_line,
                    "vs_birth": relation["label_vi"],
                    "vs_birth_relation": relation["relation"],
                }
            except Exception as e:
                by_year[yc] = {"error": str(e)}
        rows.append({"month": m, "by_year": by_year})
    return {
        "birth_summary": {
            "year_chi": birth.year_chi,
            "lunar_month": birth.lunar_month,
            "lunar_day": birth.lunar_day,
            "hour_chi": birth.hour_chi,
        },
        "years": year_chi_list,
        "months": months,
        "rows": rows,
    }


def _build_tong_doc_narrative(vongs: dict, *casts) -> dict:
    """Tổng đọc 7 vòng + giao thoa → narrative cho user.

    KHÔNG bịa, KHÔNG predict cát/hung. Chỉ kể cấu trúc.
    Tạo 4 đoạn:
    1. Cấu trúc gốc (Khởi Sinh) — anh sinh trong cấu trúc gì
    2. Vận năm này (Lưu Niên) — năm hiện tại ánh xạ paradigm gì
    3. Vận tháng + ngày (Lưu Nguyệt + Nhật) — paradigm ngắn hạn
    4. Vũ trụ + cộng hưởng — giờ này anh × vũ trụ ra paradigm gì
    """
    from engine.yi_wiki.giao_thoa import (
        BAT_QUAI_NGU_HANH, giao_thoa_2_quẻ, ngu_hanh_relation,
    )

    v1, v2, v3, v4, v6, v7 = casts

    def _q_intro(v_key: str) -> str:
        """1 dòng intro cho 1 vòng."""
        vong = vongs[v_key]
        c = vong["chinh"]
        lg = vong["luan_giai"]
        ten_quẻ = f"#{c['number']} {c['name_vi']}" if c.get("number") else c["name"]
        tom = lg.get("tom_cot", "").split(".")[0].strip()[:120] if lg.get("tom_cot") else ""
        return f"**{vong['paradigm_meta']['ten']}** = {ten_quẻ} ({c['name']}). {tom}"

    def _hao_line(v_key: str) -> str:
        """1 dòng hào động."""
        vong = vongs[v_key]
        hb = vong["luan_giai"].get("hao_brief", "")
        if not hb:
            return ""
        # Strip markdown
        return hb.replace("**", "").split("—")[0].strip()[:200]

    # Đoạn 1: Cấu trúc gốc
    section_1 = f"""## 1. Cấu trúc Khởi Sinh — gốc cố định cả đời

{_q_intro('vong_1_khoi_sinh')}

Hào động {v1.moving_line}: {_hao_line('vong_1_khoi_sinh')}

→ Đây là **TƯỢNG SINH** của anh — KHÔNG predict đời, chỉ là cấu trúc tham chiếu.
"""

    # Đoạn 2: Vận năm
    gt_khoi_nien = giao_thoa_2_quẻ(v1.chinh_quai, v2.chinh_quai)
    section_2 = f"""## 2. Lưu Niên — năm anh đi qua

{_q_intro('vong_2_luu_nien')}

Hào động {v2.moving_line}: {_hao_line('vong_2_luu_nien')}

**Giao thoa với Khởi Sinh**:
- Thể vs Thể: {gt_khoi_nien['the_vs_the']['label_vi']}
- Dụng vs Dụng: {gt_khoi_nien['dung_vs_dung']['label_vi']}

→ {gt_khoi_nien['the_vs_the']['paradigm_note']} Năm này phản chiếu paradigm này cho anh.
"""

    # Đoạn 3: Vận tháng + ngày
    gt_nien_nguyet = giao_thoa_2_quẻ(v2.chinh_quai, v3.chinh_quai)
    section_3 = f"""## 3. Lưu Nguyệt + Lưu Nhật — paradigm ngắn hạn

**Tháng**: {_q_intro('vong_3_luu_nguyet')}

**Ngày**: {_q_intro('vong_4_luu_nhat')}

Hào động ngày {v4.moving_line}: {_hao_line('vong_4_luu_nhat')}

**Giao thoa Lưu Niên ↔ Lưu Nguyệt**:
- Thể: {gt_nien_nguyet['the_vs_the']['label_vi']}
- {gt_nien_nguyet['the_vs_the']['paradigm_note']}
"""

    # Đoạn 4: Vũ trụ + cộng hưởng
    gt_khoi_vu_tru = giao_thoa_2_quẻ(v1.chinh_quai, v6.chinh_quai)
    section_4 = f"""## 4. Vũ trụ giờ này + Cộng hưởng Tam Tài

**Quẻ Vũ trụ** (chung mọi người): {_q_intro('vong_6_vu_tru')}

**Cộng hưởng** (anh × vũ trụ): {_q_intro('vong_7_cong_huong')}

**Giao thoa Khởi Sinh ↔ Vũ trụ giờ này**:
- Thể: {gt_khoi_vu_tru['the_vs_the']['label_vi']}
- {gt_khoi_vu_tru['the_vs_the']['paradigm_note']}

→ Khoảnh khắc này vũ trụ ở paradigm **{vongs['vong_6_vu_tru']['chinh']['name_vi']}** — anh phản chiếu qua quẻ Cộng hưởng **{vongs['vong_7_cong_huong']['chinh']['name_vi']}**.
"""

    # Cảnh báo paradigm cuối
    foot = """## ⚠️ Cảnh báo paradigm

Iron Rule #4 (Khang Tiết Q3): **Mai Hoa = đọc đồng dạng, KHÔNG predict cát/hung tĩnh.**

7 vòng trên là **CẤU TRÚC** vũ trụ tại thời điểm — anh là **người đọc**, không phải nhận lệnh.

> _"Một vật vốn có một thân, một thân lại có một trời đất. Biết rằng muôn việc đều sẵn nơi ta, mới dám đặt nền móng cho Tam Tài."_ — Thiệu Khang Tiết, **Vận Pháp Thi**

Trong nhật ký Phase 2 sắp tới, anh gắn việc thực vào → sau N tháng pattern mới hiện ra. Hiện tại chỉ là **tượng**, chưa phải **kiểm chứng**.
"""

    return {
        "narrative": section_1 + "\n" + section_2 + "\n" + section_3 + "\n" + section_4 + "\n" + foot,
        "sections": {
            "khoi_sinh": section_1,
            "luu_nien": section_2,
            "luu_nguyet_nhat": section_3,
            "vu_tru_cong_huong": section_4,
            "paradigm_warn": foot,
        },
    }


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

    from engine.yi_wiki.luan_sau_kinhdich import extract_loi_kinh_and_hao_brief

    def _serialize(c: CastResult, paradigm_key: str) -> dict:
        # Trích Lời Kinh + hào động + insight cốt từ 64 file deep
        brief = extract_loi_kinh_and_hao_brief(
            c.chinh_quai.upper_que, c.chinh_quai.lower_que, c.moving_line,
        )
        return {
            "paradigm_key": paradigm_key,
            "paradigm_meta": VONG_PARADIGM[paradigm_key],
            "chinh": {"upper": c.chinh_quai.upper_que, "lower": c.chinh_quai.lower_que,
                      "name": c.chinh_quai.name, "upper_num": c.chinh_quai.upper_num,
                      "lower_num": c.chinh_quai.lower_num,
                      "name_vi": brief.get("name_vi", "?"),
                      "name_zh": brief.get("name_zh", "?"),
                      "number": brief.get("number", 0)},
            "bien": {"upper": c.bien_quai.upper_que, "lower": c.bien_quai.lower_que,
                     "name": c.bien_quai.name},
            "ho": {"upper": c.ho_quai.upper_que, "lower": c.ho_quai.lower_que,
                   "name": c.ho_quai.name},
            "moving_line": c.moving_line,
            "formula_trace": c.formula_trace,
            # CỐT: luận giải cụ thể cho UI
            "luan_giai": {
                "tom_cot": brief.get("tom_cot", ""),
                "loi_kinh": brief.get("loi_kinh", ""),
                "loi_kinh_dich": brief.get("loi_kinh_dich", ""),
                "hao_brief": brief.get("hao_brief", ""),
                "insight_cot": brief.get("insight_cot", ""),
            },
        }

    vongs = {
        "vong_1_khoi_sinh": _serialize(vong_1, "khoi_sinh"),
        "vong_2_luu_nien": _serialize(vong_2, "luu_nien"),
        "vong_3_luu_nguyet": _serialize(vong_3, "luu_nguyet"),
        "vong_4_luu_nhat": _serialize(vong_4, "luu_nhat"),
        "vong_5_luu_thoi": _serialize(vong_5, "luu_thoi"),
        "vong_6_vu_tru": _serialize(vong_6, "vu_tru"),
        "vong_7_cong_huong": _serialize(vong_7, "cong_huong"),
    }

    # Tổng đọc narrative — gắn paradigm cụ thể cho mỗi vòng + giao thoa
    tong_doc = _build_tong_doc_narrative(vongs, vong_1, vong_2, vong_3, vong_4, vong_6, vong_7)

    return {
        "input": {
            "birth": birth.__dict__,
            "now": now.__dict__,
        },
        **vongs,
        "tong_doc": tong_doc,
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
