"""LM Studio provider — local OpenAI-compatible server (no auth).

LM Studio exposes `/v1/chat/completions` + `/v1/models` on localhost:1234. Used as a
free LOCAL fallback (dev / when cloud keys are down). On prod (no LM Studio) the
provider reports not-configured, so callers fall through to cloud providers.

Config: YI_LMSTUDIO_URL (default http://localhost:1234/v1), YI_LMSTUDIO_MODEL
(default an instruct model good at structured JSON).
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError

_BASE_URL = os.environ.get("YI_LMSTUDIO_URL", "http://localhost:1234/v1").rstrip("/")
_DEFAULT_MODEL = os.environ.get("YI_LMSTUDIO_MODEL", "qwen3-coder-30b-a3b-instruct-mlx")
# Reasoning models (qwen3-thinking, glm-z1) wrap output in <think>…</think>.
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


class LMStudioProvider(LLMProvider):
    def __init__(self, base_url: str | None = None, default_model: str | None = None):
        self._base_url = (base_url or _BASE_URL).rstrip("/")
        self._default_model = default_model or _DEFAULT_MODEL

    @property
    def name(self) -> str:
        return "lmstudio"

    @property
    def display_name(self) -> str:
        return f"LM Studio (local @ {self._base_url})"

    @property
    def default_model(self) -> str:
        return self._default_model

    @property
    def available_models(self) -> list[str]:
        try:
            req = urllib.request.Request(f"{self._base_url}/models")
            with urllib.request.urlopen(req, timeout=3) as r:
                data = json.load(r)
            return [m["id"] for m in data.get("data", []) if "embedding" not in m["id"].lower()]
        except Exception:
            return []

    @property
    def is_configured(self) -> bool:
        """True only if the local server actually answers (so prod falls through)."""
        try:
            req = urllib.request.Request(f"{self._base_url}/models")
            with urllib.request.urlopen(req, timeout=2) as r:
                return r.status == 200
        except Exception:
            return False

    def chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **_kwargs,
    ) -> LLMResponse:
        mdl = model or self._default_model
        body = json.dumps({
            "model": mdl,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
        except Exception as e:  # noqa: BLE001
            raise ProviderError(f"LM Studio unreachable @ {self._base_url}: {e}") from e
        choices = data.get("choices") or []
        content = _THINK_RE.sub("", (choices[0]["message"]["content"] if choices else "")).strip()
        usage = data.get("usage") or {}
        return LLMResponse(
            content=content,
            provider=self.name,
            model=mdl,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )
