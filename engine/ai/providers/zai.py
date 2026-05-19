"""ZhipuAI / z.ai provider — global GLM-4.x endpoint.

Endpoint: https://api.z.ai/api/paas/v4/chat/completions
Auth: JWT bearer from API key format `{id}.{secret}`.

Status: ZAI_API_KEY in .env.local is valid format but account may need recharge.
Models tested: glm-4.5, glm-4.5-air, glm-4-plus, glm-4.6.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

import jwt

from .base import LLMProvider, LLMResponse, ProviderError


ZAI_ENDPOINT = "https://api.z.ai/api/paas/v4/chat/completions"


class ZaiProvider(LLMProvider):
    """z.ai / ZhipuAI GLM-4.x global endpoint."""

    _MODELS: tuple[str, ...] = (
        "glm-4.5-flash",   # FREE tier — default for cost-conscious flows
        "glm-4.5-air",     # paid, cheaper
        "glm-4.5",         # paid, balanced
        "glm-4-plus",      # paid, premium
        "glm-4.6",         # paid, latest
    )

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("ZAI_API_KEY", "")
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "zai"

    @property
    def display_name(self) -> str:
        return "z.ai (ZhipuAI GLM-4.x)"

    @property
    def default_model(self) -> str:
        return "glm-4.5-flash"   # free tier — works without account balance

    @property
    def available_models(self) -> list[str]:
        return list(self._MODELS)

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and "." in self._api_key)

    def set_api_key(self, key: str) -> None:
        self._api_key = key.strip()
        self._last_error = ""

    def _make_jwt(self) -> str:
        if not self.is_configured:
            raise ProviderError("z.ai API key not set or invalid format.")
        try:
            key_id, secret = self._api_key.split(".")
        except ValueError as exc:
            raise ProviderError(f"Invalid z.ai key format (expected 'id.secret'): {exc}")
        now_ms = int(time.time() * 1000)
        return jwt.encode(
            {"api_key": key_id, "exp": now_ms + 3600 * 1000, "timestamp": now_ms},
            secret, algorithm="HS256",
            headers={"alg": "HS256", "sign_type": "SIGN"},
        )

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        model = model or self.default_model
        token = self._make_jwt()
        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }, ensure_ascii=False).encode("utf-8")

        req = urllib.request.Request(
            ZAI_ENDPOINT, data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="ignore")
            self._last_error = f"HTTP {e.code}: {msg[:200]}"
            raise ProviderError(f"z.ai {self._last_error}") from e
        except urllib.error.URLError as e:
            self._last_error = f"Network: {e}"
            raise ProviderError(f"z.ai network error: {e}") from e

        try:
            content = raw["choices"][0]["message"]["content"]
            usage = raw.get("usage", {})
        except (KeyError, IndexError) as e:
            raise ProviderError(f"Unexpected z.ai response shape: {raw}") from e

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
            "endpoint": ZAI_ENDPOINT,
            "note": (
                "Nếu gặp 1113 'Insufficient balance' → nạp tiền tại https://z.ai. "
                "Nếu gặp 1211 → kiểm tra tên model."
            ),
        }
