# CounterAgent: three-minute demo

Start a real negotiation 8–10 minutes before presenting. Keep its reviewed approval card ready. A fresh negotiation takes about 6–8 minutes, so the three-minute presentation uses a clearly identified recorded replay plus a live approval if available. Never describe replay as a new live execution.

## 0:00–0:25 — Why now (slide one)

“Agents can now access accounts, operate websites, send agreements and pay invoices. But before a company can buy anything, someone has to negotiate what it should agree to. CounterAgent represents your company in that negotiation.”

## 0:25–0:45 — The problem (slide two)

“Enterprise purchasing crosses Finance, Legal, Security and Procurement. APQC reports a 40-day median of company-reported average supplier-contract cycle times. We’re targeting that coordination problem. Our prototype does not claim to reproduce or eliminate forty days of real business work.”

## 0:45–1:15 — One request, a company team (ASI:One and graph)

“I asked for analytics software for 250 employees, under $130,000 a year. CounterAgent searched Agentverse and challenged compatible supplier agents to sign the requested scope. These are our fictional demo companies, Beacon and Quickdash. Seven buyer departments work with two supplier teams. This graph is a replay of an actual recorded run, so we can inspect the work within three minutes.”

Show the verified supplier shortlist, then messages between Procurement and vendor deal desks. Use Loop demo and Presentation pace. If displaying the current run instead, say it is live and show its actual state.

## 1:15–1:45 — Negotiation with real constraints (graph)

“Each supplier has its own costs, margin limits, cash needs and implementation capacity. Quickdash can fix its security gaps, but that costs money and adds rollout time. Procurement compares the actual price of longer payment terms with their financing benefit. The cheapest incomplete offer cannot override a failed company requirement.”

Click a negotiation decision. Read the selected deal’s actual prices, not memorized numbers. In completed run 4e901e0d4a61, Beacon moved from $124,500 to $120,000; Quickdash remained at $126,000 including its $30,000 controls package. In the later run 4a95515f5826, Quickdash was recommended at $126,000 versus Beacon at $127,500. Outcomes can vary.

## 1:45–2:10 — Independent advice and human authority

“We also consulted Azwin and Price Negotiator on Agentverse. Finance, Legal and IT each explain which advice they accept, partially accept or reject. These agents can advise; they cannot waive company policy. The final recommendation comes back to a human in ASI:One or our private Slack approval channel.”

Show an advice-assessment event and the current approval card. If the current deal awaits approval, approve only that deal. Old cards for closed deals correctly cannot trigger a second close.

## 2:10–2:40 — Security after approval

“The important security question is what happens after we trust an agent. In our security scenario, the same supplier changes its invoice or terms after approval. Accounts Payable blocks payment, revokes the old approval and routes the new revision for fresh review. Same identity does not mean unlimited authority.”

Show recorded security case 249482a9e421: vendor_revision, security_block and approval_revoked. If time is short, show the security documentation and evidence links. Do not claim we changed an Agentverse agent to bypass platform moderation; this tests CounterAgent’s own transaction controls.

## 2:40–3:00 — Close and scope

“After approval, both agents sign the identical document bundle. AP verifies the signatures, invoice and vendor record before a sandbox payment handshake, then IT receives the handoff. The prototype has 66 automated checks. No real money moves and no real SaaS tenant is created. CounterAgent shows how companies can delegate negotiation while keeping policy and human authority enforceable.”

## Exact live prompt

Select **CounterAgent B2B Procurement**, not the separate personal @counteragent AI. Then paste:

> Find analytics software for 250 employees, spending no more than $130,000 per year on a 24-month contract. Find compatible supplier agents on Agentverse, including the fictional demo suppliers. Negotiate with them, compare price, security and rollout time, and recommend a vendor. Stop for my approval before signing or payment.

Separate security scenario: `security demo invoice` or `security demo terms`. It requires two approvals and is too long to start from scratch during a three-minute presentation.

## Demo fallback

- Keep agents.py and dashboard.py running, the laptop awake, and the ASI:One API account funded.
- Use a previously completed graph case if a model call or network is slow. Replay never reruns tools or payments.
- Use the current deal’s approval card; do not click an older card in a closed chat.
- Explain that distinct agent identities currently share one Bureau/process. Process isolation and automatic crash recovery remain future work.
