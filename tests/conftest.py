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
