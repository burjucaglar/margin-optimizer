# Geliştirme Durumu: MarginOptimizer

> **Son güncelleme:** 2026-04-17 · **Branch:** main · **Faz:** Sprint 0 tamam, Sprint 1 kısmi

Bu doküman repo'nun somut durumunu takip eder — spec'lerin olması gerektiğini söylediği değil, bugün gerçekten çalışan şeyleri.

## 1. Tamamlananlar

### Repo iskelesi
- `pyproject.toml` — tüm bağımlılıklar pin'li; worker CLI için `click` + `rich` + `python-dotenv` main dep'lere yükseltildi; `strands-traffics` editable path'i `./strands-traffics` olarak düzeltildi
- `.gitignore` — Python + uv + CDK standart dışlamaları
- `.env.example` — tüm runtime değişkenleri dokümante (tasarım fazından değişmedi)

### Kaynak — `src/margin_optimizer/`

| Dosya | Durum | İçerik |
|---|---|---|
| `__init__.py` | ✅ | Paket sürümü (`0.1.0`) |
| `prompts.py` | ✅ v1 | `WORKER_SYSTEM_PROMPT` (persona, sert kurallar, kanonik tool sırası, terminal string sözleşmesi, default-sessizlik) + `PROMPT_VERSION = "v1"` |
| `schemas.py` | ✅ | `SqsPayload` ve `YieldEvent` Pydantic modelleri. Constrained string tipleri (`_OfferCode`, `_BookingId`, `_SafeStr`) prompt-injection payload'larını şema sınırında reddeder. |
| `filters.py` | ✅ | Saf fonksiyonlar: `is_baggage_equivalent`, `within_schedule_window`, `layover_acceptable`, `same_class_tier`, `passes_all`. Eşikler env'den çağrı anında okunur. |
| `hooks.py` | 🟡 stub | `AuditHooks` üç yaşam döngüsü callback'ini kaydeder ve her log satırını `prompt_version` ile damgalar. Tam CloudWatch EMF payload (`MoScannedPnrs` vb.) Sprint 2'de. |
| `worker.py` | ✅ | `build_worker_agent()` + `handler(event, context)` Lambda girişi + `main()` CLI (`click` + `rich`). `--dry-run` Bedrock'u atlar, sadece render edilmiş prompt'u yazar. |
| `ingest.py` | 🟡 stub | `handler()` + `main()` `mo-ingest` console script'ini çözer; gerçek S3 taraması Sprint 2'de. |

### Scriptler — `scripts/`
| Dosya | Durum | İçerik |
|---|---|---|
| `generate_mock_pnrs.py` | ✅ | `click` CLI — `SqsPayload`'a uyan `--count N` satır yazar `--out`'a. Seed'li RNG ile fixture'lar tekrar üretilebilir. |

### Henüz oluşturulmayanlar
`tests/`, `infra/`, `evals/`, `src/margin_optimizer/modify.py`, `src/margin_optimizer/slack_ui.py`, `src/margin_optimizer/slack_verify.py`, `src/margin_optimizer/db.py`, `src/margin_optimizer/secrets.py`, `src/margin_optimizer/weekly_report.py`, `src/margin_optimizer/saga/`.

