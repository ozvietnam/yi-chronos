"""P0-5 — rate-limit (chống abuse đốt LLM / spam endpoint).

Sliding-window-log: đếm số sự kiện trong [now-window, now] thay vì bucket cố định
→ KHÔNG còn lỗ hổng burst 2× ở ranh giới cửa sổ (fixed-window cũ cho phép `limit`
cuối bucket N + `limit` đầu bucket N+1 trong ~1s).

Backend:
  - Redis (sorted set, chia sẻ đa worker/instance) nếu có — ĐÂY là đường prod.
  - Fallback in-memory per-process: CHỈ cho dev/test/1-worker. Ở prod đa-worker,
    fallback = limit × số worker (mỗi process đếm riêng) → coi Redis là BẮT BUỘC ở
    prod (đặt REDIS_URL). Lần đầu fallback có log cảnh báo.
"""
from __future__ import annotations

import itertools
import logging
import os
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

_REDIS_URL = (os.environ.get("REDIS_URL") or os.environ.get("CELERY_BROKER_URL")
              or "redis://localhost:6379/0")
_redis = None              # None=chưa thử · False=không có · client=có
_mem: dict[str, list[float]] = {}   # key → timestamps (giây) trong cửa sổ
_lock = threading.Lock()
_seq = itertools.count()   # đảm bảo member ZADD là duy nhất
_warned_fallback = False


def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis
            c = redis.Redis.from_url(_REDIS_URL, socket_connect_timeout=0.3,
                                     socket_timeout=0.3)
            c.ping()
            _redis = c
        except Exception:
            _redis = False
    return _redis or None


def _warn_fallback():
    global _warned_fallback
    if not _warned_fallback:
        _warned_fallback = True
        logger.warning("ratelimit: Redis không sẵn sàng → fallback in-memory "
                       "per-process. Ở prod đa-worker PHẢI đặt REDIS_URL.")


def allow(key: str, limit: int, window_sec: int = 60) -> bool:
    """True nếu còn quota cho `key` trong cửa sổ trượt `window_sec`; False nếu vượt."""
    if limit <= 0:
        return False
    now = time.time()
    cutoff = now - window_sec
    r = _get_redis()
    if r is not None:
        try:
            rk = f"rl:{key}"
            pipe = r.pipeline()
            pipe.zremrangebyscore(rk, 0, cutoff)         # bỏ sự kiện ngoài cửa sổ
            pipe.zadd(rk, {f"{now}:{next(_seq)}": now})  # ghi sự kiện hiện tại
            pipe.zcard(rk)                               # đếm trong cửa sổ
            pipe.expire(rk, window_sec + 1)
            _, _, n, _ = pipe.execute()
            return int(n) <= limit
        except Exception:
            pass  # Redis lỗi giữa chừng → fallback
    _warn_fallback()
    with _lock:
        dq = _mem.setdefault(key, [])
        i = 0
        while i < len(dq) and dq[i] < cutoff:
            i += 1
        if i:
            del dq[:i]
        dq.append(now)
        return len(dq) <= limit


def remaining(key: str, limit: int, window_sec: int = 60) -> int:
    """Số lượt còn lại trong cửa sổ trượt hiện tại (xấp xỉ; cho UI/headers)."""
    now = time.time()
    cutoff = now - window_sec
    r = _get_redis()
    if r is not None:
        try:
            rk = f"rl:{key}"
            r.zremrangebyscore(rk, 0, cutoff)
            used = int(r.zcard(rk) or 0)
            return max(0, limit - used)
        except Exception:
            pass
    with _lock:
        dq = _mem.get(key, [])
        used = sum(1 for t in dq if t >= cutoff)
    return max(0, limit - used)


def reset(key: Optional[str] = None) -> None:
    """Dọn bộ đếm in-memory (chủ yếu cho test)."""
    with _lock:
        if key is None:
            _mem.clear()
        else:
            for k in [k for k in _mem if k.startswith(key)]:
                _mem.pop(k, None)
