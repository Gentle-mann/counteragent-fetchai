"""Offline evaluator. Private charter values are never sent to the buyer."""
import math
from policy import VENDORS, violations


def evaluate(state):
    rows = {}
    for key, metric in state.get('negotiation_metrics', {}).items():
        charter = VENDORS[key]
        floor = max(charter.floor, math.ceil(charter.list_price*(1-charter.max_discount/100)))
        opening, final = metric['opening_price'], metric['final_price']
        available = max(0, opening-floor)
        rows[key] = {**metric, 'evaluation_only_reservation_price': floor,
            'price_above_feasible_floor': final-floor,
            'available_price_concession_captured_pct': round(100*(opening-final)/available,1) if available else 0,
            'policy_compliant': not metric['violations']}
    feasible = any(not violations({**o,'price':max(VENDORS[o['vendor']].floor,
        math.ceil(o['list_price']*(1-VENDORS[o['vendor']].max_discount/100)))},state['budget']) for o in state.get('offers',[]))
    return {'vendors': rows, 'feasible_compliant_deal_exists': feasible,
        'walk_away_correct': state['status']=='walked_away' and not feasible,
        'interpretation': 'Scenario-specific price efficiency and compliance, not a general intelligence score.'}
