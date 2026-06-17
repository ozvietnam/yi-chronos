"""P0-3 — task found, đúng tên/queue. Logic nghiệp vụ thật đến ở các issue sau:
  - yi.deepread.*  → H5 (#38, yi-chronos)
  - yi.hermes.*    → H6 (#39)
  - yi.digest.*    → H7 (#40)
  - yi.compat.*    → cụm D precompute (gieo duyên)

P0-3 chỉ dựng ỐNG (plumbing): app + routing + beat + task mẫu chạy được. Mỗi task
nghiệp vụ là wrapper mỏng sẽ gọi engine tương ứng khi triển khai.
"""
from __future__ import annotations

import logging

from engine.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="yi.ping")
def ping(echo: str = "pong") -> dict:
    """Health task — kiểm tra worker + broker chạy."""
    return {"ok": True, "echo": echo}


@celery_app.task(name="yi.digest.weekly_tick", bind=True, max_retries=3)
def weekly_digest_tick(self) -> dict:
    """H7 (#40) — quét cái MỚI/user gói tháng → notifyUser FCM. P0-3: no-op."""
    logger.info("weekly_digest_tick: plumbing only (H7 #40 chưa triển khai logic)")
    return {"status": "noop", "stage": "P0-3 plumbing", "see": "issue #40"}


@celery_app.task(name="yi.compat.nightly_precompute", bind=True, max_retries=3)
def nightly_compat_precompute(self) -> dict:
    """Cụm D — precompute yiMatches cho user active. P0-3: no-op."""
    logger.info("nightly_compat_precompute: plumbing only (cụm D chưa triển khai)")
    return {"status": "noop", "stage": "P0-3 plumbing"}


@celery_app.task(name="yi.deepread.run", bind=True, max_retries=0,
                 acks_late=False, queue="q_deepread")
def deepread_run(self, *, firebase_uid: str, person_key: str = "self") -> dict:
    """H5 (#38) — luận sâu DeepSeek async. Gọi orchestration (gating + ngân sách +
    sinh + lưu lịch sử + consume). Heavy LLM → chạy ở worker q_deepread.

    AT-MOST-ONCE (acks_late=False + max_retries=0): orchestration KHÔNG idempotent
    (mỗi lần chạy = 1 lần gọi LLM tốn tiền + 1 lần trừ lượt). Nếu worker crash giữa
    chừng → job mất, KHÔNG redeliver → tránh double-charge. User gọi lại nếu cần."""
    from engine.deep_reading import run_deep_reading
    return run_deep_reading(firebase_uid, person_key)
