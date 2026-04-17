# Repository Structure: MarginOptimizer

> **Status:** Ready for implementation · **Last updated:** 2026-04-17

## Top-level layout

```
margin-optimizer/
├── README.md                          # quickstart, env table, run commands
├── pyproject.toml                     # uv config, pinned deps
├── uv.lock
├── .env.example
├── .gitignore
├── Dockerfile.worker                  # container for mo-worker Lambda
├── Dockerfile.ingest                  # slim image for mo-ingest
├── docs/
│   ├── 1_product_requirements_document.md
│   ├── 1_product_requirements_document_tr.md
│   ├── 2_technical_architecture.md
│   ├── 2_technical_architecture_tr.md
│   ├── 3_implementation_plan.md
│   ├── 3_implementation_plan_tr.md
│   ├── 4_repo_structure.md            # this file
│   ├── 4_repo_structure_tr.md
│   ├── 5_dev_setup.md
│   ├── 5_dev_setup_tr.md
│   ├── 6_prompt_design.md
│   ├── 6_prompt_design_tr.md
│   └── runbook.md                     # on-call procedures
├── src/margin_optimizer/
│   ├── __init__.py
│   ├── ingest.py                      # nightly cron Lambda
│   ├── worker.py                      # SQS-triggered agent Lambda
│   ├── modify.py                      # non-LLM Slack webhook Lambda
│   ├── weekly_report.py               # Monday 08:00 SES Lambda
│   ├── prompts.py                     # WORKER_SYSTEM_PROMPT
│   ├── hooks.py                       # AuditHooks (per-tool-call JSON)
│   ├── filters.py                     # baggage/timing/layover/class rules
│   ├── schemas.py                     # Pydantic: SqsPayload, YieldEvent
│   ├── slack_ui.py                    # Block Kit builder
│   ├── slack_verify.py                # HMAC verification
│   ├── secrets.py                     # Secrets Manager helper
│   ├── db.py                          # Aurora connection + yield_events insert
│   └── saga/
│       ├── __init__.py
│       ├── reserve.py                 # Step Fn task: POST /offers/{new}/reserve
│       ├── release.py                 # Step Fn task: DELETE /offers/{old}
│       ├── confirm.py                 # Step Fn task: PATCH /bookings/{id}
│       ├── compensate.py              # compensating actions for each step
│       └── journal.py                 # failure journal writer
├── scripts/
│   ├── run_evals.py
│   ├── generate_mock_pnrs.py          # synthesizes test SQS payloads
│   ├── seed_yield_events.py           # fills Aurora with demo rows for QuickSight
│   └── replay_dlq.py                  # drains DLQ back to main queue
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   └── traffics/
│   │       ├── alternative_flights_cheaper.json
│   │       ├── alternative_flights_none.json
│   │       └── alternative_flights_bad_baggage.json
│   ├── test_worker.py                 # prompt → expected tool calls
│   ├── test_margin.py                 # calculator correctness
│   ├── test_filters.py                # baggage, layover, class rules
│   ├── test_slack_verify.py           # HMAC happy + replay + bad sig
│   ├── test_saga.py                   # happy + compensate paths
│   └── test_db.py                     # yield_events insert + query
├── evals/
│   └── golden_set_50.jsonl
└── infra/
    ├── package.json
    ├── cdk.json
    ├── tsconfig.json
    ├── bin/
    │   └── mo.ts
    ├── lib/
    │   ├── mo-stack.ts                # main composition
    │   ├── queue-construct.ts         # SQS + DLQ
    │   ├── worker-construct.ts        # worker Lambda + SQS ESM
    │   ├── modify-construct.ts        # modify Lambda + API GW
    │   ├── saga-construct.ts          # Step Functions state machine
    │   ├── db-construct.ts            # Aurora Serverless v2
    │   ├── analytics-construct.ts     # QuickSight + SES weekly
    │   └── observability-construct.ts
    └── sql/
        └── 001_yield_events.sql       # Aurora migration
```

