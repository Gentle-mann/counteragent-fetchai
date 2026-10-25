"""Queued test transport. Not proof of network delivery."""
from collections import deque
from uuid import uuid4
import agents
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent


class Bus:
    def __init__(self):
        self.queue = deque()
        self.deliveries = []
        self.replies = []
        self.session = uuid4()
        self.transform = lambda message: message

    def context(self, sender, session=None):
        bus = self
        class Context:
            async def send(self, destination, message):
                bus.queue.append((sender, destination, message, self.session))
            async def send_and_receive(self,destination,message,response_type,**kwargs):
                if not isinstance(message,agents.CapabilityRequest):
                    raise RuntimeError('Harness has no external transport')
                vendor=next((k for k,a in agents.vendors.items() if a.address==destination),None)
                if not vendor:return None,None
                replies=[]
                class ReplyContext:
                    async def send(self,target,response):replies.append(response)
                await agents.capability_handler(vendor)(ReplyContext(),sender,message)
                bus.deliveries.append((sender,destination,message))
                return replies[0] if replies else None,None
        ctx = Context()
        ctx.session = session or self.session
        return ctx

    async def chat(self, text, sender='local-user', session=None):
        await self.chat_message(ChatMessage(content=[TextContent(type='text', text=text)]), sender, session)

    async def chat_message(self, message, sender='local-user', session=None):
        agents.active_transport.set('queued_harness')
        await agents.on_chat(self.context(agents.buyer.address, session), sender, message)

    async def drain(self):
        agents.active_transport.set('queued_harness')
        handled = 0
        while self.queue:
            source, destination, message, session = self.queue.popleft()
            message = self.transform(message)
            self.deliveries.append((source, destination, message))
            ctx = self.context(destination, session)
            role = next((r for r, a in agents.departments.items() if a.address == destination), None)
            vendor = next((r for r, a in agents.vendors.items() if a.address == destination), None)
            evidence_vendor = next((r for r,a in {**{k+'.trust':a for k,a in agents.vendor_trust.items()}, **{k+'.executive':a for k,a in agents.vendor_executives.items()}}.items() if a.address==destination), None)
            if isinstance(message, agents.Task) and role:
                handler = agents.procurement_task if role == 'procurement' else agents.department_handler(role)
                await handler(ctx, source, message)
            elif isinstance(message, agents.Rfp) and vendor:
                await agents.vendor_handler(vendor)(ctx, source, message)
            elif isinstance(message, agents.Proposal) and role == 'procurement':
                await agents.procurement_offer(ctx, source, message)
            elif isinstance(message, agents.EvidenceRequest) and evidence_vendor:
                await agents.evidence_vendor_handler(evidence_vendor.split('.')[0])(ctx, source, message)
            elif isinstance(message, agents.EvidenceReply) and role:
                await agents.evidence_department_handler(role)(ctx, source, message)
            elif isinstance(message, agents.Report) and destination == agents.buyer.address:
                await agents.on_report(ctx, source, message)
            elif isinstance(message, agents.InvoiceRequest) and vendor:
                await agents.invoice_handler(vendor)(ctx, source, message)
            elif isinstance(message, agents.RequestPayment) and role == 'ap':
                await agents.payment_request(ctx, source, message)
            elif isinstance(message, agents.CommitPayment) and vendor:
                await agents.seller_commit_handler(vendor)(ctx, source, message)
            elif isinstance(message, agents.CompletePayment) and role == 'ap':
                await agents.payment_complete(ctx, source, message)
            elif isinstance(message, agents.CancelPayment) and role == 'ap':
                await agents.payment_cancel(ctx, source, message)
            elif isinstance(message, agents.RejectPayment) and vendor:
                await agents.seller_reject(ctx, source, message)
            elif isinstance(message, ChatMessage):
                self.replies.extend(c.text for c in message.content if isinstance(c, TextContent))
            handled += 1
            if handled > 200:
                raise RuntimeError('Message loop detected')
