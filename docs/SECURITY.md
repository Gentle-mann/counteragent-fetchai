# Security model and adversarial demonstrations

CounterAgent enforces transaction-specific authority even when a previously recognized supplier changes its behavior. This is a prototype control set, not a security audit or a claim about Agentverse moderation internals.

## Threats and implemented controls

| Threat | Enforced control | Regression evidence |
| --- | --- | --- |
| Vendor text tells buyer to ignore policy or disclose budget | Treat counterpart content as data; model findings cannot waive deterministic requirements; outgoing commercial prose rendered from validated fields | test_budget_cannot_escape_in_model_prose |
| Cheapest quote lacks mandatory security/legal terms | Non-waivable deterministic vetoes and cleared-candidate selection | test_cheaper_unsafe_vendor_cannot_win and workflow veto tests |
| Forged or duplicate task result | Sender/role/task correlation, completed-task checks and duplicate-round handling | test_concurrent_duplicate_proposals_consume_one_round and workflow sender tests |
| Stale/changed/expired human approval | Bind offer, review results, revision and exact document hash; verify owner and expiry; reject stale card hash | test_changed_terms_invalidate_approval, test_expired_approval_blocks_closing, test_stale_card_hash_blocks_closing |
| Different person or Slack message approves | Allowlisted user, team, channel, message timestamp, approval hash and current awaiting state | test_slack_rejects_wrong_identity_channel_team_snapshot_or_message |
| Same vendor changes invoice or approved terms after approval | AP detects mismatch, blocks payment, records incident and revoked approval, re-runs clearance and requires fresh approval | test_invoice_change_blocks_then_requires_fresh_approval, test_terms_change_blocks_then_requires_fresh_approval |
| Vendor identity signs different documents | Verify both expected agent identities, roles and canonical document hash; refuse modified packets | test_modified_vendor_signature_blocks_payment and contracts tests |
| Invoice redirects to another bank record | Match approved vendor master; unverified bank-change request is held | test_bank_change_blocks_ap_and_it |
| Payment amount/currency/reference/recipient/deadline differs | Exact payment-message validation; payment completion gates IT | payment mismatch and expiry workflow tests |
| Marketplace agent claims supplier capability | Protocol compatibility plus signed nonce/request/scope/address verification | test_signed_capability_bound_to_nonce_scope_and_identity |
| Unknown company impersonates a demo vendor | No inheritance of demo charter/evidence/bank destination; independent supplier held for onboarding | discovery onboarding tests |
| Public buyer corrupts another buyer’s quote state | Scope external quote history to sender and deal; input bounds, bounded rounds and rate limits | discovery external buyer isolation/rate tests |
| External adviser injects instructions or imaginary quotes | Public offer allowlist, untrusted advice, explicit departmental verdicts and no execution authority | adviser boundary and advisory handoff tests |
| Notification failure stops safety checks | Retry notifications independently; workflow retains gates | test_notification_failure_does_not_interrupt_workflow |

## Same-identity invoice-change scenario

1. Start `security demo invoice` (or structured security_demo=invoice_change).
2. Negotiate a compliant Quickdash offer and complete departmental clearances.
3. Human approves the original version.
4. The fixture makes the same supplier executive identity send a changed invoice/offer.
5. AP records vendor_revision and security_block. The orchestrator revokes the old approval, increments revision and re-runs reviews. No CommitPayment or IT handoff occurs.
6. Reusing the old hash is rejected.
7. The human reviews and approves the new exact revision. Both agents sign its bundle; matching sandbox payment can then precede IT.

`security demo terms` exercises changed contract terms. The fixture is deliberate and documented; it is not proof we uploaded a benign agent, evaded platform scanning and later modified it maliciously. We do not claim ASI:One/Agentverse scans or rescans on any particular schedule.

## Evidence hierarchy

Live ASI:One case 249482a9e421 completed the same-vendor invoice-change/reapproval flow before the later dual-signature addition. The current regression suite covers invoice and terms revision flows with the current signing implementation. Live ASI:One case 4e901e0d4a61 separately completed signed capability discovery, external advice reviews, Slack approval, dual signatures, AP validation, sandbox payment and IT. Do not combine these into a claim that one single live run demonstrated every later feature and attack variant.

## Important limits

- Agent address signatures prove control of a key, not a company’s legal identity or signatory authority.
- Distinct agent identities share one process. Application-scoped data is not protection against malicious local Python code or an operator reading fixtures.
- Local synthetic vendor floors are private from counterpart messages, not secret from someone reading this demo source repository.
- SQLite traces are append-only by application convention, not a tamper-evident external audit ledger.
- A validator passing does not prove the authenticity or real-world adequacy of synthetic evidence.
- No funds settle. No live Docusign contract is sent and no external SaaS tenant is provisioned.
- Session execution state resets on restart. The stored audit record is not automatic recovery.
- Signed scope checks are admission controls, not a guarantee that an admitted agent will behave safely later. Execution checks remain necessary.

Never commit credentials, seeds, raw account screenshots, private role memory or local .env files. Public evidence is curated from synthetic business events with user identity and transport/session identifiers removed.
