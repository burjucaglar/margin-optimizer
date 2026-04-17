---
marp: true
theme: dark
paginate: true
---

# MarginOptimizer
## B2B Dynamic Alternative Flight & Yield Management System
### Strands Agent Automated PNR Analysis

<figure class="cover-mark">
<svg viewBox="0 0 200 140" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="coverGrad" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="#f59e0b" stop-opacity="0.25"/>
      <stop offset="1" stop-color="#f59e0b" stop-opacity="1"/>
    </linearGradient>
  </defs>
  <rect x="10"  y="100" width="30" height="26"  fill="#1f2933"/>
  <rect x="50"  y="80"  width="30" height="46"  fill="#475569"/>
  <rect x="90"  y="55"  width="30" height="71"  fill="#60a5fa" fill-opacity="0.55"/>
  <rect x="130" y="22"  width="30" height="104" fill="url(#coverGrad)"/>
  <path d="M 15 110 L 160 20" stroke="#f59e0b" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <circle cx="160" cy="20" r="4"  fill="#f59e0b"/>
  <circle cx="160" cy="20" r="10" fill="#f59e0b" fill-opacity="0.25"/>
  <text x="10" y="138" fill="#475569" font-size="6.5" letter-spacing="2" font-family="Inter">MARGIN TREND · RECOVERY</text>
</svg>
</figure>

---
**Key Metrics**
- **$5.2B** | Global Dynamic Pricing Tech Market
- **10K+** | Nightly PNR Scan Capacity
- **+1-5%** | Marginal Net Profit Increase Per Booking
- **100%** | Human-In-The-Loop Safety Record

---

# TABLE OF CONTENTS
**What This Document Covers**

<div class="toc">
<div class="toc-row"><div class="toc-num">01</div><div class="toc-body"><div class="toc-title">The Cost Factor</div><div class="toc-desc">Extracting invisible profit from waiting tickets.</div></div></div>
<div class="toc-row"><div class="toc-num">02</div><div class="toc-body"><div class="toc-title">The Solution Lifecycle</div><div class="toc-desc">How the autonomous agent operates at 02:00 (Europe/Berlin).</div></div></div>
<div class="toc-row"><div class="toc-num">03</div><div class="toc-body"><div class="toc-title">Infrastructure &amp; Scaling</div><div class="toc-desc">Processing thousands of items without triggering API bans (SQS).</div></div></div>
<div class="toc-row"><div class="toc-num">04</div><div class="toc-body"><div class="toc-title">The Approval Loop (HITL)</div><div class="toc-desc">Slack webhooks and operator-side security.</div></div></div>
<div class="toc-row"><div class="toc-num">05</div><div class="toc-body"><div class="toc-title">Development Roadmap</div><div class="toc-desc">From local validation to cloud dashboard deployment.</div></div></div>
</div>

---

# THE COST FACTOR
**Creating Money From Inefficiency**

**The Scenario:** A €1,000 flight is locked in at booking. Two months later an identical seat — same baggage, same time window — drops to €800. No human can scan 10,000 PNRs nightly, so that €200 margin slips away.

<figure class="chart chart-price">
<svg viewBox="0 0 560 170" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="145" x2="520" y2="145" stroke="#1f2933" stroke-width="1"/>
  <rect x="90"  y="25" width="100" height="120" fill="#475569"/>
  <text x="140" y="18"  text-anchor="middle" fill="#cbd5e1" font-size="18" font-family="Inter">€1,000</text>
  <text x="140" y="160" text-anchor="middle" fill="#94a3b8" font-size="9"  letter-spacing="1.5" font-family="Inter">LOCKED-IN FARE</text>
  <rect x="240" y="55" width="100" height="90" fill="#60a5fa"/>
  <text x="290" y="48"  text-anchor="middle" fill="#e6edf3" font-size="18" font-family="Inter">€800</text>
  <text x="290" y="160" text-anchor="middle" fill="#94a3b8" font-size="9"  letter-spacing="1.5" font-family="Inter">ALTERNATIVE</text>
  <path d="M 360 55 L 400 55 L 400 145 L 360 145" stroke="#f59e0b" stroke-width="1.2" fill="none"/>
  <text x="470" y="95"  text-anchor="middle" fill="#f59e0b" font-size="32" font-weight="700" font-family="Inter">€200</text>
  <text x="470" y="115" text-anchor="middle" fill="#f59e0b" font-size="9"  letter-spacing="2.5" font-family="Inter">RECOVERED</text>
  <text x="470" y="130" text-anchor="middle" fill="#94a3b8" font-size="8"  letter-spacing="1"   font-family="Inter">per booking</text>
