"""Trang Hỏi Hermes — run_council surface voices + sage-picker (explicit_agents) + gate login."""
import pytest
from sqlalchemy import text

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/hh.sqlite3")
    monkeypatch.setenv("LLM_DAILY_BUDGET_USD", "50")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def _seed(uid="uid_hh"):
    import engine.db as db
    import engine.hermes_service as hs
    import engine.subscriptions as subs
    with db.session_scope(service=True) as conn:
        user_id = conn.execute(
            text("INSERT INTO users(email,display_name,password_hash,password_salt,"
                 "role,firebase_uid,created_at) VALUES (:e,'U','h','s','user',:u,1) "
                 "RETURNING user_id"), {"e": f"{uid}@x", "u": uid}).scalar()
        conn.execute(text("INSERT INTO user_persons(user_id,person_key,name,gender,"
                          "birth_datetime_local,timezone,created_at) VALUES "
                          "(:u,'self','U','nam','1990-02-03T08:00:00','Asia/Ho_Chi_Minh',1)"),
                     {"u": user_id})
    subs.grant_subscription(user_id, hs.FEATURE, tier="vip1", remaining_uses=5)
    return user_id


def _consult_voices(q, person, uid):
    return {"synthesis": "Cấu trúc lá số vận hành đẹp khi anh chủ động.",
            "agents": ["tu_vi", "bat_tu"], "provider": "mock", "cost_usd": 0.0,
            "raw": {"round_1_outputs": [
                {"agent_id": "tu_vi", "agent_name_vi": "Tử Vi", "content": "Tiếng nói Tử Vi…"},
                {"agent_id": "bat_tu", "agent_name_vi": "Bát Tự", "content": "Tiếng nói Bát Tự…"},
                {"agent_id": "e", "agent_name_vi": "E", "content": "", "error": "boom"}]}}


def test_run_council_surfaces_voices(temp_db):
    import engine.hermes_service as hs
    _seed("uid_hh")
    r = hs.run_council("uid_hh", "Lá số em nói gì về hướng sự nghiệp?", consult=_consult_voices)
    assert r["status"] == "done"
    assert len(r["voices"]) == 2          # voice lỗi bị loại
    assert r["voices"][0]["name"] == "Tử Vi" and r["voices"][0]["content"]
    assert r["synthesis"]


def test_explicit_agents_threaded(temp_db, monkeypatch):
    """User chọn sage → explicit_agents xuyên tới _real_consult (giữ chữ ký 3-arg cho stub)."""
    import engine.hermes_service as hs
    _seed("uid_ea")
    captured = {}

    def fake_real(q, p, u, explicit_agents=None):
        captured["ea"] = explicit_agents
        return {"synthesis": "s", "agents": [], "provider": "mock", "cost_usd": 0,
                "raw": {"round_1_outputs": []}}

    monkeypatch.setattr(hs, "_real_consult", fake_real)
    hs.run_council("uid_ea", "Lá số em nói gì về sự nghiệp?", explicit_agents=["tu_vi", "chieu_dom"])
    assert captured["ea"] == ["tu_vi", "chieu_dom"]


def test_endpoints_login_gated(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    assert c.post("/api/hermes/council", json={"question": "x"}).status_code in (401, 403)
    assert c.get("/api/hermes/sages").status_code in (401, 403)
