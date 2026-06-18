"""Tests for engine.tu_vi.an_sao — Tử Vi star-placement algorithm."""

from __future__ import annotations

import pytest

# #34: /api/tu-vi/cast giờ dual-auth → test endpoint chạy as owner để qua gate.
pytestmark = pytest.mark.usefixtures("as_owner")

from engine.tu_vi import cast_la_so
from engine.tu_vi.an_sao import (
    BRANCHES_TVI,
    CUC_NAMES,
    PALACE_NAMES,
    TU_HOA_TABLE,
    arrange_palaces,
    cuc_so,
    cung_menh_index,
    cung_than_index,
    da_la,
    dai_van_direction,
    dai_van_trajectory,
    dia_khong_kiep,
    hoa_linh_tinh,
    huu_bat,
    kinh_duong,
    loc_ton,
    place_14_chinh_tinh,
    ta_phu,
    thien_khoi_viet,
    thien_phu_position,
    tieu_han_for_age,
    tu_hoa_assignments,
    tu_vi_position,
    van_khuc,
    van_xuong,
)


# ─── Cung Mệnh / Cung Thân ────────────────────────────────────────────────────


def test_cung_menh_canonical_example_thang7_gio_thin():
    """Spec example: lunar month 7, hour Thìn (H=5) → Mệnh tại Thìn (idx 4)."""
    assert cung_menh_index(7, 5) == 4


def test_cung_menh_thang12_gio_ty():
    """Lunar month 12, hour Tý (H=1) → fix(2+12-1) = 13 % 12 = 1 = Sửu."""
    assert cung_menh_index(12, 1) == 1


def test_cung_than_canonical_example():
    """Lunar month 7, hour Thìn (H=5) → Thân = fix(7+5) = 0 = Tý."""
    assert cung_than_index(7, 5) == 0


def test_menh_thân_invariant_at_ty_ngo():
    """Mệnh ≡ Thân when hour is Tý (1) or Ngọ (7)."""
    for m in range(1, 13):
        assert cung_menh_index(m, 1) == cung_than_index(m, 1)
        assert cung_menh_index(m, 7) == cung_than_index(m, 7)


def test_cung_menh_rejects_invalid():
    with pytest.raises(ValueError):
        cung_menh_index(0, 1)
    with pytest.raises(ValueError):
        cung_menh_index(1, 13)


# ─── 12 Palaces ───────────────────────────────────────────────────────────────


def test_arrange_palaces_returns_12():
    p = arrange_palaces(2)  # Mệnh at Dần
    assert len(p) == 12
    assert p[0]["name"] == "Mệnh"
    assert p[0]["branch"] == "Dần"
    # Canonical Bắc Phái counter-clockwise: Huynh Đệ at Sửu (idx 1)
    assert p[1]["name"] == "Huynh Đệ"
    assert p[1]["branch"] == "Sửu"
    assert p[11]["name"] == "Phụ Mẫu"


def test_arrange_palaces_full_cycle():
    """Last palace must be exactly 11 positions counter-clockwise from Mệnh."""
    menh_idx = 5  # Tỵ
    p = arrange_palaces(menh_idx)
    # Phụ Mẫu (idx 11) at fix(5-11) = fix(-6) = 6 = Ngọ
    assert p[11]["branch_index"] == 6


# ─── Cục số ───────────────────────────────────────────────────────────────────


def test_cuc_so_at_dan_for_at_year():
    """Ất + Dần (Mệnh) → row At-Canh × col Dan-Mao → 5 (Thổ Ngũ Cục)."""
    assert cuc_so("Ất", "Dần") == 5


def test_cuc_so_giap_at_ty():
    """Giáp + Tý → row Giap-Ky × col Ty-Suu → 2 (Thủy Nhị)."""
    assert cuc_so("Giáp", "Tý") == 2


def test_cuc_so_table_complete():
    """5 stems × 12 branches = 60 combinations must all resolve."""
    for stem in ("Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"):
        for branch in BRANCHES_TVI:
            result = cuc_so(stem, branch)
            assert result in (2, 3, 4, 5, 6)


def test_cuc_names():
    assert CUC_NAMES[2] == "Thủy Nhị Cục"
    assert CUC_NAMES[6] == "Hỏa Lục Cục"


# ─── Tử Vi anchor ─────────────────────────────────────────────────────────────


def test_tu_vi_thoi_ngu_day_30():
    """Thổ Ngũ Cục (5), day 30:
    divisor=30, quot=6, rem=0 → q=6%12=6; p_dan=5; offset=0 even → +0=5; +2→7=Mùi."""
    assert tu_vi_position(5, 30) == 7


