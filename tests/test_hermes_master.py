"""Hermes Chúa — master rà soát + giao sage con tự đánh giá (Anh chốt 20/6)."""
import pytest

from engine.db import get_engine


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/hm.sqlite3")
    get_engine.cache_clear()
    from api import sync
    sync._ensure_schema()
    yield
    get_engine.cache_clear()


def _mock_provider(monkeypatch):
    """Mỗi sage tự-đánh-giá: tu_vi → flagged (điểm thấp + có issue); còn lại → đạt."""
    from engine.ai import council
    from engine.ai.providers.base import LLMResponse

    def content_for(tag):
        if tag == "tu_vi":
            return ('{"sample":"Năm 2030 anh sẽ giàu.","paradigm_score":3,'
                    '"paradigm_ok":false,"issues":["dự báo cát/hung cụ thể"],"de_xuat":"bỏ predict"}')
        return ('{"sample":"Cấu trúc này phản chiếu một khí cần quan sát.","paradigm_score":9,'
                '"paradigm_ok":true,"issues":[],"de_xuat":"giữ vững đồng dạng"}')

    class MockP:
        def __init__(self, tag):
            self.tag = tag

        def chat(self, messages, model=None, **kw):
            return LLMResponse(content=content_for(self.tag), model="mock", provider="mock",
                               prompt_tokens=1, completion_tokens=1, total_tokens=2)

    monkeypatch.setattr(council, "_get_agent_provider",
                        lambda aid, prefer_reasoning=False: (MockP(aid), "mock"))


def test_master_review_flags_paradigm_violator(temp_db, monkeypatch):
    _mock_provider(monkeypatch)
    from engine.hermes_master import master_review
    r = master_review(tags=["tu_vi", "chieu_dom"], max_workers=2)
    assert r["n_sages"] == 2
    assert "tu_vi" in r["flagged"]          # sage predict-leakage bị Hermes Chúa flag
    assert "chieu_dom" not in r["flagged"]  # sage tuân paradigm → không flag
    assert r["avg_score"] is not None
    assert "work" in r                       # rà soát công việc (metrics) đính kèm


def test_master_review_handles_provider_error(temp_db, monkeypatch):
    from engine.ai import council

    class BoomP:
        def chat(self, *a, **k):
            raise RuntimeError("no key")
    monkeypatch.setattr(council, "_get_agent_provider",
                        lambda aid, prefer_reasoning=False: (BoomP(), "mock"))
    from engine.hermes_master import master_review
    r = master_review(tags=["tu_vi"], max_workers=1)
    # provider lỗi → sage đó flagged (ok=False), không sập master
    assert r["n_sages"] == 1 and "tu_vi" in r["flagged"]


def test_endpoint_owner_only(temp_db):
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.post("/api/admin/hermes/master-review", json={})
    assert r.status_code in (401, 403)      # anon chặn (owner-only)
