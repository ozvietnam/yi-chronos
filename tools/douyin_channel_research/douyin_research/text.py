from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify_channel(value: str) -> str:
    value = re.sub(r"^https?://", "", value.strip())
    value = re.sub(r"^(www\.|v\.)?douyin\.com/", "", value)
    value = value.split("?")[0].strip("/")
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return value or "douyin-channel"


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_vtt(vtt_text: str) -> str:
    lines: list[str] = []
    recent: list[str] = []
    for raw_line in vtt_text.splitlines():
        line = raw_line.strip()
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE")):
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
    return normalize_source_text(" ".join(lines))


def normalize_source_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.?!:;，。！？：；、])", r"\1", text)
    text = re.sub(r"([,.?!:;，。！？：；、])([^\s])", r"\1 \2", text)
    text = re.sub(r"\b(douyin|抖音)\s*[:：]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"#\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def deterministic_clean(text: str) -> str:
    text = normalize_source_text(text)
    text = re.sub(r"(关注|点赞|评论|转发|收藏|点个赞|记得关注)[，。!！]?", " ", text)
    text = re.sub(r"\b(follow|like|subscribe|comment|share)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"#", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" \t\r\n-—_.,，。")
    return text


def format_date(upload_date: str | None, timestamp: int | None = None) -> str:
    if upload_date and len(upload_date) == 8:
        return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    if timestamp:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()
    return upload_date or ""


def title_from_entry(entry: dict[str, Any]) -> str:
    title = entry.get("title") or entry.get("description") or entry.get("id") or ""
    title = re.sub(r"\s+", " ", str(title)).strip()
    return title or str(entry.get("id") or "untitled")


def video_url(entry: dict[str, Any]) -> str:
    return str(entry.get("webpage_url") or entry.get("original_url") or entry.get("url") or "")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