def test_tu_vi_hoa_luc_day_15():
    """Hỏa Lục (6), day 15: offset=3, div=18÷6=3, q=3, p_dan=2.
    offset=3 odd → -3 → p_dan=-1; -1+2=1 → Sửu.
    Canonical Dần-base +2 correction."""
    assert tu_vi_position(6, 15) == 1


def test_tu_vi_all_combinations_valid():
    """5 cục × 30 days must all produce valid branch indices 0..11."""
    for cuc in (2, 3, 4, 5, 6):
        for day in range(1, 31):
            idx = tu_vi_position(cuc, day)
            assert 0 <= idx <= 11


# ─── 14 chính tinh ────────────────────────────────────────────────────────────


def test_place_14_chinh_tinh_returns_14_keys():
    stars = place_14_chinh_tinh(5)  # Tử Vi at Tỵ
    assert len(stars) == 14
    assert all(0 <= idx <= 11 for idx in stars.values())


def test_chinh_tinh_at_ty_anchor():
    """Tử Vi at Tỵ (5) — canonical Dần-Thân axis formula _fix(4-x):
        Thiên Cơ = fix(5-1) = 4 = Thìn
        Thái Dương = fix(5-3) = 2 = Dần
        Liêm Trinh = fix(5-8) = 9 = Dậu
        Thiên Phủ = fix(4-5) = 11 = Hợi
        Phá Quân = fix(11+10) = 9 = Dậu
    """
    stars = place_14_chinh_tinh(5)
    assert stars["Tử Vi"] == 5
    assert stars["Thiên Cơ"] == 4
    assert stars["Thái Dương"] == 2
    assert stars["Liêm Trinh"] == 9
    assert stars["Thiên Phủ"] == 11
    assert stars["Phá Quân"] == 9


def test_thien_phu_mirror_for_dan_is_dan():
    """Tử Vi Dần (2) → Thiên Phủ Dần (2) — self-mirror on the Dần-Thân axis."""
    assert thien_phu_position(2) == 2


def test_thien_phu_mirror_for_ty_is_hoi():
    """Tử Vi Tỵ (5) → Thiên Phủ Hợi (11). Canonical: _fix(4-5) = 11."""
    assert thien_phu_position(5) == 11


# ─── Tứ Hóa ───────────────────────────────────────────────────────────────────


def test_tu_hoa_giap_year():
    h = tu_hoa_assignments("Giáp")
    assert h["Lộc"] == "Liêm Trinh"
    assert h["Quyền"] == "Phá Quân"
    assert h["Khoa"] == "Vũ Khúc"
    assert h["Kỵ"] == "Thái Dương"


def test_tu_hoa_at_year():
    """Ất → Lộc=Thiên Cơ, Quyền=Thiên Lương, Khoa=Tử Vi, Kỵ=Thái Âm."""
    h = tu_hoa_assignments("Ất")
    assert h == {
        "Lộc": "Thiên Cơ", "Quyền": "Thiên Lương",
        "Khoa": "Tử Vi", "Kỵ": "Thái Âm",
    }


def test_tu_hoa_all_10_stems_have_4_assignments():
    for stem in TU_HOA_TABLE:
        h = tu_hoa_assignments(stem)
        assert set(h.keys()) == {"Lộc", "Quyền", "Khoa", "Kỵ"}


# ─── 6 phụ tinh ───────────────────────────────────────────────────────────────


def test_ta_phu_huu_bat_thang_1():
    """Tháng 1 → Tả Phù tại Thìn (4), Hữu Bật tại Tuất (10)."""
    assert ta_phu(1) == 4
    assert huu_bat(1) == 10


def test_van_khuc_xuong_for_gio_ty():
    """Giờ Tý (H=1) → Văn Khúc tại Thìn, Văn Xương tại Tuất."""
    assert van_khuc(1) == 4
    assert van_xuong(1) == 10


def test_thien_khoi_viet_giap_year():
    """Giáp → Khôi Sửu, Việt Mùi."""
    khoi, viet = thien_khoi_viet("Giáp")
    assert khoi == 1   # Sửu
    assert viet == 7   # Mùi


# ─── Sát tinh ─────────────────────────────────────────────────────────────────


def test_loc_ton_giap_year_at_dan():
    assert loc_ton("Giáp") == 2  # Dần


def test_kinh_da_la_offsets_from_loc_ton():
    """Kình Dương = Lộc Tồn + 1; Đà La = Lộc Tồn - 1."""
    assert kinh_duong("Giáp") == 3   # Mão (Lộc Tồn Dần + 1)
    assert da_la("Giáp") == 1        # Sửu (Lộc Tồn Dần - 1)


def test_hoa_linh_tinh_dan_year_gio_ty():
    """Year Dần (Dần-Ngọ-Tuất group) + giờ Tý (h=0):
    Hỏa anchor Sửu (1), Linh anchor Mão (3)."""
    hoa, linh = hoa_linh_tinh("Dần", 1)
    assert hoa == 1   # Sửu
    assert linh == 3  # Mão


