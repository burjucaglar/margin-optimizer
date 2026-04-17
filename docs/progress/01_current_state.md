# Development State: MarginOptimizer

> **Last updated:** 2026-04-17 · **Branch:** main · **Phase:** Sprint 0 complete, Sprint 1 partial

This doc tracks the repo's concrete state — what actually works today, not what the specs say should exist.

## 1. What's done

### Repo scaffold
- `pyproject.toml` — all deps pinned; `click` + `rich` + `python-dotenv` promoted to main deps for the worker CLI; `strands-traffics` editable path fixed to `./strands-traffics`
- `.gitignore` — Python + uv + CDK standard exclusions
- `.env.example` — all runtime variables documented (unchanged from design phase)

### Source — `src/margin_optimizer/`

| File | Status | Contents |
|---|---|---|
| `__init__.py` | ✅ | Package version (`0.1.0`) |
| `prompts.py` | ✅ v1 | `WORKER_SYSTEM_PROMPT` (persona, hard rules, canonical tool sequence, terminal-string contract, silence default) + `PROMPT_VERSION = "v1"` |
| `schemas.py` | ✅ | `SqsPayload` and `YieldEvent` Pydantic models. Constrained string types (`_OfferCode`, `_BookingId`, `_SafeStr`) reject prompt-injection payloads at the schema boundary. |
| `filters.py` | ✅ | Pure predicates: `is_baggage_equivalent`, `within_schedule_window`, `layover_acceptable`, `same_class_tier`, `passes_all`. Thresholds read from env at call time. |
| `hooks.py` | 🟡 stub | `AuditHooks` registers all three lifecycle callbacks and stamps every log line with `prompt_version`. Full CloudWatch EMF payload (`MoScannedPnrs`, etc.) lands in Sprint 2. |
| `worker.py` | ✅ | `build_worker_agent()` + `handler(event, context)` Lambda entry + `main()` CLI (`click` + `rich`). `--dry-run` short-circuits Bedrock and just prints the rendered prompt. |
| `ingest.py` | 🟡 stub | `handler()` + `main()` resolve the `mo-ingest` console script; real S3 scan is Sprint 2. |

### Scripts — `scripts/`
| File | Status | Contents |
|---|---|---|
| `generate_mock_pnrs.py` | ✅ | `click` CLI — writes `--count N` rows matching `SqsPayload` to `--out`. Uses a seeded RNG so fixtures are reproducible. |

### Not yet created
`tests/`, `infra/`, `evals/`, `src/margin_optimizer/modify.py`, `src/margin_optimizer/slack_ui.py`, `src/margin_optimizer/slack_verify.py`, `src/margin_optimizer/db.py`, `src/margin_optimizer/secrets.py`, `src/margin_optimizer/weekly_report.py`, `src/margin_optimizer/saga/`.

### Dependencies
- `uv` installed
- `uv.lock` generated (checked in)
- `strands-traffics==0.1.0` installed editable from the nested `./strands-traffics` directory
- `strands-agents==1.35.0`, `strands-agents-tools==0.4.1`, `boto3`, `pydantic`, `click`, `rich`, `python-dotenv`, `sqlalchemy`, `slack-sdk`, etc. — `uv sync` runs clean

### Lint & types
- `uv run ruff check src scripts` → **All checks passed**
- `uv run mypy src` → **Success: no issues found in 7 source files**

## 2. What's not done

| Area | Detail | Target sprint |
|---|---|---|
| Tests | `tests/conftest.py`, `tests/test_worker.py`, `tests/test_margin.py`, `tests/test_filters.py`, `tests/fixtures/` | Sprint 0 closeout |
| Ingest | Real S3 scan + `SendMessageBatch` fan-out; `ScannedPnrs` metric | Sprint 2 |
| Slack HITL | `slack_ui.build_approval_card`, `slack_verify.verify_slack_hmac`, `modify.handler` | Sprint 3 |
| Saga | `saga/{reserve,release,confirm,compensate,journal}.py`, ASL JSON in `infra/` | Sprint 4 |
| DB | `db.py` (`get_engine`, `write_yield_event`), Alembic migration | Sprint 4 |
| Analytics | `weekly_report.py` SES PDF; QuickSight dataset | Sprint 5 |
| Golden set | `evals/golden_set_50.jsonl` + `scripts/run_evals.py` | Sprint 1 close |
| Infra | `infra/` CDK TypeScript stack | Sprint 0 closeout + builds through Sprint 5 |
| Docker | `Dockerfile.worker`, `Dockerfile.ingest` | Sprint 2 |
| Runbook | `docs/runbook.md` | Sprint 6 |

