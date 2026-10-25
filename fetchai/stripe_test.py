"""Optional Stripe TEST invoice adapter. Live keys and out-of-band paid flags forbidden."""
import httpx


async def pay_test_invoice(key, deal_id, annual_amount, client=None):
    if not isinstance(key,str) or not key.startswith(('sk_test_','rk_test_')):
        raise ValueError('Stripe test key required; live keys are forbidden')
    if type(annual_amount) is not int or not 1 <= annual_amount <= 999999:
        raise ValueError('Invalid test invoice amount')
    owned = client is None
    client = client or httpx.AsyncClient(timeout=20)
    async def post(path, step, data):
        response = await client.post('https://api.stripe.com/v1/'+path,
            auth=(key,''), headers={'Idempotency-Key':'counteragent-'+deal_id+'-'+step}, data=data)
        response.raise_for_status()
        value = response.json()
        if value.get('livemode') is not False:
            raise ValueError('Stripe object is not explicitly test mode')
        return value
    try:
        customer = await post('customers','customer',{'name':'CounterAgent FICTIONAL demo buyer','metadata[deal_id]':deal_id})
        method = await post('payment_methods/pm_card_visa/attach','method',{'customer':customer['id']})
        invoice = await post('invoices','invoice',{'customer':customer['id'], 'auto_advance':'false',
            'collection_method':'charge_automatically','default_payment_method':method['id'],
            'metadata[deal_id]':deal_id,'description':'FICTIONAL procurement demo, first annual period; TEST MODE'})
        await post('invoiceitems','item',{'customer':customer['id'],'invoice':invoice['id'],
            'amount':str(annual_amount*100),'currency':'usd','description':'First year, 250 seats; 24-month contract'})
        finalized = await post('invoices/'+invoice['id']+'/finalize','finalize',{'auto_advance':'false'})
        if finalized.get('amount_due') != annual_amount*100 or finalized.get('currency')!='usd':
            raise ValueError('Stripe invoice does not match the approved annual amount')
        paid = await post('invoices/'+invoice['id']+'/pay','pay',{'payment_method':method['id']})
        if (paid.get('id')!=invoice['id'] or paid.get('status')!='paid' or paid.get('amount_paid')!=annual_amount*100 or paid.get('currency')!='usd'):
            raise ValueError('Stripe test payment is not verified paid')
        return {'backend':'stripe_test','invoice_id':paid['id'],'status':'test_paid',
            'amount':annual_amount,'currency':'USD','livemode':False,'real_funds_moved':False,
            'hosted_invoice_url':paid.get('hosted_invoice_url')}
    finally:
        if owned:
            await client.aclose()
