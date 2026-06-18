"""LLM call wrapper with retry + provider fallback."""
from __future__ import annotations

import logging

from .llm_prompts import build_trait_prompt, parse_llm_response

logger = logging.getLogger(__name__)


def _provider_complete(prompt: str, provider_name: str = "deepseek",
                       model: str | None = None) -> str:
    """Call configured LLM provider. Imported lazily so tests can patch.

    Returns: response content string (LLMResponse.content).
    Raises: RuntimeError if provider not configured.
    """
    from engine.ai.registry import get_registry
    registry = get_registry()
    provider = registry.get(provider_name)
    if provider is None or not provider.is_configured:
        raise RuntimeError(f"Provider {provider_name!r} not configured")
    resp = provider.chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.3,
        max_tokens=2000,
    )
    return resp.content


# Per-provider preferred models. deepseek-chat (V3) returns structured JSON
# cleanly; deepseek-reasoner (R1) interleaves chain-of-thought and is hard to
# parse strictly. Anthropic fallback uses default Sonnet.
_QUIZ_MODELS = {
    "deepseek": "deepseek-chat",
    "lmstudio": "qwen3-coder-30b-a3b-instruct-mlx",  # local instruct → clean JSON
    "anthropic": None,  # provider default
}

# Fallback chain (#33): DeepSeek primary (prod, returns clean JSON), then LM Studio
# (free local — dev + resilience when cloud key is down), then Anthropic (paid, last).
_QUIZ_PROVIDER_CHAIN = ("deepseek", "lmstudio", "anthropic")


def call_trait_llm(candidates: list[dict]) -> dict:
    """Call LLM for trait derivation.

    Retry once on parse fail (DeepSeek). Fallback to Anthropic on final fail.

    Returns: {chi: {trait: value}, ...}
    Raises: RuntimeError if all retries + fallback fail.
    """
    prompt = build_trait_prompt(candidates)
    expected = [c["chi"] for c in candidates]
    last_error: Exception | None = None

    for provider_name in _QUIZ_PROVIDER_CHAIN:
        # 1 retry on parse-fail for the primary; single shot for fallbacks.
        retries = 2 if provider_name == _QUIZ_PROVIDER_CHAIN[0] else 1
        for attempt in range(retries):
            try:
                raw = _provider_complete(
                    prompt, provider_name=provider_name, model=_QUIZ_MODELS.get(provider_name),
                )
                logger.info("LLM %s attempt %d raw len=%d", provider_name, attempt + 1, len(raw or ""))
                return parse_llm_response(raw, expected)
            except ValueError as e:  # parse fail → retry same provider
                logger.warning("LLM %s attempt %d parse failed: %s", provider_name, attempt + 1, e)
                last_error = e
            except RuntimeError as e:  # provider missing/unreachable → next provider
                logger.warning("LLM %s transport failed: %s", provider_name, e)
                last_error = e
                break

    logger.error("LLM all providers failed (last: %s)", last_error)
    raise RuntimeError(f"LLM all retries failed (last: {last_error})") from last_error