## Module responsibilities

### `src/margin_optimizer/ingest.py`
EventBridge-triggered. Reads daily S3 dump of agency bookings, filters to confirmed + future, writes 1 SQS message per PNR in batches of 10. Emits `ScannedPnrs` metric. No LLM.

### `src/margin_optimizer/worker.py`
SQS-triggered. Builds one Strands Agent per SQS message (cheap — Haiku). Agent system prompt enforces: call `use_traffics`, call `calculator`, optionally call `slack`, output final message. No DB writes happen here.

### `src/margin_optimizer/modify.py`
Slack webhook entry. Verifies HMAC, parses interactive payload, starts Step Functions execution. Zero LLM. Critical for compliance: never calls Traffics directly from here — only via saga tasks.

### `src/margin_optimizer/saga/*.py`
One Python module per Step Functions task. Each is a standalone Lambda. Idempotent by design — each writes to a dedupe key in DynamoDB before acting.

### `src/margin_optimizer/filters.py`
Pure functions over alternative-flight dicts: `is_baggage_equivalent`, `within_schedule_window`, `layover_acceptable`, `same_class_tier`. Unit-tested heavily; the LLM prompt references their semantics but the worker runs them explicitly after receiving alternatives.

### `src/margin_optimizer/prompts.py`
`WORKER_SYSTEM_PROMPT` only. Length kept ≤ 800 tokens to bound Haiku input cost.

### `src/margin_optimizer/schemas.py`
Pydantic models mirrored to DB DDL. Source of truth for SQS payload shape and `yield_events` row structure.

### `src/margin_optimizer/slack_verify.py`
`verify_slack_hmac(signing_secret, body, signature_header, timestamp_header) -> bool`. 5-minute skew; rejects malformed sig.

### `src/margin_optimizer/db.py`
`get_engine()` returns a SQLAlchemy engine tied to the Aurora URL from Secrets Manager. `write_yield_event(row: YieldEvent)` is the sole write path — used only from saga confirm step.

### `scripts/generate_mock_pnrs.py`
CLI that writes `mock_pnrs.jsonl` for load testing. Uses Faker to produce booking IDs, realistic EUR prices, baggage variations.

### `infra/lib/saga-construct.ts`
Encapsulates the Step Functions state machine. Exposes `.stateMachineArn` to be passed to the modify Lambda.

## File ownership & conventions

| Path | Owner | Change cadence |
|---|---|---|
| `docs/runbook.md` | sre | on-call iterations |
| `src/margin_optimizer/prompts.py` | ai eng | weekly (guarded by evals) |
| `src/margin_optimizer/saga/` | platform + ai | per Traffics schema change |
| `infra/sql/` | platform | append-only; never edit applied migrations |
| `evals/golden_set_50.jsonl` | ai eng + qa | grows with false positives caught in prod |

## Naming conventions

- Lambda logical name: `mo-ingest`, `mo-worker`, `mo-modify`, `mo-saga-reserve`, etc.
- CloudFormation resource IDs: `MoIngestFn`, `MoWorkerFn`, `MoSagaReserveFn`.
- SQS queue: `mo-pnr-queue`, `mo-pnr-dlq`.
- CloudWatch metrics: `Mo<Capitalized>` — `MoScannedPnrs`, `MoMutationFailures`.
- Secrets: `mo/<env>/<service>` — `mo/prod/slack`.
- Aurora schema: one `public` schema in MVP; Phase 2 will use schema-per-tenant.

## What MUST NOT live in this repo

- Real booking PNRs or customer names, even in fixtures. Anonymize via `scripts/generate_mock_pnrs.py`.
- Slack signing secrets, Traffics API keys, DB passwords — Secrets Manager only.
- Node `node_modules/`.
- Raw QuickSight dashboard JSON exports that might embed account IDs — redact before commit.