</svg>
</figure>

**ROI:** ~50,000 yearly bookings × 2% profitable-hit rate × €40 average saving = **≥ €40,000 / year** in pure recovered margin.

---

# SYSTEM ARCHITECTURE
**AWS Serverless High-Throughput Engine**

<figure class="diagram diagram-arch">
<svg viewBox="0 0 720 90" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrEN" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#475569"/>
    </marker>
  </defs>
  <rect x="4"   y="25" width="108" height="38" rx="3" fill="#141a22" stroke="#f59e0b"/>
  <text x="58"  y="42" text-anchor="middle" fill="#f59e0b" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">EVENTBRIDGE</text>
  <text x="58"  y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">02:00 cron</text>
  <line x1="115" y1="44" x2="143" y2="44" stroke="#475569" stroke-width="1.4" marker-end="url(#arrEN)"/>
  <rect x="146" y="25" width="108" height="38" rx="3" fill="#141a22" stroke="#60a5fa"/>
  <text x="200" y="42" text-anchor="middle" fill="#60a5fa" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">SQS + DLQ</text>
  <text x="200" y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">10k PNRs queued</text>
  <line x1="257" y1="44" x2="285" y2="44" stroke="#475569" stroke-width="1.4" marker-end="url(#arrEN)"/>
  <rect x="288" y="25" width="126" height="38" rx="3" fill="#141a22" stroke="#f59e0b"/>
  <text x="351" y="42" text-anchor="middle" fill="#f59e0b" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">LAMBDA WORKER</text>
  <text x="351" y="54" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">Strands · Haiku 4.5</text>
  <line x1="417" y1="36" x2="450" y2="16" stroke="#475569" stroke-width="1.4" marker-end="url(#arrEN)"/>
  <line x1="417" y1="52" x2="450" y2="72" stroke="#475569" stroke-width="1.4" marker-end="url(#arrEN)"/>
  <rect x="454" y="2"  width="120" height="26" rx="3" fill="#141a22" stroke="#60a5fa"/>
  <text x="514" y="14" text-anchor="middle" fill="#60a5fa" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">SLACK HITL</text>
  <text x="514" y="23" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">API Gateway · HMAC</text>
  <rect x="454" y="60" width="120" height="26" rx="3" fill="#141a22" stroke="#84cc16"/>
  <text x="514" y="72" text-anchor="middle" fill="#84cc16" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">AURORA PG</text>
  <text x="514" y="81" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">yield_events</text>
  <line x1="577" y1="73" x2="605" y2="73" stroke="#475569" stroke-width="1.4" marker-end="url(#arrEN)"/>
  <rect x="608" y="60" width="108" height="26" rx="3" fill="#141a22" stroke="#84cc16"/>
  <text x="662" y="72" text-anchor="middle" fill="#84cc16" font-size="9.5" font-weight="600" letter-spacing="1" font-family="Inter">QUICKSIGHT</text>
  <text x="662" y="81" text-anchor="middle" fill="#94a3b8" font-size="7.5" font-family="Inter">C-level dashboards</text>
</svg>
</figure>

| **Service** | **Function in the Architecture** |
| :--- | :--- |
| **AWS EventBridge** | Nightly cron at 02:00 Europe/Berlin kicking the ingest Lambda |
| **Amazon SQS** | Queues 10,000 bookings with a DLQ, shielding Traffics from bursts |
| **Lambda (Worker)** | One Strands + Haiku 4.5 agent per PNR, max 10 concurrent |
| **API Gateway** | Receives Slack approval webhooks, HMAC-verified before routing |
| **Aurora Postgres** | Writes every approved swap to `yield_events`; feeds QuickSight |

---

# STRANDS TOOLING
**The Margin Finders**

- **`use_traffics`** ▸ `/offers/{code}/alternativeFlights`
  - Pings the Traffics spine to query identical alternative planes.
- **`calculator_tool`** ▸ deterministic (New − Old) delta
  - Prevents LLM mathematical hallucinations — arithmetic is never model-generated.
- **`slack_tool`** ▸ operations channel `#yield-ops`
  - Dispatches interactive UI blocks (Approve/Reject) showing the found margin.

---

# THE APPROVAL LOOP
**Zero Unwanted Actions**

