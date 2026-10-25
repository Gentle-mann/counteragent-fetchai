import os
import unittest
from unittest.mock import patch
from uuid import uuid4

os.environ['COUNTERAGENT_OFFLINE'] = '1'
os.environ['COUNTERAGENT_SEED'] = 'counteragent-local-test-only'
from policy import VENDORS, enforce, award, validate_budget
import agents
from harness import Bus
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent


class PolicyTests(unittest.TestCase):
    def test_floor_discount_and_terms_enforced(self):
        offer = enforce(VENDORS['beacon'], {'price': 1, 'payment_days': 999})
        self.assertEqual(offer['price'], 112500)
        self.assertEqual(offer['payment_days'], 60)

    def test_cheaper_unsafe_vendor_cannot_win(self):
        offers = [enforce(v, {'price': 1, 'payment_days': 60}) for v in VENDORS.values()]
        self.assertEqual(award(offers, 120000)['winner']['vendor'], 'beacon')
        self.assertIsNone(award(offers, 100000)['winner'])

    def test_invalid_budget_rejected(self):
        for value in [True, float('nan'), float('inf'), -1, '120000', None]:
            with self.assertRaises(ValueError):
                validate_budget(value)


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        for collection in (agents.sessions, agents.pending, agents.procurements, agents.seen, agents.payables, agents.invoices):
            collection.clear()
        agents.audit.clear()
        self.bus = Bus()

    async def start(self, budget=120000):
        await self.bus.chat('{"budget":%d}' % budget)
        await self.bus.drain()
        return next(iter(agents.sessions.values()))

    async def test_seven_departments_complete_gated_handoffs(self):
        state = await self.start()
        self.assertEqual(state['status'], 'awaiting_approval')
        self.assertEqual(set(state['reports']), {'research', 'procurement', 'security', 'legal', 'finance'})
        self.assertNotIn('ap', state['reports'])
        with patch.object(agents.ROOT.__class__, 'write_text') as write:
            await self.bus.chat('approve ' + state['id'])
            await self.bus.drain()
            self.assertTrue(state['ap']['signing_packet']['signatures']['buyer'])
            self.assertTrue(state['ap']['signing_packet']['signatures']['vendor'])
        self.assertEqual(state['status'], 'closed')
        self.assertEqual(set(state['reports']), set(agents.DEPARTMENTS))
        self.assertTrue(state['ap']['matched'])
        self.assertEqual(state['it']['manifest']['status'], 'simulated')
        completed = [e for e in agents.audit if e['kind'] == 'sent' and e['text'] == 'Report']
        self.assertEqual({e['from'] for e in completed}, set(agents.DEPARTMENTS))

    async def test_counteroffer_rounds_for_both_vendors(self):
        state = await self.start()
        for vendor, history in state['reports']['procurement']['data']['negotiations'].items():
            self.assertEqual([h['by'] for h in history], [vendor, 'procurement', vendor, 'procurement', vendor])
            self.assertEqual([h['round'] for h in history], [0, 1, 1, 2, 2])

    async def test_legal_receives_security_findings(self):
        state = await self.start()
        messages = self.bus.deliveries
        security = next(i for i, (_, _, m) in enumerate(messages) if isinstance(m, agents.Report) and m.role == 'security')
        legal_index, legal_task = next((i, m) for i, (_, to, m) in enumerate(messages)
            if to == agents.departments['legal'].address and isinstance(m, agents.Task))
        self.assertGreater(legal_index, security)
        self.assertIn('security_review', legal_task.payload)
        # Paid Enterprise now clears Legal; the baseline package exceeds this mandate's budget.
        self.assertTrue(next(v for v in state['reviews']['legal']['vendors'] if v['vendor'] == 'quickdash')['passed'])
        self.assertFalse(next(v for v in state['reviews']['finance']['vendors'] if v['vendor'] == 'quickdash')['passed'])

    async def test_walk_away_cannot_be_approved(self):
        state = await self.start(100000)
        self.assertEqual(state['status'], 'walked_away')
        await self.bus.chat('approve ' + state['id'])
        await self.bus.drain()
        self.assertNotIn('ap', state['reports'])

    async def test_owner_only_approval_across_sessions(self):
        state = await self.start()
        await self.bus.chat('approve ' + state['id'], sender='attacker')
        await self.bus.drain()
        self.assertEqual(state['status'], 'awaiting_approval')
        with patch.object(agents.ROOT.__class__, 'write_text'):
            await self.bus.chat('approve ' + state['id'], session=uuid4())
            await self.bus.drain()
        self.assertEqual(state['status'], 'closed')

    async def test_asi_recipient_mention_does_not_break_approval(self):
        state = await self.start()
        with patch.object(agents.ROOT.__class__, 'write_text'):
            await self.bus.chat('@' + agents.buyer.address + ' approve ' + state['id'])
            await self.bus.drain()
        self.assertEqual(state['status'], 'closed')

    async def test_review_card_selection_runs_payment_before_it(self):
        import json
        state = await self.start()
        with patch.object(agents.ROOT.__class__, 'write_text'):
            await self.bus.chat(json.dumps({'action': 'approve', 'deal_id': state['id']}))
            await self.bus.drain()
        payment = state['ap']['payment']
        self.assertEqual(payment['status'], 'simulated_complete')
        self.assertFalse(payment['settled'])
        types = [type(m) for _, _, m in self.bus.deliveries]
        self.assertLess(types.index(agents.RequestPayment), types.index(agents.CommitPayment))
        self.assertLess(types.index(agents.CommitPayment), types.index(agents.CompletePayment))
        complete = next(i for i, (_, _, m) in enumerate(self.bus.deliveries) if isinstance(m, agents.CompletePayment))
        it_task = next(i for i, (_, to, m) in enumerate(self.bus.deliveries)
                      if to == agents.departments['it'].address and isinstance(m, agents.Task))
        self.assertLess(complete, it_task)

    async def test_payment_amount_mismatch_blocks_it(self):
        state = await self.start()
        def corrupt(message):
            if isinstance(message, agents.RequestPayment):
                message.accepted_funds[0].amount = '99999999'
            return message
        self.bus.transform = corrupt
        await self.bus.chat('approve ' + state['id'])
        await self.bus.drain()
        self.assertEqual(state['status'], 'error')
        self.assertNotIn('it', state['reports'])

    async def test_duplicate_chat_does_not_launch_another_team(self):
        msg = ChatMessage(content=[TextContent(type='text', text='{"budget":120000}')])
        await self.bus.chat_message(msg)
        await self.bus.chat_message(msg)
        await self.bus.drain()
        self.assertEqual(len(agents.sessions), 1)

    async def test_forged_department_report_ignored(self):
        await self.bus.chat('{"budget":120000}')
        state = next(iter(agents.sessions.values()))
        task_id = next(iter(state['tasks']))
        report = agents.Report(deal_id=state['id'], task_id=task_id, role='research', ok=True, data={}, model_used=False)
        await agents.on_report(self.bus.context(agents.buyer.address), 'attacker', report)
        self.assertFalse(state['tasks'][task_id]['done'])

    async def test_model_failure_stops_instead_of_faking_a_department(self):
        async def fail(*args, **kwargs):
            raise RuntimeError('model unavailable')
        with patch.object(agents, 'decide', fail):
            state = await self.start()
        self.assertEqual(state['status'], 'error')
        self.assertNotIn(state['id'], agents.pending)

    async def test_cancel_ignores_late_reports(self):
        await self.bus.chat('{"budget":120000}')
        state = next(iter(agents.sessions.values()))
        await self.bus.chat('cancel ' + state['id'])
        await self.bus.drain()
        self.assertEqual(state['status'], 'cancelled')
        self.assertNotIn('ap', state['reports'])


if __name__ == '__main__':
    unittest.main()
