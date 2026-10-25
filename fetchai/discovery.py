"""Public Agentverse search, capability challenges, and explicit onboarding gates."""
import asyncio
import secrets
from uuid import uuid4
import httpx
from supplier_protocol import CapabilityRequest,CapabilityResponse,PROTOCOL_NAME,verify_capability

SEARCH_URL='https://agentverse.ai/v1/search/agents'

async def marketplace_search(category='analytics_software',protocol_digest=None):
    async with httpx.AsyncClient(timeout=15) as client:
        payloads=[{'search_text':'analytics software supplier','filters':{'state':['active']},
            'limit':20,'sort':'relevancy','direction':'desc'}]
        if protocol_digest:payloads.append({'filters':{'state':['active'],'protocol_digest':[protocol_digest]},'limit':20})
        responses=await asyncio.gather(*(client.post(SEARCH_URL,json=p) for p in payloads))
        rows=[]
        for response in responses:
            response.raise_for_status()
            part=response.json().get('agents',[])
            if not isinstance(part,list):raise ValueError('Invalid discovery response')
            rows.extend(part)
    return list({a.get('address'):a for a in rows if isinstance(a,dict)}.values())[:40]

def eligibility(row,protocol_digest=None):
    if row.get('status')!='active':return 'Agent is not active'
    if row.get('unresponsive'):return 'Marketplace marks agent unresponsive'
    protocols=row.get('protocols',[])
    if not isinstance(protocols,list) or not any(p.get('name')==PROTOCOL_NAME or (protocol_digest and p.get('digest')==protocol_digest) for p in protocols if isinstance(p,dict)):
        return 'No compatible supplier negotiation protocol; chat or analytics capability alone is insufficient'
    if not isinstance(row.get('address'),str) or not row['address'].startswith('agent1'):
        return 'Invalid agent address'
    return None

async def discover(ctx,deal_id,known,emit,offline=False,allow_demo=True,protocol_digest=None,request_supplier=None):
    """known maps supplier keys to expected agent addresses, never private charters."""
    emit(deal_id,'orchestrator','discovery','discovery_search','Searching Agentverse for analytics software supplier agents',
        query='analytics software supplier',discovery_source=SEARCH_URL)
    search_error=None
    if offline:rows=[]
    else:
        try:rows=await marketplace_search(protocol_digest=protocol_digest)
        except Exception as error:
            rows=[];search_error=type(error).__name__
            emit(deal_id,'discovery','orchestrator','discovery_unavailable','Agentverse search unavailable',error=search_error)
    candidates=[]
    for row in rows:
        reason=eligibility(row,protocol_digest)
        item={k:row.get(k) for k in ('address','name','status','unresponsive')}
        item.update(source='agentverse_search',eligible=reason is None,reason=reason)
        candidates.append(item)
        emit(deal_id,'discovery','orchestrator','supplier_candidate',
            (row.get('name') or 'Unnamed agent')+': '+(reason or 'Compatible protocol advertised; challenge required'),candidate=item)
    # Demo fixtures are opt-in in the public request and labelled independently of search.
    if allow_demo:
        for key,address in known.items():
            if not any(c['address']==address and c['eligible'] for c in candidates):
                candidates.append({'address':address,'name':key,'source':'configured_demo_fixture',
                    'eligible':True,'reason':'Explicitly allowed fictional supplier fixture'})
    selected=[];onboarding=[]
    for candidate in [c for c in candidates if c['eligible']][:10]:
        address=candidate['address']
        request=CapabilityRequest(request_id=uuid4().hex,nonce=secrets.token_hex(24),
            category='analytics_software',seats=250,term_months=24,
            reply_via_mailbox=bool(request_supplier and address in known.values()))
        emit(deal_id,'orchestrator','discovery','capability_challenge','Requesting a signed, scoped supplier capability response',
            candidate_address=address,discovery_source=candidate['source'])
        try:
            if request_supplier and address in known.values():
                reply,_=await asyncio.wait_for(request_supplier(address,request),timeout=40)
            else:
                reply,_=await asyncio.wait_for(ctx.send_and_receive(address,request,CapabilityResponse,timeout=15),timeout=20)
            verified=verify_capability(request,reply,address)
        except Exception:verified=False;reply=None
        if not verified:
            emit(deal_id,'discovery','orchestrator','supplier_rejected','Supplier failed the signed scope/identity challenge',candidate_address=address)
            continue
        key=next((k for k,a in known.items() if a==address),None)
        item={'supplier_id':reply.supplier_id,'name':reply.company_name,'address':address,
            'source':candidate['source'],'identity_verified':True,'fictional_demo':reply.fictional_demo,
            'capability_transport':'agentverse_mailbox' if request.reply_via_mailbox else 'uagents',
            'corporate_authority_verified':False,'capability_receipt':reply.model_dump()}
        # New suppliers need real evidence, bank-master and signing-authority onboarding.
        # Never reuse another vendor's private charter, trust pack or payment destination.
        if key is None or reply.supplier_id!=key or not reply.fictional_demo or not allow_demo:
            item['status']='needs_supplier_onboarding';onboarding.append(item)
            emit(deal_id,'discovery','human','supplier_onboarding_required','Compatible supplier found; company authority, evidence and payment onboarding required',supplier=item)
        else:
            item.update(key=key,status='qualified_demo');selected.append(item)
            emit(deal_id,'discovery',key,'supplier_verified','Signed supplier scope verified; selected as a fictional demo counterparty',supplier=item)
    result={'candidates':candidates,'selected':selected,'onboarding_required':onboarding,
        'search_error':search_error,'demo_suppliers_allowed':allow_demo}
    emit(deal_id,'discovery','orchestrator','discovery_complete',f'{len(selected)} qualified demo suppliers; {len(onboarding)} require onboarding',
        selected=[{'key':s['key'],'name':s['name'],'address':s['address'],'source':s['source']} for s in selected])
    return result
