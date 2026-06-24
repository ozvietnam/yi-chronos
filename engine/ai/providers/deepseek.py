"""DeepSeek provider — OpenAI-compatible API.

Endpoint: https://api.deepseek.com/v1/chat/completions
Auth: Bearer token (plain API key).

Models:
- deepseek-chat — general purpose, NON-reasoning (V3 → maps to v4-flash). DEFAULT.
- deepseek-v4-pro — flagship reasoning model.
- deepseek-reasoner — R1, reasoning-optimized.

⚠️ DEFAULT = deepseek-chat (KHÔNG phải v4-pro). Đo trên prod 2026-06-24: với prompt sage
lớn (persona + chart + RAG), v4-pro nghĩ (reasoning_content) ăn SẠCH max_tokens output →
content RỖNG (len=0, completion_tok=cap) — kể cả max_tokens=4000. reasoning_effort='none'
KHÔNG tắt được (đã thử: vẫn rỗng). v4-pro chỉ ra chữ ở budget rất cao (≥16k) nhưng mất ~240s
+ bất định. → default phải là model non-reasoning TIN CẬY. Ai cần v4-pro thì truyền model
tường minh (vd batch dịch cổ văn). Cùng họ lỗi với MiniMax-M3 (xem council._SAGE_FAST_MODEL).
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
        "deepseek-chat",       # V3 general, NON-reasoning, tin cậy — DEFAULT (maps v4-flash)
        "deepseek-v4-flash",   # V4 Flash — fast cheap
        "deepseek-v4-pro",     # V4 Pro — flagship REASONING (chỉ dùng khi truyền model tường minh)
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
        return "DeepSeek (chat V3 · v4-pro/flash khả dụng)"

    @property
    def default_model(self) -> str:
        # NON-reasoning, tin cậy (xem docstring module). v4-pro reasoning → content rỗng.
        return "deepseek-chat"

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
        # ⚠️ ĐÃ ĐO (prod 2026-06-24): với v4-pro, `reasoning.effort='none'` KHÔNG tắt được
        # chain-of-thought — content vẫn RỖNG trên prompt sage lớn. ĐỪNG dựa vào tham số này
        # để "cứu" v4-pro; chọn model non-reasoning (deepseek-chat) thay vì v4-pro. Giữ lại để
        # tương thích nếu API về sau honor nó.
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
