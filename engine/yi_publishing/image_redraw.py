"""Image redraw via ComfyUI (FLUX.1 schnell).

Workflow: prompt → FLUX.1 schnell (4 steps, fast) → PNG output

API: ComfyUI HTTP at http://localhost:8188
  POST /prompt        — submit workflow
  GET  /history/{id}  — check completion
  GET  /view?...      — download generated image

Output saved to data/yi_publishing/redrawn/<book>/<page>-<region>-<seq>.png
"""
from __future__ import annotations

import json
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional

COMFY_URL = "http://localhost:8188"


# FLUX.1 schnell workflow (text-to-image, 4 steps)
def build_flux_workflow(prompt: str, *, width: int = 1024, height: int = 1024,
                        seed: Optional[int] = None) -> dict:
    """Build ComfyUI workflow JSON for FLUX.1 schnell t2i."""
    if seed is None:
        seed = int(time.time() * 1000) % 2**31
    return {
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["11", 0],
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Positive Prompt"}
        },
        "8": {
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 0],
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "9": {
            "inputs": {
                "filename_prefix": "yi_publishing_redraw",
                "images": ["8", 0],
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"}
        },
        "10": {
            "inputs": {"vae_name": "ae.safetensors"},
            "class_type": "VAELoader",
            "_meta": {"title": "Load VAE"}
        },
        "11": {
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux",
                "device": "default",
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "Load Dual CLIP"}
        },
        "12": {
            "inputs": {
                "unet_name": "flux1-schnell-fp8.safetensors",
                "weight_dtype": "default",
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load Diffusion Model"}
        },
        "13": {
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["5", 0],
            },
            "class_type": "SamplerCustomAdvanced",
            "_meta": {"title": "SamplerCustomAdvanced"}
        },
        "5": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Empty Latent"}
        },
        "16": {
            "inputs": {"sampler_name": "euler"},
            "class_type": "KSamplerSelect",
            "_meta": {"title": "KSamplerSelect"}
        },
        "17": {
            "inputs": {
                "scheduler": "simple",
                "steps": 4,
                "denoise": 1.0,
                "model": ["12", 0],
            },
            "class_type": "BasicScheduler",
            "_meta": {"title": "BasicScheduler"}
        },
        "22": {
            "inputs": {
                "model": ["12", 0],
                "conditioning": ["6", 0],
            },
            "class_type": "BasicGuider",
            "_meta": {"title": "BasicGuider"}
        },
        "25": {
            "inputs": {"noise_seed": seed},
            "class_type": "RandomNoise",
            "_meta": {"title": "RandomNoise"}
        },
    }


