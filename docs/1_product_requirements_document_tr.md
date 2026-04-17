# Ürün Gereksinim Dokümanı (PRD): MarginOptimizer

> **Durum:** Geliştirmeye hazır · **Sahip:** Hashtag World · **Son güncelleme:** 2026-04-17

## 1. Yönetici Özeti

MarginOptimizer, seyahat acenteleri için arka planda koşan (headless) bir B2B Yield Management motorudur. Strands Agents (Bedrock Claude **Haiku**) + `strands-traffics` üzerine inşa edilmiştir; her gece henüz uçulmamış aktif Pauschal rezervasyonları tarar, Traffics `/offers/{code}/alternativeFlights` ile aynı bagaj kurallarına ve ±3 saat uçuş penceresine sahip daha ucuz alternatifleri bulur, marj deltasını deterministik `calculator` tool'u ile hesaplar ve — **yalnızca Slack üzerinden insan onayı alındıktan sonra** — rezervasyonu Traffics `PATCH /bookings/{id}` ile mutate eder. Sonuç: satılmış turlarda kurtarılmış marj; yönetim bunu Amazon QuickSight "Yield Recovered" panosundan takip eder.

## 2. Problem Tanımı

Bir acente Pauschal paketi sattığında uçuş maliyeti satış anında sabitlenir. Uçuştan önceki aylarda rakip havayolları daha ucuz eşdeğer uçuşlar yayınlar — ama acentede gece başına 10.000 PNR manuel tarayacak iş gücü yoktur. Sonuç: rezerve edilebilir marjın %1–3'ü masada kalır. MarginOptimizer bu açığı otonom şekilde kapatır; müşteri güvenini korumak için her mutasyon insan onayından geçer.

## 3. Hedef Kitle ve Personalar

| Persona | Temel İhtiyaç | Tipik İfade |
|---|---|---|
| **Operasyon Müdürü** | Kadro büyütmeden rezervasyon başına uçuş maliyetini düşür | "Elimde 8.000 aktif PNR var, manuel tarayacak kadrom yok." |
| **Revenue / Yield Manager** | Kurtarılan marja görünürlük + güvenli çalışma | "Her gece ne kadar kar yakaladığımızı dashboard'da görmek istiyorum — ama müşterinin uçuşu haberim olmadan değişmesin." |
| **Rezervasyon Temsilcisi** | Excel değil net bir onay/ret tuşu | "Slack'te zaten kanalımız var, yeni bir sisteme girmek istemem." |

## 4. Kullanıcı Hikayeleri ve Kabul Kriterleri

### US-1 — Gece PNR taraması
> Operasyon olarak her gece aktif tüm Pauschal PNR'ların otomatik taranmasını istiyorum.

**Kabul kriterleri:**
- [ ] Her gün `02:00 Europe/Berlin`'de EventBridge ingestion Lambda'yı tetikler.
- [ ] Ingestion Lambda acentenin rezervasyon deposundan (Postgres/DynamoDB) okur, `status = CONFIRMED` ve `departure_date > now()` filtrelerini uygular, her rezervasyon için SQS mesajı üretir.
- [ ] 3 saatlik gece penceresinde ≥ 10.000 rezervasyon sıraya alınır, DLQ taşmaz.

### US-2 — Alternatif uçuş tespiti
> Ajan olarak Traffics'ten alternatifleri çağırıp eşdeğer olmayanları elemek istiyorum.

**Kabul kriterleri:**
- [ ] Her SQS mesajı için worker Lambda `use_traffics(service="offers", endpoint="alternative_flights", params='{"code": "<offerCode>"}')` çağırır.
- [ ] Ajan şu alternatifleri eler: (a) bagaj kurallarını değiştirenler, (b) kalkış/varış saatini > 3 saat kaydıranlar, (c) > 4 saat aktarma ekleyenler, (d) booking class tier'ı değiştirenler.
- [ ] HTTP 429 yanıtları `strands-traffics`'in yerleşik Retry adapter'ı ile yeniden denenir; kalıcı hatalar CloudWatch metriği üretir.

### US-3 — Deterministik marj hesaplama
> Onay veren olarak tam euro cinsinden tasarruf görmek istiyorum, LLM tahmini değil.

