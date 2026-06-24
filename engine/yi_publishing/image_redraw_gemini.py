"""Gemini Flash Image backend — TWO ROUTES:

ROUTE A: Direct Gemini API (FREE TIER = 0 for image gen, needs paid billing)
ROUTE B: OpenRouter gateway (Anh's preferred — uses existing credits)

Native image-to-image edit: input image + text prompt → edited image.
Supports Chinese text understanding (better than FLUX for Mai Hoa books).

Setup OpenRouter route:
    pip install openai  # OpenAI-compatible SDK
    OPENROUTER_KEY in data/ai_keys.json
"""
from __future__ import annotations

import json
import time
import logging
import base64
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Model name (as of 2026)
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

_CLIENT = None


def _get_api_key() -> str:
    """Load Gemini key from ai_keys.json or env."""
    import os
    # Try env first
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        return key

    # Try ai_keys.json
    keys_path = Path("/Users/ozvietnamdesktop/Desktop/yi/data/ai_keys.json")
    if keys_path.exists():
        keys = json.loads(keys_path.read_text())
        g = keys.get("gemini")
        if isinstance(g, str):
            return g
        if isinstance(g, dict):
            return g.get("api_key", "")

    raise RuntimeError("Gemini API key not found. Set GEMINI_API_KEY or update ai_keys.json")


def get_client():
    """Lazy-init Gemini client."""
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        _CLIENT = genai.Client(api_key=_get_api_key())
    return _CLIENT


def generate_redraw_gemini(
    prompt: str,
    input_image_path: str | Path,
    *,
    output_path: Path,
    model: str = GEMINI_IMAGE_MODEL,
) -> dict:
    """Image-to-image redraw via Gemini 2.5 Flash Image (nano-banana).

    Args:
        prompt: editing instruction (e.g. "Repaint this in vibrant colors...")
        input_image_path: source image file
        output_path: where to save the redrawn PNG

    Returns: dict with elapsed_seconds, output_path, prompt
    """
    from google.genai import types
    from PIL import Image
    import io

    client = get_client()

    # Load image as PIL Image (Gemini SDK accepts PIL)
    img = Image.open(input_image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    logger.info(f"Input image: {img.size}, mode={img.mode}")

    t0 = time.time()
    logger.info(f"Calling Gemini {model}...")

    # Generate
    response = client.models.generate_content(
        model=model,
        contents=[prompt, img],
    )
    elapsed = time.time() - t0

    # Extract image from response
    output_path.parent.mkdir(parents=True, exist_ok=True)
    saved = False
    output_text = ""

    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if part.text:
                output_text += part.text
            elif part.inline_data:
                # Save image data
                img_bytes = part.inline_data.data
                output_path.write_bytes(img_bytes)
                saved = True
                logger.info(f"Saved {len(img_bytes)} bytes → {output_path}")

    if not saved:
        # Log response for debugging
        logger.error(f"No image in Gemini response. Text: {output_text[:300]}")
        raise RuntimeError(f"Gemini returned no image. Text response: {output_text[:300]}")

    return {
        "output_path": str(output_path),
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "input_image": str(input_image_path),
        "model": model,
        "mode": "gemini-img2img",
        "text_response": output_text,
    }


def generate_image_gemini(
    prompt: str,
    *,
    output_path: Path,
    model: str = GEMINI_IMAGE_MODEL,
) -> dict:
    """Text-to-image generation via Gemini 2.5 Flash Image (no source image).

    Khác generate_redraw_gemini (img2img): KHÔNG cần ảnh gốc — chỉ truyền prompt text.
    Dùng cho phác hoạ chân dung BIỂU TƯỢNG (engine.tinh_duyen.phac_hoa_phoi_ngau).

    Args:
        prompt: mô tả ảnh (text-to-image instruction).
        output_path: nơi lưu PNG.

    Returns: dict {output_path, elapsed_seconds, prompt, model, mode, text_response}.
    Raise RuntimeError nếu Gemini không trả ảnh (vd quota / safety block).
    """
    client = get_client()

    t0 = time.time()
    logger.info(f"Calling Gemini {model} (text2img)...")

    response = client.models.generate_content(
        model=model,
        contents=[prompt],
    )
    elapsed = time.time() - t0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    saved = False
    output_text = ""

    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if part.text:
                output_text += part.text
            elif part.inline_data:
                img_bytes = part.inline_data.data
                output_path.write_bytes(img_bytes)
                saved = True
                logger.info(f"Saved {len(img_bytes)} bytes → {output_path}")

    if not saved:
        logger.error(f"No image in Gemini text2img response. Text: {output_text[:300]}")
        raise RuntimeError(
            f"Gemini returned no image. Text response: {output_text[:300]}")

    return {
        "output_path": str(output_path),
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "model": model,
        "mode": "gemini-text2img",
        "text_response": output_text,
    }


def build_gemini_prompt(
    context_text: str = "",
    style: str = "",
    instruction: str = "",
    caption: str = "",
) -> str:
    """Build instruction-style prompt for Gemini image editing.

    Gemini Flash Image responds best to natural-language imperative prompts.
    """
    parts = []

    # Lead instruction
    if instruction:
        parts.append(instruction)
    else:
        parts.append(
            "Repaint this image in a more vibrant and lively style. "
            "Preserve the original composition, subjects, poses, and arrangement exactly."
        )

    if style:
        parts.append(f"Visual style: {style}")

    if caption:
        parts.append(f"This depicts: {caption}")

    if context_text:
        ctx = context_text.strip()[:400]
        parts.append(f"Context from the book this image is in: {ctx}")

    parts.append(
        "Important: keep the layout and composition unchanged. "
        "Only enhance colors, details, and artistic quality."
    )
    return " ".join(parts)
