# Uygulama Planı: MarginOptimizer

> **Durum:** Uygulanmaya hazır · **Kadans:** 2 haftalık sprint'ler · **Son güncelleme:** 2026-04-17

## Kilometre Taşları

| Sprint | Hafta | Çıkış kriteri |
|---|---|---|
| 0. Bootstrap | 1 | Repo + CI + CDK iskelet + dev döngüsü yeşil |
| 1. Agent + marj mantığı | 2–3 | Worker Lambda 100 mock PNR işler; calculator doğruluğu teyitli |
| 2. Kuyruk + ingest | 4 | 10k simüle PNR 3 saatlik pencerede SQS'ten akar, DLQ overflow yok |
| 3. Slack HITL | 5 | Approve/Reject tıklaması saga state machine'i uçtan uca tetikler |
| 4. Saga + Aurora | 6 | 10 gerçek staging onayında `yield_events` satırı yazılır |
| 5. QuickSight + SES | 7 | Dashboard canlı; Pazartesi PDF'i ops inbox'a düşer |
| 6. Sertleştirme + launch | 8 | Chaos test geçer; prod'da `DRY_RUN=false` |

## Sprint 0 — Bootstrap (Hafta 1)

### 0.1. Repo + araçlar

```bash
uv init --app
uv python pin 3.12
uv add strands-agents strands-agents-tools \
       ./strands-traffics \
       boto3 aws-lambda-powertools structlog pydantic sqlalchemy psycopg2-binary
uv add --dev pytest pytest-asyncio responses ruff mypy moto[all] locust
```

### 0.2. Dizin iskeleti

```
margin-optimizer/
├── pyproject.toml
├── .env.example
├── README.md
├── src/margin_optimizer/
│   ├── __init__.py
│   ├── ingest.py              # gece cron Lambda
│   ├── worker.py              # PNR başına agent Lambda
│   ├── modify.py              # LLM'siz mutasyon Lambda
│   ├── saga/                  # step functions task Lambda'ları
│   │   ├── reserve.py
│   │   ├── release.py
│   │   ├── confirm.py
│   │   └── compensate.py
│   ├── prompts.py             # WORKER_SYSTEM_PROMPT
│   ├── hooks.py               # AuditHooks
│   ├── schemas.py             # SQS payload, yield_events satırı
│   ├── slack_ui.py            # block-kit üreticisi
│   └── weekly_report.py       # SES Lambda
├── tests/
│   ├── conftest.py
│   ├── test_worker.py
│   ├── test_margin.py         # calculator doğruluğu
│   ├── test_filters.py        # 3s kayma / bagaj / aktarma kuralları
│   ├── test_saga.py           # compensating transaction'lar
│   └── fixtures/traffics/alternative_flights.json
├── infra/                     # CDK TypeScript
│   ├── lib/mo-stack.ts
│   └── lib/saga.ts
└── evals/
    └── golden_set_50.jsonl    # puanlanmış 50 senaryo
```

### 0.3. CDK iskeleti

```bash
cd infra && npx cdk init app --language typescript
npm i aws-cdk-lib constructs
npx cdk bootstrap aws://$(aws sts get-caller-identity --query Account --output text)/eu-central-1
```

### 0.4. CI iskeleti (TravelGenie ile aynı) + CDK diff adımı:

```yaml
- run: cd infra && npm ci && npx cdk diff --context env=staging
```

**Çıkış kriterleri:** `uv run pytest` yeşil; `cdk synth` geçerli CloudFormation üretir.

## Sprint 1 — Agent + marj mantığı (Hafta 2–3)

### 1.1. Calculator doğruluğu
- `tests/test_margin.py` 20 case ile: integer, decimal, edge (sıfır delta) yolları.
- Agent'ın aritmetiği inline hesaplamadığını, her zaman `calculator`'ı tam `<old> - <new>` formuyla çağırdığını assert et.

### 1.2. Filtre kuralları
- `filters.py` içinde Python helper'ları (prompt'tan tool olarak VEYA prompt kuralı olarak çağrılabilir — prompt kuralı ile başla):
  - Bagaj eşdeğerliği
  - Kalkış/varış ±3 saat
  - Aktarma ≤ 4 saat
  - Booking class tier eşleşmesi

### 1.3. Worker prompt v1
- `src/margin_optimizer/prompts.py` içinde sistem prompt'u. İki guardrail:
  - Kârlı alternatif yoksa `"Task Complete. No action needed."` ile bitir.
  - `calculator` çağırmadan ASLA `slack` çağrısı yapma.

### 1.4. Altın set evalleri
- `evals/golden_set_50.jsonl` — 50 Traffics response fixture + beklenen davranış (post/silent).
- Runner:
  ```bash
  uv run python scripts/run_evals.py evals/golden_set_50.jsonl
  ```
- Release gate: evallerde 0 false-positive Slack post.

**Çıkış kriterleri:** 50/50 eval geçer; calculator test suite'i yeşil.

## Sprint 2 — Kuyruk + ingest (Hafta 4)

### 2.1. SQS + DLQ
- CDK: `mo-pnr-queue` standard queue, 3 receive sonrası DLQ, visibility = 180s.

### 2.2. Ingest Lambda
- Günlük S3 dump'ı okur (acente ile anlaşılan ara form: `s3://agency-dumps/bookings/<YYYY-MM-DD>.jsonl`).
- Filtreler ve 10'lu batch'lerde enqueue eder (`SendMessageBatch`).
- `ScannedPnrs` CloudWatch metriği yayar.

### 2.3. Worker bağlantısı
- EventSourceMapping: SQS → Lambda, `reservedConcurrentExecutions=10`, batchSize=10.
- Lambda timeout = 30s (Traffics çağrısı + filtre + marj hesabı + belki Slack).