### Bağımlılıklar
- `uv` kurulu
- `uv.lock` üretildi (check-in'li)
- `strands-traffics==0.1.0` nested `./strands-traffics` dizininden editable kuruldu
- `strands-agents==1.35.0`, `strands-agents-tools==0.4.1`, `boto3`, `pydantic`, `click`, `rich`, `python-dotenv`, `sqlalchemy`, `slack-sdk` vb. — `uv sync` temiz çalışır

### Lint & tip
- `uv run ruff check src scripts` → **All checks passed**
- `uv run mypy src` → **Success: no issues found in 7 source files**

## 2. Tamamlanmayanlar

| Alan | Detay | Hedef sprint |
|---|---|---|
| Testler | `tests/conftest.py`, `tests/test_worker.py`, `tests/test_margin.py`, `tests/test_filters.py`, `tests/fixtures/` | Sprint 0 kapanışı |
| Ingest | Gerçek S3 taraması + `SendMessageBatch` fan-out; `ScannedPnrs` metriği | Sprint 2 |
| Slack HITL | `slack_ui.build_approval_card`, `slack_verify.verify_slack_hmac`, `modify.handler` | Sprint 3 |
| Saga | `saga/{reserve,release,confirm,compensate,journal}.py`, `infra/`'de ASL JSON | Sprint 4 |
| DB | `db.py` (`get_engine`, `write_yield_event`), Alembic migration | Sprint 4 |
| Analitik | `weekly_report.py` SES PDF; QuickSight dataset | Sprint 5 |
| Golden set | `evals/golden_set_50.jsonl` + `scripts/run_evals.py` | Sprint 1 kapanışı |
| Infra | `infra/` CDK TypeScript stack | Sprint 0 kapanışı + Sprint 5'e kadar genişler |
| Docker | `Dockerfile.worker`, `Dockerfile.ingest` | Sprint 2 |
| Runbook | `docs/runbook.md` | Sprint 6 |

## 3. Nasıl kurulur

Sıfırdan bir dev makinede:

```bash
# 1. uv yoksa kur
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. deps sync (uv kendi Python 3.12'sini de indirir)
cd /path/to/margin-optimizer
uv sync

# 3. .env oluştur
cp .env.example .env
# .env'i düzenle — en az şunları doldur:
#   AWS_PROFILE=mo-dev
#   AWS_REGION=eu-central-1
#   TRAFFICS_API_KEY=...
#   SLACK_BOT_TOKEN=xoxb-...     (Slack path Sprint 3'te gelince gerekecek)
#   DRY_RUN=true                 (dev'de true bırak)
```

## 4. Nasıl çalıştırılır

### Mock PNR dosyası üret + worker'ı dry-run çalıştır
```bash
uv run python scripts/generate_mock_pnrs.py --count 5 --out /tmp/mock_pnrs.jsonl
uv run python -m margin_optimizer.worker --from-file /tmp/mock_pnrs.jsonl --dry-run
```

`--dry-run` (default) render edilmiş prompt'u Bedrock'u çağırmadan yazar. AWS credential + Bedrock erişimin olunca `--no-dry-run` ile gerçek agent'ı çalıştır.

### `mo-worker` / `mo-ingest` console scriptleri
`uv sync` her iki entry point'i `[project.scripts]`'ten kurar:
```bash
uv run mo-worker --from-file /tmp/mock_pnrs.jsonl --dry-run
uv run mo-ingest   # şu an no-op stub
```

### Import-only smoke (Bedrock gerekmez)
```bash
uv run python -c "from margin_optimizer.worker import build_worker_agent; print('OK')"
uv run python -c "from margin_optimizer.prompts import WORKER_SYSTEM_PROMPT, PROMPT_VERSION; print(PROMPT_VERSION, len(WORKER_SYSTEM_PROMPT), 'chars')"
```

### Lint + type-check + (yakında) testler
```bash
uv run ruff check src scripts
uv run mypy src
uv run pytest              # testler gelince
```

## 5. Bilinen eksikler ve uyarılar

- **Test yok.** Sprint 0'ın formal çıkış kriteri `uv run pytest` yeşili — henüz karşılanmadı. Bir placeholder test bile eklenmeli.
- **`hooks.py` sadece log atıyor.** Henüz CloudWatch EMF payload veya margin telemetri metriği yok.
- **`ingest.py` stub.** Koşulsuz olarak `{"enqueued": 0}` döner.
- **Gerçek çalıştırmalar AWS erişimi ister.** `.env`'de geçerli Bedrock erişimi ve Traffics key olmadan `--no-dry-run` ilk tool call'ta başarısız olur.
- **Host'ta Python 3.13 var.** `uv sync` kendi 3.12'sini indirir (`pyproject.toml`'da pin'li); system Python'ı karıştırma.
- **`infra/` yok.** CDK iskelesi Sprint 0'ın açık kalan diğer görevi.

## 6. Önerilen sonraki adımlar

1. **`tests/conftest.py` + `tests/test_filters.py`** — saf fonksiyon predicate'ler en ucuz unit testler; Sprint 0'ı kapamak için önce bunlar.
2. **`tests/test_worker.py`** — Traffics'i `responses` ile mock'la; dry-run path'in geçerli bir `SqsPayload` inşa edip beklenen prompt'u render ettiğini assert et.
3. **`evals/golden_set_50.jsonl` seed** — `docs/6_prompt_design.md` §6.1'deki mix'i kapsayan 5–10 senaryoyla başla.
4. **`scripts/run_evals.py`** — golden set'i `build_worker_agent()` üzerinden çalıştıran runner.
5. **CDK iskelesi** — `docs/4_repo_structure.md` §`infra/lib/` bölümündeki üç-stack iskeletiyle `infra/` dizini.

## 7. Dosya haritası (gerçekten var olanlar)

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
│       ├── 01_current_state.md
│       └── 01_current_state_tr.md           # bu dosya
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
└── strands-traffics/                          # nested tool paketi (editable)
    ├── pyproject.toml
    ├── strands_traffics/
    └── tests/
```

Henüz oluşturulmayanlar: `tests/`, `evals/`, `infra/`, `src/margin_optimizer/{modify,slack_ui,slack_verify,db,secrets,weekly_report}.py`, `src/margin_optimizer/saga/`.
