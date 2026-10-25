import json
import unittest
import test_counteragent as base_tests
import agents
from policy import VENDORS,award
from negotiation import commercial_offer,award_explanation

class RemediationPolicyTests(unittest.TestCase):
    def test_head_to_head_both_vendors_can_clear_same_budget(self):
        offers=[commercial_offer(v,{'price':115000,'payment_days':45,'remediation':k=='quickdash','auto_renew':False},'head_to_head') for k,v in VENDORS.items()]
        self.assertTrue(all(not row['violations'] for row in award(offers,130000)['reviews']))

    def test_award_explanation_uses_actual_prices_and_authorized_cap(self):
        beacon=commercial_offer(VENDORS['beacon'],{'price':125000,'payment_days':45},'quickdash_value')
        quick=commercial_offer(VENDORS['quickdash'],{'price':121500,'payment_days':45,'remediation':True},'quickdash_value')
        text=award_explanation(quick,[beacon,quick],130000)
        self.assertIn('130,000',text)
        self.assertIn('3,500/year less',text)
        self.assertIn('21-day versus 7-day',text)
        self.assertNotIn('cannot be countersigned',text)

    def test_enterprise_fixes_controls_at_a_cost(self):
        base=commercial_offer(VENDORS['quickdash'],{'price':1,'payment_days':45},'quickdash_value')
        paid=commercial_offer(VENDORS['quickdash'],{'price':1,'payment_days':45,'remediation':True,'auto_renew':False},'quickdash_value')
        self.assertGreater(paid['price'],base['price'])
        self.assertEqual(paid['remediation_annual_cost'],12000)
        self.assertFalse(paid['trains_on_data'])
        self.assertEqual(paid['security_gaps'],[])
        self.assertIsNotNone(award([paid],120000)['winner'])

class NewFlows(unittest.IsolatedAsyncioTestCase):
    asyncSetUp=base_tests.WorkflowTests.asyncSetUp

    async def test_simple_demo_command_selects_opt_in_fixture(self):
        await self.bus.chat('security demo')
        s=next(iter(agents.sessions.values()))
        self.assertEqual(s['security_demo'],'invoice_change')
        self.assertEqual(s['budget'],130000)

    async def start_case(self,scenario='quickdash_value',demo='none'):
        await self.bus.chat(json.dumps({'budget':130000 if scenario=='beacon_value' else 120000,
            'scenario':scenario,'security_demo':demo}))
        await self.bus.drain()
        state=next(iter(agents.sessions.values()))
        self.assertEqual(state['status'],'awaiting_approval',str(state.get('reports')))
        return state

    async def test_quickdash_wins_with_paid_controls(self):
        s=await self.start_case()
        self.assertEqual(s['result']['winner']['vendor'],'quickdash')
        self.assertTrue(s['result']['winner']['remediation'])
        self.assertTrue(next(v for v in s['reviews']['security']['vendors'] if v['vendor']=='quickdash')['passed'])

    async def test_beacon_wins_when_remediation_is_expensive(self):
        s=await self.start_case('beacon_value')
        self.assertEqual(s['result']['winner']['vendor'],'beacon')
        self.assertTrue(next(v for v in s['reviews']['security']['vendors'] if v['vendor']=='quickdash')['passed'])

    async def security_flow(self,mode):
        s=await self.start_case(demo=mode)
        old_hash=s['approval']['hash']
        old_offer=dict(s['result']['winner'])
        await self.bus.chat(json.dumps({'action':'approve','deal_id':s['id'],'offer_hash':old_hash}))
        await self.bus.drain()
        self.assertEqual(s['status'],'awaiting_approval',str(s.get('reports')))
        self.assertFalse(s['human_approved'])
        self.assertEqual(s['approval_revision'],1)
        self.assertNotEqual(old_hash,s['approval']['hash'])
        self.assertNotEqual(old_offer,s['result']['winner'])
        self.assertNotIn('it',s['reports'])
        self.assertFalse(any(isinstance(m,agents.CommitPayment) for _,_,m in self.bus.deliveries))
        block=next(e for e in agents.audit if e['kind']=='security_block')
        self.assertEqual(block['vendor_address'],agents.vendor_executives['quickdash'].address)
        await self.bus.chat(json.dumps({'action':'approve','deal_id':s['id'],'offer_hash':old_hash}))
        await self.bus.drain()
        self.assertEqual(s['status'],'awaiting_approval')
        await self.bus.chat(json.dumps({'action':'approve','deal_id':s['id'],'offer_hash':s['approval']['hash']}))
        await self.bus.drain()
        self.assertEqual(s['status'],'closed',str(s.get('reports')))
        self.assertEqual(s['ap']['annual_amount'],s['result']['winner']['price'])
        self.assertEqual(s['ap']['payment']['status'],'simulated_complete')
        approvals=[e['seq'] for e in agents.audit if e['kind']=='approval']
        commits=[e['seq'] for e in agents.audit if e['kind']=='payment_commit']
        self.assertEqual(len(approvals),2)
        self.assertGreater(min(commits),max(approvals))

    async def test_invoice_change_blocks_then_requires_fresh_approval(self):
        await self.security_flow('invoice_change')

    async def test_terms_change_blocks_then_requires_fresh_approval(self):
        await self.security_flow('terms_change')

if __name__=='__main__':unittest.main()