### 2.4. Yük testi
```bash
uv run python scripts/generate_mock_pnrs.py --count 10000 --out mock_pnrs.jsonl
aws s3 cp mock_pnrs.jsonl s3://agency-dumps/bookings/2026-04-20.jsonl
aws lambda invoke --function-name mo-ingest out.json
# CloudWatch izle: ScannedPnrs yaklaşık 3 saatte 10000'e yaklaşmalı
```

**Çıkış kriterleri:** 10k PNR 3 saatlik pencerede tamamlanır; DLQ sayısı = 0.

## Sprint 3 — Slack HITL (Hafta 5)

### 3.1. Slack app kurulumu
- `chat:write`, `chat:postMessage` scope'ları ile Slack app oluştur.
- Interactive components URL'i: `https://api.mo.example.com/slack/actions`.
- Signing secret → Secrets Manager'da `mo/staging/slack:signingSecret`.

### 3.2. Block builder
- `src/margin_optimizer/slack_ui.py` — architecture doc §5.3 spec'ine göre block JSON üreten fonksiyon.

### 3.3. Modify Lambda (LLM'siz)
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

### 3.4. mo-worker'ı Slack'e bağla
- `SLACK_BOT_TOKEN` geç; `strands_tools.slack` üzerinden `chat.postMessage` çağır.

**Çıkış kriterleri:** Slack tıklaması → saga 2 sn içinde başlar (CloudWatch'ta gözlemlendi).

## Sprint 4 — Saga + Aurora (Hafta 6)

### 4.1. Aurora Serverless v2
- CDK: `rds.DatabaseCluster` (Aurora PG 15), serverless v2 (0.5 min / 4 max ACU).
- Migrasyon: `yield_events` tablosu `alembic` veya düz SQL ile `infra/sql/001_yield_events.sql`.

### 4.2. Step Functions saga
- ASL JSON, architecture doc §9'a göre `infra/lib/saga.ts` içinde.
- Her task Lambda'sı `src/margin_optimizer/saga/*.py` içinde.

### 4.3. Dry-run modu
- `DRY_RUN=true` → Confirm Lambda *ne yapacağını* log'lar, Traffics PATCH'i atlar.

### 4.4. Entegrasyon testleri
- `tests/test_saga.py` — `responses` ile Traffics mock:
  - Başarı yolu → `yield_events` satırı yazıldı.
  - Adım 2'de hata → reserve compensate edildi, orijinal booking el değmemiş.
  - Adım 3'te hata → tümü compensate edildi.

**Çıkış kriterleri:** 10 gerçek staging onayının tümü `yield_events` satırı yazar; 1 chaos-enjekte hata temiz rollback yapar.

## Sprint 5 — QuickSight + SES (Hafta 7)

### 5.1. QuickSight
- Dataset: IAM auth ile Aurora'ya direkt sorgu.
- Dashboard: Günlük/Haftalık/Aylık kurtarılan EUR; hit oranı; top 5 rota.
- Schedule: saatlik refresh.

### 5.2. Haftalık PDF
- `src/margin_optimizer/weekly_report.py`:
  - EventBridge cron(0 8 ? * MON *) TZ Europe/Berlin.
  - QuickSight dashboard'ını `quicksight:StartDashboardSnapshotJob` veya headless Chrome ile PDF'e render eder.
  - Ops distro listesine SES ile mail atar.

**Çıkış kriterleri:** Pazartesi 08:00 CET'te ops ekibi PDF'i alır.

## Sprint 6 — Sertleştirme + launch (Hafta 8)

- [ ] Chaos test: Traffics'te %25 sentetik 429 oranı — throughput düşer, çökmez, DLQ overflow yok.
- [ ] Slack HMAC replay testi: 6 dk eski imza → 401.
- [ ] Taranan PNR başına maliyet gerçek staging verisiyle ölçüldü — ≤ 0.005 € olmalı.
- [ ] Disaster recovery: Aurora read replica'yı düşür, saga'yı tetikle, primary'e karşı tamamlandığını doğrula.
- [ ] Prod'da `DRY_RUN=false` → ilk 24 saati yakın izle.
- [ ] On-call runbook: `docs/runbook.md`.

**Çıkış kriterleri:** Prod launch revenue + ops lead'lerinin onayı ile.

## Launch sonrası backlog

- Acente başına multi-tenancy (Aurora'da tenant başına şema).
- Predictive scan ("fiyat hâlâ düşüyorsa 3 gün sonra tekrar uç") time-series modülü ile.
- Otel fiyatı optimizasyonu (`alternative_hotels` endpoint — Traffics desteği bekliyor).
- `RejectedChanges` metriğinden rejection eşiklerini otomatik öğrenme.

## Komut kısayolları

```bash
# Birim + saga testlerini çalıştır
uv run pytest -q

# Altın-set evalleri
uv run python scripts/run_evals.py evals/golden_set_50.jsonl

# Ingest'i manuel tetikle
aws lambda invoke --function-name mo-ingest --region eu-central-1 out.json

# Worker log'larını izle
aws logs tail /aws/lambda/mo-worker --follow --region eu-central-1

# DLQ'yu incele
aws sqs receive-message --queue-url $(aws sqs get-queue-url --queue-name mo-pnr-dlq --query QueueUrl --output text)

# Kurtarılan marjı sorgula
psql $YIELD_DB_URL -c "SELECT DATE(mutated_at), SUM(delta_eur) FROM yield_events GROUP BY 1 ORDER BY 1 DESC LIMIT 7;"

# Deploy
cd infra && npx cdk deploy MoStack-staging --context env=staging
```
