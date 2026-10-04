"""Tests for engine.tu_vi.dang_son_truc — Trục Đằng Sơn (4 trợ ↔ 4 hoại).

Paradigm: Tử Vi Hoàn Toàn Khoa Học (Đằng Sơn, Ch.24-25) — luật "toàn-không".
Hình-Riêu-Không-Kiếp là PHẢN ĐỀ phương-vị của Tả-Hữu-Xương-Khúc; đọc lá số phải
soi cả 2 cực để cân âm-dương. View này KHÔNG đặt lại sao — chỉ đọc vị trí ĐÃ AN.

Đồng thời khoá (lock) cross-check: 4 sao Hình-Riêu-Không-Kiếp đã có sẵn trong engine,
an đúng công thức cổ điển Bắc Phái.
"""

from __future__ import annotations

import pytest

# #34: cast endpoint dual-auth → chạy test as owner để qua gate (đồng bộ test_tu_vi_an_sao).
pytestmark = pytest.mark.usefixtures("as_owner")

from engine.tu_vi.an_sao import BRANCHES_TVI, cast_la_so
from engine.tu_vi.from_birth import cast_la_so_from_birth
from engine.tu_vi.dang_son_truc import (
    HOAI_TINH,
    TRO_TINH,
    build_dang_son_truc,
)

B = {name: i for i, name in enumerate(BRANCHES_TVI)}


# ─── Cross-check: 4 sao Hình-Riêu-Không-Kiếp đã có sẵn, đúng công thức ────────

def test_four_hoai_stars_at_formula_positions():
    """Lá số worked-example (M=6, D=30, giờ Tỵ H=6, Ất Sửu):
    - Thiên Hình  = fix(Dậu 9 + (6-1))  = fix(14) = 2 = Dần
    - Thiên Riêu  = fix(Sửu 1 + (6-1))  = fix(6)  = 6 = Ngọ   (engine key: Thiên Diêu)
    - Địa Kiếp    = fix(Hợi 11 + (6-1)) = fix(16) = 4 = Thìn  (thuận theo giờ)
    - Địa Không   = fix(Hợi 11 - (6-1)) = fix(6)  = 6 = Ngọ   (nghịch theo giờ)
    """
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    assert r["sao_le"]["Thiên Hình"] == B["Dần"]
    assert r["sao_q2"]["Thiên Diêu"] == B["Ngọ"]
    assert r["sat_tinh"]["Địa Kiếp"] == B["Thìn"]
    assert r["sat_tinh"]["Địa Không"] == B["Ngọ"]


# ─── View shape ──────────────────────────────────────────────────────────────

def test_constants_name_the_8_stars():
    assert TRO_TINH == ("Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc")
    assert HOAI_TINH == ("Thiên Hình", "Thiên Riêu", "Địa Không", "Địa Kiếp")


def test_view_has_4_tro_and_4_hoai():
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    view = build_dang_son_truc(r)
    assert set(view["tro_tinh"].keys()) == set(TRO_TINH)
    assert set(view["hoai_tinh"].keys()) == set(HOAI_TINH)


def test_view_reads_existing_positions_no_replacement():
    """Vị trí trong view PHẢI bằng đúng vị trí trong la_so gốc (chỉ đọc, không an lại)."""
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    view = build_dang_son_truc(r)
    assert view["hoai_tinh"]["Thiên Hình"]["branch_index"] == r["sao_le"]["Thiên Hình"]
    assert view["hoai_tinh"]["Thiên Riêu"]["branch_index"] == r["sao_q2"]["Thiên Diêu"]
    assert view["hoai_tinh"]["Địa Không"]["branch_index"] == r["sat_tinh"]["Địa Không"]
    assert view["hoai_tinh"]["Địa Kiếp"]["branch_index"] == r["sat_tinh"]["Địa Kiếp"]
    assert view["tro_tinh"]["Văn Khúc"]["branch_index"] == r["phu_tinh"]["Văn Khúc"]
    # Thiên Riêu giữ con trỏ về key gốc engine để tra cứu chéo
    assert view["hoai_tinh"]["Thiên Riêu"]["engine_key"] == "Thiên Diêu"


def test_view_wired_into_cast_output_and_json_safe():
    import json
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    assert "dang_son_truc" in r
    s = json.dumps(r, ensure_ascii=False)        # phải serialize được
    assert json.loads(s)["dang_son_truc"]["target"]["palace"] == "Mệnh"


# ─── Phân loại chiếu (tam-phương-tứ-chính) ───────────────────────────────────

def _la_so_stub(menh_index: int, pos: dict[str, int]) -> dict:
    """Tạo la_so tối thiểu để test logic cân/lệch một cách tất định.

    pos: {tên-hiển-thị-sao: branch_index} cho đủ 8 sao trục Đằng Sơn.
    """
    return {
        "menh_index": menh_index,
        "palaces": [{"name": "Mệnh", "branch_index": menh_index,
                     "branch": BRANCHES_TVI[menh_index]}],
        "phu_tinh": {
            "Tả Phù": pos["Tả Phù"], "Hữu Bật": pos["Hữu Bật"],
            "Văn Xương": pos["Văn Xương"], "Văn Khúc": pos["Văn Khúc"],
            "Thiên Khôi": 2, "Thiên Việt": 2,
        },
        "sat_tinh": {"Địa Không": pos["Địa Không"], "Địa Kiếp": pos["Địa Kiếp"],
                     "Lộc Tồn": 2},
        "sao_q2": {"Thiên Diêu": pos["Thiên Riêu"]},
        "sao_le": {"Thiên Hình": pos["Thiên Hình"]},
    }


