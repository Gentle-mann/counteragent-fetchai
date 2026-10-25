import unittest
from unittest.mock import patch
import test_counteragent
import agents
import httpx,json
from uuid import uuid4
from mailbox_rpc import mailbox_send
from discovery import discover,eligibility
from supplier_protocol import CapabilityRequest,CapabilityResponse,capability_body,verify_capability,PROTOCOL_VERSION,PROTOCOL_NAME
from intake import scope_error

class DiscoveryTests(unittest.TestCase):
    def test_chat_agent_is_not_a_supplier(self):
        self.assertIn('protocol',eligibility({'status':'active','address':agents.buyer.address,
            'protocols':[{'name':'AgentChatProtocol'}]}))

    def test_inactive_and_unresponsive_rejected(self):
        self.assertIsNotNone(eligibility({'status':'inactive'}))
        self.assertIsNotNone(eligibility({'status':'active','unresponsive':True}))

    def test_signed_capability_bound_to_nonce_scope_and_identity(self):
        a=agents.vendors['beacon']
        q=CapabilityRequest(request_id='request',nonce='challenge',category='analytics_software',seats=250,term_months=24)
        r=CapabilityResponse(request_id=q.request_id,nonce=q.nonce,supplier_id='beacon',company_name='Beacon',agent_address=a.address,
            category=q.category,seats=250,term_months=24,currency='USD',can_quote=True,fictional_demo=True,protocol_version=PROTOCOL_VERSION)
        r.signature=a.sign_digest(bytes.fromhex(agents.digest(capability_body(r))))
        self.assertTrue(verify_capability(q,r,a.address))
        self.assertFalse(verify_capability(q,r,agents.vendors['quickdash'].address))
        r.nonce='replay'
        self.assertFalse(verify_capability(q,r,a.address))

    def test_wrong_category_quantity_currency_and_billing_are_not_substituted(self):
        for intent in [{'category':'other'},{'category':'unknown'},{'seats':40},{'term_months':12},
            {'currency':'EUR'},{'billing_basis':'one_time'},{'role':'seller'}]:
            self.assertIsNotNone(scope_error(intent))

class DiscoveryFlows(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=test_counteragent.WorkflowTests.asyncSetUp

    async def test_demo_fixtures_have_actual_signed_challenges(self):
        result=await discover(self.bus.context(agents.buyer.address),'123456789abc',
            {k:a.address for k,a in agents.vendors.items()},agents.event,offline=True,allow_demo=True)
        self.assertEqual({s['key'] for s in result['selected']},{'beacon','quickdash'})
        self.assertTrue(all(s['source']=='configured_demo_fixture' for s in result['selected']))
        self.assertEqual(sum(isinstance(m,CapabilityRequest) for _,_,m in self.bus.deliveries),2)

    async def test_mailbox_envelope_is_signed_and_serializable(self):
        received=[]
        def transport(request):
            received.append(json.loads(request.content))
            return httpx.Response(200,json={})
        original=httpx.AsyncClient
        q=CapabilityRequest(request_id='probe',nonce='nonce',category='analytics_software',seats=250,term_months=24)
        with patch('mailbox_rpc.httpx.AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(transport),**kwargs)):
            await mailbox_send(agents.buyer,agents.vendors['beacon'].address,q,uuid4())
        self.assertTrue(received[0]['signature'])
        self.assertEqual(received[0]['target'],agents.vendors['beacon'].address)

    async def test_no_silent_fallback_when_demo_suppliers_disabled(self):
        await self.bus.chat('{"budget":120000,"allow_demo_suppliers":false}')
        await self.bus.drain()
        s=next(iter(agents.sessions.values()))
        self.assertEqual(s['status'],'no_compatible_suppliers')
        self.assertNotIn('procurement',s['reports'])
        self.assertNotIn('contract',s)

    async def test_other_product_never_starts_analytics_team(self):
        await self.bus.chat('{"budget":120000,"objective":"Office furniture","category":"other"}')
        await self.bus.drain()
        self.assertFalse(agents.sessions)

    async def test_external_buyer_cannot_replace_another_buyers_quote(self):
        agents.external_quote_limits.clear()
        original={'price':123456}
        agents.vendor_quotes[('123456789abc','beacon')]=original.copy()
        request=agents.Rfp(deal_id='123456789abc',round=2,target_price=1,previous_price=1,message='External quote',scenario='capacity_crunch')
        await agents.vendor_handler('beacon')(self.bus.context(agents.vendors['beacon'].address),'independent-buyer',request)
        self.assertEqual(agents.vendor_quotes[('123456789abc','beacon')],original)
        self.assertFalse(any(e['deal_id']=='123456789abc' for e in agents.audit))
        self.assertEqual(request.scenario,'baseline')

    async def test_public_quote_rate_limit_precedes_model_work(self):
        agents.external_quote_limits.clear()
        for _ in range(4):
            q=agents.Rfp(deal_id='123456789abc',round=0,target_price=120000,previous_price=150000,message='Public quote')
            await agents.vendor_handler('beacon')(self.bus.context(agents.vendors['beacon'].address),'rate-test-buyer',q)
        self.assertIn('rate limit',self.bus.queue[-1][2].message)

    async def test_external_compatible_agent_requires_onboarding(self):
        remote=agents.vendor_trust['beacon']
        async def search(*args,**kwargs):return [{'status':'active','address':remote.address,'name':'Independent supplier',
            'protocols':[{'name':PROTOCOL_NAME}]}]
        class Context:
            async def send_and_receive(self,address,q,response_type,**kwargs):
                r=CapabilityResponse(request_id=q.request_id,nonce=q.nonce,supplier_id='independent',company_name='Independent',
                    agent_address=address,category=q.category,seats=250,term_months=24,currency='USD',can_quote=True,
                    fictional_demo=False,protocol_version=PROTOCOL_VERSION)
                r.signature=remote.sign_digest(bytes.fromhex(agents.digest(capability_body(r))))
                return r,None
        with patch('discovery.marketplace_search',search):
            result=await discover(Context(),'123456789abc',{},agents.event,offline=False,allow_demo=False)
        self.assertEqual(result['selected'],[])
        self.assertEqual(result['onboarding_required'][0]['status'],'needs_supplier_onboarding')
        self.assertFalse(result['onboarding_required'][0]['corporate_authority_verified'])
