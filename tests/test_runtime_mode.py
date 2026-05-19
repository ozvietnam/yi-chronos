"""Tests for runtime mode flags (EXPERIMENTAL_MODE / COMMUNITY_RELEASE)."""

from __future__ import annotations

import importlib
import os

import pytest


@pytest.fixture
def reload_config():
    """Reload core.config after mutating env."""
    import core.config

    def _reload():
        return importlib.reload(core.config)
    return _reload


def test_default_experimental_mode_on(reload_config):
    for k in ("YI_EXPERIMENTAL_MODE", "YI_COMMUNITY_RELEASE", "YI_LOCKED_PROFILE_HASH"):
        os.environ.pop(k, None)
    cfg = reload_config()
    assert cfg.EXPERIMENTAL_MODE is True
    assert cfg.COMMUNITY_RELEASE is False
    assert cfg.LOCKED_PROFILE_HASH is None


def test_gps_enabled_in_experimental_no_lock(reload_config):
    os.environ["YI_EXPERIMENTAL_MODE"] = "true"
    os.environ.pop("YI_LOCKED_PROFILE_HASH", None)
    cfg = reload_config()
    assert cfg.gps_enabled_for("any-hash") is True
    assert cfg.gps_enabled_for(None) is True


def test_gps_locked_to_one_profile(reload_config):
    os.environ["YI_EXPERIMENTAL_MODE"] = "true"
    os.environ["YI_LOCKED_PROFILE_HASH"] = "ceo-hash"
    cfg = reload_config()
    assert cfg.gps_enabled_for("ceo-hash") is True
    assert cfg.gps_enabled_for("other-hash") is False
    assert cfg.gps_enabled_for(None) is False


def test_community_release_requires_experimental_off(reload_config):
    os.environ["YI_EXPERIMENTAL_MODE"] = "false"
    os.environ["YI_COMMUNITY_RELEASE"] = "true"
    os.environ.pop("YI_LOCKED_PROFILE_HASH", None)
    cfg = reload_config()
    assert cfg.gps_enabled_for("any") is True


def test_neither_flag_disables_gps(reload_config):
    os.environ["YI_EXPERIMENTAL_MODE"] = "false"
    os.environ["YI_COMMUNITY_RELEASE"] = "false"
    os.environ.pop("YI_LOCKED_PROFILE_HASH", None)
    cfg = reload_config()
    assert cfg.gps_enabled_for("any") is False


def test_banner_includes_mode_and_message(reload_config):
    os.environ["YI_EXPERIMENTAL_MODE"] = "true"
    cfg = reload_config()
    banner = cfg.runtime_mode_banner()
    assert banner["mode"] == "EXPERIMENTAL"
    assert "thử nghiệm" in banner["message"]
    assert "community_release" in banner


def teardown_module(_):
    """Reset env so subsequent suites see defaults."""
    for k in ("YI_EXPERIMENTAL_MODE", "YI_COMMUNITY_RELEASE", "YI_LOCKED_PROFILE_HASH"):
        os.environ.pop(k, None)
    import core.config
    importlib.reload(core.config)
