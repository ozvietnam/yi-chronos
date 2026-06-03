"""Tests for Dụng Thần v2 — climate balance (Điều Hậu) layer.

Driven by sage critique #1 from kanban council:
  > "Kỷ Thổ sinh tháng Mùi (nóng khô) cần Thủy điều hậu hơn là Mộc khắc chế."

This module validates the climate matrix encodes classical 窮通寶鑑 logic.
"""

from __future__ import annotations

import pytest

from engine.bat_tu.dung_than import determine_dung_than


def _strong_thổ_chart() -> dict[str, float]:
    """Element distribution typical of Kỷ Thổ vượng (smoke #6 founder chart)."""
    return {"thổ": 5.2, "hỏa": 2.9, "mộc": 1.3, "thủy": 1.3, "kim": 0.9}


# ─── Backward compat: v1 callers (no day_stem/month_branch) ──────────────────


def test_v1_call_signature_still_works():
    """Existing callers without day_stem/month_branch must get v1 behavior."""
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=_strong_thổ_chart(),
        strength_tag="strong",
        month_branch_element="thổ",
    )
    assert dt.dung_than_element  # primary chosen
    # v2 fields default to None when climate inputs missing
    assert dt.climate_dung_than is None
    assert dt.strength_climate_agree is None
    assert dt.confidence == "medium"  # default


# ─── Sage critique #1 — Kỷ Thổ + Mùi ─────────────────────────────────────────


def test_ky_tho_thang_mui_climate_picks_thuy():
    """The flagship case: Kỷ Thổ sinh tháng Mùi → climate prefers Thủy."""
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=_strong_thổ_chart(),
        strength_tag="strong",
        month_branch_element="thổ",  # Mùi → thổ
        day_stem="Kỷ",
        month_branch="Mùi",
    )
    # Strength still picks Mộc (drain a strong Day Master)
    assert dt.dung_than_element == "mộc"
    # Climate picks Thủy (cool down the hot summer Earth)
    assert dt.climate_dung_than == "thủy"
    # They disagree → low confidence + Hỷ Thần promoted to climate
    assert dt.strength_climate_agree is False
    assert dt.confidence == "low"
    assert dt.hy_than_element == "thủy"
    assert "Điều Hậu" in dt.dung_than_reason
    assert "Thủy" in (dt.climate_reason or "")


# ─── High-confidence cases (strength + climate agree) ────────────────────────


def test_binh_hoa_dong_climate_agrees():
    """Bính Hỏa nhược sinh tháng Tý — both pick Mộc to support + warm."""
    dt = determine_dung_than(
        day_element="hỏa",
        element_counts={"hỏa": 1.0, "thủy": 4.0, "mộc": 1.0, "kim": 1.0, "thổ": 1.0},
        strength_tag="weak",
        day_stem="Bính",
        month_branch="Tý",
    )
    assert dt.strength_climate_agree is True
    assert dt.confidence == "high"
    assert dt.climate_dung_than == "mộc"


def test_giap_moc_thang_he_picks_thuy_for_climate():
    """Giáp Mộc sinh tháng Tỵ — climate needs Thủy to nourish roots."""
    dt = determine_dung_than(
        day_element="mộc",
        element_counts={"mộc": 2.0, "hỏa": 3.0, "thổ": 1.0, "kim": 1.0, "thủy": 0.5},
        strength_tag="weak",
        day_stem="Giáp",
        month_branch="Tỵ",
    )
    assert dt.climate_dung_than == "thủy"
    # Whether strength and climate agree depends on count-based heuristic;
    # what matters is climate is correctly identified.
    assert dt.confidence in ("high", "low", "medium")


# ─── Per-stem climate spot checks ────────────────────────────────────────────


