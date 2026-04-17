# Product Requirements Document (PRD): MarginOptimizer

> **Status:** Ready for implementation · **Owner:** Hashtag World · **Last updated:** 2026-04-17

## 1. Executive Summary

MarginOptimizer is a B2B, headless Yield Management engine for travel agencies. Built on Strands Agents (Bedrock Claude **Haiku**) + `strands-traffics`, it runs nightly across every active Pauschal booking that has not yet departed, scans Traffics `/offers/{code}/alternativeFlights` for cheaper yet equivalent flights (same baggage rules, ±3 h schedule window), calculates the margin delta deterministically with the `calculator` tool, and — only after a human-in-the-loop Slack approval — mutates the booking via Traffics `/bookings/{id}` PATCH. The result is recovered margin on already-sold tours, surfaced to management via an Amazon QuickSight "Yield Recovered" dashboard.

## 2. Problem Statement

When an agency sells a Pauschal package, the flight leg price is locked at sale time. In the months before departure, alternative carriers often publish cheaper equivalent flights — but nobody at the agency has the time to scan 10,000 PNRs per night by hand. Result: 1–3 % of total bookable margin is left on the table. MarginOptimizer closes that gap autonomously, with human approval on each mutation to preserve customer trust.

## 3. Target Audience & Personas

| Persona | Primary Need | Quote |
|---|---|---|
| **Agency Operations Manager** | Cut flight cost per booking without adding headcount | "Elimde 8.000 aktif PNR var, manuel tarayacak kadrom yok." |
| **Revenue / Yield Manager** | Visibility into recaptured margin, trust in execution | "Her gece ne kadar kar yakaladığımızı dashboard'da görmek istiyorum — ama müşterinin uçuşu haberim olmadan değişmesin." |
| **Reservations Agent** | A clear approve/reject button, not a spreadsheet | "Slack'te zaten kanalımız var, yeni bir sisteme girmek istemem." |

## 4. User Stories & Acceptance Criteria

### US-1 — Nightly PNR scan
> As the operations team, I want every active Pauschal PNR scanned each night automatically.

**Acceptance criteria:**
- [ ] At `02:00 Europe/Berlin` daily, EventBridge triggers the ingestion Lambda.
- [ ] The ingestion Lambda reads from the agency's booking store (Postgres/DynamoDB), filters to `status = CONFIRMED`, `departure_date > now()`, and pushes one SQS message per booking.
- [ ] ≥ 10,000 bookings are enqueued within the 3-hour nocturnal window without DLQ overflow.

### US-2 — Alternative flight detection
> As the agent, I want to call Traffics for alternatives and discard non-equivalent options.

**Acceptance criteria:**
- [ ] For each SQS message, the worker Lambda calls `use_traffics(service="offers", endpoint="alternative_flights", params='{"code": "<offerCode>"}')`.
- [ ] The agent discards alternatives that (a) change baggage rules, (b) shift departure/arrival by > 3 h, (c) add a layover > 4 h, or (d) change the booking class tier.
- [ ] Rate-limit (HTTP 429) responses are retried via `strands-traffics` built-in Retry adapter; persistent failures emit a CloudWatch metric.

### US-3 — Deterministic margin calculation
> As the approver, I want the exact euro amount saved, not an LLM estimate.

**Acceptance criteria:**
- [ ] All delta calculations are performed by `strands_tools.calculator` (SymPy-backed), never by the LLM directly.
- [ ] Only alternatives with `new_price < old_price - MIN_MARGIN_EUR` (default 30 €) are surfaced.
- [ ] The Slack card shows: old price, new price, absolute delta, percentage delta.

### US-4 — Human-in-the-Loop approval
> As a reservations agent, I want to approve/reject changes in Slack with a single click.

**Acceptance criteria:**
- [ ] When a profitable alternative is found, the agent calls `slack(action="chat.postMessage", parameters={"blocks": [...interactive...]})` targeting the configured ops channel.
- [ ] Message contains: booking ID, customer initials, old/new flight details, delta, "Approve" and "Reject" buttons.
- [ ] Clicking a button hits an API Gateway endpoint → a modification Lambda that executes the Traffics `PATCH /bookings/{id}` deterministically (no LLM in the critical path).
- [ ] Idempotency: re-clicking Approve on a completed ticket is a no-op.

### US-5 — Rollback on mutation failure
> As operations, I want any failed booking swap to leave the original booking untouched.

**Acceptance criteria:**
- [ ] The modification Lambda uses a Step Functions saga: `reserve new flight` → `release old flight` → `confirm`.
- [ ] Any step failure triggers compensating actions that leave the original booking intact.
- [ ] Failed attempts are journaled (`strands_tools.journal`) and raised to the ops channel with a red marker.

### US-6 — Management dashboard
> As the revenue manager, I want a weekly view of recovered margin.

**Acceptance criteria:**
- [ ] Every successful modification inserts a row into `yield_events` (Postgres / Aurora).
- [ ] QuickSight dashboard updates hourly showing: total euros recovered per day/week/month, hit rate (profitable / scanned), top 5 route-pairs by delta.
- [ ] A weekly PDF report is emailed Monday 08:00 CET via SES.

## 5. Functional Requirements

