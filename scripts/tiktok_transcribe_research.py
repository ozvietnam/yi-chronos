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
from urllib.parse import urlparse

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"
DEFAULT_CHANNEL_URL = "https://www.tiktok.com/@tuvibonba?lang=vi-VN"


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


def video_url(entry: dict[str, Any]) -> str:
    return entry.get("webpage_url") or entry.get("url") or f"https://www.tiktok.com/@tuvibonba/video/{entry['id']}"


def download_subtitle(url: str, video_id: str, subtitles_dir: Path, language: str) -> Path | None:
    subtitles_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(subtitles_dir.glob(f"{video_id}.{language}.vtt"))
    if existing:
        return existing[0]
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--sub-langs",
        language,
        "--sub-format",
        "vtt",
        "-o",
        str(subtitles_dir / "%(id)s.%(ext)s"),
        url,
    ]
    try:
        run(cmd)
    except subprocess.CalledProcessError as exc:
        print(f"Subtitle download failed for {video_id}: {exc.stderr.strip()}", file=sys.stderr)
        return None
    candidates = sorted(subtitles_dir.glob(f"{video_id}.{language}.vtt"))
    return candidates[0] if candidates else None


def clean_vtt(path: Path) -> str:
    lines: list[str] = []
    recent: list[str] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line or re.fullmatch(r"\d+", line):
            continue
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line or line in recent:
            continue
        lines.append(line)
        recent.append(line)
        recent = recent[-8:]
    return normalize_transcript_text(" ".join(lines))


def normalize_transcript_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    text = re.sub(r"([,.?!:;])([^\s])", r"\1 \2", text)
    text = re.sub(r"\b([A-Za-zÀ-ỹ])\s+([,.?!:;])", r"\1\2", text)
    # TikTok captions often omit sentence spacing. Keep the source wording, but make it readable.
    text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_date(upload_date: str | None) -> str:
    if not upload_date or len(upload_date) != 8:
        return upload_date or ""
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def title_to_topic(title: str) -> str:
    title = re.sub(r"^\s*Tử\s*Vi\s*Bôn\s*Ba\s*[:,-]?\s*", "", title, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", title).strip(" .")


def text_for_entry(entry: dict[str, Any], transcript: str) -> str:
    title = entry.get("title") or entry.get("description") or entry["id"]
    topic = title_to_topic(title)
    upload_date = format_date(entry.get("upload_date"))
    duration = entry.get("duration_string") or entry.get("duration") or ""
    return "\n".join(
        [
            f"Ngày đăng: {upload_date}",
            f"Chủ đề: {topic}",
            f"Tiêu đề gốc: {title}",
            f"Video ID: {entry['id']}",
            f"URL: {video_url(entry)}",
            f"Thời lượng: {duration}",
            "",
            transcript.strip(),
            "",
        ]
    )


def write_subtitle_texts(entries: list[dict[str, Any]], out_dir: Path, language: str) -> list[dict[str, Any]]:
    subtitles_dir = out_dir / "subtitles_raw"
    text_dir = out_dir / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        vid = entry["id"]
        print(f"[{index}/{len(entries)}] subtitle {vid}")
        subtitle_path = download_subtitle(video_url(entry), vid, subtitles_dir, language)
        if not subtitle_path:
            rows.append({**entry, "text_status": "missing_subtitle"})
            continue
        transcript = clean_vtt(subtitle_path)
        txt_path = text_dir / f"{vid}.txt"
        txt_path.write_text(text_for_entry(entry, transcript), encoding="utf-8")
        rows.append(
            {
                **entry,
                "text_status": "ok",
                "subtitle_path": str(subtitle_path.relative_to(ROOT)),
                "text_path": str(txt_path.relative_to(ROOT)),
                "text_chars": len(transcript),
            }
        )
    return rows


def combine_texts(entries: list[dict[str, Any]], out_dir: Path, filename: str) -> Path:
    text_dir = out_dir / "text"
    rows = sorted(entries, key=lambda row: (row.get("upload_date") or "", row.get("id") or ""))
    parts = [
        "# Tử Vi Bôn Ba - lời thoại nghiên cứu",
        "",
        f"Nguồn: {DEFAULT_CHANNEL_URL}",
        f"Cập nhật: {datetime.now(timezone.utc).isoformat()}",
        f"Số video trong metadata: {len(entries)}",
        "",
        "Ghi chú: nội dung được lấy từ phụ đề vie-VN của TikTok, đã tự động bỏ dòng lặp và chuẩn hóa dấu câu/khoảng trắng. Cần rà soát thủ công hoặc dùng LLM nếu cần biên tập học thuật tuyệt đối.",
        "",
        "---",
        "",
    ]
    for idx, entry in enumerate(rows, start=1):
        path = text_dir / f"{entry['id']}.txt"
        if not path.exists():
            continue
        parts.append(f"## {idx:03d}. {format_date(entry.get('upload_date'))} - {title_to_topic(entry.get('title') or entry['id'])}")
        parts.append("")
        parts.append(path.read_text(encoding="utf-8").strip())
        parts.append("")
        parts.append("---")
        parts.append("")
    combined_path = out_dir / filename
    combined_path.write_text("\n".join(parts), encoding="utf-8")
    return combined_path


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
    parser.add_argument("channel_url", nargs="?", default=DEFAULT_CHANNEL_URL, help="TikTok channel URL")
    parser.add_argument("--limit", type=int, default=10, help="Max videos to inspect/download; use --all for full channel")
    parser.add_argument("--all", action="store_true", help="Process all videos returned by the channel")
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory")
    parser.add_argument("--subs", action="store_true", help="Download TikTok subtitles and write cleaned text files")
    parser.add_argument("--combine", action="store_true", help="Combine per-video text files into one research text file")
    parser.add_argument("--combined-name", default="tuvi_bonba_all_cleaned.txt")
    parser.add_argument("--transcribe", action="store_true", help="Download audio and create transcripts")
    parser.add_argument("--model", default=os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1"))
    parser.add_argument("--language", default="vie-VN", help="TikTok subtitle language, or vi for OpenAI transcription")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env.local")

    channel_slug = slugify(args.channel_url)
    out_dir = args.out_dir or DEFAULT_OUT_ROOT / channel_slug
    audio_dir = out_dir / "audio"
    transcript_dir = out_dir / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Channel: {args.channel_url}")
    print(f"Output: {out_dir}")
    entries = get_channel_entries(args.channel_url, None if args.all else args.limit)
    print(f"Found entries: {len(entries)}")

    collected_at = datetime.now(timezone.utc).isoformat()
    for entry in entries:
        entry["collected_at"] = collected_at
    write_jsonl(out_dir / "metadata.jsonl", entries)

    subtitle_rows: list[dict[str, Any]] = []
    if args.subs:
        subtitle_rows = write_subtitle_texts(entries, out_dir, args.language)
        write_jsonl(out_dir / "text_manifest.jsonl", subtitle_rows)

    if args.combine:
        combined_path = combine_texts(subtitle_rows or entries, out_dir, args.combined_name)
        print(f"Combined text saved: {combined_path}")

    if not args.transcribe:
        if not args.subs and not args.combine:
            print("Metadata saved. Re-run with --subs --combine to create text from TikTok subtitles.")
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
