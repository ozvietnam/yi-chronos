from __future__ import annotations

import os

from .models import LlmConfig
from .text import deterministic_clean


def clean_with_optional_llm(text: str, config: LlmConfig) -> str:
    base = deterministic_clean(text)
    if not config.enabled or not config.model or not base:
        return base

    api_key = os.getenv(config.api_key_env) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return base

    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=os.getenv(config.base_url_env) or os.getenv("OPENAI_BASE_URL") or None)
    target = "giữ nguyên ngôn ngữ gốc" if config.target_language == "original" else f"chuyển sang {config.target_language}"
    prompt = (
        "Bạn là bộ làm sạch transcript nghiên cứu. "
        "Sửa lỗi OCR/ASR, bỏ lời kêu gọi follow/like, giữ đúng ý và thuật ngữ gốc, "
        f"{target}. Không thêm thông tin mới. Trả về duy nhất phần text đã sạch.\n\n"
        f"TEXT:\n{base}"
    )
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=config.max_output_tokens,
    )
    cleaned = response.choices[0].message.content or ""
    return cleaned.strip() or base
