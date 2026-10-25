"""Allowlisted closing receipt for the read-only dashboard."""
from contracts import verify_signature

def closing_receipt(state, events):
    winner=state.get('result',{}).get('winner')
    if not winner:return None
    packet=state.get('ap',{}).get('signing_packet') or state.get('contract',{})
    bundle=packet.get('bundle',{})
    plan=bundle.get('order_form',{}).get('payment_plan',{})
    receipts=[]
    for role in ('buyer','vendor'):
        receipt=packet.get('signatures',{}).get(role,{})
        expected=next((e.get('signer','') for e in events if e['kind']=='document_signed'
                       and ((role=='buyer' and e['from']=='orchestrator') or
                            (role=='vendor' and e['from']==winner['vendor']+'.executive'))),'')
        receipts.append({'role':role,'name':'Acme · Buying company' if role=='buyer' else winner['name']+' · Supplier',
            'address':expected,'verified':bool(expected and verify_signature(bundle,receipt,expected,role)),
            'document_hash':receipt.get('document_hash',''),'signature':receipt.get('signature','')})
    payment=state.get('ap',{}).get('payment',{})
    committed=next((e for e in reversed(events) if e['kind']=='payment_commit'),None)
    completed=next((e for e in reversed(events) if e['kind']=='payment_complete'),None)
    revoked=max((e['seq'] for e in events if e['kind']=='approval_revoked'),default=0)
    approved=max((e['seq'] for e in events if e['kind']=='approval'),default=0)
    paid=(state.get('human_approved') is True and approved>revoked and
          all(r['verified'] for r in receipts) and state.get('ap',{}).get('matched') is True and
          payment.get('status')=='simulated_complete' and committed is not None and completed is not None
          and completed['seq']>committed['seq']>approved)
    return {'deal':state['id'],'status':state['status'],'winner':winner,
        'budget':state['budget'],'signatures':receipts,'document_url':state.get('document_url'),
        'alternatives':[{'name':o['name'],'price':o['price'],'implementation_days':o.get('implementation_days',7)}
                        for o in state.get('offers',[]) if o['vendor']!=winner['vendor']],
        'payment':{'simulated_paid':paid,'amount':plan.get('first_invoice_amount',winner['price']),
            'deposit':plan.get('deposit',0),'due_at_signature':plan.get('amount_due_at_signature',0),
            'terms_days':winner['payment_days'],'second_invoice_month':12,
            'transaction':completed['text'] if paid else '', 'real_funds_moved':False},
        'po':state.get('ap',{}).get('po'),'invoice':state.get('ap',{}).get('invoice'),
        'workspace':state.get('it',{}).get('manifest',{}).get('id')}
