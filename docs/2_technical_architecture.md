# Technical Architecture: MarginOptimizer

> **Status:** Ready for implementation · **Region:** `eu-central-1` · **Last updated:** 2026-04-17

## 1. System Overview

MarginOptimizer is a headless, asynchronous batch system on AWS. A nightly EventBridge cron triggers ingestion → SQS fan-out → per-PNR Strands worker Lambdas (Bedrock Claude Haiku) that call `strands-traffics.use_traffics` for `/offers/{code}/alternativeFlights`, compute margin delta via `strands_tools.calculator`, and push Slack interactive approval cards. Approvals hit an API Gateway webhook that triggers a **non-LLM** modification Lambda — a Step Functions saga that mutates the booking via Traffics `PATCH /bookings/{id}` with full rollback. Successful mutations persist to `yield_events` in Aurora Postgres; QuickSight renders the dashboard.

## 2. Component Diagram

```mermaid
graph TD
    Cron[EventBridge cron<br/>02:00 Europe/Berlin] --> Ingest[Lambda: mo-ingest]
    Ingest -->|read active PNRs| BookStore[(Agency Booking Store<br/>S3 dump / replica)]
    Ingest -->|one msg per PNR| SQS[SQS: mo-pnr-queue]
    SQS -->|DLQ after 3 attempts| DLQ[SQS: mo-pnr-dlq]

    SQS -->|10 concurrent| Worker[Lambda: mo-worker]

    subgraph Agent Worker
        Worker --> Agent[Strands Agent<br/>Claude Haiku]
        Agent <--> Traf[strands-traffics<br/>use_traffics]
        Agent <--> Calc[calculator tool]
        Agent <--> Slack[slack tool]
        Agent <--> Journal[journal tool]
    end

    Traf <--> TrafAPI[Traffics Connector API v3<br/>connector.traffics.de]
    Slack -->|interactive blocks| Chan[#yield-ops Slack channel]

    Chan -->|Approve click| APIGW[API Gateway REST]
    APIGW --> Modify[Lambda: mo-modify<br/>non-LLM]
    Modify --> SF[Step Functions:<br/>reserve → release → confirm saga]
    SF <-->|PATCH /bookings/{id}| TrafAPI
    Modify -->|write row| YE[(Aurora Postgres:<br/>yield_events)]
    YE --> QS[QuickSight Dashboard]
    YE --> SES[SES: Monday 08:00 CET<br/>weekly PDF]
```

## 3. Technology Stack (pinned)

| Layer | Choice | Version / ID |
|---|---|---|
| Runtime | Python | 3.12 |
| Package mgr | `uv` | ≥ 0.5 |
| Agent SDK | `strands-agents` | latest |
| Tool wrapper | `strands-traffics` | 0.1.x |
| Tools pkg | `strands-agents-tools` | latest |
| LLM (worker) | Bedrock Claude Haiku | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Ingest compute | AWS Lambda (zip) | Python 3.12 |
| Worker compute | AWS Lambda (container) | Python 3.12 |
| Modify compute | AWS Lambda (zip, no LLM) | Python 3.12 |
| Queue | Amazon SQS standard | visibility = 6 × Lambda timeout |
| Scheduler | Amazon EventBridge | cron(0 2 * * ? *) EU/Berlin |
| Orchestration | AWS Step Functions | Standard (saga) |
| State | Amazon Aurora PostgreSQL | 15.x, Serverless v2 |
| Secrets | AWS Secrets Manager | — |
| Dashboard | Amazon QuickSight | Enterprise edition |
| Weekly report | Amazon SES | — |
| IaC | AWS CDK (TypeScript) | ≥ 2.150 |
| Observability | CloudWatch Logs & Metrics | — |

## 4. Minimal Agent Code (reference)

```python
# src/margin_optimizer/worker.py
import os, json
from strands import Agent
from strands.models import BedrockModel
from strands_traffics import use_traffics
from strands_tools import calculator, slack, journal

from .hooks import AuditHooks
from .prompts import WORKER_SYSTEM_PROMPT

def build_worker_agent() -> Agent:
    return Agent(
        agent_id="mo-worker",
        model=BedrockModel(
            model_id=os.environ.get(
                "BEDROCK_MODEL_ID",
                "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            ),
            region_name=os.environ.get("AWS_REGION", "eu-central-1"),
            temperature=0.0,  # deterministic parsing
            streaming=False,
        ),
        system_prompt=WORKER_SYSTEM_PROMPT,
        tools=[use_traffics, calculator, slack, journal],
        hooks=[AuditHooks()],
    )

def handler(event, context):
    for record in event["Records"]:
        payload = json.loads(record["body"])
        agent = build_worker_agent()
        prompt = (
            f"Booking {payload['booking_id']}: offerCode={payload['offer_code']}, "
            f"current flight cost={payload['current_price']} EUR, "
            f"baggage={payload['baggage']}, class={payload['class']}. "
            f"Find cheaper equivalent alternatives via Traffics. "
            f"Only surface alternatives saving > {os.environ['MIN_MARGIN_EUR']} EUR."
        )
        agent(prompt)
```