**Kabul kriterleri:**
- [ ] Tüm delta hesapları `strands_tools.calculator` (SymPy) ile yapılır, asla LLM tarafından doğrudan değil.
- [ ] Sadece `new_price < old_price - MIN_MARGIN_EUR` (varsayılan 30 €) olan alternatifler yüzeye çıkar.
- [ ] Slack kartı gösterir: eski fiyat, yeni fiyat, mutlak delta, yüzde delta.

### US-4 — İnsan onay döngüsü (HITL)
> Rezervasyon temsilcisi olarak değişiklikleri Slack'te tek tıkla onaylamak/reddetmek istiyorum.

**Kabul kriterleri:**
- [ ] Karlı alternatif bulunduğunda ajan `slack(action="chat.postMessage", parameters={"blocks": [...interactive...]})` ile ops kanalına mesaj atar.
- [ ] Mesaj şunları içerir: booking ID, müşteri baş harfleri, eski/yeni uçuş detayları, delta, "Onayla" / "Reddet" tuşları.
- [ ] Tuş tıklandığında API Gateway endpoint → modification Lambda deterministik şekilde Traffics `PATCH /bookings/{id}` çalıştırır (kritik yolda LLM yok).
- [ ] Idempotency: tamamlanmış bir biletin Onay tuşuna tekrar basılması no-op'tur.

### US-5 — Mutasyon başarısızlığında rollback
> Operasyon olarak başarısız bir bilet değişiminde orijinal rezervasyonun etkilenmemesini istiyorum.

**Kabul kriterleri:**
- [ ] Modification Lambda Step Functions saga'sı kullanır: `yeni uçuşu rezerve et` → `eskisini bırak` → `onayla`.
- [ ] Herhangi bir adım hatası, kompanse edici eylemleri tetikler ve orijinal rezervasyonu dokunulmamış bırakır.
- [ ] Başarısız girişimler `strands_tools.journal` ile günlüğe alınır, ops kanalına kırmızı bayrakla düşer.

### US-6 — Yönetim dashboard'u
> Revenue manager olarak haftalık kurtarılan marj görünümü istiyorum.

**Kabul kriterleri:**
- [ ] Her başarılı mutasyon `yield_events` tablosuna (Postgres/Aurora) bir satır yazar.
- [ ] QuickSight panosu her saat güncellenir: gün/hafta/ay bazında toplam kurtarılan euro, hit rate (karlı / taranan), delta'ya göre top 5 route-pair.
- [ ] Her pazartesi 08:00 CET SES üzerinden haftalık PDF rapor e-postalanır.

## 5. Fonksiyonel Gereksinimler

### FR-1. Zamanlama
AWS EventBridge cron `cron(0 2 * * ? *)` (timezone config ile Europe/Berlin) → Lambda `ingest_bookings`.

### FR-2. Kuyruk
- Amazon SQS standart kuyruk, visibility timeout = 6 × Lambda timeout.
- 3 receive denemesi sonrası DLQ.
- Worker Lambda reserved concurrency: başlangıç **10** (~5 Traffics TPS); tune edilir.

### FR-3. Agent Worker
- Model: Bedrock **Claude Haiku** (`us.anthropic.claude-haiku-4-5-20251001-v1:0`) — parse işleri için hızlı + ucuz.
- Tool'lar: `use_traffics`, `calculator`, `slack`, `journal`, `use_aws`.
- System prompt şunu zorlar: (a) `DRY_RUN=true` modunda dry-run; (b) insan onayı olmadan mutasyon reddi; (c) karlı alternatif yoksa "Task Complete. No action needed." çıktısı.

### FR-4. Mutasyon Yolu (LLM-siz)
Slack interactive webhook tarafından tetiklenen ayrı Lambda:
1. Slack HMAC imzasını doğrula.
2. Lokal DB'den rezervasyonu bul.
3. `strands_tools.use_aws` sadece S3 loglama için; mutasyon için DEĞİL.
4. Traffics `PATCH /bookings/{id}` doğrudan `requests` ile (idempotency key = `<booking_id>:<yeni_offerCode>`).
5. `yield_events` satırı yaz; Slack'i ack'le.

### FR-5. Gözlemlenebilirlik
- `BeforeToolCallEvent` / `AfterToolCallEvent` hook'ları her `use_traffics` çağrısını CloudWatch Logs Insights-sorgulanabilir JSON olarak loglar.
- Özel CloudWatch metrikleri: `ScannedPnrs`, `ProfitableAlternativesFound`, `ApprovedChanges`, `RejectedChanges`, `MutationFailures`.

