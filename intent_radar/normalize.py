"""Normalize company, role, and location from a raw ATS job dict."""

from __future__ import annotations

import re
from typing import Any


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def _money_from_compensation(job: dict[str, Any]) -> tuple[float | None, str | None]:
    comp = job.get("compensation") or {}
    components = comp.get("summaryComponents") or []
    if not components:
        return None, None
    c = components[0]
    lo, hi = c.get("minValue"), c.get("maxValue")
    if lo is None and hi is None:
        return None, None
    amount = (lo + hi) / 2 if (lo is not None and hi is not None) else (lo or hi)
    return float(amount), c.get("currencyCode")


def _location(job: dict[str, Any]) -> str:
    if job.get("isRemote"):
        loc = job.get("locationName") or "Remote"
        return f"Remote ({loc})" if loc != "Remote" else "Remote"
    return str(job.get("locationName") or job.get("location") or "unspecified")


def normalize_job(
    job: dict[str, Any],
    *,
    company_name: str | None = None,
    headcount: int | None = None,
) -> dict[str, Any]:
    """Map raw Ashby job JSON to a stable lead shape for gates and scoring."""
    amount, currency = _money_from_compensation(job)
    description_html = job.get("descriptionHtml") or ""
    description_text = _strip_html(description_html)

    org_name = company_name or job.get("teamName") or "unknown_org"

    return {
        "source": "ashby_fixture",
        "source_job_id": str(job.get("id") or ""),
        "company": {
            "name": org_name,
            "headcount": headcount,
        },
        "role": {
            "title": str(job.get("title") or ""),
            "department": job.get("department"),
            "employment_type": job.get("employmentType"),
        },
        "location": _location(job),
        "urls": {
            "apply": job.get("applyUrl") or job.get("jobUrl") or "",
            "public": job.get("jobUrl") or job.get("applyUrl") or "",
        },
        "compensation": {
            "amount": amount,
            "currency": currency or "USD",
            "pay_signal_present": amount is not None,
        },
        "evidence": {
            "title_quote": str(job.get("title") or ""),
            "description_quote": description_text[:2000],
            "description_html": description_html,
            "published_at": job.get("publishedAt"),
        },
    }
