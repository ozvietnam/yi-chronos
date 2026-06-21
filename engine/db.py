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

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

# Dev fallback: 1 file SQLite hợp nhất (chỉ cho local/test, KHÔNG phải prod).
# Dev fallback: store user hiện tại (users.sqlite3) — để các module được chuyển
# sang engine.db vẫn đọc đúng dữ liệu cũ trên dev (non-breaking). Prod set DATABASE_URL
# → Postgres hợp nhất. (memory.sqlite3 là file riêng, chuyển ở PR sau.)
_DEFAULT_SQLITE = Path(__file__).resolve().parent.parent / "data" / "yi_users" / "users.sqlite3"


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
    eng = create_engine(url, future=True, connect_args={"check_same_thread": False})

    # P1 (review 2026-06-21): mỗi connection SQLite bật WAL + busy_timeout + synchronous
    # =NORMAL (concurrency đa-worker). WAL persistent → cũng giúp raw connect cùng file.
    @event.listens_for(eng, "connect")
    def _sqlite_pragmas(dbapi_con, _rec):  # noqa: ANN001
        cur = dbapi_con.cursor()
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.execute("PRAGMA busy_timeout=5000")
        cur.close()

    return eng


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


# ─── SQLite-compat adapter (cho migrate module lớn như auth.py với diff nhỏ) ──
# Giữ NGUYÊN văn phong sqlite3 (? placeholder, .execute().fetchone(), .lastrowid,
# .commit(), .close()) nhưng chạy trên engine.db (SQLite/Postgres). RETURNING tự
# thêm cho INSERT để có lastrowid trên cả 2 driver.
import re as _re

# pk dùng cho RETURNING theo bảng (mặc định 'id'; None = không có serial pk).
_TABLE_PK = {"users": "user_id", "sessions": None, "audit_log": "id"}


def _qmark_to_named(sql: str):
    """'... ?, ? ...' → '... :p0, :p1 ...' + tên tham số theo thứ tự."""
    idx = 0
    names: list[str] = []

    def _repl(_m):
        nonlocal idx
        n = f"p{idx}"
        names.append(n)
        idx += 1
        return f":{n}"

    return _re.sub(r"\?", _repl, sql), names


def _table_of_insert(sql: str) -> Optional[str]:
    m = _re.search(r"insert\s+into\s+([a-zA-Z_][\w]*)", sql, _re.IGNORECASE)
    return m.group(1) if m else None


class _CompatResult:
    def __init__(self, rows):
        self._rows = rows

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class CompatConnection:
    """Wrapper kiểu sqlite3 trên 1 SQLAlchemy connection (1 transaction)."""

    def __init__(self, engine: Engine, *, service: bool = True):
        self._sa = engine.connect()
        self._txn = self._sa.begin()
        self._pg = is_postgres()
        self._service = service
        self.lastrowid = None
        self._apply_guc()

    def _apply_guc(self):
        if self._pg and self._service:
            self._sa.execute(text("SELECT set_config('app.service_mode','on',true)"))

    def execute(self, sql: str, params=()):
        named, names = _qmark_to_named(sql)
        mapping = {names[i]: v for i, v in enumerate(params)} if params else {}
        head = sql.lstrip()[:6].upper()
        if head == "INSERT" and "RETURNING" not in sql.upper():
            tbl = _table_of_insert(sql)
            pk = _TABLE_PK.get(tbl, "id")
            if pk:
                row = self._sa.execute(text(named + f" RETURNING {pk}"), mapping)
                self.lastrowid = row.scalar()
                # sqlite3.Cursor expose .lastrowid TRÊN KẾT QUẢ execute() — call-site
                # cũ đọc `cur.lastrowid`. Gương lastrowid lên result để giữ contract.
                res0 = _CompatResult([])
                res0.lastrowid = self.lastrowid
                return res0
        res = self._sa.execute(text(named), mapping)
        try:
            rows = res.fetchall() if res.returns_rows else []
        except Exception:
            rows = []
        result = _CompatResult(rows)
        result.rowcount = res.rowcount
        result.lastrowid = self.lastrowid
        return result

    def executescript(self, script: str):
        # SQLite: dùng executescript gốc (nhiều câu); psycopg: exec cả script.
        raw = getattr(self._sa.connection, "dbapi_connection", None)
        if raw is not None and hasattr(raw, "executescript"):
            raw.executescript(script)
        else:
            self._sa.exec_driver_sql(script)
        return _CompatResult([])

    def commit(self):
        self._txn.commit()
        self._txn = self._sa.begin()
        self._apply_guc()  # GUC LOCAL reset sau commit → set lại

    def close(self):
        try:
            self._txn.rollback()   # sqlite: close không commit phần chưa commit
        except Exception:
            pass
        self._sa.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def compat_connect(*, service: bool = True) -> CompatConnection:
    """Mở 1 CompatConnection trên engine hiện hành (giữ văn phong sqlite3)."""
    return CompatConnection(get_engine(), service=service)
