"""Sage Thiết Bản dịch điều văn + lời bình + cache (Anh chốt 20/6)."""
import pytest

from engine.db import get_engine


def test_sage_registered():
    from engine.ai import prompt_store as ps
    from engine.ai.council import DEFAULT_AGENT_PROVIDER
    from engine.ai.kanban_council import SAGES_BY_TAG
    assert "thiet_ban" in ps.AGENT_IDS
    assert "thiet_ban" in DEFAULT_AGENT_PROVIDER
    assert SAGES_BY_TAG["thiet_ban"] == "thiet-ban-sage"
    p = ps.get_prompt("thiet_ban")
    assert "điều văn" in p and "đồng dạng" in p and "động từ" in p   # paradigm Iron #6/#8


def test_translate_and_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/tb.sqlite3")
    get_engine.cache_clear()
    from engine.ai import council
    from engine.ai.providers.base import LLMResponse

    calls = {"n": 0}

    class MockP:
        def chat(self, messages, model=None, **kw):
            calls["n"] += 1
            assert "điều văn" in messages[0]["content"]   # persona thiet_ban nạp đúng
            return LLMResponse(
                content='[{"so":7348,"dich":"Thắp đèn soi đường, qua lại không ngờ.","binh":"Khí sáng tỏ — vận hành đẹp khi giữ tâm minh."}]',
                model="mock", provider="mock", prompt_tokens=1, completion_tokens=1, total_tokens=2)

    monkeypatch.setattr(council, "_get_agent_provider",
                        lambda aid, prefer_reasoning=False: (MockP(), "mock"))
    from engine.thiet_ban.luan_dieu_van import luan_dieu_van

    r1 = luan_dieu_van([{"so": 7348, "zh": "点灯照路，来往无疑。", "ngu_canh": "đại vận Kỷ Mùi, 3 tuổi"}])
    assert r1["luan"]["7348"]["dich"].startswith("Thắp đèn")
    assert r1["luan"]["7348"]["binh"] and r1["translated"] == 1

    # Lần 2 cùng số điều → CACHE hit, KHÔNG gọi LLM lại
    r2 = luan_dieu_van([{"so": 7348, "zh": "点灯照路，来往无疑。"}])
    assert r2["from_cache"] == 1 and r2["translated"] == 0
    assert calls["n"] == 1   # chỉ 1 LLM call tổng cộng
    get_engine.cache_clear()


def test_endpoint_requires_login(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/tb2.sqlite3")
    get_engine.cache_clear()
    from fastapi.testclient import TestClient
    from api.main import app
    c = TestClient(app)
    r = c.post("/api/thiet-ban/luan-dieu-van",
               json={"items": [{"so": 1, "zh": "测"}]})
    assert r.status_code == 401   # anon chặn (không đốt LLM)
    get_engine.cache_clear()
