"""DeepSeek provider — OpenAI-compatible API.

Endpoint: https://api.deepseek.com/v1/chat/completions
Auth: Bearer token (plain API key).

Models:
- deepseek-chat — general purpose (V3)
- deepseek-reasoner — R1, reasoning-optimized (for Đông agents)
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


ENDPOINT = "https://api.deepseek.com/v1/chat/completions"


class DeepSeekProvider(LLMProvider):
    _MODELS: tuple[str, ...] = (
        "deepseek-v4-pro",     # V4 Pro — flagship quality (anh dùng cho VIP)
        "deepseek-v4-flash",   # V4 Flash — fast cheap
        "deepseek-chat",       # V3 general (legacy)
        "deepseek-reasoner",   # R1 reasoning (legacy)
    )

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "deepseek"

    @property
    def display_name(self) -> str:
        return "DeepSeek (V4 Pro / V4 Flash)"

    @property
    def default_model(self) -> str:
        return "deepseek-v4-pro"

    @property
    def available_models(self) -> list[str]:
        return list(self._MODELS)

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def set_api_key(self, key: str) -> None:
        self._api_key = key.strip()
        self._last_error = ""

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
        reasoning_effort: str | None = None,  # 'none'|'low'|'medium'|'high'
    ) -> LLMResponse:
        if not self.is_configured:
            raise ProviderError("DEEPSEEK_API_KEY not set.")
        model = model or self.default_model
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        # V4 Pro: reasoning ON by default (depth). Caller can pass reasoning_effort='none'
        # for extraction tasks to skip reasoning chain (faster, cheaper).
        if reasoning_effort and model and "pro" in model.lower():
            payload["reasoning"] = {"effort": reasoning_effort}
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            ENDPOINT, data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="ignore")
            self._last_error = f"HTTP {e.code}: {msg[:200]}"
            raise ProviderError(f"DeepSeek {self._last_error}") from e
        except urllib.error.URLError as e:
            self._last_error = f"Network: {e}"
            raise ProviderError(f"DeepSeek network: {e}") from e

        try:
            content = raw["choices"][0]["message"]["content"]
            usage = raw.get("usage", {})
        except (KeyError, IndexError) as e:
            raise ProviderError(f"Unexpected DeepSeek response: {raw}") from e

        return LLMResponse(
            content=content,
            provider=self.name,
            model=raw.get("model", model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            raw=raw,
        )

    def status(self) -> dict:
        return {
            **super().status(),
            "last_error": self._last_error,
            "endpoint": ENDPOINT,
            "note": "Lấy key tại https://platform.deepseek.com",
        }
