"""#38/#39 hardening — tier async CHẬM (deep-reading, council) trả 503 graceful khi
broker Celery chưa sẵn sàng (Redis chưa lên prod — #41/PR#53), thay vì 500 thô.

Local KHÔNG có celery → `import engine.tasks.jobs` throw = proxy cho broker-down →
endpoint phải bắt → 503 (không 500, không 200-treo)."""
import pytest
from fastapi.testclient import TestClient

KEY = "async503-key"
UID = "_test503_uid_"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}
    uid = c.post("/api/sync/upsert-from-firebase",
                 json={"firebase_uid": UID, "display_name": "T", "email": UID + "@t.local",
                       "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
                 headers=H).json()["yi_user_id"]
    from engine import subscriptions as subs
    subs.grant_subscription(uid, "tu_vi_phe_menh_sau", enabled=True)
    subs.grant_subscription(uid, "hermes_council", enabled=True)
    yield c, H, uid
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        for t in ("user_subscriptions", "user_castings", "user_persons", "users"):
            try:
                conn.execute(text(f"DELETE FROM {t} WHERE user_id=:i"), {"i": uid})
            except Exception:
                pass


def test_deep_reading_broker_down_returns_503(client):
    c, H, _ = client
    r = c.post("/api/sync/deep-reading",
               json={"firebase_uid": UID, "person_key": "self"}, headers=H)
    # KHÔNG 500 (thô) và KHÔNG 200-treo; 503 graceful (hoặc 403 nếu gate sub khác).
    assert r.status_code in (503, 403), r.text
    if r.status_code == 503:
        assert "chưa sẵn sàng" in r.text


def test_council_broker_down_returns_503(client):
    c, H, _ = client
    r = c.post("/api/sync/hermes-council",
               json={"firebase_uid": UID, "question": "Tính cách của tôi theo lá số?",
                     "person_key": "self"}, headers=H)
    assert r.status_code in (503, 403), r.text
    if r.status_code == 503:
        assert "chưa sẵn sàng" in r.text
