"""Public boundary validation. This module knows no vendor reservation prices."""
import hashlib
import json
from policy import finite


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def public_offer(value, vendor):
    fields = {'vendor', 'name', 'list_price', 'price', 'seats', 'term_months', 'payment_days',
              'auto_renew', 'uplift_pct', 'liability_months', 'trains_on_data', 'security_gaps', 'blocks'}
    optional={'remediation','remediation_annual_cost','implementation_days','evidence_revision'}
    if not fields.issubset(value) or set(value)-fields-optional or value['vendor'] != vendor:
        raise ValueError('Unexpected offer fields or vendor')
    for field in ('list_price', 'price', 'seats', 'term_months', 'payment_days', 'uplift_pct', 'liability_months'):
        number = finite(value[field], field)
        if not 0 <= number <= 10000000:
            raise ValueError('Offer number out of bounds')
    if value['price'] <= 0 or value['seats'] != 250 or value['term_months'] != 24:
        raise ValueError('Offer does not match requested scope')
    if any(type(value[k]) is not bool for k in ('auto_renew', 'trains_on_data')):
        raise ValueError('Invalid boolean')
    for key in ('security_gaps', 'blocks'):
        if not isinstance(value[key], list) or len(value[key]) > 20 or any(not isinstance(s, str) or len(s) > 300 for s in value[key]):
            raise ValueError('Unbounded offer text')
    if not isinstance(value['name'], str) or len(value['name']) > 100:
        raise ValueError('Invalid name')
    if 'remediation' in value and type(value['remediation']) is not bool:raise ValueError('Invalid remediation flag')
    for field in ('remediation_annual_cost','implementation_days'):
        if field in value and not 0<=finite(value[field],field)<=1000000:raise ValueError('Invalid package cost or delivery')
    if 'evidence_revision' in value and value['evidence_revision'] not in ('BASE-v1','QD-ENTERPRISE-v2'):raise ValueError('Unknown evidence revision')
    return dict(value)


def quote_text(offer):
    return (f"{offer['name']}: USD {offer['price']}/year; {offer['seats']} seats; "
            f"{offer['term_months']} months; net {offer['payment_days']}; "
            f"auto-renew {offer['auto_renew']}; uplift {offer['uplift_pct']}%; "
            f"liability {offer['liability_months']} months. "
            f"Training: {offer['trains_on_data']}; gaps: {', '.join(offer['security_gaps']) or 'none reported'}. "
            f"Remediation included: {offer.get('remediation',False)}; annual package cost USD {offer.get('remediation_annual_cost',0)}; implementation {offer.get('implementation_days',7)} days.")


def counter_text(price):
    # Deliberately no arbitrary model prose crosses the company boundary.
    return (f'Counteroffer USD {price}/year for 250 seats, 24 months. Require net 45 or better, '
            'EU residency, SCIM, no training, liability >=12 months, renewal uplift <=3%.')
