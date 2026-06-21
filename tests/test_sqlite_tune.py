"""P1 (review 2026-06-21) — bật WAL cho SQLite đa-worker.

Production: 13/13 file .sqlite3 đều journal_mode=delete → writer khoá độc quyền toàn
DB, reader chặn writer. WAL = reader + 1 writer song song. WAL PERSISTENT (lưu trong
header file) → set 1 lần là mọi connection sau (kể cả 135 raw sqlite3.connect) đều
dùng, KHÔNG phải sửa từng call-site. (busy_timeout Python đã 5s mặc định — không phải
'0ms' như nghi ban đầu; vấn đề thật là journal mode.)
"""
from __future__ import annotations

import sqlite3


def test_enable_wal_persists_on_file(tmp_path):
    db = tmp_path / "t.sqlite3"
    sqlite3.connect(str(db)).close()  # tạo file (mặc định delete)
    assert sqlite3.connect(str(db)).execute("PRAGMA journal_mode").fetchone()[0] == "delete"

    from core.sqlite_tune import enable_wal
    assert enable_wal(db) is True
    # WAL persistent → connection MỚI bất kỳ vẫn thấy wal (không cần set lại)
    assert sqlite3.connect(str(db)).execute("PRAGMA journal_mode").fetchone()[0] == "wal"


def test_enable_wal_all_scans_dir_recursively(tmp_path):
    for name in ("a.sqlite3", "sub/b.sqlite3"):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        sqlite3.connect(str(p)).close()

    from core.sqlite_tune import enable_wal_all
    assert enable_wal_all(tmp_path) == 2
    for name in ("a.sqlite3", "sub/b.sqlite3"):
        mode = sqlite3.connect(str(tmp_path / name)).execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal", f"{name} chưa WAL"


def test_enable_wal_tolerates_missing_file(tmp_path):
    """File không tồn tại → trả False, KHÔNG ném (không được vỡ startup)."""
    from core.sqlite_tune import enable_wal
    assert enable_wal(tmp_path / "khong-co.sqlite3") is False


def test_tune_connection_sets_pragmas(tmp_path):
    from core.sqlite_tune import tune_connection
    con = tune_connection(sqlite3.connect(str(tmp_path / "c.sqlite3")))
    assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert con.execute("PRAGMA busy_timeout").fetchone()[0] == 5000


def test_get_engine_sqlite_connection_is_tuned(tmp_path, monkeypatch):
    """engine/db.py: connection SQLite của SQLAlchemy cũng WAL + busy_timeout 5s."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'e.sqlite3'}")
    from sqlalchemy import text
    from engine.db import get_engine
    get_engine.cache_clear()
    try:
        eng = get_engine()
        with eng.connect() as c:
            assert c.execute(text("PRAGMA journal_mode")).fetchone()[0] == "wal"
            assert c.execute(text("PRAGMA busy_timeout")).fetchone()[0] == 5000
    finally:
        get_engine.cache_clear()
