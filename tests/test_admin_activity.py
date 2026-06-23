"""Admin nhật ký hỏi-đáp (user_castings feed) — owner-gate + query chạy dual-driver."""
import time

import pytest
from sqlalchemy import text

from engine.db import get_engine, session_scope


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/act.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def test_activity_endpoints_owner_only(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.get("/api/admin/activity").status_code in (401, 403)
    assert c.get("/api/admin/activity?method=hermes_council").status_code in (401, 403)
    assert c.get("/api/admin/activity/1").status_code in (401, 403)


def test_activity_query_runs(temp_db):
    """SQL feed (JOIN users, ORDER BY id DESC) chạy được — seed 1 casting rồi đọc."""
    with session_scope(service=True) as conn:
        uid = conn.execute(text(
            "INSERT INTO users(email,display_name,password_hash,password_salt,role,created_at) "
            "VALUES ('a@x','A','h','s','user',1) RETURNING user_id")).scalar()
        rj = "CAST('{\"synthesis\":\"đáp mẫu\"}' AS JSONB)" if False else "'{\"synthesis\":\"đáp mẫu\"}'"
        conn.execute(text(
            f"INSERT INTO user_castings(user_id,method,question,result_json,verdict,algo_version,created_at) "
            f"VALUES (:u,'hermes_council','Hỏi nghề?',{rj},NULL,'v1',:t)"),
            {"u": uid, "t": int(time.time())})
        rows = conn.execute(text(
            """SELECT c.id, c.user_id, u.email, c.method, c.question, c.verdict, c.created_at
               FROM user_castings c LEFT JOIN users u ON u.user_id = c.user_id
               ORDER BY c.id DESC LIMIT 50""")).fetchall()
    assert rows and rows[0][3] == "hermes_council" and rows[0][2] == "a@x"
