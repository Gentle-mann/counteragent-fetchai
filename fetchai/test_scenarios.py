import unittest
from company_data import records,department_context,tools
from negotiation import commercial_offer,reservation,buyer_comparison,decision_explanation
from policy import VENDORS,award

class CompanyDataTests(unittest.TestCase):
    def test_roster_usage_budget_and_growth_reconcile(self):
        d=records()
        self.assertEqual(len(d['employees']),250)
        self.assertEqual(sum(p['analytics_active_30d'] for p in d['employees']),212)
        self.assertEqual(sum(p['region']=='EU' for p in d['employees']),64)
        self.assertEqual(sum(r['seats'] for r in d['department_budgets']),250)
        self.assertEqual(sum(r['annual_allocation'] for r in d['department_budgets']),120000)

    def test_department_access_is_scoped(self):
        self.assertNotIn('cash_forecast',department_context('security')['records'])
        self.assertNotIn('vendor_master',department_context('research')['records'])
        self.assertNotIn('employees',department_context('procurement')['records'])

    def test_it_detects_eight_stale_directory_entries(self):
        _,result=tools('it',{})
        self.assertEqual(len(result['missing_from_legacy']),8)
        self.assertEqual(result['pilot_seats']+result['rollout_seats'],250)

    def test_ap_does_not_adopt_unverified_bank_change(self):
        _,result=tools('ap',{'winner':{'vendor':'beacon'}})
        self.assertEqual(result['approved_bank_last4'],'4417')
        self.assertEqual(result['unverified_bank_changes'],['AP-481'])

class CommercialTests(unittest.TestCase):
    def test_cash_pressure_changes_the_price_payment_frontier(self):
        v=VENDORS['beacon']
        a=commercial_offer(v,{'price':1,'payment_days':45},'cash_pressure')
        b=commercial_offer(v,{'price':1,'payment_days':60},'cash_pressure')
        self.assertEqual(a['price'],116500)
        self.assertEqual(b['price'],125500)
        self.assertIsNotNone(award([a],120000)['winner'])
        self.assertIsNone(award([b],120000)['winner'])

    def test_capacity_opportunity_cost_can_make_walkaway_correct(self):
        offers=[commercial_offer(v,{'price':1,'payment_days':45},'capacity_crunch') for v in VENDORS.values()]
        self.assertIsNone(award(offers,120000)['winner'])

    def test_buyer_does_not_overvalue_longer_payment_terms(self):
        comparisons=buyer_comparison([{'price':116500,'payment_days':45},{'price':125500,'payment_days':60}],120000)
        self.assertLess(comparisons[0]['effective_annual_cost'],comparisons[1]['effective_annual_cost'])

    def test_cheap_price_does_not_purchase_missing_security(self):
        offer=commercial_offer(VENDORS['quickdash'],{'price':1,'payment_days':60},'baseline')
        self.assertEqual(offer['payment_days'],30)
        self.assertTrue(offer['trains_on_data'])
        self.assertTrue(offer['security_gaps'])

    def test_explanation_attributes_cash_pressure_to_correct_company(self):
        offer=commercial_offer(VENDORS['quickdash'],{'price':114000,'payment_days':30},'cash_pressure')
        explanation=decision_explanation(offer,'cash_pressure')
        self.assertNotIn('Working-capital pressure',explanation)
        self.assertIn('fails',explanation)

if __name__=='__main__':unittest.main()
