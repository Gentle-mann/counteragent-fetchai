"""Public capability handshake shared by independent supplier agents.

Address signatures prove control of an agent identity, not legal company authority.
"""
import re
from uagents import Model
from uagents_core.identity import Identity
from governance import digest

PROTOCOL_NAME='CounterAgentSupplierNegotiation'
PROTOCOL_VERSION='1.0.0'

class CapabilityRequest(Model):
    request_id: str
    nonce: str
    category: str
    seats: int
    term_months: int
    currency: str = 'USD'
    reply_via_mailbox: bool = False

class CapabilityResponse(Model):
    request_id: str
    nonce: str
    supplier_id: str
    company_name: str
    agent_address: str
    category: str
    seats: int
    term_months: int
    currency: str
    can_quote: bool
    fictional_demo: bool
    protocol_version: str
    signature: str = ''

def capability_body(response):
    body=response.model_dump()
    body.pop('signature',None)
    return body

def verify_capability(request,response,address):
    try:
        return (isinstance(response,CapabilityResponse)
            and response.request_id==request.request_id and response.nonce==request.nonce
            and response.agent_address==address and response.category==request.category
            and response.seats==request.seats and response.term_months==request.term_months
            and response.currency==request.currency and response.can_quote is True
            and response.protocol_version==PROTOCOL_VERSION
            and bool(re.fullmatch(r'[a-z][a-z0-9_-]{1,63}',response.supplier_id))
            and 0<len(response.company_name)<=100
            and Identity.verify_digest(address,bytes.fromhex(digest(capability_body(response))),response.signature))
    except Exception:
        return False
