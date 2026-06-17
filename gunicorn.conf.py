"""P0-4 — gunicorn config (đa worker + UvicornWorker) vá điểm chết G3.

Thay `uvicorn` 1 process (1 lõi, GIL, 1 request CPU-nặng block toàn server, crash =
downtime) bằng gunicorn quản N worker uvicorn. HA thật ở mốc lớn = nhiều instance
sau LB (≥3) — xem runbook P0-4; file này lo phần đa-worker mỗi instance.

Số worker: env WEB_CONCURRENCY, mặc định max(3, 2*cpu+1). Job dài (H5) KHÔNG chạy ở
web worker — đẩy sang Celery (P0-3) để không chiếm worker / timeout.
"""
import multiprocessing
import os

_cpu = multiprocessing.cpu_count()
workers = int(os.environ.get("WEB_CONCURRENCY", max(3, 2 * _cpu + 1)))
worker_class = "uvicorn.workers.UvicornWorker"
bind = os.environ.get("BIND", "0.0.0.0:8000")

# Timeout rộng cho request engine nặng (an sao/cast); job rất dài đã ở Celery.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = 30
keepalive = 5

# Tự tái sinh worker để chống rò bộ nhớ dần (jitter tránh restart đồng loạt).
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = 100

preload_app = False          # tránh chia sẻ kết nối DB/engine giữa worker (fork-safe)
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
