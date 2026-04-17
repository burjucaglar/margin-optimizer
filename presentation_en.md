---
marp: true
theme: dark
paginate: true
---

# MarginOptimizer
## B2B Dynamic Alternative Flight & Yield Management System
### Strands Agent Automated PNR Analysis

---
**Key Metrics**
- **$5.2B** | Global Dynamic Pricing Tech Market
- **10K+** | Nightly PNR Scan Capacity
- **+1-5%** | Marginal Net Profit Increase Per Booking
- **100%** | Human-In-The-Loop Safety Record

---

# T A B L E  O F  C O N T E N T S
**What This Document Covers**

**01 | The Cost Factor**
Extracting invisible profit from waiting tickets.
**02 | The Solution Lifecycle**
How the autonomous agent operates at 02:00 (Europe/Berlin).
**03 | Infrastructure & Scaling**
Processing thousands of items without triggering API bans (SQS).
**04 | The Approval Loop (HITL)**
Slack Webhooks and operator-side security.
**05 | Development Roadmap**
From local validation to cloud dashboard deployment.

---

# T H E  C O S T  F A C T O R
**Creating Money From Inefficiency**

**The Scenario:** A package tour is sold today, departure in 3 months. The locked-in flight cost is €1,000.
**The Opportunity:** In month 2 a competitor (or the same airline) drops an identical flight — same baggage, same window — to €800. Agencies miss it because a human cannot scan 10,000 PNRs every night.
**The Solution:** MarginOptimizer runs one Haiku-class worker per PNR, autonomously, every night.

**The ROI:**
~50,000 yearly bookings × 2% profitable-hit rate × €40 average saving = **≥ €40,000 / year** in pure recovered margin.

---

# S Y S T E M  A R C H I T E C T U R E
**AWS Serverless High-Throughput Engine**

| **Service** | **Function in the Architecture** |
| :--- | :--- |
| **AWS EventBridge** | Nightly cron at 02:00 Europe/Berlin kicking the ingest Lambda |
| **Amazon SQS** | Queues 10,000 bookings with a DLQ, shielding Traffics from bursts |
| **Lambda (Worker)** | One Strands + Haiku 4.5 agent per PNR, max 10 concurrent |
| **API Gateway** | Receives Slack approval webhooks, HMAC-verified before routing |
| **Aurora Postgres** | Writes every approved swap to `yield_events`; feeds QuickSight |

---

# S T R A N D S  T O O L I N G
**The Margin Finders**

- **`use_traffics`**
  - **Target:** `/offers/{code}/alternativeFlights`
  - **Execution:** Pings the Traffics spine to query identical alternative planes.
- **`calculator_tool`**
  - **Execution:** Deterministically calculates (New Price - Old Price).
  - **Integrity:** Prevents LLM mathematical hallucinations.
- **`slack_tool`**
  - **Target:** Company operations channel.
  - **Execution:** Dispatches interactive UI blocks (Approve/Reject) showing the found margin.

---

# T H E  A P P R O V A L  L O O P
**Zero Unwanted Actions**

The agent works entirely autonomously until a flight needs mutating. 
1. The AI detects an €80 margin on Booking ID 4410.
2. It sends a Slack notification: *"Revise flight to SunExpress to recover €80?"*
3. The human operator clicks **[APPROVE]**.
4. An AWS Webhook bypasses AI and directly triggers Traffics `/bookings/modify`. 
5. Absolute data safety achieved.

---

# I N V E S T M E N T  &  R O A D M A P
**Execution Strategy**

**Phase 1: Validation (0-1 Mo)**
Prove the specific prompt logic isolates profit perfectly locally.
**Phase 2: Cloud Farm (1-2 Mo)**
Deploy AWS SQS queues. Tweak rate-limit handling for 429s.
**Phase 3: Operational Link (2-3 Mo)**
Integrate the Slack Webhooks and the direct Mutation scripts.
**Phase 4: Big Data Returns (4+ Mo)**
Roll out Amazon QuickSight automated C-Level "Yield Dashboards".

---

# MarginOptimizer
**Autonomous, Invisible, Highly Profitable**

Confidential & Proprietary 
B2B Yield Optimization AI.
