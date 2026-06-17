"""P0 — integration cho migrate_sqlite_to_postgres (gated PG).

Bảo vệ tool cutover một-lần: idempotent (chạy lại không trùng/không vỡ) + coerce
JSON rỗng → NULL (không abort batch) + verify đếm dòng khớp.
"""
from __future__ import annotations

import os
import sqlite3

import pytest
from sqlalchemy import text

import engine.db as db

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
pytestmark = pytest.mark.skipif(not PG_DSN, reason="cần YI_TEST_PG_DSN")


def _seed_sqlite(path):
    con = sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE,
            display_name TEXT, password_hash TEXT, password_salt TEXT, role TEXT,
            default_person_id TEXT, created_at INTEGER, last_login_at INTEGER,
            must_change_password INTEGER, is_suspended INTEGER, suspended_at INTEGER,
            suspend_reason TEXT, firebase_uid TEXT, phone TEXT);
        CREATE TABLE user_castings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            method TEXT, subject_person_key TEXT, question TEXT, input_json TEXT,
            result_json TEXT, verdict TEXT, tags TEXT, note TEXT, algo_version TEXT,
            created_at INTEGER);
    """)
    con.execute("INSERT INTO users(user_id,email,display_name,password_hash,password_salt,"
                "role,created_at) VALUES (1,'a@x','A','h','s','user',100)")
    # input_json='' (rỗng) → phải coerce NULL; result_json hợp lệ
    con.execute("INSERT INTO user_castings(id,user_id,method,input_json,result_json,created_at) "
                "VALUES (1,1,'tu_vi','', '{\"r\":1}', 5)")
    con.commit(); con.close()


@pytest.fixture
def pg_fresh(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", PG_DSN)
    db.get_engine.cache_clear()
    with db.get_engine().begin() as c:
        c.exec_driver_sql("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        db.apply_schema(c)
    db.get_engine.cache_clear()
    yield
    db.get_engine.cache_clear()


def test_migrate_idempotent_and_json_coerce(pg_fresh, tmp_path, monkeypatch):
    import scripts.migrate_sqlite_to_postgres as mig
    sq = tmp_path / "u.sqlite3"
    _seed_sqlite(sq)
    monkeypatch.setattr(mig, "ROOT", tmp_path)
    monkeypatch.setattr(mig, "PLAN", [
        ("u.sqlite3", "users", ["user_id", "email", "display_name", "password_hash",
                                 "password_salt", "role", "created_at"], set()),
        ("u.sqlite3", "user_castings", ["id", "user_id", "method", "input_json",
                                        "result_json", "created_at"],
         {"input_json", "result_json"}),
    ])
    monkeypatch.setattr(mig, "SERIAL_TABLES", ["users", "user_castings"])

    # Lần 1 (truncate) → OK
    assert mig.migrate(dry_run=False, do_schema=False, truncate=True) == 0
    # Lần 2 (KHÔNG truncate) → ON CONFLICT DO NOTHING giữ idempotent, vẫn == nguồn
    assert mig.migrate(dry_run=False, do_schema=False, truncate=False) == 0

    with db.session_scope(service=True) as c:
        assert c.execute(text("SELECT count(*) FROM users")).scalar() == 1
        assert c.execute(text("SELECT count(*) FROM user_castings")).scalar() == 1
        # input_json rỗng đã coerce thành NULL (không vỡ CAST)
        ij = c.execute(text("SELECT input_json FROM user_castings WHERE id=1")).scalar()
        assert ij is None
        rj = c.execute(text("SELECT result_json->>'r' FROM user_castings WHERE id=1")).scalar()
        assert rj == "1"
