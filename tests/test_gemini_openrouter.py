"""Tests cho GeminiProvider + OpenRouterProvider."""

from __future__ import annotations

import json
import urllib.request

import pytest


# ─── Gemini ─────────────────────────────────────────────────────────────────


def test_gemini_default(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    from engine.ai.providers.gemini import GeminiProvider
    p = GeminiProvider(api_key="")
    assert p.name == "gemini"
    assert "Gemini" in p.display_name
    assert p.is_configured is False
    assert p.default_model.startswith("gemini-2.5")


def test_gemini_picks_up_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaTEST")
    from engine.ai.providers.gemini import GeminiProvider
    p = GeminiProvider()
    assert p.is_configured is True


def test_gemini_picks_up_google_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "AIzaGOOGLE")
    from engine.ai.providers.gemini import GeminiProvider
    p = GeminiProvider()
    assert p.is_configured is True


def test_gemini_chat_no_key_raises(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    from engine.ai.providers.gemini import GeminiProvider
    from engine.ai.providers.base import ProviderError
    p = GeminiProvider(api_key="")
    with pytest.raises(ProviderError):
        p.chat(messages=[{"role": "user", "content": "hi"}])


def test_gemini_chat_parses_openai_envelope(monkeypatch):
    from engine.ai.providers.gemini import GeminiProvider

    fake = {
        "model": "gemini-2.5-flash",
        "choices": [{"message": {"role": "assistant", "content": "Xin chào!"}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
    }
    class R:
        def read(self): return json.dumps(fake).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: R())
    p = GeminiProvider(api_key="AIzaTEST")
    resp = p.chat(messages=[{"role": "user", "content": "chào"}])
    assert resp.content == "Xin chào!"
    assert resp.provider == "gemini"
    assert resp.total_tokens == 8


# ─── OpenRouter ─────────────────────────────────────────────────────────────


def test_openrouter_default(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from engine.ai.providers.openrouter import OpenRouterProvider
    p = OpenRouterProvider(api_key="")
    assert p.name == "openrouter"
    assert "free" in p.display_name.lower() or "OpenRouter" in p.display_name
    assert p.is_configured is False
    # Default must be a free tier model (suffix :free)
    assert p.default_model.endswith(":free")


def test_openrouter_picks_up_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-test")
    from engine.ai.providers.openrouter import OpenRouterProvider
    p = OpenRouterProvider()
    assert p.is_configured is True


def test_openrouter_chat_includes_referer_header(monkeypatch):
    """OpenRouter needs HTTP-Referer + X-Title for leaderboard/analytics."""
    from engine.ai.providers.openrouter import OpenRouterProvider

    captured = {}
    def fake_urlopen(req, timeout=None):
        captured["headers"] = dict(req.headers)
        class R:
            def read(self): return json.dumps({
                "model": "test", "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
            }).encode("utf-8")
            def __enter__(self): return self
            def __exit__(self, *a): return False
        return R()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    p = OpenRouterProvider(api_key="sk-or-v1-test")
    p.chat(messages=[{"role": "user", "content": "hi"}])
    # Headers are normalized to title-case by urllib
    headers_lower = {k.lower(): v for k, v in captured["headers"].items()}
    assert "http-referer" in headers_lower
    assert "x-title" in headers_lower


def test_openrouter_strips_think_block(monkeypatch):
    """OpenRouter can route to reasoning models that emit <think> tags."""
    from engine.ai.providers.openrouter import OpenRouterProvider

    fake = {
        "model": "qwen/qwen3:free",
        "choices": [{"message": {"content": "<think>reasoning</think>\nFinal answer"}}],
        "usage": {"total_tokens": 10}
    }
    class R:
        def read(self): return json.dumps(fake).encode("utf-8")
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: R())
    p = OpenRouterProvider(api_key="sk-or-v1-test")
    resp = p.chat(messages=[{"role": "user", "content": "x"}])
    assert "<think>" not in resp.content
    assert "Final answer" in resp.content


def test_openrouter_chat_no_key_raises(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    from engine.ai.providers.openrouter import OpenRouterProvider
    from engine.ai.providers.base import ProviderError
    p = OpenRouterProvider(api_key="")
    with pytest.raises(ProviderError):
        p.chat(messages=[{"role": "user", "content": "hi"}])


# ─── Registry integration ───────────────────────────────────────────────────


def test_registry_includes_gemini_and_openrouter():
    from engine.ai.registry import get_registry
    r = get_registry()
    g = r.get("gemini")
    o = r.get("openrouter")
    assert g.name == "gemini"
    assert o.name == "openrouter"


def test_list_providers_includes_new_ones():
    from engine.ai.registry import get_registry
    listing = get_registry().list_providers()
    names = {p["name"] for p in listing}
    assert "gemini" in names
    assert "openrouter" in names
    assert "minimax" in names
    assert "ollama" in names
