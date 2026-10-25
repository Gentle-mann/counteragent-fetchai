# Verification record — 25 October 2026

## Automated checks

The current suite contains 66 tests. They exercise policy floors, scenario feasibility, department dependencies, forged/duplicate inputs, approval ownership and expiry, stale hashes, invoice/terms changes, signatures, payment matching, bank changes, supplier challenges/onboarding, cross-buyer isolation, adviser privacy boundaries, Slack action binding and sequential optional review retries.

Offline model responses are deterministic. The harness dispatches actual handlers over a queue; it does not prove network delivery or model intelligence. Stripe API calls in tests are mocked. Test results and a source snapshot are provided alongside this record.

## Live evidence

| Run | Observed result | What it does not prove |
| --- | --- | --- |
| 4e901e0d4a61, live ASI:One | Agentverse found both published demo suppliers; signed scope receipts traveled over Agentverse mailbox; both public advisers responded; Finance/Legal/IT produced two verdicts each without review errors; Slack approval; valid buyer and vendor signatures; AP match; payment_complete; IT report; closed | Real company authority, real funds, production provisioning, every adversarial variant |
| 249482a9e421, earlier live ASI:One security demo | Same supplier changed approved invoice; payment blocked, old approval revoked, fresh approval obtained; demo closed | The later dual-signature implementation in that exact historical run |
| 4a95515f5826, later user-started live ASI:One | Both suppliers discovered and negotiated; Quickdash recommended at $126,000/year versus Beacon $127,500; awaiting human approval at documentation time | Closed payment or IT execution until the human approves |
| Stored scenario comparison runs | Baseline, cash pressure, capacity shortage, infeasible budget, Beacon value, Quickdash value, head-to-head recorded with ASI model decisions | Controlled benchmark, deterministic live outcomes or measured enterprise cycle-time reduction |

The full signed run recommended Beacon at $120,000/year versus Quickdash at $126,000, with 7-day versus 21-day implementation. A later run recommended Quickdash when its compliant final quote was lower. This variability is part of real model-assisted negotiation; show the selected case’s actual recorded outcome.

## Inspect the evidence

- Curated JSON records under `evidence/` keep business events, scope/identity receipts and security transitions without raw private memory or Slack user IDs.
- Signed fictional document packet: both receipts can be independently verified with `contracts.verify_packet` and the recorded expected public addresses.
- Screenshot of the completed graph: discovery shortlist and closed status.
- The runtime dashboard at http://127.0.0.1:8060/ requires a running local process and local case data. That loopback link is not a publicly hosted application.

## Known gaps

No production crash recovery, process isolation, general supplier onboarding, non-analytics execution profile, live Stripe settlement, legal Docusign execution, externally provisioned tenant, platform-moderation bypass test or independent penetration test is claimed. The personal ASI:One profile and deployed Agentverse agent are separate identities; use the deployed agent for the actual workflow.
