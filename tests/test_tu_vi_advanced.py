"""Tests for Tử Vi advanced layers: interpretation + lưu trú + intra-cung."""

from __future__ import annotations

import pytest

from engine.tu_vi import (
    cast_la_so,
    dai_han_intra_cung_per_year,
    interpret_la_so,
    interpret_palace,
    luu_tru_for_year,
    year_to_ganzhi,
)


# ─── Interpretation ───────────────────────────────────────────────────────────


def test_interpret_palace_with_tu_vi():
    """Mệnh có Tử Vi → polarity favorable."""
    r = interpret_palace(
        palace_name="Mệnh",
        branch="Dần",
        chinh_at_palace=["Tử Vi"],
        tu_hoa={"Lộc": "Liêm Trinh", "Quyền": "Phá Quân", "Khoa": "Vũ Khúc", "Kỵ": "Thái Dương"},
    )
    assert r.palace_name == "Mệnh"
    assert r.chinh_tinh_count == 1
    assert r.polarity_score >= 1   # Tử Vi is positive
    assert r.polarity_tag in ("favorable", "mixed")
    assert "Tử Vi" in r.main_reading


def test_interpret_palace_empty():
    """Cung không chính tinh → polarity empty."""
    r = interpret_palace(
        palace_name="Tài Bạch", branch="Tý",
        chinh_at_palace=[],
        tu_hoa={"Lộc": "Liêm Trinh", "Quyền": "Phá Quân", "Khoa": "Vũ Khúc", "Kỵ": "Thái Dương"},
    )
    assert r.polarity_tag == "empty"
    # Wording v2 (2026-06-12): VCD = "bối cảnh mở", không gán nhãn cung trống xấu
    assert "Vô Chính Diệu" in r.main_reading
    assert "bối cảnh mở" in r.main_reading


def test_interpret_palace_hoa_loc_boosts_score():
    """Star with Hóa Lộc gets +2 to polarity."""
    r_with = interpret_palace(
        palace_name="Tài Bạch", branch="Tý",
        chinh_at_palace=["Vũ Khúc"],
        tu_hoa={"Lộc": "Vũ Khúc", "Quyền": "X", "Khoa": "Y", "Kỵ": "Z"},
    )
    r_without = interpret_palace(
        palace_name="Tài Bạch", branch="Tý",
        chinh_at_palace=["Vũ Khúc"],
        tu_hoa={"Lộc": "X", "Quyền": "Y", "Khoa": "Z", "Kỵ": "W"},
    )
    assert r_with.polarity_score > r_without.polarity_score
    assert len(r_with.hoa_attachments) == 1


def test_interpret_palace_includes_star_details():
    r = interpret_palace(
        palace_name="Mệnh", branch="Dần",
        chinh_at_palace=["Tử Vi", "Thiên Phủ"],
        tu_hoa={"Lộc": "X", "Quyền": "Y", "Khoa": "Z", "Kỵ": "W"},
    )
    assert len(r.star_details) == 2
    for sd in r.star_details:
        assert "ten_vi" in sd
        assert "tich_cuc" in sd
        assert "tieu_cuc" in sd


def test_interpret_la_so_full_chart():
    """Top-level interpretation produces all 12 palace readings."""
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    interp = interpret_la_so(la_so)
    assert "palace_readings" in interp
    assert len(interp["palace_readings"]) == 12
    assert "menh_focus" in interp
    assert interp["menh_focus"]["palace_name"] == "Mệnh"
    assert "chart_summary" in interp
    assert interp["chart_summary"]["favorable_palaces"] >= 0


# ─── Year ganzhi conversion ───────────────────────────────────────────────────


def test_year_to_ganzhi_1984_is_giap_ty():
    stem, branch = year_to_ganzhi(1984)
    assert stem == "Giáp"
    assert branch == "Tý"


def test_year_to_ganzhi_1985_is_at_suu():
    stem, branch = year_to_ganzhi(1985)
    assert stem == "Ất"
    assert branch == "Sửu"


