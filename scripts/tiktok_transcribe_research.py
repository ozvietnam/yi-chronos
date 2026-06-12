#!/usr/bin/env python3
"""
Collect TikTok channel video metadata and optional Vietnamese transcripts for research.

Requirements:
  - yt-dlp and ffmpeg available on PATH
  - OPENAI_API_KEY in .env.local or environment when transcribing

Example:
  python3 scripts/tiktok_transcribe_research.py \
    'https://www.tiktok.com/@tuvibonba?lang=vi-VN' \
    --limit 20 \
    --transcribe
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"


def run(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def slugify(value: str) -> str:
    value = re.sub(r"^https?://(www\.)?tiktok\.com/@", "", value)
    value = value.split("?")[0].strip("/").replace("/", "-")
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return value or "tiktok-channel"


def get_channel_entries(channel_url: str, limit: int | None) -> list[dict[str, Any]]:
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json"]
    if limit:
        cmd += ["--playlist-end", str(limit)]
    cmd.append(channel_url)
    proc = run(cmd)
    entries = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def download_audio(url: str, video_id: str, audio_dir: Path, archive_path: Path) -> Path:
    audio_dir.mkdir(parents=True, exist_ok=True)
    before = set(audio_dir.glob(f"{video_id}.*"))
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "-f",
        "b[acodec!=none]/best",
        "-S",
        "vcodec:h264,res:540",
        "--download-archive",
        str(archive_path),
        "--write-info-json",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "64K",
        "-o",
        str(audio_dir / "%(id)s.%(ext)s"),
        url,
    ]
    run(cmd)
    candidates = sorted(audio_dir.glob(f"{video_id}.mp3"))
    if candidates:
        return candidates[0]
    after = set(audio_dir.glob(f"{video_id}.*"))
    new_files = sorted(after - before)
    audio_files = [p for p in new_files if p.suffix.lower() in {".mp3", ".m4a", ".webm", ".opus"}]
    if audio_files:
        return audio_files[0]
    existing = sorted(p for p in after if p.suffix.lower() in {".mp3", ".m4a", ".webm", ".opus"})
    if existing:
        return existing[0]
    raise RuntimeError(f"Audio download did not produce an audio file for {video_id}")


def transcribe_audio(audio_path: Path, model: str, language: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    with audio_path.open("rb") as audio_file:
        result = client.audio.transcriptions.create(
            file=audio_file,
            model=model,
            language=language,
            response_format="text",
        )
    return result if isinstance(result, str) else str(result)


def video_markdown(entry: dict[str, Any], transcript: str) -> str:
    title = entry.get("title") or entry.get("description") or entry["id"]
    url = entry.get("webpage_url") or entry.get("url")
    upload_date = entry.get("upload_date") or ""
    duration = entry.get("duration_string") or entry.get("duration") or ""
    stats = {
        "views": entry.get("view_count"),
        "likes": entry.get("like_count"),
        "comments": entry.get("comment_count"),
        "saves": entry.get("save_count"),
    }
    lines = [
        f"# {title}",
        "",
        f"- URL: {url}",
        f"- Video ID: {entry['id']}",
        f"- Upload date: {upload_date}",
        f"- Duration: {duration}",
        f"- Stats: {json.dumps(stats, ensure_ascii=False)}",
        "",
        "## Transcript",
        "",
        transcript.strip(),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("channel_url", help="TikTok channel URL, e.g. https://www.tiktok.com/@tuvibonba")
    parser.add_argument("--limit", type=int, default=10, help="Max videos to inspect/download")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory")
    parser.add_argument("--transcribe", action="store_true", help="Download audio and create transcripts")
    parser.add_argument("--model", default=os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1"))
    parser.add_argument("--language", default="vi")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env.local")

    channel_slug = slugify(args.channel_url)
    out_dir = args.out_dir or DEFAULT_OUT_ROOT / channel_slug
    audio_dir = out_dir / "audio"
    transcript_dir = out_dir / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Channel: {args.channel_url}")
    print(f"Output: {out_dir}")
    entries = get_channel_entries(args.channel_url, args.limit)
    print(f"Found entries: {len(entries)}")

    collected_at = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        entry["collected_at"] = collected_at
    write_jsonl(out_dir / "metadata.jsonl", entries)

    if not args.transcribe:
        print("Metadata saved. Re-run with --transcribe to download audio and call transcription API.")
        return 0

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is missing. Add it to .env.local before using --transcribe.", file=sys.stderr)
        return 2

    transcript_dir.mkdir(parents=True, exist_ok=True)
    transcript_rows: list[dict[str, Any]] = []
    archive_path = out_dir / "downloaded.txt"

    for index, entry in enumerate(entries, start=1):
        video_id = entry["id"]
        md_path = transcript_dir / f"{video_id}.md"
        if md_path.exists():
            print(f"[{index}/{len(entries)}] skip existing transcript {video_id}")
            continue

        url = entry.get("webpage_url") or entry.get("url")
        print(f"[{index}/{len(entries)}] download audio {video_id}")
        audio_path = download_audio(url, video_id, audio_dir, archive_path)

        print(f"[{index}/{len(entries)}] transcribe {audio_path.name}")
        transcript = transcribe_audio(audio_path, args.model, args.language)
        md_path.write_text(video_markdown(entry, transcript), encoding="utf-8")
        transcript_rows.append(
            {
                "id": video_id,
                "url": url,
                "title": entry.get("title"),
                "upload_date": entry.get("upload_date"),
                "duration": entry.get("duration"),
                "transcript_path": str(md_path.relative_to(ROOT)),
                "transcript": transcript.strip(),
            }
        )

    if transcript_rows:
        existing_rows: list[dict[str, Any]] = []
        transcript_jsonl = out_dir / "transcripts.jsonl"
        if transcript_jsonl.exists():
            existing_rows = [json.loads(line) for line in transcript_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        by_id = {row["id"]: row for row in existing_rows}
        by_id.update({row["id"]: row for row in transcript_rows})
        write_jsonl(transcript_jsonl, list(by_id.values()))

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
