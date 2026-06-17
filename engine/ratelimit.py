"""P0-5 — rate-limit (chống abuse đốt LLM / spam endpoint).

Fixed-window counter: Redis (đa worker/instance dùng chung) nếu có; nếu không →
fallback in-memory per-process (đủ cho dev/test/1 worker). API layer gọi `allow()`
trước endpoint tốn LLM (H5/H6) + hạn mức/ngày theo gói.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Optional

_REDIS_URL = (os.environ.get("REDIS_URL") or os.environ.get("CELERY_BROKER_URL")
              or "redis://localhost:6379/0")
_redis = None              # None=chưa thử · False=không có · client=có
_mem: dict[str, tuple[int, int]] = {}
_lock = threading.Lock()


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


def allow(key: str, limit: int, window_sec: int = 60) -> bool:
    """True nếu còn quota cho `key` trong cửa sổ `window_sec`; False nếu vượt."""
    if limit <= 0:
        return False
    bucket = int(time.time()) // window_sec
    r = _get_redis()
    if r is not None:
        try:
            rk = f"rl:{key}:{bucket}"
            n = r.incr(rk)
            if n == 1:
                r.expire(rk, window_sec)
            return n <= limit
        except Exception:
            pass  # Redis lỗi giữa chừng → fallback
    with _lock:
        cnt, b = _mem.get(key, (0, bucket))
        if b != bucket:
            cnt, b = 0, bucket
        cnt += 1
        _mem[key] = (cnt, b)
        return cnt <= limit


def remaining(key: str, limit: int, window_sec: int = 60) -> int:
    """Số lượt còn lại trong cửa sổ hiện tại (xấp xỉ; cho UI/headers)."""
    bucket = int(time.time()) // window_sec
    r = _get_redis()
    if r is not None:
        try:
            used = int(r.get(f"rl:{key}:{bucket}") or 0)
            return max(0, limit - used)
        except Exception:
            pass
    cnt, b = _mem.get(key, (0, bucket))
    used = cnt if b == bucket else 0
    return max(0, limit - used)


def reset(key: Optional[str] = None) -> None:
    """Dọn bộ đếm in-memory (chủ yếu cho test)."""
    with _lock:
        if key is None:
            _mem.clear()
        else:
            for k in [k for k in _mem if k.startswith(key)]:
                _mem.pop(k, None)
