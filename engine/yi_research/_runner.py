"""Subprocess runner — executes 1 research job + updates job file."""

import asyncio
import sys
import time
import traceback

from .agent import ResearchConfig, research
from .catalog_sync import sync_from_report
from .jobs import load_job, save_job


async def _run(job_id: str) -> int:
    job = load_job(job_id)
    if not job:
        print(f"[runner] Job {job_id} not found", flush=True)
        return 1

    print(f"[runner] START · job={job.job_id} · query='{job.query}'", flush=True)
    job.progress_log.append(f"{time.strftime('%H:%M:%S')} START")
    save_job(job)

    cfg = ResearchConfig(
        llm_provider=job.provider,
        llm_model=job.model,
        retriever=job.retriever,
        save_report=True,
    )

    try:
        report = await research(job.query, config=cfg, verbose=True)
    except Exception as e:
        job.status = "error"
        job.error = f"{type(e).__name__}: {e}"
        job.finished_at = int(time.time())
        job.progress_log.append(f"{time.strftime('%H:%M:%S')} ERROR: {job.error}")
        save_job(job)
        traceback.print_exc()
        return 1

    job.report_path = report.saved_path
    job.sources_count = len(report.sources)
    job.cost_usd = report.cost_usd
    job.progress_log.append(f"{time.strftime('%H:%M:%S')} Research done")
    save_job(job)

    # Catalog sync
    if job.catalog_sync:
        try:
            result = sync_from_report(
                report.markdown,
                apply=job.catalog_apply,
                verbose=True,
            )
            job.new_tools = result.get("new", [])
            job.progress_log.append(
                f"{time.strftime('%H:%M:%S')} Catalog sync: {len(job.new_tools)} new tools"
            )
        except Exception as e:
            job.progress_log.append(
                f"{time.strftime('%H:%M:%S')} Catalog sync failed: {e}"
            )

    job.status = "done"
    job.finished_at = int(time.time())
    save_job(job)
    print(f"[runner] DONE · job={job.job_id} · "
          f"{job.finished_at - job.started_at}s · "
          f"sources={job.sources_count} · new_tools={len(job.new_tools)}",
          flush=True)
    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m engine.yi_research._runner <job_id>")
        sys.exit(1)
    sys.exit(asyncio.run(_run(sys.argv[1])))


if __name__ == "__main__":
    main()
