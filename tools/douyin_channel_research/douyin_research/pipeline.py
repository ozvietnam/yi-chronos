from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .extractors import (
    CommandError,
    download_audio,
    download_subtitles,
    fetch_video_metadata,
    list_channel_entries,
    resolve_video_url,
)
from .llm_cleaner import clean_with_optional_llm
from .models import PipelineConfig
from .ocr import download_image, ocr_image, thumbnail_url
from .text import clean_vtt, compact_text, format_date, slugify_channel, title_from_entry, video_url, write_text
from .transcribe import transcribe_local_whisper, transcribe_openai


ROOT = Path(__file__).resolve().parents[3]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def source_from_subtitle(metadata: dict[str, Any], channel_dir: Path, config: PipelineConfig) -> tuple[str, str]:
    url = video_url(metadata) or resolve_video_url(metadata)
    subtitle = download_subtitles(url, metadata["id"], channel_dir / "subtitles", ROOT, config.subtitle_langs, config.cookies)
    if subtitle and subtitle.exists():
        return clean_vtt(subtitle.read_text(encoding="utf-8-sig")), "subtitle"
    return "", ""


def source_from_ocr(metadata: dict[str, Any], channel_dir: Path, config: PipelineConfig) -> tuple[str, str]:
    url = thumbnail_url(metadata)
    if not url:
        return "", ""
    image_path = channel_dir / "images" / f"{metadata['id']}.jpg"
    if not download_image(url, image_path):
        return "", ""
    text = ocr_image(image_path, channel_dir / "ocr_work" / metadata["id"], config.ocr_langs)
    return text, "ocr_thumbnail" if text else ""


def source_from_audio(metadata: dict[str, Any], channel_dir: Path, config: PipelineConfig) -> tuple[str, str]:
    if config.transcriber == "none":
        return "", ""
    url = video_url(metadata) or resolve_video_url(metadata)
    audio = download_audio(url, metadata["id"], channel_dir / "audio", ROOT, config.cookies)
    if not audio:
        return "", ""
    if config.transcriber == "local-whisper":
        return transcribe_local_whisper(audio, channel_dir / "whisper", config.whisper_model), "local_whisper"
    if config.transcriber == "openai":
        return transcribe_openai(audio), "openai_audio"
    return "", ""


def process_video(entry: dict[str, Any], channel_dir: Path, config: PipelineConfig) -> dict[str, Any]:
    url = resolve_video_url(entry)
    metadata = fetch_video_metadata(url, ROOT, config.cookies)
    metadata.setdefault("id", entry.get("id"))

    raw_text = ""
    source = ""
    for extractor in (source_from_subtitle, source_from_ocr, source_from_audio):
        raw_text, source = extractor(metadata, channel_dir, config)
        if compact_text(raw_text):
            break

    cleaned = clean_with_optional_llm(raw_text, config.llm) if raw_text else ""
    video_id = metadata["id"]
    raw_path = channel_dir / "raw" / f"{video_id}.txt"
    clean_path = channel_dir / "clean" / f"{video_id}.txt"
    if raw_text:
        write_text(raw_path, raw_text)
    if cleaned:
        write_text(clean_path, cleaned)

    return {
        "id": video_id,
        "url": video_url(metadata) or url,
        "title": title_from_entry(metadata),
        "upload_date": metadata.get("upload_date"),
        "timestamp": metadata.get("timestamp"),
        "duration": metadata.get("duration_string") or metadata.get("duration"),
        "source": source or "missing",
        "raw_path": str(raw_path.relative_to(ROOT)) if raw_text else None,
        "clean_path": str(clean_path.relative_to(ROOT)) if cleaned else None,
        "raw_chars": len(compact_text(raw_text)),
        "clean_chars": len(compact_text(cleaned)),
        "has_text": bool(compact_text(cleaned)),
    }


