"""Shared pytest fixtures.

`as_owner` authenticates API requests as the owner. After the 2026-05/06 security
audits, many `/api/*` endpoints are gated (owner-only or login-required) via
`api.auth.get_current_user` / `require_user` / `require_owner`. Integration tests
that exercise those endpoints must present an owner identity. Apply per module with:

    pytestmark = pytest.mark.usefixtures("as_owner")

This patches the auth resolvers (not a real session) so the TestClient is treated
as the owner. There are intentionally no "guest is denied" tests that this would
break; if one is added, scope `as_owner` to the tests that need it instead.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def as_owner(monkeypatch):
    """Make all auth checks resolve to the owner for the duration of a test."""
    owner = {
        "user_id": 1,
        "email": "ceo@ngantin.vn",
        "role": "owner",
        "display_name": "Founder",
    }
    import api.auth as auth

    monkeypatch.setattr(auth, "get_current_user", lambda request: owner, raising=True)
    monkeypatch.setattr(auth, "require_user", lambda request: owner, raising=True)
    monkeypatch.setattr(auth, "require_owner", lambda request: owner, raising=True)
    return owner


@pytest.fixture
def force_mock_council(monkeypatch):
    """Force Council provider selection to Mock.

    Council orchestration tests verify LOGIC (rounds, synthesis, agent filtering),
    not LLM output. Since MiniMax-M3 became chủ lực (prefer_reasoning), an unguarded
    consult would fire real M3 reasoning calls → slow (~45s ea), paid, flaky. This
    pins both provider getters to Mock so the tests stay fast + deterministic.
    Provider-SELECTION logic is covered separately by a network-free unit test.
    """
    import engine.ai.council as council
    from engine.ai.registry import get_registry

    mock = get_registry().get("mock")
    monkeypatch.setattr(
        council, "_get_agent_provider",
        lambda agent_id, prefer_reasoning=False: (mock, "mock-v1"), raising=True,
    )
    monkeypatch.setattr(
        council, "_get_orchestrator_provider",
        lambda: (mock, "mock-v1"), raising=True,
    )
    return mock
