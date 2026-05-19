"""OpenRouter backend for image redraw — image-to-image via Gemini Flash Image.

Uses OpenAI-compatible SDK pointing to OpenRouter. Bypass Gemini's free-tier
quota=0 for image generation.

Available models (price/token, May 2026):
    google/gemini-2.5-flash-image          $0.0000003  ← cheapest, recommended
    google/gemini-3.1-flash-image-preview  $0.0000005
    google/gemini-3-pro-image-preview      $0.000002   (image)
    openai/gpt-5-image-mini                $0.0000025
    openai/gpt-5-image                     $0.00001
    openai/gpt-5.4-image-2                 $0.000008

Setup:
    pip install openai
    OPENROUTER_KEY in data/ai_keys.json
"""
from __future__ import annotations

import json
import time
import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "google/gemini-2.5-flash-image"
OPENROUTER_URL = "https://openrouter.ai/api/v1"

_CLIENT = None


def _get_api_key() -> str:
    """Load OpenRouter key from ai_keys.json or env."""
    import os
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_KEY")
    if key:
        return key

    keys_path = Path("/Users/ozvietnamdesktop/Desktop/yi/data/ai_keys.json")
    if keys_path.exists():
        keys = json.loads(keys_path.read_text())
        v = keys.get("openrouter")
        if isinstance(v, str):
            return v
        if isinstance(v, dict):
            return v.get("api_key", "")
    raise RuntimeError("OpenRouter API key not found")


def get_client():
    """Lazy-init OpenAI client pointed at OpenRouter."""
    global _CLIENT
    if _CLIENT is None:
        from openai import OpenAI
        _CLIENT = OpenAI(
            base_url=OPENROUTER_URL,
            api_key=_get_api_key(),
            default_headers={
                "HTTP-Referer": "https://yi-chronos.local",
                "X-Title": "YI-CHRONOS Publishing",
            },
        )
    return _CLIENT


def _encode_image_to_data_url(image_path: str | Path) -> str:
    """Convert image file → base64 data URL."""
    image_path = Path(image_path)
    suffix = image_path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/jpeg")
    b64 = base64.b64encode(image_path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def generate_redraw_openrouter(
    prompt: str,
    input_image_path: str | Path,
    *,
    output_path: Path,
    model: str = DEFAULT_MODEL,
    timeout: int = 120,
) -> dict:
    """Image-to-image redraw via OpenRouter.

    Args:
        prompt: editing instruction text
        input_image_path: source image file
        output_path: where to save edited PNG
        model: OpenRouter model ID (default: cheapest Gemini)

    Returns: dict with elapsed_seconds, output_path, prompt, model
    """
    client = get_client()
    data_url = _encode_image_to_data_url(input_image_path)

    t0 = time.time()
    logger.info(f"Calling OpenRouter model={model}...")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        modalities=["image", "text"],  # request image output
        timeout=timeout,
    )
    elapsed = time.time() - t0

    # Extract image from response
    output_path.parent.mkdir(parents=True, exist_ok=True)
    saved = False
    text_response = ""

    choice = response.choices[0]
    msg = choice.message

    # Try multiple response shapes (OpenRouter varies by upstream)
    # Shape A: msg.images = [{"image_url": {"url": "data:image/png;base64,..."}}]
    images_attr = getattr(msg, "images", None)
    if images_attr:
        for img_item in images_attr:
            url = None
            if isinstance(img_item, dict):
                url = img_item.get("image_url", {}).get("url") if isinstance(img_item.get("image_url"), dict) else img_item.get("image_url")
            else:
                url_obj = getattr(img_item, "image_url", None)
                if url_obj:
                    url = getattr(url_obj, "url", None) or (url_obj.get("url") if isinstance(url_obj, dict) else None)
            if url and url.startswith("data:"):
                header, b64data = url.split(",", 1)
                img_bytes = base64.b64decode(b64data)
                output_path.write_bytes(img_bytes)
                saved = True
                logger.info(f"Saved {len(img_bytes)} bytes → {output_path}")
                break

    # Shape B: content has image parts
    if not saved and hasattr(msg, "content") and isinstance(msg.content, list):
        for part in msg.content:
            if isinstance(part, dict) and part.get("type") == "image_url":
                url = part.get("image_url", {}).get("url")
                if url and url.startswith("data:"):
                    header, b64data = url.split(",", 1)
                    img_bytes = base64.b64decode(b64data)
                    output_path.write_bytes(img_bytes)
                    saved = True
                    break

    # Collect text
    if hasattr(msg, "content"):
        if isinstance(msg.content, str):
            text_response = msg.content
        elif isinstance(msg.content, list):
            text_response = " ".join(
                p.get("text", "") if isinstance(p, dict) else getattr(p, "text", "")
                for p in msg.content
            )

    if not saved:
        raise RuntimeError(
            f"OpenRouter returned no image. Model={model}. "
            f"Response: {text_response[:300] if text_response else 'empty'}. "
            f"Full msg: {msg}"
        )

    return {
        "output_path": str(output_path),
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "input_image": str(input_image_path),
        "model": model,
        "mode": "openrouter-img2img",
        "text_response": text_response,
        "usage": getattr(response, "usage", None) and response.usage.model_dump() if hasattr(response, "usage") else None,
    }


def build_openrouter_prompt(
    context_text: str = "",
    style: str = "",
    instruction: str = "",
    caption: str = "",
) -> str:
    """Build natural-language imperative prompt."""
    parts = []
    if instruction:
        parts.append(instruction)
    else:
        parts.append(
            "Repaint this image with more vibrant colors and richer detail. "
            "Preserve the original composition, subjects, poses, and arrangement exactly."
        )
    if style:
        parts.append(f"Visual style: {style}")
    if caption:
        parts.append(f"This depicts: {caption}")
    if context_text:
        ctx = context_text.strip()[:400]
        parts.append(f"Context from the book: {ctx}")
    parts.append(
        "Important: keep layout and composition unchanged. Only enhance colors, details, and artistic quality."
    )
    return " ".join(parts)
