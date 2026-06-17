"""H3 — version contract (§5bis freshness).

AppChat pins `algoVersion` per cached reading and refetches when YI bumps it.
That only works if YI exposes a stable, lightweight version surface.
"""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_version_endpoint_shape():
    from api.main import app
    c = TestClient(app)
    r = c.get("/api/version")
    assert r.status_code == 200, r.text
    j = r.json()
    # Global engine version (reused from core.config, not invented).
    assert isinstance(j.get("algo_version"), str) and j["algo_version"]
    # Per-method versions so a single school can bump without touching others.
    assert "methods" in j and "tu_vi" in j["methods"] and "couple_match" in j["methods"]
    # Server time lets the client apply the TTL backstop.
    assert "server_time" in j


def test_algo_version_helper_is_method_specific():
    from engine.algo_version import algo_version, version_info
    base = version_info()["algo_version"]
    tv = algo_version("tu_vi")
    assert tv.startswith(base)
    assert algo_version("tu_vi") != algo_version("bat_tu")
    # Unknown method falls back to the base version (never crashes).
    assert algo_version("nope") == base
    assert algo_version(None) == base
