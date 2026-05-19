"""Google Gemini provider — via OpenAI-compatible endpoint.

Google AI Studio (free tier) exposes an OpenAI-compat endpoint:
    https://generativelanguage.googleapis.com/v1beta/openai/chat/completions

Free tier (as of 2026):
- gemini-2.5-flash: 10 RPM, 250 RPD, 1M TPD
- gemini-2.5-pro:   5 RPM, 100 RPD
- gemini-2.0-flash: 15 RPM, 1500 RPD

API key from https://aistudio.google.com/apikey (free, no credit card).
Format: `AIza...` (39 chars).

Paste qua tab ⚙️ Cài đặt → Gemini → API Key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


class GeminiProvider(LLMProvider):
    """Google Gemini via OpenAI-compatible endpoint."""

    _MODELS: tuple[str, ...] = (
        "gemini-2.5-flash",            # fast + smart, free tier friendly
        "gemini-2.5-pro",              # flagship, slower
        "gemini-2.0-flash",            # fastest, large free quota
        "gemini-2.0-flash-thinking-exp",  # reasoning
        "gemini-1.5-flash",            # legacy stable
        "gemini-1.5-pro",              # legacy flagship
    )

    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY", "") \
                                or os.environ.get("GOOGLE_API_KEY", "")
        self._endpoint = endpoint or os.environ.get("GEMINI_ENDPOINT", _ENDPOINT)
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini (AI Studio)"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    @property
    def available_models(self) -> list[str]:
        return list(self._MODELS)

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def set_api_key(self, key: str) -> None:
        self._api_key = (key or "").strip()

    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        if not self._api_key:
            raise ProviderError(
                "Gemini: no API key. "
                "Anh paste key qua tab ⚙️ Cài đặt → Gemini → API Key."
            )
        target_model = model or self.default_model
        body = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        req = urllib.request.Request(
            self._endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120.0) as r:
                raw = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_err = e.read().decode("utf-8", errors="replace")
            self._last_error = f"HTTP {e.code}: {body_err[:300]}"
            raise ProviderError(f"Gemini {self._last_error}") from e
        except urllib.error.URLError as e:
            raise ProviderError(f"Gemini unreachable: {e.reason}") from e
        except Exception as e:
            raise ProviderError(f"Gemini error: {e}") from e

        choices = raw.get("choices") or []
        choice = choices[0] if choices else {}
        msg = choice.get("message") or {}
        content = msg.get("content", "") or ""
        usage = raw.get("usage") or {}
        return LLMResponse(
            content=content,
            provider=self.name,
            model=raw.get("model", target_model),
            prompt_tokens=usage.get("prompt_tokens", 0) or 0,
            completion_tokens=usage.get("completion_tokens", 0) or 0,
            total_tokens=usage.get("total_tokens", 0) or 0,
            raw=raw,
        )
