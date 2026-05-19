"""LLM provider abstraction.

Each provider implements `LLMProvider.chat()` with a common signature.
The Registry holds instances and routes by name.
"""

from .anthropic import AnthropicProvider
from .base import LLMProvider, LLMResponse, ProviderError
from .deepseek import DeepSeekProvider
from .gemini import GeminiProvider
from .minimax import MiniMaxProvider
from .mock import MockProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider
from .zai import ZaiProvider


__all__ = [
    "AnthropicProvider",
    "DeepSeekProvider",
    "GeminiProvider",
    "LLMProvider",
    "LLMResponse",
    "MiniMaxProvider",
    "MockProvider",
    "OllamaProvider",
    "OpenRouterProvider",
    "ProviderError",
    "ZaiProvider",
]