## 5. Data Flows

### 5.1. Nightly ingest

1. EventBridge fires `cron(0 2 * * ? *)` (TZ Europe/Berlin) → `mo-ingest`.
2. `mo-ingest` reads the day's active PNR snapshot from S3 (initially a daily dump; Month 2 promotes to a read replica).
3. Filters: `status = CONFIRMED`, `departure_date > now() + 24h`.
4. Writes one SQS message per PNR, payload ≈ 500 bytes.
5. Emits metric `ScannedPnrs` = count of enqueued messages.

### 5.2. Worker (per PNR)

6. Lambda `mo-worker` polls SQS in batches of 10, concurrency = 10 (≈ 5 TPS into Traffics).
7. Agent calls:
   ```json
   use_traffics(service="offers", endpoint="alternative_flights", params='{"code": "TRAF-9921"}')
   ```
8. Agent filters candidates — drops those that change baggage, shift times > 3h, add > 4h layovers, or change class tier.
9. Agent calls `calculator` with exact prompt: `"<old_price> - <new_price>"`.
10. If delta > `MIN_MARGIN_EUR`, agent calls `slack` with interactive blocks (see 5.3). Otherwise agent outputs `"Task Complete. No action needed."` and exits.

### 5.3. Slack approval card

```json
{
  "blocks": [
    {"type": "section", "text": {"type": "mrkdwn",
      "text": "*Margin opportunity* · Booking `9921` · Customer `M.Y.`"}},
    {"type": "section", "fields": [
      {"type": "mrkdwn", "text": "*Old:* TK1234 500 €"},
      {"type": "mrkdwn", "text": "*New:* PC3030 420 €"},
      {"type": "mrkdwn", "text": "*Delta:* +80 € (16%)"},
      {"type": "mrkdwn", "text": "*Baggage:* 1x20kg ✅"}
    ]},
    {"type": "actions", "elements": [
      {"type": "button", "style": "primary",
       "text": {"type": "plain_text", "text": "Approve"},
       "value": "{\"booking_id\":\"9921\",\"offer_code_new\":\"PC3030\"}",
       "action_id": "approve_swap"},
      {"type": "button", "style": "danger",
       "text": {"type": "plain_text", "text": "Reject"},
       "action_id": "reject_swap"}
    ]}
  ]
}
```

### 5.4. Approval → mutation saga (non-LLM)

11. Slack POSTs interactive payload → API Gateway `/slack/actions` → `mo-modify` Lambda.
12. `mo-modify` verifies Slack HMAC signature (`X-Slack-Signature`, `X-Slack-Request-Timestamp`) — rejects if > 5 min old.
13. Starts Step Functions execution (saga):
    - **Step 1:** `reserve_new_flight` → Traffics `POST /offers/{new}/reserve`.
    - **Step 2:** `release_old_flight` → Traffics `DELETE /offers/{old}/reservation`.
    - **Step 3:** `confirm` → Traffics `PATCH /bookings/{id}` (idempotency key = `{booking_id}:{offer_code_new}`).
14. Any step failure triggers compensating actions that roll back prior steps — original booking untouched.
15. On success: insert `yield_events` row; ack Slack with 200; post confirmation block in thread.

### 5.5. Observability & reporting

- CloudWatch metrics: `ScannedPnrs`, `ProfitableAlternativesFound`, `ApprovedChanges`, `RejectedChanges`, `MutationFailures`.
- `yield_events` schema: `id, booking_id, old_offer_code, new_offer_code, delta_eur, approved_by, approved_at, mutated_at, status`.
- QuickSight dataset refreshes hourly.
- Monday 08:00 CET: Lambda `mo-weekly-report` renders PDF via headless Chrome → SES.

## 6. Environment Variables

| Variable | Scope | Example |
|---|---|---|
| `AWS_REGION` | all | `eu-central-1` |
| `BEDROCK_MODEL_ID` | worker | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| `MIN_MARGIN_EUR` | worker, modify | `30` |
| `MAX_DEPARTURE_SHIFT_HOURS` | worker | `3` |
| `TRAFFICS_API_KEY` | worker, modify | Secrets Manager |
| `SLACK_BOT_TOKEN` | worker | Secrets Manager |
| `SLACK_SIGNING_SECRET` | modify | Secrets Manager |
| `SLACK_CHANNEL_ID` | worker | `C01ABCD2345` |
| `YIELD_DB_URL` | modify, weekly | `postgresql://...` (Secrets Manager) |
| `DRY_RUN` | modify | `true` in staging — skips PATCH |
| `BYPASS_TOOL_CONSENT` | worker | `true` (Lambda required) |

