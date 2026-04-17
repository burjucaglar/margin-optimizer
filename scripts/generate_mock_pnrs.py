"""Produce a jsonl file of mock SQS payloads for local worker runs.

Used by the README quickstart and by Sprint 2's load test. Output shape
matches `margin_optimizer.schemas.SqsPayload` so the worker validates
cleanly without any code path divergence between local and cloud.

Example:
    uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import click

_BAGGAGE_OPTIONS = ["1x20kg", "1x23kg", "2x23kg", "hand_only"]
_CLASSES = ["Economy", "Premium Economy", "Business"]


def _make_row(idx: int, rng: random.Random) -> dict[str, object]:
    return {
        "booking_id": f"MOCK-{idx:05d}",
        "offer_code": f"TRAF-{rng.randint(1000, 9999)}",
        "current_price": round(rng.uniform(150, 1200), 2),
        "baggage": rng.choice(_BAGGAGE_OPTIONS),
        "class": rng.choice(_CLASSES),
    }


@click.command()
@click.option("--count", default=5, show_default=True, type=int)
@click.option(
    "--out",
    "out_path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("/tmp/mock_pnrs.jsonl"),
    show_default=True,
)
@click.option("--seed", type=int, default=42, show_default=True)
def main(count: int, out_path: Path, seed: int) -> None:
    rng = random.Random(seed)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        for idx in range(count):
            fh.write(json.dumps(_make_row(idx, rng)) + "\n")
    click.echo(f"wrote {count} rows → {out_path}")


if __name__ == "__main__":
    main()
