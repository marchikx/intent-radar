"""Parse Ashby-style job JSON from local fixtures (offline only; no network)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a JSON fixture from disk."""
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("fixture root must be a JSON object")
    return data


def parse_ashby_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract one job dict from an Ashby board payload or a single-job object.

    Accepts either ``{"jobs": [...]}`` or a lone job record with ``id`` + ``title``.
    """
    if "jobs" in payload and isinstance(payload["jobs"], list):
        jobs = payload["jobs"]
        if not jobs:
            raise ValueError("jobs array is empty")
        job = jobs[0]
    else:
        job = payload
    if not job.get("id") and not job.get("title"):
        raise ValueError("not a recognizable Ashby job object")
    return dict(job)


def jobs_from_board(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all jobs from a board payload."""
    raw = payload.get("jobs")
    if not isinstance(raw, list):
        return [parse_ashby_job(payload)]
    return [dict(j) for j in raw]
