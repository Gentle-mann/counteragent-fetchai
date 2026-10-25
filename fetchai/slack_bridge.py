"""Opt-in Slack Socket Mode approval adapter. No public callback endpoint."""
import asyncio
import json
import os
import aiohttp

def configured():
    return all(os.getenv(k) for k in ('SLACK_BOT_TOKEN','SLACK_APP_TOKEN','SLACK_TEAM_ID','SLACK_CHANNEL_ID','SLACK_APPROVER_IDS'))

def allowed_action(payload,binding,team,channel,approvers):
    actions=payload.get('actions',[])
    return (payload.get('type')=='block_actions' and payload.get('team',{}).get('id')==team
        and payload.get('channel',{}).get('id')==channel
        and payload.get('user',{}).get('id') in approvers
        and payload.get('message',{}).get('ts')==binding.get('message_ts')
        and len(actions)==1 and actions[0].get('action_id') in ('counteragent_approve','counteragent_cancel')
        and actions[0].get('value')==binding.get('approval_hash'))

class SlackBridge:
    def __init__(self,submit,emit):
        self.submit,self.emit=submit,emit
        self.bindings={}

    async def api(self,method,payload,app=False):
        token=os.environ['SLACK_APP_TOKEN' if app else 'SLACK_BOT_TOKEN']
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post('https://slack.com/api/'+method,json=payload,
                headers={'Authorization':'Bearer '+token}) as response:
                body=await response.json()
                if not body.get('ok'):raise RuntimeError('Slack request failed: '+str(body.get('error','unknown')))
                return body

    async def request(self,state):
        if not configured():return False
        offer=state['result']['winner'];hashed=state['approval']['hash']
        text=f"FICTIONAL CounterAgent approval · {state['id']} · {offer['name']} · USD {offer['price']:,}/year · 24 months · 250 seats. No real payment or legal commitment."
        blocks=[{'type':'section','text':{'type':'plain_text','text':text}},
            {'type':'section','text':{'type':'plain_text','text':'Documents: http://127.0.0.1:8060'+state['document_url']}},
            {'type':'actions','elements':[{'type':'button','action_id':'counteragent_'+action,
                'text':{'type':'plain_text','text':label},'value':hashed} for action,label in [('approve','Approve demo signing'),('cancel','Cancel')]]}]
        result=await self.api('chat.postMessage',{'channel':os.environ['SLACK_CHANNEL_ID'],'text':text,'blocks':blocks})
        self.bindings[state['id']]={'message_ts':result['ts'],'approval_hash':hashed,'state':state}
        self.emit(state['id'],'orchestrator','human','slack_approval_requested','Approval posted to the configured Slack channel',channel=os.environ['SLACK_CHANNEL_ID'])
        return True

    async def handle(self,payload):
        binding=next((b for b in self.bindings.values() if b['message_ts']==payload.get('message',{}).get('ts')),None)
        if not binding:return False
        if not allowed_action(payload,binding,os.environ['SLACK_TEAM_ID'],os.environ['SLACK_CHANNEL_ID'],set(os.environ['SLACK_APPROVER_IDS'].split(','))):return False
        state=binding['state']
        if state['status']!='awaiting_approval' or state['approval']['hash']!=binding['approval_hash']:return False
        action=payload['actions'][0]['action_id'].removeprefix('counteragent_')
        self.emit(state['id'],'human','orchestrator','slack_action','Authorized Slack human requested '+action,
            slack_user=payload['user']['id'])
        await self.submit(state,action,binding['approval_hash'])
        return True

    async def run(self):
        if not configured():return
        while True:
            try:
                opened=await self.api('apps.connections.open',{},app=True)
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(opened['url'],heartbeat=20) as ws:
                        async for message in ws:
                            if message.type!=aiohttp.WSMsgType.TEXT:continue
                            envelope=json.loads(message.data)
                            if envelope.get('envelope_id'):await ws.send_json({'envelope_id':envelope['envelope_id']})
                            if envelope.get('type')=='interactive':await self.handle(envelope.get('payload',{}))
                            if envelope.get('type')=='disconnect':break
            except Exception:
                await asyncio.sleep(5)
