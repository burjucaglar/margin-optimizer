---
marp: true
theme: dark
paginate: true
---

# MarginOptimizer
## B2B Dinamik Alternatif Uçuş & Gelir Yönetimi Sistemi
### Strands Agent Destekli Otonom PNR Tarayıcı

<figure class="cover-mark">
<svg viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="coverGradTr" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#f59e0b" stop-opacity="0.25"/>
      <stop offset="1" stop-color="#f59e0b" stop-opacity="1"/>
    </linearGradient>
  </defs>
  <rect x="10"  y="100" width="30" height="26"  fill="#1f2933"/>
  <rect x="50"  y="80"  width="30" height="46"  fill="#475569"/>
  <rect x="90"  y="55"  width="30" height="71"  fill="#60a5fa" fill-opacity="0.55"/>
  <rect x="130" y="22"  width="30" height="104" fill="url(#coverGradTr)"/>
  <path d="M 15 110 L 160 20" stroke="#f59e0b" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <circle cx="160" cy="20" r="4"  fill="#f59e0b"/>
  <circle cx="160" cy="20" r="10" fill="#f59e0b" fill-opacity="0.25"/>
  <text x="10" y="138" fill="#475569" font-size="6.5" letter-spacing="2" font-family="Inter">MARJ TRENDİ · GERİ KAZANIM</text>
</svg>
</figure>

---
**Öne Çıkan Metrikler**
- **$5.2 Milyar** | Global Dinamik Fiyatlandırma Pazarı
- **10K+** | Gecelik Rezervasyon (PNR) Tarama Kapasitesi
- **+%1-5** | Satılmış Tur Başına Net Karda Marjinal Artış
- **%100** | İnsan Onaylı Döngü (Güvenlik Önceliği)

---

# İ Ç İ N D E K İ L E R
**Bu Sunumda Neler Var?**

**01 | Maliyet Fırsatı (Kar Boşluğu)**
Bekleyen biletlerin içinden gizli kar oranlarını çekip çıkarmak.
**02 | Çözüm Yaşam Döngüsü**
Otonom ajanın gece 02:00'de (Europe/Berlin) aktifleşip yaptığı tarama operasyonu.
**03 | Altyapı & Ölçek**
10.000 bileti Traffics API'yi çökertmeden Amazon SQS ile kuyruklamak.
**04 | İnsan Onay Döngüsü (HITL)**
Slack etkileşimleri ve acente tarafında hiçbir hataya yer bırakmayan güvenlik duvarı.
**05 | Geliştirme Yol Haritası**
Lokal testlerden Amazon QuickSight analiz panolarına uzanan takvim.

---

# M A L İ Y E T  F I R S A T I
**Verimsizlikten Para Yaratmak**

**Senaryo:** Bugün satılan bir paket turun seferine 3 ay vardır. Uçağın bugünkü alış maliyeti 1.000 €'dur. 2. ayda rakip havayolu veya aynı hava yolu, tıpatıp aynı saatte, aynı valiz hakkıyla uçağı talepten dolayı 800 €'ya düşürebilir. İnsan eliyle her gece 10.000 PNR tek tek taranamayacağı için bu fırsatlar masada kalır.

<figure class="chart chart-price">
<svg viewBox="0 0 560 170" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="145" x2="520" y2="145" stroke="#1f2933" stroke-width="1"/>
  <rect x="90"  y="25" width="100" height="120" fill="#475569"/>
  <text x="140" y="18"  text-anchor="middle" fill="#cbd5e1" font-size="18" font-family="Inter">€1.000</text>
  <text x="140" y="160" text-anchor="middle" fill="#94a3b8" font-size="9"  letter-spacing="1.5" font-family="Inter">BAŞLANGIÇ FİYATI</text>
  <rect x="240" y="55" width="100" height="90" fill="#60a5fa"/>
  <text x="290" y="48"  text-anchor="middle" fill="#e6edf3" font-size="18" font-family="Inter">€800</text>
  <text x="290" y="160" text-anchor="middle" fill="#94a3b8" font-size="9"  letter-spacing="1.5" font-family="Inter">ALTERNATİF</text>
  <path d="M 360 55 L 400 55 L 400 145 L 360 145" stroke="#f59e0b" stroke-width="1.2" fill="none"/>
  <text x="470" y="95"  text-anchor="middle" fill="#f59e0b" font-size="32" font-weight="700" font-family="Inter">€200</text>
  <text x="470" y="115" text-anchor="middle" fill="#f59e0b" font-size="9"  letter-spacing="2.5" font-family="Inter">KAZANILDI</text>
  <text x="470" y="130" text-anchor="middle" fill="#94a3b8" font-size="8"  letter-spacing="1"   font-family="Inter">bilet başına</text>