def test_year_to_ganzhi_2024_is_giap_thin():
    """2024 is Giáp Thìn."""
    stem, branch = year_to_ganzhi(2024)
    assert stem == "Giáp"
    assert branch == "Thìn"


def test_year_to_ganzhi_2044_back_to_giap_ty():
    """1984 + 60 = 2044 → Giáp Tý again."""
    stem, branch = year_to_ganzhi(2044)
    assert stem == "Giáp"
    assert branch == "Tý"


# ─── Lưu Trú Sao ──────────────────────────────────────────────────────────────


def test_luu_tru_for_year_returns_complete():
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    transit = luu_tru_for_year(la_so=la_so, target_year=2026, birth_year=1985)
    assert transit["target_year"] == 2026
    # 1985 → 2026 = age 42 (1-based lunar age).
    assert transit["age_at_year"] == 42
    # 2026 = Bính Ngọ
    assert transit["target_stem"] == "Bính"
    assert transit["target_branch"] == "Ngọ"
    # Lưu Tứ Hóa for Bính year: Lộc=Thiên Đồng, Quyền=Thiên Cơ, Khoa=Văn Xương, Kỵ=Liêm Trinh
    assert transit["luu_tu_hoa"]["Lộc"] == "Thiên Đồng"
    assert transit["luu_tu_hoa"]["Kỵ"] == "Liêm Trinh"


def test_luu_tru_finds_correct_dai_han_cycle():
    """Age 42 must fall into the 4th Đại Vận cycle (starting age 35 for cuc=5)."""
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    transit = luu_tru_for_year(la_so=la_so, target_year=2026, birth_year=1985)
    cycle = transit["dai_han_cycle"]
    assert cycle["start_age"] <= 42 <= cycle["end_age"]


def test_luu_tru_intra_cung_offset():
    """If age = start_age + 2, intra_cung must be 2."""
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    transit = luu_tru_for_year(la_so=la_so, target_year=2026, birth_year=1985)
    expected_intra = 42 - transit["dai_han_cycle"]["start_age"]
    assert transit["dai_han_intra_cung"] == expected_intra


# ─── Đại Hạn Intra-Cung breakdown ─────────────────────────────────────────────


def test_dai_han_intra_cung_returns_10_years():
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    breakdown = dai_han_intra_cung_per_year(la_so=la_so, birth_year=1985, cycle_index=1)
    assert len(breakdown) == 10
    # Each entry has age + year + tieu_han_branch
    for entry in breakdown:
        assert "age" in entry
        assert "year" in entry
        assert "tieu_han_branch" in entry


def test_dai_han_intra_cung_rejects_invalid_cycle():
    la_so = cast_la_so(
        lunar_month=6, lunar_day=30, hour_branch="Tỵ",
        year_stem="Ất", year_branch="Sửu", gender="nam",
    )
    with pytest.raises(ValueError):
        dai_han_intra_cung_per_year(la_so=la_so, birth_year=1985, cycle_index=0)
    with pytest.raises(ValueError):
        dai_han_intra_cung_per_year(la_so=la_so, birth_year=1985, cycle_index=13)


# ─── API integration ──────────────────────────────────────────────────────────


def test_api_tu_vi_cast_includes_interpretation_by_default():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/tu-vi/cast",
        json={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "gender": "nam",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "interpretation" in payload
    assert len(payload["interpretation"]["palace_readings"]) == 12


def test_api_tu_vi_cast_with_target_year_returns_luu_tru():
    from fastapi.testclient import TestClient

    from api.main import app

    client = TestClient(app)
    response = client.post(
        "/api/tu-vi/cast",
        json={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "gender": "nam",
            "target_year": 2026,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "luu_tru_year" in payload
    assert payload["luu_tru_year"]["target_year"] == 2026
    assert payload["luu_tru_year"]["age_at_year"] == 42