def queue_prompt(workflow: dict, client_id: str) -> str:
    """Submit workflow to ComfyUI. Returns prompt_id."""
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 180,
                        poll_interval: float = 2.0) -> dict:
    """Poll ComfyUI until prompt completes. Returns history entry."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(
                f"{COMFY_URL}/history/{prompt_id}", timeout=10
            ) as resp:
                history = json.loads(resp.read())
                if prompt_id in history:
                    entry = history[prompt_id]
                    if entry.get("status", {}).get("completed", False):
                        return entry
        except Exception:
            pass
        time.sleep(poll_interval)
    raise TimeoutError(f"ComfyUI prompt {prompt_id} did not complete in {timeout}s")


def download_image(filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
    """Download generated image from ComfyUI."""
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": folder_type,
    })
    with urllib.request.urlopen(f"{COMFY_URL}/view?{params}", timeout=30) as resp:
        return resp.read()


def generate_redraw(
    prompt: str,
    *,
    output_path: Path,
    width: int = 1024,
    height: int = 1024,
    seed: Optional[int] = None,
    timeout: int = 180,
) -> dict:
    """End-to-end redraw: prompt → image saved at output_path.

    Returns: {prompt_id, output_path, comfy_filename, elapsed_seconds}
    """
    client_id = uuid.uuid4().hex
    workflow = build_flux_workflow(prompt, width=width, height=height, seed=seed)

    t0 = time.time()
    prompt_id = queue_prompt(workflow, client_id)
    history = wait_for_completion(prompt_id, timeout=timeout)

    # Extract output images from "9" SaveImage node
    outputs = history.get("outputs", {})
    save_output = outputs.get("9", {})
    images = save_output.get("images", [])
    if not images:
        raise RuntimeError(f"No images in ComfyUI output: {outputs}")

    img_meta = images[0]
    img_bytes = download_image(
        img_meta["filename"],
        subfolder=img_meta.get("subfolder", ""),
        folder_type=img_meta.get("type", "output"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(img_bytes)

    elapsed = time.time() - t0
    return {
        "prompt_id": prompt_id,
        "output_path": str(output_path),
        "comfy_filename": img_meta["filename"],
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "width": width,
        "height": height,
        "seed": seed,
    }


def build_flux_img2img_workflow(
    prompt: str,
    input_image_name: str,
    *,
    denoise: float = 0.6,
    seed: Optional[int] = None,
) -> dict:
    """FLUX img2img workflow — preserves composition của input image.

    Args:
        prompt: text prompt for style/content
        input_image_name: filename of uploaded image in ComfyUI input/
        denoise: 0.0 = identical to input, 1.0 = pure text-to-image
                 Recommended: 0.5-0.7 for style change while keeping composition
        seed: random seed
    """
    if seed is None:
        seed = int(time.time() * 1000) % 2**31
    return {
        "1": {  # LoadImage
            "inputs": {"image": input_image_name, "upload": "image"},
            "class_type": "LoadImage",
            "_meta": {"title": "Load Source Image"}
        },
        "2": {  # VAEEncode — convert image → latent
            "inputs": {"pixels": ["1", 0], "vae": ["10", 0]},
            "class_type": "VAEEncode",
            "_meta": {"title": "VAE Encode (Image)"}
        },
        "6": {  # CLIP encode prompt
            "inputs": {"text": prompt, "clip": ["11", 0]},
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Positive Prompt"}
        },
        "8": {  # VAE Decode
            "inputs": {"samples": ["13", 0], "vae": ["10", 0]},
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "9": {  # Save
            "inputs": {
                "filename_prefix": "yi_publishing_redraw_i2i",
                "images": ["8", 0],
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"}
        },
        "10": {
            "inputs": {"vae_name": "ae.safetensors"},
            "class_type": "VAELoader",
            "_meta": {"title": "Load VAE"}
        },
        "11": {
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux",
                "device": "default",
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "Load Dual CLIP"}
        },
        "12": {
            "inputs": {
                "unet_name": "flux1-schnell-fp8.safetensors",
                "weight_dtype": "default",
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load FLUX"}
        },
        "13": {  # Sampler — input latent from VAE encode (img2img)
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["2", 0],  # ← from VAEEncode, not Empty
            },
            "class_type": "SamplerCustomAdvanced",
            "_meta": {"title": "Sampler"}
        },
        "16": {
            "inputs": {"sampler_name": "euler"},
            "class_type": "KSamplerSelect",
        },
        "17": {  # Scheduler with denoise < 1
            "inputs": {
                "scheduler": "simple",
                "steps": 4,
                "denoise": denoise,
                "model": ["12", 0],
            },
            "class_type": "BasicScheduler",
        },
        "22": {
            "inputs": {"model": ["12", 0], "conditioning": ["6", 0]},
            "class_type": "BasicGuider",
        },
        "25": {
            "inputs": {"noise_seed": seed},
            "class_type": "RandomNoise",
        },
    }


def upload_image_to_comfy(image_path: str | Path) -> str:
    """Upload image to ComfyUI input/ folder. Returns filename in ComfyUI's storage."""
    import urllib.request
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Input image not found: {image_path}")

    # ComfyUI multipart upload
    import mimetypes
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    content_type, _ = mimetypes.guess_type(str(image_path))
    content_type = content_type or "image/png"

    with open(image_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{image_path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_data + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n'
        f"--{boundary}--\r\n"
    ).encode()

    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result.get("name", image_path.name)


def generate_redraw_img2img(
    prompt: str,
    input_image_path: str | Path,
    *,
    output_path: Path,
    denoise: float = 0.6,
    seed: Optional[int] = None,
    timeout: int = 600,
) -> dict:
    """Image-to-image redraw: preserve composition of input, change style.

    Args:
        prompt: style direction
        input_image_path: source image (will be uploaded to ComfyUI)
        output_path: where to save the redrawn PNG
        denoise: 0.5-0.7 for style change keeping composition

    Returns: {prompt_id, output_path, comfy_filename, elapsed_seconds, denoise}
    """
    client_id = uuid.uuid4().hex
    t0 = time.time()

    # Upload input image
    uploaded_name = upload_image_to_comfy(input_image_path)

    # Build workflow
    workflow = build_flux_img2img_workflow(
        prompt, uploaded_name, denoise=denoise, seed=seed,
    )

    prompt_id = queue_prompt(workflow, client_id)
    history = wait_for_completion(prompt_id, timeout=timeout)

    outputs = history.get("outputs", {})
    save_output = outputs.get("9", {})
    images = save_output.get("images", [])
    if not images:
        raise RuntimeError(f"No images in output: {outputs}")

    img_meta = images[0]
    img_bytes = download_image(
        img_meta["filename"],
        subfolder=img_meta.get("subfolder", ""),
        folder_type=img_meta.get("type", "output"),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(img_bytes)

    elapsed = time.time() - t0
    return {
        "prompt_id": prompt_id,
        "output_path": str(output_path),
        "comfy_filename": img_meta["filename"],
        "input_image": str(input_image_path),
        "denoise": denoise,
        "elapsed_seconds": elapsed,
        "prompt": prompt,
        "seed": seed,
        "mode": "img2img",
    }


def build_redraw_prompt(
    source_text_context: str,
    image_caption: str = "",
    style: str = "traditional Chinese ink painting, Mai Hoa Dịch Số illustration style, clean line art, balanced composition",
) -> str:
    """Build FLUX prompt from book context.

    Args:
        source_text_context: nearby paragraphs (Chinese or Vietnamese)
        image_caption: caption near image (if any)
        style: visual style direction
    """
    parts = [style]
    if image_caption:
        parts.append(image_caption.strip())
    if source_text_context:
        # Limit context length (FLUX prompt ~512 tokens optimal)
        ctx = source_text_context.strip()[:300]
        parts.append(f"depicting: {ctx}")
    return ". ".join(parts)
