"""Tests for the kanban-based council bridge.

These tests hit the real Hermes Kanban CLI + SQLite DB. They are end-to-end
and require:
  - vendor/hermes-agent/.venv/bin/hermes exists
  - data/hermes_yi/kanban/boards/yi-chronos/kanban.db exists
  - sage profiles (mai-hoa-sage, ..., arbiter) exist

Each test archives the tasks it creates to keep the board clean.
"""

from __future__ import annotations

import subprocess

import pytest

from engine.ai import kanban_council as kc


# ─── Routing heuristic ───────────────────────────────────────────────────────


def test_select_sages_short_term():
    sages = kc.select_sages("Tuần này em có nên đổi việc không?")
    assert "mai_hoa" in sages
    assert "luc_hao" in sages
    assert "lien_hoa" in sages


def test_select_sages_destiny():
    sages = kc.select_sages("Sự nghiệp đời em sẽ ra sao?")
    assert "tu_vi" in sages
    assert "bat_tu" in sages
    assert "ha_lac" in sages


def test_select_sages_psychology():
    sages = kc.select_sages("Em đang rối loạn tâm lý")
    assert "western" in sages
    assert "bat_tu" in sages


def test_select_sages_default_when_no_keyword():
    sages = kc.select_sages("Em hỏi vu vơ")
    assert len(sages) >= 3
    # Default mix should include at least one of each domain
    assert any(s in sages for s in ("mai_hoa", "luc_hao", "lien_hoa"))
    assert any(s in sages for s in ("tu_vi", "bat_tu", "ha_lac"))


def test_select_sages_dedup():
    """Both 'tâm lý' (psych) and 'mệnh' (destiny) → bat_tu listed once."""
    sages = kc.select_sages("Tâm lý ảnh hưởng tới mệnh em ra sao?")
    assert sages.count("bat_tu") == 1


# ─── Infrastructure presence ─────────────────────────────────────────────────


def test_hermes_binary_exists():
    assert kc.HERMES_BIN.exists(), f"hermes binary missing at {kc.HERMES_BIN}"
    assert kc.HERMES_BIN.is_file()


def test_kanban_db_exists():
    assert kc.KANBAN_DB.exists(), f"kanban.db missing at {kc.KANBAN_DB}"


def test_required_profiles_exist():
    """All 7 sages + arbiter profile directories must exist."""
    profiles_dir = kc.HERMES_HOME / "profiles"
    for profile_name in list(kc.SAGES_BY_TAG.values()) + [kc.ARBITER_PROFILE]:
        assert (profiles_dir / profile_name).is_dir(), f"missing profile {profile_name}"
        assert (profiles_dir / profile_name / "SOUL.md").exists()


# ─── End-to-end consultation flow ────────────────────────────────────────────


def _archive_session(session: kc.CouncilSession) -> None:
    """Clean up tasks created by a test."""
    import os

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
        subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "archive", tid],
            env=env, capture_output=True, text=True,
        )


def test_consult_creates_p3_quorum():
    """consult() must create N sage tasks + 1 arbiter linked from all."""
    session = kc.consult(
        question="Test: tuần này em có nên ký hợp đồng?",
        sages=["mai_hoa", "luc_hao"],
        soul_key="test_user_1",
    )
    try:
        assert len(session.sage_task_ids) == 2
        assert "mai_hoa" in session.sage_task_ids
        assert "luc_hao" in session.sage_task_ids
        assert session.arbiter_id
        assert session.root_id == session.arbiter_id

        # Sage tasks must start in 'ready' (no deps)
        for tid in session.sage_task_ids.values():
            row = kc.task_status(tid)
            assert row is not None
            assert row["status"] == "ready"

        # Arbiter must start in 'todo' (parents not done yet)
        arb = kc.task_status(session.arbiter_id)
        assert arb is not None
        assert arb["status"] == "todo"
    finally:
        _archive_session(session)


