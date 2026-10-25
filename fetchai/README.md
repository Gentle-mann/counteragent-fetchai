# CounterAgent on Fetch.ai

Supplier discovery now precedes Procurement. CounterAgent queries the public Agentverse search API by category and the published `CounterAgentSupplierNegotiation` protocol digest. Search results are candidates, not verified sellers. Inactive/unresponsive agents and incompatible protocols are excluded. Each shortlisted supplier must sign a fresh nonce, request ID, agent address, product category, quantity, term and currency. The graph records search results, rejection reasons, capability challenges, verified suppliers and onboarding holds.

Beacon and Quickdash publish the same versioned capability/RFP/Proposal protocol and clearly fictional supplier profiles. Their private charters remain separate. For multi-agent Bureau inspector setup, run `python supplier_inspectors.py`; connect Beacon through Agentverse inspector with local URI `http://127.0.0.1:8002`, Quickdash through `http://127.0.0.1:8003`. These fixed-address adapters bind only to loopback and forward the SDK inspector's required address header. They do not log tokens.

Natural-language requests use fictional suppliers only when the user explicitly requests a demo. JSON fixture requests retain demo defaults for existing scenario scripts; set `"allow_demo_suppliers": false` for discovery without fixtures. Fixture use is labelled `configured_demo_fixture`, never represented as a marketplace result. A compatible independent supplier is held at `needs_supplier_onboarding` until company authority, trust evidence, signer authority and bank-master records are established; its data never inherits a demo vendor's private pricing or payment destination. No matching supplier means no contract, payment or invented quote.

The executable supplier profile remains analytics software, 250 employees, 24 months, annual USD. Intake rejects other categories, currencies, quantities and billing bases instead of silently substituting that scope. Public agent address signatures prove identity control, not real company authority. The next production extension is supplier-specific evidence and onboarding adapters; arbitrary third-party suppliers cannot yet close deals automatically.

Demo prompt: “Run a demo: find analytics software for 250 employees for 24 months, spending no more than $130,000 per year in USD. Negotiate with supplier agents and recommend a deal for my approval.”

New Python implementation of CounterAgent's procurement design. The original
TypeScript application remains in `src/` and `public/` for reference.

Fourteen uAgent identities run in one Bureau: a company orchestrator, seven departments,
and two vendors each with a deal desk, Trust/Legal desk and executive approver. ASI:One models generate departmental findings and negotiation
messages. All collaboration happens through typed uAgents messages, with correlated
task IDs, sender checks, duplicate-result protection, and a timestamped transcript.

| Department | Actual work and dependencies |
| --- | --- |
| Research | Reads company policy and previous-contract files; briefs Procurement |
| Procurement | Exchanges opening quotes and two counteroffer rounds with each vendor |
| Security | Reviews privacy, residency, audit, and identity-management facts |
| Legal | Receives Security findings, reviews renewal and liability terms |
| Finance | Reviews budget, payment terms, TCV, and delegated authority |
| Accounts Payable | Waits for approval; checks vendor countersignature, invoice, bank directory and sandbox payment |
| IT | Waits for AP; writes an actual local demo workspace manifest |

The orchestrator waits for all clearances, makes its ASI-backed award decision,
then requests human approval. Every department has a policy veto. The buyer and two supplier deal desks are public. Signed supplier discovery traverses Agentverse mailbox; internal department/evidence negotiation messages use the Bureau local dispatcher. They have distinct cryptographic identities and message handlers.

No real payment, external tenant provisioning, or legal commitment occurs. Records
are explicitly simulated. Session state is in memory and resets on restart.

Verified on October 25, 2026: offline regression tests cover negotiation rounds,
departmental handoffs, vetoes, approval identity, cancellation, and model failure.
A live model check of the fourteen-identity implementation reached closed with all seven departments, 20 logical model
calls and 57 queued messages (deal `cb401b70cde2`, Beacon $118,000/year). That harness is not a network test. Agentverse mailbox
registration and ACP publication are complete. A real ASI:One UI run (deal
`d59feaf53e8a`) negotiated Beacon to $114,000/year, displayed a native review card,
accepted its approval button, completed AP's invoice match and sandbox payment
handshake, and ran IT provisioning. The returned transcript contains 69 events;
payment completion precedes the IT task. The workspace manifest exists locally.
The expanded evidence/clarification workflow also completed through the ASI:One
approval card (deal `e8189a8ab663`, Beacon $114,000/year, 133 recorded events),
including the independent invoice check, payment handshake and AP-to-IT handoff.

## Payment scope

AP and the winning vendor use the installed `AgentPaymentProtocol 0.1.0` models:
`RequestPayment -> CommitPayment -> CompletePayment`. The buyer checks the exact
amount, currency, sender, recipient, invoice reference, and deadline. A mismatch
fails the deal before IT runs. This uses the explicit custom rail
`counteragent_demo`, currency USD, and transaction IDs prefixed `DEMO-`.
`settled` is always false. No actual transfer, wallet debit or bank settlement occurs.
Protocol compliance is not settlement. An optional Stripe TEST adapter creates,
finalizes and pays a test invoice with a Stripe test payment method, validates the
exact amount and `livemode=false`, and refuses live keys or any out-of-band paid
fallback. Set `COUNTERAGENT_PAYMENT_BACKEND=stripe_test` and a local test-only
`STRIPE_SECRET_KEY` to enable it. No Stripe key is configured in this checkout;
that adapter has mocked API tests, not an account-backed integration test.

