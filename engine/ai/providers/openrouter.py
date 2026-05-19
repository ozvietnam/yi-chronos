"""OpenRouter provider — gateway tới 200+ models, có free tier.

Endpoint: https://openrouter.ai/api/v1/chat/completions (OpenAI-compatible)
Auth: Bearer token, key prefix `sk-or-v1-...`

Free tier: nhiều model có suffix `:free` — quota giới hạn nhưng đủ test/light use:
- `meta-llama/llama-3.3-70b-instruct:free`
- `deepseek/deepseek-chat-v3.1:free`
- `google/gemini-2.0-flash-exp:free`
- `qwen/qwen-2.5-72b-instruct:free`
- `mistralai/mistral-7b-instruct:free`

Paid models cũng route qua đây — anh chỉ cần 1 key.

API key từ https://openrouter.ai/keys (cần đăng ký free).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(LLMProvider):
    """OpenRouter — universal LLM gateway với free tier."""

    # Live free models (probed 2026-05-12). Most need anh accept Privacy policy
    # at https://openrouter.ai/settings/privacy first.
    _MODELS: tuple[str, ...] = (
        # Free tier — verified working without privacy config
        "z-ai/glm-4.5-air:free",
        # Free tier — need privacy config first
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen3-coder:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "openai/gpt-oss-120b:free",
        "openai/gpt-oss-20b:free",
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        # Paid models (anh có thể chuyển khi free hết quota)
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3.5-haiku",
        "openai/gpt-4o-mini",
        "deepseek/deepseek-chat",
    )

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        site_url: str = "http://localhost:5173",
        app_title: str = "YI-Chronos",
    ):
        self._api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self._endpoint = endpoint or os.environ.get("OPENROUTER_ENDPOINT", _ENDPOINT)
        # Headers required by OpenRouter for analytics + leaderboard
        self._site_url = site_url
        self._app_title = app_title
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def display_name(self) -> str:
        return "OpenRouter (free tier + paid models)"

    @property
    def default_model(self) -> str:
        # Free + verified working without anh phải config privacy
        return "z-ai/glm-4.5-air:free"

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
                "OpenRouter: no API key. "
                "Anh paste key (sk-or-v1-...) qua tab ⚙️ Cài đặt → OpenRouter."
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
                "HTTP-Referer": self._site_url,
                "X-Title": self._app_title,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120.0) as r:
                raw = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body_err = e.read().decode("utf-8", errors="replace")
            self._last_error = f"HTTP {e.code}: {body_err[:300]}"
            raise ProviderError(f"OpenRouter {self._last_error}") from e
        except urllib.error.URLError as e:
            raise ProviderError(f"OpenRouter unreachable: {e.reason}") from e
        except Exception as e:
            raise ProviderError(f"OpenRouter error: {e}") from e

        choices = raw.get("choices") or []
        choice = choices[0] if choices else {}
        msg = choice.get("message") or {}
        content = msg.get("content", "") or ""
        # Some routed models also use reasoning <think> blocks; strip if present
        if "<think>" in content.lower():
            import re
            content = re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL).strip()
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