_FAR = 2  # Dần — nằm ngoài tam-phương-tứ-chính của Mệnh Tý (={0,6,4,8})


def _all_far() -> dict[str, int]:
    return {name: _FAR for name in (*TRO_TINH, *HOAI_TINH)}


def test_chieu_dong_cung_xung_tam_hop():
    """Mệnh Tý (0): đồng=0, xung=6, tam-hợp=4 & 8."""
    pos = _all_far()
    pos["Tả Phù"] = 0     # đồng cung
    pos["Hữu Bật"] = 6    # xung chiếu
    pos["Văn Xương"] = 4  # tam hợp chiếu
    pos["Văn Khúc"] = 8   # tam hợp chiếu
    view = build_dang_son_truc(_la_so_stub(0, pos))
    assert view["tro_tinh"]["Tả Phù"]["chieu"] == "đồng cung"
    assert view["tro_tinh"]["Hữu Bật"]["chieu"] == "xung chiếu"
    assert view["tro_tinh"]["Văn Xương"]["chieu"] == "tam hợp chiếu"
    assert view["tro_tinh"]["Văn Khúc"]["chieu"] == "tam hợp chiếu"
    assert view["hoai_tinh"]["Thiên Hình"]["chieu"] == "không tới"


# ─── Cờ cân / lệch âm-dương ──────────────────────────────────────────────────

def test_balance_tinh_when_nothing_reaches():
    view = build_dang_son_truc(_la_so_stub(0, _all_far()))
    assert view["can_bang"]["the"] == "tĩnh"
    assert view["can_bang"]["tro_toi_target"] == []
    assert view["can_bang"]["hoai_toi_target"] == []


def test_balance_thien_duong_when_only_tro():
    pos = _all_far()
    pos["Văn Khúc"] = 6   # 1 trợ tới (xung)
    view = build_dang_son_truc(_la_so_stub(0, pos))
    assert view["can_bang"]["the"] == "thiên dương"
    assert view["can_bang"]["tro_toi_target"] == ["Văn Khúc"]
    assert view["can_bang"]["hoai_toi_target"] == []


def test_balance_thien_am_when_only_hoai():
    pos = _all_far()
    pos["Địa Kiếp"] = 4   # 1 hoại tới (tam hợp)
    view = build_dang_son_truc(_la_so_stub(0, pos))
    assert view["can_bang"]["the"] == "thiên âm"
    assert view["can_bang"]["hoai_toi_target"] == ["Địa Kiếp"]


def test_balance_luong_cuc_when_both():
    pos = _all_far()
    pos["Văn Khúc"] = 6   # trợ tới
    pos["Địa Kiếp"] = 4   # hoại tới
    view = build_dang_son_truc(_la_so_stub(0, pos))
    assert view["can_bang"]["the"] == "lưỡng cực giao"
    assert "Văn Khúc" in view["can_bang"]["tro_toi_target"]
    assert "Địa Kiếp" in view["can_bang"]["hoai_toi_target"]


# ─── Đối chiếu lá số founder (Mệnh Thiên Tướng @ Tỵ) ─────────────────────────

def test_founder_chart_dang_son_truc():
    """Founder 1988-06-05 23:30 (ÂL 4/22, giờ Tý, Mậu Thìn), Mệnh Thiên Tướng @ Tỵ.

    Cấu trúc (đọc đồng dạng, KHÔNG predict): Địa Không + Địa Kiếp cùng ở Hợi =
    xung-chiếu thẳng Mệnh Tỵ; 4 trợ-tinh KHÔNG tới Mệnh → trục Đằng Sơn nghiêng ÂM.
    Thiên Hình ở Tý (Tật Ách) — không đồng cung, không xung-chiếu Mệnh.
    """
    r = cast_la_so_from_birth(
        birth_datetime_local="1988-06-05T23:30:00",
        timezone="Asia/Ho_Chi_Minh", gender="nam",
    )
    assert r["menh_branch"] == "Tỵ"
    view = build_dang_son_truc(r)
    assert view["target"]["palace"] == "Mệnh"
    assert view["hoai_tinh"]["Địa Không"]["chieu"] == "xung chiếu"
    assert view["hoai_tinh"]["Địa Kiếp"]["chieu"] == "xung chiếu"
    assert view["hoai_tinh"]["Thiên Hình"]["chieu"] == "không tới"
    assert view["can_bang"]["the"] == "thiên âm"
    assert set(view["can_bang"]["hoai_toi_target"]) == {"Địa Không", "Địa Kiếp"}
    assert view["can_bang"]["tro_toi_target"] == []
