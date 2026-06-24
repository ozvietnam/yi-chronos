#!/usr/bin/env python3
"""Fill TikTok transcript gaps with local Whisper for videos without subtitles."""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"
TRANSCRIBE_SCRIPT = ROOT / "scripts" / "tiktok_transcribe_research.py"
CLEAN_SCRIPT = ROOT / "scripts" / "clean_tiktok_research_outputs.py"


def load_transcribe_module():
    spec = importlib.util.spec_from_file_location("tiktok_transcribe_research", TRANSCRIBE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {TRANSCRIBE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def download_audio(row: dict[str, Any], audio_dir: Path) -> Path | None:
    audio_dir.mkdir(parents=True, exist_ok=True)
    vid = row["id"]
    existing = audio_dir / f"{vid}.mp3"
    if existing.exists():
        return existing
    url = row.get("webpage_url") or row.get("url")
    if not url:
        return None
    try:
        run(
            [
                "yt-dlp",
                "--no-playlist",
                "-f",
                "b[acodec!=none]/best",
                "-S",
                "vcodec:h264,res:540",
                "-x",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "64K",
                "-o",
                str(audio_dir / "%(id)s.%(ext)s"),
                url,
            ]
        )
    except subprocess.CalledProcessError:
        return None
    return existing if existing.exists() else None


def chunk_paths(paths: list[Path], jobs: int) -> list[list[Path]]:
    chunks = [[] for _ in range(jobs)]
    for index, path in enumerate(paths):
        chunks[index % jobs].append(path)
    return [chunk for chunk in chunks if chunk]


def transcribe_batch(audio_paths: list[Path], whisper_dir: Path, model: str, jobs: int = 1) -> None:
    todo = [path for path in audio_paths if not (whisper_dir / f"{path.stem}.txt").exists()]
    if not todo:
        return
    whisper_dir.mkdir(parents=True, exist_ok=True)
    jobs = max(1, min(jobs, len(todo)))
    commands = []
    for chunk in chunk_paths(todo, jobs):
        commands.append(
            [
                "whisper",
                *[str(path) for path in chunk],
                "--model",
                model,
                "--language",
                "vi",
                "--task",
                "transcribe",
                "--output_format",
                "txt",
                "--output_dir",
                str(whisper_dir),
                "--verbose",
                "False",
            ]
        )
    if len(commands) == 1:
        run(commands[0])
        return
    print(f"Transcribing {len(todo)} audio files with {len(commands)} Whisper jobs")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as executor:
        futures = [executor.submit(run, command) for command in commands]
        for future in concurrent.futures.as_completed(futures):
            future.result()


def merge_whisper(channel: str, combined_name: str) -> None:
    transcribe = load_transcribe_module()
    channel_dir = TRANSCRIPT_ROOT / channel
    manifest_path = channel_dir / "text_manifest.jsonl"
    rows = read_manifest(manifest_path)
    text_dir = channel_dir / "text"
    whisper_dir = channel_dir / "whisper_missing"
    updated = []
    for row in rows:
        if row.get("text_status") == "ok":
            updated.append(row)
            continue
        whisper_path = whisper_dir / f"{row['id']}.txt"
        if not whisper_path.exists():
            updated.append(row)
            continue
        transcript = transcribe.normalize_transcript_text(whisper_path.read_text(encoding="utf-8"))
        txt_path = text_dir / f"{row['id']}.txt"
        body = transcribe.text_for_entry(row, transcript)
        body += "Nguồn lời thoại: Whisper local từ audio vì TikTok không có phụ đề.\n"
        txt_path.write_text(body, encoding="utf-8")
        updated.append(
            {
                **row,
                "text_status": "ok",
                "subtitle_path": None,
                "text_path": str(txt_path.relative_to(ROOT)),
                "text_chars": len(transcript),
                "transcript_source": "whisper_local",
            }
        )
    transcribe.write_jsonl(manifest_path, updated)
    transcribe.combine_texts(updated, channel_dir, combined_name, f"https://www.tiktok.com/@{channel}")
    run(["python3", str(CLEAN_SCRIPT), channel])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channel")
    parser.add_argument("--combined-name", required=True)
    parser.add_argument("--model", default="large-v3-turbo")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--jobs", type=int, default=1, help="Parallel Whisper process count.")
    parser.add_argument("--skip-whisper", action="store_true")
    args = parser.parse_args()

    channel_dir = TRANSCRIPT_ROOT / args.channel
    rows = read_manifest(channel_dir / "text_manifest.jsonl")
    missing = [row for row in rows if row.get("text_status") != "ok"]
    if args.limit:
        missing = missing[: args.limit]
    print(f"Missing rows selected: {len(missing)}")

    audio_dir = channel_dir / "audio_missing"
    audio_paths: list[Path] = []
    for index, row in enumerate(missing, start=1):
        print(f"[{index}/{len(missing)}] audio {row['id']}")
        audio_path = download_audio(row, audio_dir)
        if audio_path:
            audio_paths.append(audio_path)

    if not args.skip_whisper:
        transcribe_batch(audio_paths, channel_dir / "whisper_missing", args.model, args.jobs)
    merge_whisper(args.channel, args.combined_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
