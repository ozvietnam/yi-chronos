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


def call_trait_llm(candidates: list[dict]) -> dict:
    """Call LLM for trait derivation.

    Retry once on parse fail (DeepSeek). Fallback to Anthropic on final fail.

    Returns: {chi: {trait: value}, ...}
    Raises: RuntimeError if all retries + fallback fail.
    """
    prompt = build_trait_prompt(candidates)
    expected = [c["chi"] for c in candidates]
    last_error: Exception | None = None

    # Primary: DeepSeek, retry once
    for attempt in range(2):
        try:
            raw = _provider_complete(prompt, provider_name="deepseek")
            return parse_llm_response(raw, expected)
        except ValueError as e:
            logger.warning("LLM deepseek attempt %d parse failed: %s", attempt + 1, e)
            last_error = e
        except RuntimeError as e:
            logger.warning("LLM deepseek attempt %d transport failed: %s", attempt + 1, e)
            last_error = e
            break  # don't retry on provider missing

    # Fallback: Anthropic Claude
    try:
        raw = _provider_complete(prompt, provider_name="anthropic")
        return parse_llm_response(raw, expected)
    except (ValueError, RuntimeError) as e:
        logger.error("LLM fallback also failed: %s", e)
        raise RuntimeError(
            f"LLM all retries failed (last: {last_error or e})"
        ) from (last_error or e)
