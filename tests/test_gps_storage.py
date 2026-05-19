"""Tests for GPS storage — pre-registration + feedback flow.

Uses an isolated SQLite file via env var to avoid clobbering production DB.
"""

from __future__ import annotations

import importlib
import os
import tempfile
from datetime import date, timedelta

import pytest


@pytest.fixture(scope="module")
def isolated_db():
    """Point YI_CHRONOS_DATABASE_URL to a temp SQLite for this module."""
    import data.database as db_mod

    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
    tmp.close()
    os.environ["YI_CHRONOS_DATABASE_URL"] = f"sqlite:///{tmp.name}"
    importlib.reload(db_mod)
    import engine.gps_storage as gs
    importlib.reload(gs)
    yield gs
    os.environ.pop("YI_CHRONOS_DATABASE_URL", None)
    importlib.reload(db_mod)
    importlib.reload(gs)
    try:
        os.unlink(tmp.name)
    except OSError:
        pass


@pytest.fixture
def make_gps():
    """Factory that returns a GPSDay for a given offset of days from today."""
    from engine.gps_engine import compute_gps_day
    from engine.personal_quai import compute_natal_hexagram

    natal = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")

    def _factory(days_offset: int = 3):
        target = date.today() + timedelta(days=days_offset)
        return natal, compute_gps_day(natal, target, "Asia/Ho_Chi_Minh", min_score_for_trigger=70)
    return _factory


def test_register_predictions_creates_records(isolated_db, make_gps):
    _, gps = make_gps(days_offset=2)
    receipts = isolated_db.register_predictions(gps)
    assert len(receipts) == len(gps.triggers)
    for r in receipts:
        assert r["prediction_id"].startswith("gp_")
        assert r["payload_hash"]
        assert r["for_date"] == gps.date_local


def test_duplicate_registration_raises(isolated_db, make_gps):
    _, gps = make_gps(days_offset=4)
    isolated_db.register_predictions(gps)
    with pytest.raises(isolated_db.DuplicatePredictionError):
        isolated_db.register_predictions(gps)


def test_back_dating_rejected(isolated_db, make_gps):
    from engine.gps_engine import compute_gps_day
    from engine.personal_quai import compute_natal_hexagram

    natal = compute_natal_hexagram("1985-07-20T03:30:00", "Asia/Ho_Chi_Minh")
    past_target = date.today() - timedelta(days=1)
    past_gps = compute_gps_day(natal, past_target, "Asia/Ho_Chi_Minh", min_score_for_trigger=70)
    with pytest.raises(isolated_db.BackDatingError):
        isolated_db.register_predictions(past_gps)


def test_list_predictions_returns_active(isolated_db, make_gps):
    _, gps = make_gps(days_offset=6)
    isolated_db.register_predictions(gps)
    rows = isolated_db.list_predictions(gps.profile_hash, status="active")
    assert len(rows) >= 1
    for r in rows:
        assert r["profile_hash"] == gps.profile_hash
        assert r["status"] == "active"


def test_feedback_too_early_rejected(isolated_db, make_gps):
    """Cannot submit feedback for a future date."""
    _, gps = make_gps(days_offset=8)
    receipts = isolated_db.register_predictions(gps)
    assert receipts, "Need at least one trigger registered"
    with pytest.raises(isolated_db.FeedbackTooEarlyError):
        isolated_db.submit_feedback(receipts[0]["prediction_id"], "matched")


def test_invalid_feedback_enum_rejected(isolated_db, make_gps):
    _, gps = make_gps(days_offset=10)
    receipts = isolated_db.register_predictions(gps)
    assert receipts
    with pytest.raises(ValueError):
        isolated_db.submit_feedback(receipts[0]["prediction_id"], "wrong_value")


def test_unknown_prediction_id_rejected(isolated_db):
    with pytest.raises(isolated_db.PredictionLogError):
        isolated_db.submit_feedback("gp_does_not_exist", "matched")


def test_compute_accuracy_on_empty_history(isolated_db):
    stats = isolated_db.compute_accuracy_stats("hash_with_no_history")
    assert stats["total_feedback"] == 0
    assert stats["match_rate"] is None


def test_gps_disabled_when_locked_to_other_profile(isolated_db, make_gps):
    """If LOCKED_PROFILE_HASH is set to a different hash, registration refused."""
    import core.config as config_mod

    _, gps = make_gps(days_offset=12)
    os.environ["YI_LOCKED_PROFILE_HASH"] = "some-other-hash"
    importlib.reload(config_mod)
    importlib.reload(isolated_db)
    try:
        with pytest.raises(isolated_db.GpsDisabledError):
            isolated_db.register_predictions(gps)
    finally:
        os.environ.pop("YI_LOCKED_PROFILE_HASH", None)
        importlib.reload(config_mod)
        importlib.reload(isolated_db)
