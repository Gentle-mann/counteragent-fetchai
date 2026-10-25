"""Scope validation before analytics-specific models, policies or vendors run."""
def scope_error(intent):
    if not isinstance(intent,dict):return 'Describe the deal you want your company to negotiate.'
    category=intent.get('category')
    if category not in (None,'analytics_software'):
        return ('I represent your company, but the executable demo currently supports analytics software contracts. '
            'I can help scope another deal, but I will not send it to analytics suppliers. What product or service do you need?')
    if intent.get('currency','USD')!='USD' or intent.get('billing_basis','annual')!='annual':
        return 'This supplier profile quotes annual USD subscriptions. Please confirm currency and whether your budget is annual or one-time.'
    if intent.get('seats',250)!=250 or intent.get('term_months',24)!=24:
        return 'The available demo suppliers support 250 employees and a 24-month term. Confirm that scope or provide compatible supplier agents; I will not silently change your requested quantity or term.'
    if intent.get('role','buyer')!='buyer':return 'CounterAgent currently represents the buying company. Please describe what your company wants to buy.'
    return None
