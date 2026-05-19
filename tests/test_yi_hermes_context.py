"""Tests for YI-Hermes system-level context (project manifest + founder profile)."""

from __future__ import annotations

import pytest


# ─── Founder detection ────────────────────────────────────────────────────────


def test_default_founder_keys_include_telegram_id():
    from engine.yi_hermes import get_founder_soul_keys

    keys = get_founder_soul_keys()
    assert "telegram:6452658353" in keys
    assert "_founder" in keys


def test_is_founder_recognizes_anh():
    from engine.yi_hermes import is_founder

    assert is_founder("telegram:6452658353")
    assert is_founder("_founder")
    assert not is_founder("telegram:99999999")
    assert not is_founder("random_user")
    assert not is_founder("")


def test_is_founder_respects_env_override(monkeypatch):
    from engine.yi_hermes import get_founder_soul_keys, is_founder

    monkeypatch.setenv("YI_HERMES_FOUNDER_SOUL_KEYS", "custom_id,another_id")
    # Need to bypass cache — call get_founder_soul_keys (not cached) directly
    keys = get_founder_soul_keys()
    assert "custom_id" in keys
    assert "another_id" in keys
    assert is_founder("custom_id")


# ─── Manifest + Founder file loading ──────────────────────────────────────────


def test_manifest_loads_canonical_content():
    from engine.yi_hermes import get_manifest

    manifest = get_manifest()
    assert manifest
    assert len(manifest) > 500
    # Spot-check canonical content
    assert "YI-CHRONOS" in manifest
    assert "trường phái" in manifest


def test_founder_profile_loads():
    from engine.yi_hermes import get_founder_profile

    profile = get_founder_profile()
    assert profile
    assert "Founder" in profile or "founder" in profile.lower()


# ─── Context assembly ─────────────────────────────────────────────────────────


def test_assemble_system_context_for_founder():
    from engine.yi_hermes import assemble_system_context

    msgs = assemble_system_context(soul_key="telegram:6452658353", query_hint="test")
    # Founder gets 3 blocks: manifest + founder + soul (memory empty)
    assert len(msgs) >= 3
    contents = [m["content"] for m in msgs]
    assert any("PROJECT YI-CHRONOS" in c for c in contents)
    assert any("FOUNDER" in c for c in contents)
    assert any("Soul" in c for c in contents)


def test_assemble_system_context_for_non_founder():
    from engine.yi_hermes import assemble_system_context

    msgs = assemble_system_context(soul_key="telegram:9999999", query_hint="test")
    contents = [m["content"] for m in msgs]
    # Non-founder gets manifest + soul (NO founder profile)
    assert any("PROJECT YI-CHRONOS" in c for c in contents)
    assert not any("FOUNDER" in c for c in contents)
    assert any("Soul" in c for c in contents)


def test_context_summary_for_founder():
    from engine.yi_hermes import context_summary

    summary = context_summary("telegram:6452658353")
    assert summary["is_founder"] is True
    assert summary["has_manifest"] is True
    assert summary["has_founder_profile"] is True
    assert summary["manifest_size_chars"] > 500


def test_context_summary_for_anon():
    from engine.yi_hermes import context_summary

    summary = context_summary("telegram:99999999")
    assert summary["is_founder"] is False
    assert summary["has_manifest"] is True
    assert summary["has_founder_profile"] is None  # not checked for non-founder


# ─── Manifest update + reload ────────────────────────────────────────────────


def test_update_manifest_persists_and_reloads():
    from engine.yi_hermes import get_manifest, update_manifest

    original = get_manifest()
    try:
        new_content = original + "\n\n## Test addendum (will be removed)\n"
        update_manifest(new_content)
        reloaded = get_manifest()
        assert "Test addendum" in reloaded
    finally:
        # Restore
        update_manifest(original)


# ─── API endpoints ───────────────────────────────────────────────────────────


def test_api_get_manifest():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/context/manifest")
    assert r.status_code == 200
    payload = r.json()
    assert payload["size_chars"] > 500
    assert "YI-CHRONOS" in payload["content"]


def test_api_get_founder():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/yi-hermes/context/founder")
    assert r.status_code == 200
    payload = r.json()
    assert payload["size_chars"] > 100
    assert "telegram:6452658353" in payload["founder_soul_keys"]


def test_api_context_summary():
    from fastapi.testclient import TestClient
    from api.main import app

    import urllib.parse
    client = TestClient(app)
    soul_key = urllib.parse.quote("telegram:6452658353", safe="")
    r = client.get(f"/api/yi-hermes/context/summary/{soul_key}")
    assert r.status_code == 200
    payload = r.json()["context"]
    assert payload["is_founder"] is True


def test_chat_for_founder_injects_founder_context():
    """LLM call for founder must include founder profile in system messages.

    We test the assemble_system_context output rather than mocking full LLM.
    """
    from engine.yi_hermes import assemble_system_context

    # Founder
    founder_msgs = assemble_system_context(soul_key="telegram:6452658353", query_hint="")
    founder_content = "\n".join(m["content"] for m in founder_msgs)
    assert "FOUNDER" in founder_content
    assert "anh" in founder_content  # founder profile uses "anh"

    # Non-founder
    other_msgs = assemble_system_context(soul_key="telegram:0", query_hint="")
    other_content = "\n".join(m["content"] for m in other_msgs)
    assert "FOUNDER" not in other_content
