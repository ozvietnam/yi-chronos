"""MiniMax provider — Hailuo / MiniMax M1 / Coding Plan via OpenAI-compatible API.

Endpoint variants:
- Token Plan (Coding Plan): https://api.minimaxi.com/v1/text/chatcompletion_v2
  with key prefix `sk-cp-...` — has Text/Coding/VLM/Search models.
- General API: https://api.minimax.chat/v1/text/chatcompletion_v2
  with key prefix `sk-...`

Both use OpenAI-style chat completions. We auto-route based on key prefix.

Coding-plan exclusive models (per platform.minimax.io dashboard):
- coding-plan-vlm     → vision-language for coding contexts
- coding-plan-search  → web-search aware coding
- (text generation slot — model name "abab6.5s-chat" or "MiniMax-M1")

To use: anh paste key vào tab ⚙️ Cài đặt → field "API Key" của provider "minimax".
KHÔNG hardcode key vào code/env.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from .base import LLMProvider, LLMResponse, ProviderError


# MiniMax-M2 (reasoning model) prepends `<think>...</think>` block before the
# actual answer. Strip it so downstream JSON-parsing prompts work cleanly.
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def _strip_think(text: str) -> str:
    return _THINK_RE.sub("", text or "").strip()


# Three known MiniMax endpoints (probed 2026-05-12)
# - sk-cp-* (Token Plan / Coding Plan) → `api.minimax.io/v1/chat/completions` (OpenAI-style)
#   supports: MiniMax-M2 (reasoning, returns <think> blocks)
# - General sk-* → `api.minimaxi.com/v1/text/chatcompletion_v2` (legacy v2 format)
_ENDPOINT_CODING_PLAN = "https://api.minimax.io/v1/chat/completions"
_ENDPOINT_GENERAL     = "https://api.minimaxi.com/v1/text/chatcompletion_v2"


def _resolve_endpoint(api_key: str, override: str | None = None) -> str:
    """Auto-pick endpoint by key prefix. Anh override via MINIMAX_ENDPOINT env."""
    if override:
        return override
    if api_key.startswith("sk-cp-"):
        return _ENDPOINT_CODING_PLAN
    return _ENDPOINT_GENERAL


class MiniMaxProvider(LLMProvider):
    """MiniMax (Hailuo) LLM provider — supports Coding Plan + General API."""

    # Curated list of models (probed 2026-05-12 against sk-cp- key)
    _MODELS: tuple[str, ...] = (
        "MiniMax-M2",                 # ✓ Token Plan main — reasoning w/ <think>
        "minimax-m2",                  # ✓ lowercase alias
        "MiniMax-M1",                  # flagship reasoning (general API only)
        "MiniMax-Text-01",             # general text
        "coding-plan-vlm",             # vision-aware coding (token plan only)
        "coding-plan-search",          # search-aware coding (token plan only)
    )

    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self._api_key = api_key or os.environ.get("MINIMAX_API_KEY", "")
        self._endpoint_override = endpoint or os.environ.get("MINIMAX_ENDPOINT", "")
        self._last_error: str = ""

    @property
    def name(self) -> str:
        return "minimax"

    @property
    def display_name(self) -> str:
        ep_hint = "Coding Plan" if self._api_key.startswith("sk-cp-") else "General"
        return f"MiniMax / Hailuo ({ep_hint})"

    @property
    def default_model(self) -> str:
        # Coding plan keys → default to MiniMax-M2 (text reasoning, working slot)
        # Note: coding-plan-vlm needs image input; M2 is best for text-only cleanup.
        if self._api_key.startswith("sk-cp-"):
            return "MiniMax-M2"
        return "MiniMax-M1"

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
                "MiniMax: no API key configured. "
                "Anh paste key qua tab ⚙️ Cài đặt → MiniMax → API Key."
            )
        endpoint = _resolve_endpoint(self._api_key, self._endpoint_override)
        target_model = model or self.default_model
        body = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
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
            raise ProviderError(f"MiniMax {self._last_error}") from e
        except urllib.error.URLError as e:
            self._last_error = f"unreachable: {e.reason}"
            raise ProviderError(f"MiniMax {self._last_error}") from e
        except Exception as e:
            self._last_error = f"{type(e).__name__}: {e}"
            raise ProviderError(f"MiniMax error: {e}") from e

        # MiniMax follows OpenAI-style envelope
        choices = raw.get("choices") or []
        choice = choices[0] if choices else {}
        message = choice.get("message") or {}
        content = message.get("content", "") or ""
        if isinstance(content, list):
            # Vision/multimodal sometimes returns parts; concatenate text parts.
            parts = [p.get("text", "") for p in content if isinstance(p, dict)]
            content = "".join(parts)
        # Strip <think>...</think> for M2 (reasoning model) — downstream code
        # expects clean answer text, not the reasoning trace.
        if "<think>" in content.lower():
            content = _strip_think(content)
        # If choices is null (some Token Plan endpoints), try `reply` field
        if not content and raw.get("reply"):
            content = _strip_think(str(raw["reply"]))

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
