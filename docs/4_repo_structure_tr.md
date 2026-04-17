# Repo Yapısı: MarginOptimizer

> **Durum:** Uygulanmaya hazır · **Son güncelleme:** 2026-04-17

## Üst seviye düzen

```
margin-optimizer/
├── README.md                          # quickstart, env tablosu, run komutları
├── pyproject.toml                     # uv config, pin'li bağımlılıklar
├── uv.lock
├── .env.example
├── .gitignore
├── Dockerfile.worker                  # mo-worker Lambda için container
├── Dockerfile.ingest                  # mo-ingest için slim image
├── docs/
│   ├── 1_product_requirements_document.md
│   ├── 1_product_requirements_document_tr.md
│   ├── 2_technical_architecture.md
│   ├── 2_technical_architecture_tr.md
│   ├── 3_implementation_plan.md
│   ├── 3_implementation_plan_tr.md
│   ├── 4_repo_structure.md
│   ├── 4_repo_structure_tr.md         # bu dosya
│   ├── 5_dev_setup.md
│   ├── 5_dev_setup_tr.md
│   ├── 6_prompt_design.md
│   ├── 6_prompt_design_tr.md
│   └── runbook.md                     # on-call prosedürleri
├── src/margin_optimizer/
│   ├── __init__.py
│   ├── ingest.py                      # gece cron Lambda
│   ├── worker.py                      # SQS-tetiklemeli agent Lambda
│   ├── modify.py                      # LLM'siz Slack webhook Lambda
│   ├── weekly_report.py               # Pazartesi 08:00 SES Lambda
│   ├── prompts.py                     # WORKER_SYSTEM_PROMPT
│   ├── hooks.py                       # AuditHooks (tool call başına JSON)
│   ├── filters.py                     # bagaj/zamanlama/aktarma/sınıf kuralları
│   ├── schemas.py                     # Pydantic: SqsPayload, YieldEvent
│   ├── slack_ui.py                    # Block Kit üreticisi
│   ├── slack_verify.py                # HMAC doğrulama
│   ├── secrets.py                     # Secrets Manager helper
│   ├── db.py                          # Aurora bağlantısı + yield_events insert
│   └── saga/
│       ├── __init__.py
│       ├── reserve.py                 # Step Fn task: POST /offers/{new}/reserve
│       ├── release.py                 # Step Fn task: DELETE /offers/{old}
│       ├── confirm.py                 # Step Fn task: PATCH /bookings/{id}
│       ├── compensate.py              # her adım için compensating action
│       └── journal.py                 # başarısızlık journal writer
├── scripts/
│   ├── run_evals.py
│   ├── generate_mock_pnrs.py          # test SQS payload'ları üretir
│   ├── seed_yield_events.py           # Aurora'yı QuickSight için demo satırlarla doldurur
│   └── replay_dlq.py                  # DLQ'yu ana kuyruğa geri boşaltır
├── tests/
│   ├── conftest.py
│   ├── fixtures/
│   │   └── traffics/
│   │       ├── alternative_flights_cheaper.json
│   │       ├── alternative_flights_none.json
│   │       └── alternative_flights_bad_baggage.json
│   ├── test_worker.py                 # prompt → beklenen tool çağrıları
│   ├── test_margin.py                 # calculator doğruluğu
│   ├── test_filters.py                # bagaj, aktarma, sınıf kuralları
│   ├── test_slack_verify.py           # HMAC happy + replay + bozuk sig
│   ├── test_saga.py                   # happy + compensate yolları
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
    │   ├── mo-stack.ts                # ana kompozisyon
    │   ├── queue-construct.ts         # SQS + DLQ
    │   ├── worker-construct.ts        # worker Lambda + SQS ESM
    │   ├── modify-construct.ts        # modify Lambda + API GW
    │   ├── saga-construct.ts          # Step Functions state machine
    │   ├── db-construct.ts            # Aurora Serverless v2
    │   ├── analytics-construct.ts     # QuickSight + SES haftalık
    │   └── observability-construct.ts
    └── sql/
        └── 001_yield_events.sql       # Aurora migrasyonu
```

## Modül sorumlulukları

### `src/margin_optimizer/ingest.py`
EventBridge ile tetiklenir. Acente booking'lerinin günlük S3 dump'ını okur, confirmed + future olarak filtreler, 10'lu batch'lerde PNR başına 1 SQS mesajı yazar. `ScannedPnrs` metriği yayar. LLM yok.

