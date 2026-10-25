import copy
import unittest
from advisers import brief,consult,ADVISERS
from slack_bridge import allowed_action
from uagents_core.contrib.protocols.chat import ChatMessage,TextContent

class Boundaries(unittest.TestCase):
    def test_external_brief_excludes_private_company_and_vendor_data(self):
        data=brief([{'vendor':'beacon','name':'Beacon','price':121000,'floor':106000,
            'bank_account':'secret','payroll':'secret','private_memory':'secret','seats':250}],130000)
        offer=data['offers'][0]
        self.assertEqual(offer,{'vendor':'beacon','name':'Beacon','price':121000,'seats':250})

    def test_slack_rejects_wrong_identity_channel_team_snapshot_or_message(self):
        binding={'message_ts':'1.2','approval_hash':'abc'}
        payload={'type':'block_actions','team':{'id':'T1'},'channel':{'id':'C1'},'user':{'id':'U1'},
            'message':{'ts':'1.2'},'actions':[{'action_id':'counteragent_approve','value':'abc'}]}
        self.assertTrue(allowed_action(payload,binding,'T1','C1',{'U1'}))
        for path,value in [(('team','id'),'T2'),(('channel','id'),'C2'),(('user','id'),'U2'),(('message','ts'),'1.3')]:
            changed=copy.deepcopy(payload);changed[path[0]][path[1]]=value
            self.assertFalse(allowed_action(changed,binding,'T1','C1',{'U1'}))
        payload['actions'][0]['value']='stale'
        self.assertFalse(allowed_action(payload,binding,'T1','C1',{'U1'}))

class OptionalAdvisers(unittest.IsolatedAsyncioTestCase):
    async def test_independent_replies_recorded_and_timeout_not_fabricated(self):
        class Context:
            async def send_and_receive(self,address,*args,**kwargs):
                if address==ADVISERS['azwin']:return ChatMessage(content=[TextContent(type='text',text='Check rollout evidence')]),None
                raise TimeoutError()
        events=[]
        def emit(*args,**kwargs):events.append((args,kwargs))
        rows=await consult(Context(),[],120000,emit,'123456789abc')
        self.assertEqual([r['status'] for r in rows],['responded','unavailable'])
        self.assertEqual(sum(a[0][3]=='adviser_response' for a in events),1)
        self.assertEqual(sum(a[0][3]=='adviser_unavailable' for a in events),1)