## 7. Secrets Manager Layout

| Secret name | Keys |
|---|---|
| `mo/{env}/traffics` | `apiKey` |
| `mo/{env}/slack` | `botToken`, `signingSecret` |
| `mo/{env}/db` | `host`, `port`, `user`, `password`, `dbname` |

## 8. IAM (least-privilege)

**`mo-ingest` role:** `s3:GetObject` on booking-dump bucket; `sqs:SendMessage` on `mo-pnr-queue`; `secretsmanager:GetSecretValue`; CloudWatch Logs.

**`mo-worker` role:** `sqs:ReceiveMessage`, `DeleteMessage` on queue; `bedrock:InvokeModel` on the Haiku ARN; `secretsmanager:GetSecretValue`; `chat.postMessage` via Slack token (not IAM).

**`mo-modify` role:** `states:StartExecution` on the saga state machine ARN; `secretsmanager:GetSecretValue`; `rds-data:ExecuteStatement` on `yield_events`.

**Explicitly denied across all roles:** `iam:*`, mutation of infrastructure, S3 outside named buckets.

## 9. Saga State Machine (ASL sketch)

```json
{
  "StartAt": "ReserveNew",
  "States": {
    "ReserveNew": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:mo-traffics-reserve",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "RollbackNothing"}],
      "Next": "ReleaseOld"
    },
    "ReleaseOld": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:mo-traffics-release",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "CompensateReserve"}],
      "Next": "Confirm"
    },
    "Confirm": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:mo-traffics-confirm",
      "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "CompensateAll"}],
      "Next": "WriteYieldEvent"
    },
    "WriteYieldEvent": {"Type": "Task", "Resource": "...", "End": true},
    "RollbackNothing": {"Type": "Pass", "Next": "FailJournal"},
    "CompensateReserve": {"Type": "Task", "Resource": "...", "Next": "FailJournal"},
    "CompensateAll": {"Type": "Task", "Resource": "...", "Next": "FailJournal"},
    "FailJournal": {"Type": "Task", "Resource": "...", "End": true}
  }
}
```

## 10. Resilience

| Failure | Handling |
|---|---|
| Traffics 429 | `urllib3.Retry` built into `strands-traffics` (3 attempts, 0.5 s). Persistent → DLQ after 3 SQS attempts. |
| Traffics 5xx during saga | Step Functions retry + catch → compensating action. |
| Slack outage | Worker journals the opportunity; daily 08:00 digest via SES if Slack was down. |
| Bedrock throttling | `ModelRetryStrategy` default. If hit rate > 10%, reduce worker concurrency. |
| DB write failure | Queue `yield_events` row to SQS fallback; replay every 5 min. |
| Saga partial failure | Compensating transactions + journal entry with red marker posted in Slack thread. |

## 11. Cost & Scaling

- **Cost ceiling:** ≤ 0.005 €/PNR. At 10k PNRs = ≤ 50 €/night. Breakdown:
  - Haiku: ~300 tokens in + ~200 out per PNR @ $0.80/$4.00 per 1M → ≈ $0.001.
  - Traffics: agency contract (assume flat).
  - AWS Lambda + SQS: < 10 € / 10k PNRs at current pricing.
- **Worker concurrency floor:** 10 (≈ 5 Traffics TPS with 2 calls/PNR).
- **Worker concurrency ceiling:** raise only after Traffics clears > 10 TPS allocation.
- **Aurora Serverless v2 ACUs:** min 0.5, max 4 — scales with QuickSight query load.

## 12. Security

- Slack HMAC verification mandatory before any DB read or Traffics write.
- Timestamp skew tolerance: 5 min (stops replay attacks).
- Traffics API key per environment; rotated every 90 days via Secrets Manager rotation.
- No PII in CloudWatch: worker logs customer initials only (e.g., `M.Y.`).
- Dry-run default: new environments ship with `DRY_RUN=true` until first green staging canary.
- Outbound allowlist: `bedrock.eu-central-1.amazonaws.com`, `connector.traffics.de`, `slack.com`.

## 13. Open Architectural Decisions

- **Aurora vs. DynamoDB for `yield_events`?** Aurora — QuickSight SQL native; analytical joins on `route_pair`, `airline_pair` are easier.
- **Direct replica vs. daily dump for booking ingest?** MVP: daily S3 dump (simpler, agency-side minimal work). Month 2: promote to Postgres logical replica for 15-min freshness.
- **Re-run of rejected alternatives?** MVP: never re-offer a rejected swap for the same PNR/route. Phase 2: learn from rejection patterns to improve filter thresholds.
