"""Pure filter predicates over Traffics `alternative_flights` candidates.

The worker runs these AFTER the LLM has received the Traffics response and
BEFORE it asks `calculator` to compute the margin delta. Two layers — prompt
rules + these predicates — is defense in depth: if the prompt forgets a
rule, the filter catches it; if the filter has a bug, the prompt catches
it. Discrepancies are detected in `tests/test_filters.py` against the
golden set.

Each predicate takes the original booking summary and one candidate dict and
returns `True` iff the candidate is acceptable. Thresholds are read from env
at call time so that staging can widen them without redeploying code.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any


def _env_hours(name: str, default: int) -> timedelta:
    raw = os.environ.get(name)
    return timedelta(hours=int(raw)) if raw else timedelta(hours=default)


def is_baggage_equivalent(booking: dict[str, Any], candidate: dict[str, Any]) -> bool:
    """Candidate must match the booked baggage string verbatim.

    We compare strings rather than parsed allowances because the agency's
    fare rules treat "1x20kg" and "20kg" as semantically different — the
    former is a piece concept, the latter a weight concept. Downgrading
    silently is worse than missing a swap.
    """
    return str(booking.get("baggage", "")) == str(candidate.get("baggage", ""))


def within_schedule_window(booking: dict[str, Any], candidate: dict[str, Any]) -> bool:
    """Departure and arrival must both shift by ≤ MAX_DEPARTURE_SHIFT_HOURS."""
    limit = _env_hours("MAX_DEPARTURE_SHIFT_HOURS", 3)
    try:
        dep_old = datetime.fromisoformat(booking["departure_at"])
        dep_new = datetime.fromisoformat(candidate["departure_at"])
        arr_old = datetime.fromisoformat(booking["arrival_at"])
        arr_new = datetime.fromisoformat(candidate["arrival_at"])
    except (KeyError, ValueError):
        return False
    return abs(dep_new - dep_old) <= limit and abs(arr_new - arr_old) <= limit


def layover_acceptable(candidate: dict[str, Any]) -> bool:
    """Total layover duration on the candidate must be ≤ MAX_LAYOVER_HOURS."""
    limit = _env_hours("MAX_LAYOVER_HOURS", 4)
    total = timedelta(minutes=int(candidate.get("layover_minutes", 0)))
    return total <= limit


def same_class_tier(booking: dict[str, Any], candidate: dict[str, Any]) -> bool:
    """Booking class must match exactly (Economy ≠ Premium Economy)."""
    return str(booking.get("class", "")) == str(candidate.get("class", ""))


def passes_all(booking: dict[str, Any], candidate: dict[str, Any]) -> bool:
    """Convenience aggregator. The worker uses this; tests exercise each
    predicate in isolation to localize failure diagnostics.
    """
    return (
        is_baggage_equivalent(booking, candidate)
        and within_schedule_window(booking, candidate)
        and layover_acceptable(candidate)
        and same_class_tier(booking, candidate)
    )
