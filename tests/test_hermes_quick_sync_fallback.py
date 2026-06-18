"""#50 — hermes-quick sync fallback khi broker Celery chưa sẵn sàng.

Khi enqueue `.delay()` fail (Redis chưa có trên prod — #41 — hoặc celery chưa cài),
endpoint chạy run_quick ĐỒNG BỘ inline + lưu kết quả → poll vẫn trả SUCCESS theo
contract AppChat {processing → job_id → SUCCESS}. Trước fix: 500.
"""
import pytest
from fastapi.testclient import TestClient

UID = "_test50_uid_"
KEY = "qk-key-50"
CANNED = {"status": "done", "answer": "Theo lá số, anh là người quyết đoán...",
          "sage": "tu_vi", "paradigm_ok": True}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    # run_quick canned → test FLOW fallback, không phụ thuộc LLM
    import engine.hermes_service as HS
    monkeypatch.setattr(HS, "run_quick", lambda fu, q, pk="self": dict(CANNED))
    from api.main import app
    c = TestClient(app)
    H = {"X-API-Key": KEY}
    c.post("/api/sync/upsert-from-firebase",
           json={"firebase_uid": UID, "display_name": "T", "email": UID + "@t.local",
                 "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
           headers=H)
    yield c, H
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        r = conn.execute(text("SELECT user_id FROM users WHERE firebase_uid=:u"),
                         {"u": UID}).fetchone()
        if r:
            conn.execute(text("DELETE FROM user_persons WHERE user_id=:i"), {"i": r[0]})
            conn.execute(text("DELETE FROM users WHERE user_id=:i"), {"i": r[0]})
        conn.execute(text("DELETE FROM quick_job_results WHERE job_id LIKE 'sync-%'"))


def test_hermes_quick_in_scope_returns_job_not_500(client):
    """In-scope → KHÔNG 500; trả {status:processing, job_id}."""
    c, H = client
    r = c.post("/api/sync/hermes-quick",
               json={"firebase_uid": UID, "question": "Tính cách của tôi theo lá số thế nào?"},
               headers=H)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["status"] == "processing"
    assert j["job_id"]


def test_hermes_quick_poll_returns_success_with_answer(client):
    """Poll job (sync fallback) → SUCCESS + result.answer."""
    c, H = client
    j = c.post("/api/sync/hermes-quick",
               json={"firebase_uid": UID, "question": "Vận trình sự nghiệp của tôi ra sao?"},
               headers=H).json()
    jid = j["job_id"]
    # Trong env không có broker → fallback đồng bộ → job_id 'sync-' + poll từ store.
    assert jid.startswith("sync-")
    poll = c.get(f"/api/sync/hermes-quick/{jid}", headers=H).json()
    assert poll["state"] == "SUCCESS"
    assert poll["result"]["answer"] == CANNED["answer"]


def test_hermes_quick_out_of_scope_still_sync(client):
    """Ngoài phạm vi vẫn trả đồng bộ (không enqueue, không fallback)."""
    c, H = client
    import engine.hermes_service as HS
    # precheck_quick dùng guard thật; câu rõ ràng ngoài miền
    r = c.post("/api/sync/hermes-quick",
               json={"firebase_uid": UID, "question": "Viết hộ tôi đoạn code Python sắp xếp mảng"},
               headers=H)
    assert r.status_code == 200
    # out_of_scope → reply (không có job_id)
    assert r.json().get("status") in {"out_of_scope", "needs_clarification"} or "reply" in r.json()