## 3. How to install

From a cold developer machine:

```bash
# 1. install uv if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. sync deps (uv also downloads Python 3.12)
cd /path/to/margin-optimizer
uv sync

# 3. create .env
cp .env.example .env
# edit .env — at minimum fill:
#   AWS_PROFILE=mo-dev
#   AWS_REGION=eu-central-1
#   TRAFFICS_API_KEY=...
#   SLACK_BOT_TOKEN=xoxb-...     (only needed once Slack path lands in Sprint 3)
#   DRY_RUN=true                 (keep true in dev)
```

## 4. How to run

### Generate a mock PNR file + dry-run worker
```bash
uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
uv run python -m margin_optimizer.worker --from-file /tmp/mock_pnrs.jsonl --dry-run
```

`--dry-run` (default) prints the rendered prompt without calling Bedrock. Flip to `--no-dry-run` once you have AWS credentials + Bedrock access to exercise the real agent.

### `mo-worker` / `mo-ingest` console scripts
`uv sync` installs both entry points from `[project.scripts]`:
```bash
uv run mo-worker --from-file /tmp/mock_pnrs.jsonl --dry-run
uv run mo-ingest   # currently a no-op stub
```

### Import-only smoke (no Bedrock needed)
```bash
uv run python -c "from margin_optimizer.worker import build_worker_agent; print('OK')"
uv run python -c "from margin_optimizer.prompts import WORKER_SYSTEM_PROMPT, PROMPT_VERSION; print(PROMPT_VERSION, len(WORKER_SYSTEM_PROMPT), 'chars')"
```

### Lint + type-check + (soon) tests
```bash
uv run ruff check src scripts
uv run mypy src
uv run pytest              # once tests exist
```

## 5. Known gaps & caveats

- **No tests.** Sprint 0's formal exit criterion is `uv run pytest` green — not met yet. Even a placeholder test should be added.
- **`hooks.py` only logs.** No CloudWatch EMF payload or margin telemetry metric yet.
- **`ingest.py` is a stub.** Returns `{"enqueued": 0}` unconditionally.
- **Real runs need AWS access.** Without valid Bedrock access in `.env` and Traffics key, `--no-dry-run` will fail at first tool call.
- **Python 3.13 is on the host.** `uv sync` downloads its own 3.12 (pinned in `pyproject.toml`); do not mix with system Python.
- **`infra/` does not exist.** CDK scaffold is Sprint 0's other open task.

## 6. Next steps (recommended order)

1. **`tests/conftest.py` + `tests/test_filters.py`** — pure-function predicates are the cheapest unit tests; land these first to close Sprint 0.
2. **`tests/test_worker.py`** — use `responses` to mock Traffics; assert that the dry-run path builds a valid `SqsPayload` and renders the expected prompt.
3. **`evals/golden_set_50.jsonl` seed** — start with 5–10 scenarios covering the mix in `docs/6_prompt_design.md` §6.1.
4. **`scripts/run_evals.py`** — runner that replays the golden set through `build_worker_agent()`.
5. **CDK scaffold** — `infra/` directory with the three-stack skeleton from `docs/4_repo_structure.md` §`infra/lib/`.

## 7. File map (what actually exists)

```
margin-optimizer/
├── .env.example
├── .gitignore
├── README.md
├── README_en.md
├── pyproject.toml
├── uv.lock
├── presentation_tr.md
├── presentation_en.md
├── docs/
│   ├── 1_product_requirements_document{,_tr}.md
│   ├── 2_technical_architecture{,_tr}.md
│   ├── 3_implementation_plan{,_tr}.md
│   ├── 4_repo_structure{,_tr}.md
│   ├── 5_dev_setup{,_tr}.md
│   ├── 6_prompt_design{,_tr}.md
│   └── progress/
│       ├── 01_current_state.md           # this file
│       └── 01_current_state_tr.md
├── scripts/
│   └── generate_mock_pnrs.py
├── src/margin_optimizer/
│   ├── __init__.py
│   ├── prompts.py
│   ├── hooks.py
│   ├── schemas.py
│   ├── filters.py
│   ├── worker.py
│   └── ingest.py
└── strands-traffics/                      # nested tool package (editable)
    ├── pyproject.toml
    ├── strands_traffics/
    └── tests/
```

Not yet created: `tests/`, `evals/`, `infra/`, `src/margin_optimizer/{modify,slack_ui,slack_verify,db,secrets,weekly_report}.py`, `src/margin_optimizer/saga/`.
