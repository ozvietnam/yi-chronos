#!/usr/bin/env python3
"""
Build reader-friendly research transcript files from extracted TikTok text.

This does deterministic cleanup only: it removes repeated technical metadata from
the combined file format, normalizes common TikTok caption casing errors, and
keeps one compact source line per video.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"


COMMON_WORD_FIXES = {
    "AI": "ai",
    "BA": "ba",
    "Cao": "cao",
    "Cho": "cho",
    "Ra": "ra",
    "SAO": "sao",
    "Sai": "sai",
    "Tay": "tay",
    "Theo": "theo",
    "Xu": "xu",
    "Xin": "xin",
}

PHRASE_FIXES = [
    (r"\btử VI\b", "tử vi"),
    (r"\bTử VI\b", "Tử vi"),
    (r"\btừ VI\b", "tử vi"),
    (r"\bTừ VI\b", "Tử vi"),
    (r"\btử bi\b", "tử vi"),
    (r"\bTử bi\b", "Tử vi"),
    (r"\btử vì\b", "tử vi"),
    (r"\bTử vì\b", "Tử vi"),
    (r"\btừ vi\b", "tử vi"),
    (r"\bTừ vi\b", "Tử vi"),
    (r"\bđầu số\b", "đẩu số"),
    (r"\bĐầu số\b", "Đẩu số"),
    (r"\blá số tử VI\b", "lá số tử vi"),
    (r"\blà số tử vi\b", "lá số tử vi"),
    (r"\blà số\b", "lá số"),
    (r"\blá số này\b", "lá số này"),
    (r"\blận giải\b", "luận giải"),
    (r"\blợn giải\b", "luận giải"),
    (r"\blận lá số\b", "luận lá số"),
    (r"\b7 bại\b", "thất bại"),
    (r"\b7 nghiệp\b", "thất nghiệp"),
    (r"\bnội 7\b", "nội thất"),
    (r"\b2 BA\b", "hai ba"),
    (r"\bthứ BA\b", "thứ ba"),
    (r"\bThứ BA\b", "Thứ ba"),
    (r"\bchồng em chào anh nhá\b", "chồng em"),
    (r"\buống rượu thứ\b", "phương diện thứ"),
    (r"\bphương vị thứ\b", "phương diện thứ"),
    (r"\bbệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bmệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bsắp phá tham\b", "Sát Phá Tham"),
    (r"\bphàm quân\b", "Phá Quân"),
    (r"\btham Lam\b", "Tham Lang"),
    (r"\bTham Lam\b", "Tham Lang"),
    (r"\bcựu môn\b", "Cự Môn"),
    (r"\bngười đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ người đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyện đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyệt đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bphá tan\b", "Phá Tham"),
    (r"\bphá tha\b", "Phá Tham"),
    (r"\bthiên hạ\b", "thiên hạ"),
    (r"\bkhông AI\b", "không ai"),
    (r"\bAI cũng\b", "ai cũng"),
    (r"\bAI là\b", "ai là"),
    (r"\bAI nhìn\b", "anh nhìn"),
]


def load_manifest(channel_dir: Path) -> list[dict[str, Any]]:
    manifest = channel_dir / "text_manifest.jsonl"
    return [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]


def format_date(upload_date: str | None) -> str:
    if not upload_date or len(upload_date) != 8:
        return upload_date or ""
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def topic_from_title(title: str, channel_name: str) -> str:
    topic = re.sub(r"\s+", " ", title or "").strip()
    topic = re.sub(r"^\s*Tử\s*Vi\s*Bôn\s*Ba\s*[:,-]?\s*", "", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\s*\.\.\.$", "", topic).strip()
    if len(topic) > 120:
        topic = topic[:117].rstrip(" ,.;:-") + "..."
    return topic or channel_name


def extract_body(text_path: Path) -> str:
    text = text_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("Thời lượng:"):
            start = idx + 1
            break
    body = "\n".join(lines[start:]).strip()
    body = re.sub(r"\n?Nguồn lời thoại: Whisper local.*$", "", body, flags=re.S).strip()
    return body


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    for pattern, replacement in PHRASE_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE if pattern.islower() else 0)
    for wrong, right in COMMON_WORD_FIXES.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text)
    text = re.sub(r"\b(\d)\s+(\d{2})\b", r"\1\2", text)
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    text = re.sub(r"([,.?!:;])([^\s])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def channel_name(rows: list[dict[str, Any]], fallback: str) -> str:
    for row in rows:
        if row.get("channel"):
            return str(row["channel"])
    return fallback


def build_clean_file(channel_slug: str, output_name: str | None = None) -> Path:
    channel_dir = TRANSCRIPT_ROOT / channel_slug
    rows = load_manifest(channel_dir)
    rows.sort(key=lambda row: (row.get("upload_date") or "", row.get("id") or ""))
    display_name = channel_name(rows, channel_slug)
    output_path = channel_dir / (output_name or f"{channel_slug}_research_clean.txt")

    parts = [
        f"# {display_name} - bản lời thoại sạch",
        "",
        f"Cập nhật bản sạch: {datetime.now(timezone.utc).isoformat()}",
        f"Tổng số video: {len(rows)}",
        "",
        "Ghi chú: bản này đã bỏ metadata kỹ thuật lặp, chuẩn hóa các lỗi caption phổ biến và giữ một dòng nguồn cho từng video.",
        "",
        "---",
        "",
    ]

    missing = 0
    for idx, row in enumerate(rows, start=1):
        text_path_value = row.get("text_path")
        text_path = ROOT / text_path_value if text_path_value else channel_dir / "text" / f"{row['id']}.txt"
        title = row.get("title") or row.get("description") or row["id"]
        topic = topic_from_title(title, display_name)
        date = format_date(row.get("upload_date"))
        duration = row.get("duration_string") or row.get("duration") or ""
        url = row.get("webpage_url") or row.get("url") or ""
        source = row.get("transcript_source") or ("subtitle" if row.get("subtitle_path") else "text")

        parts.append(f"## {idx:03d}. {date} - {topic}")
        parts.append("")
        parts.append(f"Nguồn: {url} | Thời lượng: {duration} | Transcript: {source}")
        parts.append("")
        if text_path.exists():
            parts.append(normalize_text(extract_body(text_path)))
        else:
            missing += 1
            parts.append("[Chưa có lời thoại.]")
        parts.append("")
        parts.append("---")
        parts.append("")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output_path} ({len(rows)} videos, missing text files: {missing})")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channels", nargs="+", help="Channel folder slug(s), e.g. huytuantuvi")
    parser.add_argument("--output-name", default=None, help="Use only with one channel")
    args = parser.parse_args()
    if args.output_name and len(args.channels) != 1:
        parser.error("--output-name can only be used with one channel")
    for channel in args.channels:
        build_clean_file(channel, args.output_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
