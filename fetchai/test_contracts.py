import copy
import unittest
import test_counteragent
import agents
from contracts import unsigned_bundle,sign_bundle,verify_packet,payment_plan
from negotiation import commercial_offer
from policy import VENDORS

class SignatureTests(unittest.TestCase):
    def packet(self):
        offer=commercial_offer(VENDORS['beacon'],{'price':120000,'payment_days':45},'baseline')
        bundle=unsigned_bundle('123456789abc',offer)
        return {'bundle':bundle,'signatures':{'buyer':sign_bundle(agents.buyer,bundle,'buyer'),
            'vendor':sign_bundle(agents.vendor_executives['beacon'],bundle,'vendor')}}

    def test_both_signatures_verify_and_edit_invalidates(self):
        p=self.packet()
        self.assertTrue(verify_packet(p,agents.buyer.address,agents.vendor_executives['beacon'].address))
        p['bundle']['order_form']['annual_subscription_fee']+=1
        self.assertFalse(verify_packet(p,agents.buyer.address,agents.vendor_executives['beacon'].address))

    def test_wrong_signer_missing_signature_and_new_revision_fail(self):
        p=self.packet()
        self.assertFalse(verify_packet(p,agents.buyer.address,agents.vendor_executives['quickdash'].address))
        p['bundle']['revision']=1
        self.assertFalse(verify_packet(p,agents.buyer.address,agents.vendor_executives['beacon'].address))
        p=self.packet();p['signatures'].pop('buyer')
        self.assertFalse(verify_packet(p,agents.buyer.address,agents.vendor_executives['beacon'].address))

    def test_payment_plan_is_two_annual_invoices_not_deposit(self):
        p=self.packet()['bundle']['order_form']['payment_plan']
        self.assertEqual(p['deposit'],0)
        self.assertEqual(p['amount_due_at_signature'],0)
        self.assertEqual(sum(i['amount'] for i in p['invoices']),240000)
        self.assertEqual(p['invoices'][1]['invoice_month'],12)

class SigningFlow(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=test_counteragent.WorkflowTests.asyncSetUp
    async def test_modified_vendor_signature_blocks_payment(self):
        await self.bus.chat('{"budget":120000}')
        await self.bus.drain()
        state=next(iter(agents.sessions.values()))
        def corrupt(message):
            if isinstance(message,agents.EvidenceReply) and message.purpose=='ap':
                message.evidence['signing_packet']['signatures']['vendor']['signature']='invalid'
            return message
        self.bus.transform=corrupt
        await self.bus.chat('approve '+state['id']);await self.bus.drain()
        self.assertEqual(state['status'],'error')
        self.assertFalse(any(isinstance(m,agents.CommitPayment) for _,_,m in self.bus.deliveries))
        self.assertNotIn('it',state['reports'])
