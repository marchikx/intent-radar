"""Evidence passport: structured dict; quoted fields come from source text only."""

from __future__ import annotations

import re
from typing import Any

from intent_radar.gates import GateResult


def _extract_money_quote(description: str) -> str | None:
    pattern = re.compile(
        r"(\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?|\d+[\d,]*\s*(?:USD|EUR|€|\$)(?:\s*/\s*(?:yr|year|mo|month))?)",
        re.I,
    )
    m = pattern.search(description)
    return m.group(0).strip() if m else None


def build_passport(
    lead: dict[str, Any],
    gate_results: dict[str, GateResult],
    score_payload: dict[str, Any],
) -> dict[str, Any]:
    """Build an evidence passport suitable for JSON export."""
    ev = lead.get("evidence") or {}
    comp = lead.get("compensation") or {}
    desc = ev.get("description_quote") or ""

    quotes: dict[str, str | None] = {
        "title": ev.get("title_quote") or None,
        "description_excerpt": (desc[:500] + "…") if len(desc) > 500 else desc or None,
    }
    money_quote = _extract_money_quote(desc)
    if money_quote:
        quotes["pay_mentioned_in_text"] = money_quote
    elif comp.get("amount") is not None:
        quotes["pay_structured_field"] = (
            f"{comp['amount']:.0f} {comp.get('currency', '')}".strip()
        )

    gates_summary = {
        name: {"result": gr.result, "value": gr.value}
        for name, gr in gate_results.items()
    }

    return {
        "meta": {
            "source": lead.get("source"),
            "source_job_id": lead.get("source_job_id"),
            "url": (lead.get("urls") or {}).get("public"),
        },
        "company": {
            "name": (lead.get("company") or {}).get("name"),
            "headcount": (lead.get("company") or {}).get("headcount"),
        },
        "role": {
            "title": (lead.get("role") or {}).get("title"),
            "location": lead.get("location"),
        },
        "quotes_from_source_only": quotes,
        "gates": gates_summary,
        "score": {
            "value": score_payload.get("score"),
            "breakdown": score_payload.get("breakdown"),
        },
        "notes": {
            "inference_policy": (
                "Fields under quotes_from_source_only are verbatim or structural "
                "compensation from the fixture; score breakdown is labeled inference."
            ),
        },
    }
