from __future__ import annotations

import os
import subprocess
from pathlib import Path


def transcribe_local_whisper(audio_path: Path, work_dir: Path, model: str) -> str:
    work_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "whisper",
            str(audio_path),
            "--model",
            model,
            "--language",
            "Chinese",
            "--task",
            "transcribe",
            "--output_format",
            "txt",
            "--output_dir",
            str(work_dir),
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return ""
    txt = work_dir / f"{audio_path.stem}.txt"
    return txt.read_text(encoding="utf-8").strip() if txt.exists() else ""


def transcribe_openai(audio_path: Path, model: str = "whisper-1") -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY") or os.getenv("LITELLM_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("LITELLM_BASE_URL") or None,
    )
    with audio_path.open("rb") as fh:
        result = client.audio.transcriptions.create(model=model, file=fh)
    return getattr(result, "text", "") or ""
