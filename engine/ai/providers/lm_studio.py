"""LM Studio provider — local LLM Mac M4.

Endpoint: http://localhost:1234/v1/chat/completions (OpenAI-compatible)
KHÔNG cần API key. Privacy-first: data Tử Vi KHÔNG leak ra cloud.

Models available (2026-06-09):
- glm-z1-32b-0414            — GLM reasoning 32B (mạnh Trung văn)
- qwen3-30b-a3b-thinking     — Qwen thinking 30B MLX
- qwen3-coder-30b-instruct   — Qwen coder
- google/gemma-4-e4b         — Gemma 4
- text-embedding-nomic       — embedding model

Use case: việc QUAN TRỌNG (anh chốt 2026-06-09 KHÔNG dùng minimal).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


DEFAULT_ENDPOINT = "http://localhost:1234/v1/chat/completions"


class LMStudioProvider(LLMProvider):
    """Local LM Studio. No API key, OpenAI-compatible."""

    _MODELS: tuple[str, ...] = (
        "qwen3-30b-a3b-thinking-2507-mlx",      # default — thinking model best cho Tử Vi
        "glm-z1-32b-0414",                       # GLM Z1 reasoning
        "qwen3-coder-30b-a3b-instruct-mlx",      # coder model
        "google/gemma-4-e4b",                    # Gemma 4
    )

    def __init__(self, endpoint: str | None = None, timeout: float = 600.0):
        self._endpoint = endpoint or os.environ.get("LM_STUDIO_ENDPOINT", DEFAULT_ENDPOINT)
        self._timeout = timeout
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "lm_studio"

    @property
    def display_name(self) -> str:
        return "LM Studio (local Mac M4)"

    @property
    def default_model(self) -> str:
        # qwen3-thinking = reasoning + MLX optimized for Mac M4
        return "qwen3-30b-a3b-thinking-2507-mlx"

    @property
    def available_models(self) -> list[str]:
        return list(self._MODELS)

    @property
    def is_configured(self) -> bool:
        return True  # local, no key

    def set_api_key(self, key: str) -> None:
        pass  # no key needed

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 4000,
        reasoning_effort: str | None = None,  # accepted but ignored (LM Studio handles internally)
    ) -> LLMResponse:
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="ignore")
            self._last_error = f"HTTP {e.code}: {err[:300]}"
            raise ProviderError(f"LM Studio {self._last_error}") from e
        except urllib.error.URLError as e:
            self._last_error = f"Network: {e}"
            raise ProviderError(f"LM Studio unreachable: {e}") from e
        except Exception as e:
            raise ProviderError(f"LM Studio error: {e}") from e

        try:
            message = raw["choices"][0]["message"]
            content = message.get("content") or ""
            # Thinking models (qwen3-thinking) put reasoning in separate field
            # If content empty but reasoning exists → response truncated mid-think, use reasoning
            if not content.strip() and message.get("reasoning_content"):
                # Take reasoning as content (it's the model's working)
                content = "[REASONING_TRUNCATED]\n" + message["reasoning_content"]
            usage = raw.get("usage", {})
        except (KeyError, IndexError) as e:
            raise ProviderError(f"Unexpected LM Studio response: {raw}") from e

        # Strip <think>...</think> tags if present
        if "<think>" in content and "</think>" in content:
            think_end = content.find("</think>") + len("</think>")
            content_clean = content[think_end:].strip()
            if content_clean:
                content = content_clean

        return LLMResponse(
            content=content,
            provider=self.name,
            model=raw.get("model", target_model),
            prompt_tokens=usage.get("prompt_tokens", 0) or 0,
            completion_tokens=usage.get("completion_tokens", 0) or 0,
            total_tokens=usage.get("total_tokens", 0) or 0,
            raw=raw,
        )
