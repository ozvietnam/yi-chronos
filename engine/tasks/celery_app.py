"""P0-3 — Celery app (broker/backend Redis) + queue routing + Beat schedule.

Chọn Celery (KHÔNG arq — arq maintenance-only từ 02/2025; master plan §1). Đây là
backbone hàng đợi cho:
  - q_deepread : H5 luận sâu DeepSeek (job dài, ít concurrency, timeout cao)
  - q_hermes   : H6 Hermes (RAG/LLM)
  - q_digest   : H7 digest tuần (fan-out FCM)
  - q_compat   : cron đêm precompute yiMatches (cụm D gieo duyên)
Beat lo CRON (digest tuần + precompute đêm).

Broker/backend lấy từ env (mặc định redis local). Import KHÔNG kết nối broker
(Celery lazy) → an toàn import trong test/app; chỉ worker/beat + .delay() mới nối.
"""
from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", BROKER_URL)

celery_app = Celery(
    "yi",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["engine.tasks.jobs"],
)

celery_app.conf.update(
    task_default_queue="q_default",
    # Route theo prefix tên task → đúng queue (worker scale độc lập từng queue).
    task_routes={
        "yi.deepread.*": {"queue": "q_deepread"},
        "yi.hermes.*": {"queue": "q_hermes"},
        "yi.digest.*": {"queue": "q_digest"},
        "yi.compat.*": {"queue": "q_compat"},
    },
    # Job dài (H5) → ack sau khi xong + fair dispatch (không prefetch ồ ạt).
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=False,
    result_expires=24 * 3600,
    # CRON (Beat). Logic thật của các task ở H7/#40 (digest) + cụm D/#38 (compat).
    beat_schedule={
        "weekly-digest": {            # H7 — thứ Hai 06:00 (gói trả phí)
            "task": "yi.digest.weekly_tick",
            "schedule": crontab(hour=6, minute=0, day_of_week="mon"),
        },
        "nightly-compat-precompute": {  # cụm D — gắn cùng auto-sync 23:30
            "task": "yi.compat.nightly_precompute",
            "schedule": crontab(hour=23, minute=30),
        },
    },
)
