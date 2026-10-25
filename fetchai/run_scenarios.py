"""Real ASI calls through all review departments; queued transport, no approval/payment."""
import asyncio
import json
import sys
import agents
from harness import Bus
from negotiation import SCENARIOS

result_path=agents.ROOT/'.runtime'/'scenario-results.json'
results=json.loads(result_path.read_text(encoding='utf-8')) if len(sys.argv)>1 and result_path.exists() else []
limit=asyncio.Semaphore(1)

async def run(key):
    async with limit:
        bus=Bus()
        cfg=SCENARIOS[key]
        await bus.chat(json.dumps({'budget':cfg['budget'],'scenario':key,
            'objective':'Find analytics software for 250 employees. Negotiate with Beacon and Quickdash and recommend a vendor.'}),sender='scenario-'+key)
        await bus.drain()
        state=next(s for s in agents.sessions.values() if s['owner']=='scenario-'+key)
        winner=state.get('result',{}).get('winner')
        reason=('Compliant offer within budget; human approval still required.' if winner else
            'No offer met both the budget and non-waivable controls.' if state['status']=='walked_away' else
            'Execution failed: '+str({r:v.get('error') for r,v in state['reports'].items() if not v['ok']}))
        result={'scenario':key,'label':cfg['label'],'deal_id':state['id'],'status':state['status'],
            'budget':cfg['budget'],'winner':winner,'reason':reason,'metrics':state.get('negotiation_metrics',{}),
            'model_calls':state['model_calls'],'transport':'queued_harness','description':cfg['description']}
        results[:]=[r for r in results if r['scenario']!=key]
        results.append(result)
        path=agents.ROOT/'.runtime'/'scenario-results.json'
        temp=path.with_suffix('.tmp')
        temp.write_text(json.dumps(results,indent=2),encoding='utf-8')
        temp.replace(path)
        (agents.ROOT/'.runtime'/(state['id']+'-scenario.json')).write_text(json.dumps({'state':agents.public_state(state),'events':[e for e in agents.audit if e['deal_id']==state['id']]},indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=True),flush=True)
        if state['status'] not in ('awaiting_approval','walked_away'):
            raise RuntimeError(key+' failed: '+reason)

async def main():
    if agents.OFFLINE:raise RuntimeError('Live scenario suite requires ASI credentials')
    keys=sys.argv[1:] or list(SCENARIOS)
    if any(key not in SCENARIOS for key in keys):raise ValueError('Unknown scenario')
    outcomes=await asyncio.gather(*(run(key) for key in keys),return_exceptions=True)
    if any(isinstance(o,Exception) for o in outcomes):raise RuntimeError('Some scenarios failed; see recorded results')

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    asyncio.run(main())