Real settlement would require a supported rail (for example Skyfire/USDC or
verified FET transfers), separate account configuration, amount authorization,
and verified settlement before IT. Never treat the sandbox handshake as payment.

## Existing Agentverse agents

The verified ASI1-Mini Agent at
`agent1qdhaqxdvjhtchfmra6ycwjt7p3dj7ucq2ccnx2ppk4pa5mde4kc0ghep43j`
was tested separately through ASI:One with fictional vendor terms. It returned an
independent five-policy comparison, passing Beacon and rejecting Quickdash. It is
an advisory-review candidate, not yet wired into the orchestration runtime. Its
profile calls it ASI1-Mini while the README references asi1; do not assume its
underlying model version. The inspected Web Search Agent was marked unresponsive,
so it was not used as a dependency. External outputs must not override charters.

Buyer address for this checkout:
`agent1q2qz4tp5uylllpqjs8f9497cx72k7rkmww7t72shxnam22xszk0e2mzcy0k`

## Run on Windows

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r fetchai/requirements.txt
Copy-Item fetchai/.env.example fetchai/.env
# Fill in ASI1_API_KEY and a private, randomly generated COUNTERAGENT_SEED.
.\.venv\Scripts\python fetchai/agents.py
```

Never commit `.env` or the agent seed. The seed controls the agent identities.
`ASI1_MODEL=asi1` is the starting model; `asi1-mini` is an option after latency and
negotiation-quality testing. API usage may require separate credits from ASI:One Pro.

## Verify locally

```powershell
.\.venv\Scripts\python -m unittest discover -s fetchai -v
```

Tests run offline with deterministic role outputs, exercise queued message dispatch
across all fourteen identities, and verify policy boundaries. They do not prove Agentverse
registration, real network delivery, model quality, or ASI:One UI compatibility.

Real API check (uses ASI:One usage allowance):

```powershell
.\.venv\Scripts\python fetchai/check_live.py
```

## Connect to Agentverse and ASI:One

1. Keep the fourteen-agent Bureau running on port 8001.
2. Register the **buyer address printed by this process**, never an example address.
3. For the mailbox route, set `COUNTERAGENT_MAILBOX=true`, restart, and use the
   Inspector link to connect the buyer's mailbox. Current v2 external onboarding
   alternatively requires a public `/submit` endpoint; set
   `COUNTERAGENT_ENDPOINT=https://YOUR-HOST/submit` when using that route.
4. Confirm the buyer's ACP manifest and profile are visible on Agentverse. Use
   accurate keywords: B2B procurement, vendor negotiation, charter enforcement,
   approval, analytics software. Mark the profile as a fictional-company demo.
5. Use Chat with Agent from that profile and test the entire workflow in ASI:One.
6. Test: `Procure analytics for 250 seats with a $120,000 annual budget.`
7. Inspect both vendor reviews. Click the native review card's approval button or
   send `approve DEAL_ID` to authorize AP, sandbox payment messaging, and IT.
   Use `status DEAL_ID`, `transcript DEAL_ID`, or `cancel DEAL_ID`. A deal ID allows
   the same sender to continue even if ASI:One changes the ACP envelope session.
8. Test a $100,000 budget: the buyer should walk away instead of breaking its charter.

The primary workflow is conversational, with a native approval card. Department memory
and events persist in SQLite; active execution is still in memory and does not resume
automatically after a process restart. Payments use a sandbox protocol, not real settlement.

## Team graph and new department capabilities

Run `.\.venv\Scripts\python fetchai/dashboard.py` from the repository root and open
http://127.0.0.1:8060. The read-only graph polls persisted message events, supports
node filtering and replay, and shows opening/final prices, savings and policy violations.
It exposes event records, not private department memories. Offline tests use a separate database.

Each department has durable case records and bounded tools. Research reads policy,
contract history, usage and synthetic benchmark documents. Procurement runs two
counteroffer rounds with each vendor. Security verifies trust-pack controls; Legal
compares quote and contract evidence; both can request one clarification round through
actual uAgents messages. Finance computes TCV, authority, budget headroom, utilization
and an early-payment comparison. AP obtains a vendor countersignature bound to the
offer hash and a vendor-issued invoice, checks amount/scope and a fixed bank directory,
screens a demo sanctions list, then executes the sandbox Payment Protocol. IT writes
and checks a local workspace manifest after the completed payment handoff.

Approval expires after 30 minutes and binds the winner plus all three reviews by hash.
Changing those terms invalidates approval. Outbound negotiation prose is rendered from
validated fields; arbitrary model prose cannot reveal the internal budget. The buyer
validates public offer fields without consulting the vendor's private floor. Vendor
validation always enforces that floor, including when a counterpart sends a lower
previous price. All fourteen agents currently share a process and OS identity: role identities
and memories are logical boundaries, not an isolation guarantee.