<figure class="flow flow-approval">
<svg viewBox="0 0 720 100" xmlns="http://www.w3.org/2000/svg">
  <line x1="50" y1="40" x2="670" y2="40" stroke="#1f2933" stroke-width="2"/>
  <circle cx="50"  cy="40" r="22" fill="#141a22" stroke="#f59e0b" stroke-width="2"/>
  <text x="50"  y="46" text-anchor="middle" fill="#f59e0b" font-size="16" font-weight="700" font-family="Inter">1</text>
  <text x="50"  y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">DETECT</text>
  <text x="50"  y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">€80 delta</text>
  <circle cx="205" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="205" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">2</text>
  <text x="205" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">NOTIFY</text>
  <text x="205" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">Slack blocks</text>
  <circle cx="360" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="360" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">3</text>
  <text x="360" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">APPROVE</text>
  <text x="360" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">human click</text>
  <circle cx="515" cy="40" r="22" fill="#141a22" stroke="#60a5fa" stroke-width="2"/>
  <text x="515" y="46" text-anchor="middle" fill="#60a5fa" font-size="16" font-weight="700" font-family="Inter">4</text>
  <text x="515" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">WEBHOOK</text>
  <text x="515" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">HMAC · bypass LLM</text>
  <circle cx="670" cy="40" r="22" fill="#141a22" stroke="#84cc16" stroke-width="2"/>
  <text x="670" y="46" text-anchor="middle" fill="#84cc16" font-size="16" font-weight="700" font-family="Inter">5</text>
  <text x="670" y="82" text-anchor="middle" fill="#e6edf3" font-size="9"  letter-spacing="1.5" font-family="Inter">MUTATE</text>
  <text x="670" y="94" text-anchor="middle" fill="#94a3b8" font-size="8"  font-family="Inter">/bookings/modify</text>
</svg>
</figure>

The agent runs fully autonomous up to step 2. At step 4 the Webhook **bypasses the LLM entirely** — deterministic code (and only deterministic code) ever touches production bookings. One locked path in, one locked path out.

---

# INVESTMENT & ROADMAP
**Execution Strategy**

<figure class="chart chart-timeline">
<svg viewBox="0 0 720 155" xmlns="http://www.w3.org/2000/svg">
  <line x1="40" y1="130" x2="700" y2="130" stroke="#1f2933"/>
  <text x="40"  y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">M0</text>
  <text x="205" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">M1</text>
  <text x="370" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">M2</text>
  <text x="535" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" font-family="Inter">M3</text>
  <text x="700" y="146" fill="#475569" font-size="8.5" letter-spacing="1.2" text-anchor="end" font-family="Inter">M4+</text>
  <rect x="40"  y="15"  width="165" height="22" fill="#60a5fa" fill-opacity="0.85"/>
  <text x="50"  y="30" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">01 · VALIDATION</text>
  <rect x="205" y="45"  width="165" height="22" fill="#60a5fa" fill-opacity="0.55"/>
  <text x="215" y="60" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">02 · CLOUD FARM</text>
  <rect x="370" y="75"  width="165" height="22" fill="#f59e0b" fill-opacity="0.85"/>
  <text x="380" y="90" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">03 · OPERATIONAL LINK</text>
  <rect x="535" y="105" width="165" height="22" fill="#84cc16" fill-opacity="0.85"/>
  <text x="545" y="120" fill="#0a0e14" font-size="10.5" font-weight="700" letter-spacing="0.8" font-family="Inter">04 · BIG DATA · QUICKSIGHT</text>
</svg>
</figure>

<div class="phases">
<div class="phase-row"><div class="phase-num">01 · VALIDATION</div><div class="phase-desc"><span class="phase-time">0-1 mo</span> Prove the prompt logic isolates profit perfectly, locally.</div></div>
<div class="phase-row"><div class="phase-num">02 · CLOUD FARM</div><div class="phase-desc"><span class="phase-time">1-2 mo</span> Deploy AWS SQS. Tune rate-limit handling for 429s.</div></div>
<div class="phase-row accent"><div class="phase-num">03 · OPERATIONAL</div><div class="phase-desc"><span class="phase-time">2-3 mo</span> Slack webhooks + direct mutation scripts.</div></div>
<div class="phase-row done"><div class="phase-num">04 · BIG DATA</div><div class="phase-desc"><span class="phase-time">4+ mo</span> Amazon QuickSight "Yield Dashboards" for C-level.</div></div>
</div>

---

# MarginOptimizer
**Autonomous, Invisible, Highly Profitable**

Confidential & Proprietary 
B2B Yield Optimization AI.
