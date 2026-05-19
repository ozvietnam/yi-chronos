"""Test for core/lunar_calendar.py — Hồ Ngọc Đức algorithm.

Validation strategy:
1. Spot-check known Tết Nguyên Đán dates (2018–2030).
2. Round-trip solar → lunar → solar across 5 consecutive years.
3. Specific leap-month spot checks (2023 has lunar leap month 2; 2025 has lunar leap month 6).
"""

from __future__ import annotations

import pytest

from core.lunar_calendar import LunarDate, lunar_to_solar, solar_to_lunar


# Known Tết Nguyên Đán (Vietnam, +07:00) — solar date of Lunar Jan 1.
# Source: official Vietnamese calendar publications.
TET_DATES = [
    (2018, 2, 16),
    (2019, 2, 5),
    (2020, 1, 25),
    (2021, 2, 12),
    (2022, 2, 1),
    (2023, 1, 22),
    (2024, 2, 10),
    (2025, 1, 29),
    (2026, 2, 17),
    (2027, 2, 6),
    (2028, 1, 26),
    (2029, 2, 13),
    (2030, 2, 2),
]


@pytest.mark.parametrize("year,month,day", TET_DATES)
def test_solar_to_lunar_tet_matches_official(year: int, month: int, day: int) -> None:
    lunar = solar_to_lunar(day, month, year, 7.0)
    assert lunar.day == 1
    assert lunar.month == 1
    assert lunar.year == year
    assert lunar.is_leap is False


@pytest.mark.parametrize("year,month,day", TET_DATES)
def test_lunar_to_solar_tet_matches_official(year: int, month: int, day: int) -> None:
    back_day, back_month, back_year = lunar_to_solar(1, 1, year, False, 7.0)
    assert (back_year, back_month, back_day) == (year, month, day)


def test_round_trip_full_year_2024() -> None:
    """Every solar date in 2024 must round-trip cleanly."""
    from datetime import date, timedelta

    cur = date(2024, 1, 1)
    end = date(2024, 12, 31)
    while cur <= end:
        lunar = solar_to_lunar(cur.day, cur.month, cur.year, 7.0)
        back = lunar_to_solar(lunar.day, lunar.month, lunar.year, lunar.is_leap, 7.0)
        assert back == (cur.day, cur.month, cur.year), \
            f"Round-trip failed for {cur}: lunar={lunar} → back={back}"
        cur = cur + timedelta(days=1)


def test_round_trip_full_year_2023_has_leap_month() -> None:
    """2023 must have at least one lunar leap month observed (round-trip clean)."""
    from datetime import date, timedelta

    cur = date(2023, 1, 1)
    end = date(2023, 12, 31)
    seen_leap = False
    while cur <= end:
        lunar = solar_to_lunar(cur.day, cur.month, cur.year, 7.0)
        back = lunar_to_solar(lunar.day, lunar.month, lunar.year, lunar.is_leap, 7.0)
        assert back == (cur.day, cur.month, cur.year), \
            f"Round-trip failed for {cur}: lunar={lunar} → back={back}"
        if lunar.is_leap:
            seen_leap = True
        cur = cur + timedelta(days=1)
    assert seen_leap, "2023 must have at least one lunar leap month observed"


def test_round_trip_full_year_2025_has_leap_month() -> None:
    """2025 must have at least one lunar leap month observed."""
    from datetime import date, timedelta

    cur = date(2025, 1, 1)
    end = date(2025, 12, 31)
    seen_leap = False
    while cur <= end:
        lunar = solar_to_lunar(cur.day, cur.month, cur.year, 7.0)
        back = lunar_to_solar(lunar.day, lunar.month, lunar.year, lunar.is_leap, 7.0)
        assert back == (cur.day, cur.month, cur.year)
        if lunar.is_leap:
            seen_leap = True
        cur = cur + timedelta(days=1)
    assert seen_leap, "2025 must have at least one lunar leap month observed"


def test_lunar_to_solar_with_invalid_leap_raises() -> None:
    # 2023 leap month is 2. Asking for "leap month 5" should fail.
    with pytest.raises(ValueError):
        lunar_to_solar(5, 5, 2023, True, 7.0)


def test_known_specific_dates() -> None:
    """A handful of known solar→lunar conversions from published Vietnamese calendars."""
    # 2024-04-30 (Giải phóng Miền Nam) = lunar 22/03/Giáp Thìn
    lunar = solar_to_lunar(30, 4, 2024, 7.0)
    assert (lunar.day, lunar.month, lunar.year, lunar.is_leap) == (22, 3, 2024, False)

    # 2024-09-02 (Quốc khánh) = lunar 30/07 Giáp Thìn
    lunar = solar_to_lunar(2, 9, 2024, 7.0)
    assert (lunar.day, lunar.month, lunar.year, lunar.is_leap) == (30, 7, 2024, False)


def test_lunar_date_dataclass_defaults() -> None:
    d = LunarDate(day=15, month=8, year=2024)
    assert d.is_leap is False  # Default.
