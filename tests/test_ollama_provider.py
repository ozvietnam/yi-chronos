"""Tests for OllamaProvider + restoration integration with local LLM.

Mostly offline-safe — uses fake HTTP server / monkey-patch instead of requiring
real Ollama install. Integration tests requiring real Ollama are skipped
gracefully if server not running.
"""

from __future__ import annotations

import json
import urllib.request
from unittest.mock import MagicMock, patch

import pytest


def test_ollama_provider_default_endpoint():
    from engine.ai.providers.ollama import OllamaProvider
    p = OllamaProvider()
    assert p.name == "ollama"
    assert "ollama" in p.display_name.lower()
    assert p.default_model.startswith("qwen") or p.default_model.startswith("llama")


def test_ollama_provider_custom_endpoint_and_model():
    from engine.ai.providers.ollama import OllamaProvider
    p = OllamaProvider(endpoint="http://example.com:11434", default_model="llama3.1:8b")
    assert p.default_model == "llama3.1:8b"
    assert "example.com" in p.display_name


def test_ollama_is_configured_caches_failure(monkeypatch):
    """If server unreachable, is_configured returns False without spamming."""
    from engine.ai.providers.ollama import OllamaProvider
    p = OllamaProvider(endpoint="http://localhost:65535")  # unlikely port
    p._configured_cache = None
    assert p.is_configured is False
    assert p._configured_cache is False
    # Second call uses cache, doesn't reconnect
    assert p.is_configured is False


def test_ollama_available_models_fallback_when_offline():
    """When server down, available_models returns curated fallback."""
    from engine.ai.providers.ollama import OllamaProvider
    p = OllamaProvider(endpoint="http://localhost:65535")
    models = p.available_models
    assert isinstance(models, list)
    assert any("qwen" in m.lower() or "llama" in m.lower() for m in models)


def test_ollama_chat_raises_provider_error_when_unreachable():
    from engine.ai.providers.ollama import OllamaProvider
    from engine.ai.providers.base import ProviderError
    p = OllamaProvider(endpoint="http://localhost:65535")
    with pytest.raises(ProviderError) as exc:
        p.chat(
            messages=[{"role": "user", "content": "hi"}],
            model="qwen2.5:7b", max_tokens=10,
        )
    assert "unreachable" in str(exc.value).lower() or "ollama" in str(exc.value).lower()


def test_ollama_chat_parses_response_correctly(monkeypatch):
    """Mock urlopen to return Ollama-style response, ensure LLMResponse populated."""
    from engine.ai.providers.ollama import OllamaProvider

    fake_payload = {
        "model": "qwen2.5:7b",
        "message": {"role": "assistant", "content": "Trả lời thử nghiệm."},
        "done": True,
        "prompt_eval_count": 15,
        "eval_count": 42,
    }

    class FakeResp:
        def __init__(self):
            self.status = 200
            self._data = json.dumps(fake_payload).encode("utf-8")
        def read(self):
            return self._data
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        return FakeResp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    p = OllamaProvider()
    resp = p.chat(messages=[{"role": "user", "content": "test"}], model="qwen2.5:7b")
    assert resp.content == "Trả lời thử nghiệm."
    assert resp.provider == "ollama"
    assert resp.model == "qwen2.5:7b"
    assert resp.prompt_tokens == 15
    assert resp.completion_tokens == 42
    assert resp.total_tokens == 57


def test_registry_includes_ollama():
    from engine.ai.registry import get_registry
    r = get_registry()
    p = r.get("ollama")
    assert p.name == "ollama"


def test_registry_first_configured_skips_unreachable_ollama(monkeypatch):
    """If ollama unreachable and no API keys → falls back to mock."""
    from engine.ai.registry import ProviderRegistry
    r = ProviderRegistry()
    # Force ollama to be unconfigured (fresh instance with unlikely port)
    from engine.ai.providers.ollama import OllamaProvider
    r._providers["ollama"] = OllamaProvider(endpoint="http://localhost:65535")
    # And clear API keys so cloud providers are also unconfigured
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Reset their key state
    r._providers["deepseek"]._api_key = ""
    if hasattr(r._providers["zai"], "_api_key"):
        r._providers["zai"]._api_key = ""
    if hasattr(r._providers["anthropic"], "_api_key"):
        r._providers["anthropic"]._api_key = ""
    chosen = r.first_configured(preferred_order=["ollama", "deepseek", "zai", "anthropic"])
    assert chosen.name == "mock"


