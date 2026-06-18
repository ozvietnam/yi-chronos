"""#40 (H7) — digest tuần: gate sub, teaser cái mới, idempotent. Mock notifyUser."""
import pytest
from fastapi.testclient import TestClient

KEY = "digest-key-40"
SUB_UID = "_test40_sub_"
FREE_UID = "_test40_free_"
NOW1 = 1750000000.0
NOW2 = NOW1 + 7 * 86400  # tuần ISO kế tiếp


@pytest.fixture
def users(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}

    def mk(uid):
        r = c.post("/api/sync/upsert-from-firebase",
                   json={"firebase_uid": uid, "display_name": uid, "email": uid + "@t.local",
                         "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
                   headers=H).json()
        return r["yi_user_id"]

    sub_id, free_id = mk(SUB_UID), mk(FREE_UID)
    from engine import subscriptions as subs
    subs.grant_subscription(sub_id, "tu_vi_phe_menh_sau", enabled=True)
    from engine.yi_hermes import memory
    memory.add_summary(user_id=str(sub_id), summary="Phiên test digest", session_id=1)
    yield {"sub_id": sub_id, "free_id": free_id}
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        for uid in (sub_id, free_id):
            for t in ("weekly_digest_sent", "user_subscriptions", "chat_summaries",
                      "user_persons", "users"):
                try:
                    conn.execute(text(f"DELETE FROM {t} WHERE user_id=:i"), {"i": uid})
                except Exception:
                    pass


def test_gates_to_subscribers_only(users):
    from engine.weekly_digest import run_weekly_digest
    calls = []
    run_weekly_digest(notify_fn=lambda fb, p: (calls.append((fb, p)) or True), now=NOW1)
    notified = {fb for fb, _ in calls}
    assert SUB_UID in notified          # sub user nhận
    assert FREE_UID not in notified     # free user KHÔNG (gate)


def test_teaser_shape(users):
    from engine.weekly_digest import run_weekly_digest
    calls = []
    run_weekly_digest(notify_fn=lambda fb, p: (calls.append((fb, p)) or True), now=NOW1)
    p = next(pl for fb, pl in calls if fb == SUB_UID)
    assert p["kind"] == "weekly_digest"
    assert 1 <= len(p["items"]) <= 3    # teaser, không luận đầy
    assert "deeplink" in p
    assert "_algo_version" not in p     # field nội bộ không lộ ra payload


def test_idempotent_same_week(users):
    from engine.weekly_digest import run_weekly_digest
    n1 = run_weekly_digest(notify_fn=lambda fb, p: True, now=NOW1)
    n2 = run_weekly_digest(notify_fn=lambda fb, p: True, now=NOW1)
    assert n1["sent"] >= 1
    assert n2["sent"] == 0               # cùng tuần → không gửi trùng
    assert n2["skipped_already"] >= 1


def test_no_change_next_week_skips(users):
    from engine.weekly_digest import run_weekly_digest
    run_weekly_digest(notify_fn=lambda fb, p: True, now=NOW1)
    n2 = run_weekly_digest(notify_fn=lambda fb, p: True, now=NOW2)
    assert n2["sent"] == 0               # tuần sau không có gì mới → không gửi
    assert n2["skipped_no_change"] >= 1


def test_not_delivered_does_not_record(users):
    """notify_fn trả False (notifyUser chưa sẵn sàng) → KHÔNG ghi sent → lần sau retry."""
    from engine.weekly_digest import run_weekly_digest
    n1 = run_weekly_digest(notify_fn=lambda fb, p: False, now=NOW1)
    assert n1["sent"] == 0
    assert n1["skipped_not_delivered"] >= 1
    n2 = run_weekly_digest(notify_fn=lambda fb, p: True, now=NOW1)
    assert n2["sent"] >= 1               # retry thành công khi delivery sẵn sàng
