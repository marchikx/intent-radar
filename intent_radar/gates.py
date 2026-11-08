"""Rule gates: headcount band, tool keywords, pay signal."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


PASS = "PASS"
FAIL = "FAIL"


@dataclass
class GateResult:
    name: str
    result: str
    value: Any
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


DEFAULT_TOOL_KEYWORDS = (
    "n8n",
    "python",
    "automation",
    "workflow",
    "api",
    "integrate",
    "zapier",
)


def gate_headcount_band(
    lead: dict[str, Any],
    *,
    min_headcount: int = 11,
    max_headcount: int = 200,
) -> GateResult:
    hc = lead.get("company", {}).get("headcount")
    if hc is None:
        return GateResult("headcount_band", FAIL, {"headcount": None, "reason": "unknown"})
    ok = min_headcount <= int(hc) <= max_headcount
    return GateResult(
        "headcount_band",
        PASS if ok else FAIL,
        {"headcount": hc, "min": min_headcount, "max": max_headcount},
    )


def gate_tool_keywords(
    lead: dict[str, Any],
    keywords: tuple[str, ...] | None = None,
) -> GateResult:
    keywords = keywords or DEFAULT_TOOL_KEYWORDS
    text = " ".join(
        [
            lead.get("role", {}).get("title") or "",
            lead.get("evidence", {}).get("description_quote") or "",
        ]
    ).lower()
    hits = [kw for kw in keywords if kw.lower() in text]
    return GateResult(
        "tool_keywords",
        PASS if hits else FAIL,
        {"matched": hits, "checked": list(keywords)},
    )


def gate_pay_signal(lead: dict[str, Any]) -> GateResult:
    comp = lead.get("compensation") or {}
    present = bool(comp.get("pay_signal_present")) and comp.get("amount") is not None
    return GateResult(
        "pay_signal",
        PASS if present else FAIL,
        {
            "amount": comp.get("amount"),
            "currency": comp.get("currency"),
        },
    )


def evaluate_gates(
    lead: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, GateResult]:
    cfg = config or {}
    gates_cfg = cfg.get("gates", {})
    hc = gates_cfg.get("headcount", {})
    tools = tuple(gates_cfg.get("tool_keywords", DEFAULT_TOOL_KEYWORDS))

    return {
        "headcount_band": gate_headcount_band(
            lead,
            min_headcount=int(hc.get("min", 11)),
            max_headcount=int(hc.get("max", 200)),
        ),
        "tool_keywords": gate_tool_keywords(lead, keywords=tools),
        "pay_signal": gate_pay_signal(lead),
    }


def all_pass(results: dict[str, GateResult]) -> bool:
    return all(r.result == PASS for r in results.values())
