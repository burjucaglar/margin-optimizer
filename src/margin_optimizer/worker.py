"""`mo-worker` — SQS-triggered agent Lambda, and a local CLI twin.

Two entry points live in this module:

- `handler(event, context)` — the AWS Lambda entry. Iterates SQS records,
  validates each via `schemas.SqsPayload`, builds a fresh Strands agent, and
  runs it once per record. No persistence happens here; the saga handles
  writes.
- `main()` — a `click` CLI used during dev to replay a jsonl file of mock
  PNRs through the same code path, optionally in `--dry-run`. The CLI is
  wired to the `mo-worker` console script in `pyproject.toml`.

Import-time side effects are avoided — env reads happen inside
`build_worker_agent` so that unit tests can stub them cheaply.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import click
from dotenv import load_dotenv
from pydantic import ValidationError
from rich.console import Console
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, journal, slack
from strands_traffics import use_traffics

from .hooks import AuditHooks
from .prompts import WORKER_SYSTEM_PROMPT
from .schemas import SqsPayload

log = logging.getLogger(__name__)
console = Console()


def build_worker_agent() -> Agent:
    """Construct the worker Strands agent. One per invocation — cheap on Haiku."""
    region = os.environ.get("AWS_REGION", "eu-central-1")
    model_id = os.environ.get(
        "BEDROCK_MODEL_ID",
        "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    )
    return Agent(
        agent_id="mo-worker",
        model=BedrockModel(
            model_id=model_id,
            region_name=region,
            temperature=0.0,  # deterministic parsing
            streaming=False,
        ),
        system_prompt=WORKER_SYSTEM_PROMPT,
        tools=[use_traffics, calculator, slack, journal],
        hooks=[AuditHooks()],
    )


def _build_prompt(payload: SqsPayload) -> str:
    """Render the per-PNR user prompt. Values are trusted only as strings —
    the schema has already constrained them to safe character classes."""
    min_margin = os.environ.get("MIN_MARGIN_EUR", "30")
    return (
        f"Booking {payload.booking_id}: offerCode={payload.offer_code}, "
        f"current flight cost={payload.current_price} EUR, "
        f"baggage={payload.baggage}, class={payload.booking_class}. "
        f"Find cheaper equivalent alternatives via Traffics. "
        f"Only surface alternatives saving > {min_margin} EUR."
    )


def _run_one(payload: SqsPayload, *, dry_run: bool) -> str:
    """Build an agent, run it once for `payload`, return the terminal string.

    `dry_run=True` short-circuits the LLM call — used by local CLI runs
    that want to verify parsing + prompt rendering without burning Bedrock
    tokens.
    """
    prompt = _build_prompt(payload)
    if dry_run:
        console.print(f"[dim]DRY_RUN prompt →[/dim] {prompt}")
        return "Task Complete. No action needed."
    agent = build_worker_agent()
    result = agent(prompt)
    return str(getattr(result, "output", result))


def handler(event: dict[str, Any], context: object) -> dict[str, Any]:
    """AWS Lambda entry point. SQS batch → per-record invocation.

    Record-level failures are swallowed so one bad PNR does not fail the
    whole batch — the record lands in the DLQ via SQS's own retry budget.
    """
    outcomes: list[dict[str, str]] = []
    for record in event.get("Records", []):
        body = record.get("body", "")
        try:
            payload = SqsPayload.model_validate_json(body)
        except ValidationError as exc:
            log.warning("invalid_sqs_payload", extra={"error": str(exc)})
            outcomes.append({"status": "rejected", "reason": "schema"})
            continue
        try:
            terminal = _run_one(payload, dry_run=False)
            outcomes.append({"booking_id": payload.booking_id, "terminal": terminal})
        except Exception as exc:
            log.exception("worker_failed", extra={"booking_id": payload.booking_id})
            outcomes.append({"booking_id": payload.booking_id, "error": str(exc)})
    return {"processed": len(outcomes), "outcomes": outcomes}


@click.command()
@click.option(
    "--from-file",
    "from_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to jsonl file of mock PNR payloads.",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=True,
    help="Skip Bedrock; print the rendered prompt instead. Default: true.",
)
def main(from_file: Path | None, dry_run: bool) -> None:
    """Local harness: replay a jsonl of PNR payloads through the worker."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    if from_file is None:
        console.print(
            "[yellow]No --from-file supplied.[/yellow] "
            "Generate one with scripts/generate_mock_pnrs.py."
        )
        return

    count = 0
    for line in from_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = SqsPayload.model_validate_json(line)
        except ValidationError as exc:
            console.print(f"[red]schema-reject[/red] {exc.errors()[0]['msg']}")
            continue
        terminal = _run_one(payload, dry_run=dry_run)
        console.print(f"[green]✓[/green] {payload.booking_id} → {terminal}")
        count += 1
    console.print(f"[dim]processed {count} record(s)[/dim]")


if __name__ == "__main__":
    main()
