"""Anthropic Claude provider — Sonnet (agents) + Opus (Trọng tài).

Endpoint: https://api.anthropic.com/v1/messages
Auth: x-api-key header.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class AnthropicProvider(LLMProvider):
    _MODELS: tuple[str, ...] = (
        "claude-opus-4-5-20250929",         # Opus 4.5 - Trọng tài
        "claude-sonnet-4-5-20250929",       # Sonnet 4.5 - agents
        "claude-haiku-4-5-20250929",        # Haiku - cheap
        # Older snapshots for fallback
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
    )

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def display_name(self) -> str:
        return "Anthropic Claude (Opus + Sonnet + Haiku)"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-5-20250929"

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
    ) -> LLMResponse:
        if not self.is_configured:
            raise ProviderError("ANTHROPIC_API_KEY not set.")
        model = model or self.default_model

        # Anthropic format: system is separate, no role 'system' in messages list.
        system = ""
        msgs: list[dict] = []
        for m in messages:
            if m["role"] == "system":
                system = (system + "\n\n" + m["content"]).strip()
            else:
                msgs.append({"role": m["role"], "content": m["content"]})

        body_dict = {
            "model": model,
            "messages": msgs,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system:
            body_dict["system"] = system
        body = json.dumps(body_dict, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            ENDPOINT, data=body,
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="ignore")
            self._last_error = f"HTTP {e.code}: {msg[:200]}"
            raise ProviderError(f"Anthropic {self._last_error}") from e
        except urllib.error.URLError as e:
            self._last_error = f"Network: {e}"
            raise ProviderError(f"Anthropic network: {e}") from e

        try:
            content = raw["content"][0]["text"]
            usage = raw.get("usage", {})
            prompt_tokens = usage.get("input_tokens", 0)
            completion_tokens = usage.get("output_tokens", 0)
        except (KeyError, IndexError) as e:
            raise ProviderError(f"Unexpected Anthropic response: {raw}") from e

        return LLMResponse(
            content=content,
            provider=self.name,
            model=raw.get("model", model),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            raw=raw,
        )

    def status(self) -> dict:
        return {
            **super().status(),
            "last_error": self._last_error,
            "endpoint": ENDPOINT,
            "note": "Lấy key tại https://console.anthropic.com (cùng tài khoản Claude Desktop).",
        }