### `src/margin_optimizer/worker.py`
SQS tetiklemeli. Her SQS mesajı için bir Strands Agent kurar (ucuz — Haiku). Agent sistem prompt'u şunu zorlar: `use_traffics` çağır, `calculator` çağır, opsiyonel `slack` çağrısı, son mesajı yaz. Burada DB yazımı yok.

### `src/margin_optimizer/modify.py`
Slack webhook girişi. HMAC doğrular, interaktif payload parse eder, Step Functions execution başlatır. Sıfır LLM. Compliance için kritik: buradan Traffics'i doğrudan ASLA çağırma — sadece saga task'leri üzerinden.

### `src/margin_optimizer/saga/*.py`
Step Functions task başına bir Python modülü. Her biri standalone Lambda. Idempotent tasarım — her biri aksiyon öncesi DynamoDB'de dedupe key'e yazar.

### `src/margin_optimizer/filters.py`
Alternatif-uçuş dict'leri üzerinde saf fonksiyonlar: `is_baggage_equivalent`, `within_schedule_window`, `layover_acceptable`, `same_class_tier`. Yoğun birim test edilir; LLM prompt'u semantiklerine atıfta bulunur ama worker alternatifler alındıktan sonra bunları explicit çalıştırır.

### `src/margin_optimizer/prompts.py`
Sadece `WORKER_SYSTEM_PROMPT`. Haiku input maliyetini sınırlamak için ≤ 800 token tutulur.

### `src/margin_optimizer/schemas.py`
DB DDL'ine yansıtılmış Pydantic modelleri. SQS payload şekli ve `yield_events` satır yapısı için source of truth.

### `src/margin_optimizer/slack_verify.py`
`verify_slack_hmac(signing_secret, body, signature_header, timestamp_header) -> bool`. 5 dakika skew; bozuk sig reddedilir.

### `src/margin_optimizer/db.py`
`get_engine()` Secrets Manager'dan Aurora URL'ine bağlı SQLAlchemy engine döner. `write_yield_event(row: YieldEvent)` tek yazma yolu — yalnızca saga confirm adımından kullanılır.

### `scripts/generate_mock_pnrs.py`
Yük testi için `mock_pnrs.jsonl` yazan CLI. Faker ile booking ID, gerçekçi EUR fiyatlar, bagaj varyasyonları üretir.

### `infra/lib/saga-construct.ts`
Step Functions state machine'i kapsüller. `.stateMachineArn`'i modify Lambda'sına geçirilmek üzere expose eder.

## Dosya sahipliği ve kuralları

| Yol | Sahip | Değişiklik kadansı |
|---|---|---|
| `docs/runbook.md` | sre | on-call iterasyonlarında |
| `src/margin_optimizer/prompts.py` | ai eng | haftalık (evaller ile korunur) |
| `src/margin_optimizer/saga/` | platform + ai | her Traffics şema değişimi |
| `infra/sql/` | platform | append-only; uygulanmış migrasyonu düzenleme |
| `evals/golden_set_50.jsonl` | ai eng + qa | prod'da yakalanan false positive'lerle büyür |

## İsimlendirme kuralları

- Lambda mantıksal adı: `mo-ingest`, `mo-worker`, `mo-modify`, `mo-saga-reserve`, vb.
- CloudFormation resource ID'leri: `MoIngestFn`, `MoWorkerFn`, `MoSagaReserveFn`.
- SQS queue: `mo-pnr-queue`, `mo-pnr-dlq`.
- CloudWatch metrikleri: `Mo<Capitalized>` — `MoScannedPnrs`, `MoMutationFailures`.
- Secret'lar: `mo/<env>/<service>` — `mo/prod/slack`.
- Aurora şeması: MVP'de tek `public` şema; Faz 2'de tenant başına şema.

## Bu repo'ya ASLA girmeyecekler

- Gerçek PNR veya müşteri isimleri — fixture'larda bile. `scripts/generate_mock_pnrs.py` ile anonimleştir.
- Slack signing secret, Traffics API key, DB şifresi — sadece Secrets Manager.
- Node `node_modules/`.
- Account ID gömebilecek ham QuickSight dashboard JSON export'ları — commit öncesi redact et.
