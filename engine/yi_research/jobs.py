"""File-based job tracker cho async research.

Research mất 2-5 phút → API không thể block. Pattern:
1. POST /api/yi-research/run → create job, return job_id, spawn subprocess
2. Subprocess updates job file with progress
3. Frontend polls GET /api/yi-research/jobs/{job_id}
4. When status=done → fetch report

Job state stored: data/yi_research/jobs/<job_id>.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path


JOBS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_research" / "jobs"
REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "yi_research" / "reports"


@dataclass
class ResearchJob:
    job_id: str
    query: str
    status: str = "pending"   # 'pending' | 'running' | 'done' | 'error'
    provider: str = "ollama"
    model: str = "qwen3:32b"
    retriever: str = "duckduckgo"
    catalog_sync: bool = True
    catalog_apply: bool = False
    started_at: int = 0
    finished_at: int | None = None
    pid: int | None = None
    report_path: str | None = None
    error: str | None = None
    progress_log: list[str] = field(default_factory=list)
    sources_count: int = 0
    cost_usd: float = 0.0
    new_tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _job_path(job_id: str) -> Path:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    return JOBS_DIR / f"{job_id}.json"


def save_job(job: ResearchJob) -> Path:
    """Persist job state. Atomic via temp + rename."""
    path = _job_path(job.job_id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(job.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(tmp, path)
    return path


def load_job(job_id: str) -> ResearchJob | None:
    path = _job_path(job_id)
    if not path.exists():
        return None
    try:
        return ResearchJob(**json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return None


def list_jobs(limit: int = 50, status: str | None = None) -> list[ResearchJob]:
    """List recent jobs. Newest first."""
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(JOBS_DIR.glob("*.json"), key=lambda p: -p.stat().st_mtime)
    out: list[ResearchJob] = []
    for f in files[:limit * 2]:  # over-fetch for status filter
        try:
            j = ResearchJob(**json.loads(f.read_text(encoding="utf-8")))
            if status and j.status != status:
                continue
            out.append(j)
            if len(out) >= limit:
                break
        except Exception:
            continue
    return out


def create_job(
    query: str,
    *,
    provider: str = "ollama",
    model: str = "qwen3:32b",
    retriever: str = "duckduckgo",
    catalog_sync: bool = True,
    catalog_apply: bool = False,
) -> ResearchJob:
    """Create + save new job."""
    job = ResearchJob(
        job_id=str(uuid.uuid4())[:12],
        query=query,
        provider=provider,
        model=model,
        retriever=retriever,
        catalog_sync=catalog_sync,
        catalog_apply=catalog_apply,
        started_at=int(time.time()),
    )
    save_job(job)
    return job


def spawn_research_subprocess(job: ResearchJob) -> int:
    """Spawn `python3 -m engine.yi_research <query>` as subprocess.

    Subprocess runs independently — API returns immediately.
    Output goes to job file via separate runner script.
    """
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    runner = Path(__file__).parent / "_runner.py"
    log_path = JOBS_DIR / f"{job.job_id}.log"

    venv_python = "/Users/ozvietnamdesktop/Desktop/yi/.venv/bin/python3"
    cmd = [venv_python, str(runner), job.job_id]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env.setdefault("OLLAMA_KEEP_ALIVE", "8h")

    log_f = log_path.open("w", encoding="utf-8")
    log_f.write(f"# Job {job.job_id} started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_f.write(f"# Query: {job.query}\n")
    log_f.write(f"# Provider: {job.provider}:{job.model}\n\n")
    log_f.flush()

    proc = subprocess.Popen(
        cmd,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=env,
        cwd="/Users/ozvietnamdesktop/Desktop/yi",
    )
    job.pid = proc.pid
    job.status = "running"
    save_job(job)
    return proc.pid
