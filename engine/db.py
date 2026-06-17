"""P0 data layer — SQLAlchemy engine + RLS session (Postgres prod / SQLite dev).

Non-breaking: đây là tầng MỚI dùng cho lộ trình migrate sang Postgres. Code cũ
(`sqlite3.connect` trong api/auth.py…) vẫn chạy cho tới khi từng module được
chuyển qua tầng này (các PR P0 kế tiếp).

Chọn driver qua env `DATABASE_URL`:
  - chưa set            → SQLite file (dev/test) — KHÔNG có RLS (SQLite không hỗ trợ).
  - postgresql+psycopg://… → Postgres (prod, in-VN) — RLS bật theo GUC phiên.

RLS (chỉ Postgres): mỗi phiên đặt 2 GUC (xem db/postgres/schema.sql):
  - app.current_uid  : id user đang thao tác (deny-by-default nếu không set).
  - app.service_mode : 'on' = bypass cho luồng service-to-service (bridge)/owner.
Dùng `session_scope(uid=...)` cho thao tác theo user, `session_scope(service=True)`
cho luồng bridge (Cloud Functions) / cron / admin.

Cấu hình pool hợp với PgBouncer (transaction mode): pool_pre_ping + pool nhỏ.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Dev fallback: 1 file SQLite hợp nhất (chỉ cho local/test, KHÔNG phải prod).
_DEFAULT_SQLITE = Path(__file__).resolve().parent.parent / "data" / "yi_users" / "yi_unified.sqlite3"


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url
    _DEFAULT_SQLITE.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{_DEFAULT_SQLITE}"


def is_postgres(url: Optional[str] = None) -> bool:
    return (url or database_url()).startswith(("postgresql", "postgres://"))


@lru_cache(maxsize=8)
def get_engine(url: Optional[str] = None) -> Engine:
    url = url or database_url()
    if is_postgres(url):
        # pool nhỏ + pre_ping: PgBouncer (transaction mode) lo gom kết nối thật,
        # SQLAlchemy không cần pool to. pre_ping tránh kết nối chết.
        return create_engine(
            url, pool_pre_ping=True, pool_size=5, max_overflow=10,
            future=True,
        )
    # SQLite dev/test
    return create_engine(url, future=True, connect_args={"check_same_thread": False})


@contextmanager
def session_scope(uid: Optional[str | int] = None, *, service: bool = False) -> Iterator:
    """Mở 1 transaction + (nếu Postgres) đặt GUC RLS cho đúng phạm vi.

    - service=True → bypass RLS (bridge/cron/admin).
    - uid set      → chỉ thấy/ghi dữ liệu của user đó.
    - cả hai unset → trên Postgres = deny-by-default (an toàn).
    SQLite: GUC bị bỏ qua (không có RLS) — chỉ dùng dev/test.
    """
    engine = get_engine()
    with engine.begin() as conn:
        if is_postgres():
            # set_config(..., is_local=true) = SET LOCAL nhưng nhận tham số bind
            # (SET LOCAL thuần KHÔNG nhận placeholder).
            if service:
                conn.execute(text("SELECT set_config('app.service_mode','on',true)"))
            if uid is not None:
                conn.execute(text("SELECT set_config('app.current_uid', :u, true)"),
                             {"u": str(uid)})
        yield conn


def apply_schema(conn, schema_path: Optional[Path] = None) -> None:
    """Chạy DDL schema Postgres (idempotent). Chỉ dùng cho Postgres — SQLite
    không hiểu RLS/JSONB/GUC. Prod nên chạy bằng psql/migration tool (runbook);
    hàm này tiện cho test/CI."""
    schema_path = schema_path or (
        Path(__file__).resolve().parent.parent / "db" / "postgres" / "schema.sql"
    )
    sql = schema_path.read_text(encoding="utf-8")
    # exec_driver_sql gửi nguyên script (DO $$, function, policy) xuống psycopg3.
    conn.exec_driver_sql(sql)


def healthcheck() -> dict:
    """Trả trạng thái kết nối + driver — cho /api/health mở rộng sau."""
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"db": "ok", "driver": "postgres" if is_postgres() else "sqlite"}
    except Exception as e:  # pragma: no cover
        return {"db": "error", "driver": "postgres" if is_postgres() else "sqlite",
                "detail": str(e)[:200]}
