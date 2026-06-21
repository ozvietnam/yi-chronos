"""Bật WAL cho SQLite (review 2026-06-21, P1 — concurrency đa-worker).

VẤN ĐỀ: gunicorn chạy nhiều worker (mỗi worker tới 40 luồng threadpool) cùng ghi 1
file SQLite. Mặc định journal_mode='delete' → writer khoá ĐỘC QUYỀN toàn DB; reader
chặn writer và ngược lại → contention dưới tải.

GIẢI: WAL (Write-Ahead Logging) cho reader + 1 writer song song KHÔNG chặn nhau. WAL
là thiết lập PERSISTENT (lưu trong header file) → set 1 lần trên file là MỌI connection
sau (kể cả ~135 raw `sqlite3.connect` rải khắp code) đều dùng WAL, KHÔNG cần sửa từng
call-site. Gọi enable_wal_all() lúc startup là đủ.

GHI CHÚ: busy_timeout của Python sqlite3 ĐÃ mặc định 5000ms (không phải 0) nên writer
chờ 5s thay vì lỗi ngay — không cần ép. synchronous=NORMAL (an toàn với WAL, nhanh hơn
FULL) là per-connection → chỉ áp khi code dùng tune_connection(); raw connect vẫn FULL
(an toàn, chỉ chậm hơn chút khi ghi).
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


def enable_wal(path) -> bool:
    """Set journal_mode=WAL trên 1 file SQLite (persistent). True nếu file giờ ở WAL.

    Bỏ qua (trả False) nếu file không tồn tại / khoá / không phải SQLite — KHÔNG ném
    để không làm vỡ startup.
    """
    p = Path(path)
    if not p.exists():
        return False
    try:
        con = sqlite3.connect(str(p), timeout=5.0)
        try:
            row = con.execute("PRAGMA journal_mode=WAL").fetchone()
            con.execute("PRAGMA synchronous=NORMAL")
            con.commit()
            ok = bool(row and str(row[0]).lower() == "wal")
            if not ok:
                logger.warning("enable_wal(%s): journal_mode=%s (không chuyển được WAL)", p.name, row)
            return ok
        finally:
            con.close()
    except Exception as e:  # noqa: BLE001 — file lạ/khoá → bỏ qua, không vỡ startup
        logger.warning("enable_wal(%s) bỏ qua: %s", p.name, e)
        return False


def tune_connection(con: sqlite3.Connection) -> sqlite3.Connection:
    """Áp PRAGMA hiệu năng cho 1 connection (cho code MỚI dùng khi mở raw)."""
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA busy_timeout=5000")
    return con


def enable_wal_all(data_dir) -> int:
    """Quét data_dir đệ quy, bật WAL mọi *.sqlite3. Trả số file đã bật WAL thành công."""
    root = Path(data_dir)
    if not root.exists():
        return 0
    n = 0
    for p in sorted(root.rglob("*.sqlite3")):
        if enable_wal(p):
            n += 1
    return n
