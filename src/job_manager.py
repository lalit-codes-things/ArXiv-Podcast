from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

_jobs: dict[str, dict] = {}
_lock = Lock()


def create_job(arxiv_id: str) -> dict:
    """Create an in-memory job record."""
    job_id = str(uuid4())
    job = {
        "job_id": job_id,
        "arxiv_id": arxiv_id,
        "status": "queued",
        "message": "Job queued",
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _jobs[job_id] = job
    return job.copy()


def update_job(job_id: str, **updates) -> dict:
    """Patch an in-memory job record."""
    with _lock:
        if job_id not in _jobs:
            raise KeyError(job_id)
        _jobs[job_id].update(updates)
        _jobs[job_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        return _jobs[job_id].copy()


def get_job(job_id: str) -> dict | None:
    """Return a copy of a job record if it exists."""
    with _lock:
        job = _jobs.get(job_id)
        return job.copy() if job else None
