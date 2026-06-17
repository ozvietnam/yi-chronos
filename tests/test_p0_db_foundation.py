"""P0-1 — nền data layer: engine dual-driver + RLS + migration.

- Test SQLite (engine factory) chạy mọi nơi.
- Test Postgres (RLS cô lập tenant + migration SQLite→PG) chỉ chạy khi đặt env
  `YI_TEST_PG_DSN` (vd postgresql+psycopg://yi_app:app@localhost:55432/yi_test).
  CI không có PG → tự skip (không fail).
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import text

import engine.db as db

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
pg_only = pytest.mark.skipif(not PG_DSN, reason="cần YI_TEST_PG_DSN (Postgres) để test RLS/migration")


# ─── SQLite / engine factory (luôn chạy) ─────────────────────────────────────

def test_default_is_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert db.database_url().startswith("sqlite:///")
    assert db.is_postgres() is False


def test_is_postgres_detection():
    assert db.is_postgres("postgresql+psycopg://u@h/db") is True
    assert db.is_postgres("sqlite:///x.db") is False


def test_sqlite_healthcheck(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path/'t.db'}")
    db.get_engine.cache_clear()
    hc = db.healthcheck()
    assert hc["db"] == "ok" and hc["driver"] == "sqlite"


# ─── Postgres: RLS cô lập tenant (gated) ─────────────────────────────────────

@pytest.fixture
def pg(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", PG_DSN)
    db.get_engine.cache_clear()
    # schema idempotent + dọn sạch để test độc lập
    with db.get_engine().begin() as conn:
        db.apply_schema(conn)
    with db.session_scope(service=True) as conn:
        for t in ["user_castings", "user_favorites", "user_subscriptions",
                  "user_persons", "user_facts", "chat_summaries",
                  "glossary_views", "users"]:
            conn.execute(text(f"TRUNCATE {t} RESTART IDENTITY CASCADE"))
    yield
    db.get_engine.cache_clear()


@pg_only
def test_rls_isolates_per_user(pg):
    # service_mode: seed xuyên user
    with db.session_scope(service=True) as conn:
        conn.execute(text(
            "INSERT INTO users(user_id,email,display_name,password_hash,password_salt,created_at)"
            " VALUES (1,'a@x','A','h','s',1),(2,'b@x','B','h','s',2)"))
        conn.execute(text(
            "INSERT INTO user_castings(user_id,method,result_json,created_at)"
            " VALUES (1,'tu_vi','{}'::jsonb,10),(1,'luc_hao','{}'::jsonb,11),"
            "(2,'tu_vi','{}'::jsonb,12)"))
    # user 1 chỉ thấy của mình
    with db.session_scope(uid=1) as conn:
        assert conn.execute(text("SELECT count(*) FROM user_castings")).scalar() == 2
        assert conn.execute(text("SELECT count(*) FROM users")).scalar() == 1
    # user 2 chỉ thấy của mình
    with db.session_scope(uid=2) as conn:
        assert conn.execute(text("SELECT count(*) FROM user_castings")).scalar() == 1


@pg_only
def test_rls_blocks_cross_write(pg):
    with db.session_scope(service=True) as conn:
        conn.execute(text(
            "INSERT INTO users(user_id,email,display_name,password_hash,password_salt,created_at)"
            " VALUES (1,'a@x','A','h','s',1),(2,'b@x','B','h','s',2)"))
    # user 2 cố ghi casting cho user 1 → RLS chặn
    with pytest.raises(Exception) as ei:
        with db.session_scope(uid=2) as conn:
            conn.execute(text(
                "INSERT INTO user_castings(user_id,method,result_json,created_at)"
                " VALUES (1,'x','{}'::jsonb,9)"))
    assert "row-level security" in str(ei.value).lower()


@pg_only
def test_deny_by_default_no_guc(pg):
    with db.session_scope(service=True) as conn:
        conn.execute(text(
            "INSERT INTO users(user_id,email,display_name,password_hash,password_salt,created_at)"
            " VALUES (1,'a@x','A','h','s',1)"))
    # Không set GUC (không service, không uid) → deny-by-default
    eng = db.get_engine()
    with eng.begin() as conn:
        assert conn.execute(text("SELECT count(*) FROM users")).scalar() == 0


# ─── Postgres: migration SQLite → PG (gated) ─────────────────────────────────

@pg_only
def test_migration_copies_and_verifies(pg, tmp_path, monkeypatch):
    import scripts.migrate_sqlite_to_postgres as mig

    # Dựng nguồn SQLite giả ở layout mong đợi dưới tmp ROOT
    (tmp_path / "data/yi_users").mkdir(parents=True)
    (tmp_path / "data/yi_hermes").mkdir(parents=True)
    u = sqlite3.connect(tmp_path / "data/yi_users/users.sqlite3")
    u.executescript("""
        CREATE TABLE users(user_id INTEGER PRIMARY KEY, email TEXT, display_name TEXT,
            password_hash TEXT, password_salt TEXT, role TEXT, default_person_id TEXT,
            created_at INTEGER, last_login_at INTEGER, must_change_password INTEGER,
            is_suspended INTEGER, suspended_at INTEGER, suspend_reason TEXT,
            firebase_uid TEXT, phone TEXT);
        INSERT INTO users(user_id,email,display_name,password_hash,password_salt,role,created_at)
            VALUES (1,'a@x','A','h','s','owner',1),(2,'b@x','B','h','s','user',2);
        CREATE TABLE user_castings(id INTEGER PRIMARY KEY, user_id INTEGER, method TEXT,
            subject_person_key TEXT, question TEXT, input_json TEXT, result_json TEXT,
            verdict TEXT, tags TEXT, note TEXT, algo_version TEXT, created_at INTEGER);
        INSERT INTO user_castings(user_id,method,result_json,algo_version,created_at)
            VALUES (1,'tu_vi','{"cung":"menh"}','mvp-0.1.0+tu_vi-1',10),
                   (2,'luc_hao','{"q":"x"}','mvp-0.1.0+luc_hao-1',11);
    """)
    u.commit(); u.close()
    m = sqlite3.connect(tmp_path / "data/yi_hermes/memory.sqlite3")
    m.executescript("""
        CREATE TABLE user_facts(id INTEGER PRIMARY KEY, user_id TEXT, fact TEXT,
            category TEXT, confidence REAL, source_session_id INTEGER, notes TEXT,
            extracted_at TEXT);
        INSERT INTO user_facts(user_id,fact,category) VALUES ('1','thích cà phê','preference');
    """)
    m.commit(); m.close()

    monkeypatch.setattr(mig, "ROOT", tmp_path)
    rc = mig.migrate(dry_run=False, do_schema=False, truncate=True)
    assert rc == 0  # verify đếm dòng khớp

    # Kiểm chứng dữ liệu thật + JSONB parse được + sequence đã sync
    with db.session_scope(service=True) as conn:
        assert conn.execute(text("SELECT count(*) FROM users")).scalar() == 2
        assert conn.execute(text("SELECT count(*) FROM user_castings")).scalar() == 2
        assert conn.execute(text("SELECT count(*) FROM user_facts")).scalar() == 1
        av = conn.execute(text(
            "SELECT result_json->>'cung' FROM user_castings WHERE user_id=1")).scalar()
        assert av == "menh"  # JSONB hợp lệ
        # sequence synced: insert mới không trùng PK
        conn.execute(text(
            "INSERT INTO users(email,display_name,password_hash,password_salt,created_at)"
            " VALUES ('c@x','C','h','s',3)"))
