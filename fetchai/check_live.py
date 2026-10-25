"""Real ASI calls through all departments; queued transport, not network."""
import asyncio
import sys
import json
import agents
from harness import Bus
from benchmark import evaluate


async def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if agents.OFFLINE:
        raise RuntimeError('Unset COUNTERAGENT_OFFLINE for live check')
    bus = Bus()
    await bus.chat('Run a demo: find analytics software for 250 employees for 24 months, spending no more than $120,000 per year in USD.')
    await bus.drain()
    if not agents.sessions:
        raise RuntimeError('Live intake failed')
    state = next(iter(agents.sessions.values()))
    print('Review outcome:', state['status'], flush=True)
    if state['status'] != 'awaiting_approval':
        for reply in bus.replies:
            print(reply)
        raise RuntimeError('No offer ready for approval')
    await bus.chat('approve ' + state['id'])
    await bus.drain()
    print('Final status:', state['status'])
    print('Departments:', ', '.join(state['reports']))
    print('ASI calls:', state['model_calls'])
    print('Transport messages:', len(bus.deliveries))
    print('Negotiation evaluation:', json.dumps(evaluate(state), indent=2))
    (agents.ROOT / '.runtime' / 'live-check.json').write_text(
        json.dumps({'state': agents.public_state(state), 'audit': agents.audit}, indent=2), encoding='utf-8')
    for reply in bus.replies:
        print(reply)
    assert state['status'] == 'closed'
    assert set(state['reports']) == set(agents.DEPARTMENTS)
    assert all(r['model_used'] for r in state['reports'].values())


if __name__ == '__main__':
    asyncio.run(main())
