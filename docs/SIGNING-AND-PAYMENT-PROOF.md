# What counts as signing and payment proof?

There is **no Docusign envelope or real payment receipt** in this prototype. Docusign was researched and a connector is available in the development chat, but the CounterAgent runtime does not call it. Agent signatures and sandbox payment are the implemented features.

## User-run Quickdash deal: 4a95515f5826

- ASI:One chat: https://asi1.ai/chat/3e8d168e-cf22-420b-8b9b-4044a05620b6 (access depends on the account).
- Approved price: USD 126,000 per year, 250 employees, 24 months; total subscription commitment USD 252,000.
- Agreement bundle: order form, MSA, DPA/security addendum and implementation SOW.
- Local inspection link: http://127.0.0.1:8060/documents/4a95515f5826/0/316f7a6f5ecd (requires the local dashboard).
- Public signed packet: `evidence/4a95515f5826-r0-316f7a6f5ecd.json`.
- Both buyer and supplier sign the identical document hash with their uAgent identities. AP checks the expected addresses, signature roles and document hash.
- Recorded payment progression: payment_request → payment_commit → payment_complete; sandbox transaction identifier **DEMO-4a95515f5826**. This is a message-exchange receipt, not bank or blockchain settlement. No money moved.
- First annual invoice: USD 126,000 under Net 45 terms; zero deposit and zero due at signature. The demo clock compresses the invoice due date. The second annual invoice remains scheduled at month 12.
- IT creates the local TENANT-4a95515f5826 manifest after AP/payment completion. No real Quickdash tenant exists.

The ASI closing message confirms closed demo status, purchase order, invoice and manifest IDs. Detailed evidence is in the linked document packet and public event trace; the current UI does not show a Docusign envelope or actual settlement receipt because neither exists.

## Independently verify the packet

From an environment with the repository dependencies installed:

```python
import json, sys
sys.path.insert(0, 'fetchai')
from contracts import verify_packet
packet = json.load(open('evidence/4a95515f5826-r0-316f7a6f5ecd.json'))
expected_buyer = 'agent1q2qz4tp5uylllpqjs8f9497cx72k7rkmww7t72shxnam22xszk0e2mzcy0k'
expected_vendor = 'agent1q2g5w8wcaavrfc63qx0c552ggr9s4vsl45fr0lnryyxga8cjsck3ur39gwh'
print(verify_packet(packet, expected_buyer, expected_vendor))  # True
```

Cryptographic validity proves integrity and control of these agent keys, not legal corporate authority. For a production workflow, connect a governed eSignature provider, verify signatory authority, configure an authorized real payment rail and confirm actual settlement independently.