The synthetic benchmark is in `company_docs/negotiation-scenario.txt`. A $120,000
budget may produce a compliant deal; $100,000 should produce a walk-away. Vendor
models receive their private charter and case history, not a command to accept the final
buyer offer. Results can vary. Price concessions and policy compliance are observable
metrics; one successful run does not establish general negotiating intelligence.

The Fetch path now includes optional ASI hosted web search (set
`COUNTERAGENT_WEB_RESEARCH=true`), distinct vendor Trust/Legal and executive identities,
the optional Stripe test adapter, a local tenant page at `/t/DEAL_ID`, and model-call
timings/token counts/input-output hashes in the event inspector. Public research sends
only a fixed generic query and logs actual hosted-search call records; it never proves
fictional vendor compliance. The hosted search was separately checked against the ASI
Responses API. The original comparative human-time estimates are not migrated; measured
run time is preferable to an unverified productivity multiplier. No production SaaS
tenant, automatic restart recovery or real settlement is implemented.

## Submission checklist

- Public repository with run instructions and actual agent address.
- Agentverse registration and published ACP manifest.
- Discoverable and usable inside ASI:One; record intake through closing in chat.
- Evidence of real vendor-agent messages and real ASI:One API calls.
- Show charter-block and walk-away cases, not only the successful deal.
- Devpost submission plus Fetch's ASI:One submission agent.
- Check event rules on pre-existing code with organizers; describe the new work accurately.

Agentverse profile badges:

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)

## Primary references

- [Fetch Cal Hacks hackpack](https://www.fetch.ai/events/hackathons/calhacks-13-0/hackpack)
- [Official compatible uAgent example](https://innovationlab.fetch.ai/resources/docs/examples/chat-protocol/asi-compatible-uagents)
- [Agentverse v2 onboarding](https://docs.agentverse.ai/documentation/launch-agents/agentverse-sdk/u-agents)
- [ASI:One API quickstart](https://docs.asi1.ai/documentation/getting-started/quickstart)
- [Interactive cards](https://docs.agentverse.ai/documentation/advanced-usages/agent-driven-interactive-cards)

## Realistic company records and negotiation scenarios

`company_data.py` defines a versioned, explicitly synthetic ERP/HRIS fixture:
250 employees in five departments, 212 active analytics users, 64 EU employees,
annual allocations totaling $120,000, demand forecasting, cash commitments,
security classifications, contract clauses, vendor master records, historical invoices,
an unverified bank-change ticket and a stale 242-person SCIM snapshot.
Each department receives a scoped view and runs deterministic reconciliation tools;
source receipts and business findings appear in the graph's Tools & data tab.
IT reconciles eight missing directory entries and stages a 25/225-seat rollout.

`negotiation.py` gives each vendor private delivery costs, implementation costs,
margin targets, quota attainment, cash position, available capacity and contractual
authority. Delivery-cost margin floors, opportunity cost and payment financing premiums
are executable limits. Model-generated quotes include an alternative payment schedule;
Procurement evaluates the actual quote premium against an explicit 8% cost-of-capital
assumption. Neither private reservation prices nor buyer budgets are sent in counterpart
prose. Decision events distinguish a model-selected action from a commercial-policy
explanation; they do not expose hidden chain of thought.

Run all four real-model scenarios with:

```powershell
.\.venv\Scripts\python fetchai/run_scenarios.py
# Retry individual cases while preserving other recorded results:
.\.venv\Scripts\python fetchai/run_scenarios.py capacity_crunch tight_budget
```

Cases cover a normal quarter, cash pressure, scarce implementation capacity and an
infeasible budget. They run real ASI calls over the queued harness, stopping at approval
or walk-away. Timeouts are execution errors, never successful walk-aways. Results are
saved to `.runtime/scenario-results.json` and displayed as selectable comparisons in
the graph. Live quotes vary; this is not a controlled causal study or a general
intelligence benchmark. Offline tests separately establish the expected feasibility
boundaries and record reconciliation invariants.

Plain-language demo prompt:
"Find analytics software for 250 employees, spending no more than $130,000 per year
on a 24-month contract. Discover compatible agents on Agentverse, including the
fictional demo suppliers. Negotiate with them and recommend a vendor. Stop for my approval."

Natural-language requests require explicit permission to use fictional demo suppliers.
Discovery searches Agentverse, challenges each compatible supplier with a signed nonce
and requested scope, and records the source and transport in the graph. A signature
proves control of an agent identity, not corporate authority. Unknown third-party
suppliers stop at onboarding before negotiation or commitments; this demo does not
automatically adapt arbitrary agents. Unsupported categories, quantities, terms or
currencies ask for clarification instead of substituting the analytics fixture.

Use a structured request to select a scenario explicitly:
`{"budget":120000,"scenario":"cash_pressure","objective":"Find analytics software for 250 employees."}`
The default is `baseline`. The native approval gate still applies.