</svg>
</figure>

**Yatırım Getirisi (ROI):** Yılda ~50.000 bilet × %2 kar-yakalama oranı × 40 €'luk ortalama tasarruf = yılda **≥ 40.000 €** saf geri kazanılmış marj.

---

# S İ S T E M  M İ M A R İ S İ
**AWS Serverless: Yüksek Hacimli İşlem Motoru**

<figure class="diagram diagram-arch">
<svg viewBox="0 0 720 90" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrTR" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#475569"/>
    </marker>
  </defs>
  <rect x="4"   y="25" width="108" height="38" rx="3" fill="#141a22" stroke="#f59e0b"/>
  <text x="58"  y="42" text-anchor="middle" fill="#f59e0b" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">EVENTBRIDGE</text>
  <text x="58"  y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">02:00 cron</text>
  <line x1="115" y1="44" x2="143" y2="44" stroke="#475569" stroke-width="1.4" marker-end="url(#arrTR)"/>
  <rect x="146" y="25" width="108" height="38" rx="3" fill="#141a22" stroke="#60a5fa"/>
  <text x="200" y="42" text-anchor="middle" fill="#60a5fa" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">SQS + DLQ</text>
  <text x="200" y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">10k PNR kuyrukta</text>
  <line x1="257" y1="44" x2="285" y2="44" stroke="#475569" stroke-width="1.4" marker-end="url(#arrTR)"/>
  <rect x="288" y="25" width="126" height="38" rx="3" fill="#141a22" stroke="#f59e0b"/>
  <text x="351" y="42" text-anchor="middle" fill="#f59e0b" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">LAMBDA WORKER</text>
  <text x="351" y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">Strands · Haiku 4.5</text>
  <line x1="417" y1="36" x2="450" y2="16" stroke="#475569" stroke-width="1.4" marker-end="url(#arrTR)"/>
  <line x1="417" y1="52" x2="450" y2="72" stroke="#475569" stroke-width="1.4" marker-end="url(#arrTR)"/>
  <rect x="454" y="2"  width="120" height="26" rx="3" fill="#141a22" stroke="#60a5fa"/>
  <text x="514" y="14" text-anchor="middle" fill="#60a5fa" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">SLACK HITL</text>
  <text x="514" y="23" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">API Gateway · HMAC</text>
  <rect x="454" y="60" width="120" height="26" rx="3" fill="#141a22" stroke="#84cc16"/>
  <text x="514" y="72" text-anchor="middle" fill="#84cc16" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">AURORA PG</text>
  <text x="514" y="81" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">yield_events</text>
  <line x1="577" y1="73" x2="605" y2="73" stroke="#475569" stroke-width="1.4" marker-end="url(#arrTR)"/>
  <rect x="608" y="60" width="108" height="26" rx="3" fill="#141a22" stroke="#84cc16"/>
  <text x="662" y="72" text-anchor="middle" fill="#84cc16" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">QUICKSIGHT</text>
  <text x="662" y="81" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">C-level panoları</text>
</svg>
</figure>

| **Servis** | **Mimarideki Görevi** |
| :--- | :--- |
| **AWS EventBridge** | Her gece 02:00'de (Europe/Berlin) sistemi uyandıran cron |
| **Amazon SQS** | 10.000 PNR'i DLQ ile Traffics API'yi boğmadan sıraya sokan kuyruk |
| **Lambda (Worker)** | Kuyruktan aldığı her PNR için Strands + Haiku 4.5 ajanı çalıştıran ünite |
| **API Gateway** | Slack'ten gelen "Onayla" webhook'unu HMAC doğrulamasıyla karşılayan port |
| **Aurora Postgres** | `yield_events` tablosuna her onaylı marjı yazar, QuickSight besler |

---

# S T R A N D S  A R A Ç L A R I
**Marj Avcıları**

- **`use_traffics`** ▸ `/offers/{code}/alternativeFlights`
  - Ana Traffics omurgasına tıpatıp aynı özellikli daha ucuz bir alternatif var mı sinyali çakar.
