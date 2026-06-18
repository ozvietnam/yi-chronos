"""P0-3 — Celery app/queue/Beat plumbing. Chạy task ở EAGER mode (in-process,
KHÔNG cần Redis daemon) → verify task + routing + schedule không cần broker."""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def eager():
    from engine.tasks.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False


def test_ping_runs_eager():
    from engine.tasks.jobs import ping
    r = ping.delay("hi").get()
    assert r == {"ok": True, "echo": "hi"}


def test_queue_routing_configured():
    from engine.tasks.celery_app import celery_app
    routes = celery_app.conf.task_routes
    assert routes["yi.deepread.*"]["queue"] == "q_deepread"
    assert routes["yi.hermes.*"]["queue"] == "q_hermes"
    assert routes["yi.digest.*"]["queue"] == "q_digest"
    assert routes["yi.compat.*"]["queue"] == "q_compat"


def test_beat_schedule_has_cron_jobs():
    from engine.tasks.celery_app import celery_app
    sched = celery_app.conf.beat_schedule
    assert sched["weekly-digest"]["task"] == "yi.digest.weekly_tick"
    assert sched["nightly-compat-precompute"]["task"] == "yi.compat.nightly_precompute"


def test_tasks_registered_with_names():
    from engine.tasks.celery_app import celery_app
    import engine.tasks.jobs  # noqa: F401 — đăng ký task
    names = set(celery_app.tasks.keys())
    for n in ("yi.ping", "yi.digest.weekly_tick",
              "yi.compat.nightly_precompute", "yi.deepread.run"):
        assert n in names


def test_long_job_config_for_deepread():
    # Job dài cần ack-late + fair dispatch (không prefetch ồ ạt).
    from engine.tasks.celery_app import celery_app
    assert celery_app.conf.task_acks_late is True
    assert celery_app.conf.worker_prefetch_multiplier == 1


def test_stub_tasks_noop_eager():
    # nightly_compat vẫn plumbing (cụm D chưa làm). weekly_digest (H7) + deepread (H5)
    # đã chạy thật — kiểm ở tests/test_digest.py + test_deep_reading.py.
    from engine.tasks.jobs import nightly_compat_precompute
    assert nightly_compat_precompute.delay().get()["status"] == "noop"
