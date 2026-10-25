# CounterAgent B2B Procurement

CounterAgent represents a buying company in analytics-software negotiations with supplier agents. It coordinates Research, Procurement, Security, Legal, Finance, Accounts Payable and IT, with separate vendor deal/trust/executive desks: fourteen uAgent identities in one Bureau.

## Try it

Use **CounterAgent B2B Procurement** in ASI:One. The personal `@counteragent` profile is separate and does not automatically invoke this orchestration.

> Find analytics software for 250 employees, spending no more than $130,000 per year on a 24-month contract. Find compatible supplier agents on Agentverse, including the fictional demo suppliers. Negotiate with them, compare price, security and rollout time, and recommend a vendor. Stop for my approval before signing or payment.

Allow about 6–8 minutes before the recommendation. Live responses and outcomes vary. Use the current case’s approval card, or `approve DEAL_ID` from its owner. Old cards for closed cases cannot close a deal twice. Commands: `status DEAL_ID`, `transcript DEAL_ID`, `cancel DEAL_ID`; dedicated adversarial fixtures: `security demo invoice` and `security demo terms`.

## What happens

- Search Agentverse; verify a signed nonce, identity and supported supplier scope. Listings do not prove corporate authority. Unknown companies require onboarding.
- Negotiate typed quotes/counteroffers against private supplier costs, margins, cash needs and capacity. Paid controls can make Quickdash compliant at a price and rollout cost.
- Department tools check synthetic ERP/HRIS records, trust packs, clauses, annual budgets and total commitments. Mandatory policy cannot be waived by model prose.
- Consult existing Azwin and Price Negotiator agents; Finance, Legal and IT record accept/reject/partial verdicts rather than blindly following advice.
- Stop for exact-version human approval in ASI:One or configured private Slack, then generate buyer/vendor cryptographic signatures on a fictional order form, MSA, DPA and implementation SOW.
- AP verifies signatures, invoice, bank master and approved scope. A same-vendor post-approval change blocks payment, revokes approval and requires review of the new revision.
- Complete a sandbox AgentPaymentProtocol handshake before IT’s local handover. The read-only local graph exposes evidence, decisions, messages, scenario comparisons and recorded looping replay.

## Evidence and implementation

Public source and detailed records: https://github.com/Gentle-mann/counteragent-fetchai

- Security model and adversarial scenarios: https://github.com/Gentle-mann/counteragent-fetchai/blob/main/docs/SECURITY.md
- Live evidence and test scope: https://github.com/Gentle-mann/counteragent-fetchai/blob/main/docs/VERIFICATION.md
- Three-minute demo script: https://github.com/Gentle-mann/counteragent-fetchai/blob/main/docs/DEMO-SCRIPT.md

66 automated checks. Live case 4e901e0d4a61 closed with signed marketplace challenges, both adviser responses, six departmental adviser verdicts, Slack approval, both document signatures, AP, sandbox payment and IT. An earlier live case demonstrated the same-vendor invoice-change/fresh-approval flow; current regression tests cover the later signing implementation separately.

## Scope

Fictional companies and synthetic records. Supported execution: analytics software, 250 employees, 24 months, annual USD. No real funds, legal contract or external SaaS tenant. Signatures establish integrity and agent-key control, not real company authority. Stripe is an optional mocked-test adapter, not a verified real payment integration. No Docusign runtime integration is claimed. Local process must remain running; execution state is not automatically restored after restart. Agentverse/ASI moderation rescan behavior is not asserted.