- **`calculator_tool`** ▸ deterministik (Yeni − Eski) fark
  - LLM'in halüsinasyon görüp yanlış matematik yapmasını engeller — aritmetik asla modelden gelmez.
- **`slack_tool`** ▸ operasyon kanalı `#yield-ops`
  - Ekibe ciro farkını (Kâr'ı) ve ONAYLA/REDDET butonlarını fırlatır.

---

# O N A Y  D Ö N G Ü S Ü
**Sıfır İstenmeyen Hata Riski**

<figure class="flow flow-approval">
<svg viewBox="0 0 720 100" xmlns="http://www.w3.org/2000/svg">
  <line x1="50" y1="40" x2="670" y2="40" stroke="#1f2933" stroke-width="2"/>
  <circle cx="50"  cy="40" r="22" fill="#141a22" stroke="#f59e0b" stroke-width="2"/>
  <text x="50"  y="46" text-anchor="middle" fill="#f59e0b" font-size="16" font-weight="700" font-family="Inter">1</text>
  <text x="50"  y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">TESPİT</text>
  <text x="50"  y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">€80 fark</text>
  <circle cx="205" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="205" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">2</text>
  <text x="205" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">BİLDİRİM</text>
  <text x="205" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">Slack bloklar</text>
  <circle cx="360" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="360" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">3</text>
  <text x="360" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">ONAY</text>
  <text x="360" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">operatör klik</text>
  <circle cx="515" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="515" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">4</text>
  <text x="515" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">WEBHOOK</text>
  <text x="515" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">HMAC · LLM bypass</text>
  <circle cx="670" cy="40" r="22" fill="#141a22" stroke="#84cc16" stroke-width="2"/>
  <text x="670" y="46" text-anchor="middle" fill="#84cc16" font-size="16" font-weight="700" font-family="Inter">5</text>
  <text x="670" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">DEĞİŞİM</text>
  <text x="670" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">/bookings/modify</text>
</svg>
</figure>

Sistem 2. adıma kadar tamamen otonomdur. 4. adımda Webhook **LLM'i tamamen bypass eder** — prodüksiyon biletine sadece deterministik kod dokunur. Tek giriş, tek çıkış, tek güvenli yol.

---

# Y A T I R I M  &  Y O L  H A R İ T A S İ
**Uygulama Stratejisi**

<figure class="chart chart-timeline">
<svg viewBox="0 0 720 155" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="130" x2="700" y2="130" stroke="#1f2933"/>
  <text x="40"  y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">A0</text>
  <text x="205" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">A1</text>
  <text x="370" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">A2</text>
  <text x="535" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">A3</text>
  <text x="700" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" text-anchor="end" font-family="Inter">A4+</text>
  <rect x="40"  y="15"  width="165" height="22" fill="#60a5fa" fill-opacity="0.85"/>
  <text x="50"  y="30" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">01 · DOĞRULAMA</text>
  <rect x="205" y="45"  width="165" height="22" fill="#60a5fa" fill-opacity="0.55"/>
  <text x="215" y="60" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">02 · BULUT KUYRUK</text>
  <rect x="370" y="75"  width="165" height="22" fill="#f59e0b" fill-opacity="0.85"/>
  <text x="380" y="90" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">03 · OPERASYON</text>
  <rect x="535" y="105" width="165" height="22" fill="#84cc16" fill-opacity="0.85"/>
  <text x="545" y="120" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">04 · BIG DATA · QUICKSIGHT</text>
</svg>
</figure>

**01 · Doğrulama (0-1 Ay)** — Ajan lokalde sahte PNR'lar ile doğru "Kar" hesabını matematiksel olarak yaptığı kanıtlanır.
**02 · Bulut Kuyruklama (1-2 Ay)** — Amazon SQS aktif. Rate-limit davranışı 429'lara göre ayarlanır.
**03 · Operasyonel İletişim (2-3 Ay)** — Slack webhook butonları + Traffics bilet değiştirme uçları.
**04 · Big Data Raporları (4+ Ay)** — Amazon QuickSight "Yield Dashboard" C-level panosu.

---

# MarginOptimizer
**Otonom, Görünmez, Son Derece Karlı**

Gizli & Özel 
B2B Gelir Optimizasyonu Sistemi