def test_dia_khong_kiep_gio_ty():
    """Gờ Tý (h=0): Địa Không = Hợi, Địa Kiếp = Hợi."""
    khong, kiep = dia_khong_kiep(1)
    assert khong == 11
    assert kiep == 11


# ─── Đại Vận ──────────────────────────────────────────────────────────────────


def test_dai_van_direction_yang_male_forward():
    assert dai_van_direction("Giáp", "nam") == +1


def test_dai_van_direction_yin_male_backward():
    assert dai_van_direction("Ất", "nam") == -1


def test_dai_van_trajectory_starts_at_cuc_age():
    """Thổ Ngũ Cục → starting age 5."""
    traj = dai_van_trajectory(menh_index=2, cuc=5, year_stem="Ất", gender="nam")
    assert traj[0]["start_age"] == 5
    # Nghịch direction from Dần (2): V1 at Dần, V2 at Sửu (1), V3 at Tý (0).
    assert traj[0]["branch_index"] == 2
    assert traj[1]["branch_index"] == 1
    assert traj[2]["branch_index"] == 0


# ─── Tiểu Hạn ─────────────────────────────────────────────────────────────────


def test_tieu_han_dan_year_male_age_1():
    """Năm Dần (Dần-Ngọ-Tuất group) → Tiểu Hạn khởi tại Thìn (4)."""
    assert tieu_han_for_age("Dần", "nam", 1) == 4


def test_tieu_han_male_walks_forward():
    """Nam thuận: age 2 = Thìn + 1 = Tỵ (5)."""
    assert tieu_han_for_age("Dần", "nam", 2) == 5


def test_tieu_han_female_walks_backward():
    """Nữ nghịch: age 2 = Thìn - 1 = Mão (3)."""
    assert tieu_han_for_age("Dần", "nữ", 2) == 3


# ─── Top-level cast ───────────────────────────────────────────────────────────


def test_cast_la_so_complete_shape():
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    assert r["method_id"] == "tu_vi_an_sao_bac_phai_v1"
    assert r["menh_branch"] == "Dần"
    assert r["cuc"] == 5
    assert r["cuc_name"] == "Thổ Ngũ Cục"
    assert len(r["palaces"]) == 12
    assert len(r["chinh_tinh"]) == 14
    assert len(r["phu_tinh"]) == 6
    assert len(r["sat_tinh"]) == 7   # 6 sát + Lộc Tồn
    assert len(r["tu_hoa"]) == 4
    assert len(r["dai_van"]) == 12


def test_cast_la_so_known_chart_values():
    """Verify worked example (Ất Sửu year, M=6, D=30, hour Tỵ, nam)."""
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    # Mệnh Dần
    assert r["menh_branch"] == "Dần"
    # Thân = fix(6+6) = 0 = Tý
    assert r["than_branch"] == "Tý"
    # Cục = Thổ Ngũ
    assert r["cuc"] == 5
    # Tử Vi at Mùi (7) — Thổ Cục (5), day 30, Dần-base +2 formula
    assert r["chinh_tinh"]["Tử Vi"] == 7
    # Tứ Hóa Ất: Khoa = Tử Vi
    assert r["tu_hoa"]["Khoa"] == "Tử Vi"


def test_cast_la_so_is_json_serializable():
    import json
    r = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    s = json.dumps(r, ensure_ascii=False)
    decoded = json.loads(s)
    assert decoded["cuc"] == 5


def test_cast_la_so_rejects_invalid_gender():
    with pytest.raises(ValueError):
        cast_la_so(
            lunar_month=6, lunar_day=30, hour_branch="Tỵ",
            year_stem="Ất", year_branch="Sửu", gender="other",
        )


def test_api_tu_vi_cast_direct_mode():
    """Test /api/tu-vi/cast with direct lunar inputs."""
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/tu-vi/cast",
        json={
            "lunar_month": 6, "lunar_day": 30,
            "hour_branch": "Tỵ",
            "year_stem": "Ất", "year_branch": "Sửu",
            "gender": "nam",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "la_so" in payload
    state = payload["la_so"]
    assert state["menh_branch"] == "Dần"
    assert state["cuc"] == 5
    assert state["chinh_tinh"]["Tử Vi"] == 7


def test_api_tu_vi_cast_datetime_mode():
    """Test /api/tu-vi/cast with birth_datetime_local."""
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/tu-vi/cast",
        json={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "gender": "nam",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "la_so" in payload
    assert "input_resolved" in payload
    # Hour 10 → Tỵ (09:00-11:00).
    assert payload["input_resolved"]["hour_branch"] == "Tỵ"
