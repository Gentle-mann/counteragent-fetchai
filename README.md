# CounterAgent

**Your company’s agent for negotiating with other companies’ agents.**

CounterAgent coordinates Procurement, Research, Security, Legal, Finance, Accounts Payable and IT. It discovers compatible suppliers on Agentverse, negotiates validated offers, gathers evidence and independent advice, and stops for human approval before signing and sandbox closing.

![CounterAgent cover](fetchai/assets/counteragent-cover.png)

## Start here

- [Three-minute demo script and exact prompt](docs/DEMO-SCRIPT.md)
- [Complete feature record](docs/FEATURES.md)
- [Security model, adversarial scenarios and limitations](docs/SECURITY.md)
- [Verification record and evidence](docs/VERIFICATION.md)
- [Architecture and message handoffs](docs/ARCHITECTURE.md)
- [Setup and detailed implementation notes](fetchai/README.md)

## Try the deployed agent

[CounterAgent B2B Procurement on ASI:One](https://asi1.ai/ai/agent1q2qz4tp5uylllpqjs8f9497cx72k7rkmww7t72shxnam22xszk0e2mzcy0k) · [Agentverse profile](https://agentverse.ai/agents/details/agent1q2qz4tp5uylllpqjs8f9497cx72k7rkmww7t72shxnam22xszk0e2mzcy0k/profile)

The deployed process must be running. Type `@CounterAgent` and select **CounterAgent B2B Procurement**. The personal `@counteragent` profile is a different AI and does not automatically invoke this backend.

> Find analytics software for 250 employees, spending no more than $130,000 per year on a 24-month contract. Find compatible supplier agents on Agentverse, including the fictional demo suppliers. Negotiate with them, compare price, security and rollout time, and recommend a vendor. Stop for my approval before signing or payment.

A full live run commonly takes 6–8 minutes before approval; latency and outcomes vary. Use the graph’s recorded replay for a short presentation.

## What is implemented

- Fourteen distinct uAgent identities: one orchestrator, seven buyer departments and two supplier companies with three desks each.
- Real ASI:One model calls, typed uAgents messages, Agent Chat Protocol and native review cards.
- Real Agentverse marketplace search and mailbox-based signed capability challenges for the demo suppliers.
- Synthetic ERP/HRIS records, scoped departmental tools, SQLite memory and follow-up evidence requests.
- Private supplier economics, bounded counteroffers, paid remediation and multiple negotiation scenarios.
- Azwin and Price Negotiator advice, with independent departmental accept/reject/partial decisions.
- Slack Socket Mode approval with allowlisted identity and exact-approval binding.
- Fictional order form, MSA, DPA and implementation SOW with actual agent cryptographic signatures.
- Post-approval invoice/terms mutation checks, revoked approvals, fresh review, AP matching and gated IT handoff.
- AgentPaymentProtocol sandbox messages, plus a separately optional Stripe test adapter.
- Read-only local graph with messages, tools, decisions, scenario comparisons, document inspection and continuous recorded replay.

## Run

Requires Python 3.12 (tested). From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r fetchai/requirements.txt
Copy-Item fetchai/.env.example fetchai/.env
# Fill in ASI1_API_KEY and a new private COUNTERAGENT_SEED.
.\.venv\Scripts\python -B fetchai/agents.py
```

In a second terminal: `.\.venv\Scripts\python -B fetchai/dashboard.py`, then open http://127.0.0.1:8060/. Follow the implementation README to connect your own addresses to Agentverse. A new seed produces different agent identities; it does not control the published demo addresses.

```powershell
.\.venv\Scripts\python -B -m unittest discover -s fetchai -q
```

## Scope and evidence

The executable profile is analytics software, 250 employees, a 24-month term and annual USD pricing. Incompatible requests ask for clarification. Unknown supplier agents stop at onboarding before negotiation/closing; a marketplace listing is not proof of corporate authority.

All company records and vendors are explicitly fictional. Cryptographic signatures prove integrity and identity control, not legally established corporate signing authority. Payments use a sandbox rail; no money moves. IT writes a local manifest, not a vendor SaaS tenant. Stripe has mocked tests only; Docusign, 1Password and Browserbase are ecosystem examples, not runtime integrations.

This repository publishes the Python Fetch implementation and curated, redacted evidence without local credentials, seeds, raw private role memory or unrelated earlier application files. See [verification](docs/VERIFICATION.md) for what was actually tested.
