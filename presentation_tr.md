---
marp: true
theme: dark
paginate: true
---

# MarginOptimizer
## B2B Dinamik Alternatif Uçuş & Gelir Yönetimi Sistemi
### Strands Agent Destekli Otonom PNR Tarayıcı

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

**Senaryo:** Bugün satılan bir paket turun seferine 3 ay vardır. Uçağın bugünkü alış maliyeti 1.000 €'dur.
**Fırsat:** 2. ayda, rakip bir havayolu veya aynı hava yolu, tıpatıp aynı saatte, aynı valiz hakkındaki uçağı talepten dolayı 800 €'ya düşürebilir. İnsan eliyle her gece 10.000 PNR tek tek taranamayacağı için bu fırsatlar masada kalır.
**Çözüm:** MarginOptimizer bu devasa aramayı saatte bir Haiku-worker ile otonom yapar.

**Yatırım Getirisi (ROI):**
Yılda satılan ~50.000 biletin %2'sinde 40 €'luk alternatif bulunması = yılda **≥ 40.000 €** saf geri kazanılmış marj.

---

# S İ S T E M  M İ M A R İ S İ
**AWS Serverless: Yüksek Hacimli İşlem Motoru**

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

- **`use_traffics`**
  - **Hedef:** `/offers/{code}/alternativeFlights`
  - **Görev:** Ana Traffics omurgasına tıpatıp aynı özellikli daha ucuz bir alternatif var mı sinyali çakar.
- **`calculator_tool`**
  - **Görev:** Net ve kesin olarak Eski Fiyat - Yeni Fiyat (Delta) formülünü uygular.
  - **Önem:** LLM (Bedrock) modellerinin halüsinasyon görüp yanlış matematik hesabı yapmasını engeller. 
- **`slack_tool`**
  - **Hedef:** Acente ofisinin Slack / Teams operasyon kanalı.
  - **Görev:** Ekibe bulunan ciro farkını (Kar'ı) ve ONAYLA/REDDET butonlarını fırlatır.

---

# O N A Y  D Ö N G Ü S Ü
**Sıfır İstenmeyen Hata Riski**

Sistem bir değişime karar verene dek %100 otonom çalışır. İşlem kısmında insan devreye girer:
1. AI, ID:4410 numaralı bilette 80 €'luk kar bulur.
2. Slack'e mesaj atar: *"Uçuşu SunExpress ile revize edip 80 € ekstra kazanalım mı?"*
3. Operatör **[ONAYLA]** butonuna basar.
4. Çıkan Webhook, zekayı (LLM) bypass eder ve sıfır riskle Traffics `/bookings/modify` komutunu işletir.
5. Mutlak finansal güvenle bilet değiştirilir.

---

# Y A T I R I M  &  Y O L  H A R İ T A S İ
**Uygulama Stratejisi**

**Faz 1: Zeka Doğrulaması (0-1 Ay)**
Ajanın lokalde sahte PNR'lar ile doğru "Kar" hesabını matematiksel olarak yaptığı kanıtlanır.
**Faz 2: Bulut Kuyruklama (1-2 Ay)**
Amazon SQS aktif edilir. Ajanın otonom olarak (Rate-Limitleri de düşünerek) paralel uçuş taraması testi yapılır.
**Faz 3: Operasyonel İletişim (2-3 Ay)**
Slack webhook butonlarının ve Traffics Booking Modification (bilet değiştirme) uçlarının programlanması.
**Faz 4: Big Data Raporları (4+ Ay)**
Acenteye aylık ne kadar para kazandırıldığını patronlara gösteren Amazon QuickSight pano arayüzü kurulur.

---

# MarginOptimizer
**Otonom, Görünmez, Son Derece Karlı**

Gizli & Özel 
B2B Gelir Optimizasyonu Sistemi