@pytest.mark.parametrize("stem,branch,expected", [
    ("Bính", "Ngọ", "thủy"),  # Hot Fire in summer — cool with Thủy
    ("Đinh", "Tỵ", "thủy"),
    ("Mậu", "Ngọ", "thủy"),   # Hot Earth in summer
    ("Kỷ", "Tỵ", "thủy"),
    ("Canh", "Ngọ", "thủy"),  # Hot Metal in summer
    ("Nhâm", "Tý", "hỏa"),    # Frozen Water in winter — warm with Hỏa
    ("Quý", "Hợi", "hỏa"),
    ("Đinh", "Sửu", "mộc"),   # Cold Fire in winter — Mộc feeds the flame
])
def test_climate_matrix_canonical_picks(stem, branch, expected):
    dt = determine_dung_than(
        day_element="thổ",  # element doesn't matter; we test climate_dung_than
        element_counts={"thổ": 2, "hỏa": 2, "mộc": 2, "thủy": 2, "kim": 2},
        strength_tag="balanced",
        day_stem=stem,
        month_branch=branch,
    )
    assert dt.climate_dung_than == expected, (
        f"{stem} sinh tháng {branch} expected climate={expected}, got {dt.climate_dung_than}"
    )


# ─── Note + confidence integrity ─────────────────────────────────────────────


def test_v2_note_mentions_v2_and_climate():
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=_strong_thổ_chart(),
        strength_tag="strong",
        day_stem="Kỷ",
        month_branch="Mùi",
    )
    assert "v2" in dt.note
    assert "Điều Hậu" in dt.note or "窮通寶鑑" in dt.note


def test_dataclass_to_dict_includes_climate_fields():
    dt = determine_dung_than(
        day_element="thổ",
        element_counts=_strong_thổ_chart(),
        strength_tag="strong",
        day_stem="Kỷ",
        month_branch="Mùi",
    )
    d = dt.to_dict()
    for k in ("climate_dung_than", "climate_secondary", "climate_reason",
              "strength_climate_agree", "confidence"):
        assert k in d, f"Missing v2 field {k} in to_dict()"


# ─── Regression: hỷ/kỵ thần computed relative to NHẬT CHỦ (issue #16) ──────────
# Bug was: hy=_generating(dung), ky=_controlling(dung) → for weak DM the hỷ thần
# resolved to 官殺 (the element that KILLS the day master). Must be the supporting
# group {印, 比劫} instead, with 官殺 as kỵ thần.


@pytest.mark.parametrize(
    "dm, seal, pressure",
    [
        ("mộc", "thủy", "kim"),
        ("hỏa", "mộc", "thủy"),
        ("thổ", "hỏa", "mộc"),
        ("kim", "thổ", "hỏa"),
        ("thủy", "kim", "thổ"),
    ],
)
def test_weak_dm_hy_is_self_not_pressure(dm, seal, pressure):
    """Weak DM using Ấn (印): hỷ must be 比劫 (=DM element), kỵ must be 官殺.

    Previously hỷ wrongly resolved to 官殺 (the killing element).
    """
    counts = {e: 0.5 for e in ("mộc", "hỏa", "thổ", "kim", "thủy")}
    counts[seal] = 3.0  # make seal (印) the dụng thần
    dt = determine_dung_than(
        day_element=dm, strength_tag="weak", element_counts=counts
    )
    assert dt.dung_than_element == seal, f"dung should be 印={seal}"
    assert dt.hy_than_element == dm, (
        f"hỷ must be 比劫 (={dm}), got {dt.hy_than_element} — "
        f"must NOT be 官殺 ({pressure})"
    )
    assert dt.ky_than_element == pressure, f"kỵ must be 官殺 ({pressure})"


@pytest.mark.parametrize("dm", ["mộc", "hỏa", "thổ", "kim", "thủy"])
def test_strong_dm_ky_is_seal_not_output(dm):
    """Strong DM: kỵ thần must be 印 (seal — fuels the strong DM), and hỷ must be
    in the draining/restraining group {食傷, 財, 官殺}."""
    from engine.bat_tu.dung_than import classify_elements_role

    roles = classify_elements_role(dm)
    role_to_el = {r: e for e, r in roles.items()}
    counts = {e: 0.5 for e in ("mộc", "hỏa", "thổ", "kim", "thủy")}
    counts[role_to_el["pressure"]] = 2.0  # dung = pressure
    counts[role_to_el["wealth"]] = 1.0
    dt = determine_dung_than(
        day_element=dm, strength_tag="strong", element_counts=counts
    )
    assert dt.ky_than_element == role_to_el["seal"], "kỵ must be 印 for strong DM"
    favorable = {role_to_el["output"], role_to_el["wealth"], role_to_el["pressure"]}
    assert dt.hy_than_element in favorable
    assert dt.hy_than_element != dt.dung_than_element
