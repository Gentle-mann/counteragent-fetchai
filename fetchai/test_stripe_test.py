import unittest
import httpx
from stripe_test import pay_test_invoice

class StripeTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_key_rejected_without_network(self):
        with self.assertRaises(ValueError):await pay_test_invoice('sk_live_not-a-key','demo',114000)

    async def test_invoice_mismatch_cannot_be_paid(self):
        paths=[]
        def respond(request):
            paths.append(request.url.path)
            value={'id':'in_test','livemode':False}
            if request.url.path.endswith('/finalize'):
                value.update(amount_due=1,currency='usd')
            return httpx.Response(200,json=value)
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            with self.assertRaises(ValueError):await pay_test_invoice('sk_test_fake','demo',114000,client)
        self.assertFalse(any(p.endswith('/pay') for p in paths))

    async def test_success_requires_verified_test_paid_response(self):
        calls=[]
        def respond(request):
            calls.append(request)
            value={'id':'in_test','livemode':False,'amount_due':11400000,'amount_paid':11400000,'currency':'usd','status':'paid'}
            return httpx.Response(200,json=value)
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            result=await pay_test_invoice('sk_test_fake','demo',114000,client)
        self.assertEqual(result['status'],'test_paid')
        self.assertFalse(result['real_funds_moved'])
        self.assertTrue(all('paid_out_of_band' not in str(r.content) for r in calls))
        self.assertEqual(len(calls),6)

if __name__=='__main__':unittest.main()
