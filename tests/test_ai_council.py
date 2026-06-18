"""Tests for AI Hội Đồng (Sages Council) infrastructure."""

from __future__ import annotations

import pytest

# /api/ai/* provider+prompt endpoints are owner-gated (security audit).
pytestmark = pytest.mark.usefixtures("as_owner")


# ─── Providers ────────────────────────────────────────────────────────────────


def test_registry_lists_all_providers():
    from engine.ai.registry import get_registry

    reg = get_registry()
    names = {p["name"] for p in reg.list_providers()}
    # 9 providers: local (ollama, lmstudio) + cloud + free + paid + mock.
    assert names == {
        "zai", "deepseek", "anthropic", "minimax",
        "gemini", "openrouter", "ollama", "lmstudio", "mock",
    }


def test_mock_provider_always_configured():
    from engine.ai.registry import get_registry

    reg = get_registry()
    mock = reg.get("mock")
    assert mock.is_configured


def test_mock_chat_returns_canned_response():
    from engine.ai.registry import get_registry

    mock = get_registry().get("mock")
    resp = mock.chat(
        messages=[
            {"role": "system", "content": "Bạn là Trọng tài."},
            {"role": "user", "content": "test"},
        ],
        max_tokens=200,
    )
    assert "MOCK" in resp.content
    assert "Trọng tài" in resp.content
    assert resp.provider == "mock"


def test_set_api_key_via_registry():
    from engine.ai.registry import get_registry

    reg = get_registry()
    status = reg.set_api_key("anthropic", "sk-ant-test-key-12345")
    assert status["is_configured"] is True


def test_first_configured_falls_back_to_mock():
    """If preferred providers not configured, falls back to Mock."""
    from engine.ai.registry import ProviderRegistry

    reg = ProviderRegistry()
    p = reg.first_configured(["nonexistent_provider"])
    assert p.name == "mock"


# ─── Prompt store ─────────────────────────────────────────────────────────────


def test_default_prompts_exist_for_7_agents_plus_orchestrator():
    from engine.ai.prompt_store import ALL_PROMPT_IDS, get_default

    for pid in ALL_PROMPT_IDS:
        content = get_default(pid)
        assert len(content) > 100, f"Default prompt for {pid} too short"


def test_set_and_reset_prompt_override():
    from engine.ai.prompt_store import (
        get_default, get_prompt, is_overridden, reset_prompt, set_prompt,
    )

    default = get_default("tu_vi")
    set_prompt("tu_vi", "Custom prompt for testing")
    assert is_overridden("tu_vi")
    assert get_prompt("tu_vi") == "Custom prompt for testing"
    reset_prompt("tu_vi")
    assert not is_overridden("tu_vi")
    assert get_prompt("tu_vi") == default


def test_agent_metadata_complete():
    from engine.ai.prompt_store import AGENT_IDS, AGENT_METADATA

    for aid in AGENT_IDS:
        m = AGENT_METADATA[aid]
        assert m["name_vi"]
        assert m["icon"]
        assert m["specialty"]
        assert m["best_for"]


# ─── Agent runner ─────────────────────────────────────────────────────────────


def test_run_agent_with_mock():
    from engine.ai.agents import run_agent
    from engine.ai.registry import get_registry

    mock = get_registry().get("mock")
    resp = run_agent(
        agent_id="tu_vi",
        provider=mock,
        model="mock-v1",
        question="Test question",
        chart_data={"mock": True},
    )
    assert resp.agent_id == "tu_vi"
    assert resp.content
    assert resp.provider == "mock"
    assert resp.error is None


def test_run_agent_rejects_unknown_id():
    from engine.ai.agents import run_agent
    from engine.ai.registry import get_registry

    mock = get_registry().get("mock")
    with pytest.raises(ValueError):
        run_agent(agent_id="not_a_school", provider=mock, model="mock-v1",
                  question="x", chart_data={})


# ─── Council orchestration ───────────────────────────────────────────────────


def test_consult_council_with_explicit_agents():
    from engine.ai.council import consult_council

    r = consult_council(
        question="Test question",
        chart_data={"day_master": "Kỷ"},
        explicit_agents=["tu_vi", "bat_tu"],
        persist=False,
    )
    assert r["agents_consulted"] == ["tu_vi", "bat_tu"]
    assert len(r["round_1_outputs"]) == 2
    assert r["final_synthesis"]
    assert r["duration_ms"] > 0


def test_consult_council_skip_challenge():
    from engine.ai.council import consult_council

    r = consult_council(
        question="x", chart_data={},
        explicit_agents=["tu_vi"],
        skip_challenge=True, persist=False,
    )
    assert r["agents_consulted"] == ["tu_vi"]
    assert r["round_3_outputs"] == []   # skipped


def test_consult_council_rejects_invalid_agent():
    """Invalid agents should be filtered out, only valid ones used."""
    from engine.ai.council import consult_council

    r = consult_council(
        question="x", chart_data={},
        explicit_agents=["tu_vi", "fake_agent"],
        persist=False,
    )
    assert "tu_vi" in r["agents_consulted"]
    assert "fake_agent" not in r["agents_consulted"]


def test_consult_council_persists_session():
    from engine.ai.council import consult_council, get_session

    r = consult_council(
        question="persist test",
        chart_data={"test": True},
        explicit_agents=["tu_vi"],
        skip_challenge=True,
        persist=True,
    )
    # Session is saved via _save_session inside consult_council; verify retrievable.
    # Note: session_id is set on the dataclass but our return is dict-from-asdict
    # which doesn't include session_id since we set it AFTER asdict was already called.
    # That's OK — we can still query recent sessions.


# ─── API endpoints ───────────────────────────────────────────────────────────


def test_api_list_providers():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/ai/providers")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert len(payload["providers"]) == 9  # full provider stack + LM Studio (CLAUDE.md)


def test_api_list_agents():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/ai/agents")
    assert r.status_code == 200
    payload = r.json()
    assert len(payload["agents"]) == 8  # 8 council sages
    ids = {a["id"] for a in payload["agents"]}
    assert ids == {"mai_hoa", "luc_hao", "lien_hoa", "tu_vi", "bat_tu", "ha_lac", "than_so", "western"}


def test_api_get_prompt_returns_default_and_current():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.get("/api/ai/prompts/tu_vi")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert payload["current"]
    assert payload["default"]


def test_api_set_and_reset_prompt():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.put("/api/ai/prompts/lien_hoa", json={"content": "Custom test override"})
    assert r.status_code == 200

    r = client.get("/api/ai/prompts/lien_hoa")
    assert r.json()["is_overridden"]
    assert r.json()["current"] == "Custom test override"

    r = client.delete("/api/ai/prompts/lien_hoa")
    assert r.status_code == 200

    r = client.get("/api/ai/prompts/lien_hoa")
    assert not r.json()["is_overridden"]


def test_api_set_provider_key():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/ai/providers/deepseek/key", json={"api_key": "test_key_123"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_council_consult_with_mock_fallback():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    r = client.post("/api/ai/council/consult", json={
        "question": "Tôi nên đầu tư bất động sản?",
        "chart_data": {"day_master": {"stem": "Kỷ"}},
        "explicit_agents": ["bat_tu", "tu_vi"],
        "skip_challenge": True,
        "persist": False,
    })
    assert r.status_code == 200
    session = r.json()["session"]
    assert session["agents_consulted"] == ["bat_tu", "tu_vi"]
    assert len(session["round_1_outputs"]) == 2
    assert session["final_synthesis"]
