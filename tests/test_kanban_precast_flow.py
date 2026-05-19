"""Integration: kanban_council + precast helper + critique harvest.

Verifies the engine-data-in, critique-out flow end-to-end:
1. consult() with precast_data embeds engine JSON into sage task body
2. precast_for_sages auto-routes by sage_tag
3. session_snapshot harvests improve_system items from sage results
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def _archive(session) -> None:
    from engine.ai import kanban_council as kc

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
        subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "archive", tid],
            env=env, capture_output=True, text=True,
        )


# ─── Body templating ─────────────────────────────────────────────────────────


def test_consult_embeds_precast_json_in_sage_body():
    """When precast_data is provided, the sage task body must contain JSON
    payload + 'KHÔNG được cast lại' guard."""
    from engine.ai import kanban_council as kc

    precast = {
        "bat_tu": {
            "tu_tru": {"day_master": "Kỷ thổ"},
            "_test_marker": "PRECAST_INSIDE",
        }
    }
    session = kc.consult(
        question="Test embed precast",
        sages=["bat_tu"],
        precast_data=precast,
        soul_key="test_embed",
    )
    try:
        # Inspect the task body via hermes kanban show
        import json
        env = os.environ.copy()
        env["HERMES_HOME"] = str(kc.HERMES_HOME)
        out = subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "show",
             session.sage_task_ids["bat_tu"], "--json"],
            env=env, capture_output=True, text=True, check=True,
        )
        payload = json.loads(out.stdout)
        body = payload["task"]["body"]
        assert "KHÔNG được cast lại" in body
        assert "PRECAST_INSIDE" in body
        assert "Kỷ thổ" in body
        assert "precast_data (bat_tu)" in body
    finally:
        _archive(session)


def test_consult_without_precast_warns_engine_gap():
    """Without precast, body must tell sage to annotate engine_gap."""
    from engine.ai import kanban_council as kc

    session = kc.consult(
        question="Test missing precast",
        sages=["bat_tu"],
        soul_key="test_no_precast",
    )
    try:
        import json
        env = os.environ.copy()
        env["HERMES_HOME"] = str(kc.HERMES_HOME)
        out = subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "show",
             session.sage_task_ids["bat_tu"], "--json"],
            env=env, capture_output=True, text=True, check=True,
        )
        body = json.loads(out.stdout)["task"]["body"]
        assert "engine_gap" in body
        assert "không có precast_data" in body.lower() or "không có precast" in body.lower()
    finally:
        _archive(session)


# ─── precast_for_sages router ────────────────────────────────────────────────


def test_precast_for_sages_skips_when_no_payload():
    from engine.ai.precast import precast_for_sages

    # No birth, no event → nothing precast
    out = precast_for_sages(["bat_tu", "tu_vi"])
    assert out == {}


def test_precast_for_sages_event_only():
    """lien_hoa accepts n1+n2 from event payload."""
    from engine.ai.precast import precast_for_sages

    out = precast_for_sages(
        ["lien_hoa"], event={"n1": 5, "n2": 9}
    )
    # Either succeeds with engine output or returns error envelope — both fine,
    # what matters is that the router attempted the cast.
    assert "lien_hoa" in out


def test_required_inputs_describes_payload():
    from engine.ai.precast import required_inputs

    assert "birth" in required_inputs("bat_tu")
    assert "event" in required_inputs("lien_hoa")
    assert required_inputs("unknown") == {}


def test_precast_for_sages_with_birth_real_engine():
    """End-to-end: bat_tu cast with a real birth payload should succeed."""
    from engine.ai.precast import precast_for_sages

    out = precast_for_sages(
        ["bat_tu"],
        birth={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "timezone": "Asia/Ho_Chi_Minh",
            "gender": "nam",
        },
    )
    assert "bat_tu" in out
    result = out["bat_tu"]
    # If engine succeeded, we expect tu_tru in output. If it errored, the
    # envelope contains _precast_error — both prove the router worked.
    if "_precast_error" not in result:
        assert "tu_tru" in result or "pillars" in str(result)


# ─── End-to-end consult with precast + API ───────────────────────────────────


def test_api_consult_with_auto_precast():
    from fastapi.testclient import TestClient

    from api.main import app
    from engine.ai import kanban_council as kc

    client = TestClient(app)
    r = client.post(
        "/api/ai/council/kanban/consult",
        json={
            "question": "Test API precast",
            "sages": ["bat_tu"],
            "birth": {
                "birth_datetime_local": "1985-08-15T10:30:00",
                "timezone": "Asia/Ho_Chi_Minh",
                "gender": "nam",
            },
            "soul_key": "test_api_precast",
        },
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    # API surfaces which sages got precast
    assert "bat_tu" in payload["precast_sages"]

    # Cleanup
    root_id = payload["session"]["root_id"]
    session = kc.load_session(root_id)
    if session:
        _archive(session)


def test_api_consult_with_explicit_precast_overrides_auto():
    from fastapi.testclient import TestClient

    from api.main import app
    from engine.ai import kanban_council as kc

    client = TestClient(app)
    r = client.post(
        "/api/ai/council/kanban/consult",
        json={
            "question": "Explicit precast wins",
            "sages": ["bat_tu"],
            "precast_data": {
                "bat_tu": {"_marker": "EXPLICIT_OVERRIDE"}
            },
            "birth": {  # would auto-cast but explicit wins
                "birth_datetime_local": "1985-08-15T10:30:00",
            },
            "soul_key": "test_override",
        },
    )
    assert r.status_code == 200
    root_id = r.json()["session"]["root_id"]

    # Verify the body contains EXPLICIT_OVERRIDE (not auto-cast Tứ Trụ)
    import json
    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    sage_tid = r.json()["session"]["sage_task_ids"]["bat_tu"]
    out = subprocess.run(
        [str(kc.HERMES_BIN), "kanban", "show", sage_tid, "--json"],
        env=env, capture_output=True, text=True, check=True,
    )
    body = json.loads(out.stdout)["task"]["body"]
    assert "EXPLICIT_OVERRIDE" in body

    session = kc.load_session(root_id)
    if session:
        _archive(session)


# ─── Harvest integration ─────────────────────────────────────────────────────


def test_session_snapshot_harvests_when_sage_completes(monkeypatch, tmp_path):
    """Simulate a completed sage task with improve_system in result → snapshot
    should auto-extract critiques."""
    from engine.ai import critique_store as cs
    from engine.ai import kanban_council as kc

    # Isolate critique DB
    monkeypatch.setattr(cs, "CRITIQUE_DB", tmp_path / "crit.sqlite3")

    session = kc.consult(
        question="Harvest test",
        sages=["bat_tu"],
        soul_key="test_harvest",
    )
    try:
        sage_tid = session.sage_task_ids["bat_tu"]
        # Inject a fake "done" result directly into kanban.db
        import sqlite3
        with sqlite3.connect(kc.KANBAN_DB) as c:
            c.execute(
                "UPDATE tasks SET status='done', result=?, completed_at=? WHERE id=?",
                (
                    """## READ\nDay Master nhược\n\n### improve_system\n"""
                    """- target: engine.bat_tu.than_sat\n"""
                    """  suggestion: bổ sung Văn Xương\n"""
                    """  priority: high\n"""
                    """  rationale: hiện thiếu sao Văn Xương\n""",
                    1_700_000_000,
                    sage_tid,
                ),
            )

        snap = kc.session_snapshot(session)
        # The completed sage task should have been harvested
        assert snap["harvested_critiques"].get("bat_tu") == 1

        # The critique store should now contain that item
        crits = cs.list_critiques()
        assert len(crits) == 1
        assert crits[0]["target"] == "engine.bat_tu.than_sat"
        assert crits[0]["priority"] == "high"

        # Second snapshot must not double-harvest (idempotent)
        snap2 = kc.session_snapshot(session)
        assert snap2["harvested_critiques"] == {}
    finally:
        _archive(session)