def test_ocr_backend_factory_supports_ollama_vision():
    from engine.yi_lexicon.restoration.ocr_backends import (
        get_backend, OllamaVisionBackend
    )
    b = get_backend("qwen-vl")
    assert isinstance(b, OllamaVisionBackend)
    assert b.model == "qwen2.5vl:7b"
    b2 = get_backend("minicpm-v")
    assert b2.model == "minicpm-v:8b"
    b3 = get_backend("ollama-vision", model="custom-model:1b")
    assert b3.model == "custom-model:1b"


def test_ocr_backend_factory_rejects_lang_kwarg_for_vl():
    """VL backend should silently drop the `lang` kwarg (Tesseract-only)."""
    from engine.yi_lexicon.restoration.ocr_backends import get_backend
    # Should NOT raise
    b = get_backend("qwen-vl", lang="vie")
    assert b.name == "ollama-vision"


def test_ollama_vision_backend_returns_error_when_unreachable(tmp_path):
    """ocr_page returns OcrPageResult with errors, not raising."""
    from engine.yi_lexicon.restoration.ocr_backends import OllamaVisionBackend
    # Create a dummy PNG (1×1 black pixel)
    png = tmp_path / "test.png"
    png.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xfa\xcf\xc0"
        b"\x00\x00\x00\x03\x00\x01\xa9\x80\x07\xa7\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    b = OllamaVisionBackend(endpoint="http://localhost:65535", timeout=2)
    r = b.ocr_page(png)
    assert r.backend == "ollama-vision"
    assert r.text == ""
    assert len(r.errors) > 0


def test_nightly_queue_priority_order(tmp_path, monkeypatch):
    """select_queue: tier S+partial sorted before tier B+none."""
    from engine.yi_lexicon import store as st
    db = tmp_path / "lex.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    st.bootstrap_db()

    s_done = st.add_corpus(name="S Done", tier="S", file_path="/tmp/x.pdf",
                           pages_total=100)
    st.update_corpus(s_done.corpus_id, restored_status="done")

    s_partial = st.add_corpus(name="S Partial", tier="S", file_path="/tmp/y.pdf",
                              pages_total=100)
    st.update_corpus(s_partial.corpus_id, restored_status="partial", restored_pages=50)

    a_none = st.add_corpus(name="A None", tier="A", file_path="/tmp/a.pdf",
                           pages_total=100)
    b_none = st.add_corpus(name="B None", tier="B", file_path="/tmp/b.pdf",
                           pages_total=100)

    from engine.yi_lexicon.restoration.nightly import select_queue
    queue = select_queue(tiers=["S", "A", "B"])
    names = [c.name for c in queue]
    # S Partial first (partial wins), then S None (none — but S Done skipped), then A, then B
    assert "S Done" not in names  # done skipped
    assert names[0] == "S Partial"  # partial bumped to top
    # then A None (tier A higher than B)
    assert names.index("A None") < names.index("B None")


def test_nightly_dry_run(tmp_path, monkeypatch):
    from engine.yi_lexicon import store as st
    db = tmp_path / "lex.sqlite3"
    monkeypatch.setattr(st, "_DB_PATH", db)
    st.bootstrap_db()
    st.add_corpus(name="Test Book", tier="S", file_path="/tmp/test.pdf")

    from engine.yi_lexicon.restoration.nightly import run_nightly
    summary = run_nightly(
        max_hours=0.01, tiers=["S"], dry_run=True,
        provider="ollama", ocr_backend="tesseract",
    )
    assert summary["dry_run"] is True
    assert summary["queue_size"] == 1
