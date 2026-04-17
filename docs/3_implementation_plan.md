# Implementation Plan: MarginOptimizer

> **Status:** Ready for execution · **Cadence:** 2-week sprints · **Last updated:** 2026-04-17

## Milestones

| Sprint | Weeks | Exit criterion |
|---|---|---|
| 0. Bootstrap | 1 | Repo + CI + CDK scaffold + dev loop green |
| 1. Agent + margin logic | 2–3 | Worker Lambda handles 100 mock PNRs; calculator accuracy verified |
| 2. Queue + ingest | 4 | 10k simulated PNRs flow through SQS in a 3h window, no DLQ overflow |
| 3. Slack HITL | 5 | Approve/Reject click triggers saga state machine end-to-end |
| 4. Saga + Aurora | 6 | `yield_events` row written on 10 real staging approvals |
| 5. QuickSight + SES | 7 | Dashboard live; Monday PDF delivered to ops inbox |
| 6. Hardening + launch | 8 | Chaos test passes; DRY_RUN flipped to `false` in prod |

## Sprint 0 — Bootstrap (Week 1)

### 0.1. Repo + tooling

```bash
uv init --app
uv python pin 3.12
uv add strands-agents strands-agents-tools \
       ./strands-traffics \
       boto3 aws-lambda-powertools structlog pydantic sqlalchemy psycopg2-binary
uv add --dev pytest pytest-asyncio responses ruff mypy moto[all] locust
```

### 0.2. Directory scaffold

```
margin-optimizer/
├── pyproject.toml
├── .env.example
├── README.md
├── src/margin_optimizer/
│   ├── __init__.py
│   ├── ingest.py              # nightly cron Lambda
│   ├── worker.py              # per-PNR agent Lambda
│   ├── modify.py              # non-LLM mutation Lambda
│   ├── saga/                  # step functions task Lambdas
│   │   ├── reserve.py
│   │   ├── release.py
│   │   ├── confirm.py
│   │   └── compensate.py
│   ├── prompts.py             # WORKER_SYSTEM_PROMPT
│   ├── hooks.py               # AuditHooks
│   ├── schemas.py             # SQS payload, yield_events row
│   ├── slack_ui.py            # block-kit builder
│   └── weekly_report.py       # SES Lambda
├── tests/
│   ├── conftest.py
│   ├── test_worker.py
│   ├── test_margin.py         # calculator correctness
│   ├── test_filters.py        # 3h shift / baggage / layover rules
│   ├── test_saga.py           # compensating transactions
│   └── fixtures/traffics/alternative_flights.json
├── infra/                     # CDK TypeScript
│   ├── lib/mo-stack.ts
│   └── lib/saga.ts
└── evals/
    └── golden_set_50.jsonl    # 50 scored scenarios
```

### 0.3. CDK scaffold

```bash
cd infra && npx cdk init app --language typescript
npm i aws-cdk-lib constructs
npx cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/eu-central-1
```

### 0.4. CI skeleton (same as TravelGenie) + CDK diff step:

```yaml
- run: cd infra && npm ci && npx cdk diff --context env=staging
```

**Exit criteria:** `uv run pytest` green; `cdk synth` produces valid CloudFormation.

## Sprint 1 — Agent + margin logic (Weeks 2–3)

### 1.1. Calculator correctness
- Write `tests/test_margin.py` with 20 cases covering integer, decimal, and edge (zero delta) paths.
- Assert that the agent always calls `calculator` with the exact form `<old> - <new>` and never computes arithmetic inline.

### 1.2. Filter rules
- Implement filters as Python helpers in `filters.py` (callable from the prompt via tool OR encoded into prompt rules — start with prompt rules):
  - Baggage equivalence
  - Departure/arrival ±3h
  - Layover ≤ 4h
  - Booking class tier match

### 1.3. Worker prompt v1
- System prompt in `src/margin_optimizer/prompts.py`. Two guardrails:
  - Must finish with `"Task Complete. No action needed."` if no profitable alternative.
  - Must NEVER emit a `slack` call without first calling `calculator`.

### 1.4. Golden set evals
- `evals/golden_set_50.jsonl` — 50 Traffics response fixtures + expected behavior (post/silent).
- Runner:
  ```bash
  uv run python scripts/run_evals.py evals/golden_set_50.jsonl
  ```
- Release gate: 0 false-positive Slack posts in evals.

**Exit criteria:** 50/50 evals pass; calculator test suite green.

## Sprint 2 — Queue + ingest (Week 4)

### 2.1. SQS + DLQ
- CDK: `mo-pnr-queue` standard queue, DLQ after 3 receives, visibility = 180s.

### 2.2. Ingest Lambda
- Reads daily S3 dump (agreed interim shape with the agency: `s3://agency-dumps/bookings/<YYYY-MM-DD>.jsonl`).
- Filters and enqueues in batches of 10 (`SendMessageBatch`).
- Emits `ScannedPnrs` CloudWatch metric.

### 2.3. Worker wiring
- EventSourceMapping: SQS → Lambda with `reservedConcurrentExecutions=10`, batchSize=10.
- Lambda timeout = 30s (Traffics call + filter + margin calc + maybe Slack).

