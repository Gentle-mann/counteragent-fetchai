## Inspiration

Agents can increasingly sign into accounts, operate websites and initiate business workflows. But buying software still means reconciling price, cash flow, security requirements and contractual obligations across two companies.

We built CounterAgent around a concrete question: what if your company had an agent that could coordinate its own departments and negotiate with the agents of supplier companies, while keeping policy and human authority enforceable?

APQC reports a 40-calendar-day median of company-reported average supplier-contract cycle times across 3,081 companies. That motivates the coordination problem; our synthetic demo does not establish a real-world cycle-time reduction.

## What it does

CounterAgent is your company’s procurement agent inside ASI:One. Ask:

> Find analytics software for 250 employees, spending no more than $130,000 per year on a 24-month contract. Find compatible supplier agents on Agentverse, including the fictional demo suppliers. Negotiate with them, compare price, security and rollout time, and recommend a vendor. Stop for my approval before signing or payment.

The orchestrator coordinates seven departments: Research, Procurement, Security, Legal, Finance, Accounts Payable and IT. Beacon and Quickdash each have a Deal Desk, Trust/Legal desk and Executive Approver: fourteen distinct uAgent identities, plus two independent public advisers.

Before negotiation, CounterAgent searches Agentverse, checks protocol compatibility and challenges suppliers to sign a fresh nonce and requested scope. A listing is not enough. Unknown companies stop for onboarding rather than inheriting a demo supplier’s evidence or payment destination.

Procurement exchanges actual typed quotes and counteroffers. Each vendor has private costs, margin limits, cash constraints, quota and implementation capacity. Quickdash can fix its missing controls through a paid Enterprise package; the buyer must weigh the resulting price and rollout delay against Beacon. Both vendors can win under different conditions, and an infeasible deal ends without a purchase.

Security, Legal and Finance inspect evidence and enforce their requirements. Existing Agentverse agents Azwin and Price Negotiator provide independent advice; Finance, Legal and IT each explain what they accept, reject or partially accept. Advice cannot waive company policy or turn an unaccepted counteroffer into an agreed price.

A native ASI:One review card or private Slack message requests human approval of the exact reviewed version. Buyer and supplier agents then cryptographically sign the same fictional order form, MSA, DPA and implementation SOW. AP checks both signatures, invoice, amount, scope and vendor bank record before a sandbox payment-protocol exchange. IT receives the handoff only afterward.

The graph shows messages, decisions, evidence, concessions, adviser verdicts and security transitions. Recorded replay and continuous looping let judges inspect a full run without waiting for every model call.

## Security after approval

Recognizing an agent’s identity does not give it unlimited transaction authority. In our adversarial demo, the same supplier changes its invoice or approved terms after the human approves. AP blocks payment, revokes the old approval, re-runs review and routes the new revision for fresh approval. The old hash cannot authorize the changed deal, and IT cannot proceed while payment is blocked.

We also test stale/expired approvals, wrong approvers, forged or duplicate messages, document tampering, bank-change mismatches, incorrect payment amounts, supplier challenge mismatches, cross-buyer quote isolation and model-generated attempts to leak the private budget. These are CounterAgent’s application controls, not claims about bypassing or reverse-engineering Agentverse’s moderation checks.

## How we built it

The Python implementation uses Fetch.ai uAgents, Agentverse discovery/mailboxes, Agent Chat Protocol, AgentPaymentProtocol and ASI:One model calls. Fourteen identities share one Bureau. Typed messages carry correlated task IDs; handlers check expected senders, roles and duplicate results.

Each department works from a scoped view of synthetic company records: 250 employees, 212 active users, 64 EU employees, departmental budgets, cash commitments, contract history, vendor records, an unverified bank-change ticket and a stale SCIM snapshot. Tools reconcile those records; SQLite preserves role-specific case steps and event traces.

Models propose findings and terms. Executable checks enforce commercial limits, mandatory requirements and approval authority. Outgoing commercial text comes from validated fields. Human approval binds the offer, review results, revision and document hash. Slack Socket Mode validates the authorized user, workspace, channel, message and current approval snapshot.

## Challenges we ran into

The hard part was making agent communication useful without letting persuasive text override structured facts. Remediation fees must not be counted twice. Proposed counteroffers must not become accepted quotes. A supplier’s quote must remain separate from another buyer’s case. Duplicate messages must not consume another round, and an optional adviser timeout must not derail required reviews.

We also handled ASI:One session changes, exact-version approval cards, Agentverse mailbox delivery, multi-agent inspector routing and the difference between payment-protocol completion and actual settlement. Optional adviser assessments now run sequentially with compact context and a bounded retry.

## Accomplishments that we’re proud of

A live ASI:One run completed Agentverse search, signed supplier capability checks, negotiations, both independent adviser responses, all six departmental adviser verdicts, Slack approval, buyer/vendor signatures, AP verification, sandbox payment and IT handoff. In that run, Beacon won at $120,000/year versus Quickdash at $126,000, with a 7-day rather than 21-day rollout. A later user-started run recommended Quickdash at $126,000 versus Beacon at $127,500, showing the winner is not hardcoded.

An earlier live security run demonstrated a same-vendor invoice change, payment blocking and fresh approval. Current automated tests cover invoice and term changes with the newer signature implementation. The suite passes 66 checks. Our public repository documents these evidence levels separately instead of claiming every feature was demonstrated in one run.

## What we learned

An agent becomes useful when it has relevant records, bounded tools, memory, and a decision it is responsible for. Negotiation intelligence also needs enforceable limits: discovering an agent, trusting its identity and approving a particular transaction are separate decisions.

## What’s next

Supplier-specific production onboarding, durable execution recovery, separately permissioned agent services and broader contract categories. The current executable profile is analytics software for 250 employees over 24 months in annual USD pricing. Other scopes request clarification.

All company records and supplier companies are fictional. Signatures prove document integrity and agent key control, not legal corporate authority. Payments are sandbox-only; no real funds move. IT creates a local manifest, not a live SaaS tenant. The optional Stripe test adapter has mocked tests and is not account-verified. Docusign, 1Password and Browserbase illustrate the wider ecosystem; they are not runtime integrations.

Code, security documentation, recorded evidence and demo guide: https://github.com/Gentle-mann/counteragent-fetchai

Problem research: https://www.apqc.org/resources/benchmarking/open-standards-benchmarking/measures/average-cycle-time-days-establish
