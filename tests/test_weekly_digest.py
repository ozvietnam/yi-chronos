"""#40 (H7) — digest tuần (engine.digest): gate sub, teaser, push notifyUser, idempotent.

engine/digest.py là module canonical (wired Beat `yi.digest.weekly_tick` Mon 06:00).
Test enhancement #40: gate sub enabled + notify_fn push (mock) + idempotent theo tuần.
"""
import time

import pytest
from fastapi.testclient import TestClient

KEY = "digest-key-40"
SUB_UID = "_test40_sub_"
FREE_UID = "_test40_free_"
NOW = 1750000000


def _add_activity(uid: int, now: int):
    from engine.db import session_scope, is_postgres
    from sqlalchemy import text
    res = "CAST(:r AS JSONB)" if is_postgres() else ":r"
    with session_scope(service=True) as conn:
        conn.execute(text(
            f"""INSERT INTO user_castings (user_id, method, subject_person_key, question,
                    result_json, verdict, tags, note, algo_version, created_at)
                VALUES (:u,'tu_vi','self','Tính cách tôi?',{res},NULL,'quick',NULL,'v1',:t)"""
        ), {"u": uid, "r": "{}", "t": now})


@pytest.fixture
def users(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}

    def mk(uid):
        return c.post("/api/sync/upsert-from-firebase",
                      json={"firebase_uid": uid, "display_name": uid, "email": uid + "@t.local",
                            "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
                      headers=H).json()["yi_user_id"]

    sub_id, free_id = mk(SUB_UID), mk(FREE_UID)
    from engine import subscriptions as subs
    subs.grant_subscription(sub_id, "tu_vi_phe_menh_sau", enabled=True)
    _add_activity(sub_id, NOW)        # sub user có hoạt động tuần qua
    yield {"sub_id": sub_id, "free_id": free_id}
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        for uid in (sub_id, free_id):
            for t in ("user_subscriptions", "user_castings", "user_persons", "users"):
                try:
                    conn.execute(text(f"DELETE FROM {t} WHERE user_id=:i"), {"i": uid})
                except Exception:
                    pass


def test_gates_to_subscribers_only(users):
    from engine.digest import run_weekly_digest_all
    calls = []
    run_weekly_digest_all(now=NOW, notify_fn=lambda fb, p: (calls.append((fb, p)) or True))
    notified = {fb for fb, _ in calls}
    assert SUB_UID in notified          # sub + có hoạt động → nhận
    assert FREE_UID not in notified     # free → gate chặn


def test_teaser_shape(users):
    from engine.digest import run_weekly_digest_all
    calls = []
    run_weekly_digest_all(now=NOW, notify_fn=lambda fb, p: (calls.append((fb, p)) or True))
    p = next(pl for fb, pl in calls if fb == SUB_UID)
    assert p["kind"] == "weekly_digest"
    assert 1 <= len(p["items"]) <= 3    # teaser, không luận đầy
    assert "deeplink" in p


def test_idempotent_same_week(users):
    from engine.digest import run_weekly_digest_all
    n1 = run_weekly_digest_all(now=NOW, notify_fn=lambda fb, p: True)
    n2 = run_weekly_digest_all(now=NOW, notify_fn=lambda fb, p: True)
    assert n1["sent"] >= 1
    assert n2["sent"] == 0               # đã gửi tuần này → không trùng
    assert n2["skipped_already"] >= 1


def test_no_activity_not_sent(users):
    """User có sub nhưng KHÔNG hoạt động tuần qua → không làm phiền."""
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:   # xoá hoạt động đã seed
        conn.execute(text("DELETE FROM user_castings WHERE user_id=:i"),
                     {"i": users["sub_id"]})
    from engine.digest import run_weekly_digest_all
    n = run_weekly_digest_all(now=NOW, notify_fn=lambda fb, p: True)
    assert n["sent"] == 0
