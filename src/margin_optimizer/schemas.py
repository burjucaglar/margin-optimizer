"""Pydantic schemas: SQS payload in, `yield_events` row out.

Source of truth for the worker-agent input shape. The ingest Lambda produces
`SqsPayload` instances; the worker validates on ingress so a malformed
payload (or a prompt-injection attempt smuggled into a field) is rejected
before it reaches the LLM. The `YieldEvent` row is written exclusively by
the saga's Confirm step — never by the agent.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# Constrained strings — anything that reaches the LLM prompt goes through
# these so that an attacker who controls the upstream booking store cannot
# inject arbitrary system-prompt text via a field value.
_SafeStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=128),
]
_OfferCode = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Za-z0-9_\-]{1,64}$"),
]
_BookingId = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Za-z0-9_\-]{1,64}$"),
]


class SqsPayload(BaseModel):
    """One scanned PNR, produced by `mo-ingest`, consumed by `mo-worker`.

    Field names mirror `docs/2_technical_architecture.md` §5.1.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    booking_id: _BookingId
    offer_code: _OfferCode
    current_price: Annotated[Decimal, Field(gt=0, lt=100_000)]
    baggage: _SafeStr
    booking_class: _SafeStr = Field(alias="class")


YieldStatus = Literal["confirmed", "compensated", "journaled"]


class YieldEvent(BaseModel):
    """One row in Aurora `yield_events`. Written by the saga Confirm task only."""

    model_config = ConfigDict(extra="forbid")

    booking_id: _BookingId
    old_offer_code: _OfferCode
    new_offer_code: _OfferCode
    delta_eur: Annotated[Decimal, Field(gt=0)]
    approved_by: _SafeStr
    approved_at: datetime
    mutated_at: datetime
    status: YieldStatus
