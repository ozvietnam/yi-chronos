"""P0-4 — gunicorn.conf.py hợp lệ: đa worker + UvicornWorker (vá G3)."""
from __future__ import annotations

import runpy
from pathlib import Path

CONF = Path(__file__).resolve().parent.parent / "gunicorn.conf.py"


def _load(monkeypatch=None, env=None):
    import os
    for k, v in (env or {}).items():
        os.environ[k] = v
    try:
        return runpy.run_path(str(CONF))
    finally:
        for k in (env or {}):
            os.environ.pop(k, None)


def test_defaults_multi_worker_uvicorn():
    ns = _load()
    assert ns["worker_class"] == "uvicorn.workers.UvicornWorker"
    assert ns["workers"] >= 3                 # ≥3 → không còn single-worker (G3)
    assert ns["bind"] == "0.0.0.0:8000"
    assert ns["max_requests"] >= 1            # tái sinh worker chống rò RAM
    assert ns["graceful_timeout"] >= 1


def test_web_concurrency_env_override():
    ns = _load(env={"WEB_CONCURRENCY": "8"})
    assert ns["workers"] == 8


def test_uvicorn_worker_importable():
    import uvicorn.workers  # noqa: F401  — worker_class phải import được
