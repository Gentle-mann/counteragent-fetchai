# Detailed feature record

## Department depth and synthetic company data

The company fixture models 250 employees across five departments, 212 active analytics users, 64 EU employees, annual department allocations totaling $120,000, forecast demand, cash commitments, security classifications, contract clauses, historical invoices, vendor master records, an unverified bank-change ticket and a stale 242-user SCIM snapshot. These are synthetic fixtures, never customer records. The authorized per-deal cap can differ from historical allocations.

| Agent | Data and tools | Memory and follow-up | Decision responsibility |
| --- | --- | --- | --- |
| Orchestrator | Scope, reports, clearances, public offers, authority and approval snapshot | Assignment/result correlation and case status | Choose among cleared offers; stop for exact human approval |
| Research | Policy files, prior contracts, department facts and optional public background research | Source-backed purchasing brief | Propose target and requirements without waiving controls |
| Procurement | Validated offers, payment alternatives and financing comparison | Separate bounded negotiation track per supplier | Counter price/payment terms while preserving mandatory requirements |
| Security | Data-region, training, audit, SAML and SCIM requirements; trust-pack inspection | Evidence requests and bounded clarifications | Veto unresolved mandatory security failures |
| Legal | Liability, renewal, uplift, term and Security findings; contract comparison | Evidence provenance and clarification | Veto non-waivable legal failures; prepare document terms |
| Finance | Annual cap, 24-month TCV, allocations, credit/payment constraints and authority | Reconciliation and adviser assessment | Validate affordability and authorized commercial terms |
| Accounts Payable | Approved snapshot, both signatures, order, invoice, tax fixture and bank master | Revision incident, match result and payment correlation | Block changed/forged/mismatched execution before payment |
| IT | Approved 250-seat scope, identity snapshot and AP/payment result | Eight-user reconciliation and local rollout manifest | Stage 25-seat pilot / 225-seat rollout only after gated handoff |
| Vendor deal desk (each) | Private delivery/implementation costs, margins, quota, cash and capacity | Negotiation history; independent buyer scoping | Offer terms within supplier authority |
| Vendor Trust/Legal (each) | Supplier-specific evidence and policy | Purpose/offer-bound evidence replies | Supply substantiated controls and contract evidence |
| Vendor Executive (each) | Approved commercial quote, invoice and signing identity | Countersignature and payment flow | Countersign identical bundle; respond to AP/payment |

ASI:One models reason over the supplied records and return concise business findings. Executable tools and validators enforce boundaries. The graph records findings and decisions, not hidden chain-of-thought. Offline tests replace model decisions deterministically; they do not prove real-model reasoning quality.

## Commercial intelligence

Private supplier economics include cost-derived reservation limits, financing premiums, margin targets, quota pressure and implementation opportunity cost. Counteroffers cannot force a supplier below its validated floor. Quickdash’s base offering fails mandatory controls, but a paid Enterprise package can fix them. Remediation is included in the quoted annual total, not added twice. It increases price and adds implementation time; Beacon can win on included controls and speed, while Quickdash can win when its final compliant price is better.

Scenarios cover baseline, cash pressure, capacity shortage, infeasible budget, Beacon value, Quickdash value and head-to-head compliance. The graph compares actual concessions, controls, financing alternatives and final prices. Live outcomes vary; this is not a controlled causal intelligence benchmark.

## Discovery and specialist collaboration

Agentverse search combines category keywords and an exact published protocol digest. Listing/active status is only a candidate signal. A fresh signed challenge verifies identity control and supported scope before selection. Fictional fixture fallback is explicitly labeled separately from marketplace discovery. Unknown third-party suppliers are held for evidence, authority and payment onboarding rather than inheriting a demo company’s private records.

Azwin and Price Negotiator are existing external agents contacted through typed chat messages. Their actual text and identity are recorded. Finance, Legal and IT issue accept/reject/partial verdicts against the validated company context. An adviser’s proposed counterprice is never treated as an accepted quote. No response is recorded as unavailable, never fabricated advice. A reply from a public adviser cannot execute buyer commands or waive policy.

## Human approval, documents and payment

Native ASI:One review cards and private Slack Block Kit messages expose the reviewed vendor, amount, term and document link. Slack uses a bot plus Socket Mode, with an allowlisted approver and checks for workspace, channel, message timestamp, current state and approval hash.

The document bundle includes a fictional order form, MSA, DPA/security addendum and implementation SOW. Both agent identities sign the identical canonical bundle using actual secp256k1/SHA-256 signatures. AP verifies expected identities, roles, hashes and approved content. These are integrity demonstrations, not Docusign or legally verified corporate execution.

Billing models an annual subscription in advance over 24 months: zero deposit, zero due at signature, first annual invoice payable under the negotiated Net terms, second annual invoice at month 12. Remediation is included; there is no separate implementation charge in the fixture. The compressed demo clock replays first-invoice payment at its due date. It does not mean an immediate real-world down payment.

Payment uses AgentPaymentProtocol 0.1.0 RequestPayment → CommitPayment → CompletePayment with the custom counteragent_demo rail, USD and DEMO transaction IDs. Settled remains false. An optional Stripe test adapter rejects live keys and checks test invoice amount; it has mocked tests but no account-backed verification. IT creates a real local JSON manifest, not an external tenant.

## Graph and demo operations

Company groups and agent nodes show actual recorded communication paths. Messages, Decisions and Tools & data filters support event inspection. Quote cards show opening/final prices, remediation cost, rollout and policy status. Discovery cards show source, signed scope and fictional-company labeling. Revision events show what changed, why approval was revoked and how execution resumed. Documents expose signature checks. Scenario cards compare completed model runs. Replay, speed controls and Loop demo support a three-minute presentation without fabricating activity or rerunning transactions.

## Closing receipt UI

The dashboard shows the selected completed deal’s annual price, TCV, policy cap, remediation cost, evidence revision and rollout tradeoff. The first annual invoice is labeled Paid — sandbox only when the recorded approval, matching packet signatures, AP match and ordered payment completion are present. The UI explicitly shows zero down payment, zero due at signing and the year-two schedule. Verified signature cards link to the complete signed packet. Ad hoc negative checks confirmed that document mutation, missing payment completion or revoked approval suppress the paid state. This is not a Docusign receipt or real settlement.
