"""H7 — digest tuần (engine/digest): tổng hợp 7 ngày, chỉ user gói, có hoạt động."""
from __future__ import annotations

import os
import time

import pytest
from sqlalchemy import text

import engine.db as db
import engine.digest as dg
import engine.subscriptions as subs

PG_DSN = os.environ.get("YI_TEST_PG_DSN", "").strip()
BACKENDS = ["sqlite"] + (["pg"] if PG_DSN else [])


def _seed_user(uid_email: str) -> int:
    with db.session_scope(service=True) as conn:
        return conn.execute(
            text("INSERT INTO users(email,display_name,password_hash,password_salt,role,"
                 "created_at) VALUES (:e,'U','h','s','user',1) RETURNING user_id"),
            {"e": uid_email}).scalar()


def _add_casting(user_id: int, method: str, when: int):
    je = "CAST('{}' AS JSONB)" if db.is_postgres() else "'{}'"
    with db.session_scope(service=True) as conn:
        conn.execute(text(f"INSERT INTO user_castings(user_id,method,question,result_json,"
                          f"created_at) VALUES (:u,:m,'q',{je},:t)"),
                     {"u": user_id, "m": method, "t": when})


@pytest.fixture(params=BACKENDS)
def backend(request, tmp_path, monkeypatch):
    if request.param == "sqlite":
        path = tmp_path / "u.sqlite3"
        monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
        db.get_engine.cache_clear()
        import api.sync as sync
        sync._ensure_schema()
    else:
        monkeypatch.setenv("DATABASE_URL", PG_DSN)
        db.get_engine.cache_clear()
        with db.get_engine().begin() as c:
            db.apply_schema(c)
        with db.session_scope(service=True) as c:
            c.execute(text("TRUNCATE users, user_castings, user_subscriptions "
                           "RESTART IDENTITY CASCADE"))
    db.get_engine.cache_clear()
    yield request.param
    db.get_engine.cache_clear()


def test_build_weekly_digest_counts(backend):
    now = int(time.time())
    uid = _seed_user("a@x")
    _add_casting(uid, "tu_vi", now - 3600)          # trong tuần
    _add_casting(uid, "hermes_quick", now - 2 * 86400)
    _add_casting(uid, "tu_vi", now - 30 * 86400)    # ngoài 7 ngày → không tính
    d = dg.build_weekly_digest(uid, now=now)
    assert d["n"] == 2 and d["by_method"] == {"tu_vi": 1, "hermes_quick": 1}
    assert len(d["highlights"]) == 2


def test_run_all_only_vip_with_activity(backend):
    now = int(time.time())
    vip = _seed_user("vip@x"); subs.grant_subscription(vip, "hermes_council", remaining_uses=5)
    vip_idle = _seed_user("idle@x"); subs.grant_subscription(vip_idle, "hermes_council", remaining_uses=5)
    free = _seed_user("free@x")                     # không gói
    _add_casting(vip, "tu_vi", now - 3600)
    _add_casting(free, "tu_vi", now - 3600)         # free có hoạt động nhưng không gói
    out = dg.run_weekly_digest_all(now=now)
    assert out["vip"] == 2 and out["sent"] == 1     # chỉ vip (có hoạt động) được digest
    # digest đã lưu cho vip
    with db.session_scope(service=True) as c:
        n = c.execute(text("SELECT count(*) FROM user_castings WHERE user_id=:u "
                           "AND method='weekly_digest'"), {"u": vip}).scalar()
    assert n == 1
