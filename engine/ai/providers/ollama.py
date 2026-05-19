"""Ollama provider — local LLM via Ollama HTTP API.

Endpoint: http://localhost:11434/api/chat (OpenAI-compatible chat completions)
No auth needed (localhost).

Use case: anh chạy Mac M4 36GB → cài Ollama → pull model 7B/8B → restoration pipeline
dùng provider này thay DeepSeek cho 8000+ trang nightly batch.

Recommended models for YI-Chronos:
- qwen2.5:7b           — best Vietnamese + Hán (text cleanup)
- qwen2.5:14b          — higher quality, 9GB
- qwen2.5-vl:7b        — vision-OCR (replaces Tesseract — Phase B)
- llama3.1:8b          — general fallback
- minicpm-v:8b         — Chinese OCR specialist

Cost: $0 (local).
Speed on M4 24-core GPU: 30-60 tok/s for 7B Q4_K_M.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


DEFAULT_ENDPOINT = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


class OllamaProvider(LLMProvider):
    """Talks to a local Ollama server via /api/chat."""

    _MODELS: tuple[str, ...] = (
        "qwen2.5:7b",
        "qwen2.5:14b",
        "qwen2.5-vl:7b",
        "qwen2.5:7b-instruct-q5_K_M",
        "llama3.1:8b",
        "llama3.2:3b",
        "minicpm-v:8b",
        "gemma2:9b",
        "phi3.5:3.8b",
    )

    def __init__(self, endpoint: str | None = None, default_model: str | None = None):
        self._endpoint = (endpoint or DEFAULT_ENDPOINT).rstrip("/")
        self._default_model = default_model or os.environ.get(
            "OLLAMA_DEFAULT_MODEL", "qwen3:32b"
        )
        self._last_error: str = ""
        self._configured_cache: bool | None = None
        self._cache_until: float = 0.0

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return f"Ollama (local @ {self._endpoint})"

    @property
    def default_model(self) -> str:
        return self._default_model

    @property
    def available_models(self) -> list[str]:
        """Return list of model names installed on the local server.

        Falls back to a curated list if the server is unreachable.
        """
        live = self._list_installed_models()
        if live:
            return live
        return list(self._MODELS)

    @property
    def is_configured(self) -> bool:
        """Check if Ollama server is reachable. Cached for 30s to avoid spam."""
        now = time.time()
        if self._configured_cache is not None and now < self._cache_until:
            return self._configured_cache
        try:
            req = urllib.request.Request(f"{self._endpoint}/api/tags")
            with urllib.request.urlopen(req, timeout=2.0) as r:
                self._configured_cache = (r.status == 200)
        except Exception as e:
            self._last_error = str(e)
            self._configured_cache = False
        self._cache_until = now + 30
        return self._configured_cache

    # ─── Internals ───────────────────────────────────────────────────────

    def _list_installed_models(self) -> list[str]:
        try:
            req = urllib.request.Request(f"{self._endpoint}/api/tags")
            with urllib.request.urlopen(req, timeout=3.0) as r:
                data = json.loads(r.read().decode("utf-8"))
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        except Exception:
            return []

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        """Send chat completion to Ollama. Blocking (not streamed)."""
        target_model = model or self._default_model
        body = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self._endpoint}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=600.0) as r:  # local can be slow on big prompts
                raw = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_err = e.read().decode("utf-8", errors="replace")
            raise ProviderError(f"Ollama HTTP {e.code}: {body_err}") from e
        except urllib.error.URLError as e:
            raise ProviderError(
                f"Ollama unreachable @ {self._endpoint} — chạy `ollama serve`? "
                f"({e.reason})"
            ) from e
        except Exception as e:
            raise ProviderError(f"Ollama error: {e}") from e

        content = (raw.get("message") or {}).get("content", "")
        prompt_tokens = raw.get("prompt_eval_count", 0) or 0
        completion_tokens = raw.get("eval_count", 0) or 0
        return LLMResponse(
            content=content,
            provider=self.name,
            model=target_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            raw=raw,
        )

    def pull_model(self, model: str) -> dict:
        """Trigger Ollama to download a model. Returns status dict.

        Useful to call from setup script: provider.pull_model("qwen2.5:7b").
        """
        try:
            req = urllib.request.Request(
                f"{self._endpoint}/api/pull",
                data=json.dumps({"name": model, "stream": False}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1800.0) as r:
                return {"status": "ok", "raw": r.read().decode("utf-8")[:500]}
        except Exception as e:
            return {"status": "error", "error": str(e)}
