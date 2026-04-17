"""`mo-ingest` — nightly cron Lambda entry point (Sprint 0 stub).

Sprint 2 wires this up to S3 (or an Aurora read replica) and enqueues one
SQS message per active PNR. For now the module exposes a no-op `handler`
and a `main` CLI shim so the `mo-ingest` console script in pyproject.toml
resolves. Full implementation: `docs/3_implementation_plan.md` §2.2.
"""

from __future__ import annotations

import logging
from typing import Any

import click

log = logging.getLogger(__name__)


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """EventBridge entry. Current state: emits a log line and exits.

    Real implementation will read the daily S3 dump, filter to
    `CONFIRMED && departure > now()+24h`, and batch-enqueue.
    """
    log.info("ingest_invoked_stub")
    return {"enqueued": 0, "note": "Sprint-0 stub — see docs/3_implementation_plan.md §2.2"}


@click.command()
def main() -> None:
    """Local smoke test: runs the handler with an empty event."""
    result = handler({}, None)
    click.echo(result)


if __name__ == "__main__":
    main()
