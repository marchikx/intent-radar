"""Simple rule-based score 0–100 from gate outcomes and lead signals."""

from __future__ import annotations

from typing import Any

from intent_radar.gates import FAIL, PASS, GateResult


def compute_score(
    lead: dict[str, Any],
    gate_results: dict[str, GateResult],
) -> dict[str, Any]:
    """Return score 0–100 with a transparent breakdown."""
    breakdown: list[dict[str, Any]] = []
    total = 0

    weights = {
        "pay_signal": 35,
        "tool_keywords": 35,
        "headcount_band": 20,
    }

    for name, weight in weights.items():
        gr = gate_results.get(name)
        if gr is None:
            delta = 0
            status = "missing"
        elif gr.result == PASS:
            delta = weight
            status = PASS
        else:
            delta = 0
            status = FAIL
        total += delta
        breakdown.append({"gate": name, "weight": weight, "earned": delta, "status": status})

    title = (lead.get("role") or {}).get("title") or ""
    desc = (lead.get("evidence") or {}).get("description_quote") or ""
    bonus = 0
    if "senior" in title.lower() or "lead" in title.lower():
        bonus = 5
        breakdown.append({"gate": "title_seniority", "weight": 5, "earned": bonus, "status": PASS})
    elif len(desc) > 400:
        bonus = 5
        breakdown.append({"gate": "rich_description", "weight": 5, "earned": bonus, "status": PASS})
    else:
        breakdown.append({"gate": "quality_bonus", "weight": 5, "earned": 0, "status": FAIL})

    total = min(100, total + bonus)

    return {
        "score": total,
        "max": 100,
        "breakdown": breakdown,
        "all_gates_pass": all(
            gate_results[n].result == PASS for n in weights if n in gate_results
        ),
    }
