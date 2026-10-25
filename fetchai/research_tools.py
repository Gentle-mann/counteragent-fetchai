"""ASI hosted search, with explicit search-call provenance and no mandate data."""
import asyncio


async def public_research(client, model):
    response = await asyncio.wait_for(client.responses.create(model=model,
        input='Search primary official sources for enterprise analytics procurement security questions about EU data residency, SCIM and customer-data training. '
              'Return a short summary with source URLs. Our vendors Beacon and Quickdash are fictional: do not search or make claims about them. '
              'This is background research, never vendor compliance evidence.',
        tools=[{'type':'web_search','search_context_size':'low'}], max_output_tokens=1000), timeout=45)
    output = response.model_dump()
    searches = [item for item in output.get('output',[]) if item.get('type')=='web_search_call']
    citations = []
    text = []
    for item in output.get('output',[]):
        if item.get('type') != 'message':
            continue
        for part in item.get('content',[]):
            if part.get('type')=='output_text':
                text.append(part.get('text',''))
                citations.extend(a.get('url') for a in part.get('annotations',[]) if a.get('type')=='url_citation' and a.get('url'))
    return {'summary':'\n'.join(text)[:5000], 'search_calls': searches,
        'verified_response_citations': citations, 'status': 'searched' if any(s.get('status')=='completed' for s in searches) else 'no_search_record',
        'scope':'Public background only; not proof about a fictional vendor.'}