def write_final(channel_dir: Path, records: list[dict[str, Any]], channel_url: str) -> None:
    final_dir = channel_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    rows = sorted(records, key=lambda row: (row.get("upload_date") or "", row.get("id") or ""))
    parts = [
        "# Douyin channel - bản text sạch",
        "",
        f"Nguồn: {channel_url}",
        f"Cập nhật: {datetime.now(timezone.utc).isoformat()}",
        f"Tổng số video: {len(rows)}",
        f"Có text: {sum(1 for row in rows if row['has_text'])}",
        "",
        "---",
        "",
    ]
    index_lines = ["# Index", "", f"Tổng số video: {len(rows)}", ""]
    for idx, record in enumerate(rows, start=1):
        date = format_date(record.get("upload_date"), record.get("timestamp"))
        title = record["title"]
        parts += [
            f"## {idx:03d}. {date} - {title}",
            "",
            f"Nguồn: {record['url']} | Thời lượng: {record.get('duration') or ''} | Transcript: {record['source']}",
            "",
        ]
        clean_path = ROOT / record["clean_path"] if record.get("clean_path") else None
        parts.append(clean_path.read_text(encoding="utf-8").strip() if clean_path and clean_path.exists() else "[Chưa nhận diện được text.]")
        parts += ["", "---", ""]
        index_lines.append(f"{idx:03d}. {date} | {record.get('duration') or ''} | {title} | {record['source']} | {record['id']}")
    (final_dir / "transcripts.txt").write_text("\n".join(parts), encoding="utf-8")
    (final_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    (final_dir / "videos.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    missing = [row for row in rows if not row["has_text"]]
    sources: dict[str, int] = {}
    for row in rows:
        sources[row["source"]] = sources.get(row["source"], 0) + 1
    report = [
        "# Quality report",
        "",
        f"- total: {len(rows)}",
        f"- with_text: {len(rows) - len(missing)}",
        f"- missing: {len(missing)}",
        f"- sources: {json.dumps(sources, ensure_ascii=False, sort_keys=True)}",
        "",
    ]
    if missing:
        report.append("## Missing")
        report.extend(f"- {row['id']} | {row['url']} | {row['title']}" for row in missing)
    (final_dir / "quality_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def run_pipeline(config: PipelineConfig) -> Path:
    load_dotenv(ROOT / ".env.local")
    channel_slug = slugify_channel(config.channel_url)
    channel_dir = config.out_root / channel_slug
    channel_dir.mkdir(parents=True, exist_ok=True)

    entries = list_channel_entries(config.channel_url, ROOT, config.limit, config.cookies)
    write_jsonl(channel_dir / "entries.jsonl", entries)
    print(f"Found {len(entries)} entries. Output: {channel_dir}", file=sys.stderr)

    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, config.jobs)) as pool:
        futures = {pool.submit(process_video, entry, channel_dir, config): entry for entry in entries}
        for index, future in enumerate(as_completed(futures), start=1):
            entry = futures[future]
            try:
                record = future.result()
            except (CommandError, Exception) as exc:
                record = {
                    "id": entry.get("id") or f"failed-{index}",
                    "url": entry.get("url") or entry.get("webpage_url") or "",
                    "title": title_from_entry(entry),
                    "upload_date": entry.get("upload_date"),
                    "timestamp": entry.get("timestamp"),
                    "duration": entry.get("duration_string") or entry.get("duration"),
                    "source": "error",
                    "raw_path": None,
                    "clean_path": None,
                    "raw_chars": 0,
                    "clean_chars": 0,
                    "has_text": False,
                    "error": str(exc),
                }
            records.append(record)
            print(f"[{index}/{len(entries)}] {record['id']} {record['source']} chars={record['clean_chars']}", file=sys.stderr)

    write_jsonl(channel_dir / "manifest.jsonl", records)
    write_final(channel_dir, records, config.channel_url)
    return channel_dir / "final" / "transcripts.txt"
