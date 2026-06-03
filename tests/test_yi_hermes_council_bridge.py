"""Tests for YI-Hermes chat → kanban council auto-routing."""

from __future__ import annotations

import os
import subprocess

import pytest

# /api/yi-hermes/chat is login-gated; council routing also needs the hermes binary.
pytestmark = pytest.mark.usefixtures("as_owner")


def _archive_session(session) -> None:
    from engine.ai import kanban_council as kc

    env = os.environ.copy()
    env["HERMES_HOME"] = str(kc.HERMES_HOME)
    for tid in list(session.sage_task_ids.values()) + [session.arbiter_id]:
        subprocess.run(
            [str(kc.HERMES_BIN), "kanban", "archive", tid],
            env=env, capture_output=True, text=True,
        )


# ─── Intent detection ────────────────────────────────────────────────────────


def test_deep_question_auto_routes_to_council():
    from engine.yi_hermes.chat import _detect_intent

    # Career
    assert _detect_intent("Năm sau em có nên đổi việc không?") == "route_to_council"
    # Marriage
    assert _detect_intent("Hôn nhân của em ra sao trong 2026?") == "route_to_council"
    # Finance
    assert _detect_intent("Tài lộc đầu tư cuối năm thế nào?") == "route_to_council"
    # Destiny
    assert _detect_intent("Đời em sẽ thăng trầm ra sao?") == "route_to_council"


def test_short_deep_keyword_doesnt_trigger():
    """A bare keyword without question shape should fall through (e.g. glossary)."""
    from engine.yi_hermes.chat import _detect_intent

    # 'Đại vận' alone is just a term lookup
    assert _detect_intent("Đại vận") != "route_to_council"


def test_glossary_still_wins_short_queries():
    from engine.yi_hermes.chat import _detect_intent

    # Term lookup intent for short term-shaped queries
    assert _detect_intent("Dụng Thần là gì?") == "explain_term"


# ─── Birth extraction ────────────────────────────────────────────────────────


def test_extract_birth_from_chart_data_excerpt():
    from engine.yi_hermes.chat import HermesChat, HermesContext

    ctx = HermesContext(
        chart_data_excerpt={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "gender": "nam",
        },
    )
    birth = HermesChat._extract_birth_from_context(ctx)
    assert birth is not None
    assert birth["birth_datetime_local"] == "1985-08-15T10:30:00"
    assert birth["gender"] == "nam"


def test_extract_birth_from_active_person_birth():
    from engine.yi_hermes.chat import HermesChat, HermesContext

    ctx = HermesContext(active_person_birth="1985-08-15 10:30", user_gender="nam")
    birth = HermesChat._extract_birth_from_context(ctx)
    assert birth is not None
    assert "1985" in birth["birth_datetime_local"]


def test_extract_birth_returns_none_when_missing():
    from engine.yi_hermes.chat import HermesChat, HermesContext

    ctx = HermesContext()  # all defaults, no birth
    assert HermesChat._extract_birth_from_context(ctx) is None


# ─── Chat → council end-to-end ───────────────────────────────────────────────


def test_chat_route_to_council_spawns_session_with_birth():
    from engine.ai.kanban_council import load_session
    from engine.yi_hermes.chat import HermesChat, HermesContext

    chat = HermesChat()
    ctx = HermesContext(
        active_person_id="test_chat_council_1",
        active_person_name="Test User",
        chart_data_excerpt={
            "birth_datetime_local": "1985-08-15T10:30:00",
            "gender": "nam",
        },
    )
    reply = chat.send(
        user_message="Sự nghiệp năm 2026 của em ra sao? Có nên chuyển hướng?",
        context=ctx,
    )

    try:
        assert reply["intent"] == "route_to_council"
        assert "council_root_id" in reply
        assert reply["council_sages"]  # at least one sage
        assert "Hội Đồng" in reply["content"]

        # Session must be persisted
        session = load_session(reply["council_root_id"])
        assert session is not None
        # With birth data, at least one sage should have precast
        assert reply["council_precast_sages"]
    finally:
        session = load_session(reply["council_root_id"])
        if session:
            _archive_session(session)


def test_chat_route_to_council_works_without_birth():
    """Chat must still spawn council even when birth is missing — sage will
    annotate engine_gap rather than fail."""
    from engine.ai.kanban_council import load_session
    from engine.yi_hermes.chat import HermesChat, HermesContext

    chat = HermesChat()
    ctx = HermesContext(active_person_id="test_chat_no_birth")
    reply = chat.send(
        user_message="Tài lộc đầu tư của em năm tới như thế nào?",
        context=ctx,
    )

    try:
        assert reply["intent"] == "route_to_council"
        assert reply["council_root_id"]
        # Should warn about missing birth in reply
        assert "engine_gap" in reply["content"] or "chưa có dữ liệu sinh" in reply["content"]
    finally:
        session = load_session(reply["council_root_id"])
        if session:
            _archive_session(session)


def test_poll_council_returns_snapshot():
    from engine.yi_hermes.chat import HermesChat, HermesContext

    chat = HermesChat()
    ctx = HermesContext(
        active_person_id="test_poll_1",
        chart_data_excerpt={"birth_datetime_local": "1985-08-15T10:30:00"},
    )
    reply = chat.send(
        user_message="Hôn nhân năm 2026 của em ra sao?", context=ctx
    )
    root_id = reply["council_root_id"]
    try:
        polled = chat.poll_council(root_id)
        assert polled["status"] == "ok"
        snap = polled["snapshot"]
        assert "progress" in snap
        assert snap["session"]["root_id"] == root_id
    finally:
        from engine.ai.kanban_council import load_session
        session = load_session(root_id)
        if session:
            _archive_session(session)


def test_poll_council_returns_not_found_for_bad_id():
    from engine.yi_hermes.chat import HermesChat

    chat = HermesChat()
    result = chat.poll_council("t_nonexistent_id")
    assert result["status"] == "not_found"


# ─── API integration: /api/yi-hermes/chat triggers council ──────────────────


def test_api_yi_hermes_chat_routes_deep_question():
    from fastapi.testclient import TestClient

    from api.main import app
    from engine.ai.kanban_council import load_session

    client = TestClient(app)
    r = client.post(
        "/api/yi-hermes/chat",
        json={
            "user_message": "Sự nghiệp 2026 nên đi hướng nào?",
            "context": {
                "active_person_id": "api_council_user",
                "active_person_name": "API Test",
                "chart_data_excerpt": {
                    "birth_datetime_local": "1985-08-15T10:30:00",
                    "gender": "nam",
                },
            },
        },
    )
    assert r.status_code == 200
    payload = r.json()
    response = payload.get("response", {})
    assert response.get("intent") == "route_to_council"
    assert "council_root_id" in response

    # Cleanup
    session = load_session(response["council_root_id"])
    if session:
        _archive_session(session)
