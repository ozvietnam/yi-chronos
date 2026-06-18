"""Tests cho MiniMaxProvider — OpenAI-compat, route by key prefix."""

from __future__ import annotations

import json
import urllib.request

import pytest


def test_minimax_provider_default(monkeypatch):
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="")
    assert p.name == "minimax"
    assert "MiniMax" in p.display_name
    assert p.is_configured is False


def test_minimax_with_key():
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="sk-abcdef")
    assert p.is_configured is True
    # General key → MiniMax-M1 default
    assert p.default_model == "MiniMax-M1"


def test_minimax_coding_plan_default_model():
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="sk-cp-test123")
    # Coding plan → MiniMax-M3 (chủ lực 2026-06, newest flagship reasoning)
    assert p.default_model == "MiniMax-M3"
    assert "Coding Plan" in p.display_name


def test_minimax_chat_strips_think_in_response(monkeypatch):
    """Ensure M2 <think> blocks are removed from final content."""
    from engine.ai.providers.minimax import MiniMaxProvider

    fake_payload = {
        "model": "MiniMax-M2",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "<think>User wants OK. Let me say OK.</think>\nOK",
            },
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }

    class FakeResp:
        def read(self):
            return json.dumps(fake_payload).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp())
    p = MiniMaxProvider(api_key="sk-cp-test")
    resp = p.chat(messages=[{"role": "user", "content": "say OK"}], model="MiniMax-M2")
    assert "<think>" not in resp.content
    assert "OK" in resp.content
    assert "User wants OK" not in resp.content  # reasoning text removed


def test_minimax_endpoint_routing():
    from engine.ai.providers.minimax import _resolve_endpoint, _ENDPOINT_CODING_PLAN, _ENDPOINT_GENERAL
    assert _resolve_endpoint("sk-cp-test") == _ENDPOINT_CODING_PLAN
    assert _resolve_endpoint("sk-test") == _ENDPOINT_GENERAL
    assert _resolve_endpoint("anything", override="https://custom.example.com") == "https://custom.example.com"
    # Coding plan should hit api.minimax.io (OpenAI-style)
    assert "api.minimax.io" in _ENDPOINT_CODING_PLAN
    assert "chat/completions" in _ENDPOINT_CODING_PLAN


def test_minimax_strip_think_block():
    from engine.ai.providers.minimax import _strip_think
    assert _strip_think("<think>reasoning here</think>Hello") == "Hello"
    assert _strip_think("<think>multi\nline\nreasoning</think>\n\nAnswer text") == "Answer text"
    assert _strip_think("No think tag here") == "No think tag here"
    assert _strip_think("") == ""


def test_minimax_chat_no_key_raises(monkeypatch):
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    from engine.ai.providers.minimax import MiniMaxProvider
    from engine.ai.providers.base import ProviderError
    p = MiniMaxProvider(api_key="")
    with pytest.raises(ProviderError) as exc:
        p.chat(messages=[{"role": "user", "content": "hi"}])
    assert "no API key" in str(exc.value).lower() or "API key" in str(exc.value)


def test_minimax_chat_parses_response(monkeypatch):
    from engine.ai.providers.minimax import MiniMaxProvider

    fake_payload = {
        "id": "chatcmpl-test",
        "model": "MiniMax-M1",
        "choices": [{
            "message": {"role": "assistant", "content": "Test response."},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 12, "completion_tokens": 24, "total_tokens": 36},
    }

    class FakeResp:
        def __init__(self):
            self.status = 200
            self._data = json.dumps(fake_payload).encode("utf-8")
        def read(self): return self._data
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp())
    p = MiniMaxProvider(api_key="sk-test")
    resp = p.chat(messages=[{"role": "user", "content": "test"}])
    assert resp.content == "Test response."
    assert resp.provider == "minimax"
    assert resp.prompt_tokens == 12
    assert resp.completion_tokens == 24
    assert resp.total_tokens == 36


def test_minimax_chat_handles_multimodal_content(monkeypatch):
    """If MiniMax returns content as list of parts (vision), concatenate text."""
    from engine.ai.providers.minimax import MiniMaxProvider

    fake_payload = {
        "model": "coding-plan-vlm",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Part 1 "},
                    {"type": "text", "text": "Part 2."},
                ],
            },
        }],
        "usage": {"prompt_tokens": 5, "completion_tokens": 8, "total_tokens": 13},
    }

    class FakeResp:
        def read(self): return json.dumps(fake_payload).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: FakeResp())
    p = MiniMaxProvider(api_key="sk-cp-test")
    resp = p.chat(messages=[{"role": "user", "content": "vision test"}])
    assert "Part 1" in resp.content and "Part 2" in resp.content


def test_minimax_chat_http_error_wrapped(monkeypatch):
    from engine.ai.providers.minimax import MiniMaxProvider
    from engine.ai.providers.base import ProviderError
    import urllib.error

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            url=req.full_url, code=401, msg="Unauthorized",
            hdrs={}, fp=__import__("io").BytesIO(b'{"error":"invalid key"}')
        )

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    p = MiniMaxProvider(api_key="sk-invalid")
    with pytest.raises(ProviderError) as exc:
        p.chat(messages=[{"role": "user", "content": "x"}])
    assert "401" in str(exc.value)


def test_minimax_set_api_key_at_runtime(monkeypatch):
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="")
    assert p.is_configured is False
    p.set_api_key("sk-cp-newkey")
    assert p.is_configured is True
    assert p.default_model == "MiniMax-M3"


def test_minimax_set_api_key_strips_whitespace():
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="")
    p.set_api_key("  sk-cp-test  \n")
    assert p._api_key == "sk-cp-test"


def test_registry_includes_minimax():
    from engine.ai.registry import get_registry
    p = get_registry().get("minimax")
    assert p.name == "minimax"


def test_minimax_available_models():
    from engine.ai.providers.minimax import MiniMaxProvider
    p = MiniMaxProvider(api_key="sk-cp-test")
    models = p.available_models
    assert "coding-plan-vlm" in models
    assert "coding-plan-search" in models
    assert "MiniMax-M1" in models


def test_minimax_endpoint_env_override(monkeypatch):
    from engine.ai.providers.minimax import MiniMaxProvider
    monkeypatch.setenv("MINIMAX_ENDPOINT", "https://custom.example.com/v1/chat")
    p = MiniMaxProvider(api_key="sk-cp-test")
    assert p._endpoint_override == "https://custom.example.com/v1/chat"
