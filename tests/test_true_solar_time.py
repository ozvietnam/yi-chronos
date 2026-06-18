"""Tests for true-solar-time correction (Y4 / issue #35)."""
from __future__ import annotations

from datetime import datetime

from core.true_solar_time import (
    adjust_datetime,
    province_longitude,
    resolve_longitude,
    solar_offset_minutes,
)
from engine.bat_tu import cast_bat_tu


def test_province_lookup_accent_insensitive():
    assert province_longitude("Lạng Sơn") == province_longitude("lang son")
    assert province_longitude("Hà Nội") is not None
    assert province_longitude("không-tồn-tại") is None


def test_resolve_longitude_exact_wins_over_province():
    assert resolve_longitude(birth_longitude=106.76, birth_province="Hà Nội") == 106.76
    assert resolve_longitude(birth_province="Hà Nội") == province_longitude("Hà Nội")
    assert resolve_longitude() is None
    assert resolve_longitude(birth_longitude=999) is None  # out of range → None


def test_offset_sign_east_positive_west_negative():
    dt = datetime(1988, 6, 5, 12, 0)
    assert solar_offset_minutes(110.0, dt) > 0   # east of 105°E → solar ahead
    assert solar_offset_minutes(103.0, dt) < 0   # west of 105°E → solar behind


def test_adjust_none_is_unchanged():
    assert adjust_datetime("1988-06-05T22:55:00", None) == "1988-06-05T22:55:00"


def test_adjust_crosses_hour_boundary():
    # Far-east province in June (~+10 min) pushes 22:55 past 23:00.
    out = adjust_datetime("1988-06-05T22:55:00", 107.08)
    assert out > "1988-06-05T23:00:00"


def test_cast_bat_tu_backward_compatible():
    """No birth_longitude → identical to the civil-time chart."""
    a = cast_bat_tu(birth_datetime_local="1988-06-05T23:30", timezone="Asia/Ho_Chi_Minh", gender="nam")
    b = cast_bat_tu(birth_datetime_local="1988-06-05T23:30", timezone="Asia/Ho_Chi_Minh",
                    gender="nam", birth_longitude=None)
    assert a["tu_tru"]["pillars"] == b["tu_tru"]["pillars"]
    # Founder day master stays Nhâm (the corrected baseline).
    assert a["tu_tru"]["day_master"]["stem"] == "Nhâm"


def test_cast_bat_tu_true_solar_shifts_boundary_hour():
    """A near-boundary birth in a far-east province shifts the Hour pillar."""
    civil = cast_bat_tu(birth_datetime_local="1988-06-05T22:55",
                        timezone="Asia/Ho_Chi_Minh", gender="nam")
    solar = cast_bat_tu(birth_datetime_local="1988-06-05T22:55",
                        timezone="Asia/Ho_Chi_Minh", gender="nam", birth_longitude=107.08)
    assert civil["tu_tru"]["pillars"]["hour"] != solar["tu_tru"]["pillars"]["hour"]
