# Geliştirici Kurulumu: MarginOptimizer

> **Durum:** Onboarding'e hazır · **İlk lokal worker run hedefi: 60 dakika** · **Son güncelleme:** 2026-04-17

## Ön gereksinimler

| Araç | Sürüm | Not |
|---|---|---|
| Python | 3.12 | `uv python install 3.12` |
| `uv` | ≥ 0.5 | |
| Node.js | ≥ 20 | AWS CDK için |
| AWS CLI v2 | ≥ 2.15 | |
| Docker | ≥ 25 | worker container'da çalışır |
| PostgreSQL client | ≥ 15 | Aurora sorguları için `psql` |
| `ngrok` veya `cloudflared` | latest | Slack interactive callback'lerini lokal'de almak için |

## 1. Clone & bağımlılıklar

```bash
git clone https://github.com/mertozbas/margin-optimizer.git
cd margin-optimizer

uv sync
```

## 2. AWS erişimi

```bash
aws configure sso --profile mo-dev
export AWS_PROFILE=mo-dev
export AWS_REGION=eu-central-1
aws sts get-caller-identity
```

Gerekli yetkiler (dev rolü):
- `eu-central-1`'de Haiku için `bedrock:InvokeModel`
- `mo-*-dev` kuyruklarında `sqs:*`
- `mo/dev/*` için `secretsmanager:GetSecretValue`
- `MoSaga-dev` için `states:StartExecution`
- `mo-yield-events-dev` Aurora cluster'ına read/write (Secrets Manager üzerinden)

### Bedrock Haiku erişimi

Console → Bedrock → Model access → Claude Haiku 4.5.

## 3. Ortam dosyası

```bash
cp .env.example .env
```

`.env`'i düzenle:

```bash
AWS_REGION=eu-central-1
AWS_PROFILE=mo-dev
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
MIN_MARGIN_EUR=30
MAX_DEPARTURE_SHIFT_HOURS=3

# Slack (staging workspace değerleri)
SLACK_BOT_TOKEN=xoxb-your-dev-bot
SLACK_SIGNING_SECRET=dev-signing-secret
SLACK_CHANNEL_ID=C01DEV0000

# Aurora (Secrets Manager'dan al — hardcode etme)
YIELD_DB_URL=postgresql+psycopg2://...

# Flag'ler
DRY_RUN=true
ENV=dev
LOG_LEVEL=DEBUG
BYPASS_TOOL_CONSENT=true

# Traffics
TRAFFICS_API_KEY=<senin-dev-key>
```

## 4. Lokal mock kuyruk seed

Hızlı iterasyon için, worker'ı SQS yerine lokal fixture dosyalarına karşı koştur:

```bash
uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
uv run python -m margin_optimizer.worker --from-file /tmp/mock_pnrs.jsonl --dry-run
```

Beklenen: her PNR için ya `Task Complete. No action needed.` ya da `Slack card would be posted: {booking_id=..., delta=...}` log satırı.

## 5. Full test suite

```bash
uv run pytest -q
uv run pytest -q tests/test_saga.py           # subset
uv run pytest -q tests/test_slack_verify.py   # sadece HMAC testleri
```

## 6. Slack HMAC'i lokal test et

`modify.py`'ı lokal tunnel ile çalıştır:

```bash
uv run uvicorn margin_optimizer.modify:asgi_app --port 8080 &
ngrok http 8080
# https URL'ini Slack app → Interactivity → Request URL'e yapıştır
# Test Slack mesajından Approve/Reject butonlarına tıkla
```

`DRY_RUN=true` Traffics PATCH'in çağrılmamasını sağlar — saga niyet edilen mutasyonu log'lar.

## 7. Aurora dev'e bağlan

```bash
PGURL=$(aws secretsmanager get-secret-value \
  --secret-id mo/dev/db \
  --query SecretString --output text | jq -r '"\(.user):\(.password)@\(.host):\(.port)/\(.dbname)"')

psql "postgresql://$PGURL"
# psql içinde:
\d yield_events
SELECT * FROM yield_events ORDER BY mutated_at DESC LIMIT 5;
```

## 8. CDK (staging diff)

```bash
cd infra
npm ci
npx cdk diff --context env=staging
# Deploy sadece CI.
```

## 9. Kullanışlı tek satırlıklar

```bash
# Dev SQS'e 1 mock PNR gönder
aws sqs send-message \
  --queue-url $(aws sqs get-queue-url --queue-name mo-pnr-queue-dev --query QueueUrl --output text) \
  --message-body "$(cat tests/fixtures/sqs_payload.json)"

# Worker log'larını izle
aws logs tail /aws/lambda/mo-worker-dev --follow

# DLQ boşalt
uv run python scripts/replay_dlq.py --env dev --max 10

# Dünkü kurtarılan marjı sorgula
psql "$YIELD_DB_URL" -c "SELECT SUM(delta_eur) FROM yield_events WHERE DATE(mutated_at) = CURRENT_DATE - 1;"

# Saga'yı manuel tetikle (ileri seviye — genelde Slack üzerinden)
aws stepfunctions start-execution \
  --state-machine-arn $MO_SAGA_ARN \
  --input '{"booking_id":"DEV-0001","offer_code_new":"PC-NEW"}'
```

## 10. IDE & hijyen

- VS Code + Python + SQLTools (Postgres) + ESLint + Ruff.
- Pre-commit hook'ları: `ruff`, `ruff format`, `mypy src`, `pytest -q tests/test_slack_verify.py tests/test_filters.py`.

## 11. Sorun giderme

### Worker "calculator tool not found" diyor
Pull sonrası `uv sync` unutulmuş — strands-agents-tools bir runtime dep.

### Saga `CompensateAll`'u hemen tetikliyor
Traffics dev sandbox'ı kontrol et — offer code'ları günlük döner. Mock PNR'ları yeniden üret.

### Slack buton tıklaması 401 dönüyor
HMAC doğrulama başarısız. Yaygın sebepler:
1. Clock skew > 5 dk (sistem saatini resync et).
2. Yanlış signing secret (app'in hangi workspace'e bağlı olduğunu kontrol et).
3. Body ngrok tarafından mutasyona uğramış — raw byte okuduğundan emin ol.

### Aurora bağlantısı timeout
Security group erişimi Lambda SG'ye kısıtlı. Lokal dev için Session Manager port forwarding:
```bash
aws ssm start-session --target <bastion-instance-id> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters 'host=<aurora-endpoint>,portNumber=5432,localPortNumber=5433'
```

## 12. YAPMA!

- Dev'de `DRY_RUN=false` yapma — staging Traffics booking'lerini yanlışlıkla mutasyona uğratırsın.
- `.env` veya Aurora şifresi commit'leme.
- Ops lead onayı olmadan prod'da `scripts/replay_dlq.py` çalıştırma.
- Slack signing secret'larını ortamlar arası paylaşma — her env'in kendi Slack app'i var.
- "Sadece test için" `modify.py`'da HMAC doğrulamayı atla — code path güvenlik-kritik.
