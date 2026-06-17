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

# Timeout cho request engine nặng. Mặc định 180s: một số endpoint GỌI LLM ĐỒNG BỘ
# (quiz tìm giờ sinh / luận giải dùng MiniMax|DeepSeek) có thể vượt 120s → gunicorn
# giết worker giữa response = 502 + rớt request khác trên worker đó. Job RẤT dài (H5
# luận sâu) đã đẩy sang Celery. TODO: chuyển nốt các endpoint LLM-inline sang async
# queue để có thể hạ timeout này về ~60s (worker không bị giữ lâu).
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "180"))
graceful_timeout = 30
keepalive = 5

# Tự tái sinh worker để chống rò bộ nhớ dần (jitter tránh restart đồng loạt).
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = 100

preload_app = False          # tránh chia sẻ kết nối DB/engine giữa worker (fork-safe)
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
