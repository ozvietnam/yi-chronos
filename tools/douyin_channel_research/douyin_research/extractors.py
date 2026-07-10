from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class CommandError(RuntimeError):
    pass


def run_command(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise CommandError(proc.stderr.strip() or "command failed")
    return proc


def cookie_args(cookies: Path | None) -> list[str]:
    return ["--cookies", str(cookies)] if cookies else []


def list_channel_entries(channel_url: str, root: Path, limit: int | None, cookies: Path | None) -> list[dict[str, Any]]:
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", *cookie_args(cookies)]
    if limit:
        cmd += ["--playlist-end", str(limit)]
    cmd.append(channel_url)
    proc = run_command(cmd, root)
    rows: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def resolve_video_url(entry: dict[str, Any]) -> str:
    url = entry.get("webpage_url") or entry.get("url")
    if url and str(url).startswith("http"):
        return str(url)
    video_id = entry.get("id")
    if video_id:
        return f"https://www.douyin.com/video/{video_id}"
    raise ValueError(f"Cannot resolve video URL from entry: {entry!r}")


def fetch_video_metadata(url: str, root: Path, cookies: Path | None) -> dict[str, Any]:
    cmd = ["yt-dlp", "--dump-single-json", "--skip-download", *cookie_args(cookies), url]
    proc = run_command(cmd, root)
    return json.loads(proc.stdout)


def download_subtitles(
    url: str,
    video_id: str,
    out_dir: Path,
    root: Path,
    languages: tuple[str, ...],
    cookies: Path | None,
) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(out_dir.glob(f"{video_id}*.vtt"))
    if existing:
        return existing[0]
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        ",".join(languages),
        "--sub-format",
        "vtt",
        "-o",
        str(out_dir / "%(id)s.%(ext)s"),
        *cookie_args(cookies),
        url,
    ]
    try:
        run_command(cmd, root)
    except CommandError:
        return None
    candidates = sorted(out_dir.glob(f"{video_id}*.vtt"))
    return candidates[0] if candidates else None


def download_audio(url: str, video_id: str, out_dir: Path, root: Path, cookies: Path | None) -> Path | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(out_dir.glob(f"{video_id}.*"))
    if existing:
        return existing[0]
    cmd = [
        "yt-dlp",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "m4a",
        "-o",
        str(out_dir / "%(id)s.%(ext)s"),
        *cookie_args(cookies),
        url,
    ]
    try:
        run_command(cmd, root)
    except CommandError:
        return None
    candidates = sorted(out_dir.glob(f"{video_id}.*"))
    return candidates[0] if candidates else None
