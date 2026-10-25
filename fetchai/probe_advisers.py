"""Live Agentverse protocol smoke test; fictional data only."""
import asyncio
import json
from uagents.query import query
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from advisers import ADVISERS
from transport import ApiResolver

PROMPT=('Fictional procurement test only. Analytics for 250 employees, annual cap $130000, 24 months. '
 'Both offers verified EU residency, SAML/SCIM, no training, liability12 months, uplift<=3%, optional renewal, Net45. '
 'Beacon $121000/year, rollout7days. Quickdash Enterprise $112500/year including $12000 remediation, rollout21days. '
 'Deadline10days. A 14day extension is NOT approved. Recommend a vendor, explain conditions and tradeoffs, '
 'give one hypothetical counteroffer. Do not contact sellers, waive requirements or transact. Concise JSON please.')

async def main():
    async def one(key,address):
        try:
            result=await asyncio.wait_for(query(address,ChatMessage(content=[TextContent(type='text',text=PROMPT)]),
                resolver=ApiResolver(),timeout=60),timeout=70)
            if hasattr(result,'decode_payload'):
                raw=result.decode_payload()
                print(json.dumps({'adviser':key,'status':'response','sender':result.sender,'payload':raw}),flush=True)
            else:print(json.dumps({'adviser':key,'status':'no_response','detail':str(result)}),flush=True)
        except Exception as e:print(json.dumps({'adviser':key,'status':'error','error':type(e).__name__}),flush=True)
    await asyncio.gather(*(one(k,a) for k,a in ADVISERS.items()))
if __name__=='__main__':asyncio.run(main())
