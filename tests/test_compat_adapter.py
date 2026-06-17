"""P0-2d (a) — test adapter CompatConnection (engine/db.py) trên 2 driver.

Adapter giữ văn phong sqlite3 (? + lastrowid + commit/close) → cần đúng trên cả
SQLite lẫn Postgres trước khi gắn vào auth.py (module login, rủi ro cao).
"""
from __future__ import annotations

import os
import sqlite3

import pytest

import engine.db as db

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        path = tmp_path / "users.sqlite3"
        import api.auth as auth
        con = sqlite3.connect(path)
        auth._init_schema(con)
        con.commit(); con.close()
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        from sqlalchemy import text
        with db.get_engine().begin() as conn:
            db.apply_schema(conn)
        with db.session_scope(service=True) as conn:
            conn.execute(text("TRUNCATE users, user_castings RESTART IDENTITY CASCADE"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_qmark_translation():
    named, names = db._qmark_to_named("SELECT * FROM t WHERE a=? AND b=?")
    assert named == "SELECT * FROM t WHERE a=:p0 AND b=:p1"
    assert names == ["p0", "p1"]


def test_insert_lastrowid_users_pk(backend):
    c = db.compat_connect()
    try:
        c.execute("INSERT INTO users(email,display_name,password_hash,password_salt,"
                  "role,created_at) VALUES (?,?,?,?,?,?)",
                  ("a@x", "A", "h", "s", "user", 1))
        c.commit()
        assert c.lastrowid >= 1                      # RETURNING user_id
        uid = c.lastrowid
        row = c.execute("SELECT email, role FROM users WHERE user_id=?", (uid,)).fetchone()
        assert row[0] == "a@x" and row[1] == "user"
    finally:
        c.close()


def test_lastrowid_on_execute_result(backend):
    """Regression: auth.py đọc `cur = db.execute(INSERT); cur.lastrowid` — sqlite3.Cursor
    expose lastrowid TRÊN result, không chỉ trên connection. Trước fix → AttributeError."""
    c = db.compat_connect()
    try:
        cur = c.execute("INSERT INTO users(email,display_name,password_hash,"
                        "password_salt,role,created_at) VALUES (?,?,?,?,?,?)",
                        ("res@x", "R", "h", "s", "user", 1))
        c.commit()
        assert cur.lastrowid >= 1 and cur.lastrowid == c.lastrowid
    finally:
        c.close()


def test_insert_lastrowid_id_pk(backend):
    c = db.compat_connect()
    try:
        c.execute("INSERT INTO users(user_id,email,display_name,password_hash,"
                  "password_salt,role,created_at) VALUES (?,?,?,?,?,?,?)",
                  (7, "b@x", "B", "h", "s", "user", 1))
        c.execute("INSERT INTO user_castings(user_id,method,result_json,created_at) "
                  "VALUES (?,?,?,?)", (7, "tu_vi", "{}", 10))
        c.commit()
        assert c.lastrowid >= 1                      # RETURNING id
        n = c.execute("SELECT COUNT(*) FROM user_castings WHERE user_id=?", (7,)).fetchone()[0]
        assert n == 1
    finally:
        c.close()


def test_update_rowcount_and_close_discards(backend):
    c = db.compat_connect()
    try:
        c.execute("INSERT INTO users(email,display_name,password_hash,password_salt,"
                  "role,created_at) VALUES (?,?,?,?,?,?)", ("c@x", "C", "h", "s", "user", 1))
        c.commit()
        r = c.execute("UPDATE users SET display_name=? WHERE email=?", ("C2", "c@x"))
        assert r.rowcount == 1
        # CHƯA commit rồi close → thay đổi bị bỏ (giống sqlite)
    finally:
        c.close()
    c2 = db.compat_connect()
    try:
        nm = c2.execute("SELECT display_name FROM users WHERE email=?", ("c@x",)).fetchone()[0]
        assert nm == "C"   # update chưa commit đã bị rollback khi close
    finally:
        c2.close()
