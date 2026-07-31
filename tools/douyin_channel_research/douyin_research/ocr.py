from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import cv2
import requests


def thumbnail_url(metadata: dict[str, Any]) -> str | None:
    thumbnails = metadata.get("thumbnails") or []
    for thumb in reversed(thumbnails):
        if thumb.get("url"):
            return str(thumb["url"])
    return metadata.get("thumbnail")


def download_image(url: str, path: Path) -> bool:
    if path.exists() and path.stat().st_size > 0:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        response.raise_for_status()
    except requests.RequestException:
        return False
    path.write_bytes(response.content)
    return path.stat().st_size > 0


def image_variants(image_path: Path, work_dir: Path) -> list[Path]:
    image = cv2.imread(str(image_path))
    if image is None:
        return []
    height, width = image.shape[:2]
    work_dir.mkdir(parents=True, exist_ok=True)
    variants: list[Path] = []

    crops = {
        "full": image,
        "center": image[int(height * 0.15) : int(height * 0.9), int(width * 0.03) : int(width * 0.97)],
        "lower": image[int(height * 0.35) : int(height * 0.9), int(width * 0.03) : int(width * 0.97)],
    }
    for name, crop in crops.items():
        if crop.size == 0:
            continue
        resized = cv2.resize(crop, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9)
        out = work_dir / f"{image_path.stem}_{name}.png"
        cv2.imwrite(str(out), threshold)
        variants.append(out)
    return variants


def run_tesseract(image_path: Path, langs: str, psm: str) -> str:
    proc = subprocess.run(
        ["tesseract", str(image_path), "stdout", "-l", langs, "--psm", psm],
        capture_output=True,
        text=True,
    )
    return proc.stdout if proc.returncode == 0 else ""


def clean_ocr_text(text: str) -> str:
    text = re.sub(r"[^\w\u3400-\u9fffÀ-ỹ0-9.,:;!?%/\\+()|\-，。！？：；、 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"#\S+", " ", text)
    return re.sub(r"\s+", " ", text).strip(" .,:;，。")


def ocr_image(image_path: Path, work_dir: Path, langs: str) -> str:
    candidates: list[str] = []
    for variant in image_variants(image_path, work_dir):
        for psm in ("6", "11"):
            text = clean_ocr_text(run_tesseract(variant, langs, psm))
            if len(text) >= 8:
                candidates.append(text)
    if not candidates:
        return ""
    return max(candidates, key=lambda value: (sum("\u3400" <= ch <= "\u9fff" for ch in value), len(value)))