### FR-1. Scheduling
AWS EventBridge cron rule `cron(0 2 * * ? *)` (Europe/Berlin via timezone config) → Lambda `ingest_bookings`.

### FR-2. Queueing
- Amazon SQS standard queue with visibility timeout = 6 × Lambda timeout.
- Dead-letter queue after 3 receive attempts.
- Reserved concurrency on the worker Lambda: start at **10** (≈ 5 Traffics TPS) and tune.

### FR-3. Agent Worker
- Model: Bedrock **Claude Haiku** (`us.anthropic.claude-haiku-4-5-20251001-v1:0`) — fast + cheap for parsing tasks.
- Tools: `use_traffics`, `calculator`, `slack`, `journal`, `use_aws`.
- System prompt enforces: (a) dry-run mode when `DRY_RUN=true`; (b) refuse mutation without human approval; (c) output "Task Complete. No action needed." when no profitable alternative exists.

### FR-4. Mutation Path (non-LLM)
A separate Lambda triggered by the Slack interactive webhook:
1. Verify HMAC signature from Slack.
2. Look up booking in local DB.
3. Call `strands_tools.use_aws` only for S3 logging, NOT for the mutation.
4. Call Traffics `PATCH /bookings/{id}` directly via `requests` (idempotency key = `<booking_id>:<offerCode_new>`).
5. Write `yield_events` row; acknowledge Slack.

### FR-5. Observability
- `BeforeToolCallEvent` / `AfterToolCallEvent` hooks log every `use_traffics` invocation to CloudWatch Logs Insights–queryable JSON.
- Custom CloudWatch metrics: `ScannedPnrs`, `ProfitableAlternativesFound`, `ApprovedChanges`, `RejectedChanges`, `MutationFailures`.

## 6. Non-Functional Requirements

| Category | Target |
|---|---|
| **Throughput** | 10,000 PNRs processed in ≤ 3 h nightly window |
| **Traffics TPS** | ≤ 5 TPS (respects rate limit with headroom) |
| **Mutation latency** | Approve click → Traffics PATCH success < 4 s (p95) |
| **Fault tolerance** | Zero partially-mutated bookings (saga rollback) |
| **Cost ceiling** | ≤ 0.005 € per scanned PNR (model + API) |
| **Region** | `eu-central-1` |
| **Security** | Slack HMAC verification; Traffics API key in Secrets Manager; least-privilege IAM per Lambda |

## 7. Out of Scope (MVP)

- Hotel rate optimization (flight swap only in MVP).
- Multi-tenant SaaS — initial deployment is single-agency.
- Customer-facing notifications about the swap (handled by agency's existing CRM).
- Predictive ("will price drop next week?") — reactive scan only in MVP.
- Non-Pauschal products.

## 8. Success Metrics & KPIs

| Metric | Target (Month 3 post-launch) | Target (Month 6) |
|---|---|---|
| Nightly PNR coverage | ≥ 95 % of active PNRs scanned | ≥ 99 % |
| Hit rate (profitable / scanned) | ≥ 2 % | ≥ 4 % |
| Approve rate (human accepts suggestion) | ≥ 70 % | ≥ 85 % |
| Mutation failure rate | < 0.5 % | < 0.1 % |
| Monthly recovered margin (single agency, 10k PNRs) | ≥ 8,000 € | ≥ 25,000 € |
| Cost per scanned PNR | ≤ 0.005 € | ≤ 0.003 € |

## 9. Testing Strategy

- **Unit:** `pytest` on margin logic, rollback saga, HMAC verification.
- **Integration:** Mocked Traffics via `responses` — including the 429 path and the `/bookings` PATCH path.
- **LLM evals:** Golden set of 50 alternative-flight scenarios. The agent must correctly surface only those with margin > threshold and stay silent on the rest. Zero false-positive mutation attempts in evals is release-blocking.
- **Dry-run mode:** `DRY_RUN=true` environment variable skips the actual PATCH; used in staging.
- **Chaos test:** Simulated Traffics 429 storm (25 % error rate) — throughput should degrade gracefully, not crash.
- **Security:** Slack signature verification test suite; IAM policy simulator in CI.

## 10. Dependencies & Risks

| Risk | Mitigation |
|---|---|
| Traffics 429 cascading | SQS throttle + exponential backoff + circuit breaker metric |
| Accidental customer-visible flight swap | Saga pattern + HITL Slack approval + DRY_RUN default for new environments |
| Slack outage blocks approvals | Fallback: daily email digest of pending approvals via SES |
| LLM hallucinates margin | Margin is **never** computed by the LLM — always via `calculator` tool |
| DB drift between agency system and our local cache | Daily reconciliation job; alarm if delta > 2 % |
| Leaked Traffics API key | Secrets Manager rotation policy (90 days); Key per environment |

## 11. Open Questions

- **Q1:** How do we access the agency's booking store? Direct DB replica, nightly dump, or their API? (Assumption: daily export to S3 for now; promote to replica in Month 2.)
- **Q2:** What's the minimum margin threshold (MIN_MARGIN_EUR)? (Assumption: 30 € EUR; configurable per agency.)
- **Q3:** Who is paged when nightly run fails entirely? (Assumption: on-call rotation in PagerDuty integration — define in Sprint 4.)
