# Developer Setup: MarginOptimizer

> **Status:** Ready for onboarding · **Target time to first local worker run: 60 minutes** · **Last updated:** 2026-04-17

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.12 | `uv python install 3.12` |
| `uv` | ≥ 0.5 | |
| Node.js | ≥ 20 | for AWS CDK |
| AWS CLI v2 | ≥ 2.15 | |
| Docker | ≥ 25 | worker runs in a container |
| PostgreSQL client | ≥ 15 | `psql` for Aurora queries |
| `ngrok` or `cloudflared` | latest | to receive Slack interactive callbacks locally |

## 1. Clone & dependencies

```bash
git clone https://github.com/mertozbas/margin-optimizer.git
cd margin-optimizer

uv sync
```

## 2. AWS access

```bash
aws configure sso --profile mo-dev
export AWS_PROFILE=mo-dev
export AWS_REGION=eu-central-1
aws sts get-caller-identity
```

Required permissions (dev role):
- `bedrock:InvokeModel` on Haiku in `eu-central-1`
- `sqs:*` on `mo-*-dev` queues
- `secretsmanager:GetSecretValue` on `mo/dev/*`
- `states:StartExecution` on `MoSaga-dev`
- Read/write on `mo-yield-events-dev` Aurora cluster (via Secrets Manager)

### Bedrock Haiku access

Request in Console → Bedrock → Model access → Claude Haiku 4.5.

## 3. Environment file

```bash
cp .env.example .env
```

Edit `.env`:

```bash
AWS_REGION=eu-central-1
AWS_PROFILE=mo-dev
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
MIN_MARGIN_EUR=30
MAX_DEPARTURE_SHIFT_HOURS=3

# Slack (set to staging workspace values)
SLACK_BOT_TOKEN=xoxb-your-dev-bot
SLACK_SIGNING_SECRET=dev-signing-secret
SLACK_CHANNEL_ID=C01DEV0000

# Aurora (get from Secrets Manager — don't hardcode)
YIELD_DB_URL=postgresql+psycopg2://...

# Flags
DRY_RUN=true
ENV=dev
LOG_LEVEL=DEBUG
BYPASS_TOOL_CONSENT=true

# Traffics
TRAFFICS_API_KEY=<your-dev-key>
```

## 4. Seed a local mock queue

For fast iteration, run the worker against local fixture files instead of SQS:

```bash
uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
uv run python -m margin_optimizer.worker --from-file /tmp/mock_pnrs.jsonl --dry-run
```

Expected: for each PNR, a log line either `Task Complete. No action needed.` or `Slack card would be posted: {booking_id=..., delta=...}`.

## 5. Run the full test suite

```bash
uv run pytest -q
uv run pytest -q tests/test_saga.py           # subset
uv run pytest -q tests/test_slack_verify.py   # HMAC tests only
```

## 6. Test Slack HMAC locally

Launch `modify.py` against a local tunnel:

```bash
uv run uvicorn margin_optimizer.modify:asgi_app --port 8080 &
ngrok http 8080
# Paste the https URL into Slack app → Interactivity → Request URL
# Click the Approve/Reject buttons from a test Slack message
```

`DRY_RUN=true` ensures Traffics PATCH is NOT called — saga logs the intended mutation.

## 7. Connect to Aurora dev

```bash
PGURL=$(aws secretsmanager get-secret-value \
  --secret-id mo/dev/db \
  --query SecretString --output text | jq -r '"\(.user):\(.password)@\(.host):\(.port)/\(.dbname)"')

psql "postgresql://$PGURL"
# Inside psql:
\d yield_events
SELECT * FROM yield_events ORDER BY mutated_at DESC LIMIT 5;
```

## 8. CDK (staging diff)

```bash
cd infra
npm ci
npx cdk diff --context env=staging
# Deploy is CI-only.
```

## 9. Useful one-liners

```bash
# Enqueue 1 mock PNR to dev SQS
aws sqs send-message \
  --queue-url $(aws sqs get-queue-url --queue-name mo-pnr-queue-dev --query QueueUrl --output text) \
  --message-body "$(cat tests/fixtures/sqs_payload.json)"

# Tail worker logs
aws logs tail /aws/lambda/mo-worker-dev --follow

# Drain DLQ
uv run python scripts/replay_dlq.py --env dev --max 10

# Query yesterday's recovered margin
psql "$YIELD_DB_URL" -c "SELECT SUM(delta_eur) FROM yield_events WHERE DATE(mutated_at) = CURRENT_DATE - 1;"

# Manually trigger the saga (advanced — usually via Slack)
aws stepfunctions start-execution \
  --state-machine-arn $MO_SAGA_ARN \
  --input '{"booking_id":"DEV-0001","offer_code_new":"PC-NEW"}'
```

## 10. IDE & hygiene

- VS Code + Python + SQLTools (Postgres) + ESLint + Ruff.
- Pre-commit hooks: `ruff`, `ruff format`, `mypy src`, `pytest -q tests/test_slack_verify.py tests/test_filters.py`.

## 11. Troubleshooting

### Worker says "calculator tool not found"
Forgot to `uv sync` after pulling — strands-agents-tools is a runtime dep.

### Saga fails with `CompensateAll` triggered immediately
Check Traffics dev sandbox — offer codes rotate daily. Regenerate mock PNRs.

### Slack button click returns 401
HMAC verification failed. Common causes:
1. Clock skew > 5 min (re-sync system clock).
2. Wrong signing secret (check which workspace your app points to).
3. Body mutated by ngrok — make sure you're reading raw bytes.

### Aurora connection times out
Security group restricts access to Lambda SG. For local dev, use Session Manager port forwarding:
```bash
aws ssm start-session --target <bastion-instance-id> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters 'host=<aurora-endpoint>,portNumber=5432,localPortNumber=5433'
```

## 12. What NOT to do

- Don't `DRY_RUN=false` in dev — you'll accidentally mutate staging Traffics bookings.
- Don't commit `.env` or Aurora passwords.
- Don't run `scripts/replay_dlq.py` in prod without ops lead approval.
- Don't share Slack signing secrets across environments — each env has its own Slack app.
- Don't skip HMAC verification in `modify.py` "just for testing" — the code path is security-critical.
