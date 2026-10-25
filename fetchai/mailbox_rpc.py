"""Signed asynchronous Agentverse mailbox RPC, including same-process peers.

Uses the platform mailbox in both directions instead of the SDK's local shortcut.
"""
import time
from uuid import uuid4
import httpx
from uagents import Model
from uagents.dispatch import dispatcher
from uagents_core.envelope import Envelope

MAILBOX_SUBMIT='https://agentverse.ai/v2/agents/mailbox/submit'

async def mailbox_send(agent,destination,message,session):
    envelope=Envelope(version=1,sender=agent.address,target=destination,session=session,
        schema_digest=Model.build_schema_digest(message),expires=int(time.time())+45)
    envelope.encode_payload(message.model_dump_json())
    envelope.sign(agent)  # Agent exposes the same public sign_digest interface as Identity.
    async with httpx.AsyncClient(timeout=15) as client:
        response=await client.post(MAILBOX_SUBMIT,content=envelope.model_dump_json(),headers={'Content-Type':'application/json'})
        response.raise_for_status()

async def mailbox_request(agent,destination,message,response_type,timeout=25):
    session=uuid4()
    await dispatcher.register_pending_response(sender=agent.address,destination=destination,session=session,
        expected_schema_digests={Model.build_schema_digest(response_type)})
    try:
        await mailbox_send(agent,destination,message,session)
        response=await dispatcher.wait_for_response(agent.address,destination,session,timeout)
        if response is None:raise TimeoutError('Supplier mailbox did not respond')
        return response_type.parse_raw(response.message),None
    finally:
        dispatcher.cancel_pending_response(agent.address,destination,session)