## 6. Fonksiyonel Olmayan Gereksinimler

| Kategori | Hedef |
|---|---|
| **Throughput** | 3 saatlik gece penceresinde ≤ 10.000 PNR |
| **Traffics TPS** | ≤ 5 TPS (rate-limit'e payla uyum) |
| **Mutasyon gecikmesi** | Onay tıklaması → Traffics PATCH başarılı < 4 s (p95) |
| **Hata toleransı** | Sıfır yarı-mutate rezervasyon (saga rollback) |
| **Maliyet tavanı** | Taranan PNR başı ≤ 0.005 € |
| **Bölge** | `eu-central-1` |
| **Güvenlik** | Slack HMAC doğrulama; Traffics API key Secrets Manager'da; Lambda bazlı least-privilege IAM |

## 7. Kapsam Dışı (MVP)

- Otel fiyat optimizasyonu (MVP'de yalnızca uçuş swap).
- Multi-tenant SaaS — ilk deploy tek acente.
- Müşteriye swap bildirimi (acentenin mevcut CRM'i hallediyor).
- Tahminsel ("gelecek hafta fiyat düşer mi?") — MVP'de sadece reaktif tarama.
- Pauschal dışı ürünler.

## 8. Başarı Metrikleri (KPI'lar)

| Metrik | Hedef (Launch + 3 ay) | Hedef (Launch + 6 ay) |
|---|---|---|
| Gece PNR kapsaması | ≥ %95 aktif PNR taranır | ≥ %99 |
| Hit rate (karlı / taranan) | ≥ %2 | ≥ %4 |
| Onay oranı | ≥ %70 | ≥ %85 |
| Mutasyon hata oranı | < %0.5 | < %0.1 |
| Aylık kurtarılan marj (tek acente, 10k PNR) | ≥ 8.000 € | ≥ 25.000 € |
| Taranan PNR başı maliyet | ≤ 0.005 € | ≤ 0.003 € |

## 9. Test Stratejisi

- **Birim:** `pytest` — marj mantığı, rollback saga, HMAC doğrulama.
- **Entegrasyon:** `responses` ile mock Traffics — 429 yolu ve `/bookings` PATCH yolu dahil.
- **LLM evals:** 50 alternatif-uçuş senaryoluk altın set. Ajan yalnızca eşik üstü marjları yüzeye çıkarmalı, diğerlerinde sessiz kalmalı. Evals'da sıfır yanlış-pozitif mutasyon girişimi release-blocker'dır.
- **Dry-run modu:** `DRY_RUN=true` env değişkeni gerçek PATCH'i atlar; staging'de kullanılır.
- **Chaos testi:** Simüle Traffics 429 fırtınası (%25 hata oranı) — throughput kademeli düşmeli, crash olmamalı.
- **Güvenlik:** Slack signature doğrulama test suite'i; CI'da IAM policy simulator.

## 10. Bağımlılıklar ve Riskler

| Risk | Azaltma |
|---|---|
| Traffics 429 kaskadı | SQS throttle + exponential backoff + circuit breaker metriği |
| Yanlışlıkla müşteri-görünür uçuş değişimi | Saga pattern + HITL Slack onayı + yeni env'lerde `DRY_RUN=true` varsayılan |
| Slack kesintisi onayları bloklar | Fallback: SES ile günlük bekleyen onay özeti e-postası |
| LLM marj halüsinasyonu | Marj **asla** LLM ile değil; daima `calculator` tool'u ile |
| Acente DB'si ile lokal cache arası drift | Günlük reconciliation job; delta > %2'de alarm |
| Traffics API key sızıntısı | Secrets Manager rotation (90 gün); her env'de ayrı key |

## 11. Açık Sorular

- **Q1:** Acentenin rezervasyon deposuna erişim? Doğrudan DB replica, günlük dump ya da API? (Varsayım: şimdilik günlük S3 export; 2. ay'da replica'ya taşı.)
- **Q2:** Minimum marj eşiği (MIN_MARGIN_EUR)? (Varsayım: 30 €; acente bazlı yapılandırılabilir.)
- **Q3:** Gece run'u tamamen başarısız olursa kim uyanır? (Varsayım: PagerDuty entegrasyonunda on-call rotation — Sprint 4'te tanımla.)
