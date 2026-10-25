import unittest
from unittest.mock import AsyncMock, patch
import test_counteragent
import agents


class AdvisoryHandoffs(unittest.IsolatedAsyncioTestCase):
    async def test_retry_once_then_advance_sequentially(self):
        deal='abcdef123456'
        state={'id':deal,'status':'reviewing','tasks':{},'model_calls':0,
               '_ctx':object(),'external_advice':[],'offers':[],'budget':130000,
               'reviews':{},'advisory_reviews':{}}
        agents.pending[deal]=state
        async def report(task_id, ok):
            state['tasks'][task_id]={'role':'finance','action':'advisory_review','done':False}
            await agents.on_report(None,agents.departments['finance'].address,
                agents.Report(deal_id=deal,task_id=task_id,role='finance',ok=ok,
                              data={},model_used=False,error='' if ok else 'timeout'))
        try:
            with patch.object(agents,'assign',new_callable=AsyncMock) as assign:
                await report('first',False)
                self.assertEqual(assign.call_args.args[2],'finance')
                self.assertEqual(state['advisory_reviews'],{})
                await report('second',False)
                self.assertEqual(assign.call_args.args[2],'legal')
                self.assertIn('error',state['advisory_reviews']['finance'])
                self.assertEqual(assign.await_count,2)
        finally:
            agents.pending.pop(deal,None)

    def test_review_payload_excludes_full_department_evidence(self):
        payload=agents.advisory_payload({'external_advice':[],'offers':[],'budget':130000,
            'reviews':{'legal':{'vendors':[{'vendor':'beacon','passed':True}],
                                'summary':'x'*4000,'evidence':'unneeded repeated full document'}}})
        self.assertNotIn('evidence',payload['reviews']['legal'])
        self.assertEqual(len(payload['reviews']['legal']['summary']),1200)