def test_consult_with_chart_context():
    session = kc.consult(
        question="Phân tích cấu trúc đời",
        sages=["bat_tu"],
        chart_context={"day_master": "Kỷ thổ", "year": "Ất Sửu"},
        soul_key="test_user_2",
    )
    try:
        # Body of sage task should mention chart context
        # We test via session snapshot — task body isn't surfaced there,
        # so just confirm the task exists in ready state.
        snap = kc.session_snapshot(session)
        assert snap["progress"]["sages_total"] == 1
        assert snap["sages"]["bat_tu"]["status"] == "ready"
    finally:
        _archive_session(session)


def test_consult_rejects_unknown_sage():
    with pytest.raises(ValueError, match="Unknown sage"):
        kc.consult("test", sages=["unknown_school"])


def test_consult_rejects_empty_sage_list():
    with pytest.raises(ValueError, match="No sages"):
        kc.consult("test", sages=[])


def test_session_snapshot_shows_progress():
    session = kc.consult(
        question="Snapshot progress test",
        sages=["mai_hoa", "bat_tu"],
        soul_key="test_user_3",
    )
    try:
        snap = kc.session_snapshot(session)
        assert snap["progress"]["sages_total"] == 2
        assert snap["progress"]["sages_done"] == 0
        assert snap["progress"]["complete"] is False
        assert snap["arbiter"]["status"] == "todo"
        assert set(snap["sages"].keys()) == {"mai_hoa", "bat_tu"}
    finally:
        _archive_session(session)


# ─── Session persistence ─────────────────────────────────────────────────────


def test_save_and_load_session():
    session = kc.consult(
        question="Persist test",
        sages=["mai_hoa"],
        soul_key="test_user_persist",
    )
    try:
        kc.save_session(session)
        loaded = kc.load_session(session.root_id)
        assert loaded is not None
        assert loaded.root_id == session.root_id
        assert loaded.sage_task_ids == session.sage_task_ids
        assert loaded.question == session.question
        assert loaded.soul_key == "test_user_persist"
    finally:
        _archive_session(session)


def test_list_recent_sessions():
    session = kc.consult(
        question="Recent list test",
        sages=["lien_hoa"],
        soul_key="test_user_recent",
    )
    try:
        kc.save_session(session)
        recent = kc.list_recent_sessions(limit=5)
        assert any(r["root_id"] == session.root_id for r in recent)
    finally:
        _archive_session(session)


def test_get_synthesis_returns_none_when_pending():
    session = kc.consult(
        question="Synthesis pending test",
        sages=["mai_hoa"],
        soul_key="test_user_synth",
    )
    try:
        # Arbiter is 'todo' — synthesis must be None
        assert kc.get_synthesis(session) is None
    finally:
        _archive_session(session)


# ─── FastAPI integration ─────────────────────────────────────────────────────


def test_api_kanban_consult_and_snapshot():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)

    # 1. Spawn a council
    r = client.post(
        "/api/ai/council/kanban/consult",
        json={
            "question": "API test: vận tháng tới",
            "sages": ["mai_hoa", "luc_hao"],
            "soul_key": "api_test_user",
        },
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    root_id = payload["session"]["root_id"]

    # 2. Snapshot
    r2 = client.get(f"/api/ai/council/kanban/sessions/{root_id}")
    assert r2.status_code == 200
    snap = r2.json()["snapshot"]
    assert snap["progress"]["sages_total"] == 2
    assert snap["progress"]["complete"] is False

    # 3. Synthesis (pending)
    r3 = client.get(f"/api/ai/council/kanban/sessions/{root_id}/synthesis")
    assert r3.status_code == 200
    assert r3.json()["status"] == "pending"
    assert r3.json()["synthesis"] is None

    # 4. Recent sessions
    r4 = client.get("/api/ai/council/kanban/sessions")
    assert r4.status_code == 200
    assert any(s["root_id"] == root_id for s in r4.json()["sessions"])

    # Clean up
    session = kc.load_session(root_id)
    if session:
        _archive_session(session)


def test_api_kanban_session_not_found():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/ai/council/kanban/sessions/t_nonexistent")
    assert r.status_code == 200
    assert r.json()["status"] == "not_found"
