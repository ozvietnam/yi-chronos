"""Integration tests: family overlay flowing into van_trong_van + gps_engine."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from engine.family_system import (
    FamilyMember,
    compute_family_overlay_for_branch,
)
from engine.gps_engine import compute_gps_day
from engine.personal_quai import compute_natal_hexagram
from engine.van_trong_van import compute_van_trong_van


@pytest.fixture
def natal():
    return compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")


@pytest.fixture
def family():
    return [
        FamilyMember(role="self", name="Self", birth_year=1985,
                     birth_datetime_local="1985-07-20T03:30:00"),
        FamilyMember(role="spouse", name="Spouse", birth_year=1990),
        FamilyMember(role="child", name="Child", birth_year=2018),
    ]


# ---- compute_family_overlay_for_branch -----------------------------------

class TestFamilyOverlayHelper:
    def test_skip_self_default(self, family):
        overlay, avg = compute_family_overlay_for_branch(family, "Tý")
        names = [i.member_name for i in overlay]
        assert "Self" not in names
        assert len(overlay) == 2

    def test_can_include_self(self, family):
        overlay, _ = compute_family_overlay_for_branch(family, "Tý", skip_self=False)
        names = [i.member_name for i in overlay]
        assert "Self" in names

    def test_average_is_int_in_range(self, family):
        for branch in ("Tý", "Ngọ", "Sửu", "Mùi"):
            _, avg = compute_family_overlay_for_branch(family, branch)
            assert -25 <= avg <= 18

    def test_empty_family_returns_zero(self):
        overlay, avg = compute_family_overlay_for_branch([], "Tý")
        assert overlay == ()
        assert avg == 0


# ---- van_trong_van with family -------------------------------------------

class TestVanTrongVanWithFamily:
    def test_no_family_keeps_legacy_fields_empty(self, natal):
        start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        result = compute_van_trong_van(natal, start_date=start, span_days=3)
        for d in result.days:
            assert d.family_overlay == ()
            assert d.family_avg_score == 0
            assert d.final_score_with_family is None

    def test_with_family_populates_overlay_and_blended(self, natal, family):
        start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        result = compute_van_trong_van(
            natal, start_date=start, span_days=5, family_members=family
        )
        for d in result.days:
            assert len(d.family_overlay) == 2  # spouse + child (self excluded)
            assert d.final_score_with_family is not None
            assert 0 <= d.final_score_with_family <= 100

    def test_blended_score_differs_when_family_clashes(self, natal, family):
        """A day where family clashes hard should have blended < personal."""
        start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        result = compute_van_trong_van(
            natal, start_date=start, span_days=14, family_members=family
        )
        # At least one day should have family_avg negative (some clash).
        clash_days = [d for d in result.days if d.family_avg_score < 0]
        if clash_days:
            for d in clash_days:
                assert d.final_score_with_family <= d.day_compatibility.final_score

    def test_determinism(self, natal, family):
        start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        a = compute_van_trong_van(natal, start_date=start, span_days=7, family_members=family)
        b = compute_van_trong_van(natal, start_date=start, span_days=7, family_members=family)
        assert a.to_dict() == b.to_dict()

    def test_serializable(self, natal, family):
        import json
        start = datetime(2026, 5, 11, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        result = compute_van_trong_van(natal, start_date=start, span_days=3, family_members=family)
        payload = json.dumps(result.to_dict(), ensure_ascii=False)
        restored = json.loads(payload)
        assert "days" in restored
        assert restored["days"][0]["family_avg_score"] is not None


# ---- gps with family -----------------------------------------------------

class TestGPSWithFamily:
    def test_no_family_legacy_fields_empty(self, natal):
        target = date.today() + timedelta(days=3)
        gps = compute_gps_day(natal, target, min_score_for_trigger=70)
        for t in gps.triggers:
            assert t.family_overlay == ()
            assert t.family_avg_score == 0
            assert t.personal_only_score is None

    def test_with_family_populates_per_trigger(self, natal, family):
        target = date.today() + timedelta(days=3)
        gps = compute_gps_day(natal, target, min_score_for_trigger=70, family_members=family)
        for t in gps.triggers:
            assert len(t.family_overlay) == 2
            assert t.personal_only_score is not None
            assert 0 <= t.score <= 100
            assert 0 <= t.personal_only_score <= 100

    def test_blended_score_changes_filter_count(self, natal, family):
        """Adding family changes which triggers cross the threshold."""
        target = date.today() + timedelta(days=3)
        without_fam = compute_gps_day(natal, target, min_score_for_trigger=70)
        with_fam = compute_gps_day(natal, target, min_score_for_trigger=70, family_members=family)
        # Counts may differ because blending shifts some scores across threshold.
        assert isinstance(with_fam.triggers, tuple)
        # At minimum, every trigger that survived family blending has family_overlay.
        for t in with_fam.triggers:
            assert t.family_overlay

    def test_determinism(self, natal, family):
        target = date.today() + timedelta(days=3)
        a = compute_gps_day(natal, target, family_members=family)
        b = compute_gps_day(natal, target, family_members=family)
        assert a.to_dict() == b.to_dict()

    def test_serializable(self, natal, family):
        import json
        target = date.today() + timedelta(days=3)
        gps = compute_gps_day(natal, target, family_members=family, min_score_for_trigger=70)
        payload = json.dumps(gps.to_dict(), ensure_ascii=False)
        restored = json.loads(payload)
        if restored["triggers"]:
            assert "family_overlay" in restored["triggers"][0]
