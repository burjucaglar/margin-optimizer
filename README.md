# MarginOptimizer

**B2B headless yield-management motoru** — acenteler için satılmış Pauschal rezervasyonlarda geceki flight-swap otomasyonu. Strands Agents + Bedrock Claude Haiku 4.5 + Traffics Connector API v3 + Slack HITL onay + Step Functions saga + Aurora Postgres.

> **Durum:** Sprint 0 tamam · Sprint 1 kısmi (worker iskeleti + dry-run CLI çalışıyor, testler + ingest Sprint 2 bekliyor) · **Bölge:** `eu-central-1` · **Son güncelleme:** 2026-04-17

Güncel uygulama durumu, kurulum ve çalıştırma komutları için: **[docs/progress/01_current_state_tr.md](docs/progress/01_current_state_tr.md)** · [EN](docs/progress/01_current_state.md)

[English docs below](#english)

---

## Özet

Her gece 02:00'de (Europe/Berlin), acentenin aktif Pauschal PNR'ları taranır. PNR başına bir Strands Haiku worker, `use_traffics` ile eşdeğer ama daha ucuz alternatif uçuşları bulur, `calculator` ile marj delta'sını deterministik hesaplar ve eşiği aşanlar için Slack onay kartı gönderir. Onay → API Gateway webhook → **LLM'siz** modify Lambda → Step Functions saga → Traffics `PATCH /bookings/{id}`. Başarılı mutasyonlar Aurora `yield_events` tablosuna yazılır; QuickSight dashboard + haftalık SES PDF.

## Dokümantasyon

| # | Doküman | Türkçe | English |
|---|---|---|---|
| 1 | Ürün Gereksinimleri (PRD) | [→](docs/1_product_requirements_document_tr.md) | [→](docs/1_product_requirements_document.md) |
| 2 | Teknik Mimari | [→](docs/2_technical_architecture_tr.md) | [→](docs/2_technical_architecture.md) |
| 3 | Uygulama Planı (sprint'ler + komutlar) | [→](docs/3_implementation_plan_tr.md) | [→](docs/3_implementation_plan.md) |
| 4 | Repo Yapısı | [→](docs/4_repo_structure_tr.md) | [→](docs/4_repo_structure.md) |
| 5 | Geliştirici Kurulumu | [→](docs/5_dev_setup_tr.md) | [→](docs/5_dev_setup.md) |
| 6 | Prompt Tasarımı | [→](docs/6_prompt_design_tr.md) | [→](docs/6_prompt_design.md) |
| — | **Geliştirme Durumu** (canlı) | [→](docs/progress/01_current_state_tr.md) | [→](docs/progress/01_current_state.md) |

## Teknoloji yığını (özet)

- **Runtime:** Python 3.12 · `uv` ≥ 0.5
- **Agent:** `strands-agents` + `strands-agents-tools` (worker Lambda'da, Claude Haiku 4.5)
- **LLM (worker):** `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Tool'lar:** `use_traffics`, `calculator`, `slack`, `journal`
- **Scheduler:** Amazon EventBridge `cron(0 2 * * ? *)` Europe/Berlin
- **Queue:** Amazon SQS standard + DLQ
- **Orchestration:** AWS Step Functions (reserve → release → confirm saga)
- **State:** Amazon Aurora PostgreSQL Serverless v2 (`yield_events`)
- **HITL:** Slack Block Kit + API Gateway webhook (LLM'siz modify Lambda)
- **Dashboard:** Amazon QuickSight + haftalık SES PDF
- **IaC:** AWS CDK (TypeScript) ≥ 2.150
- **Bölge:** `eu-central-1`

## Hızlı başlangıç

```bash
cd margin-optimizer
uv sync
cp .env.example .env                  # düzenle: DRY_RUN=true (dev), Slack token, Traffics key

# 5 mock PNR üret + worker'ı dry-run'da lokal çalıştır
uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
uv run python -m margin_optimizer.worker --from-file /tmp/mock_pnrs.jsonl --dry-run
```

Detay: [Geliştirici kurulumu](docs/5_dev_setup_tr.md) · [Güncel durum](docs/progress/01_current_state_tr.md).

## Mimari (yüksek seviye)

```mermaid
graph TD
    Cron[EventBridge cron 02:00 EU/Berlin] --> Ingest[Lambda: mo-ingest]
    Ingest --> SQS[SQS: mo-pnr-queue]
    SQS --> Worker[Lambda: mo-worker Claude Haiku]
    Worker <--> Traf[strands-traffics /alternative_flights]
    Worker <--> Calc[calculator]
    Worker -->|interaktif blok| Slack[#yield-ops]
    Slack -->|Approve| APIGW[API Gateway]
    APIGW --> Modify[Lambda: mo-modify LLM'siz]
    Modify --> SF[Step Functions saga]
    SF <-->|PATCH /bookings/{id}| Traf
    Modify --> YE[(Aurora yield_events)]
    YE --> QS[QuickSight + haftalık PDF]
```

Tam mimari: [docs/2_technical_architecture_tr.md](docs/2_technical_architecture_tr.md).

## Hedef KPI'lar (MVP)

| Metrik | 3. ay hedefi |
|---|---|
| Gecelik PNR kapsamı | ≥ %95 |
| Kârlı hit oranı (profitable / scanned) | ≥ %2 |
| İnsan onay oranı | ≥ %70 |
| Mutasyon hatası | < %0.5 |
| Aylık kurtarılan marj (tek acente, 10k PNR) | ≥ 8.000 € |
| Taranan PNR başı maliyet | ≤ 0.005 € |

## Güvenlik notları

- Saga pattern + HITL onay → tek bir yetkisiz müşteri-görünür uçuş değişikliği olmaz.
- Modify Lambda'da Slack HMAC doğrulama + 5 dk timestamp skew.
- `DRY_RUN=true` yeni ortamlarda default — staging canary yeşile dönmeden prod'a `false` atılmaz.
- Tüm secret'lar AWS Secrets Manager'da; 90 günlük rotation.

---

<a id="english"></a>

## English

**Current status:** Sprint 0 complete, Sprint 1 partial — the worker agent scaffold, Pydantic schemas, filter predicates, and dry-run CLI are in place; tests, the real ingest Lambda, and the Slack/saga/infra path are next. See **[docs/progress/01_current_state.md](docs/progress/01_current_state.md)** for the live state.

MarginOptimizer is a B2B headless yield-management engine for travel agencies. It nightly scans every active Pauschal booking that hasn't departed, searches Traffics `/offers/{code}/alternativeFlights` for cheaper equivalent flights (same baggage, ±3h schedule, ≤ 4h layover, same class tier), computes the margin delta deterministically via `strands_tools.calculator`, and — only after a human approval in Slack — mutates the booking via a Step Functions saga that calls Traffics `PATCH /bookings/{id}` with full rollback. Successful mutations land in an Aurora Postgres `yield_events` table feeding a QuickSight dashboard and a Monday 08:00 CET SES PDF.

See the docs table above for the full set of bilingual specs, all of which are at a ready-for-implementation state.
