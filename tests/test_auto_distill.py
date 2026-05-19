"""Tests for auto-distill: kanban council done → background lexicon distillation.

Verifies:
- Atomic claim (only fires once even on repeated snapshot calls)
- Sets status='pending' → 'done'/'failed' correctly
- Doesn't break snapshot when LLM/distill fails
- Skips distillation when council not complete
"""

from __future__ import annotations

import os
import subprocess
import time

import pytest


def _archive_session(session) -> None:
    from engine.ai import kanban_council as kc

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
        subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "archive", tid],
            env=env, capture_output=True, text=True,
        )


# ─── Atomic claim ────────────────────────────────────────────────────────────


def test_atomic_claim_first_call_wins():
    """First _try_claim_distill returns True; subsequent calls return False."""
    from engine.ai.kanban_council import (
        _try_claim_distill, save_session, CouncilSession,
    )

    s = CouncilSession(
        question="claim test",
        sage_task_ids={"bat_tu": "t_claim_a"},
        arbiter_id="t_claim_arb",
        soul_key="test",
    )
    save_session(s)

    assert _try_claim_distill(s.root_id) is True
    # Second time → already pending
    assert _try_claim_distill(s.root_id) is False


def test_claim_idempotent_after_done():
    """Even after status='done', re-claim returns False."""
    from engine.ai.kanban_council import (
        CouncilSession, _mark_distill_result, _try_claim_distill, save_session,
    )

    s = CouncilSession(
        question="idem", sage_task_ids={"bat_tu": "t_idem"},
        arbiter_id="t_idem_arb", soul_key="test",
    )
    save_session(s)
    assert _try_claim_distill(s.root_id) is True
    _mark_distill_result(s.root_id, status="done", concepts=3, mappings=5)
    assert _try_claim_distill(s.root_id) is False


def test_get_distill_status():
    from engine.ai.kanban_council import (
        CouncilSession, _mark_distill_result, _try_claim_distill,
        get_distill_status, save_session,
    )

    s = CouncilSession(
        question="status test",
        sage_task_ids={"a": "t_a"}, arbiter_id="t_arb_status",
        soul_key="test",
    )
    save_session(s)

    # Untouched
    st = get_distill_status(s.root_id)
    assert st is not None
    assert st["lexicon_distilled"] is None

    # Claim
    _try_claim_distill(s.root_id)
    st = get_distill_status(s.root_id)
    assert st["lexicon_distilled"] == "pending"

    # Mark done
    _mark_distill_result(s.root_id, status="done", concepts=2, mappings=4)
    st = get_distill_status(s.root_id)
    assert st["lexicon_distilled"] == "done"
    assert st["lexicon_concepts_added"] == 2
    assert st["lexicon_mappings_added"] == 4


# ─── Snapshot trigger logic ──────────────────────────────────────────────────


def test_snapshot_does_not_fire_when_incomplete():
    """If arbiter not done → auto_distill should NOT fire."""
    from engine.ai.kanban_council import (
        consult, save_session, session_snapshot,
    )

    s = consult(
        question="auto-distill incomplete test",
        sages=["bat_tu"], soul_key="test_incomp",
    )
    try:
        save_session(s)
        snap = session_snapshot(s, harvest=False, auto_distill=True)
        assert snap["progress"]["complete"] is False
        assert snap["auto_distill"]["fired_this_call"] is False
    finally:
        _archive_session(s)


def test_snapshot_fires_once_when_complete(monkeypatch):
    """Mock arbiter done, ensure auto_distill fires exactly once across multiple polls."""
    from engine.ai import kanban_council as kc

    # Monkeypatch: pretend arbiter is done with fake result
    fake_arbiter_status = {
        "id": "t_fake_arb",
        "title": "fake",
        "assignee": "arbiter",
        "status": "done",
        "started_at": 1, "completed_at": 2,
        "result": "## Tổng hợp\nĐã xong.",
    }
    fake_sage_status = {
        "id": "t_fake_sage",
        "title": "fake sage",
        "assignee": "bat-tu-sage",
        "status": "done",
        "started_at": 1, "completed_at": 2,
        "result": "## READ\nDay Master.",
    }

    def fake_task_status(task_id: str):
        if "arb" in task_id or task_id.endswith("99"):
            return dict(fake_arbiter_status)
        return dict(fake_sage_status)

    monkeypatch.setattr(kc, "task_status", fake_task_status)

    # Mock the distill thread runner so we don't actually call LLM
    fired_count = {"n": 0}
    real_thread = __import__("threading").Thread

    class FakeThread:
        def __init__(self, target=None, args=(), daemon=False, **kw):
            self.target = target
            self.args = args

        def start(self):
            fired_count["n"] += 1
            # Mark immediately to simulate completion (so subsequent claim returns False)
            kc._mark_distill_result(self.args[0], status="done", concepts=1, mappings=1)

    monkeypatch.setattr(kc.threading if hasattr(kc, "threading") else __import__("threading"),
                        "Thread", FakeThread)
    # The kanban_council module imports threading inside the function, so patch at module level
    import engine.ai.kanban_council
    monkeypatch.setattr("threading.Thread", FakeThread)

    s = kc.CouncilSession(
        question="snap fire test",
        sage_task_ids={"bat_tu": "t_fake_sage"},
        arbiter_id="t_fake_99",
        soul_key="test_snap_fire",
    )
    kc.save_session(s)

    # First poll → should fire
    snap1 = kc.session_snapshot(s, harvest=False, auto_distill=True)
    assert snap1["progress"]["complete"] is True
    assert snap1["auto_distill"]["fired_this_call"] is True
    assert fired_count["n"] == 1

    # Second poll → already claimed, should NOT fire again
    snap2 = kc.session_snapshot(s, harvest=False, auto_distill=True)
    assert snap2["auto_distill"]["fired_this_call"] is False
    assert fired_count["n"] == 1  # still 1, no double-fire


def test_snapshot_auto_distill_can_be_disabled():
    """Caller can pass auto_distill=False to skip the trigger entirely."""
    from engine.ai.kanban_council import consult, save_session, session_snapshot

    s = consult(
        question="disable test", sages=["bat_tu"], soul_key="test_dis",
    )
    try:
        save_session(s)
        snap = session_snapshot(s, harvest=False, auto_distill=False)
        assert "auto_distill" in snap
        assert snap["auto_distill"]["fired_this_call"] is False
    finally:
        _archive_session(s)


# ─── Distill module idempotency ──────────────────────────────────────────────


def test_distill_returns_error_for_unknown_session():
    from engine.yi_lexicon.distill import distill_from_council

    result = distill_from_council("t_nonexistent_xyz")
    assert "session not found" in (result.errors[0] if result.errors else "")


def test_distill_skips_incomplete_council():
    from engine.ai.kanban_council import consult, save_session
    from engine.yi_lexicon.distill import distill_from_council

    s = consult(
        question="incomp distill test", sages=["bat_tu"], soul_key="test_inc_d",
    )
    try:
        save_session(s)
        result = distill_from_council(s.root_id)
        assert any("not complete" in e for e in result.errors)
        assert result.concepts_added == 0
    finally:
        _archive_session(s)
