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
How the autonomous agent operates at 03:00 AM.
**03 | Infrastructure & Scaling**
Processing thousands of items without triggering API bans (SQS).
**04 | The Approval Loop (HITL)**
Slack Webhooks and operator-side security.
**05 | Development Roadmap**
From local validation to cloud dashboard deployment.

---

# T H E  C O S T  F A C T O R
**Creating Money From Inefficiency**

**The Scenario:** A package tour is sold today for departure in 3 months. The flight cost locked today is $1000. 
**The Opportunity:** In month 2, a competitor airline drops identical flights (same luggage, similar time) to $800. Agencies miss this because humans cannot manually check 50,000 PNRs every day.
**The Solution:** MarginOptimizer entirely automates this tracking using AI.

**The ROI:**
Discovering just a $20 saving on 10% of 50,000 yearly bookings = **$100,000 pure Net Profit**. 

---

# S Y S T E M  A R C H I T E C T U R E
**AWS Serverless High-Throughput Engine**

| **Service** | **Function in the Architecture** |
| :--- | :--- |
| **AWS EventBridge** | Cron trigger launching the scan at 03:00 AM nightly |
| **Amazon SQS** | Queues 10,000 Bookings, protecting Traffics API from DDoS |
| **Lambda (Worker)** | Spawns Strands Agent to process singular queue items |
| **API Gateway** | Listens for human "Approve" clicks from Slack |
| **DynamoDB/RDS** | Logs every detected margin to generate BI dashboards |

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
1. The AI detects an $80 margin on Booking ID 4410.
2. It sends a Slack notification: *"Revise flight to SunExpress to save $80?"*
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
