"""Hook providers for audit logging and margin telemetry.

Sprint 1 scaffold: `AuditHooks` registers the three lifecycle callbacks and
emits compact, structured log lines. The full CloudWatch EMF payload
(`MoScannedPnrs`, `MoProfitableAlternativesFound`, etc.) lands in Sprint 2
once the worker Lambda is wired to real SQS input — see
`docs/3_implementation_plan.md` §2.
"""

from __future__ import annotations

import logging
from typing import Any

from strands.hooks import HookProvider, HookRegistry
from strands.hooks.events import (
    AfterInvocationEvent,
    AfterToolCallEvent,
    BeforeToolCallEvent,
)

from .prompts import PROMPT_VERSION

log = logging.getLogger(__name__)


class AuditHooks(HookProvider):
    """Emits one log line per tool boundary, stamped with `prompt_version`.

    CloudWatch Logs Insights queries group on `prompt_version` so a
    regression can be bisected to the prompt change that caused it.
    """

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeToolCallEvent, self._before)
        registry.add_callback(AfterToolCallEvent, self._after)
        registry.add_callback(AfterInvocationEvent, self._after_invocation)

    def _before(self, event: BeforeToolCallEvent) -> None:
        log.info(
            "tool_call_start",
            extra={"tool": event.tool_use["name"], "prompt_version": PROMPT_VERSION},
        )

    def _after(self, event: AfterToolCallEvent) -> None:
        log.info(
            "tool_call_end",
            extra={"tool": event.tool_use["name"], "prompt_version": PROMPT_VERSION},
        )

    def _after_invocation(self, event: AfterInvocationEvent) -> None:
        log.info("invocation_complete", extra={"prompt_version": PROMPT_VERSION})
