"""Synthetic commercial data and executable multi-attribute reservation policies."""
from dataclasses import asdict, replace
import math
from policy import enforce, finite

SCENARIOS = {
    'head_to_head': {'label':'Head-to-head: both compliant and affordable','budget':130000,
        'description':'Quickdash has a discounted Enterprise package; Beacon has normal capacity. Both have room to close within budget, so negotiated total price and rollout speed decide.'},
    'beacon_value': {'label':'Beacon wins on included controls','budget':130000,
        'description':'Both can comply. Quickdash pays full enterprise remediation cost; Beacon already operates the required controls.'},
    'quickdash_value': {'label':'Quickdash wins after paid remediation','budget':120000,
        'description':'Quickdash has a subsidized enterprise rollout and available capacity; Beacon has a scarce implementation slot.'},
    'baseline': {'label':'Normal quarter', 'budget':120000,
        'description':'Normal capacity and cash: compare price against the value of longer payment terms.'},
    'cash_pressure': {'label':'Vendor cash squeeze', 'budget':120000,
        'description':'Beacon has a working-capital squeeze. Net 60 costs more; net 45 may unlock a compliant deal.'},
    'capacity_crunch': {'label':'Implementation capacity scarce', 'budget':120000,
        'description':'Beacon has one implementation slot left and a profitable alternative customer. Walking away may be correct.'},
    'tight_budget': {'label':'No feasible budget', 'budget':100000,
        'description':'A lower price cannot compensate for missing security controls. Test a principled walk-away.'},
}

def remediation_cost(scenario):
    return 12000 if scenario in ('quickdash_value','head_to_head') else 30000

def effective_vendor(vendor, proposed, scenario):
    if vendor.key!='quickdash' or not proposed.get('remediation',False):
        return vendor
    cost=remediation_cost(scenario)
    return replace(vendor,list_price=vendor.list_price+cost,floor=vendor.floor+cost,
        max_payment_days=60,requires_renewal=False,min_uplift=3,liability_months=12,
        trains_on_data=False,security_gaps=())

def private_data(vendor, scenario):
    if scenario not in SCENARIOS:
        raise ValueError('Unknown scenario')
    beacon = vendor.key == 'beacon'
    return {'charter':asdict(vendor), 'synthetic':True,
        'annual_delivery_cost':72000 if beacon else 61000,
        'implementation_cost':14000 if beacon else 9000,
        'support_hours_per_year':240 if beacon else 140,
        'gross_margin_target_pct':35 if beacon else 30,
        'quota_attainment_pct':82 if beacon else 58,
        'implementation_slots_remaining':1 if scenario in ('capacity_crunch','quickdash_value') and beacon else 6,
        'opportunity_cost_premium':12500 if scenario in ('capacity_crunch','quickdash_value') and beacon else 0,
        'working_capital_premium_net45':4000 if scenario=='cash_pressure' and beacon else 0,
        'additional_net60_premium':9000 if scenario=='cash_pressure' and beacon else 1800 if beacon else 2500,
        'cash_position':'constrained' if scenario=='cash_pressure' and beacon else 'healthy',
        'security_remediation': {'available':True,'annual_cost':remediation_cost(scenario),'delivery_days':21,
            'scope':['EU isolated tenant','SCIM production connector','no-training DPA','closed audit exceptions','12-month liability','net 45 or 60','renewal uplift <=3%'],
            'evidence':'QD-ENTERPRISE-v2; completed controls, verified before buyer approval'} if not beacon else 'Existing EU and SCIM infrastructure included',
        'renewal_preference':'Prefer predictable retention; may waive renewal within charter' if beacon else 'Mandatory renewal supports current business model',
        'authority':'Cannot trade security assertions or liability protections for a lower price'}

def reservation(vendor, scenario, payment_days):
    facts=private_data(vendor,scenario)
    margin_floor=math.ceil(facts['annual_delivery_cost']/(1-facts['gross_margin_target_pct']/100))
    base=max(vendor.floor, math.ceil(vendor.list_price*(1-vendor.max_discount/100)),margin_floor)
    return base + facts['opportunity_cost_premium'] + facts['working_capital_premium_net45'] + (
        facts['additional_net60_premium'] if payment_days>45 else 0)

def commercial_offer(vendor, proposed, scenario):
    package=proposed.get('remediation',False)
    if type(package) is not bool:raise ValueError('Invalid remediation selection')
    effective=effective_vendor(vendor,proposed,scenario)
    offer=enforce(effective,proposed)
    minimum=reservation(effective,scenario,offer['payment_days'])
    if offer['price'] < minimum:
        offer['price']=minimum
        offer['blocks'].append('Commercial authority enforced')
    if offer['price']>effective.list_price:
        raise ValueError('No authorized commercial offer')
    offer.update(remediation=package and vendor.key=='quickdash',
        remediation_annual_cost=remediation_cost(scenario) if package and vendor.key=='quickdash' else 0,
        implementation_days=21 if package and vendor.key=='quickdash' else 7,
        evidence_revision='QD-ENTERPRISE-v2' if package and vendor.key=='quickdash' else 'BASE-v1')
    return offer

def buyer_comparison(offers, budget):
    # Buyer-owned treasury assumption, separate from vendor cost/reservation data.
    return [{'price':o['price'],'payment_days':o['payment_days'],
        'annual_cash_timing_value':round(o['price']*.08*max(0,o['payment_days']-45)/365,2),
        'effective_annual_cost':round(o['price']-o['price']*.08*max(0,o['payment_days']-45)/365,2),
        'within_budget':o['price']<=budget} for o in offers]

def decision_explanation(offer, scenario):
    why=[]
    if scenario=='cash_pressure' and offer['vendor']=='beacon':
        why.append('Working-capital pressure makes slower collection expensive')
    if scenario=='capacity_crunch' and offer['vendor']=='beacon':
        why.append('Scarce implementation capacity carries an opportunity cost')
    why.append('Longer payment terms must be compensated in price' if offer['payment_days']>45 else
        'Net 45 limits the cost of financing the customer' if offer['payment_days']==45 else
        f"Net {offer['payment_days']} accelerates collection but fails the buyer's net-45 requirement")
    if offer['security_gaps']:
        why.append('A price concession cannot authorize unavailable security capabilities')
    if offer.get('remediation'):
        why.append(f"Enterprise remediation adds USD {offer['remediation_annual_cost']}/year and 21 days of implementation; all required controls are included")
    return '. '.join(why)+'.'

def award_explanation(selected,candidates,budget):
    if selected is None:return 'No offer cleared the authorized budget and all mandatory departmental controls.'
    text=(f"Recommendation awaiting human approval: {selected['name']} at USD {selected['price']:,}/year "
        f"against an authorized USD {budget:,} annual cap; net {selected['payment_days']}, "
        f"{selected.get('implementation_days',7)}-day rollout. All listed candidates cleared Security, Legal and Finance. ")
    if selected.get('remediation'):
        text+=f"The USD {selected['remediation_annual_cost']:,}/year Enterprise Controls package is included in that total and verified under QD-ENTERPRISE-v2. "
    alternatives=[o for o in candidates if o['vendor']!=selected['vendor']]
    for other in alternatives:
        delta=other['price']-selected['price']
        text+=(f"Compared with {other['name']}, this is USD {abs(delta):,}/year "
            f"{'less' if delta>=0 else 'more'}, with a {selected.get('implementation_days',7)}-day versus "
            f"{other.get('implementation_days',7)}-day rollout. ")
    if not alternatives:text+='This is the only offer meeting the current budget and all mandatory controls. '
    return text+'Closing requires explicit approval of this exact offer.'
