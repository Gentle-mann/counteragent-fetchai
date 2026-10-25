"""Bounded deterministic tools; no shell, arbitrary URL or filesystem access."""
from policy import violations


def inspect_evidence(role, payload):
    evidence = payload.get('vendor_evidence', {})
    result = []
    for offer in payload.get('offers', [payload.get('winner')]):
        if not offer:
            continue
        e = evidence.get(offer['vendor'], {})
        missing = []
        if role == 'security':
            for key in ('residency', 'scim', 'training', 'audit_exceptions'):
                if key not in e:
                    missing.append(key)
            contradictions = (e.get('training') != offer['trains_on_data'] or
                              e.get('audit_exceptions') != offer['security_gaps'])
            passed = not missing and not contradictions and e.get('residency') == 'EU' and e.get('scim') is True and e.get('training') is False and not e.get('audit_exceptions')
            if offer.get('remediation'):
                passed = passed and e.get('remediation_verified') is True and e.get('evidence_revision')=='QD-ENTERPRISE-v2' and e.get('source_document')=='quickdash-enterprise-trust.txt'
        elif role == 'legal':
            missing = [k for k in ('liability_months', 'auto_renew', 'uplift_pct') if k not in e]
            passed = not missing and all(e[k] == offer[k] for k in ('liability_months', 'auto_renew', 'uplift_pct'))
        else:
            missing = [k for k in ('annual_amount', 'total_contract_value', 'payment_days') if k not in e]
            passed = not missing and e.get('annual_amount') == offer['price'] and e.get('total_contract_value') == offer['price']*2 and e.get('payment_days') == offer['payment_days']
        result.append({'vendor': offer['vendor'], 'passed': passed, 'missing': missing,
                       'tool': {'security': 'verify_trust_pack', 'legal': 'compare_contract_terms', 'finance': 'reconcile_quote_and_tcv'}[role]})
    return result


def finance_analysis(offer, budget):
    # These are explicit scenario assumptions, not observed production usage.
    return {'annual_amount': offer['price'], 'contract_value': offer['price']*2,
            'budget_headroom': budget-offer['price'], 'annual_cost_per_active_user': round(offer['price']/212, 2),
            'unused_seats': 38, 'utilization_pct': 84.8,
            'net10_discount_value': round(offer['price']*.02,2),
            'approval_tier': 'finance' if offer['price']*2<=200000 else 'orchestrator' if offer['price']*2<=500000 else 'human',
            'policy_violations': violations(offer,budget)}
