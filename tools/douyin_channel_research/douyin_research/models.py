from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LlmConfig:
    enabled: bool = False
    model: str | None = None
    api_key_env: str = "LITELLM_API_KEY"
    base_url_env: str = "LITELLM_BASE_URL"
    max_output_tokens: int = 800
    target_language: str = "original"


@dataclass(frozen=True)
class PipelineConfig:
    channel_url: str
    out_root: Path
    limit: int | None = None
    jobs: int = 4
    cookies: Path | None = None
    subtitle_langs: tuple[str, ...] = ("zh-Hans", "zh-CN", "zh", "en")
    ocr_langs: str = "chi_sim+eng"
    transcriber: str = "none"
    whisper_model: str = "small"
    llm: LlmConfig = field(default_factory=LlmConfig)
