"""Qwen-Image-Edit-2511 backend — image-to-image redraw via Diffusers + Lightning LoRA.

Native zh+en support, image-to-image task, ~13-16GB RAM with Lightning 4-step.

Setup (one-time):
    pip install diffusers accelerate sentencepiece
    huggingface-cli download Qwen/Qwen-Image-Edit-2511
    huggingface-cli download lightx2v/Qwen-Image-Edit-2511-Lightning

Usage:
    pipe = get_pipeline()  # caches globally
    out_path = generate_redraw_qwen(
        prompt="...",
        input_image_path="...",
        output_path=Path("..."),
    )
"""
from __future__ import annotations

import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-load pipeline (heavy import)
_PIPE = None


def get_pipeline(
    *,
    base_model: str = "Qwen/Qwen-Image-Edit-2511",
    lora_repo: str = "lightx2v/Qwen-Image-Edit-2511-Lightning",
    device: str = "mps",
    dtype_str: str = "bfloat16",
):
    """Load Qwen-Image-Edit pipeline với Lightning LoRA (cache global)."""
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    import torch
    from diffusers import QwenImageEditPlusPipeline

    dtype = torch.bfloat16 if dtype_str == "bfloat16" else torch.float16

    logger.info(f"Loading Qwen pipeline {base_model} on {device} ({dtype_str})...")
    t0 = time.time()

    pipe = QwenImageEditPlusPipeline.from_pretrained(
        base_model,
        torch_dtype=dtype,
    )

    # Apply Lightning LoRA for 4-step inference
    logger.info(f"Loading Lightning LoRA: {lora_repo}")
    try:
        pipe.load_lora_weights(
            lora_repo,
            weight_name="Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors",
        )
        pipe.fuse_lora()
        logger.info("Lightning LoRA fused")
    except Exception as e:
        logger.warning(f"Lightning LoRA load failed: {e} — falling back to base 40-step")

    pipe = pipe.to(device)
    elapsed = time.time() - t0
    logger.info(f"Pipeline ready in {elapsed:.1f}s")
    _PIPE = pipe
    return pipe


def generate_redraw_qwen(
    prompt: str,
    input_image_path: str | Path,
    *,
    output_path: Path,
    num_inference_steps: int = 4,
    guidance_scale: float = 1.0,
    seed: Optional[int] = None,
    pipeline=None,
) -> dict:
    """Image-to-image edit via Qwen-Image-Edit-2511 + Lightning.

    Args:
        prompt: instruction like "Repaint this in vibrant colors..."
        input_image_path: source image
        output_path: where to save
        num_inference_steps: 4 with Lightning, 40 without
        guidance_scale: 1.0 with Lightning (no CFG)
    """
    from PIL import Image
    import torch

    pipe = pipeline or get_pipeline()

    img = Image.open(input_image_path).convert("RGB")
    logger.info(f"Input image: {img.size}")

    generator = None
    if seed is not None:
        generator = torch.Generator(device=pipe.device).manual_seed(seed)

    t0 = time.time()
    logger.info(f"Generating ({num_inference_steps} steps)...")
    result = pipe(
        image=img,
        prompt=prompt,
        num_inference_steps=num_inference_steps,
        true_cfg_scale=guidance_scale,  # Lightning uses no CFG
        generator=generator,
    )
    elapsed = time.time() - t0

    out_img = result.images[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(output_path, "PNG", optimize=True)

    return {
        "output_path": str(output_path),
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "input_image": str(input_image_path),
        "num_inference_steps": num_inference_steps,
        "seed": seed,
        "mode": "qwen-img2img-lightning",
    }


def build_qwen_prompt(
    context_text: str = "",
    style: str = "",
    instruction: str = "",
) -> str:
    """Build prompt for Qwen-Image-Edit instruction style.

    Qwen-Image-Edit responds best to imperative instructions.
    """
    parts = []
    if instruction:
        parts.append(instruction)
    else:
        parts.append("Repaint this image keeping the original composition and subjects.")

    if style:
        parts.append(f"Style: {style}")

    if context_text:
        ctx = context_text.strip()[:200]
        parts.append(f"Context from book: {ctx}")

    parts.append("Make colors vibrant and lively. Preserve all subjects, poses, and arrangement.")
    return " ".join(parts)
