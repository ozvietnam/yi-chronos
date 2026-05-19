"""Provider base class — LLM abstraction.

All providers expose the same `.chat()` method so the council can swap them
freely. New providers (e.g. OpenAI, Gemini, Mistral) plug in by inheriting
this class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ProviderError(RuntimeError):
    """Provider-level errors (API down, no balance, bad key, etc.)."""


@dataclass(frozen=True)
class LLMResponse:
    """Unified LLM response shape."""

    content: str
    provider: str         # e.g. "zai" / "deepseek" / "anthropic" / "mock"
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    raw: dict | None = None

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


class LLMProvider(ABC):
    """Abstract LLM provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g. 'zai', 'deepseek')."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g. 'ZhipuAI GLM-4.5')."""

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier for this provider."""

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """List of model IDs supported."""

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """True if API key is set + provider is usable."""

    @abstractmethod
    def chat(
        self,
        *,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.6,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        """Send chat completion request.

        `messages` is list of {role: 'system'|'user'|'assistant', content: str}.
        Returns LLMResponse or raises ProviderError.
        """

    def set_api_key(self, key: str) -> None:
        """Update API key at runtime. Default: no-op for providers without keys."""

    def status(self) -> dict:
        """Return status info for UI (configured? available models? last error?)."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "is_configured": self.is_configured,
            "default_model": self.default_model,
            "available_models": self.available_models,
        }
