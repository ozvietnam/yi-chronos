"""ZhipuAI (智谱 AI) GLM-4 client — minimal HTTP wrapper.

Auth: ZhipuAI uses JWT bearer tokens generated from API key `{id}.{secret}`.
Endpoint: https://open.bigmodel.cn/api/paas/v4/chat/completions

Reference: https://bigmodel.cn/dev/api/normal-model/glm-4

Why ZhipuAI:
- Tiếng Việt + Chinese cosmology knowledge native (GLM-4 trained on Chinese classics).
- Pricing: GLM-4-Flash is free; GLM-4-Air ~0.001 ¥/1k tokens.
- Available in this project via ZAI_API_KEY env var.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

import jwt


ZAI_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# Models (cheapest first)
MODEL_FLASH = "glm-4-flash"    # free tier
MODEL_AIR = "glm-4-air"        # 0.001 ¥/1k tokens
MODEL_PLUS = "glm-4-plus"      # 0.05 ¥/1k tokens — best quality

DEFAULT_MODEL = MODEL_FLASH


class ZaiError(RuntimeError):
    """ZhipuAI API errors."""


def _make_jwt(api_key: str, expires_in: int = 3600) -> str:
    """Generate JWT bearer token from ZhipuAI API key `{id}.{secret}`."""
    try:
        key_id, secret = api_key.split(".")
    except ValueError as exc:
        raise ZaiError(f"Invalid ZAI_API_KEY format (expected 'id.secret'): {exc}")

    now_ms = int(time.time() * 1000)
    payload = {
        "api_key": key_id,
        "exp": now_ms + expires_in * 1000,
        "timestamp": now_ms,
    }
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )


def get_api_key() -> str | None:
    """Read ZAI_API_KEY from environment (loaded from .env.local at app startup)."""
    return os.environ.get("ZAI_API_KEY")


@dataclass(frozen=True)
class ChatResponse:
    """Wrapped GLM-4 chat completion response."""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    raw: dict

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


def chat(
    *,
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.6,
    max_tokens: int = 1500,
    api_key: str | None = None,
    timeout: int = 60,
) -> ChatResponse:
    """Send a chat-completion request to ZhipuAI.

    Args:
        messages: list of {role, content} dicts (system / user / assistant).
        model: glm-4-flash | glm-4-air | glm-4-plus.
        temperature: 0..1.
        max_tokens: output budget.
        api_key: override env. If None, reads ZAI_API_KEY.
        timeout: seconds.

    Returns: ChatResponse.

    Raises: ZaiError on API failure.
    """
    key = api_key or get_api_key()
    if not key:
        raise ZaiError("ZAI_API_KEY not set (check .env.local or env).")

    token = _make_jwt(key)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        ZAI_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise ZaiError(f"ZhipuAI HTTP {e.code}: {msg}") from e
    except urllib.error.URLError as e:
        raise ZaiError(f"ZhipuAI network error: {e}") from e

    if "error" in raw:
        raise ZaiError(f"ZhipuAI API error: {raw['error']}")

    try:
        content = raw["choices"][0]["message"]["content"]
        usage = raw.get("usage", {})
    except (KeyError, IndexError) as e:
        raise ZaiError(f"Unexpected ZhipuAI response shape: {raw}") from e

    return ChatResponse(
        content=content,
        model=raw.get("model", model),
        prompt_tokens=usage.get("prompt_tokens", 0),
        completion_tokens=usage.get("completion_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
        raw=raw,
    )
