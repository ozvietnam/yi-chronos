#!/usr/bin/env python3
"""Fill TikTok photo-mode transcript gaps with OCR from thumbnail images."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import cv2
import requests


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"
CLEAN_SCRIPT = ROOT / "scripts" / "clean_tiktok_research_outputs.py"


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def thumbnail_url(row: dict[str, Any]) -> str | None:
    thumbnails = row.get("thumbnails") or []
    for preferred in ("originCover", "cover", "dynamicCover"):
        for thumb in thumbnails:
            if thumb.get("id") == preferred and thumb.get("url"):
                return thumb["url"]
    for thumb in thumbnails:
        if thumb.get("url"):
            return thumb["url"]
    return row.get("thumbnail")


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

    full = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    full_path = work_dir / f"{image_path.stem}_full.png"
    cv2.imwrite(str(full_path), full)
    variants.append(full_path)

    crop = image[int(height * 0.22) : int(height * 0.88), int(width * 0.03) : int(width * 0.97)]
    crop = cv2.resize(crop, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    crop_path = work_dir / f"{image_path.stem}_crop.png"
    cv2.imwrite(str(crop_path), crop)
    variants.append(crop_path)

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 9)
    threshold_path = work_dir / f"{image_path.stem}_threshold.png"
    cv2.imwrite(str(threshold_path), threshold)
    variants.append(threshold_path)

    # Most photo-mode posters in this channel use large black/red title text on
    # a pale card around the middle-lower part of the image. Isolating those
    # colors avoids Tesseract reading decorative branches and texture as text.
    title_crop = image[int(height * 0.38) : int(height * 0.76), int(width * 0.05) : int(width * 0.95)]
    hsv = cv2.cvtColor(title_crop, cv2.COLOR_BGR2HSV)
    mask_dark = cv2.inRange(hsv, (0, 0, 0), (179, 255, 115))
    mask_red1 = cv2.inRange(hsv, (0, 60, 40), (12, 255, 220))
    mask_red2 = cv2.inRange(hsv, (165, 60, 40), (179, 255, 220))
    title_mask = cv2.bitwise_or(mask_dark, cv2.bitwise_or(mask_red1, mask_red2))
    title_mask = cv2.morphologyEx(title_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    title_mask = 255 - title_mask
    title_mask = cv2.resize(title_mask, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    title_mask_path = work_dir / f"{image_path.stem}_title_mask.png"
    cv2.imwrite(str(title_mask_path), title_mask)
    variants.append(title_mask_path)
    return variants


def run_tesseract(image_path: Path, psm: str) -> str:
    result = subprocess.run(
        ["tesseract", str(image_path), "stdout", "-l", "vie+eng", "--psm", psm],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def clean_ocr_text(text: str) -> str:
    text = re.sub(r"[^\wÀ-ỹ0-9.,:;!?%/\\+()|\- ]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\b(trend|viral|fyp|xuhuong|xuhướng|tracuutuvi)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" .,:;|-")
    return text


def score_text(text: str) -> tuple[int, int, int]:
    vietnamese = sum(1 for char in text if "à" <= char.lower() <= "ỹ")
    letters = sum(1 for char in text if char.isalpha())
    domain_hits = sum(
        term in text.lower()
        for term in [
            "tử vi",
            "số mệnh",
            "cung",
            "sao",
            "mệnh",
            "tuổi",
            "canh",
            "nhâm",
            "quý",
            "giáp",
            "ất",
            "bính",
            "đinh",
            "mậu",
            "kỷ",
            "tân",
            "thìn",
            "tuất",
            "sửu",
            "mùi",
            "dần",
            "mão",
            "tỵ",
            "ngọ",
            "thân",
            "dậu",
            "hợi",
        ]
    )
    return (domain_hits, vietnamese, letters)


def score_candidate(variant_name: str, text: str) -> tuple[int, int, int, int]:
    domain_hits, vietnamese, letters = score_text(text)
    title_mask_bonus = 0
    if "title_mask" in variant_name and 15 <= len(text) <= 260 and vietnamese >= 2:
        title_mask_bonus = 1000
    length_penalty = max(0, len(text) - 350)
    return (title_mask_bonus + domain_hits * 100 - length_penalty, vietnamese, letters, -len(text))


def ocr_image(image_path: Path, work_dir: Path) -> str:
    candidates: list[tuple[str, str]] = []
    for variant in image_variants(image_path, work_dir):
        for psm in ("6", "11"):
            candidates.append((variant.name, clean_ocr_text(run_tesseract(variant, psm))))
    candidates = [(name, candidate) for name, candidate in candidates if len(candidate) >= 12]
    if not candidates:
        return ""
    return max(candidates, key=lambda item: score_candidate(item[0], item[1]))[1]


def text_for_entry(row: dict[str, Any], text: str) -> str:
    lines = [
        f"Tiêu đề: {row.get('title') or row.get('description') or row['id']}",
        f"Ngày đăng: {row.get('upload_date') or ''}",
        f"URL: {row.get('webpage_url') or row.get('url') or ''}",
        f"Thời lượng: {row.get('duration_string') or row.get('duration') or ''}",
        "",
        text.strip(),
        "",
        "Nguồn lời thoại: OCR thumbnail/poster vì TikTok photo-mode không có voice/subtitle rõ.",
        "",
    ]
    return "\n".join(lines)


def existing_body(row: dict[str, Any], channel_dir: Path) -> str:
    text_path_value = row.get("text_path")
    if not text_path_value:
        return ""
    text_path = ROOT / text_path_value
    if not text_path.exists():
        return ""
    lines = text_path.read_text(encoding="utf-8").splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.strip().startswith("Thời lượng:"):
            start = index + 1
            break
    return " ".join(lines[start:]).strip()


def has_domain_content(text: str) -> bool:
    compact = clean_ocr_text(text).lower()
    if len(compact) < 100:
        return False
    return score_text(compact)[0] > 0


def should_ocr(row: dict[str, Any], channel_dir: Path) -> bool:
    if row.get("subtitle_path"):
        return False
    if row.get("transcript_source") == "whisper_local" and has_domain_content(existing_body(row, channel_dir)):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channel")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--min-chars", type=int, default=20)
    args = parser.parse_args()

    channel_dir = TRANSCRIPT_ROOT / args.channel
    manifest_path = channel_dir / "text_manifest.jsonl"
    rows = read_manifest(manifest_path)
    image_dir = channel_dir / "ocr_images"
    work_dir = channel_dir / "ocr_work"
    text_dir = channel_dir / "text"
    selected = [row for row in rows if should_ocr(row, channel_dir)]
    if args.limit:
        selected = selected[: args.limit]
    selected_ids = {row["id"] for row in selected}
    updated: list[dict[str, Any]] = []
    ok = 0
    skipped = 0

    for index, row in enumerate(rows, start=1):
        if row["id"] not in selected_ids:
            updated.append(row)
            continue
        url = thumbnail_url(row)
        if not url:
            updated.append(row)
            skipped += 1
            continue
        image_path = image_dir / f"{row['id']}.jpg"
        if not download_image(url, image_path):
            updated.append(row)
            skipped += 1
            continue
        text = ocr_image(image_path, work_dir)
        if len(text) < args.min_chars:
            updated.append(row)
            skipped += 1
            continue
        txt_path = text_dir / f"{row['id']}.txt"
        txt_path.write_text(text_for_entry(row, text), encoding="utf-8")
        updated.append(
            {
                **row,
                "text_status": "ok",
                "subtitle_path": None,
                "text_path": str(txt_path.relative_to(ROOT)),
                "text_chars": len(text),
                "transcript_source": "ocr_thumbnail",
            }
        )
        ok += 1
        print(f"[{index}/{len(rows)}] OCR {row['id']} {len(text)} chars")

    write_jsonl(manifest_path, updated)
    print(f"OCR ok: {ok}; skipped: {skipped}")
    subprocess.run(["python3", str(CLEAN_SCRIPT), args.channel], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
