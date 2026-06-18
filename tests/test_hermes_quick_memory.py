"""#39 (H6) — vòng ký ức quick tier: mỗi phiên run_quick chưng cất summary →
build_memory_context phiên sau có ngữ cảnh ("càng dùng càng hiểu user")."""
import pytest
from fastapi.testclient import TestClient

UID = "_test39_mem_uid_"
KEY = "mem-key-39"


@pytest.fixture
def synced_uid(monkeypatch):
    monkeypatch.setenv("YI_SYNC_API_KEY", KEY)
    from api.main import app
    c = TestClient(app)
    r = c.post("/api/sync/upsert-from-firebase",
               json={"firebase_uid": UID, "display_name": "M", "email": UID + "@t.local",
                     "birth": {"datetime_local": "1988-06-05T23:30:00", "gender": "nam"}},
               headers={"X-API-Key": KEY}).json()
    uid = r["yi_user_id"]
    yield uid
    from engine.db import session_scope
    from sqlalchemy import text
    with session_scope(service=True) as conn:
        for t in ("user_castings", "user_persons", "users"):
            try:
                conn.execute(text(f"DELETE FROM {t} WHERE user_id=:i"), {"i": uid})
            except Exception:
                pass


def test_run_quick_distills_summary_into_memory(synced_uid):
    from engine.hermes_service import run_quick
    from engine.yi_hermes import memory

    def mock_answer(q, person, u):
        return {"answer": "Theo lá số, anh thiên về tư duy phân tích.",
                "sage": "tu_vi", "cost_usd": 0.0, "provider": "mock"}

    res = run_quick("", "Tính cách của tôi theo lá số thế nào?",
                    user_id=synced_uid, answer=mock_answer)
    assert res["status"] == "done"

    # Phiên sau: memory context phải chứa tóm tắt phiên vừa rồi.
    ctx = memory.build_memory_context(str(synced_uid))
    assert "Hỏi nhanh" in ctx
    assert "tư duy phân tích" in ctx


def test_memory_writeback_failure_does_not_break_answer(synced_uid, monkeypatch):
    """Lỗi ghi memory KHÔNG được làm hỏng câu trả lời."""
    from engine.hermes_service import run_quick
    from engine.yi_hermes import memory

    def _boom(**k):
        raise RuntimeError("memory store down")
    monkeypatch.setattr(memory, "add_summary", _boom)

    res = run_quick("", "Vận sự nghiệp của tôi ra sao?", user_id=synced_uid,
                    answer=lambda q, p, u: {"answer": "...", "sage": "tu_vi", "cost_usd": 0.0})
    assert res["status"] == "done"  # vẫn trả lời dù memory write-back lỗi
