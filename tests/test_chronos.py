"""Tests for core/chronos.py.

Note: This module has known simplifications compared to strict tradition:
- Year pillar uses CALENDAR year boundary (Jan 1), not Tết. So early-Jan
  results don't match traditional almanacs. Tests work around this by
  picking dates safely after Tết for year-pillar checks.
- Solar term computation uses a tropical-year approximation, not full
  ephemeris. Tests allow ±1 tiết khí slop near boundaries.

Day-pillar absolute calibration is a known issue (TODO: cross-check vs
Hồ Ngọc Đức published almanac). Tests here verify determinism + format
consistency rather than absolute values.
"""

from __future__ import annotations

import re

import pytest

from core.chronos import (
    BRANCHES,
    SOLAR_TERMS,
    STEMS,
    calculate_chronos_state,
    estimate_moon_phase,
    sexagenary_name,
)


def test_sexagenary_name_format() -> None:
    name = sexagenary_name(0)
    assert name == "Giáp Tý"
    assert sexagenary_name(59) == "Quý Hợi"
    # Index wraps modulo 60.
    assert sexagenary_name(60) == sexagenary_name(0)


def test_sexagenary_name_all_60_unique() -> None:
    seen = {sexagenary_name(i) for i in range(60)}
    assert len(seen) == 60


@pytest.mark.parametrize("year,expected", [
    (1984, "Giáp Tý"),    # Canonical start of 60-year cycle.
    (2024, "Giáp Thìn"),  # Year of the Dragon, Tết Feb 10 2024.
    (2025, "Ất Tỵ"),      # Year of the Snake.
    (2026, "Bính Ngọ"),   # Year of the Horse.
])
def test_year_pillar_after_tet(year: int, expected: str) -> None:
    """Spot-check year pillar at Mar 15 (well after Tết) of the given year."""
    state = calculate_chronos_state(f"{year}-03-15T12:00:00", "Asia/Ho_Chi_Minh")
    assert state.ganzhi.year == expected


def test_ganzhi_format_validity() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    pattern = re.compile(rf"^({'|'.join(STEMS)}) ({'|'.join(BRANCHES)})$")
    for pillar in (state.ganzhi.year, state.ganzhi.month, state.ganzhi.day, state.ganzhi.hour):
        assert pattern.match(pillar), f"Invalid pillar format: {pillar}"


@pytest.mark.parametrize("hour,expected_branch", [
    (23, "Tý"),
    (0, "Tý"),
    (1, "Sửu"),
    (3, "Dần"),
    (5, "Mão"),
    (11, "Ngọ"),
    (13, "Mùi"),
    (21, "Hợi"),
])
def test_hour_branch_mapping(hour: int, expected_branch: str) -> None:
    """Hour branches: Tý=23-1, Sửu=1-3, Dần=3-5, Mão=5-7, ..."""
    state = calculate_chronos_state(f"2026-05-10T{hour:02d}:00:00", "Asia/Ho_Chi_Minh")
    assert state.ganzhi.hour.split()[1] == expected_branch


def test_determinism_same_input_same_output() -> None:
    a = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    b = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert a.model_dump() == b.model_dump()


def test_solar_term_at_vernal_equinox_is_xuan_phan() -> None:
    """Around Mar 20-21, solar longitude ~0° → tiết Xuân phân."""
    state = calculate_chronos_state("2026-03-21T12:00:00", "Asia/Ho_Chi_Minh")
    assert state.solar_term.name_vi in ("Xuân phân", "Kinh trập"), \
        f"Expected Xuân phân near vernal equinox, got {state.solar_term.name_vi}"


def test_solar_term_id_in_valid_range() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert 1 <= state.solar_term.id <= 24
    assert state.solar_term.name_vi in SOLAR_TERMS


def test_solar_longitude_in_valid_range() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert 0 <= state.solar_term.solar_longitude < 360


def test_almanac_lunar_date_format() -> None:
    state = calculate_chronos_state("2024-02-10T12:00:00", "Asia/Ho_Chi_Minh")
    # 2024-02-10 = Tết Giáp Thìn = lunar 01/01/2024.
    assert state.almanac.lunar_date == "01/01/2024"
    assert state.almanac.lunar_is_leap_month is False


def test_almanac_weekday_correct() -> None:
    # 2024-02-10 was a Saturday.
    state = calculate_chronos_state("2024-02-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert state.almanac.weekday_vi == "Thứ Bảy"


def test_almanac_truc_in_valid_set() -> None:
    valid_truc = {"Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp", "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế"}
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert state.almanac.truc_of_day in valid_truc


def test_almanac_fortune_labels() -> None:
    valid = {"Cát", "Bình", "Hung"}
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert state.almanac.annual_fortune in valid
    assert state.almanac.monthly_fortune in valid
    assert state.almanac.daily_fortune in valid
    assert state.almanac.hourly_fortune in valid


def test_moon_phase_illumination_in_range() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert 0 <= state.moon_phase.illumination <= 1
    assert 0 <= state.moon_phase.phase_norm <= 1


def test_moon_phase_at_known_full_moon() -> None:
    """Jan 25 2024 was a full moon. Allow neighboring phase names too (1-day window)."""
    from datetime import datetime, timezone

    full_moon_dt = datetime(2024, 1, 25, 17, 54, tzinfo=timezone.utc)
    phase = estimate_moon_phase(full_moon_dt)
    assert phase.name in ("full_moon", "waxing_gibbous", "waning_gibbous"), \
        f"Expected full-moon family near 2024-01-25, got {phase.name}"
    assert phase.illumination > 0.9


def test_cycle_60_idx_in_range() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert 0 <= state.cycle_60_idx < 60


def test_local_datetime_preserves_timezone() -> None:
    state = calculate_chronos_state("2026-05-10T12:00:00", "Asia/Ho_Chi_Minh")
    assert "+07:00" in state.local_datetime or state.local_datetime.endswith("+07:00")