### 2.4. Load test
```bash
uv run python scripts/generate_mock_pnrs.py --count 10000 --out mock_pnrs.jsonl
aws s3 cp mock_pnrs.jsonl s3://agency-dumps/bookings/2026-04-20.jsonl
aws lambda invoke --function-name mo-ingest out.json
# Watch CloudWatch: ScannedPnrs should approach 10000 over ~3h
```

**Exit criteria:** 10k PNRs complete in 3h window; DLQ count = 0.

## Sprint 3 — Slack HITL (Week 5)

### 3.1. Slack app setup
- Create Slack app with `chat:write`, `chat:postMessage` scopes.
- Interactive components URL: `https://api.mo.example.com/slack/actions`.
- Copy signing secret → `mo/staging/slack:signingSecret` in Secrets Manager.

### 3.2. Block builder
- `src/margin_optimizer/slack_ui.py` — function returns block JSON per 5.3 spec in architecture doc.

### 3.3. Modify Lambda (non-LLM)
- `src/margin_optimizer/modify.py`:
  ```python
  def handler(event, context):
      body, sig, ts = event["body"], event["headers"]["x-slack-signature"], event["headers"]["x-slack-request-timestamp"]
      if not verify_slack_hmac(signing_secret, body, sig, ts):
          return {"statusCode": 401}
      payload = parse_slack_interactive(body)
      if payload["action_id"] == "approve_swap":
          sfn.start_execution(stateMachineArn=os.environ["SAGA_ARN"],
                              input=json.dumps(payload["value"]))
      return {"statusCode": 200}
  ```

### 3.4. Wire mo-worker to Slack
- Pass `SLACK_BOT_TOKEN`; call via `strands_tools.slack` with `chat.postMessage`.

**Exit criteria:** Slack click → saga starts within 2s (observed in CloudWatch).

## Sprint 4 — Saga + Aurora (Week 6)

### 4.1. Aurora Serverless v2
- CDK: `rds.DatabaseCluster` (Aurora PG 15), serverless v2 (0.5 min / 4 max ACU).
- Migration: `yield_events` table via `alembic` or plain SQL in `infra/sql/001_yield_events.sql`.

### 4.2. Step Functions saga
- ASL JSON in `infra/lib/saga.ts` per architecture doc §9.
- Each task Lambda in `src/margin_optimizer/saga/*.py`.

### 4.3. Dry-run mode
- `DRY_RUN=true` → Confirm Lambda logs what it *would* do, skips Traffics PATCH.

### 4.4. Integration tests
- `tests/test_saga.py` — mock Traffics with `responses`:
  - Success path → `yield_events` row written.
  - Failure at Step 2 → compensate reserve, original booking untouched.
  - Failure at Step 3 → compensate all.

**Exit criteria:** 10 real staging approvals all write `yield_events` rows; 1 chaos-injected failure rolls back cleanly.

## Sprint 5 — QuickSight + SES (Week 7)

### 5.1. QuickSight
- Dataset: Direct query against Aurora with IAM auth.
- Dashboards: Daily/Weekly/Monthly recovered EUR; hit rate; top 5 routes.
- Schedule: hourly refresh.

### 5.2. Weekly PDF
- `src/margin_optimizer/weekly_report.py`:
  - EventBridge cron(0 8 ? * MON *) TZ Europe/Berlin.
  - Renders QuickSight dashboard to PDF via `quicksight:StartDashboardSnapshotJob` or headless Chrome.
  - Emails via SES to ops distribution list.

**Exit criteria:** Monday 08:00 CET PDF received by ops team.

## Sprint 6 — Hardening + launch (Week 8)

- [ ] Chaos test: 25% synthetic 429 rate on Traffics — throughput degrades, no crashes, no DLQ overflow.
- [ ] Slack HMAC replay test: 6-minute-old signature → 401.
- [ ] Cost per scanned PNR measured from real staging data — must be ≤ 0.005 €.
- [ ] Disaster recovery: drop Aurora read replica, trigger saga, verify it still completes against primary.
- [ ] Flip `DRY_RUN=false` in prod; monitor first 24h closely.
- [ ] On-call runbook in `docs/runbook.md`.

**Exit criteria:** Prod launch approved by revenue + ops leads.

## Post-launch backlog

- Per-agency multi-tenancy (schema per tenant in Aurora).
- Predictive scan ("fly again in 3 days if price is still dropping") via time-series module.
- Hotel rate optimization (`alternative_hotels` endpoint — pending Traffics support).
- Auto-learn rejection thresholds from `RejectedChanges` metric.

## Commands cheat sheet

```bash
# Run unit + saga tests
uv run pytest -q

# Run golden-set evals
uv run python scripts/run_evals.py evals/golden_set_50.jsonl

# Manually invoke ingest
aws lambda invoke --function-name mo-ingest --region eu-central-1 out.json

# Tail worker logs
aws logs tail /aws/lambda/mo-worker --follow --region eu-central-1

# Inspect DLQ
aws sqs receive-message --queue-url $(aws sqs get-queue-url --queue-name mo-pnr-dlq --query QueueUrl --output text)

# Query recovered margin
psql $YIELD_DB_URL -c "SELECT DATE(mutated_at), SUM(delta_eur) FROM yield_events GROUP BY 1 ORDER BY 1 DESC LIMIT 7;"

# Deploy
cd infra && npx cdk deploy MoStack-staging --context env=staging
```
